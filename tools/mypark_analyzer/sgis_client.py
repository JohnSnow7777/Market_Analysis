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


class _CallBudget:
    """API 호출 횟수 상한을 들고 다니는 카운터.

    Vercel 서버리스에서 전체 요청이 수십 초 안에 끝나야 하는데, 산하에 구가
    여러 개인 시(구마다 stage 조회가 추가됨)에서는 호출이 쉽게 불어난다.
    그래서 호출 지점마다 남은 예산을 물어보고, 예산이 없으면 '동 이름 수집'
    같은 부가 작업만 조용히 포기하도록 한다(총인구/동 개수는 먼저 확보).
    """

    def __init__(self, limit=15):
        self.limit = limit
        self.used = 0

    def take(self, n=1):
        """n회를 쓸 여유가 있으면 차감하고 True, 없으면 False(호출 자체를 생략)."""
        if self.used + n > self.limit:
            return False
        self.used += n
        return True


def _row_name(row):
    """stage/population 응답의 지역명 필드명이 문서로 확정되지 않아 후보를 모두 본다."""
    if not isinstance(row, dict):
        return None
    for key in ('addr_name', 'adm_nm', 'adm_name', 'nm', 'name'):
        val = row.get(key)
        if val:
            return str(val).strip()
    return None


def _row_cd(row):
    """지역코드 필드명도 마찬가지로 여러 후보를 관대하게 받는다."""
    if not isinstance(row, dict):
        return None
    for key in ('cd', 'adm_cd', 'adm_code', 'code'):
        val = row.get(key)
        if val:
            return str(val).strip()
    return None


def _stage_rows(access_token, cd, budget=None, timeout=6):
    """addr/stage.json 한 단계를 조회해 [(이름, 코드), ...]로 정규화. 실패 시 []."""
    if budget is not None and not budget.take():
        return []
    try:
        params = {'accessToken': access_token}
        if cd:
            params['cd'] = cd
        data = _get('addr/stage.json', params, timeout=timeout)
        rows = data.get('result', [])
        if not isinstance(rows, list):
            return []
        out = []
        for row in rows:
            nm = _row_name(row)
            rc = _row_cd(row)
            if nm and rc:
                out.append((nm, rc))
        return out
    except Exception as e:
        print(f"[SGIS STAGE FAIL] cd={cd}: {e}")
        return []


def _classify_sub_level(rows):
    """하위 목록이 '읍면동'인지 '구'인지를 응답에 실제로 들어있는 이름으로 판별.

    SGIS 코드 자릿수 체계를 추측하지 않고 이름 접미사만 본다.
    - 읍/면/동으로 끝나는 항목이 하나라도 있으면 'dong'
      (동이 있으면 그 계층이 최말단이므로 더 내려갈 필요가 없다)
    - 그렇지 않고 '구'로 끝나는 항목이 있으면 'gu' (성남시·창원시처럼 시 밑에 구)
    - 둘 다 아니면 'unknown' -> 하강하지 않고 조용히 포기
    """
    has_dong = any(nm.endswith(('동', '읍', '면')) for nm, _ in rows)
    if has_dong:
        return 'dong'
    if any(nm.endswith('구') for nm, _ in rows):
        return 'gu'
    return 'unknown'


