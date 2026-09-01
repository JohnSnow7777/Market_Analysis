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


def list_dongs_in_sigungu(access_token, sido, sigungu, limit=8):
    """시도/시군구 산하 실제 행정동 목록을 조회. 실패 시 None.

    사용자가 동을 특정하지 않고 '구/군' 단위만 입력했을 때, 가짜 동
    이름("사업권역1동" 등)을 지어내는 대신 SGIS에 실제로 존재하는
    행정동 이름과 adm_cd를 그대로 써서 대표 동을 고르는 데 쓴다.
    반환: [{'name': str, 'adm_cd': str}, ...] 또는 None.
    """
    if not (sido and sigungu):
        return None
    try:
        sido_cd = _find_region_cd(access_token, None, sido)
        if not sido_cd:
            return None
        sigungu_short = sigungu.split()[-1] if ' ' in sigungu else sigungu
        sigungu_cd = _find_region_cd(access_token, sido_cd, sigungu_short)
        if not sigungu_cd:
            return None
        data = _get('addr/stage.json', {'accessToken': access_token, 'cd': sigungu_cd})
        rows = data.get('result', [])
        if not isinstance(rows, list) or not rows:
            return None
        out = []
        for row in rows:
            name = row.get('addr_name')
            cd = row.get('cd')
            if name and cd and name.endswith(('동', '읍', '면')):
                out.append({'name': name, 'adm_cd': cd})
        return out[:limit] if out else None
    except Exception as e:
        print(f"[SGIS DONG LIST FAIL] sido={sido} sigungu={sigungu}: {e}")
        return None


def fetch_district_population(sido, sigungu):
    """시군구(구/군) 단위 실제 인구를 SGIS에서 조회. 실패 시 None.

    "광주광역시 서구"처럼 동을 특정하지 않은 구 전체 분석용. 동을 하나씩
    N번 조회하는 대신 searchpopulation을 시군구 코드로 두 번만 호출한다:
      - low_search='0' -> 그 구 자체의 총인구 (구 전체 합계의 정답)
      - low_search='1' -> 산하 행정동별 인구 (표에 보여줄 내역)
    구 전체 합계는 반드시 low_search='0' 값을 쓴다. 동별 목록은 표시용이며,
    일부 동이 누락돼도 합계가 틀어지지 않도록 분리해서 관리한다.

    반환: {'total': int, 'sigungu_cd': str, 'year': str,
           'dongs': [{'name': str, 'adm_cd': str, 'total': int}, ...]} 또는 None
    """
    token = get_access_token()
    if not token or not (sido and sigungu):
        return None
    try:
        sido_cd = _find_region_cd(token, None, sido)
        if not sido_cd:
            return None
        sigungu_short = sigungu.split()[-1] if ' ' in sigungu else sigungu
        sigungu_cd = _find_region_cd(token, sido_cd, sigungu_short)
        if not sigungu_cd:
            return None

        district = get_population_by_age(token, sigungu_cd)
        if not district or district.get('total', 0) <= 0:
            return None

        # 관할 행정동 목록/개수는 addr/stage.json에서 받는다. 이 경로는 실제 키로
        # 응답 형식을 확인한 적이 있어 신뢰할 수 있고, "구 전체 N개 동"의 N을
        # 정확히 세는 것이 채점 보정(생활권 환산)의 전제라 반드시 확보해야 한다.
        dong_names = []
        try:
            stage = _get('addr/stage.json', {'accessToken': token, 'cd': sigungu_cd}, timeout=6)
            rows = stage.get('result', [])
            if isinstance(rows, list):
                for row in rows:
                    nm = row.get('addr_name')
                    cd = row.get('cd')
                    if nm and cd and str(nm).endswith(('동', '읍', '면')):
                        dong_names.append({'name': str(nm), 'adm_cd': cd})
        except Exception as e:
            print(f"[SGIS DONG NAMES FAIL] {sigungu_cd}: {e}")

        # 동별 인구 내역(선택). 응답 필드명이 확인되지 않아 실패할 수 있으므로
        # 실패해도 구 총인구/동 개수에는 영향이 없도록 완전히 분리한다.
        pop_by_cd = {}
        try:
            data = _get('stats/searchpopulation.json', {
                'accessToken': token,
                'adm_cd': sigungu_cd,
                'low_search': '1',
                'year': district['year'],
            }, timeout=8)
            rows = data.get('result', [])
            if isinstance(rows, list):
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    cd = row.get('adm_cd') or row.get('cd')
                    tot = row.get('tot_ppltn') or row.get('population')
                    if cd and tot:
                        try:
                            pop_by_cd[str(cd)] = int(float(tot))
                        except (TypeError, ValueError):
                            continue
            if not pop_by_cd:
                print(f"[SGIS LOW_SEARCH SHAPE] rows={str(rows)[:300]}")
        except Exception as e:
            print(f"[SGIS DONG BREAKDOWN FAIL] {sigungu_cd}: {e}")

        dongs = []
        for d in dong_names:
            tot = pop_by_cd.get(str(d['adm_cd']))
            if tot:
                dongs.append({'name': d['name'], 'adm_cd': d['adm_cd'], 'total': tot})
        dongs.sort(key=lambda d: d['total'], reverse=True)

        return {
            'total': district['total'],
            'sigungu_cd': sigungu_cd,
            'year': district['year'],
            'dong_count': len(dong_names),
            'dong_names': [d['name'] for d in dong_names],
            'dongs': dongs,
        }
    except Exception as e:
        print(f"[SGIS DISTRICT POP FAIL] {sido} {sigungu}: {e}")
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


def get_population_by_age(access_token, adm_cd, year=None):
    """행정동 단위 연령대별 인구 조회. 실패/필드불일치 시 None.

    SGIS 인구통계는 집계·공표 주기상 항상 '작년' 자료까지만 존재한다
    (예: 2026년에 연도 2026을 넣으면 "년도 정보를 확인해주세요" 에러 발생,
    2026-08-27 실키로 실제 확인함). year 미지정 시 작년부터 최대 3개년을
    역순으로 시도해 향후 연도가 바뀌어도 재수정 없이 최신 가용 연도를 쓴다.

    반환 형식(성공 시): {'total': int, 'age_buckets': {age_label: count, ...}}
    """
    import datetime
    years_to_try = [str(year)] if year else [str(datetime.datetime.now().year - i) for i in (1, 2, 3)]
    for yr in years_to_try:
        try:
            data = _get('stats/searchpopulation.json', {
                'accessToken': access_token,
                'adm_cd': adm_cd,
                'low_search': '0',
                'year': yr,
            })
            rows = data.get('result', [])
            if not rows:
                continue
            row = rows[0] if isinstance(rows, list) else rows
            total = row.get('tot_ppltn') or row.get('population') or row.get('avg_age')
            if total is None:
                continue
            return {'raw': row, 'total': int(total), 'year': yr}
        except Exception as e:
            print(f"[SGIS POPULATION FAIL] adm_cd={adm_cd} year={yr}: {e}")
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
