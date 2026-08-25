# -*- coding: utf-8 -*-
"""5대 핵심 입지 지표(100점 만점) 채점 및 사업성 보고서 생성 엔진 (변별력 강화 모델)"""

def format_payback_text(months, capex_amount=336000000):
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
        
        # 4. 수요공급 갭 - 블루오션 (15점 만점)
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
            
        value_franchisee = (
            f"1. 주간 유휴시간 제로(100% 예약 풀가동 체계): 반경 3km 내 50대 이상 시니어 {senior_pop:,}명({senior_ratio}%) 및 "
            f"여성 주부 동호회를 타겟팅하여 평일 낮 10~17시 유휴 시간을 100% 예약제로 가동합니다.\n"
            f"2. 10타석 플래그십 상위 20% 시장 독점: 노후 1~2타석 매장 대비 10타석 플래그십 압도적 시설 경쟁력과 카페형 휴게 라운지로 객단가를 극대화합니다.\n"
            f"3. 빠른 원금 회수 및 고수익성: 오토 운영 시 월 순영업이익 약 {financials['monthly_scenarios']['moderate']['operating_profit']//10000:,}만원, "
            f"창업주 직접 운영 시 월 순영업이익 약 {financials['owner_operated']['monthly_operating_profit_moderate']//10000:,}만원(영업이익률 {financials['owner_operated']['profit_margin_moderate']}%)을 달성하여 "
            f"단 {financials['owner_operated']['payback_months']:.1f}개월 만에 순투자금 3.36억원을 전액 회수할 수 있습니다."
        )
        
        value_landlord = (
            f"1. 일 60~90명 액티브 시니어 지속 유입: 구매력과 소비 여력이 높은 지역 시니어 고객이 매일 건물을 방문하여 "
            f"상가 내 식당, 병원, 약국, 카페 등 타 점포 매출을 동반 견인합니다.\n"
            f"2. 공실 완전 해소 및 5년 장기 우량 임대차: 마이파크 가맹점과의 5년 장기 계약으로 공실 리스크를 완전 박멸하고 매월 안정적 임대료를 확보합니다.\n"
            f"3. 건물 전체의 자산 가치(Cap Rate) 상승 견인: 우량 핵심 점포(Anchor Tenant) 입점에 따른 유동인구 급증으로 "
            f"상가 매매 가치 및 부동산 감정평가액 상승을 주도합니다."
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
            'payback_text': format_payback_text(financials['investment']['payback_months_moderate'], financials['investment']['total_capex']),
            'value_franchisee': value_franchisee,
            'value_landlord': value_landlord
        }
