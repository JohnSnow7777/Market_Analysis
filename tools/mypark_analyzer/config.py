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


TIER_PRIME = 1        # 최상위 소비 상권
TIER_METRO = 2        # 서울/광역시/수도권 주요시
TIER_MID_CITY = 3     # 지방 중소도시 (시 단위)
TIER_RURAL = 4        # 군 단위 / 외곽

_PRIME_KEYWORDS = ['강남', '서초', '송파', '분당', '판교', '송도', '해운대', '수성구', '용산', '과천']
_METRO_SIDO = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종']
_METRO_GYEONGGI = [
    '고양', '덕양', '일산', '용인', '수지', '기흥', '수원', '영통', '광교', '성남', '중원', '수정',
    '안양', '평촌', '동안', '만안', '부천', '광명', '하남', '동탄', '화성', '시흥', '김포', '남양주',
    '의정부', '구리', '안산', '군포', '의왕', '오산', '파주', '평택',
]


def classify_region_tier(address, sigungu=''):
    """주소를 4단계 지역 등급으로 분류한다 (1=최상위 ~ 4=군 단위)."""
    text = f"{address} {sigungu}"

    if any(k in text for k in _PRIME_KEYWORDS):
        return TIER_PRIME
    if any(k in text for k in _METRO_SIDO):
        return TIER_METRO
    if any(k in text for k in _METRO_GYEONGGI):
        return TIER_METRO

    # 시/군 접미사로 판정 (키워드 목록에 없는 전국 모든 지역 대응)
    for token in text.split():
        if token.endswith('군'):
            return TIER_RURAL
    for token in text.split():
        if token.endswith('시'):
            return TIER_MID_CITY

    return TIER_MID_CITY
