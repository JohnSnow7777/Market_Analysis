# -*- coding: utf-8 -*-
"""5대 핵심 입지 지표(100점 만점) 채점 및 사업성 보고서 생성 엔진 (객관적 사실 기반)"""

def format_payback_text(months, capex_amount=319000000):
    m = float(months)
    capex_str = f"약 {capex_amount / 100000000:.2f}억원 ({capex_amount // 10000:,}만원)"
    if m < 12:
        return f"초기 순투자금 {capex_str} 기준 약 {m:.1f}개월 만에 전액 회수"
    years = int(m // 12)
    rem = round(m % 12)
    if rem == 0:
        return f"초기 순투자금 {capex_str} 기준 약 {years}년 ({m:.1f}개월) 만에 전액 회수"
    return f"초기 순투자금 {capex_str} 기준 약 {years}년 {rem}개월 ({m:.1f}개월) 만에 전액 회수"


class ScoringEngine:
    """입지 최적성 5대 다이아몬드 스코어링 및 기대효과 리포트 생성기"""
    
    @staticmethod
    def evaluate_site(demographics, commercial_data, site_info, financials):
        senior_ratio = demographics.get('senior_ratio', 38.4)
        senior_pop = demographics.get('senior_50_plus', 72400)
        monthly_sales = commercial_data.get('monthly_avg_sales', 20500000)
        
        # 1. 골든 시니어 집적도 (25점 만점)
        if senior_pop >= 70000:
            score_senior = 25.0
        elif senior_pop >= 50000:
            score_senior = 22.0
        elif senior_pop >= 30000:
            score_senior = 17.0
        elif senior_pop >= 15000:
            score_senior = 12.0
        else:
            score_senior = 8.0
            
        # 2. 접근성 및 주차 인프라 (25점 만점)
        score_parking = 20.0
        
        # 3. 공간 적합성 및 층고 (15점 만점)
        score_space = 13.0
        
        # 4. 수요공급 갭 (15점 만점)
        competitors = commercial_data.get('competitors', [])
        comp_count = len(competitors)
        if comp_count <= 1:
            score_gap = 15.0
        elif comp_count <= 3:
            score_gap = 13.0
        else:
            score_gap = 10.0
            
        # 5. 지역 소비력 및 매출 (20점 만점)
        if monthly_sales >= 22000000:
            score_spending = 19.0
        elif monthly_sales >= 18000000:
            score_spending = 16.0
        elif monthly_sales >= 13000000:
            score_spending = 12.0
        else:
            score_spending = 8.0
            
        total_score = round(score_senior + score_parking + score_space + score_gap + score_spending, 1)
        
        if total_score >= 87.0:
            grade = 'S'
            grade_desc = '출점 최우선 추천 (Golden Prime Spot)'
        elif total_score >= 79.0:
            grade = 'A'
            grade_desc = '출점 우수 추천 (Prime Spot)'
        elif total_score >= 68.0:
            grade = 'B'
            grade_desc = '출점 양호 (Standard Spot)'
        else:
            grade = 'C'
            grade_desc = '출점 신중 검토 (Sub-Prime Spot)'
            
        inv = financials['investment']
        sc = financials['monthly_scenarios']['moderate']
        
        value_franchisee = (
            f"1. 평일 주간 높은 가동률 확보: 반경 3km 내 50대 이상 시니어 {senior_pop:,}명({senior_ratio}%) 및 "
            f"주부 동호회를 타겟팅하여 평일 낮 10~17시 정기 모임 중심의 안정적 가동률을 확보합니다.\n"
            f"2. 10타석 대규모 플래그십 시설 경쟁력: 기존 소규모 매장 대비 10타석 쾌적한 시설과 단체 모임 수용력으로 고객 선호도를 극대화합니다.\n"
            f"3. 안정적 수익성 및 빠른 원금 회수: 보편적 가동 기준 월 순영업이익 약 {sc['operating_profit']//10000:,}만원(영업이익률 {sc['profit_margin']}%)을 달성하여 "
            f"약 {inv['payback_months_moderate']:.1f}개월 만에 초기 순투자금 3.19억원을 전액 회수할 수 있습니다."
        )
        
        value_landlord = (
            f"1. 주간 시니어 소비층 지속 유입: 구매력과 여유가 있는 지역 50~70대 고객이 매일 건물을 방문하여 "
            f"상가 내 식당, 병원, 약국, 카페 등 타 점포 매출을 동반 견인합니다.\n"
            f"2. 공실 해소 및 장기 우량 임대차: 마이파크 매장 입점을 통해 공실을 해소하고 매월 안정적인 임대 수익을 확보합니다.\n"
            f"3. 건물 전체의 자산 가치(Cap Rate) 상승: 대형 체육 집객 시설 입점으로 건물 인지도 및 상가 매매 가치 상승에 기여합니다."
        )
        
        return {
            'scores': {
                'senior_population': score_senior,
                'accessibility_parking': score_parking,
                'space_efficiency': score_space,
                'supply_gap': score_gap,
                'commercial_spending': score_spending
            },
            'total_score': total_score,
            'grade': grade,
            'grade_desc': grade_desc,
            'payback_text': format_payback_text(inv['payback_months_moderate'], inv['total_capex']),
            'value_franchisee': value_franchisee,
            'value_landlord': value_landlord
        }
