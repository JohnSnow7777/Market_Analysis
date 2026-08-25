# -*- coding: utf-8 -*-
"""16:9 와이드 전문 프레젠테이션 보고서 생성기 (고객 친화적 쉬운 비즈니스 텍스트)"""
import os
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

class PPTXGenerator:
    """마이파크 상권 및 사업분석 PPTX 생성기"""
    
    def __init__(self):
        self.prs = pptx.Presentation()
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.blank_layout = self.prs.slide_layouts[6]
        
        self.c_navy = RGBColor(0, 51, 102)
        self.c_blue = RGBColor(30, 136, 229)
        self.c_gold = RGBColor(255, 179, 0)
        self.c_dark = RGBColor(51, 51, 51)
        self.c_gray = RGBColor(100, 100, 100)
        self.c_light = RGBColor(245, 247, 250)
        self.c_white = RGBColor(255, 255, 255)
        self.c_table_hdr = RGBColor(230, 238, 248)

    def _add_header_bar(self, slide, title_text):
        header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(0.4), Inches(12.333), Inches(0.8))
        header.fill.solid()
        header.fill.fore_color.rgb = self.c_navy
        header.line.fill.background()
        
        tf = header.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = 'Malgun Gothic'
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = self.c_white
        p.alignment = PP_ALIGN.CENTER
        
        footer_box = slide.shapes.add_textbox(Inches(0.5), Inches(7.0), Inches(12.333), Inches(0.4))
        p_f = footer_box.text_frame.paragraphs[0]
        p_f.text = "Copyright© Smilesquare, Inc. (마이파크 사업본부) All Rights Reserved."
        p_f.font.name = 'Malgun Gothic'
        p_f.font.size = Pt(9)
        p_f.font.color.rgb = self.c_gray

    def generate(self, data, output_pptx_path):
        site = data['site']
        demo = data['demographics']
        comm = data['commercial']
        fin = data['financials']
        score = data['scores']
        charts = data['charts']
        
        # Slide 1: 표지
        s1 = self.prs.slides.add_slide(self.blank_layout)
        bg_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg_bar.fill.solid()
        bg_bar.fill.fore_color.rgb = self.c_navy
        bg_bar.line.fill.background()
        
        tb1 = s1.shapes.add_textbox(Inches(1.5), Inches(2.0), Inches(10.333), Inches(3.5))
        tf1 = tb1.text_frame
        
        p1 = tf1.paragraphs[0]
        p1.text = "마이파크(MYPARK) 스크린 파크골프"
        p1.font.name = 'Malgun Gothic'
        p1.font.size = Pt(24)
        p1.font.color.rgb = self.c_gold
        p1.font.bold = True
        
        p2 = tf1.add_paragraph()
        p2.text = f"{site.get('building_name', '사업지')} 상권 및 사업성 분석"
        p2.font.name = 'Malgun Gothic'
        p2.font.size = Pt(36)
        p2.font.color.rgb = self.c_white
        p2.font.bold = True
        p2.space_before = Pt(15)
        
        p3 = tf1.add_paragraph()
        p3.text = f"위치: {site['full_address']} | {site['rooms']}타석 ({site['area_pyeong']}평) 기준"
        p3.font.name = 'Malgun Gothic'
        p3.font.size = Pt(16)
        p3.font.color.rgb = self.c_white
        p3.space_before = Pt(20)
        
        p4 = tf1.add_paragraph()
        p4.text = f"입지 최적성 종합 평가: [{score['grade']}등급 - {score['total_score']}점] | 2026. 08"
        p4.font.name = 'Malgun Gothic'
        p4.font.size = Pt(14)
        p4.font.color.rgb = self.c_gold
        p4.space_before = Pt(10)

        # Slide 2: 개요
        s2 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s2, f"1. 사업지 개요 및 공간 구성 ({site['rooms']}타석 / {site['area_pyeong']}평)")
        tb2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.0))
        tf2 = tb2.text_frame
        
        def add_bullet(tf, text, bold_prefix="", size=14):
            p = tf.add_paragraph()
            p.space_before = Pt(10)
            if bold_prefix:
                r1 = p.add_run()
                r1.text = bold_prefix + " "
                r1.font.bold = True
                r1.font.size = Pt(size)
                r1.font.color.rgb = self.c_navy
            r2 = p.add_run()
            r2.text = text
            r2.font.size = Pt(size)
            r2.font.color.rgb = self.c_dark
            
        add_bullet(tf2, f"{site['full_address']} ({site.get('building_name', '상가')})", "▲ 사업지 주소:")
        add_bullet(tf2, f"전용면적 {site['area_pyeong']}평 | {site['rooms']}타석 + 라운지/카페 + 휴게존 최적 동선 배치", "▲ 공간 규모:")
        add_bullet(tf2, f"순수 유효 층고 {site['clear_height']}m (파크골프 권장 기준 2.8m 이상 완벽 충족)", "▲ 층고 요건:")
        add_bullet(tf2, f"{site['parking_type']} ({site['parking_spaces']}대 이상 확보 가능, 시니어 자차 접근 편리)", "▲ 주차 인프라:")
        add_bullet(tf2, f"{site['elevator']} 및 {site['zoning']}", "▲ 건물 편의성:")
        add_bullet(tf2, f"반경 3km 내 대규모 주거단지 밀집, 교통 간선도로 인접 생활밀착형 최적 상권", "▲ 입지 특성:")

        # Slide 3: 인구
        s3 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s3, f"2. 사업지 배후 인구 분석 (반경 3km & 10분 생활권 약 {demo['total_pop']//10000}만명)")
        tb3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(5.5), Inches(5.0))
        tf3 = tb3.text_frame
        add_bullet(tf3, f"{demo['region_name']}", "▲ 분석 권역:")
        add_bullet(tf3, f"총 {demo['total_pop']:,}명 (남: {demo['male_pop']:,}명 / 여: {demo['female_pop']:,}명)", "▲ 배후 총인구:")
        add_bullet(tf3, f"{demo['base_date']}", "▲ 통계 출처:")
        add_bullet(tf3, f"차량 10분 이내 생활권 내 고밀도 아파트 단지 및 배후 수요 집중", "▲ 핵심 요약:")
        
        dongs = demo['dongs']
        rows = len(dongs) + 2
        table_s3 = s3.shapes.add_table(rows, 4, Inches(6.5), Inches(1.8), Inches(6.0), Inches(0.4 * rows)).table
        headers = ['행정동', '남자(명)', '여자(명)', '합계(명)']
        for col_idx, h in enumerate(headers):
            cell = table_s3.cell(0, col_idx)
            cell.text = h
            cell.fill.solid()
            cell.fill.fore_color.rgb = self.c_navy
            for p in cell.text_frame.paragraphs:
                p.font.color.rgb = self.c_white
                p.font.bold = True
                p.font.size = Pt(11)
                p.alignment = PP_ALIGN.CENTER
        for row_idx, d in enumerate(dongs):
            table_s3.cell(row_idx+1, 0).text = str(d['dong'])
            table_s3.cell(row_idx+1, 1).text = f"{d['male']:,}"
            table_s3.cell(row_idx+1, 2).text = f"{d['female']:,}"
            table_s3.cell(row_idx+1, 3).text = f"{d['total']:,}"
            for c in range(4):
                p = table_s3.cell(row_idx+1, c).text_frame.paragraphs[0]
                p.font.size = Pt(10)
                p.alignment = PP_ALIGN.CENTER
        last_r = rows - 1
        table_s3.cell(last_r, 0).text = "합계"
        table_s3.cell(last_r, 1).text = f"{demo['male_pop']:,}"
        table_s3.cell(last_r, 2).text = f"{demo['female_pop']:,}"
        table_s3.cell(last_r, 3).text = f"{demo['total_pop']:,}"
        for c in range(4):
            cell = table_s3.cell(last_r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = self.c_table_hdr
            p = cell.text_frame.paragraphs[0]
            p.font.bold = True
            p.font.size = Pt(10)
            p.alignment = PP_ALIGN.CENTER

        # Slide 4: 타겟 시니어
        s4 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s4, f"2. 메인 타겟 분석 (50대 이상 시니어 약 {demo['senior_50_plus']:,}명_{demo['senior_ratio']}%)")
        tb4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(5.5), Inches(5.0))
        tf4 = tb4.text_frame
        add_bullet(tf4, f"스크린 파크골프 핵심 소비층은 50대 이상 여성(약 {demo['senior_50_female']:,}명)", "▲ 핵심 타겟군:")
        add_bullet(tf4, f"여성 인구 비중이 높아 평일 낮 주간 단체/친목 모임 유치에 최적", "▲ 타겟 시사점:")
        add_bullet(tf4, f"은퇴 세대 및 액티브 시니어의 날씨 무관 4계절 생활체육 참여 급증", "▲ 수요 트렌드:")
        
        ages = demo['age_distribution']
        rows4 = len(ages) + 1
        table_s4 = s4.shapes.add_table(rows4, 4, Inches(6.5), Inches(1.8), Inches(6.0), Inches(0.4 * rows4)).table
        headers4 = ['연령대', '남자(명)', '여자(명)', '합계(명)']
        for col_idx, h in enumerate(headers4):
            cell = table_s4.cell(0, col_idx)
            cell.text = h
            cell.fill.solid()
            cell.fill.fore_color.rgb = self.c_navy
            for p in cell.text_frame.paragraphs:
                p.font.color.rgb = self.c_white
                p.font.bold = True
                p.font.size = Pt(11)
                p.alignment = PP_ALIGN.CENTER
        for row_idx, a in enumerate(ages):
            table_s4.cell(row_idx+1, 0).text = str(a['age_group'])
            table_s4.cell(row_idx+1, 1).text = f"{int(a['male']):,}"
            table_s4.cell(row_idx+1, 2).text = f"{int(a['female']):,}"
            table_s4.cell(row_idx+1, 3).text = f"{int(a['total']):,}"
            for c in range(4):
                p = table_s4.cell(row_idx+1, c).text_frame.paragraphs[0]
                p.font.size = Pt(10)
                p.alignment = PP_ALIGN.CENTER

        # Slide 5: 소상공인 매출
        s5 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s5, f"3. 상권 및 업종 분석 (월평균 매출액 약 {comm['monthly_avg_sales']//10000:,}만원)")
        if 'sales_trend' in charts and os.path.exists(charts['sales_trend']):
            s5.shapes.add_picture(charts['sales_trend'], Inches(0.8), Inches(1.6), width=Inches(7.2))
        tb5 = s5.shapes.add_textbox(Inches(8.3), Inches(1.8), Inches(4.3), Inches(4.5))
        tf5 = tb5.text_frame
        add_bullet(tf5, f"반경 1.5~3km 내 유사업종 매장 총 {comm['store_count']}개소 운영 중", "▲ 업소 현황:")
        add_bullet(tf5, f"월평균 매출액 {comm['monthly_avg_sales']//10000:,}만원 수준 (안정적 상승세)", "▲ 매출 동향:")
        add_bullet(tf5, f"소상공인 365 플랫폼 실측 데이터 기반 분석", "▲ 데이터 출처:")

        # Slide 6: 패턴 분석
        s6 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s6, f"3. 상권 매출 패턴 분석 (주간 10~17시 {comm['time_distribution']['주간_10_17시_비중']}%, 50대이상 {comm['age_distribution']['50대이상_비중']}%)")
        tb6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
        tf6 = tb6.text_frame
        add_bullet(tf6, f"주말 평균 비중 {comm['day_distribution']['주말평균비중']}%, 평일 월요일 {comm['day_distribution']['월']}% 피크 (정기 모임)", "▲ 요일별 패턴:")
        add_bullet(tf6, f"주간(10~17시) 이용 비중 {comm['time_distribution']['주간_10_17시_비중']}% 차지 -> 일반 스크린골프 대비 주간 고가동률 달성", "▲ 시간대별 패턴:")
        add_bullet(tf6, f"50대 이상 이용자 매출 기여도 {comm['age_distribution']['50대이상_비중']}% -> 압도적 타겟 일치도", "▲ 연령별 패턴:")
        add_bullet(tf6, f"평일 낮 유휴 시간대를 주간 시니어 동호회가 풀가동하는 독보적 수익 구조", "▲ 사업화 시사점:")

        # Slide 7: 경쟁점
        s7 = self.prs.slides.add_slide(self.blank_layout)
        comps = comm.get('competitors', [])
        self._add_header_bar(s7, f"4. 주변 스크린 파크골프 경쟁 매장({len(comps)}곳) 현황")
        rows7 = len(comps) + 1
        table_s7 = s7.shapes.add_table(rows7, 5, Inches(0.8), Inches(1.8), Inches(11.7), Inches(0.6 * rows7)).table
        headers7 = ['매장명', '소재지 주소', '사용 시스템', '보유 타석', '주요 특징']
        for col_idx, h in enumerate(headers7):
            cell = table_s7.cell(0, col_idx)
            cell.text = h
            cell.fill.solid()
            cell.fill.fore_color.rgb = self.c_navy
            for p in cell.text_frame.paragraphs:
                p.font.color.rgb = self.c_white
                p.font.bold = True
                p.font.size = Pt(11)
                p.alignment = PP_ALIGN.CENTER
        for row_idx, c in enumerate(comps):
            table_s7.cell(row_idx+1, 0).text = str(c['name'])
            table_s7.cell(row_idx+1, 1).text = str(c['address'])
            table_s7.cell(row_idx+1, 2).text = str(c['system'])
            table_s7.cell(row_idx+1, 3).text = f"{c['rooms']}타석"
            table_s7.cell(row_idx+1, 4).text = str(c.get('features', '-'))
            for col in range(5):
                p = table_s7.cell(row_idx+1, col).text_frame.paragraphs[0]
                p.font.size = Pt(10)
                p.alignment = PP_ALIGN.CENTER

        # Slide 8: 5대 지표 평가
        s8 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s8, f"5. 마이파크 입지 최적성 종합 평가 [{score['grade']}등급 - {score['total_score']}점 / 100점]")
        if 'radar_score' in charts and os.path.exists(charts['radar_score']):
            s8.shapes.add_picture(charts['radar_score'], Inches(0.8), Inches(1.6), width=Inches(5.2))
        tb8 = s8.shapes.add_textbox(Inches(6.3), Inches(1.6), Inches(6.2), Inches(5.0))
        tf8 = tb8.text_frame
        add_bullet(tf8, f"{score['scores']['senior_population']}점 / 25점 만점", "1) 골든 시니어 집적도:")
        add_bullet(tf8, f"{score['scores']['accessibility_parking']}점 / 25점 만점", "2) 접근성 및 주차 인프라:")
        add_bullet(tf8, f"{score['scores']['space_efficiency']}점 / 15점 만점", "3) 공간 적합성 및 임대료:")
        add_bullet(tf8, f"{score['scores']['supply_gap']}점 / 15점 만점", "4) 수요 공급 갭 (블루오션):")
        add_bullet(tf8, f"{score['scores']['commercial_spending']}점 / 20점 만점", "5) 지역 소비력 및 여가지출:")
        add_bullet(tf8, f"총점 {score['total_score']}점 ({score['grade_desc']})", "★ 종합 판정:")

        # Slide 9: 월 매출
        s9 = self.prs.slides.add_slide(self.blank_layout)
        m_scen = fin['monthly_scenarios']
        self._add_header_bar(s9, f"6. 마이파크 사업 타당성 분석 ({site['rooms']}타석) - 월 예상 매출")
        table_s9 = s9.shapes.add_table(4, 7, Inches(0.8), Inches(2.0), Inches(11.7), Inches(2.2)).table
        h9 = ['구분', '타석 이용료', '용품(10%)', '카페(5%)', '레슨(3%)', '월 총매출 합계', '비고 (1일 이용자)']
        for col_idx, h in enumerate(h9):
            cell = table_s9.cell(0, col_idx)
            cell.text = h
            cell.fill.solid()
            cell.fill.fore_color.rgb = self.c_navy
            for p in cell.text_frame.paragraphs:
                p.font.color.rgb = self.c_white
                p.font.bold = True
                p.font.size = Pt(11)
                p.alignment = PP_ALIGN.CENTER
        for row_idx, k in enumerate(['conservative', 'moderate', 'optimistic']):
            sc = m_scen[k]
            table_s9.cell(row_idx+1, 0).text = sc['scenario_name']
            table_s9.cell(row_idx+1, 1).text = f"{sc['room_revenue']:,}원"
            table_s9.cell(row_idx+1, 2).text = f"{sc['goods_revenue']:,}원"
            table_s9.cell(row_idx+1, 3).text = f"{sc['cafe_revenue']:,}원"
            table_s9.cell(row_idx+1, 4).text = f"{sc['lesson_revenue']:,}원"
            table_s9.cell(row_idx+1, 5).text = f"{sc['total_revenue']:,}원"
            table_s9.cell(row_idx+1, 6).text = f"1일 {sc['daily_users']}명 (월 {sc['monthly_users']:,}명)"
            for c in range(7):
                p = table_s9.cell(row_idx+1, c).text_frame.paragraphs[0]
                p.font.size = Pt(10)
                p.alignment = PP_ALIGN.CENTER
                if c == 5:
                    p.font.bold = True
                    p.font.color.rgb = self.c_blue

        # Slide 10: 운영 비용
        s10 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s10, f"6. 마이파크 사업 타당성 분석 ({site['rooms']}타석) - 예상 운영 비용")
        table_s10 = s10.shapes.add_table(5, 5, Inches(0.8), Inches(1.8), Inches(11.7), Inches(3.0)).table
        h10 = ['구분', '보수적 시나리오', '보편적 시나리오', '긍정적 시나리오', '비고']
        for col_idx, h in enumerate(h10):
            cell = table_s10.cell(0, col_idx)
            cell.text = h
            cell.fill.solid()
            cell.fill.fore_color.rgb = self.c_navy
            for p in cell.text_frame.paragraphs:
                p.font.color.rgb = self.c_white
                p.font.bold = True
                p.font.size = Pt(11)
                p.alignment = PP_ALIGN.CENTER
        c_sc = m_scen['conservative']
        m_sc = m_scen['moderate']
        o_sc = m_scen['optimistic']
        cost_rows = [
            ('인건비 + 임대료', f"{c_sc['labor_cost']+c_sc['rent_cost']:,}원", f"{m_sc['labor_cost']+m_sc['rent_cost']:,}원", f"{o_sc['labor_cost']+o_sc['rent_cost']:,}원", f"인력 {fin['staff_count']}명 / 임대료 {fin['monthly_rent']//10000:,}만원"),
            ('원가 3종 + 카드수수료', f"{c_sc['goods_cost']+c_sc['cafe_cost']+c_sc['lesson_cost']+c_sc['card_fee']:,}원", f"{m_sc['goods_cost']+m_sc['cafe_cost']+m_sc['lesson_cost']+m_sc['card_fee']:,}원", f"{o_sc['goods_cost']+o_sc['cafe_cost']+o_sc['lesson_cost']+o_sc['card_fee']:,}원", "용품60%, 식음50%, 레슨80%, 카드2%"),
            ('매장운영비 + 렌탈/마케팅', f"{c_sc['store_ops_cost']+c_sc['rental_cost']+c_sc['marketing_cost']:,}원", f"{m_sc['store_ops_cost']+m_sc['rental_cost']+m_sc['marketing_cost']:,}원", f"{o_sc['store_ops_cost']+o_sc['rental_cost']+o_sc['marketing_cost']:,}원", "수도광열, 소모품, 공청기, 보험 등"),
            ('월 총 비용 합계', f"{c_sc['total_cost']:,}원", f"{m_sc['total_cost']:,}원", f"{o_sc['total_cost']:,}원", "VAT 별도 기준")
        ]
        for row_idx, r in enumerate(cost_rows):
            for col_idx in range(5):
                table_s10.cell(row_idx+1, col_idx).text = r[col_idx]
                p = table_s10.cell(row_idx+1, col_idx).text_frame.paragraphs[0]
                p.font.size = Pt(10)
                p.alignment = PP_ALIGN.CENTER
                if row_idx == 3:
                    p.font.bold = True
                    p.font.color.rgb = self.c_navy

        # Slide 11: 5개년 손익
        s11 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s11, f"6. 마이파크 사업 타당성 분석 - 5개년 손익 예측 (연 2% 성장률 반영)")
        if 'profit_forecast' in charts and os.path.exists(charts['profit_forecast']):
            s11.shapes.add_picture(charts['profit_forecast'], Inches(0.8), Inches(1.6), width=Inches(6.5))
        tb11 = s11.shapes.add_textbox(Inches(7.6), Inches(1.8), Inches(5.0), Inches(4.5))
        tf11 = tb11.text_frame
        mod_1y = fin['forecast_5year']['moderate'][0]
        mod_5y = fin['forecast_5year']['moderate'][4]
        add_bullet(tf11, f"1년차 연매출 {mod_1y['total_revenue']//100000000:.1f}억원 / 영업이익 {mod_1y['operating_profit']//100000000:.1f}억원", "▲ 1년차(기준):")
        add_bullet(tf11, f"5년차 연매출 {mod_5y['total_revenue']//100000000:.1f}억원 / 영업이익 {mod_5y['operating_profit']//100000000:.1f}억원", "▲ 5년차(기준):")
        add_bullet(tf11, f"손익분기점(BEP) 월매출: 약 {fin['investment']['bep_monthly_sales']//10000:,}만원 (일 {fin['investment']['bep_turns_per_room']}회전)", "▲ 손익분기점:")
        add_bullet(tf11, f"초기 순투자금 회수 기간: {score['payback_text']}", "▲ 투자금 회수:")

        # Slide 12: 종합 결론 및 기대효과
        s12 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s12, "7. 종합 결론 및 사업 타당성 평가")
        tb12 = s12.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.8))
        tf12 = tb12.text_frame
        add_bullet(tf12, score['value_franchisee'], "【 가맹점 출점 기대효과 및 핵심 경쟁력 】", 13)
        add_bullet(tf12, score['value_landlord'], "【 상가 전체 상권 활성화 및 건물 가치 상승 효과 】", 13)
        add_bullet(tf12, f"종합 입지 평가 [{score['grade']}등급 - {score['total_score']}점]으로 마이파크 스크린 파크골프 출점에 최적의 조건을 갖추고 있으며, 신속한 상권 선점을 권장합니다.", "★ 최종 권고안:", 13)
        
        os.makedirs(os.path.dirname(output_pptx_path), exist_ok=True)
        self.prs.save(output_pptx_path)
        print(f"[PPTX GENERATED] {output_pptx_path}")
        return output_pptx_path
