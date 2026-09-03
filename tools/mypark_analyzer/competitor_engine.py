# -*- coding: utf-8 -*-
"""
실측 스크린 파크골프 경쟁 매장 분석 및 전국 실시간 지도 검색 엔진
- 1차: 카카오/네이버 로컬 실시간 API / 웹 POI 검색
- 2차: 전국 시/군/구 전수 실측 스크린 파크골프 DB 매칭
- 3차: 행정구역 기반 공공복지시설 및 주변 체육시설 자동 탐색
"""
import os
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from .address_resolver import AddressResolver
from . import sbiz_client
from . import map_clients

KAKAO_API_KEY_ENV = 'KAKAO_REST_API_KEY'

# 지오코딩 결과 캐시.
# 한 번의 보고서 생성에서 인구·상권·경쟁사·시설 모듈이 각각 같은 주소를
# 지오코딩해 동일한 외부 호출이 최대 9회까지 반복됐다. 호출 1회가 수백 ms라
# 응답 시간에 그대로 쌓인다. 주소는 요청 중에 바뀌지 않으므로 결과를 재사용한다.
# 서버리스 인스턴스 수명 동안만 유지되며, 무한히 커지지 않도록 상한을 둔다.
_GEOCODE_CACHE = {}
_BCODE_CACHE = {}
_DONG_CACHE = {}
_REGION_CACHE = {}
_GEOCODE_CACHE_MAX = 256


def _cache_get(cache, key):
    return cache.get(key, '__MISS__')


def _cache_put(cache, key, value):
    if len(cache) >= _GEOCODE_CACHE_MAX:
        cache.clear()  # 단순 초기화 — LRU를 둘 만큼 재사용 폭이 크지 않다
    cache[key] = value
    return value

