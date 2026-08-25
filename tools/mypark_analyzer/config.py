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
    'interior_cost_per_pyeong': 1200000,# 평당 120만원
    'hvac_cost': 12000000,              # 냉난방기 4대 1,200만원
    'signage_cost': 5000000,            # 간판/싸인물 500만원
    'furniture_cost': 3000000,          # 가구/집기 300만원
    'supplies_cost': 5000000,           # 초도용품 500만원
    
    # 운영 비용
    'labor_cost_manager': 2500000,      # 실장(점주) 1인 250만원
    'pos_telecom_monthly': 300000,      # 통신/POS 30만원
    'store_ops_monthly': 1500000,       # 매장운영비 (수도광열비/소모품) 150만원
    'marketing_monthly': 500000,        # 마케팅비 50만원
}

SCENARIO_CONFIG = {
    'conservative': {
        'name': '보수적 시나리오 (3회전)',
        'turns': 3.0,
        'daily_users': 100,             # 1일 100명 (월 3,000명)
        'goods_daily': 25000,           # 일 용품 2.5만 (월 75만)
        'description': '상권 초기 진입 및 평일 주간 위주 가동',
    },
    'moderate': {
        'name': '보편적 시나리오 (4회전)',
        'turns': 4.0,
        'daily_users': 133,             # 1일 133명 (월 4,000명)
        'goods_daily': 40000,           # 일 용품 4.0만 (월 120만)
        'description': '평일 주간 정기 모임 정착 및 안정적 단골 확보',
    },
    'optimistic': {
        'name': '긍정적 시나리오 (5회전)',
        'turns': 5.0,
        'daily_users': 167,             # 1일 167명 (월 5,000명)
        'goods_daily': 50000,           # 일 용품 5.0만 (월 150만)
        'description': '지역 랜드마크 매장 선점 및 주말/야간 활성화',
    }
}
