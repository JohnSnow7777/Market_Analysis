# -*- coding: utf-8 -*-
"""한국부동산원 부동산통계정보시스템(R-ONE) Open API 클라이언트.

엔드포인트/파라미터는 실제 서버에 실키로 호출해 확인함(2026-08-31):
  통계표 목록: https://www.reb.or.kr/r-one/openapi/SttsApiTbl.do
      ?KEY=&Type=json&pIndex=&pSize=
  통계 데이터: https://www.reb.or.kr/r-one/openapi/SttsApiTblData.do
      ?KEY=&STATBL_ID=&DTACYCLE_CD=QY&START_WRTTIME=&END_WRTTIME=&Type=json
      -> {"SttsApiTblData":[{"head":...},{"row":[{"CLS_ID","CLS_NM","CLS_FULLNM",
          "ITM_NM":"임대료","DTA_VAL"(단위: 천원/㎡),"WRTTIME_DESC", ...}]}]}

STATBL_ID='T248223134698125' = "임대동향 지역별 임대료(2024년3분기~)_소규모 상가"
(소상공인 매장 규모에 가장 가까운 구간). 분기별 갱신, 통계 공표 주기상
가장 최근 1~2분기는 아직 데이터가 없을 수 있어 최대 4개 분기 역순 시도한다
(SGIS 인구통계와 동일한 '작년/직전 분기 폴백' 패턴).

CLS_FULLNM은 "전국", "서울", "서울>강남", "경기>고양시청" 처럼 상권명/시군구명
계층 텍스트라 정식 행정구역 코드가 아니다. 시군구명이 포함된 행을 우선
매칭하고, 없으면 시/도 광역 단위, 그래도 없으면 전국으로 넓혀간다.
"""
import os
import json
import datetime
import urllib.request
import urllib.parse

REB_API_KEY_ENV = "REB_API_KEY"
REB_BASE = "https://www.reb.or.kr/r-one/openapi/SttsApiTblData.do"
STATBL_ID_SMALL_STORE = "T248223134698125"
PYEONG_PER_SQM = 3.305785

# R-ONE CLS_FULLNM은 시/도 약칭("경기","전북")을 쓰는데, 우리 주소는 정식
# 행정구역명("경기도","전라북도")이라 단순 substring 매칭이 안 된다.
SIDO_ABBR = {
    '서울특별시': '서울', '부산광역시': '부산', '대구광역시': '대구', '인천광역시': '인천',
    '광주광역시': '광주', '대전광역시': '대전', '울산광역시': '울산', '세종특별자치시': '세종',
    '경기도': '경기',
    '강원도': '강원', '강원특별자치도': '강원',
    '충청북도': '충북', '충청남도': '충남',
    '전라북도': '전북', '전북특별자치도': '전북', '전라남도': '전남',
    '경상북도': '경북', '경상남도': '경남',
    '제주특별자치도': '제주',
}


def _sido_abbr(sido):
    if sido in SIDO_ABBR:
        return SIDO_ABBR[sido]
    for full, abbr in SIDO_ABBR.items():
        if sido and sido.startswith(abbr):
            return abbr
    return sido


def _get(params, timeout=8):
    url = REB_BASE + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode('utf-8')
    data = json.loads(raw)
    body = data.get('SttsApiTblData', [])
    if len(body) < 2:
        return []
    head = body[0].get('head', [{}])
    for h in head:
        if 'RESULT' in h and h['RESULT'].get('CODE') not in (None, 'INFO-000'):
            print(f"[REB API ERROR] {h['RESULT'].get('CODE')}: {h['RESULT'].get('MESSAGE')}")
            return []
    return body[1].get('row', [])


def _recent_quarters(max_back=4):
    """올해 기준 최근 분기부터 역순으로 'YYYYQQ'(예: 202602) 문자열을 생성."""
    today = datetime.date.today()
    q = (today.month - 1) // 3 + 1
    y, qq = today.year, q
    out = []
    for _ in range(max_back):
        out.append(f"{y}{qq:02d}")
        qq -= 1
        if qq == 0:
            qq = 4
            y -= 1
    return out


def get_small_store_rent(sido, sigungu, dong=None):
    """행정구역명으로 소규모 상가 평당 임대료(원/평/월) 조회. 실패 시 None.

    반환: {'rent_per_pyeong': int, 'rent_per_sqm_1000won': float,
           'region_label': str, 'quarter_label': str} 또는 None.
    """
    api_key = os.environ.get(REB_API_KEY_ENV)
    if not api_key:
        return None
    try:
        for wt in _recent_quarters():
            rows = _get({
                'KEY': api_key,
                'STATBL_ID': STATBL_ID_SMALL_STORE,
                'DTACYCLE_CD': 'QY',
                'START_WRTTIME': wt,
                'END_WRTTIME': wt,
                'Type': 'json',
                'pIndex': 1,
                'pSize': 1000,
            })
            if not rows:
                continue

            def _match(rows, key):
                if not key:
                    return None
                for r in rows:
                    if key in (r.get('CLS_FULLNM') or ''):
                        return r
                return None

            sigungu_core = sigungu.split()[0] if sigungu else ''
            for suf in ('특별자치시', '광역시', '특별시', '시', '군', '구'):
                if sigungu_core.endswith(suf) and len(sigungu_core) > len(suf):
                    sigungu_core = sigungu_core[:-len(suf)]
                    break
            dong_core = dong or ''
            for suf in ('행정동', '동', '읍', '면'):
                if dong_core.endswith(suf) and len(dong_core) > len(suf):
                    dong_core = dong_core[:-len(suf)]
                    break

            abbr = _sido_abbr(sido)
            row = (_match(rows, sigungu) or _match(rows, sigungu_core) or
                   _match(rows, dong_core) or _match(rows, dong))
            if row is None:
                row = next((r for r in rows if r.get('CLS_FULLNM') == abbr), None)
            if row is None:
                row = next((r for r in rows if r.get('CLS_ID') == 500001), None)  # 전국
            if row is None:
                continue

            val_1000won_sqm = float(row['DTA_VAL'])
            rent_per_pyeong = int(round(val_1000won_sqm * 1000 * PYEONG_PER_SQM, -3))
            return {
                'rent_per_pyeong': rent_per_pyeong,
                'rent_per_sqm_1000won': round(val_1000won_sqm, 2),
                'region_label': row.get('CLS_FULLNM', ''),
                'quarter_label': row.get('WRTTIME_DESC', wt),
            }
        return None
    except Exception as e:
        print(f"[REB API FAIL] {e}")
        return None