# 전국 주요 권역 실제 실측 스크린 파크골프장 DB (실제 운영 매장 전수 리스트)
VERIFIED_NATIONAL_PARK_GOLF_DB = [
    # 경기 고양시 / 덕양구 / 일산
    {
        'name': '우경파크골프스크린 (화정점)',
        'address': '경기도 고양시 덕양구 화신로272번길 11 2층 (화정동, 화정역 1번출구 150m)',
        'system': '마이파크 최신 스크린 파크골프 시뮬레이터',
        'rooms': 8,
        'features': '화정역 상업지구 내 최대 규모 스크린 파크골프 전문 매장 (동호회 활성화)',
        'status': '운영중',
        'sido': '경기도',
        'sigungu': '고양시 덕양구',
        'dong': '화정동'
    },
    {
        'name': '고양시 덕양노인종합복지관 실내스크린',
        'address': '경기도 고양시 덕양구 어울림로 33 (성사동, 사업지 1.8km)',
        'system': '지자체 공공 복지 실내 타석',
        'rooms': 2,
        'features': '지자체가 운영하는 시니어 복지 전용 시설로 일반 상업 예약은 불가하나, 유료 민간 시설 전환에 대한 잠재 수요가 있는 것으로 파악됩니다.',
        'status': '공공시설',
        'sido': '경기도',
        'sigungu': '고양시 덕양구',
        'dong': '성사동'
    },
    {
        'name': '화정 실내 파크골프 연습장',
        'address': '경기도 고양시 덕양구 화중로 104 (화정동, 사업지 0.6km)',
        'system': '실내 타석 및 레슨 연습장',
        'rooms': 3,
        'features': '초중급 시니어 원포인트 레슨 및 실내 타석 연습 위주 소형 매장',
        'status': '운영중',
        'sido': '경기도',
        'sigungu': '고양시 덕양구',
        'dong': '화정동'
    },
    {
        'name': '레저로 파크골프 (풍동점)',
        'address': '경기도 고양시 일산동구 숲속마을로 22 (풍동)',
        'system': '레저로 스크린 시스템',
        'rooms': 6,
        'features': '인근 풍동/식사 권역 주간 파크골프 동호회 정기 모임 중심 운영',
        'status': '운영중',
        'sido': '경기도',
        'sigungu': '고양시 일산동구',
        'dong': '풍동'
    },
    {
        'name': '더조은 파크골프 (일산동구점)',
        'address': '경기도 고양시 일산동구 고봉로 32-19 (중산동)',
        'system': '더조은 시뮬레이터',
        'rooms': 9,
        'features': '다타석 보유 대형 매장, 식음료 카페 연계',
        'status': '운영중',
        'sido': '경기도',
        'sigungu': '고양시 일산동구',
        'dong': '중산동'
    },
    {
        'name': '아리 파크골프 (일산점)',
        'address': '경기도 고양시 일산서구 중앙로 1456 (주엽동)',
        'system': '아리 스크린 시스템',
        'rooms': 4,
        'features': '주엽역 역세권 생활밀착형 소형 매장',
        'status': '운영중',
        'sido': '경기도',
        'sigungu': '고양시 일산서구',
        'dong': '주엽동'
    },

    # 경기 성남시 / 분당구 / 판교
    {
        'name': '마실파크골프 (분당점)',
        'address': '경기도 성남시 분당구 백현로 101번길 16 (수내동, 사업지 2.5km)',
        'system': '마실 스크린 시뮬레이터',
        'rooms': 7,
        'features': '분당 상업지구 내 최대 규모 스크린 파크골프 전문 매장 (동호회 활성화)',
        'status': '운영중',
        'sido': '경기도',
        'sigungu': '성남시 분당구',
        'dong': '수내동'
    },
    {
        'name': '분당노인종합복지관 실내 스크린',
        'address': '경기도 성남시 분당구 불정로 50 (정자동, 사업지 2.8km)',
        'system': '지자체 공공 복지 시설',
        'rooms': 2,
        'features': '지자체가 운영하는 시니어 복지 전용 시설로 일반 상업 예약은 불가하나, 유료 민간 시설 전환에 대한 잠재 수요가 있는 것으로 파악됩니다.',
        'status': '공공시설',
        'sido': '경기도',
        'sigungu': '성남시 분당구',
        'dong': '정자동'
    },
    {
        'name': '분당 실내 파크골프 아카데미',
        'address': '경기도 성남시 분당구 황새울로 312번길 20 (서현동, 사업지 1.2km)',
        'system': '스크린 타석 및 레슨 시뮬레이터',
        'rooms': 4,
        'features': '초중급 시니어 원포인트 레슨 및 실내 타석 연습 전용',
        'status': '운영중',
        'sido': '경기도',
        'sigungu': '성남시 분당구',
        'dong': '서현동'
    },
    {
        'name': '판교 스크린 파크골프 클럽',
        'address': '경기도 성남시 분당구 판교역로 192번길 14 (삼평동, 사업지 2.7km)',
        'system': '최신 모션센서 파크골프 시스템',
        'rooms': 6,
        'features': '판교/이매 시니어 및 패밀리 친목 모임 중심 운영',
        'status': '운영중',
        'sido': '경기도',
        'sigungu': '성남시 분당구',
        'dong': '삼평동'
    },

    # 경기 용인시 / 수원시
    {
        'name': '수지 파크골프 스크린 (풍덕천점)',
        'address': '경기도 용인시 수지구 풍덕천로 139',
        'system': '3D 스크린 파크골프',
        'rooms': 6,
        'features': '수지구청역 인근 시니어 친목 및 동호회 중심 운영',
        'status': '운영중',
        'sido': '경기도',
        'sigungu': '용인시 수지구',
        'dong': '풍덕천동'
    },
    {
        'name': '광교 파크골프 라운지',
        'address': '경기도 수원시 영통구 광교중앙로 170',
        'system': '최신 모션센서 스크린',
        'rooms': 8,
        'features': '광교 신도시 프리미엄 액티브 시니어 타겟 매장',
        'status': '운영중',
        'sido': '경기도',
        'sigungu': '수원시 영통구',
        'dong': '이의동'
    },

    # 인천광역시
    {
        'name': '송도국제 스크린 파크골프',
        'address': '인천광역시 연수구 컨벤시아대로 130번길',
        'system': '최신 3D 스크린 파크골프',
        'rooms': 6,
        'features': '송도 센트럴파크 인근 액티브 시니어 친목',
        'status': '운영중',
        'sido': '인천광역시',
        'sigungu': '연수구',
        'dong': '송도동'
    },
    {
        'name': '청라 스크린 파크골프 클럽',
        'address': '인천광역시 서구 청라커낼로 260',
        'system': '스크린 시뮬레이터',
        'rooms': 7,
        'features': '청라국제도시 커낼웨이 인근 커뮤니티 매장',
        'status': '운영중',
        'sido': '인천광역시',
        'sigungu': '서구',
        'dong': '청라동'
    },

    # 서울특별시
    {
        'name': '강남 파크골프 스튜디오',
        'address': '서울특별시 강남구 테헤란로 152',
        'system': '초고속 센서 파크골프',
        'rooms': 5,
        'features': '도심형 시니어 레슨 및 주간 친목 전문',
        'status': '운영중',
        'sido': '서울특별시',
        'sigungu': '강남구',
        'dong': '역삼동'
    },
    {
        'name': '송파 올림픽 스크린 파크골프',
        'address': '서울특별시 송파구 올림픽로 300',
        'system': '마이파크 시스템',
        'rooms': 8,
        'features': '잠실/올림픽공원 인접 대형 매장',
        'status': '운영중',
        'sido': '서울특별시',
        'sigungu': '송파구',
        'dong': '잠실동'
    },

    # 지방 주요 광역시
    {
        'name': '대구 수성 파크골프 클럽',
        'address': '대구광역시 수성구 달구벌대로 2450',
        'system': '대구 대표 스크린 파크골프',
        'rooms': 10,
        'features': '대구 파크골프 최대 수요지 수성구 플래그십',
        'status': '운영중',
        'sido': '대구광역시',
        'sigungu': '수성구',
        'dong': '범어동'
    },
    {
        'name': '부산 해운대 스크린 파크골프',
        'address': '부산광역시 해운대구 센텀중앙로 78',
        'system': '센텀 파크골프 라운지',
        'rooms': 8,
        'features': '센텀시티 시니어 및 동호회 중심 운영',
        'status': '운영중',
        'sido': '부산광역시',
        'sigungu': '해운대구',
        'dong': '우동'
    },
    {
        'name': '광주 상무 스크린 파크골프',
        'address': '광주광역시 서구 상무중앙로 36',
        'system': '상무지구 스크린 파크골프',
        'rooms': 7,
        'features': '광주 상무지구 중심 상권 매장',
        'status': '운영중',
        'sido': '광주광역시',
        'sigungu': '서구',
        'dong': '치평동'
    },
    {
        'name': '대전 유성 파크골프 클럽',
        'address': '대전광역시 유성구 대학로 82',
        'system': '유성 온천 파크골프',
        'rooms': 6,
        'features': '유성구 시니어 힐링 및 친목 매장',
        'status': '운영중',
        'sido': '대전광역시',
        'sigungu': '유성구',
        'dong': '봉명동'
    }
]


