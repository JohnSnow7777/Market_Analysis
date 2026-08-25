# -*- coding: utf-8 -*-
"""마이파크 전역 설정 및 파라미터 모듈"""

DEFAULT_SETTINGS = {
    # 기본 단가 및 이용료
    'game_price_18hole': 8000,          # 파크골프 18홀 이용료 8,000원
    'screengolf_price_18hole': 15000,   # 일반 스크린골프 18홀 이용료 15,000원
    
    # 영업 기준
    'hours_per_game': 1.0,              # 18홀 1게임 1시간
    'daily_business_hours': 10.0,       # 1일 10시간 영업
    'default_rooms': 12,                # 기본 12타석
    
    # 부가 매출 비율
    'ratio_goods': 0.10,                # 용품 매출 10%
    'ratio_cafe': 0.05,                 # 카페 매출 5%
    'ratio_lesson': 0.03,               # 레슨 매출 3%
    'total_revenue_multiplier': 1.18,   # 총매출 1.18배
    
    # 변동 원가율
    'cost_rate_goods': 0.60,            # 용품 원가율 60%
    'cost_rate_cafe': 0.50,             # 식음 원가율 50%
    'cost_rate_lesson': 0.80,           # 레슨 원가율 80%
    'card_fee_rate': 0.02,              # 카드수수료 2.0%
    
    # 5개년 연간 매출 성장률
    'annual_growth_rate': 0.02,         # 연 2.0% 복리 성장
    
    # 고정 및 운영비용 (12타석 기준 표준)
    'labor_cost_per_person': 2500000,   # 인건비 1인당 250만원
    'default_staff_count': 4,           # 4명 운영
    'default_monthly_rent': 5000000,    # 임대료 월 500만원
    
    # 타석 연동 비용
    'sensor_consumables_monthly': 20000,    # 타석당 소모품비 2만원 (12타석 24만)
    'sensor_utilities_monthly': 50000,      # 타석당 수도광열비 5만원 (12타석 60만)
    
    # 매장 고정 관리비
    'monthly_telecom': 100000,          # 통신비 10만원
    'monthly_welfare': 1000000,         # 복리후생비 100만원
    'monthly_maintenance': 500000,      # 유지보수비 50만원
    'monthly_air_cleaner_per_5rooms': 400000, # 공기청정기 렌탈 (5타석당 40만원)
    'monthly_water_purifier': 100000,   # 정수기 10만원
    'monthly_insurance': 200000,        # 영업배상보험료 20만원
    'monthly_marketing': 500000,        # 광고선전비 50만원
}

SCENARIO_CONFIG = {
    'conservative': {
        'name': '보수적',
        'name_en': 'Conservative',
        'avg_daily_users_per_room': 12.5,   # 타석당 1일 12.5명 (12타석=150명/일, 월 4,500명)
        'daily_operating_hours': 5.0,       # 1일 5시간 가동 (타석당 2.5명/시간)
        'description': '상권 초기 진입 및 평일 주간 위주 가동',
    },
    'moderate': {
        'name': '보편적',
        'name_en': 'Moderate',
        'avg_daily_users_per_room': 15.0,   # 타석당 1일 15.0명 (12타석=180명/일, 월 5,400명)
        'daily_operating_hours': 5.0,       # 1일 5시간 가동 (타석당 3.0명/시간)
        'description': '지역 내 안정적 회원 확보 및 정기 모임 정착',
    },
    'optimistic': {
        'name': '긍정적',
        'name_en': 'Optimistic',
        'avg_daily_users_per_room': 20.0,   # 타석당 1일 20.0명 (12타석=240명/일, 월 7,200명)
        'daily_operating_hours': 5.0,       # 1일 5시간 가동 (타석당 4.0명/시간)
        'description': '지역 랜드마크 매장 선점 및 동호회/대회 유치 활성화',
    }
}

SCORING_WEIGHTS = {
    'senior_population': {
        'name': '골든 시니어 집적도',
        'weight': 25,
        'desc': '반경 3km 내 50~70대 시니어 인구수 및 구성비율'
    },
    'accessibility_parking': {
        'name': '접근성 및 주차 인프라',
        'weight': 25,
        'desc': '자주식 주차 편의성, 승강기 완비, 주요 간선도로 접면'
    },
    'space_efficiency': {
        'name': '공간 적합성 및 임대료',
        'weight': 15,
        'desc': '유효 층고(2.8m 이상), 기둥 간격, 평당 임대료 경쟁력'
    },
    'supply_gap': {
        'name': '수요 공급 갭 (블루오션)',
        'weight': 15,
        'desc': '반경 3km 내 스크린 파크골프 경쟁 강도 및 야외구장 대기수요'
    },
    'commercial_spending': {
        'name': '지역 소비력 및 여가지출',
        'weight': 20,
        'desc': '소상공인 스포츠/여가 카드 매출액 및 생활밀착 상권 활성도'
    }
}

BRAND_COLORS = {
    'navy_primary': '#003366',       # 스마일스퀘어/마이파크 네이비
    'blue_accent': '#1E88E5',        # 액센트 블루
    'gold_accent': '#FFB300',        # 골든 앰버
    'green_accent': '#43A047',       # 파크골프 그린
    'red_accent': '#E53935',         # 강조 레드
    'gray_dark': '#333333',          # 본문 진회색
    'gray_light': '#F5F7FA',         # 배경 연회색
    'white': '#FFFFFF'
}
