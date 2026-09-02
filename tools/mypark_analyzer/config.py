# -*- coding: utf-8 -*-
"""마이파크 전역 설정 및 파라미터 모듈 (10타석 120평 플래그십 표준 SSOT)"""

DEFAULT_SETTINGS = {
    # 기본 단가 및 이용료
    'game_price_18hole': 7000,          # 파크골프 18홀 이용료 7,000원
    'screengolf_price_18hole': 15000,   # 일반 스크린골프 18홀 이용료 15,000원
    
    # 영업 및 공간 기준 (플래그십 표준: 10타석 120평)
    'hours_per_game': 1.0,              # 18홀 1게임 1시간
    'daily_business_hours': 10.0,       # 1일 10시간 영업
    'default_rooms': 10,                # 기본 10타석 (플래그십 표준)
    'default_area_pyeong': 120,         # 기본 120평
    
    # 3대 매출 항목 단가 및 비중 (엑셀 원본 일치)
    'team_beverage_price': 3000,        # 팀당 음료 판매 3,000원
    'cost_rate_goods': 0.50,            # 용품 원가율 50%
    'cost_rate_beverage': 0.50,         # 식음료 원가율 50%
    'card_fee_rate': 0.02,              # 카드수수료 2.0%
    
    # 5개년 연간 매출 성장률
    'annual_growth_rate': 0.02,         # 연 2.0% 복리 성장
    
    # 초기 투자비 (SSOT: 3.19억원)
    'simulator_unit_price': 15000000,   # 대당 1,500만원
    'interior_cost_per_pyeong': 1000000,# 평당 100만원
    'hvac_cost': 12000000,              # 냉난방기 4대 1,200만원
    'signage_cost': 5000000,            # 간판/싸인물 500만원
    'furniture_cost': 3000000,          # 가구/집기 300만원
    'supplies_cost': 3500000,           # 초도용품 350만원
    
    # 운영 비용
    'labor_cost_manager': 2500000,      # 실장(점주) 1인 250만원
    'pos_telecom_monthly': 300000,      # 통신/POS 30만원
    'store_ops_monthly': 1500000,       # 매장운영비 (수도광열비/소모품) 150만원
    'marketing_monthly': 500000,        # 마케팅비 50만원
}

# -----------------------------------------------------------------------------
# 지역 등급 분류 (demographics / commercial_data 공용 SSOT)
#
# 과거에는 두 모듈이 각각 다른 키워드 목록을 들고 있어서 같은 주소가 모듈마다
# 다른 등급으로 분류되는 문제가 있었다. (예: 서울 노원구 -> 인구는 '대도시',
# 상권은 '군 단위'로 분류되어 월매출이 지방 군 수준으로 산정됨)
# 이제 아래 단일 함수만 사용한다.
# -----------------------------------------------------------------------------
def fmt_eok(won):
    """원 단위 금액을 'N.NN억원'으로 표기."""
    return f"{won / 100000000:.2f}억원"


def fmt_won_full(won):
    """원 단위 금액을 'N억 N,NNN만원'으로 표기 (1억 미만이면 'N,NNN만원')."""
    man = int(won) // 10000
    if man >= 10000:
        eok, rest = divmod(man, 10000)
        return f"{eok}억 {rest:,}만원" if rest else f"{eok}억원"
    return f"{man:,}만원"


