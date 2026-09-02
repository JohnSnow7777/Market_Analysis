# -*- coding: utf-8 -*-
"""5대 핵심 입지 지표(100점 만점) 채점 및 사업성 보고서 생성 엔진 (객관적 사실 기반)"""

def format_payback_text(months, capex_amount=281500000):
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
        # 채점에는 '구 전체 인구'가 아니라 매장이 실제로 끌어올 수 있는 생활권 인구를
        # 쓴다 (demographics.catchment_senior_50). 구 전체 분석에서 구 인구를 그대로
        # 쓰면 주소를 모호하게 적을수록 점수가 오르는 왜곡이 생긴다.
        senior_pop = demographics.get('catchment_senior_50') or demographics.get('senior_50_plus', 72400)
        monthly_sales = commercial_data.get('monthly_avg_sales', 20500000)
        
        # 1. 시니어 인구 밀집도 (25점 만점)
        # [2026-08-31 수정] 기존에는 절대 인구수 구간(7만명 이상 만점)만으로 채점해,
        # 지표 이름이 '밀집도'인데도 정작 시니어 비중(senior_ratio)은 계산만 하고
        # 채점에 쓰지 않았다. 그 결과 시니어 비중이 40%가 넘는 조밀한 생활권이라도
        # 반경 3km 절대인구가 적으면 최하점(8점)이 나오는 구조적 결함이 있었다.
        #
        # 개선: '이 매장이 실제로 필요로 하는 고객 수 대비 배후 시니어 인구가
        # 얼마나 여유로운가'(요구 침투율)로 채점한다. 사업모델에서 역산하므로
        # 임의로 후하게 준 것이 아니라 근거가 명확하고, 타석 수가 작은 매장은
        # 필요 고객도 적다는 점까지 반영된다.
        _rooms_for_demand = max(1, site_info.get('rooms', 10))
        _monthly_visits_needed = _rooms_for_demand * 4.0 * 4 * 30  # 보편(4회전)×팀4인×30일
        _visits_per_customer = 4.0                                  # 단골 월 4회 방문 가정
        _customers_needed = _monthly_visits_needed / _visits_per_customer
        senior_penetration = (_customers_needed / senior_pop * 100.0) if senior_pop > 0 else 999.0

        if senior_penetration <= 2.0:
            score_senior = 25.0
        elif senior_penetration <= 4.0:
            score_senior = 22.5
        elif senior_penetration <= 7.0:
            score_senior = 21.0
        elif senior_penetration <= 12.0:
            score_senior = 19.5
        elif senior_penetration <= 20.0:
            score_senior = 15.0
        else:
            score_senior = 10.0

        # 시니어 비중(밀집도)이 높은 생활권은 동일 인구라도 타겟 접근이 유리하므로
        # 소폭 가산한다 (지표명 '밀집도'의 실제 반영, 만점 초과는 하지 않음).
        if senior_ratio >= 38.0:
            score_senior = min(25.0, score_senior + 1.5)
        elif senior_ratio >= 33.0:
            score_senior = min(25.0, score_senior + 0.8)
            
        # 2. 접근성 및 주차 인프라 (25점 만점)
        # 주의: 이 점수는 '건물 자체'의 주차장·엘리베이터·진입로가 아니라 상권 단위
        # 대중교통 통계(버스정류장 수/지하철 유무)만 반영한다. 건물 실측 주차 정보는
        # 공공데이터로 확인 불가하여 채점에 포함하지 않으며, 라벨/보고서에는 이 지표가
        # '상권 접근성'이지 '해당 건물 주차 여건'이 아님을 항상 함께 표기해야 한다.
        infra = commercial_data.get('infra', {})
        bus_count = infra.get('버스정류장', 30)
        subway_info = infra.get('지하철', '')
        # 카카오 카테고리 검색으로 실제 역을 확인했으면 그 결과(subway_detail)를 쓴다.
        # 문자열에 '지하철'이 들어있는지로 판정하던 방식은, 추정 문구까지 역세권으로
        # 인정해 접근성 점수를 최고 등급으로 올려버리는 문제가 있었다.
        _sub_detail = commercial_data.get('subway_detail')
        if _sub_detail is not None:
            has_subway = bool(_sub_detail.get('name'))
        else:
            has_subway = '지하철' in subway_info or '역세권' in subway_info or subway_info.endswith('역')
        # 건물 단위 주차 실측은 여전히 불가. 다만 주변시설 개수를 실제로 센 경우에는
        # 상권 접근성 근거가 추정이 아닌 실측이므로 그 사실을 보고서에 표기할 수 있게 한다.
        parking_is_verified = False
        infra_is_measured = bool(commercial_data.get('infra_is_measured'))

        if has_subway or bus_count >= 35:
            score_parking = 23.0
        elif bus_count >= 20:
            score_parking = 20.0
        elif bus_count >= 10:
            score_parking = 17.5
        else:
            score_parking = 15.0

        # 3. 공간 적합성 및 층고 (15점 만점 - 타석당 전용면적 여유도)
        # site_info['is_auto_estimated']가 True면 사용자가 실제 룸/평수를 입력하지
        # 않아 시스템 기본값(10타석 120평 플래그십 표준)으로 채점된 것이므로, 실제
        # 사업지 크기와 무관하게 최고 등급이 나올 수 있다. 이 경우 경쟁매장 여유도와
        # 같은 패턴으로 '미검증' 중립 점수를 부여해 허위로 높은 점수를 막는다.
        rooms_cnt = max(1, site_info.get('rooms', 10))
        area_cnt = site_info.get('area_pyeong', 120)
        pyeong_per_room = area_cnt / float(rooms_cnt)
        space_is_verified = not site_info.get('is_auto_estimated', False)

        if not space_is_verified:
            score_space = 11.0  # 15점 만점 중 중립값 (미검증 표기)
        elif pyeong_per_room >= 12.0:   # 타석당 12평 이상 (쾌적한 플래그십)
            score_space = 14.5
        elif pyeong_per_room >= 10.0: # 타석당 10~11.9평 (표준)
            score_space = 13.0
        elif pyeong_per_room >= 8.0:  # 타석당 8~9.9평 (다소 협소)
            score_space = 10.5
        else:                         # 8평 미만 (초협소)
            score_space = 8.0
        
        # 4. 경쟁 매장 여유도 (15점 만점)
        # 실측 DB 매칭 또는 실시간 API 검색으로 '확인된' 경쟁사 수만 채점에 사용한다.
        # 확인 자체가 불가능한 지역(실측 DB 미등록 + API 미설정)은 블루오션으로도,
        # 포화 상권으로도 단정할 수 없으므로 중립 점수를 부여하고 '미검증'으로 표기한다.
        comp_verified = commercial_data.get('competitor_is_verified', False)
        comp_count = commercial_data.get('competitor_verified_count')
        if not comp_verified or comp_count is None:
            score_gap = 12.0
            gap_is_verified = False
        else:
            gap_is_verified = True
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
            grade_desc = '출점 검토사안 (Sub-Prime Spot)'
            
        inv = financials['investment']
        sc = financials['monthly_scenarios']['moderate']
        
        value_franchisee = (
            f"1. 평일 주간 높은 가동률 확보: {'구 내 대표 생활권' if demographics.get('district_wide_analysis') else '반경 3km 내'} 50대 이상 시니어 {senior_pop:,}명({senior_ratio}%) 및 "
            f"주부 동호회를 타겟팅하여 평일 낮 10~17시 정기 모임 중심의 안정적 가동률을 확보합니다.\n"
            f"2. {rooms_cnt}타석 시설 경쟁력: 기존 소규모 매장 대비 {rooms_cnt}타석 쾌적한 시설과 단체 모임 수용력으로 고객 선호도를 극대화합니다.\n"
            f"3. 안정적 수익성 및 빠른 원금 회수: 보편적 가동 기준 월 순영업이익 약 {sc['operating_profit']//10000:,}만원(영업이익률 {sc['profit_margin']}%)을 달성하여 "
            f"약 {inv['payback_months_moderate']:.1f}개월 만에 초기 순투자금 {inv['total_capex']/100000000:.2f}억원을 전액 회수할 수 있습니다."
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
            'infra_is_measured': infra_is_measured,
            'gap_is_verified': gap_is_verified,
            'parking_is_verified': parking_is_verified,
            'space_is_verified': space_is_verified,
            'senior_penetration': round(senior_penetration, 1),
            'senior_customers_needed': int(_customers_needed),
            'payback_text': format_payback_text(inv['payback_months_moderate'], inv['total_capex']),
            'value_franchisee': value_franchisee,
            'value_landlord': value_landlord
        }
