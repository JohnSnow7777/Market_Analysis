# -*- coding: utf-8 -*-
"""5대 핵심 입지 지표(100점 만점) 채점 및 사업성 보고서 생성 엔진"""

def format_payback_text(months, capex_amount=386000000):
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
        senior_ratio = demographics.get('senior_ratio', 38.5)
        senior_pop = demographics.get('senior_50_plus', 72000)
        
        # 1. 골든 시니어 집적도 (25점)
        if senior_ratio >= 40.0 and senior_pop >= 80000:
            score_senior = 25.0
        elif senior_ratio >= 35.0 or senior_pop >= 60000:
            score_senior = 22.0
        elif senior_ratio >= 28.0:
            score_senior = 18.0
        else:
            score_senior = 14.0
            
        # 2. 접근성 및 주차 인프라 (25점)
        parking = site_info.get('parking_spaces', 10)
        score_parking = 25.0 if parking >= 10 else 20.0
        
        # 3. 공간 적합성 및 층고 (15점)
        clear_height = site_info.get('clear_height', 3.0)
        score_space = 15.0 if clear_height >= 2.8 else 10.0
        
        # 4. 수요공급 갭 (15점)
        comp_count = len(commercial_data.get('competitors', []))
        if comp_count <= 4:
            score_gap = 15.0
        elif comp_count <= 8:
            score_gap = 12.0
        else:
            score_gap = 9.0
            
        # 5. 지역 소비력 및 매출 (20점)
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
            
        senior_f_pop = demographics.get('senior_50_female', 38900)
        moderate_op = financials['monthly_scenarios']['moderate']['operating_profit']
        moderate_rev = financials['monthly_scenarios']['moderate']['total_revenue']
        total_capex = financials['investment']['total_capex']
        payback_months = financials['investment']['payback_months_moderate']
        payback_str = format_payback_text(payback_months, total_capex)
        
        # 앵커 테넌트 / 피칭 등 금지 단어 완전 제거된 객관적 기대효과
        value_franchisee = (
            f"반경 3km 생활권 내 50대 이상 시니어 인구 {senior_pop:,}명(여성 {senior_f_pop:,}명)이 밀집한 배후 상권입니다. "
            f"일반 스크린골프의 유휴 시간대인 '평일 낮 10시~오후 5시'에 주간 시니어 동호회 모임으로 안정적인 가동률을 확보합니다. "
            f"보편 운영 기준 월 예상 총매출 {moderate_rev/10000000:.1f}천만원, 월 영업이익 {moderate_op/10000000:.1f}천만원을 달성하며, "
            f"{payback_str} 가능한 사업 구조입니다."
        )
        
        value_landlord = (
            f"본 매장 입점 시 구매력 있는 지역 액티브 시니어 고객이 정기적으로 방문하여, "
            f"상가 내 식당, 카페 등 인접 점포의 고객 유입을 함께 촉진하는 '상가 활성화 대표 점포' 역할을 수행합니다. "
            f"5년 이상의 장기 안정적 임대차 계약을 통해 공실을 해소하고 건물의 자산 가치 상승을 기대할 수 있습니다."
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
