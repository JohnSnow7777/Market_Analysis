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
SBIZ_BASE = "https://apis.data.go.kr/B553077/api/open/sdsc2/storeListInRadius"

# 스크린 파크골프 반경 경쟁사 탐지에 쓰는 업종 키워드
# (표준산업분류/상권업종 명칭에 아래 키워드가 들어가면 경쟁/유사 업종으로 간주)
GOLF_KEYWORDS = ['골프', '스크린골프', '파크골프']


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
        return items or []
    except Exception as e:
        print(f"[SBIZ API FAIL] {e}")
        return None


def _norm(store):
    """원본 상가업소 레코드를 프로젝트 공통 competitor 스키마로 변환."""
    name = store.get('bizesNm') or store.get('bizesnm') or store.get('상호명') or '이름 미상'
    addr = store.get('rdnmadr') or store.get('lnoadr') or store.get('adres') or ''
    category = store.get('indsSclsNm') or store.get('indsMclsNm') or store.get('indsLclsNm') or ''
    return {'name': name, 'address': addr, 'category': category, 'raw': store}


def find_golf_competitors(x, y, radius=3000):
    """반경 내 골프/스크린골프 관련 업소만 필터링. 실패 시 None.

    밀집 상권은 3km 반경에 상가업소가 만 단위로 잡혀 골프 관련 업소가
    상위 100건 안에 없을 수 있어 500건까지 조회한다
    (2026-08-31 전주 완산구 실키 테스트: 100건 내 0건, 500건 내 5건 확인)."""
    items = search_stores_in_radius(x, y, radius=radius, num_rows=500)
    if items is None:
        return None
    out = []
    for it in items:
        norm = _norm(it)
        if any(kw in norm['category'] for kw in GOLF_KEYWORDS) or any(kw in norm['name'] for kw in GOLF_KEYWORDS):
            out.append({
                'name': norm['name'],
                'address': norm['address'],
                'system': f"소상공인 상가정보 등록 업종: {norm['category']}" if norm['category'] else '업종 미상',
                'rooms': 0,
                'features': f"공공데이터(소상공인시장진흥공단) 상가업소 DB 등록 확인 (업종: {norm['category'] or '미상'})",
                'status': '공공DB 등록 확인'
            })
    return out


def industry_mix(x, y, radius=3000, top_n=8):
    """반경 내 업종 구성비 집계 (시니어 동선 업종 밀집도 분석용). 실패 시 None."""
    items = search_stores_in_radius(x, y, radius=radius, num_rows=500)
    if items is None:
        return None
    counts = {}
    for it in items:
        norm = _norm(it)
        cat = norm['category'] or '기타'
        counts[cat] = counts.get(cat, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    total = len(items)
    return {
        'total_stores': total,
        'top_categories': [{'category': c, 'count': n, 'ratio': round(n / total * 100.0, 1) if total else 0.0} for c, n in ranked]
    }
