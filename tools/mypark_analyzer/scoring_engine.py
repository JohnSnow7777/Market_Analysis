# -*- coding: utf-8 -*-
"""5대 핵심 입지 지표(100점 만점) 채점 및 맞춤형 피칭 논리 생성 엔진"""
from .config import SCORING_WEIGHTS

class ScoringEngine:
    """입지 최적성 5대 다이아몬드 스코어링 및 피칭 생성기"""
    
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
        payback = financials['investment']['payback_months_moderate']
        
        pitch_franchisee = (
            f"반경 3km 내 50대 이상 시니어 인구 {senior_pop:,}명(여성 {senior_f_pop:,}명)이 밀집되어 있어, "
            f"일반 스크린골프가 비어 있는 '평일 주간 10~17시'에 100% 예약 풀가동이 가능합니다. "
            f"보편 가동 시 월 총매출 {moderate_rev/10000000:.1f}천만원, 월 영업이익 {moderate_op/10000000:.1f}천만원(영업이익률 50% 이상)을 달성하며, "
            f"초기 투자금은 약 {payback:.0f}개월 이내에 전액 회수되는 최고 수준의 안정적 캐시카우입니다."
        )
        
        pitch_landlord = (
            f"본 입점 시 지역 내 구매력 높은 액티브 시니어 수백 명이 매일 건물을 방문하여 1층 식당, 카페 등 "
            f"건물 전체 상권의 가치와 매출을 견인하는 강력한 앵커 테넌트(Anchor Tenant) 역할을 수행합니다. "
            f"마이파크 본사와의 연계를 통해 5년 이상의 장기 우량 임차 계약을 보장합니다."
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
            'pitch_franchisee': pitch_franchisee,
            'pitch_landlord': pitch_landlord
        }
