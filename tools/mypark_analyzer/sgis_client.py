# -*- coding: utf-8 -*-
"""SGIS(통계청 통계지리정보서비스) Open API 클라이언트.

실제 서버에 파라미터 없이/일부만 채워 호출해 에러 메시지로 필수 파라미터를
직접 확인한 뒤 작성함 (2026-08-27):
  - 인증: GET auth/authentication.json?consumer_key=&consumer_secret=
          -> {"result": {"accessToken": "..."}} , 토큰 유효 4시간
  - 행정구역 계층 조회: GET addr/stage.json?accessToken=&cd=(생략시 시도 목록)
  - 인구통계 조건검색: GET stats/searchpopulation.json?accessToken=&adm_cd=&low_search=&year=
          (네 파라미터 모두 필수 확인됨. age_type/gender는 선택)

[2026-09-03 실키 응답으로 확정된 사양]
  searchpopulation.json 응답 항목: adm_cd, adm_nm, population (3개)
    예) {"adm_cd":"31023","adm_nm":"성남시 분당구","population":"447920"}
    - population은 문자열이다. 연령대별 분포는 제공하지 않는다.
    - avg_age(평균연령) 항목은 존재하지 않는다(총인구 폴백으로 쓰면 안 됨).
  addr/stage.json: 시/도 하위에 '성남시 분당구'처럼 시+구가 한 항목으로 온다.
    구 하위는 바로 읍면동이다(예: 구미1동, 금곡동, 백현동, 서현1동 …).

연령 분포가 없으므로 시니어 비중은 지역 체급별 추정 계수를 적용한다.
그 외 필드가 기대와 다르면 예외를 던지는 대신 조용히 None을 반환한다
(호출부는 기존 추정모델로 폴백).
"""
import os
import json
import time
import urllib.request
import urllib.parse

SGIS_BASE = "https://sgisapi.kostat.go.kr/OpenAPI3"
SGIS_SERVICE_ID_ENV = "SGIS_SERVICE_ID"
SGIS_SECURITY_KEY_ENV = "SGIS_SECURITY_KEY"

# SGIS 호출은 응답이 느려(1회당 1~2초) 순차 호출이 그대로 응답 시간이 된다.
# 실측 결과 인구 분석 단계가 전체 응답의 60~72%(12~22초)를 차지했고, 그 대부분이
# 매 요청 반복되는 인증·지역코드 조회였다. 아래 세 가지는 요청 간에 바뀌지 않는
# 값이라 캐시해 재사용한다(서버리스 인스턴스가 살아있는 동안 유지).
_TOKEN_CACHE = {'token': None, 'expires_at': 0.0}
_TOKEN_TTL_SEC = 3 * 3600          # 발급 후 4시간 유효 — 여유를 두고 3시간만 쓴다
_REGION_CD_CACHE = {}              # (부모코드, 지역명) -> 지역코드 (행정구역은 고정값)
_POP_YEAR_CACHE = {'year': None}   # 조회에 성공한 연도 — 실패 연도 재시도를 없앤다
_SGIS_CACHE_MAX = 512


def _get(path, params, timeout=4):
    url = f"{SGIS_BASE}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def get_access_token():
    """환경변수에 키가 없거나 인증 실패 시 None.

    토큰은 4시간 유효한데 매 요청 재발급하고 있었다. 유효기간 내에는 재사용한다.
    """
    consumer_key = os.environ.get(SGIS_SERVICE_ID_ENV)
    consumer_secret = os.environ.get(SGIS_SECURITY_KEY_ENV)
    if not consumer_key or not consumer_secret:
        return None
    if _TOKEN_CACHE['token'] and time.time() < _TOKEN_CACHE['expires_at']:
        return _TOKEN_CACHE['token']
    try:
        data = _get('auth/authentication.json', {
            'consumer_key': consumer_key,
            'consumer_secret': consumer_secret,
        })
        token = data.get('result', {}).get('accessToken')
        if token:
            _TOKEN_CACHE['token'] = token
            _TOKEN_CACHE['expires_at'] = time.time() + _TOKEN_TTL_SEC
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


def _remember_region(key, cd):
    """지역코드 캐시에 저장하고 그대로 반환. 무한 증가만 막는다."""
    if cd:
        if len(_REGION_CD_CACHE) >= _SGIS_CACHE_MAX:
            _REGION_CD_CACHE.clear()
        _REGION_CD_CACHE[key] = cd
    return cd


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
    """addr/stage.json 한 단계를 조회해 target_name과 일치하는 지역의 cd를 찾는다.

    행정구역 코드는 바뀌지 않으므로 조회 결과를 캐시한다. 이 조회가 주소 1건당
    3회 순차로 일어나 인구 분석 지연의 큰 몫을 차지했다.
    """
    _ck = (parent_cd, target_name)
    if _ck in _REGION_CD_CACHE:
        return _REGION_CD_CACHE[_ck]
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
                return _remember_region(_ck, row.get('cd'))
        for row in rows:
            name = str(row.get('addr_name', '')).replace(' ', '')
            if len(clean_target) >= 2 and clean_target in name:
                return _remember_region(_ck, row.get('cd'))
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
    if year:
        years_to_try = [str(year)]
    elif _POP_YEAR_CACHE['year']:
        # 이미 성공한 연도를 알고 있으면 실패하는 연도를 다시 시도하지 않는다.
        # (자료가 없는 연도를 매 호출 1~2회씩 헛되이 조회하고 있었다.)
        years_to_try = [_POP_YEAR_CACHE['year']]
    else:
        years_to_try = [str(datetime.datetime.now().year - i) for i in (1, 2, 3)]
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
            # avg_age(평균연령)를 총인구 폴백으로 쓰면 '구 전체 인구 43명' 같은
            # 값이 만들어져 인구·채점·매출이 통째로 무너진다. 인구 필드만 본다.
            total = row.get('tot_ppltn') or row.get('population')
            if total is None:
                continue
            _POP_YEAR_CACHE['year'] = yr
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
