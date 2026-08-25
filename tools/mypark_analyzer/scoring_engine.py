# -*- coding: utf-8 -*-
"""5대 핵심 입지 지표(100점 만점) 채점 및 고객 친화적 쉬운 제안서 생성 엔진"""
from .config import SCORING_WEIGHTS

def format_payback_text(months):
    m = float(months)
    if m < 12:
        return f"약 {m:.1f}개월 (1년 이내 전액 회수)"
    years = int(m // 12)
    rem = round(m % 12)
    if rem == 0:
        return f"약 {years}년 ({m:.1f}개월)"
    return f"약 {years}년 {rem}개월 ({m:.1f}개월)"

class ScoringEngine:
    """입지 최적성 5대 다이아몬드 스코어링 및 기대효과 리포트 생성기"""
    
    @staticmethod
    def evaluate_site(demographics, commercial_data, site_info, financials):
        senior_ratio = demographics.get('senior_ratio', 40.0)
        senior_pop = demographics.get('senior_50_plus', 100000)
        if senior_ratio >= 40.0 and senior_pop >= 90000:
            score_senior = 25.0
        elif senior_ratio >= 35.0 or senior_pop >= 60000:
            score_senior = 22.0
        elif senior_ratio >= 28.0:
            score_senior = 18.0
        else:
            score_senior = 14.0
            
        parking = site_info.get('parking_spaces', 10)
        score_parking = 25.0 if parking >= 10 else 20.0
        
        clear_height = site_info.get('clear_height', 3.0)
        score_space = 15.0 if clear_height >= 2.8 else 10.0
        
        comp_count = len(commercial_data.get('competitors', []))
        if comp_count <= 4:
            score_gap = 15.0
        elif comp_count <= 8:
            score_gap = 12.0
        else:
            score_gap = 9.0
            
        monthly_sales = commercial_data.get('monthly_avg_sales', 18000000)
        if monthly_sales >= 20000000:
            score_spending = 20.0
        elif monthly_sales >= 15000000:
            score_spending = 18.0
        else:
            score_spending = 15.0
            
        total_score = round(score_senior + score_parking + score_space + score_gap + score_spending, 1)
        
        if total_score >= 90:
            grade = 'S'
            grade_desc = '출점 최우선 추천 (Golden Prime Spot)'
        elif total_score >= 80:
            grade = 'A'
            grade_desc = '출점 우수 추천 (Prime Spot)'
        elif total_score >= 70:
            grade = 'B'
            grade_desc = '조건부 출점 추천 (Conditional Spot)'
        else:
            grade = 'C'
            grade_desc = '출점 재검토 (Review Needed)'
            
        senior_f_pop = demographics.get('senior_50_female', 50000)
        moderate_op = financials['monthly_scenarios']['moderate']['operating_profit']
        moderate_rev = financials['monthly_scenarios']['moderate']['total_revenue']
        payback_months = financials['investment']['payback_months_moderate']
        payback_str = format_payback_text(payback_months)
        
        # 누구나 쉽게 이해하는 고객 맞춤형 사업성 제안 문구
        value_franchisee = (
            f"반경 3km 내 50대 이상 골든 시니어 인구 {senior_pop:,}명(여성 {senior_f_pop:,}명)이 밀집한 특급 배후 상권입니다. "
            f"일반 스크린골프 손님이 없는 '평일 낮 10시~오후 5시' 시간대에 시니어 주간 동호회 모임으로 100% 예약 풀가동이 가능합니다. "
            f"보편 가동 기준 월 예상 총매출 {moderate_rev/10000000:.1f}천만원, 월 순영업이익 {moderate_op/10000000:.1f}천만원(영업이익률 약 45~50%)을 달성하며, "
            f"초기 투자금은 {payback_str} 만에 전액 회수 가능한 안정적인 고수익 생활체육 창업 모델입니다."
        )
        
        value_landlord = (
            f"본 매장 입점 시 구매력 높은 지역 액티브 시니어 고객 수백 명이 매일 건물을 찾아와, "
            f"1층 카페, 식당 등 상가 내 다른 상점들의 손님까지 함께 늘려주는 '상가 전체를 살리는 대표 핵심 매장' 역할을 톡톡히 해냅니다. "
            f"마이파크 본사와의 연계를 통해 5년 이상의 장기 우량 임대차 계약으로 공실 걱정 없이 안정적인 월세 수익과 건물 가치 상승을 동시에 누리실 수 있습니다."
        )
        
        return {
            'scores': {
                'senior_population': score_senior,
                'accessibility_parking': score_parking,
                'space_efficiency': score_space,
                'supply_gap': score_gap,
                'commercial_spending': score_spending,
            },
            'total_score': total_score,
            'grade': grade,
            'grade_desc': grade_desc,
            'payback_text': payback_str,
            'value_franchisee': value_franchisee,
            'value_landlord': value_landlord,
            'pitch_franchisee': value_franchisee,
            'pitch_landlord': value_landlord
        }
