# -*- coding: utf-8 -*-
"""소상공인시장진흥공단 상가(상권)정보 API 클라이언트 (공공데이터포털).

엔드포인트/파라미터는 실제 서버에 더미 값으로 호출해 에러 응답으로 확인함
(2026-08-27, curl 직접 테스트):
  GET https://apis.data.go.kr/B553077/api/open/sdsc2/storeListInRadius
      ?serviceKey=&cx=&cy=&radius=&type=json
  - serviceKey 누락 -> {"errMsg":"SERVICE_KEY_IS_NULL"} (200 이전 401)
  - 더미 키 전달 -> {"errMsg":"SERVICE_KEY_IS_NOT_REGISTERED_ERROR"} (403)
    -> cx/cy/radius/type 파라미터명은 서버가 인식해 다음 단계(키 검증)까지
       진행시켜준 것으로 확인됨.

주의: 정상 응답의 개별 상가 필드명(상호명=bizesNm 등)은 서버 문서가 계정
활동신청 후에만 열람 가능해, 공개된 개발자 커뮤니티 자료를 근거로 최선으로
추정한 이름을 사용한다. 필드가 실제와 다르면 해당 값만 빈 값으로 빠질 뿐
예외를 던지지 않도록 전부 .get()으로 방어했다. 실제 키로 첫 호출 후 응답
원본을 로그로 남기니, 필드명이 다르면 그때 바로 잡으면 된다.
"""
import os
import json
import urllib.request
import urllib.parse

SBIZ_API_KEY_ENV = "DATA_GO_KR_API_KEY"
DIAG = {}  # [임시 진단] 확인 후 제거
SBIZ_BASE = "https://apis.data.go.kr/B553077/api/open/sdsc2/storeListInRadius"

# 스크린 파크골프 반경 경쟁사 탐지에 쓰는 업종 키워드
# (표준산업분류/상권업종 명칭에 아래 키워드가 들어가면 경쟁/유사 업종으로 간주)
# 직접 경쟁 = '파크골프' 종목을 다루는 곳만.
#
# 파크골프와 스크린골프는 다른 종목이다. 규칙·클럽·타겟 연령·이용 시간대가
# 모두 다르므로 스크린골프 매장을 경쟁매장으로 세면 안 된다.
# (실제로 '골프존파크 수내JUN스크린점'처럼 골프존의 스크린골프 브랜드가
#  경쟁사로 실렸던 사례가 있었다. '골프존파크'는 파크골프장이 아니다.)
DIRECT_KEYWORDS = ['파크골프', '파크 골프']

# 이름에 '파크'가 들어가지만 파크골프가 아닌 스크린골프 브랜드/업태.
# 이 목록에 걸리면 파크골프 키워드가 있어도 직접 경쟁에서 제외한다.
EXCLUDE_BRANDS = ['골프존파크', '골프존 파크', 'GDR', '골프존조이마루']

# 참고 업종: 골프 수요는 보여주지만 업태가 다른 곳
# (스크린골프, 골프연습장, 골프용품 소매업 등). 경쟁매장으로 세지 않는다.
GOLF_KEYWORDS = ['골프']


def is_park_golf(name, category=''):
    """이름/업종이 실제 '파크골프' 업태인지 판정.

    스크린골프 브랜드를 걸러내는 것이 핵심이다. 파크골프 키워드가 있어도
    제외 브랜드에 해당하면 파크골프장이 아니다.
    """
    blob = f"{name or ''} {category or ''}"
    if any(b in blob for b in EXCLUDE_BRANDS):
        return False
    return any(kw in blob for kw in DIRECT_KEYWORDS)