def _find_region_named(access_token, parent_cd, target_name):
    """_find_region_cd와 같지만 (cd, 실제로 매칭된 지역명)을 함께 돌려준다.

    '성남시'를 찾았는데 실제로는 '성남시 분당구'가 잡히는 식의 하위 구역 오매칭을
    호출부가 감지해야 해서, 매칭된 이름을 그대로 알려준다.
    """
    try:
        params = {'accessToken': access_token}
        if parent_cd:
            params['cd'] = parent_cd
        data = _get('addr/stage.json', params)
        rows = data.get('result', [])
        if not isinstance(rows, list):
            return None, None
        clean_target = target_name.replace(' ', '')
        for row in rows:
            name = str(row.get('addr_name', '')).replace(' ', '')
            if name == clean_target:
                return row.get('cd'), str(row.get('addr_name', ''))
        for row in rows:
            name = str(row.get('addr_name', '')).replace(' ', '')
            if len(clean_target) >= 2 and clean_target in name:
                return row.get('cd'), str(row.get('addr_name', ''))

    except Exception as e:
        print(f"[SGIS STAGE FAIL] parent_cd={parent_cd} target={target_name}: {e}")
    return None, None


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
        # 1순위: 정확히 일치. 부분 일치를 먼저 하면 '성남시'가 '성남시분당구'에
        # 걸려 시 전체 대신 특정 구가 잡히므로, 완전 일치를 반드시 우선한다.
        for row in rows:
            name = str(row.get('addr_name', '')).replace(' ', '')
            if name == clean_target:
                return row.get('cd')
        for row in rows:
            name = str(row.get('addr_name', '')).replace(' ', '')
            if len(clean_target) >= 2 and clean_target in name:
                return row.get('cd')
        # 앞 두 글자만 같은 지역을 반환하던 폴백은 제거했다. 요청한 동이 그 구에
        # 없을 때(상류에서 잘못된 동 이름이 넘어온 경우) 엉뚱한 동의 실측 인구를
        # 조용히 가져와 오염시키기 때문이다. 못 찾으면 못 찾았다고 하는 편이 낫다.
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

    행정 계층 깊이는 지역마다 다르다. 자치구/군은 산하가 바로 읍면동이지만
    성남시·창원시 같은 일반시는 산하가 먼저 '구'이고 그 밑에 동이 있다.
    그래서 하위 목록을 받아본 뒤 이름으로 계층을 판별하고, 구라면 한 단계
    더 내려가 동을 모은다(지역명 하드코딩 없이 응답만으로 판단).

    반환: {'total': int, 'sigungu_cd': str, 'year': str,
           'dong_count': int, 'dong_names': [str],
           'dongs': [{'name': str, 'adm_cd': str, 'total': int}, ...],
           'sub_level': 'dong'|'gu', 'gu_names': [str]} 또는 None
    """
    token = get_access_token()
    if not token or not sido:
        return None
    # 인증 1회 + _find_region_cd 2회는 이미 쓴 것으로 계산해 예산에 반영한다.
    budget = _CallBudget(limit=15)
    budget.take(3)
    try:
        sido_cd = _find_region_cd(token, None, sido)
        if not sido_cd:
            return None
        matched_name = None
        if sigungu:
            sigungu_short = sigungu.split()[-1] if ' ' in sigungu else sigungu
            sigungu_cd, matched_name = _find_region_named(token, sido_cd, sigungu_short)
            if not sigungu_cd:
                return None
        else:
            # 시/도만 입력된 경우("광주광역시"). 없는 시군구를 지어내지 않고
            # 시/도 자체를 집계 단위로 삼는다. 산하가 시군구라 _classify_sub_level이
            # 'gu'로 판별해 한 단계 더 내려가며, 동 이름까지 예산 안에서 모은다.
            sigungu_cd = sido_cd

        # 총인구는 항상 최상위 집계값(low_search='0')을 쓴다. 하위 동을 합산하면
        # 일부 누락 시 총계가 틀어지므로 계층 깊이와 무관하게 이 값만 신뢰한다.
        # 연도 탐색으로 내부에서 최대 3회 호출될 수 있어 예산에서 미리 뺀다.
        budget.take(3)
        district = get_population_by_age(token, sigungu_cd)
        if not district or district.get('total', 0) <= 0:
            return None

        # 관할 행정동 목록/개수는 addr/stage.json에서 받는다. "구 전체 N개 동"의 N을
        # 정확히 세는 것이 채점 보정(생활권 환산)의 전제라 반드시 확보해야 한다.
        sub_rows = _stage_rows(token, sigungu_cd, budget)
        sub_level = _classify_sub_level(sub_rows)

        dong_names = []
        gu_names = []
        if sub_level == 'dong':
            # 자치구/군: 산하가 바로 읍면동이므로 그대로 사용.
            for nm, cd in sub_rows:
                if nm.endswith(('동', '읍', '면')):
                    dong_names.append({'name': nm, 'adm_cd': cd})
        elif sub_level == 'gu':
            # 일반시: 구마다 한 단계 더 내려가야 동이 나온다. 구 수가 많으면
            # 남은 예산 안에서만 내려가고, 못 내려간 구는 조용히 건너뛴다.
            # (총인구는 이미 확보했으므로 결과가 틀리지는 않고 동 목록만 부분적)
            gu_names = [nm for nm, _ in sub_rows]
            for nm, cd in sub_rows:
                if budget.used >= budget.limit:
                    print(f"[SGIS BUDGET] 구 하강 중단 used={budget.used} gu={nm}")
                    break
                child_rows = _stage_rows(token, cd, budget)
                if not child_rows:
                    # 예산 소진이나 형식 불일치 — 나머지 구도 어차피 못 받는다.
                    if budget.used >= budget.limit:
                        print(f"[SGIS BUDGET] 구 하강 중단 used={budget.used}")
                        break
                    continue
                for c_nm, c_cd in child_rows:
                    if c_nm.endswith(('동', '읍', '면')):
                        dong_names.append({'name': c_nm, 'adm_cd': c_cd})
        else:
            print(f"[SGIS SUB LEVEL UNKNOWN] cd={sigungu_cd} rows={str(sub_rows[:3])[:200]}")

        # 동별 인구 내역(선택). 응답 필드명이 확인되지 않아 실패할 수 있으므로
        # 실패해도 구 총인구/동 개수에는 영향이 없도록 완전히 분리한다.
        # 산하가 구인 경우 low_search='1'은 '구별' 인구를 주므로 동 코드와 매칭되지
        # 않는다. 헛호출로 예산만 쓰지 않도록 산하가 읍면동일 때만 호출한다.
        pop_by_cd = {}
        try:
            if sub_level == 'dong' and budget.take():
                data = _get('stats/searchpopulation.json', {
                    'accessToken': token,
                    'adm_cd': sigungu_cd,
                    'low_search': '1',
                    'year': district['year'],
                }, timeout=8)
                rows = data.get('result', [])
                if isinstance(rows, list):
                    for row in rows:
                        cd = _row_cd(row)
                        tot = row.get('tot_ppltn') or row.get('population') if isinstance(row, dict) else None
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

        # 구역 면적(㎢). 검색 반경을 임의 상수 대신 실제 구역 크기에서 역산하려
        # 했으나, 2026-09-02 실제 응답 확인 결과 이 API는 adm_cd/adm_nm/population
        # 세 필드만 돌려주며 면적·인구밀도가 없다. 다른 응답 형식이나 향후 필드
        # 추가에 대비해 탐지 로직은 남겨두되, 없으면 조용히 None을 반환한다.
        area_km2 = None
        try:
            raw = district.get('raw') or {}
            for key in ('ppltn_dnsty', 'population_density', 'dnsty'):
                dnsty = raw.get(key)
                if dnsty:
                    dnsty = float(dnsty)
                    if dnsty > 0:
                        area_km2 = round(district['total'] / dnsty, 2)
                        break
            if area_km2 is None:
                print(f"[SGIS AREA MISS] density fields absent; raw keys={list(raw.keys())[:20]}")
        except Exception as e:
            print(f"[SGIS AREA CALC FAIL] {e}")

        return {
            'total': district['total'],
            'sigungu_cd': sigungu_cd,
            'year': district['year'],
            'dong_count': len(dong_names),
            'dong_names': [d['name'] for d in dong_names],
            'dongs': dongs,
            # 호출부가 "N개 동" 문구를 만들 때 계층을 알아야 해서 함께 돌려준다.
            'sub_level': sub_level,
            'gu_names': gu_names,
            'area_km2': area_km2,
            # SGIS에서 실제로 매칭된 지역명. 요청한 이름과 다르면(예: '성남시'를
            # 요청했는데 '성남시 분당구'가 잡힘) 호출부가 라벨을 실제 값에 맞춰
            # 고칠 수 있게 그대로 돌려준다 — 요청한 이름으로 표기하면 허위가 된다.
            'matched_region_name': (matched_name or '').strip(),
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
