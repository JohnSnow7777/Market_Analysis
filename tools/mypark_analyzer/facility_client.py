# -*- coding: utf-8 -*-
"""카카오 로컬 API 카테고리 검색 기반 주변 생활시설 '실측' 카운트 클라이언트.

기존 보고서의 주변 인프라 수치(관공서/교육기관/금융기관/버스정류장 등)는
지역등급에서 역산한 추정치였다. 이 모듈은 좌표 반경 내 시설 수를 카카오
카테고리 검색의 meta.total_count로 실제 조회해 그 값을 대체한다.

엔드포인트:
  GET https://dapi.kakao.com/v2/local/search/category.json
      ?category_group_code=<코드>&x=<경도>&y=<위도>&radius=<m>&page=1&size=15
  헤더: Authorization: KakaoAK <REST키>
  응답: {"documents":[...], "meta":{"total_count":N, "pageable_count":M, "is_end":bool}}

가장 중요한 원칙 — None과 0을 절대 섞지 않는다:
  0    -> API 호출은 성공했고 반경 내에 실제로 그 시설이 '없음'(확정된 사실)
  None -> 키 미설정/호출 실패로 '확인 불가'(사실 아님)
호출부는 None을 보면 기존 지역등급 추정 모델로 폴백하고, 0은 그대로 싣는다.
실패를 0으로 뭉개면 "인프라 전무" 같은 허위 결론이 보고서에 실린다.
"""
import os
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# 카카오 키 환경변수 이름은 competitor_engine과 동일한 것을 공유한다.
KAKAO_API_KEY_ENV = 'KAKAO_REST_API_KEY'

KAKAO_CATEGORY_URL = "https://dapi.kakao.com/v2/local/search/category.json"

# 카카오 공식 카테고리 그룹 코드
CATEGORY_CODES = {
    'MT1': '대형마트',
    'CS2': '편의점',
    'PS3': '어린이집·유치원',
    'SC4': '학교',
    'AC5': '학원',
    'PK6': '주차장',
    'OL7': '주유소',
    'SW8': '지하철역',
    'BK9': '은행',
    'CT1': '문화시설',
    'AG2': '중개업소',
    'PO3': '공공기관',
    'AT4': '관광명소',
    'AD5': '숙박',
    'FD6': '음식점',
    'CE7': '카페',
    'HP8': '병원',
    'PM9': '약국',
}

# fetch_facility_counts가 한 번에 조회하는 시설 (한글명 -> 카테고리 코드)
FACILITY_TARGETS = [
    ('지하철역', 'SW8'),
    ('병원', 'HP8'),
    ('약국', 'PM9'),
    ('은행', 'BK9'),
    ('학교', 'SC4'),
    ('학원', 'AC5'),
    ('공공기관', 'PO3'),
    ('주차장', 'PK6'),
    ('카페', 'CE7'),
    ('대형마트', 'MT1'),
    ('문화시설', 'CT1'),
]

# 카카오 반경 검색 상한은 20km. 넘겨서 400을 받는 대신 미리 잘라낸다.
MAX_RADIUS_M = 20000
REQUEST_TIMEOUT = 4


def _request_category(x, y, radius, category_code, api_key, sort=None, size=15):
    """카테고리 검색 원본 응답(dict)을 반환. 실패 시 None.

    '결과 0건'과 '호출 실패'를 호출부가 구분할 수 있어야 하므로, 실패는
    빈 dict가 아니라 반드시 None으로 돌려준다.
    """
    try:
        params = {
            'category_group_code': category_code,
            'x': x,
            'y': y,
            'radius': int(max(0, min(int(radius), MAX_RADIUS_M))),
            'page': 1,
            'size': size,
        }
        if sort:
            params['sort'] = sort
        url = KAKAO_CATEGORY_URL + '?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={'Authorization': f'KakaoAK {api_key}'})
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        if not isinstance(data, dict):
            print(f"[KAKAO CATEGORY FAIL] {category_code}: unexpected payload type")
            return None
        return data
    except Exception as e:
        print(f"[KAKAO CATEGORY FAIL] {category_code} @({x},{y}) r={radius}: {e}")
        return None