def search_stores_in_radius(x, y, radius=3000, page_no=1, num_rows=100):
    """좌표 반경 내 상가업소 목록 조회. 키 없음/실패 시 None."""
    api_key = os.environ.get(SBIZ_API_KEY_ENV)
    if not api_key:
        return None
    try:
        params = {
            'serviceKey': api_key,
            'cx': x,
            'cy': y,
            'radius': radius,
            'type': 'json',
            'numOfRows': num_rows,
            'pageNo': page_no,
        }
        url = SBIZ_BASE + '?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read().decode('utf-8')
        data = json.loads(raw)
        if 'OpenAPI_ServiceResponse' in data:
            err = data['OpenAPI_ServiceResponse'].get('cmmMsgHeader', {})
            print(f"[SBIZ API ERROR] {err.get('errMsg')}: {err.get('returnAuthMsg')}")
            return None
        header = data.get('header', {})
        if header.get('resultCode') not in (None, '00'):
            print(f"[SBIZ API ERROR] {header.get('resultCode')}: {header.get('resultMsg')}")
            return None
        # 실제 응답은 'response' 래퍼 없이 최상위에 바로 header/body가 온다
        # (2026-08-31 실키로 확인: {"header":..., "body":{"items":[...]}})
        body = data.get('body', {})
        items = body.get('items', [])
        if isinstance(items, dict):
            items = items.get('item', [])
        if isinstance(items, dict):
            items = [items]
        DIAG['sbiz_total_count'] = body.get('totalCount')
        return items or []
    except Exception as e:
        print(f"[SBIZ API FAIL] {e}")
        return None


def search_all_stores_in_radius(x, y, radius=3000, page_size=1000, max_pages=6):
    """반경 내 상가업소를 페이지를 넘겨가며 모두 조회. 실패 시 None.

    한 페이지(500건)만 보고 판단하면 밀집 상권에서 경쟁 매장이 뒤 페이지에
    있을 때 '0건'으로 확정해버린다(실측: 분당 서현동 3km에서 정확히 500건
    반환 = 잘림 확인). 페이지를 끝까지 넘겨 실제 전수를 본다.

    max_pages로 상한을 둬 서버리스 응답 시간이 무한정 늘어나는 것을 막고,
    상한에 걸리면 그 사실을 DIAG에 남겨 호출부가 '전수 아님'을 알 수 있게 한다.
    """
    collected = []
    for page in range(1, max_pages + 1):
        items = search_stores_in_radius(x, y, radius=radius, page_no=page, num_rows=page_size)
        if items is None:
            # 첫 페이지부터 실패면 판정 불가, 중간 실패면 지금까지 모은 것을 쓴다
            return None if page == 1 else collected
        collected.extend(items)
        if len(items) < page_size:
            DIAG['sbiz_paged_complete'] = True
            return collected
    DIAG['sbiz_paged_complete'] = False
    print(f"[SBIZ PAGING] 상한 {max_pages}페이지 도달 — 전수가 아닐 수 있음")
    return collected


def _norm(store):
    """원본 상가업소 레코드를 프로젝트 공통 competitor 스키마로 변환."""
    name = store.get('bizesNm') or store.get('bizesnm') or store.get('상호명') or '이름 미상'
    # 주소 필드명이 문서로 확정되지 않아 후보를 넓게 본다. 그래도 못 찾으면
    # 값 자체가 주소처럼 생긴 필드를 찾는다(보고서에 주소가 공란으로 나가던 문제).
    # 필드명은 2026-09-03 실키 응답으로 확정: rdnmAdr(도로명), lnoAdr(지번),
    # bizesNm(상호), indsSclsNm(업종소분류), ctprvnNm/signguNm/adongNm(행정구역)
    addr = (store.get('rdnmAdr') or store.get('rdnmadr') or store.get('lnoAdr')
            or store.get('lnoadr') or store.get('adres') or store.get('newAddr')
            or store.get('jibunAddr') or '')
    if not addr:
        for k, v in store.items():
            if not isinstance(v, str) or len(v) < 6:
                continue
            if ('로 ' in v or '길 ' in v or v.endswith('로') or v.endswith('길')) and                     any(t in v for t in ('시', '군', '구')):
                addr = v
                break
    category = store.get('indsSclsNm') or store.get('indsMclsNm') or store.get('indsLclsNm') or ''
    return {'name': name, 'address': addr, 'category': category, 'raw': store}