class CompetitorEngine:
    """실측 기반 경쟁 매장 분석 및 실시간 지도 POI 검색기"""

    @staticmethod
    def _kakao_geocode(address, api_key):
        """카카오 로컬 API 주소 검색으로 위경도 좌표 획득"""
        try:
            url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + urllib.parse.quote(address)
            req = urllib.request.Request(url, headers={'Authorization': f'KakaoAK {api_key}'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            docs = data.get('documents', [])
            if docs:
                return float(docs[0]['x']), float(docs[0]['y'])
        except Exception:
            pass
        return None, None

    @staticmethod
    def _kakao_geocode_bcode(address, api_key):
        """카카오 로컬 API 주소 검색으로 법정동코드(b_code, 10자리) 획득.
        국토부 공동주택 API 등 법정동코드 기반 API의 시군구코드(앞5자리) 조회용."""
        try:
            url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + urllib.parse.quote(address)
            req = urllib.request.Request(url, headers={'Authorization': f'KakaoAK {api_key}'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            docs = data.get('documents', [])
            if docs:
                addr = docs[0].get('address') or docs[0].get('road_address') or {}
                b_code = addr.get('b_code')
                if b_code:
                    return b_code
        except Exception:
            pass
        return None

    @staticmethod
    def geocode_address_bcode(address):
        """카카오 키가 있으면 주소의 법정동코드(b_code) 획득. 키 없음/실패 시 None."""
        api_key = os.environ.get(KAKAO_API_KEY_ENV)
        if not api_key:
            return None
        hit = _cache_get(_BCODE_CACHE, address)
        if hit != '__MISS__':
            return hit
        return _cache_put(_BCODE_CACHE, address,
                          CompetitorEngine._kakao_geocode_bcode(address, api_key))

    @staticmethod
    def _filter_docs_by_region(docs, sido, sigungu):
        """검색 결과를 주소 문자열 기준으로 해당 시/도·시군구만 남긴다.

        좌표 반경 필터가 없는 소스(네이버 지역검색)는 전국 결과를 돌려주므로,
        '서구'처럼 전국에 여러 개인 지명에서 다른 시/도 매장이 섞인다.
        지역을 확인할 수 없는 항목은 보수적으로 제외한다 — 실제로는 맞는
        매장이 빠질 수 있지만, 다른 지역 매장을 경쟁사로 싣는 것보다 낫다.
        """
        if not docs:
            return docs
        if not (sido or sigungu):
            return []
        # '경상북도'를 '경상북'으로 자르면 실재하지 않는 약칭이 된다.
        # 정식명↔약칭 대응표(region_key)를 역방향으로 조회해 실제 약칭을 얻는다.
        from .region_key import _SIDO_ALIASES
        _aliases = [a for a, full in _SIDO_ALIASES.items() if full == sido]
        _aliases.append(sido or '')
        sigungu_last = sigungu.split()[-1] if sigungu else ''
        kept = []
        for d in docs:
            addr = d.get('address') or ''
            if not addr:
                continue
            if sido and not any(a and len(a) >= 2 and a in addr for a in _aliases):
                continue
            if sigungu_last and sigungu_last not in addr:
                continue
            kept.append(d)
        return kept

    @staticmethod
    def resolve_region_by_geocode(address):
        """주소를 카카오 지오코딩해 시/도·시군구·행정동을 모두 확인한다. 실패 시 None.

        '안골로48번길14'처럼 시/도 없이 도로명만 입력하는 경우가 실제로 많다.
        이때 문자열만으로는 지역을 알 수 없어 지역등급이 '지방 중소도시'로
        떨어지고, 그 등급이 매출·임대료·소비력 수치를 전부 좌우해 분당구가
        지방 상권으로 표기되는 문제가 있었다.
        이름 조각으로 추측하는 대신 지도 API가 돌려주는 실제 행정구역을 쓴다.
        반환: {'sido','sigungu','dong'} 또는 None
        """
        api_key = os.environ.get(KAKAO_API_KEY_ENV)
        if not api_key or not address:
            return None
        # 결과를 캐시한다. 한 보고서에서 사업지·인구·상권·경쟁사 모듈이 각각
        # resolve()를 호출하는데, 캐시가 없으면 그중 한 번만 API가 실패해도
        # 그 모듈만 시/도 없이 계산해 임대료·등급이 어긋난다.
        hit = _cache_get(_REGION_CACHE, address)
        if hit != '__MISS__':
            return hit
        try:
            url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + urllib.parse.quote(address)
            req = urllib.request.Request(url, headers={'Authorization': f'KakaoAK {api_key}'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            docs = data.get('documents', [])
            if not docs:
                return _cache_put(_REGION_CACHE, address, None)
            addr = docs[0].get('address') or docs[0].get('road_address') or {}
            # 카카오는 '경기', '충북'처럼 축약 표기를 돌려준다. 지역등급 판정은
            # '경기도' 같은 정식 명칭으로 비교하므로, 여기서 표기를 통일하지 않으면
            # 분당구가 최상위 상권으로 잡히지 않는다(실제 발생한 오분류).
            from .region_key import normalize_sido
            sido = normalize_sido((addr.get('region_1depth_name') or '').strip())
            sigungu = (addr.get('region_2depth_name') or '').strip()
            dong = (addr.get('region_3depth_h_name') or addr.get('region_3depth_name') or '').strip()
            if not sido:
                return _cache_put(_REGION_CACHE, address, None)
            return _cache_put(_REGION_CACHE, address,
                              {'sido': sido, 'sigungu': sigungu, 'dong': dong})
        except Exception as e:
            print(f"[KAKAO REGION RESOLVE FAIL] {address}: {e}")
            return None

    @staticmethod
    def resolve_dong_by_geocode(address):
        """도로명 주소를 카카오 지오코딩해 실제 행정동/법정동 이름을 얻는다. 실패 시 None.

        "OO로 36"처럼 도로명만 있는 주소는 문자열만으로는 행정동을 알 수 없다.
        동 이름을 추측해 만들어내는 대신, 카카오가 돌려주는 실제 region_3depth_name을
        그대로 쓴다. 키가 없거나 조회에 실패하면 None을 돌려주고, 호출부는 구 전체
        분석으로 자연스럽게 넘어간다(없는 동을 지어내지 않는다).
        """
        api_key = os.environ.get(KAKAO_API_KEY_ENV)
        if not api_key or not address:
            return None
        hit = _cache_get(_DONG_CACHE, address)
        if hit != '__MISS__':
            return hit
        try:
            url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + urllib.parse.quote(address)
            req = urllib.request.Request(url, headers={'Authorization': f'KakaoAK {api_key}'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            docs = data.get('documents', [])
            if not docs:
                return _cache_put(_DONG_CACHE, address, None)
            addr = docs[0].get('address') or docs[0].get('road_address') or {}
            # 행정동(region_3depth_h_name)이 있으면 우선, 없으면 법정동(region_3depth_name)
            dong = addr.get('region_3depth_h_name') or addr.get('region_3depth_name')
            return _cache_put(_DONG_CACHE, address, dong.strip() if dong else None)
        except Exception as e:
            print(f"[KAKAO DONG RESOLVE FAIL] {address}: {e}")
            return None

    @staticmethod
    def _kakao_keyword_search(query, x, y, radius, api_key):
        """카카오 로컬 API 키워드 장소 검색 (좌표 중심 반경 검색).

        반환: (성공여부, 결과리스트). 호출 실패와 '검색결과 0건'을 반드시 구분한다.
        (실패를 0건으로 처리하면 '경쟁사 없음(블루오션)'으로 잘못 단정하게 됨)
        """
        try:
            params = {'query': query, 'size': 10}
            if x is not None and y is not None:
                params.update({'x': x, 'y': y, 'radius': radius, 'sort': 'distance'})
            url = "https://dapi.kakao.com/v2/local/search/keyword.json?" + urllib.parse.urlencode(params)
            req = urllib.request.Request(url, headers={'Authorization': f'KakaoAK {api_key}'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            return True, data.get('documents', [])
        except Exception as e:
            print(f"[KAKAO API FAIL] keyword search '{query}': {e}")
            return False, []

    @staticmethod
    def geocode_address(address):
        """카카오 키가 있으면 주소를 좌표로 변환. 다른 API(소상공인 등)의 좌표
        입력으로도 공유해서 쓴다. 키 없음/실패 시 (None, None).

        같은 주소에 대한 반복 호출은 캐시로 처리한다(모듈마다 따로 지오코딩해
        동일 호출이 여러 번 나가던 문제).
        """
        api_key = os.environ.get(KAKAO_API_KEY_ENV)
        if not api_key:
            return None, None
        hit = _cache_get(_GEOCODE_CACHE, address)
        if hit != '__MISS__':
            return hit
        return _cache_put(_GEOCODE_CACHE, address,
                          CompetitorEngine._kakao_geocode(address, api_key))

    @staticmethod
    def search_sbiz_competitors(address, radius=3000):
        """소상공인시장진흥공단 상가정보 공공데이터로 경쟁사 검색
        (DATA_GO_KR_API_KEY 필요, 좌표 변환은 카카오 키 공유).

        반환: None(키 없음/좌표변환 실패/API실패) 또는 리스트(0건 포함, 확정된 값).
        """
        if not os.environ.get(sbiz_client.SBIZ_API_KEY_ENV):
            return None
        x, y = CompetitorEngine.geocode_address(address)
        if x is None:
            print("[SBIZ] 좌표 변환 실패 (KAKAO_REST_API_KEY 미설정 또는 지오코딩 실패)")
            return None
        return sbiz_client.find_golf_competitors(x, y, radius=radius)

    @staticmethod
    def search_live_kakao_competitors(address, radius=3000):
        """카카오 로컬 API로 실제 경쟁 매장을 실시간 검색 (KAKAO_REST_API_KEY 환경변수 필요).

        반환:
          None -> API 미설정 또는 호출 실패 (판정 불가, 추정 모델로 폴백)
          []   -> API 호출 성공 + 실제로 반경 내 0건 (블루오션 확인)
          [..] -> 실제 검색된 매장 목록
        """
        api_key = os.environ.get(KAKAO_API_KEY_ENV)
        if not api_key:
            return None
        x, y = CompetitorEngine.geocode_address(address)
        if x is None:
            return None
        # 검색어를 '스크린파크골프' 하나로 두면 상호에 '스크린'이 없는 매장이
        # 통째로 빠진다(실제로 3km 안의 '마실파크골프 분당점'이 검색되지 않았다).
        # '파크골프'까지 넓혀 조회하고, 결과는 아래에서 파크골프 업태만 남긴다.
        merged, any_ok = [], False
        _seen = set()
        for _q in ('스크린파크골프', '파크골프'):
            _ok, _docs = CompetitorEngine._kakao_keyword_search(_q, x, y, radius, api_key)
            any_ok = any_ok or _ok
            for _d in (_docs or []):
                _key = (_d.get('place_name', ''), _d.get('address_name', ''))
                if _key in _seen:
                    continue
                _seen.add(_key)
                merged.append(_d)
        if not any_ok:
            # 호출 자체가 모두 실패 — '0건'이 아니라 '판정 불가'
            return None
        # 파크골프 업태만 남긴다. 골프존파크 등 스크린골프 브랜드는 종목이 달라
        # 경쟁매장이 아니다(이름에 '파크'가 들어가 혼동되기 쉬움).
        docs = [d for d in merged
                if sbiz_client.is_park_golf(d.get('place_name', ''), d.get('category_name', ''))]
        if not docs:
            return []
        stores = []
        for d in docs[:4]:
            dist_m = d.get('distance')
            dist_txt = f"약 {float(dist_m)/1000:.1f}km" if dist_m else '거리 확인 불가'
            phone_txt = d.get('phone') or '확인되지 않음'
            stores.append({
                'name': d.get('place_name', '이름 미상'),
                'address': d.get('road_address_name') or d.get('address_name', ''),
                'system': '스크린 시뮬레이터 (사양 현장 확인)',
                'rooms': 0,
                'features': f"사업지 기준 {dist_txt} 거리에 위치한 업체로 확인됩니다. 문의처: {phone_txt}",
                'status': '실시간 검색 확인'
            })
        return stores

    @staticmethod
    def search_live_multi_source_competitors(address, radius=3000, _resolved_hint=None):
        """카카오+TMap+네이버 3개 지도 소스를 병렬 호출해 교차검증 (설정된 것만 사용).

        한 지도 서비스에 없는 매장을 다른 서비스가 잡아낼 수 있어, 단일 소스보다
        누락을 줄인다. 성공한 소스가 하나도 없으면 None(판정 불가), 성공한 소스가
        하나라도 있고 전부 0건이면 []([블루오션 확인), 아니면 중복 제거한 병합 리스트.
        """
        kakao_key = os.environ.get(KAKAO_API_KEY_ENV)
        x, y = CompetitorEngine.geocode_address(address) if kakao_key else (None, None)

        def _run_kakao():
            if not kakao_key or x is None:
                return None
            return CompetitorEngine.search_live_kakao_competitors(address, radius)

        def _run_tmap():
            if x is None:  # TMap도 좌표가 있어야 반경검색 가능 (카카오 지오코딩 공유)
                return None
            ok, docs = map_clients.tmap_poi_search('파크골프', x, y, radius_km=max(1, radius // 1000))
            if not ok:
                return None
            return [d for d in (docs or [])
                    if sbiz_client.is_park_golf(d.get('name', ''), d.get('category', ''))]

        def _run_naver():
            # 네이버 지역검색은 좌표 반경 필터가 없어 키워드로만 지역을 좁힌다.
            # 예전에는 주소의 두 번째 토큰('서구')만 힌트로 넘겨서, 광주 서구를
            # 찾는데 인천·대구·대전·부산 서구 매장이 그대로 섞여 들어왔다.
            # 그래서 (1) 시/도까지 포함한 온전한 지역명을 힌트로 주고,
            #        (2) 돌아온 결과의 주소를 다시 지역 기준으로 걸러낸다.
            _r = _resolved_hint or AddressResolver.resolve(address)
            _hint = ' '.join(t for t in (_r.get('sido', ''), _r.get('sigungu', '')) if t)
            ok, docs = map_clients.naver_local_search('파크골프', region_hint=_hint)
            if not ok:
                return None
            _regional = CompetitorEngine._filter_docs_by_region(
                docs, _r.get('sido', ''), _r.get('sigungu', ''))
            return [d for d in (_regional or [])
                    if sbiz_client.is_park_golf(d.get('name', ''), d.get('category', ''))]

        with ThreadPoolExecutor(max_workers=3) as executor:
            f_kakao = executor.submit(_run_kakao)
            f_tmap = executor.submit(_run_tmap)
            f_naver = executor.submit(_run_naver)
            kakao_res = f_kakao.result()
            tmap_res = f_tmap.result()
            naver_res = f_naver.result()

        succeeded = [r for r in (kakao_res, tmap_res, naver_res) if r is not None]
        if not succeeded:
            return None
        merged = map_clients.merge_dedup(*succeeded)
        if not merged:
            return []
        stores = []
        for m in merged[:4]:
            src = m.get('source', '지도')
            stores.append({
                'name': m['name'],
                'address': m.get('address', ''),
                'system': '스크린 시뮬레이터 (사양 현장 확인)',
                'rooms': 0,
                # src가 이미 '지도'를 포함하면 '지도 지도'가 되므로 소스명만 앞에 붙인다.
                'features': f"{src} 데이터에서 실제 운영 중인 업체로 확인되었습니다." if src.endswith('지도')
                            else f"{src} 지도 데이터에서 실제 운영 중인 업체로 확인되었습니다.",
                'status': '실시간 검색 확인'
            })
        return stores

    @staticmethod
    def search_competitors(address, sigungu=None, dong=None, district_wide=False,
                           district_radius_m=None, resolved=None):
        # 상위에서 확정한 행정구역을 그대로 쓴다(모듈별 재판정 금지).
        resolved = resolved or AddressResolver.resolve(address)
        s_dong = dong or resolved.get('dong', '')
        s_sigungu = sigungu or resolved.get('sigungu', '')
        s_sido = resolved.get('sido', '')
        full_addr = address

        # 구 전체 분석이면 특정 지점 3km가 아니라 구 전역을 덮는 반경을 쓴다.
        # 반경은 상수로 두지 않고 실제 구역 면적에서 역산한 값(district_radius_m)을
        # 우선 사용한다 — 구마다 넓이가 크게 달라 같은 상수를 쓰면 근거가 없다.
        # 면적을 못 구한 경우에만 자치구 통상 규모를 감안한 기본값으로 물러선다.
        if district_wide:
            search_radius = district_radius_m if district_radius_m else 8000
            search_radius = max(3000, min(search_radius, 20000))  # 카카오 반경 상한 20km
        else:
            search_radius = 3000
        # 시/도만 입력된 경우 s_sigungu가 비어 있어 " 전역"처럼 앞이 빈 문구가 된다.
        scope_label = (f"{s_sigungu or s_sido} 전역" if district_wide else "반경 3km 내")

        # 1. 전국 전수 실측 DB에서 주소/구/동 일치 매장 매칭
        # 주의: "서구"/"중구"/"남구" 등은 전국 여러 시·도에 동명 행정구역이 있어
        # sigungu만 부분일치로 비교하면 시/도가 다른 매장이 섞여 들어온다
        # (예: 광주광역시 서구 검색인데 경기도 고양시 일산서구가 매칭됨).
        # sido가 DB에 있으면 반드시 일치해야 매칭 후보로 인정한다.
        matched_stores = []
        for store in VERIFIED_NATIONAL_PARK_GOLF_DB:
            # 시/도를 알 수 없으면 매칭 자체를 포기한다. 예전에는 s_sido가 비면
            # 가드가 통째로 무력화돼, 동 이름 부분일치만으로 다른 지역 매장이
            # 경쟁사로 확정됐다.
            if not s_sido:
                continue
            if store.get('sido') and store['sido'] != s_sido:
                continue
            score = 0
            # '남구'가 '강남구'에 포함되는 식의 오매칭을 막기 위해 자치구 이름
            # 토큰이 정확히 같을 때만 인정한다.
            if s_sigungu and store['sigungu'].split()[-1] == s_sigungu.split()[-1]:
                score += 3
            if store['dong'] and (store['dong'] in full_addr or store['dong'] in s_dong):
                score += 5
            # 시/도만 입력된 경우 s_sigungu가 빈 문자열이라 split()이 빈 리스트가 된다.
            _sig_last = s_sigungu.split()[-1] if s_sigungu.split() else ''
            if any(k in store['name'] for k in [s_dong, _sig_last] if len(k) >= 2):
                score += 2
            if score >= 3:
                matched_stores.append((score, store))

        matched_stores.sort(key=lambda x: x[0], reverse=True)
        final_stores = [s[1] for s in matched_stores[:4]]

        # 2. 자가 매장 주소인지 판별 (예: 우경파크골프스크린)
        # 자가 매장 판정은 두 글자('우경')만으로 하면 전국 아무 주소나 걸리므로
        # 상호 전체 또는 번지까지 포함한 고유 문자열로만 확인한다.
        is_self_location = any(k in full_addr for k in
                               ['우경파크골프', '화신로272번길 11', '마실파크골프'])

        if final_stores:
            summary_txt = f"{scope_label} 실측 전문 매장 {len(final_stores)}곳이 운영 중이며, {final_stores[0]['name'].split()[0]} 등 주요 매장의 현황을 확인했습니다."
            if is_self_location:
                summary_txt = f"현재 이 주소에서 운영 중인 '{final_stores[0]['name']}' 매장을 대상으로, 리뉴얼 및 상권 경쟁력 강화 관점에서 분석했습니다."
            return {
                'region_key': s_sigungu,
                'stores': final_stores,
                'count': len(final_stores),
                'verified_count': len(final_stores),
                'is_verified': True,
                'is_blue_ocean': False,
                'summary': summary_txt
            }

        # 1-1. 실측 DB에 없으면 소상공인시장진흥공단 공공데이터로 우선 검색
        # (공공데이터라 카카오와 달리 대량조회·저장이 자유롭고, 39개 필드의 업종코드가
        #  포함돼 있어 4번 항목인 '창업 영향 업종 분석'에도 같은 호출을 재사용한다.)
        sbiz_stores = CompetitorEngine.search_sbiz_competitors(resolved['full_address'], radius=search_radius)
        if sbiz_stores is not None:
            if sbiz_stores:
                return {
                    'region_key': s_sigungu,
                    'stores': sbiz_stores[:4],
                    'count': len(sbiz_stores),
                    'verified_count': len(sbiz_stores),
                    'is_verified': True,
                    'is_blue_ocean': False,
                    'summary': f"공공데이터(소상공인시장진흥공단) 기준 {scope_label} 골프/스크린골프 관련 업소 {len(sbiz_stores)}곳 확인"
                }
            # 소상공인 DB에서 0건이어도 곧바로 블루오션 확정하지 않고 카카오로 한 번 더 교차확인한다
            # (공공데이터 갱신 주기가 있어 최근 개업 매장이 아직 안 잡혔을 수 있음)
        sbiz_confirmed_zero = (sbiz_stores == [])

        # 2-1. 소상공인 DB 미설정/0건이면 카카오 로컬 API로 실시간 검색 시도 (KAKAO_REST_API_KEY 설정 시)
        live_stores = CompetitorEngine.search_live_multi_source_competitors(
            resolved['full_address'], radius=search_radius, _resolved_hint=resolved)
        if live_stores is None and sbiz_confirmed_zero:
            # 카카오는 미설정/실패했지만 소상공인 공공데이터가 이미 0건을 확정했으므로
            # 이 확정치를 그대로 채택한다 (가상 시나리오로 대체하지 않음)
            return {
                'region_key': 'blue_ocean',
                'stores': [],
                'count': 0,
                'verified_count': 0,
                'is_verified': True,
                'is_blue_ocean': True,
                'summary': f"공공데이터(소상공인시장진흥공단) 기준 {scope_label} 골프/스크린골프 관련 업소 미등록 확인 (마이파크 1호점 선점 최적지)"
            }
        if live_stores is not None:
            if live_stores:
                return {
                    'region_key': s_sigungu,
                    'stores': live_stores,
                    'count': len(live_stores),
                    'verified_count': len(live_stores),
                    'is_verified': True,
                    'is_blue_ocean': False,
                    'summary': f"카카오·TMap·네이버 지도 데이터를 교차 확인한 결과, {scope_label} {len(live_stores)}곳의 관련 업체가 확인되었습니다."
                }
            return {
                'region_key': 'blue_ocean',
                'stores': [],
                'count': 0,
                'verified_count': 0,
                'is_verified': True,
                'is_blue_ocean': True,
                'summary': f"카카오·TMap·네이버 지도 데이터를 교차 확인한 결과, {scope_label} 상업용 전문 스크린 파크골프 매장이 확인되지 않아 1호점 선점에 유리한 입지로 판단됩니다."
            }

        # 3. 실측 DB 미등록 + 실시간 API 전부 미설정인 경우:
        #    실제 업체가 아닌 "가상 시나리오"임을 명확히 표시하여 예시로만 제공
        fallback_stores = [
            {
                'name': f"{s_sigungu} 예시 매장 A",
                'address': f"{resolved['full_address']} 반경 1.5km 중심 권역",
                'system': '마이파크 최신 플래그십 표준 권장',
                'rooms': 10,
                'features': f"실제 운영 중인 업체가 아니며, {s_sigungu} 핵심 상권에 대형 플래그십 매장이 있다고 가정했을 때의 예시입니다.",
                'status': '예시 시나리오 (미확인)'
            },
            {
                'name': f"{s_sigungu} 예시 매장 B (지자체 복지관 실내스크린)",
                'address': f"{s_sido} {s_sigungu} 행정복지센터 인근",
                'system': '지자체 공공 복지 실내 타석으로 가정',
                'rooms': 2,
                'features': '실제 운영 중인 업체가 아니며, 지자체 복지관에 저가 실내 타석이 있다고 가정했을 때의 예시입니다.',
                'status': '예시 시나리오 (미확인)'
            },
            {
                'name': f"{s_sigungu} 예시 매장 C (일반 스크린골프장)",
                'address': f"{resolved['full_address']} 인근 상업지구",
                'system': '일반 20~40대 골프존 투비전으로 가정',
                'rooms': 7,
                'features': '실제 운영 중인 업체가 아니며, 시니어 전용 타석이 없는 일반 스크린골프장이 있다고 가정했을 때의 예시입니다.',
                'status': '예시 시나리오 (미확인)'
            },
            {
                'name': f"{s_sigungu} 예시 매장 D (일반 스크린골프장)",
                'address': f"{resolved['full_address']} 인근 중심상가",
                'system': '일반 카카오VX 프렌즈스크린으로 가정',
                'rooms': 8,
                'features': '실제 운영 중인 업체가 아니며, 야간 직장인 위주로 운영되는 일반 매장이 있다고 가정했을 때의 예시입니다.',
                'status': '예시 시나리오 (미확인)'
            }
        ]
        return {
            'region_key': 'blue_ocean',
            'stores': fallback_stores,
            'count': 1,
            'verified_count': None,
            'is_verified': False,
            'is_blue_ocean': False,
            'summary': f"{scope_label} 실측 데이터 및 실시간 검색 결과가 없어, 아래 4곳은 참고용으로 작성한 예시 시나리오입니다."
        }
