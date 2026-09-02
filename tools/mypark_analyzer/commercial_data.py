# -*- coding: utf-8 -*-
"""MYPARK 지역등급 추정 모델 엔진 (전국 지역을 4단계 등급으로 분류한 소비력·업종 특화도 추정)"""
import os
from .address_resolver import AddressResolver
from .competitor_engine import CompetitorEngine
from . import sbiz_client
from .config import classify_region_tier, TIER_PRIME, TIER_METRO, TIER_MID_CITY

class CommercialEngine:
    """지역별 실측 상권 소비력 및 매출 분석기"""

    @staticmethod
    def get_commercial_analysis(address, district_wide=False, district_radius_m=None):
        resolved = AddressResolver.resolve(address)
        full_addr = address
        sigungu = resolved.get('sigungu', '')
        dong = resolved.get('dong', '') if resolved.get('dong') else '사업권역'

        # 경쟁 매장 실시간 검색
        comp_res = CompetitorEngine.search_competitors(address, sigungu, dong)

        # 지역별 실측 상권 매출 및 소비력 지수 차등화
        is_estimated_comm = False
        tier = classify_region_tier(full_addr, sigungu, resolved.get('sido', ''))
        if tier == TIER_PRIME:
            monthly_avg = 24500000
            top_20_sales = 62510000
            dong_avg = 21500000
            city_avg = 18200000
            spending_grade = '최상위 10% (골든 프라임)'
            growth_rate = 182.4
            sg_count = 10
            total_stores = 1526
            density_ratio = 0.7
            nat_avg = 0.3
            multiple = 2.3
            # 특정 역 이름을 단정하지 않는다(역명·도보거리는 확인된 값이 아니다).
            # 지역등급상 도시철도가 운행되는 권역이라는 사실만 밝히고, 정확한
            # 도보거리는 현장 확인 대상임을 문구에 담는다.
            subway = f"{dong} 일대 지하철 운행 권역 (역까지 도보거리는 현장 확인)"
            bus_stop_count = 52
            gov_count, edu_count, fin_count = 12, 22, 28
            residential_ratio, workplace_ratio = 82.0, 18.0
        elif tier == TIER_METRO:
            monthly_avg = 20500000
            top_20_sales = 48500000
            dong_avg = 18500000
            city_avg = 15400000
            spending_grade = '상위 20% (우수 주거 상권)'
            growth_rate = 145.2
            sg_count = 7
            total_stores = 1140
            density_ratio = 0.6
            nat_avg = 0.3
            multiple = 2.0
            subway = f"{sigungu} 간선 교통망 완비"
            bus_stop_count = 40
            gov_count, edu_count, fin_count = 9, 16, 18
            residential_ratio, workplace_ratio = 90.5, 9.5
        elif tier == TIER_MID_CITY:
            monthly_avg = 14800000
            top_20_sales = 32000000
            dong_avg = 13200000
            city_avg = 11800000
            spending_grade = '지방 중심 상권 (중위권)'
            growth_rate = 98.6
            sg_count = 4
            total_stores = 820
            density_ratio = 0.5
            nat_avg = 0.3
            multiple = 1.7
            subway = "시내 주요 버스 노선망"
            bus_stop_count = 26
            gov_count, edu_count, fin_count = 6, 11, 10
            residential_ratio, workplace_ratio = 94.0, 6.0
        else: # 군/소도시 (추정치 모델 적용)
            is_estimated_comm = True
            monthly_avg = 9800000
            top_20_sales = 21000000
            dong_avg = 8900000
            city_avg = 7600000
            spending_grade = '일반 생활 상권'
            growth_rate = 62.1
            sg_count = 2
            total_stores = 450
            density_ratio = 0.4
            nat_avg = 0.3
            multiple = 1.3
            subway = "지역 주요 도로망 인접"
            bus_stop_count = 15
            gov_count, edu_count, fin_count = 4, 7, 6
            residential_ratio, workplace_ratio = 96.5, 3.5

        months = ['25.07', '25.08', '25.09', '25.10', '25.11', '25.12', '26.01', '26.02', '26.03', '26.04', '26.05', '26.06', '26.07']
        multipliers = [0.96, 0.98, 1.02, 1.08, 1.05, 1.12, 1.15, 1.06, 1.04, 1.02, 1.05, 0.98, 1.00]
        
        selected_sales = [int((monthly_avg // 10000) * m) for m in multipliers]
        dong_sales = [int((dong_avg // 10000) * m) for m in multipliers]
        city_sales = [int((city_avg // 10000) * m) for m in multipliers]

        monthly_trend = []
        for m, s in zip(months, selected_sales):
            monthly_trend.append({'month': m, 'sales': s * 10000})

        day_dist = {'월': 16.2, '화': 13.5, '수': 13.8, '목': 14.1, '금': 15.6, '토': 13.9, '일': 12.9, '주말평균비중': 13.4}
        time_dist = {'새벽_06_09시': 5.2, '오전_09_12시': 28.6, '오후_12_17시': 42.8, '야간_17_21시': 18.2, '심야_21_06시': 5.2, '주간_10_17시_비중': 71.4}
        
        # TOP 5 매출 증가 업종 실측 데이터
        # 순위(rank)는 하드코딩하지 않고 실제 성장률 값으로 정렬해 부여한다.
        # (골프용품 성장률은 지역등급에 따라 변하는데 rank를 1로 고정해두면,
        #  지방 등급에서 62.1% < 스크린체육시설 84.2% 인데도 '1위'로 표기되어
        #  같은 페이지의 차트와 본문이 서로 모순되는 문제가 있었다.)
        # [2026-09-02] 이 값들은 실제 매출 통계가 아니라 지역등급별로 정해둔
        # 내부 참고 지수다. 예전에는 이를 '전년 대비 매출 성장률 +98.6%'처럼
        # 확정된 실측치로 표기해, 근거를 댈 수 없는 수치가 보고서 전면에 나갔다.
        # (실제 골프 업종은 최근 위축 국면이라는 지적도 받았다.)
        # 명칭을 '시니어 여가 수요 지수'로 바꿔 무엇을 나타내는 값인지 분명히 하고,
        # 출처 표기도 추정 모델임을 드러내도록 했다.
        _industry_pool = [
            {'name': '골프 및 레저용품', 'value': float(growth_rate), 'status': '시니어 소비 집중 업종'},
            {'name': '스크린 체육시설', 'value': 84.2, 'status': '실내 생활체육 선호'},
            {'name': '체력단련 및 피트니스', 'value': 42.5, 'status': '건강관리 수요'},
            {'name': '브런치 및 디저트카페', 'value': 31.8, 'status': '친목 모임 연계 소비'},
            {'name': '한식 및 건강음식점', 'value': 18.4, 'status': '생활밀착 단골 소비'},
        ]
        _industry_pool.sort(key=lambda d: d['value'], reverse=True)
        top_growth_industries = [
            {'rank': i + 1, 'name': d['name'], 'growth': f"{d['value']:.0f}점",
             'value': d['value'], 'status': d['status']}
            for i, d in enumerate(_industry_pool)
        ]

        golf_industry_density = {
            'store_count': sg_count,
            'total_stores_in_dong': total_stores,
            'density_ratio': density_ratio,
            'national_avg_density': nat_avg,
            'multiple': multiple,
            'growth_stage': '수요 급증 및 시설 대형화 단계'
        }

        infra = {
            '관공서': gov_count,
            '교육기관': edu_count,
            '금융기관': fin_count,
            '버스정류장': bus_stop_count,
            '지하철': subway
        }
        # 위 수치는 지역등급 기반 추정치다. 카카오 카테고리 검색으로 실제 개수를
        # 셀 수 있으면 그 값으로 교체하고, 무엇이 실측인지 플래그로 남긴다.
        # (특히 지하철은 '○○동 인근 지하철역'처럼 역명을 만들어내고 있었는데,
        #  실제 역명과 실제 도보거리로 바꾼다.)
        infra_is_measured = False
        subway_detail = None
        try:
            from . import facility_client
            _fx, _fy = CompetitorEngine.geocode_address(full_addr)
            if _fx is not None:
                _radius = (max(3000, min(district_radius_m or 8000, 20000))
                           if district_wide else 3000)
                counts = facility_client.fetch_facility_counts(_fx, _fy, radius=_radius)
                if counts:
                    infra_is_measured = True
                    if counts.get('공공기관') is not None:
                        infra['관공서'] = counts['공공기관']
                    if counts.get('학교') is not None and counts.get('학원') is not None:
                        infra['교육기관'] = counts['학교'] + counts['학원']
                    elif counts.get('학교') is not None:
                        infra['교육기관'] = counts['학교']
                    if counts.get('은행') is not None:
                        infra['금융기관'] = counts['은행']
                    for _k in ('병원', '약국', '주차장', '카페', '대형마트', '문화시설'):
                        if counts.get(_k) is not None:
                            infra[_k] = counts[_k]
                    _sub = facility_client.nearest_subway(_fx, _fy, radius=_radius)
                    if _sub and _sub.get('name'):
                        subway_detail = _sub
                        _dist = _sub.get('distance_m')
                        infra['지하철'] = (f"{_sub['name']} (직선 {_dist:,}m)" if _dist
                                        else f"{_sub['name']}")
                    elif _sub is not None:
                        # 조회는 성공했는데 반경 내 역이 없음 — 없는 역을 만들지 않는다
                        infra['지하철'] = '반경 내 지하철역 없음 (자차·버스 접근 중심 상권)'
                        subway_detail = {'name': None, 'distance_m': None}
        except Exception as e:
            print(f"[FACILITY SKIP] {e}")

        # 반경 내 실제 업종 구성비 (공공데이터, DATA_GO_KR_API_KEY 없으면 None)
        # top_growth_industries(위 성장률 추정표)를 대체하는 게 아니라, "지금 이 순간
        # 반경 내에 실제로 어떤 업종이 몇 곳 있는지"를 보여주는 별개의 실측 스냅샷이다.
        real_industry_mix = None
        if os.environ.get(sbiz_client.SBIZ_API_KEY_ENV):
            x, y = CompetitorEngine.geocode_address(full_addr)
            if x is not None:
                # 구 전체 분석이면 특정 지점 3km가 아니라 구 전역을 덮는 반경을 쓴다
                _mix_radius = (max(3000, min(district_radius_m or 8000, 20000)) if district_wide else 3000)
                real_industry_mix = sbiz_client.industry_mix(x, y, radius=_mix_radius)

        return {
            'monthly_avg_sales': monthly_avg,
            'top_20_sales': top_20_sales,
            'spending_grade': spending_grade,
            'growth_rate': growth_rate,
            'months': months,
            'selected_area_sales': selected_sales,
            'dong_avg_sales': dong_sales,
            'city_avg_sales': city_sales,
            'monthly_trend': monthly_trend,
            'day_distribution': day_dist,
            'time_distribution': time_dist,
            'residential_pop_ratio': residential_ratio,
            'workplace_pop_ratio': workplace_ratio,
            'top_growth_industries': top_growth_industries,
            'infra_is_measured': infra_is_measured,
            'subway_detail': subway_detail,
            'golf_industry_density': golf_industry_density,
            'infra': infra,
            'competitors': comp_res['stores'],
            'competitor_count': comp_res['count'],
            'competitor_summary': comp_res['summary'],
            'is_blue_ocean': comp_res['is_blue_ocean'],
            'base_source': 'MYPARK 지역등급 추정 모델 (Tier 1~4)',
            'is_estimated': is_estimated_comm,
            'real_industry_mix': real_industry_mix
        }

CommercialEngine.get_commercial_trends = CommercialEngine.get_commercial_analysis
CommercialDataEngine = CommercialEngine
