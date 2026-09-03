# -*- coding: utf-8 -*-
"""TMap(SK Open API) + 네이버 지역검색 POI 클라이언트.

  - TMap POI 반경검색: GET https://apis.openapi.sk.com/tmap/pois
        ?version=1&searchKeyword=&centerLon=&centerLat=&radius=(km)&appKey=
    -> 더미 appKey로 {"error":{"code":"INVALID_API_KEY"}} (403) 확인(2026-08-27).
       실키 미보유 상태라 필드명은 공식 문서 기준, 첫 실호출 시 재확인 필요.
  - 네이버 지역검색: 기존 개발자센터 엔드포인트(openapi.naver.com/v1/search/local.json,
    X-Naver-Client-Id/Secret 헤더)는 2026-07-31부로 신규발급 차단되어 폐지 수순.
    NAVER API HUB(NCP)로 이관된 신규 엔드포인트로 실키 호출까지 확인함(2026-08-31):
        GET https://naverapihub.apigw.ntruss.com/search/v1/local
        헤더: X-NCP-APIGW-API-KEY-ID, X-NCP-APIGW-API-KEY (NCP Client ID/Secret)
        파라미터: query, display, start, sort, format
    응답 구조(items[].title/address/roadAddress)는 기존과 동일, 실키로 확인됨.

전부 .get()으로 방어해 필드가 다르면 그 값만 비어 보일 뿐 예외를 던지지 않는다.
"""
import os
DIAG = {}  # [임시 진단] 확인 후 제거
import re
import json
import urllib.request
import urllib.parse

TMAP_APP_KEY_ENV = "TMAP_APP_KEY"
NAVER_CLIENT_ID_ENV = "NAVER_CLIENT_ID"
NAVER_CLIENT_SECRET_ENV = "NAVER_CLIENT_SECRET"


def tmap_poi_search(query, x, y, radius_km=3, timeout=4):
    """TMap 반경 POI 검색. 반환: (성공여부, 결과리스트). 키 없으면 (False, [])."""
    app_key = os.environ.get(TMAP_APP_KEY_ENV)
    if not app_key:
        return False, []
    try:
        params = {
            'version': 1,
            'searchKeyword': query,
            'centerLon': x,
            'centerLat': y,
            'radius': radius_km,
            'reqCoordType': 'WGS84GEO',
            'resCoordType': 'WGS84GEO',
            'count': 10,
        }
        url = "https://apis.openapi.sk.com/tmap/pois?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={'appKey': app_key, 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        pois = data.get('searchPoiInfo', {}).get('pois', {}).get('poi', [])
        if isinstance(pois, dict):
            pois = [pois]
        out = []
        for p in pois:
            addr_list = p.get('newAddressList', {}).get('newAddress', [])
            road_addr = addr_list[0].get('fullAddressRoad', '') if addr_list else ''
            out.append({
                'name': p.get('name', '이름 미상'),
                'address': road_addr or p.get('upperAddrName', '') + ' ' + p.get('middleAddrName', ''),
                'source': 'TMap',
            })
        return True, out
    except Exception as e:
        print(f"[TMAP API FAIL] {e}")
        return False, []


def naver_local_search(query, region_hint='', display=10, timeout=4):
    """네이버 지역검색 (좌표 반경 필터 미지원, 키워드+지역명 조합). 반환: (성공여부, 결과리스트)."""
    client_id = os.environ.get(NAVER_CLIENT_ID_ENV)
    client_secret = os.environ.get(NAVER_CLIENT_SECRET_ENV)
    if not (client_id and client_secret):
        return False, []
    try:
        q = f"{region_hint} {query}".strip()
        params = {'query': q, 'display': display}
        url = "https://naverapihub.apigw.ntruss.com/search/v1/local?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={
            'X-NCP-APIGW-API-KEY-ID': client_id,
            'X-NCP-APIGW-API-KEY': client_secret,
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        items = data.get('items', [])
        DIAG['naver_count'] = len(items)
        if items:
            DIAG['naver_keys'] = sorted(items[0].keys())
            DIAG['naver_addr_sample'] = items[0].get('roadAddress') or items[0].get('address')
        out = []
        for it in items:
            name = re.sub('<[^<]+?>', '', it.get('title', '이름 미상'))
            out.append({
                'name': name,
                'address': it.get('roadAddress') or it.get('address', ''),
                'source': '네이버',
            })
        return True, out
    except Exception as e:
        print(f"[NAVER API FAIL] {e}")
        return False, []


def _normalize_name(name):
    return re.sub(r'[\s()（）·\-]', '', name or '').lower()


def merge_dedup(*store_lists):
    """여러 소스의 결과를 상호명 유사도로 중복 제거하며 병합."""
    merged = []
    seen = []
    for stores in store_lists:
        for s in stores:
            key = _normalize_name(s['name'])
            if not key:
                continue
            is_dup = any(key in k or k in key for k in seen if len(key) >= 2 and len(k) >= 2)
            if not is_dup:
                seen.append(key)
                merged.append(s)
    return merged
