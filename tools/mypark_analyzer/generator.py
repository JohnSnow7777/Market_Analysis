# -*- coding: utf-8 -*-
"""마이파크 상권 및 사업분석 종합 생성기 파이프라인"""
import os
import time
from concurrent.futures import ThreadPoolExecutor
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
from .address_resolver import AddressResolver, validate_address, AddressNotResolvedError

class MyParkReportGenerator:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def analyze_and_generate(self, address, building_name=None, rooms=None, monthly_rent=None, area_pyeong=None, staff_count=None, special_notes=None):
        # 확인되지 않은 주소로는 보고서를 만들지 않는다. 존재하지 않는 주소에도
        # 등급·회수기간이 붙은 완성 문서가 나가면 그 자체가 허위 자료가 된다.
        _t = {}
        _t0 = time.time()

        def _lap(name, start):
            _t[name] = round(time.time() - start, 2)
            return time.time()

        resolved = validate_address(address)
        _m = _lap('validate', _t0)
        site_info = GeoEngine.analyze_site(address, building_name, area_pyeong, rooms, monthly_rent, staff_count, special_notes)
        _m = _lap('geo', _m)
        demographics = DemographicsEngine.get_demographics(address)
        _m = _lap('demographics', _m)
        _district_wide = demographics.get('district_wide_analysis', False)
        _district_radius_m = demographics.get('district_radius_m')
        # 상권 분석과 경쟁사 검색은 서로 의존하지 않고 각각 외부 API를 여러 번
        # 호출한다(응답의 대부분이 이 대기 시간이다). 순차로 두면 두 시간이
        # 그대로 더해지므로 병렬로 실행한다.
        with ThreadPoolExecutor(max_workers=2) as _ex:
            _f_comm = _ex.submit(
                CommercialDataEngine.get_commercial_trends,
                address, _district_wide, _district_radius_m)
            _f_comp = _ex.submit(
                CompetitorEngine.search_competitors,
                address, site_info['sigungu'], site_info['dong'],
                _district_wide, _district_radius_m)
            commercial = _f_comm.result()
            competitors = _f_comp.result()
        _m = _lap('commercial+competitors(병렬)', _m)
        commercial['competitors'] = competitors['stores']
        commercial['competitor_summary'] = competitors['summary']
        commercial['is_blue_ocean'] = competitors['is_blue_ocean']
        # 채점은 '실제로 확인된 경쟁사 수'만 사용한다.
        # (미확인 지역의 참고용 가상 시나리오 4곳을 실제 경쟁사로 세면 안 됨)
        commercial['competitor_verified_count'] = competitors.get('verified_count')
        commercial['competitor_is_verified'] = competitors.get('is_verified', False)
        
        # [2026-09-02] 손익 기준을 '건물주(자가 소유)'로 전환.
        # 가맹 상담 대상의 다수가 건물을 보유한 점주라 임대료가 발생하지 않는다.
        # 임대료를 기본 비용으로 깔면 실제 조건과 다른 보수적 수치가 대표값이
        # 되므로, 건물주 기준을 본문으로 두고 임차 시나리오를 참고선으로 병기한다.
        # 전제(임대료 미포함)는 보고서 전반에 명시해 임차 고객이 오해하지 않게 한다.
        financials = FinanceEngine.get_full_financial_analysis(
            rooms=site_info['rooms'],
            monthly_rent=0,
            area_pyeong=site_info['area_pyeong'],
            staff_count=site_info['staff_count'],
            demographics=demographics,
            commercial=commercial
        )
        # 참고선: 입력(또는 지역 시세 추정) 임대료를 반영한 임차인 기준
        financials_tenant = FinanceEngine.get_full_financial_analysis(
            rooms=site_info['rooms'],
            monthly_rent=site_info['monthly_rent'],
            area_pyeong=site_info['area_pyeong'],
            staff_count=site_info['staff_count'],
            demographics=demographics,
            commercial=commercial
        )
        
        _m = _lap('financials', _m)
        scores = ScoringEngine.evaluate_site(demographics, commercial, site_info, financials)
        _m = _lap('scoring', _m)
        
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

        _m = _lap('charts(7종)', _m)
        charts = {
            'sales_trend': chart_sales,
            'radar_score': chart_radar,
            'profit_forecast': chart_profit,
            'map_radius': map_radius,
            'growth_radar': chart_growth,
            'waterfall_cost': chart_waterfall,
            'bep_chart': chart_bep
        }
        
        # 임차인(임대료 지불) 참고 시나리오 — 웹/PDF/PPTX가 동일한 값을 쓰도록
        # 여기서 한 번만 계산해 bundle에 포함한다. 본문은 건물주 기준이다.
        _tenant_inv = financials_tenant['investment']
        tenant_payback = _tenant_inv['payback_months_moderate']
        tenant_bep_turns = _tenant_inv['bep_turns_per_room']

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
            # 손익 기준 표기용 — 보고서 전반에서 전제를 밝히는 데 쓴다.
            'financial_basis': 'owner',
            'financial_basis_label': '건물주(자가 소유, 임대료 미포함) 기준',
            'financials_tenant': financials_tenant,
            'tenant_payback_months': tenant_payback,
            'tenant_bep_turns_per_room': tenant_bep_turns,
            'tenant_monthly_rent': site_info['monthly_rent'],
        }

        safe_name = site_info['building_name'].replace(' ', '_').replace('/', '_')
        date_str = datetime.now().strftime("%y%m%d")
        now = datetime.now()
        date_kor = f"{now.strftime('%y')}년{now.month}월{now.day}일"

        pptx_path = os.path.join(self.output_dir, f"{date_str}_마이파크_{safe_name}_상권및사업분석_{date_kor}.pptx")
        pdf_path = os.path.join(self.output_dir, f"{date_str}_마이파크_{safe_name}_상권및사업분석_{date_kor}.pdf")

        _m2 = time.time()
        PPTXGenerator().generate(bundle, pptx_path)
        _m2 = _lap('pptx', _m2)
        PDFGenerator().generate(bundle, pdf_path)
        _lap('pdf', _m2)
        _t['합계'] = round(time.time() - _t0, 2)
        bundle['_timing'] = _t
        print(f"[TIMING] {_t}")

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
            'financial_basis_label': '건물주(자가 소유, 임대료 미포함) 기준',
            'tenant_payback_months': tenant_payback,
        }