def count_by_category(x, y, radius, category_code):
    """반경 내 해당 카테고리 시설 수. 키 없음/실패 시 None, 실제 0건이면 0.

    전체 페이지를 순회하지 않고 meta.total_count 한 값만 쓴다. 개수만 필요한데
    페이징하면 호출 수가 시설 종류 x 페이지 수로 불어나 카카오 쿼터를 낭비하고
    서버리스 타임아웃도 유발한다.
    """
    api_key = os.environ.get(KAKAO_API_KEY_ENV)
    if not api_key:
        return None
    data = _request_category(x, y, radius, category_code, api_key)
    if data is None:
        return None
    meta = data.get('meta')
    if not isinstance(meta, dict):
        # 응답 형식이 기대와 다르면 0으로 단정하지 않고 '확인 불가'로 넘긴다.
        print(f"[KAKAO CATEGORY FAIL] {category_code}: meta 누락")
        return None
    total = meta.get('total_count')
    if total is None:
        print(f"[KAKAO CATEGORY FAIL] {category_code}: total_count 누락")
        return None
    try:
        return int(total)
    except (TypeError, ValueError):
        print(f"[KAKAO CATEGORY FAIL] {category_code}: total_count 형식 오류 ({total!r})")
        return None


def fetch_facility_counts(x, y, radius=3000):
    """주요 생활시설 개수를 한 번에 조회. 반환 예: {'지하철역': 3, '병원': 42, ...}

    - 키가 없거나 모든 항목이 실패하면 dict 자체를 None으로 반환한다
      (호출부가 통째로 기존 추정 모델로 폴백할 수 있게).
    - 일부만 실패하면 그 키만 None으로 두고 성공한 값은 살린다.
      한 항목의 일시적 실패 때문에 확인된 나머지 실측치를 버릴 이유가 없다.

    Vercel 서버리스 환경에서 11개를 순차 호출하면 최악의 경우 4초 x 11 = 44초로
    함수 타임아웃에 걸리므로 스레드 풀로 병렬 호출한다. 워커를 과하게 늘리면
    카카오 쪽 순간 호출량이 튀므로 5로 제한한다.
    """
    api_key = os.environ.get(KAKAO_API_KEY_ENV)
    if not api_key:
        return None

    def _one(item):
        label, code = item
        return label, count_by_category(x, y, radius, code)

    results = {}
    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            for label, value in executor.map(_one, FACILITY_TARGETS):
                results[label] = value
    except Exception as e:
        # 스레드 풀 자체가 실패한 경우도 추정값으로 메우지 않는다.
        print(f"[KAKAO CATEGORY FAIL] facility counts batch: {e}")
        return None

    # 하나도 확인하지 못했다면 '부분 실측'이 아니라 '확인 불가'다.
    if all(v is None for v in results.values()):
        return None
    return results


def nearest_subway(x, y, radius=3000):
    """가장 가까운 지하철역 1곳. 반환 {'name': 역명, 'distance_m': int}.

    반경 내에 역이 없으면 {'name': None, 'distance_m': None} (확정된 '없음'),
    키 없음/호출 실패는 None (확인 불가).

    보고서가 역 이름을 확인 없이 지어내지 않도록, 카카오가 돌려준 place_name과
    distance를 그대로 쓴다. sort=distance로 정렬해 첫 문서만 보면 되므로
    페이징이 필요 없다.
    """
    api_key = os.environ.get(KAKAO_API_KEY_ENV)
    if not api_key:
        return None
    # size=1이면 문서가 비었을 때 '없음'인지 판별이 애매할 수 있어 넉넉히 받고 첫 건만 쓴다.
    data = _request_category(x, y, radius, 'SW8', api_key, sort='distance', size=15)
    if data is None:
        return None
    docs = data.get('documents')
    if docs is None:
        print("[KAKAO CATEGORY FAIL] SW8: documents 누락")
        return None
    if not docs:
        return {'name': None, 'distance_m': None}

    first = docs[0] if isinstance(docs[0], dict) else {}
    name = first.get('place_name') or None
    # distance는 문자열("1234")로 오는 것으로 알려져 있으나, 정렬 파라미터가
    # 무시되거나 필드가 비는 경우도 있어 방어적으로 변환한다.
    raw_dist = first.get('distance')
    try:
        distance_m = int(float(raw_dist)) if raw_dist not in (None, '') else None
    except (TypeError, ValueError):
        distance_m = None
    return {'name': name, 'distance_m': distance_m}
