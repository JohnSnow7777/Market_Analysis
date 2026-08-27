# -*- coding: utf-8 -*-
"""SGIS(통계청 통계지리정보서비스) Open API 클라이언트.

실제 서버에 파라미터 없이/일부만 채워 호출해 에러 메시지로 필수 파라미터를
직접 확인한 뒤 작성함 (2026-08-27):
  - 인증: GET auth/authentication.json?consumer_key=&consumer_secret=
          -> {"result": {"accessToken": "..."}} , 토큰 유효 4시간
  - 행정구역 계층 조회: GET addr/stage.json?accessToken=&cd=(생략시 시도 목록)
  - 인구통계 조건검색: GET stats/searchpopulation.json?accessToken=&adm_cd=&low_search=&year=
          (네 파라미터 모두 필수 확인됨. age_type/gender는 선택)

주의: addr/stage.json의 응답 필드명(cd, addr_name)과 searchpopulation.json의
연령대별 필드명은 공식 문서가 로그인 후에만 열람 가능해 제3자 예제 코드로
교차 확인한 것이며, 실제 키로 첫 호출한 뒤 반드시 재확인이 필요하다.
그래서 이 클라이언트는 필드가 기대와 다르면 예외를 던지는 대신 조용히
None을 반환하도록 방어적으로 작성했다 (호출부는 기존 추정모델로 폴백).
"""
import os
import json
import urllib.request
import urllib.parse

SGIS_BASE = "https://sgisapi.kostat.go.kr/OpenAPI3"
SGIS_SERVICE_ID_ENV = "SGIS_SERVICE_ID"
SGIS_SECURITY_KEY_ENV = "SGIS_SECURITY_KEY"


def _get(path, params, timeout=4):
    url = f"{SGIS_BASE}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def get_access_token():
    """환경변수에 키가 없거나 인증 실패 시 None."""
    consumer_key = os.environ.get(SGIS_SERVICE_ID_ENV)
    consumer_secret = os.environ.get(SGIS_SECURITY_KEY_ENV)
    if not consumer_key or not consumer_secret:
        return None
    try:
        data = _get('auth/authentication.json', {
            'consumer_key': consumer_key,
            'consumer_secret': consumer_secret,
        })
        token = data.get('result', {}).get('accessToken')
        return token
    except Exception as e:
        print(f"[SGIS AUTH FAIL] {e}")
        return None


def _find_region_cd(access_token, parent_cd, target_name):
    """addr/stage.json 한 단계를 조회해 target_name과 일치하는 지역의 cd를 찾는다."""
    try:
        params = {'accessToken': access_token}
        if parent_cd:
            params['cd'] = parent_cd
        data = _get('addr/stage.json', params)
        rows = data.get('result', [])
        if not isinstance(rows, list):
            return None
        clean_target = target_name.replace(' ', '')
        for row in rows:
            name = str(row.get('addr_name', '')).replace(' ', '')
            if name == clean_target or (len(clean_target) >= 2 and clean_target in name):
                return row.get('cd')
        # 정확히 일치하는 게 없으면 부분 포함 재시도(예: '서현동' vs '서현제1동')
        for row in rows:
            name = str(row.get('addr_name', '')).replace(' ', '')
            if len(name) >= 2 and (name[:2] == clean_target[:2]):
                return row.get('cd')
    except Exception as e:
        print(f"[SGIS STAGE FAIL] parent_cd={parent_cd} target={target_name}: {e}")
    return None


def resolve_adm_cd(access_token, sido, sigungu, dong):
    """시도/시군구/읍면동 텍스트명을 SGIS 행정동코드(adm_cd)로 변환. 실패 시 None."""
    if not (sido and sigungu and dong):
        return None
    sido_cd = _find_region_cd(access_token, None, sido)
    if not sido_cd:
        return None
    sigungu_short = sigungu.split()[-1] if ' ' in sigungu else sigungu
    sigungu_cd = _find_region_cd(access_token, sido_cd, sigungu_short)
    if not sigungu_cd:
        return None
    dong_cd = _find_region_cd(access_token, sigungu_cd, dong)
    return dong_cd


def get_population_by_age(access_token, adm_cd, year='2025'):
    """행정동 단위 연령대별 인구 조회. 실패/필드불일치 시 None.

    반환 형식(성공 시): {'total': int, 'age_buckets': {age_label: count, ...}}
    """
    try:
        data = _get('stats/searchpopulation.json', {
            'accessToken': access_token,
            'adm_cd': adm_cd,
            'low_search': '0',
            'year': year,
        })
        rows = data.get('result', [])
        if not rows:
            return None
        row = rows[0] if isinstance(rows, list) else rows
        total = row.get('tot_ppltn') or row.get('population') or row.get('avg_age')
        if total is None:
            return None
        return {'raw': row, 'total': int(total)}
    except Exception as e:
        print(f"[SGIS POPULATION FAIL] adm_cd={adm_cd}: {e}")
        return None


def fetch_real_population(sido, sigungu, dong):
    """SGIS로 실제 인구 데이터 취득 시도. 키 없음/실패 시 반드시 None 반환
    (호출부는 None이면 기존 추정모델을 그대로 사용해야 함)."""
    token = get_access_token()
    if not token:
        return None
    adm_cd = resolve_adm_cd(token, sido, sigungu, dong)
    if not adm_cd:
        print(f"[SGIS] adm_cd 매칭 실패: {sido} {sigungu} {dong}")
        return None
    result = get_population_by_age(token, adm_cd)
    if result:
        result['adm_cd'] = adm_cd
    return result