def fmt_months(months):
    """개월 수를 'N년 N개월' 형태로 표기."""
    m = float(months)
    if m < 12:
        return f"{m:.1f}개월"
    years = int(m // 12)
    rem = int(round(m % 12))
    if rem == 0:
        return f"{years}년"
    if rem == 12:
        return f"{years + 1}년"
    return f"{years}년 {rem}개월"


# 인접 업종(골프 연습장) 참고 지표.
# 출처: 소상공인시장진흥공단 상권정보시스템 상권분석리포트(2026년 6월 기준).
# 용도: 마이파크(스크린 파크골프)와 고객층·이용시간대가 어떻게 다른지 보여주는
#       비교 기준. 매출 추정에는 쓰지 않는다(업종이 다르므로 대입하면 왜곡된다).
# 주의: 각 수치의 적용 범위가 다르므로 보고서에 범위를 반드시 함께 표기한다.
#       - national_*: 전국 집계라 어느 지역 보고서에나 인용 가능
#       - usage_*   : 광주 서구 사례라 '사례'임을 명시해야 함
DRIVING_RANGE_BENCHMARK = {
    'source': '소상공인시장진흥공단 상권정보시스템',
    'base_month': '2026년 6월',
    'national_monthly_sales_manwon': 1692,   # 전국 업소당 월평균 매출(만원)
    'national_store_count': 12354,           # 전국 골프 연습장 업소 수
    'usage_scope': '광주 서구 사례',
    'usage_male_ratio': 76.2,                # 남성 매출 비중(%)
    'usage_age_40_50_ratio': 65.3,           # 40~50대 매출 비중(%)
    'usage_evening_ratio': 33.7,             # 18~23시 매출 비중(%)
    'usage_afternoon_ratio': 37.7,           # 14~18시 매출 비중(%)
}

# 반경 3km 생활권이 포함하는 행정동 수(가정값).
#
# 근거: 반경 3km 원의 면적은 약 28.3km²이고, 국내 도시지역 행정동은 대체로
#       3~6km² 규모라 한 생활권에 5~7개 동이 들어간다. 그 중앙값을 쓴다.
# 한계: 지역별 실제 행정동 면적으로 계산하는 것이 정확하지만, 통계청 SGIS
#       인구통계 응답에는 면적·인구밀도 필드가 없어(2026-09-02 실제 응답 확인:
#       adm_cd/adm_nm/population 3개 필드뿐) 구역 면적을 얻을 수 없다.
#       그래서 지역과 무관한 단일 가정값을 쓰며, 보고서에는 이 값이 추정
#       전제임을 함께 표기한다. 면적 데이터를 확보하면
#       (3km 원 면적 ÷ 평균 행정동 면적)으로 대체할 수 있다.
LIFEZONE_DONG_COUNT = 6

TIER_PRIME = 1        # 최상위 소비 상권
TIER_METRO = 2        # 서울/광역시/수도권 주요시
TIER_MID_CITY = 3     # 지방 중소도시 (시 단위)
TIER_RURAL = 4        # 군 단위 / 외곽

# 최상위 소비 상권은 '이름'이 아니라 '어느 시/도의 어느 시군구'로 지정한다.
# '강남'이라는 두 글자로 판정하면 경상남도 진주시 강남동이 서울 강남구 등급을
# 받아 매출·임대료가 실제의 두 배 가까이 부풀려진다(실제 발생했던 오류).
_PRIME_REGIONS = {
    ('서울특별시', '강남구'), ('서울특별시', '서초구'), ('서울특별시', '송파구'),
    ('서울특별시', '용산구'),
    ('경기도', '성남시 분당구'), ('경기도', '과천시'),
    ('인천광역시', '연수구'),      # 송도
    ('부산광역시', '해운대구'),
    ('대구광역시', '수성구'),
}

# 광역시·특별시는 시/도 자체로 판정한다(문자열 포함 검사 금지).
_METRO_SIDO = {
    '서울특별시', '부산광역시', '대구광역시', '인천광역시',
    '광주광역시', '대전광역시', '울산광역시', '세종특별자치시',
}

# 경기도 내 주요 도시는 시군구의 '시' 이름으로 판정한다.
# 주소 전체를 훑지 않으므로 '중원대로'(충주) 같은 도로명에 걸리지 않는다.
_METRO_GYEONGGI_CITIES = {
    '고양시', '용인시', '수원시', '성남시', '안양시', '부천시', '광명시', '하남시',
    '화성시', '시흥시', '김포시', '남양주시', '의정부시', '구리시', '안산시',
    '군포시', '의왕시', '오산시', '파주시', '평택시',
}


def _sigungu_city_token(sigungu):
    """'고양시 덕양구' -> '고양시', '이천시' -> '이천시', '무안군' -> '무안군'."""
    if not sigungu:
        return ''
    return sigungu.split()[0]


def classify_region_tier(address, sigungu='', sido=''):
    """주소를 4단계 지역 등급으로 분류한다 (1=최상위 ~ 4=군 단위).

    판정은 주소 문자열 검색이 아니라 (시/도, 시군구)로 한다. 예전에는
    `'강남' in 주소` 방식이라 진주시 강남동이 최상위 등급을 받고, 충주
    중원대로가 '중원'에 걸려 광역시 등급을 받았다. 이 등급 하나가 매출·
    소비력·인구계수·임대료까지 20개 넘는 수치를 좌우하므로 오분류의
    파급이 크다.

    sido/sigungu가 비어 있으면(구주소 호출부 호환) 주소에서 시/도만 안전하게
    추정해 쓴다 — 이때도 부분 문자열로 동 이름을 뒤지지는 않는다.
    """
    sigungu = ' '.join((sigungu or '').split())
    sido = (sido or '').strip()

    if not sido and address:
        # 주소 맨 앞 토큰이 시/도인 경우만 인정한다(주소 중간의 지명은 보지 않음).
        first = address.split()[0] if address.split() else ''
        for full in _METRO_SIDO:
            if first and (first == full or full.startswith(first)) and len(first) >= 2:
                sido = full
                break
        if not sido and first.startswith(('경기', '강원', '충청', '충북', '충남',
                                          '전라', '전북', '전남', '경상', '경북',
                                          '경남', '제주')):
            sido = first

    city_token = _sigungu_city_token(sigungu)

    # 1) 군 단위를 가장 먼저 본다. 광역시 안에도 군이 있어(울산 울주군,
    #    부산 기장군, 인천 강화군·옹진군) 시/도부터 보면 군이 광역시 등급을
    #    받아버린다.
    if city_token.endswith('군'):
        return TIER_RURAL

    # 2) 최상위 상권은 (시/도, 시군구) 조합이 정확히 일치할 때만.
    for p_sido, p_sigungu in _PRIME_REGIONS:
        if sido == p_sido and sigungu and (sigungu == p_sigungu or sigungu.split()[-1] == p_sigungu.split()[-1]):
            return TIER_PRIME

    # 3) 광역시·특별시
    if sido in _METRO_SIDO:
        return TIER_METRO

    # 4) 경기도 주요시
    if sido == '경기도' and city_token in _METRO_GYEONGGI_CITIES:
        return TIER_METRO

    if city_token.endswith('시'):
        return TIER_MID_CITY
    return TIER_MID_CITY

    return TIER_MID_CITY