def find_golf_competitors(x, y, radius=3000):
    """반경 내 골프/스크린골프 관련 업소만 필터링. 실패 시 None.

    밀집 상권은 3km 반경에 상가업소가 만 단위로 잡혀 골프 관련 업소가
    상위 100건 안에 없을 수 있어 500건까지 조회한다
    (2026-08-31 전주 완산구 실키 테스트: 100건 내 0건, 500건 내 5건 확인)."""
    # 페이지를 끝까지 넘겨 전수를 본다(한 페이지만 보면 뒤 페이지의 매장을
    # 놓친 채 '0건 = 블루오션'으로 확정해버린다).
    items = search_all_stores_in_radius(x, y, radius=radius)
    if items is None:
        return None
    if DIAG.get('sbiz_paged_complete') is False:
        # 전수를 못 봤으면 0건을 확정하지 않는다
        _found = [it for it in items
                  if is_park_golf(_norm(it)['name'], _norm(it)['category'])]
        if not _found:
            return None
    # 예전에는 '골프' 두 글자만 걸리면 전부 경쟁매장으로 실어, 골프용품 소매점과
    # 골프의류점까지 '경쟁 매장' 카드에 올라갔다. 업태가 다른 곳은 경쟁이 아니므로
    # 실내 시뮬레이터 업태(직접 경쟁)만 남기고, 나머지는 참고 업종으로 분리한다.
    direct, related = [], []
    for it in items:
        norm = _norm(it)
        blob = (norm['category'] or '') + ' ' + (norm['name'] or '')
        entry = {
            'name': norm['name'],
            'address': norm['address'],
            'system': f"소상공인 상가정보 등록 업종: {norm['category']}" if norm['category'] else '업종 미상',
            'rooms': 0,
            'features': f"공공데이터(소상공인시장진흥공단) 상가업소 DB 등록 (업종: {norm['category'] or '미상'})",
            'status': '공공DB 등록 확인',
            'category': norm['category'] or '',
        }
        if is_park_golf(norm['name'], norm['category']):
            direct.append(entry)
        elif any(kw in blob for kw in GOLF_KEYWORDS):
            related.append(entry)
    # 직접 경쟁이 하나도 없으면 그 사실 자체가 결과다(참고 업종을 경쟁으로 올리지 않음).
    return direct


def find_related_golf_businesses(x, y, radius=3000):
    """직접 경쟁은 아니지만 골프 수요를 보여주는 참고 업종(용품점 등). 실패 시 None."""
    items = search_all_stores_in_radius(x, y, radius=radius)
    if items is None:
        return None
    out = []
    for it in items:
        norm = _norm(it)
        blob = (norm['category'] or '') + ' ' + (norm['name'] or '')
        if is_park_golf(norm['name'], norm['category']):
            continue
        if any(kw in blob for kw in GOLF_KEYWORDS):
            out.append({'name': norm['name'], 'address': norm['address'],
                        'category': norm['category'] or '미상'})
    return out


def industry_mix(x, y, radius=3000, top_n=8):
    """반경 내 업종 구성비 집계 (시니어 동선 업종 밀집도 분석용). 실패 시 None."""
    items = search_all_stores_in_radius(x, y, radius=radius)
    if items is None:
        return None
    DIAG['sbiz_returned'] = len(items)
    if items:
        DIAG['sbiz_item_keys'] = sorted(items[0].keys())
    counts = {}
    for it in items:
        norm = _norm(it)
        cat = norm['category'] or '기타'
        counts[cat] = counts.get(cat, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    total = len(items)
    # 상한에 걸렸으면 구성비가 전체 상권을 대표하지 않는다. 호출부가 알 수 있게
    # 표시한다(정확히 500이면 잘린 것).
    truncated = total >= 500
    return {
        'truncated': truncated,
        'total_stores': total,
        'top_categories': [{'category': c, 'count': n, 'ratio': round(n / total * 100.0, 1) if total else 0.0} for c, n in ranked]
    }
