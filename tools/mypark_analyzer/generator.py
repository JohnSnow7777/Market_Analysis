# -*- coding: utf-8 -*-
"""마이파크 상권 및 사업분석 종합 생성기 파이프라인"""
import os
from datetime import datetime
from .geo_engine import GeoEngine
from .demographics import DemographicsEngine
from .commercial_data import CommercialDataEngine
from .competitor_engine import CompetitorEngine
from .finance_engine import FinanceEngine
from .scoring_engine import ScoringEngine
from .visualizer import Visualizer
from .pptx_generator import PPTXGenerator
from .pdf_generator import PDFGenerator
from .address_resolver import AddressResolver

class MyParkReportGenerator:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def analyze_and_generate(self, address, building_name=None, rooms=None, monthly_rent=None, area_pyeong=None, staff_count=None, special_notes=None):
        resolved = AddressResolver.resolve(address)
        site_info = GeoEngine.analyze_site(address, building_name, area_pyeong, rooms, monthly_rent, staff_count, special_notes)
        demographics = DemographicsEngine.get_demographics(address)
        _district_wide = demographics.get('district_wide_analysis', False)
        _district_radius_m = demographics.get('district_radius_m')
        commercial = CommercialDataEngine.get_commercial_trends(
            address, district_wide=_district_wide, district_radius_m=_district_radius_m)
        competitors = CompetitorEngine.search_competitors(
            address, site_info['sigungu'], site_info['dong'],
            district_wide=_district_wide, district_radius_m=_district_radius_m)
        commercial['competitors'] = competitors['stores']
        commercial['competitor_summary'] = competitors['summary']
        commercial['is_blue_ocean'] = competitors['is_blue_ocean']
        # 채점은 '실제로 확인된 경쟁사 수'만 사용한다.
        # (미확인 지역의 참고용 가상 시나리오 4곳을 실제 경쟁사로 세면 안 됨)
        commercial['competitor_verified_count'] = competitors.get('verified_count')
        commercial['competitor_is_verified'] = competitors.get('is_verified', False)
        
        financials = FinanceEngine.get_full_financial_analysis(
            rooms=site_info['rooms'],
            monthly_rent=site_info['monthly_rent'],
            area_pyeong=site_info['area_pyeong'],
            staff_count=site_info['staff_count'],
            demographics=demographics,
            commercial=commercial
        )
        
        scores = ScoringEngine.evaluate_site(demographics, commercial, site_info, financials)
        
        # 차트 및 상권 지도 이미지 생성
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        chart_dir = os.path.join(self.output_dir, "charts")
        
        chart_sales = os.path.join(chart_dir, f"sales_trend_{timestamp}.png")
        chart_radar = os.path.join(chart_dir, f"radar_score_{timestamp}.png")
        chart_profit = os.path.join(chart_dir, f"profit_forecast_{timestamp}.png")
        map_radius = os.path.join(chart_dir, f"map_radius_{timestamp}.png")
        chart_growth = os.path.join(chart_dir, f"growth_radar_{timestamp}.png")
        chart_waterfall = os.path.join(chart_dir, f"waterfall_cost_{timestamp}.png")
        chart_bep = os.path.join(chart_dir, f"bep_chart_{timestamp}.png")

        Visualizer.generate_sales_trend_chart(commercial, chart_sales)
        Visualizer.generate_radar_score_chart(scores, chart_radar)
        Visualizer.generate_profit_forecast_chart(financials['forecast_5year'], chart_profit, rooms=site_info['rooms'])
        Visualizer.generate_radius_map(site_info, competitors, map_radius, district_wide=_district_wide)
        Visualizer.generate_industry_growth_chart(commercial, chart_growth)
        Visualizer.generate_cost_waterfall_chart(financials['monthly_scenarios']['moderate'], chart_waterfall)
        Visualizer.generate_bep_chart(financials, chart_bep)

        charts = {
            'sales_trend': chart_sales,
            'radar_score': chart_radar,
            'profit_forecast': chart_profit,
            'map_radius': map_radius,
            'growth_radar': chart_growth,
            'waterfall_cost': chart_waterfall,
            'bep_chart': chart_bep
        }
        
        # 건물주(자가 소유, 임대료 없음) 참고 시나리오 — 웹/PDF/PPTX가 동일한 값을
        # 쓰도록 여기서 한 번만 계산해 bundle에 포함한다.
        owner_only_scenario = FinanceEngine.calculate_monthly_scenario(
            site_info['rooms'], 0, site_info['staff_count'], 'moderate')
        owner_only_op = owner_only_scenario['operating_profit']
        owner_only_payback = (financials['investment']['total_capex'] / owner_only_op) if owner_only_op > 0 else None

        bundle = {
            'site': site_info,
            'demographics': demographics,
            'commercial': commercial,
            'competitors': competitors,
            'financials': financials,
            'scores': scores,
            'score': scores,
            'charts': charts,
            'created_at': datetime.now().strftime("%Y. %m. %d"),
            'owner_only_payback_months': round(owner_only_payback, 1) if owner_only_payback else None
        }

        safe_name = site_info['building_name'].replace(' ', '_').replace('/', '_')
        date_str = datetime.now().strftime("%y%m%d")
        now = datetime.now()
        date_kor = f"{now.strftime('%y')}년{now.month}월{now.day}일"

        pptx_path = os.path.join(self.output_dir, f"{date_str}_마이파크_{safe_name}_상권및사업분석_{date_kor}.pptx")
        pdf_path = os.path.join(self.output_dir, f"{date_str}_마이파크_{safe_name}_상권및사업분석_{date_kor}.pdf")

        PPTXGenerator().generate(bundle, pptx_path)
        PDFGenerator().generate(bundle, pdf_path)

        return {
            'pptx_path': pptx_path,
            'pdf_path': pdf_path,
            'bundle': bundle,
            'total_score': scores['total_score'],
            'grade': scores['grade'],
            'payback_months': financials['investment']['payback_months_moderate'],
            'payback_text': scores['payback_text'],
            'operating_profit_moderate': financials['monthly_scenarios']['moderate']['operating_profit'],
            'total_revenue_moderate': financials['monthly_scenarios']['moderate']['total_revenue'],
            'owner_only_payback_months': round(owner_only_payback, 1) if owner_only_payback else None
        }
