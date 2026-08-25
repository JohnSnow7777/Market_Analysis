# -*- coding: utf-8 -*-
"""마이파크 상권 및 사업분석 전체 파이프라인 총괄 통합 모듈"""
import os
import re
import datetime
from .geo_engine import GeoEngine
from .demographics import DemographicsEngine
from .commercial_data import CommercialDataEngine
from .finance_engine import FinanceEngine
from .scoring_engine import ScoringEngine
from .visualizer import Visualizer
from .pptx_generator import PPTXGenerator
from .docx_generator import DOCXGenerator

class MyParkReportGenerator:
    """주소 입력부터 보고서 자동 생성까지 원클릭 처리 엔진"""
    
    def __init__(self, output_dir='output'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def analyze_and_generate(self, address, building_name=None, rooms=None, monthly_rent=None, staff_count=None, area_pyeong=None):
        # 1. 지리 및 입지 스펙 (미입력 파라미터는 상권/지역 시세 기반 스마트 자동 추정)
        site_info = GeoEngine.analyze_site(
            address=address,
            building_name=building_name,
            area_pyeong=area_pyeong,
            rooms=rooms,
            monthly_rent=monthly_rent,
            staff_count=staff_count
        )
        
        actual_rooms = site_info['rooms']
        actual_rent = site_info['monthly_rent']
        actual_staff = site_info['staff_count']
        
        # 2. 인구 통계 데이터
        demographics = DemographicsEngine.get_demographics(address)
        
        # 3. 상권 및 소상공인 매출
        commercial = CommercialDataEngine.get_commercial_trends(address)
        
        # 4. 정밀 재무 시뮬레이션
        financials = FinanceEngine.get_full_financial_analysis(actual_rooms, actual_rent, actual_staff)
        
        # 5. 5대 지표 채점 및 피칭 생성
        scores = ScoringEngine.evaluate_site(demographics, commercial, site_info, financials)
        
        # 6. 차트 생성
        chart_dir = os.path.join(self.output_dir, 'charts')
        os.makedirs(chart_dir, exist_ok=True)
        
        radar_chart_path = os.path.join(chart_dir, 'radar_score.png')
        sales_trend_path = os.path.join(chart_dir, 'sales_trend.png')
        profit_chart_path = os.path.join(chart_dir, 'profit_forecast.png')
        
        Visualizer.create_radar_chart(scores['scores'], radar_chart_path)
        Visualizer.create_sales_trend_chart(commercial, sales_trend_path)
        Visualizer.create_5year_profit_chart(financials, profit_chart_path)
        
        charts = {
            'radar_score': radar_chart_path,
            'sales_trend': sales_trend_path,
            'profit_forecast': profit_chart_path
        }
        
        bundle = {
            'site': site_info,
            'demographics': demographics,
            'commercial': commercial,
            'financials': financials,
            'scores': scores,
            'charts': charts,
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        # 파일명 생성 (한국어 지원)
        raw_name = site_info['building_name']
        clean_name = re.sub(r'[^0-9a-zA-Z가-힣_]', '_', str(raw_name))
        clean_name = re.sub(r'_+', '_', clean_name).strip('_')
        
        date_str = datetime.datetime.now().strftime('%y%m%d')
        pptx_filename = f"{date_str}_마이파크_{clean_name}_상권및사업분석_v1.0.pptx"
        docx_filename = f"{date_str}_마이파크_{clean_name}_출점타당성보고서_v1.0.docx"
        
        pptx_path = os.path.join(self.output_dir, pptx_filename)
        docx_path = os.path.join(self.output_dir, docx_filename)
        
        # 7. PPTX 및 DOCX 생성
        pptx_gen = PPTXGenerator()
        pptx_gen.generate(bundle, pptx_path)
        
        docx_gen = DOCXGenerator()
        docx_gen.generate(bundle, docx_path)
        
        return {
            'status': 'SUCCESS',
            'grade': scores['grade'],
            'total_score': scores['total_score'],
            'total_revenue_moderate': financials['monthly_scenarios']['moderate']['total_revenue'],
            'operating_profit_moderate': financials['monthly_scenarios']['moderate']['operating_profit'],
            'payback_months': financials['investment']['payback_months_moderate'],
            'pptx_path': os.path.abspath(pptx_path),
            'docx_path': os.path.abspath(docx_path),
            'bundle': bundle
        }
