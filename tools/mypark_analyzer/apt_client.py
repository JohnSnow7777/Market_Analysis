# -*- coding: utf-8 -*-
"""국토교통부 공동주택 기본정보/단지목록 API 클라이언트 (공공데이터포털).

엔드포인트/필드는 실제 서버에 실키로 호출해 확인함(2026-08-31):
  단지목록: https://apis.data.go.kr/1613000/AptListService4/getSigunguAptList4
            ?serviceKey=&sigunguCode=&pageNo=&numOfRows=&type=json
            -> {"response":{"body":{"items":[{"kaptCode","kaptName","bjdCode",
                "as1"(시도),"as2"(시군구),"as3"(읍면동),"as4"(리)}], "totalCount"}}}
  기본정보: https://apis.data.go.kr/1613000/AptBasisInfoServiceV5/getAphusBassInfoV5
            ?serviceKey=&kaptCode=
            -> {"response":{"body":{"item":{"kaptdaCnt"(세대수),"hoCnt"(세대수),
                "kaptUsedate"(사용승인일 YYYYMMDD),"kaptDongCnt"(동수), ...}}}}

sigunguCode(법정동코드 앞5자리)는 카카오 지오코딩의 b_code로 구한다
(competitor_engine.CompetitorEngine.geocode_address_bcode).
"""
import os
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

APT_LIST_URL = "https://apis.data.go.kr/1613000/AptListService4/getSigunguAptList4"
APT_INFO_URL = "https://apis.data.go.kr/1613000/AptBasisInfoServiceV5/getAphusBassInfoV5"
APT_API_KEY_ENV = "DATA_GO_KR_API_KEY"

# 소상공인 API와 동일 계정 키를 공유하되, 별도 활용신청이 안 되어 있으면
# NO_OPENAPI_SERVICE_ERROR가 나므로 그 경우도 실패(None)로 조용히 처리한다.
MAX_DETAIL_COMPLEXES = 15


def _get(url, params):
    full_url = url + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=6) as resp:
        raw = resp.read().decode('utf-8')
    data = json.loads(raw)
    if 'OpenAPI_ServiceResponse' in data:
        err = data['OpenAPI_ServiceResponse'].get('cmmMsgHeader', {})
        print(f"[APT API ERROR] {err.get('errMsg')}: {err.get('returnAuthMsg')}")
        return None
    header = data.get('response', {}).get('header', {})
    if header.get('resultCode') not in (None, '00'):
        print(f"[APT API ERROR] {header.get('resultCode')}: {header.get('resultMsg')}")
        return None
    return data.get('response', {}).get('body', {})


def get_apt_list(sigungu_code, num_rows=200):
    """시군구(법정동코드 앞5자리) 내 공동주택 단지 목록. 키 없음/실패 시 None."""
    api_key = os.environ.get(APT_API_KEY_ENV)
    if not api_key:
        return None
    try:
        body = _get(APT_LIST_URL, {
            'serviceKey': api_key,
            'sigunguCode': sigungu_code,
            'pageNo': 1,
            'numOfRows': num_rows,
        })
        if body is None:
            return None
        items = body.get('items', [])
        if isinstance(items, dict):
            items = items.get('item', [])
        if isinstance(items, dict):
            items = [items]
        return items or []
    except Exception as e:
        print(f"[APT LIST FAIL] {e}")
        return None


def get_apt_basis(kapt_code):
    """단지코드로 세대수/준공년도 등 기본정보 조회. 실패 시 None."""
    api_key = os.environ.get(APT_API_KEY_ENV)
    if not api_key:
        return None
    try:
        body = _get(APT_INFO_URL, {'serviceKey': api_key, 'kaptCode': kapt_code})
        if body is None:
            return None
        return body.get('item')
    except Exception as e:
        print(f"[APT INFO FAIL] {e}")
        return None


def fetch_apt_summary(sigungu_code, dong_name):
    """행정동 기준 공동주택 현황 요약. 키 없음/좌표실패/API실패 시 None
    (호출부는 None이면 이 항목을 보고서에서 생략해야 함).

    반환: {'complex_count': int, 'sample_count': int, 'total_households_sample': int,
           'year_min': int, 'year_max': int, 'scope_label': str}
    """
    if not sigungu_code:
        return None
    items = get_apt_list(sigungu_code)
    if not items:
        return None

    dong_matched = [it for it in items if dong_name and dong_name in (it.get('as3') or '')]
    if dong_matched:
        target = dong_matched
        scope_label = f"{dong_name} 소재"
    else:
        # 법정동/행정동 표기 차이로 매칭 안 될 수 있어, 시군구 전체로 대체하되
        # 라벨을 정직하게 구분한다 (3km 생활권과 다른 범위임을 명시)
        target = items
        scope_label = "행정구역(시/군/구) 전체 기준"

    sample = target[:MAX_DETAIL_COMPLEXES]
    households = []
    years = []
    # 단지 상세는 단지마다 1회씩 조회해야 하는데, 순차로 돌면 15회가 그대로
    # 쌓여 실측 10~11초(전체 응답의 3분의 1 이상)를 차지했다. 서로 독립적인
    # 조회라 병렬로 보낸다. 실패한 단지는 기존처럼 조용히 건너뛴다.
    with ThreadPoolExecutor(max_workers=8) as _ex:
        _infos = list(_ex.map(
            lambda it: (it, get_apt_basis(it.get('kaptCode')) if it.get('kaptCode') else None),
            sample))
    for it, info in _infos:
        if not info:
            continue
        hc = info.get('kaptdaCnt') or info.get('hoCnt')
        if hc:
            try:
                households.append(int(float(hc)))
            except (ValueError, TypeError):
                pass
        yr = info.get('kaptUsedate')
        if yr and len(str(yr)) >= 4:
            try:
                years.append(int(str(yr)[:4]))
            except ValueError:
                pass

    if not households:
        return None

    return {
        'complex_count': len(target),
        'sample_count': len(households),
        'total_households_sample': sum(households),
        'year_min': min(years) if years else None,
        'year_max': max(years) if years else None,
        'scope_label': scope_label,
    }
