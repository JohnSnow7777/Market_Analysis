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
        commercial = CommercialDataEngine.get_commercial_trends(address)
        competitors = CompetitorEngine.search_competitors(address, site_info['sigungu'], site_info['dong'])
        commercial['competitors'] = competitors['stores']
        commercial['competitor_summary'] = competitors['summary']
        commercial['is_blue_ocean'] = competitors['is_blue_ocean']
        
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
        
        Visualizer.generate_sales_trend_chart(commercial, chart_sales)
        Visualizer.generate_radar_score_chart(scores, chart_radar)
        Visualizer.generate_profit_forecast_chart(financials['forecast_5year'], chart_profit)
        Visualizer.generate_radius_map(site_info, competitors, map_radius)
        
        charts = {
            'sales_trend': chart_sales,
            'radar_score': chart_radar,
            'profit_forecast': chart_profit,
            'map_radius': map_radius
        }
        
        bundle = {
            'site': site_info,
            'demographics': demographics,
            'commercial': commercial,
            'competitors': competitors,
            'financials': financials,
            'scores': scores,
            'score': scores,
            'charts': charts,
            'created_at': datetime.now().strftime("%Y. %m. %d")
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
            'total_revenue_moderate': financials['monthly_scenarios']['moderate']['total_revenue']
        }
