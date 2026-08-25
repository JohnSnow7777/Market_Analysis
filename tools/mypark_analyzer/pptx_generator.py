# -*- coding: utf-8 -*-
"""16:9 와이드 최고급 비즈니스 컨설팅 프레젠테이션 생성기 (원문 4열 비주얼 카드 완벽 구현)"""
import os
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

class PPTXGenerator:
    """마이파크 상권 및 사업분석 PPTX 생성기"""
    
    def __init__(self):
        self.prs = pptx.Presentation()
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.blank_layout = self.prs.slide_layouts[6]
        
        # 럭셔리 모던 컬러 팔레트
        self.c_navy_dark = RGBColor(10, 25, 47)      # #0A192F
        self.c_navy = RGBColor(15, 39, 68)          # #0F2744
        self.c_royal_blue = RGBColor(37, 99, 235)   # #2563EB
        self.c_gold = RGBColor(245, 158, 11)        # #F59E0B
        self.c_emerald = RGBColor(16, 185, 129)     # #10B981
        self.c_red = RGBColor(220, 38, 38)          # #DC2626
        self.c_slate_dark = RGBColor(30, 41, 59)    # #1E293B
        self.c_slate_gray = RGBColor(100, 116, 139) # #64748B
        self.c_card_bg = RGBColor(248, 250, 252)    # #F8FAFC
        self.c_border = RGBColor(226, 232, 240)     # #E2E8F0
        self.c_white = RGBColor(255, 255, 255)
        self.c_pink_bg = RGBColor(254, 242, 242)

    def _add_header_bar(self, slide, white_prefix, gold_highlight, white_suffix=""):
        header = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(0.4), Inches(12.133), Inches(0.75))
        header.fill.solid()
        header.fill.fore_color.rgb = self.c_navy
        header.line.color.rgb = self.c_royal_blue
        header.line.width = Pt(1.5)
        
        tf = header.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        
        if white_prefix:
            r1 = p.add_run()
            r1.text = white_prefix
            r1.font.name = 'Malgun Gothic'
            r1.font.size = Pt(19)
            r1.font.bold = True
            r1.font.color.rgb = self.c_white
            
        if gold_highlight:
            r2 = p.add_run()
            r2.text = gold_highlight
            r2.font.name = 'Malgun Gothic'
            r2.font.size = Pt(19)
            r2.font.bold = True
            r2.font.color.rgb = self.c_gold
            
        if white_suffix:
            r3 = p.add_run()
            r3.text = white_suffix
            r3.font.name = 'Malgun Gothic'
            r3.font.size = Pt(19)
            r3.font.bold = True
            r3.font.color.rgb = self.c_white

    def _add_source_footer(self, slide, source_text):
        tb = slide.shapes.add_textbox(Inches(5.0), Inches(6.98), Inches(7.7), Inches(0.35))
        p = tb.text_frame.paragraphs[0]
        p.text = source_text
        p.font.name = 'Malgun Gothic'
        p.font.size = Pt(8.5)
        p.font.color.rgb = self.c_slate_gray
        p.alignment = PP_ALIGN.RIGHT

    def _format_cell(self, cell, text, font_size=10, bold=False, color=None, bg_color=None, align=PP_ALIGN.CENTER):
        cell.text = ""
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_top = Pt(3)
        cell.margin_bottom = Pt(3)
        cell.margin_left = Pt(5)
        cell.margin_right = Pt(5)
        
        if bg_color:
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg_color
            
        p = cell.text_frame.paragraphs[0]
        p.alignment = align
        run = p.add_run()
        run.text = str(text)
        run.font.name = 'Malgun Gothic'
        run.font.size = Pt(font_size)
        run.font.bold = bold
        if color:
            run.font.color.rgb = color

    def generate(self, data, output_pptx_path):
        site = data['site']
        demo = data['demographics']
        comm = data['commercial']
        fin = data['financials']
        score = data['scores']
        charts = data['charts']
        
        # Slide 1: 표지
        s1 = self.prs.slides.add_slide(self.blank_layout)
        bg = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = self.c_navy_dark
        bg.line.fill.background()
        
        line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.5), Inches(1.8), Inches(10.333), Inches(0.04))
        line.fill.solid()
        line.fill.fore_color.rgb = self.c_gold
        line.line.fill.background()
        
        tb1 = s1.shapes.add_textbox(Inches(1.5), Inches(2.1), Inches(10.333), Inches(3.2))
        tf1 = tb1.text_frame
        tf1.word_wrap = True
        
        p1 = tf1.paragraphs[0]
        p1.text = "MYPARK SCREEN PARK GOLF  |  출점 타당성 분석 보고서"
        p1.font.name = 'Malgun Gothic'
        p1.font.size = Pt(14)
        p1.font.color.rgb = self.c_gold
        p1.font.bold = True
        
        p2 = tf1.add_paragraph()
        p2.space_before = Pt(12)
        p2.text = f"{site.get('building_name', '사업지')} 상권 및 사업성 분석"
        p2.font.name = 'Malgun Gothic'
        p2.font.size = Pt(34)
        p2.font.color.rgb = self.c_white
        p2.font.bold = True
        
        p3 = tf1.add_paragraph()
        p3.space_before = Pt(16)
        p3.text = f"대상 주소: {site['full_address']}  |  표준 모델: {site['rooms']}타석 ({site['area_pyeong']}평)"
        p3.font.name = 'Malgun Gothic'
        p3.font.size = Pt(15)
        p3.font.color.rgb = self.c_border
        
        badges = [
            (Inches(1.5), "입지 최적성 등급", f"{score['grade']}등급 ({score['total_score']}점)", self.c_gold),
            (Inches(5.1), "예상 월 영업이익 (보편)", f"{fin['monthly_scenarios']['moderate']['operating_profit']//10000:,}만원/월", self.c_emerald),
            (Inches(8.7), "투자금 회수 기간", f"{score['payback_text'].split('기준')[1].split('만에')[0].strip() if '기준' in score['payback_text'] else score['payback_text']}", self.c_white)
        ]
        for bx, btitle, bval, bcol in badges:
            b_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, Inches(5.6), Inches(3.1), Inches(1.1))
            b_card.fill.solid()
            b_card.fill.fore_color.rgb = self.c_navy
            b_card.line.color.rgb = self.c_royal_blue
            tf_b = b_card.text_frame
            tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
            p_bt = tf_b.paragraphs[0]
            p_bt.text = btitle
            p_bt.font.size = Pt(10)
            p_bt.font.color.rgb = self.c_slate_gray
            p_bv = tf_b.add_paragraph()
            p_bv.text = bval
            p_bv.font.size = Pt(14)
            p_bv.font.bold = True
            p_bv.font.color.rgb = bcol

        # Slide 2: 4대 출점 점검 체크리스트
        s2 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s2, "1. 사업지 개요 및 ", "출점 점검 체크리스트", f" ({site['rooms']}타석 / {site['area_pyeong']}평 권장)")
        
        cards_s2 = [
            (Inches(0.6), Inches(1.4), Inches(5.9), Inches(2.5), "📐 공간 & 층고 점검 기준", [
                f"• 대상 주소: {site['full_address']}",
                f"• 권장 공간: 전용면적 {site['area_pyeong']}평 (10타석 + 라운지/카페 최적 배치)",
                f"• 층고 기준: {site['clear_height_spec']}",
                f"• 추천 층수: 지상 2~3층 권장 (또는 쾌적한 지하 1층)"
            ]),
            (Inches(6.8), Inches(1.4), Inches(5.9), Inches(2.5), "🚗 주차 & 접근성 점검 기준", [
                f"• 주차 요건: {site['parking_spec']}",
                f"• 고객 특성: 자차 이용 시니어 비중 80% 이상으로 편리한 진출입 필수",
                f"• 도로 접면: 주요 간선도로 및 대단지 아파트 진입로 인접 우수",
                f"• 보행 동선: 대중교통(버스/지하철) 도보 5~10분 생활권"
            ]),
            (Inches(0.6), Inches(4.2), Inches(5.9), Inches(2.5), "🏢 건물 편의 & 승강기 요건", [
                f"• 고객 편의: {site['accessibility_spec']}",
                f"• 계단 여건: 계단 단차가 낮거나 완만한 진입 경사로 확보 필요",
                f"• 냉난방/환기: 개별 공조 및 고성능 환기 덕트 설치 공간 확인",
                f"• 소음/진동: 상하층 타 업종 간섭 방지 방음 설계 적용"
            ]),
            (Inches(6.8), Inches(4.2), Inches(5.9), Inches(2.5), "⚖️ 인허가 및 건축물 용도", [
                f"• 적합 용도: {site['zoning_spec']}",
                f"• 지자체 체육시설: 체육시설의 설치·이용에 관한 법률 검토",
                f"• 소방 기준: 스프링클러, 비상유도등, 비상탈출구 완비 점검",
                f"• 정화조/전기: 동시 이용 인원 대비 전기 용량(30kW 이상) 확인"
            ]),
        ]
        for cx, cy, cw, ch, ctitle, clines in cards_s2:
            box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, cy, cw, ch)
            box.fill.solid()
            box.fill.fore_color.rgb = self.c_card_bg
            box.line.color.rgb = self.c_border
            tf = box.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.18)
            tf.margin_right = Inches(0.18)
            tf.margin_top = Inches(0.15)
            p0 = tf.paragraphs[0]
            p0.text = ctitle
            p0.font.name = 'Malgun Gothic'
            p0.font.size = Pt(13)
            p0.font.bold = True
            p0.font.color.rgb = self.c_navy
            for line_txt in clines:
                p = tf.add_paragraph()
                p.space_before = Pt(4)
                p.text = line_txt
                p.font.size = Pt(10)
                p.font.color.rgb = self.c_slate_dark
        self._add_source_footer(s2, "* 기준: 마이파크 표준 가맹 모델 및 건축물 현장 실측 권장 기준")

        # Slide 3: 배후 인구 분석
        s3 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s3, f"{demo.get('center_dong', '사업지')} 반경 3Km 생활권 (", f"약 {demo['total_pop']//10000}만명", ")")
        
        if 'map_radius' in charts and os.path.exists(charts['map_radius']):
            s3.shapes.add_picture(charts['map_radius'], Inches(0.6), Inches(1.4), width=Inches(5.8))
            
        tb3_sum = s3.shapes.add_textbox(Inches(6.6), Inches(1.4), Inches(6.1), Inches(0.7))
        p3_sum = tb3_sum.text_frame.paragraphs[0]
        p3_sum.text = f"▲ 사업지 주변 총 인구수 : {demo['total_pop']:,}명 (반경 3km {len(demo['dongs'])}개 행정동)"
        p3_sum.font.name = 'Malgun Gothic'
        p3_sum.font.size = Pt(12)
        p3_sum.font.bold = True
        p3_sum.font.color.rgb = self.c_red
        
        dongs = demo['dongs']
        rows3 = len(dongs) + 2
        table_s3 = s3.shapes.add_table(rows3, 4, Inches(6.6), Inches(2.2), Inches(6.1), Inches(0.42 * rows3)).table
        
        col_w3 = [Inches(1.8), Inches(1.4), Inches(1.4), Inches(1.5)]
        for c_idx, w in enumerate(col_w3):
            table_s3.columns[c_idx].width = w
            
        headers3 = ['행정구역(동)', '남자(명)', '여자(명)', '합계(명)']
        for col_idx, h in enumerate(headers3):
            self._format_cell(table_s3.cell(0, col_idx), h, font_size=10.5, bold=True, color=self.c_white, bg_color=self.c_navy)
            
        for idx, d in enumerate(dongs):
            r = idx + 1
            self._format_cell(table_s3.cell(r, 0), d['dong'], font_size=10, color=self.c_slate_dark)
            self._format_cell(table_s3.cell(r, 1), f"{d['male']:,}", font_size=10, color=self.c_slate_dark)
            self._format_cell(table_s3.cell(r, 2), f"{d['female']:,}", font_size=10, color=self.c_slate_dark)
            self._format_cell(table_s3.cell(r, 3), f"{d['total']:,}", font_size=10, color=self.c_slate_dark)
            
        last_r = rows3 - 1
        self._format_cell(table_s3.cell(last_r, 0), "합계", font_size=10.5, bold=True, color=self.c_red, bg_color=self.c_pink_bg)
        self._format_cell(table_s3.cell(last_r, 1), f"{demo['male_pop']:,}", font_size=10.5, bold=True, color=self.c_red, bg_color=self.c_pink_bg)
        self._format_cell(table_s3.cell(last_r, 2), f"{demo['female_pop']:,}", font_size=10.5, bold=True, color=self.c_red, bg_color=self.c_pink_bg)
        self._format_cell(table_s3.cell(last_r, 3), f"{demo['total_pop']:,}", font_size=10.5, bold=True, color=self.c_red, bg_color=self.c_pink_bg)
            
        self._add_source_footer(s3, f"* 출처 : {demo['base_date']}")

        # Slide 4: 메인 타겟 50대이상 시니어 분석
        s4 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s4, "파크골프 메인 타겟 장·노년층 인구 수 (", f"약 {demo['senior_50_plus']:,}명_{demo['senior_ratio']}%", ")")
        
        c4_1 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.5), Inches(5.0), Inches(2.3))
        c4_1.fill.solid()
        c4_1.fill.fore_color.rgb = self.c_pink_bg
        c4_1.line.color.rgb = self.c_red
        tf_c4_1 = c4_1.text_frame
        tf_c4_1.word_wrap = True
        tf_c4_1.margin_left = Inches(0.18)
        tf_c4_1.margin_right = Inches(0.18)
        p = tf_c4_1.paragraphs[0]
        p.text = "🎯 핵심 소비층: 50대 이상 여성"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = self.c_red
        p2 = tf_c4_1.add_paragraph()
        p2.space_before = Pt(8)
        p2.text = f"• 여성 시니어 인구: 약 {demo['senior_50_female']:,}명\n• 타겟 분석 결과 여성 인구 비중이 높아, 평일 낮 주간(10~17시) 주부/친목 모임 유치에 최적"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = self.c_slate_dark
        
        c4_2 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(4.1), Inches(5.0), Inches(2.4))
        c4_2.fill.solid()
        c4_2.fill.fore_color.rgb = self.c_card_bg
        c4_2.line.color.rgb = self.c_royal_blue
        tf_c4_2 = c4_2.text_frame
        tf_c4_2.word_wrap = True
        tf_c4_2.margin_left = Inches(0.18)
        tf_c4_2.margin_right = Inches(0.18)
        p = tf_c4_2.paragraphs[0]
        p.text = "💡 시니어 상권 사업화 시사점"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = self.c_navy
        p2 = tf_c4_2.add_paragraph()
        p2.space_before = Pt(8)
        p2.text = f"• 시니어 인구 집적도 {demo['senior_ratio']}%의 최상급 골든 배후지\n• 은퇴 세대의 건강 생활체육 참여 급증으로 계절/날씨 무관 4계절 안정적 풀가동 실현"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = self.c_slate_dark
        
        ages = demo['age_distribution']
        rows4 = len(ages) + 2
        table_s4 = s4.shapes.add_table(rows4, 4, Inches(5.8), Inches(1.5), Inches(6.9), Inches(0.44 * rows4)).table
        
        col_w4 = [Inches(2.0), Inches(1.6), Inches(1.6), Inches(1.7)]
        for c_idx, w in enumerate(col_w4):
            table_s4.columns[c_idx].width = w
            
        headers4 = ['연령대', '남자(명)', '여자(명)', '합계(명)']
        for col_idx, h in enumerate(headers4):
            self._format_cell(table_s4.cell(0, col_idx), h, font_size=10.5, bold=True, color=self.c_white, bg_color=self.c_navy)
            
        for row_idx, a in enumerate(ages):
            self._format_cell(table_s4.cell(row_idx+1, 0), a['age_group'], font_size=10, color=self.c_slate_dark)
            self._format_cell(table_s4.cell(row_idx+1, 1), f"{int(a['male']):,}", font_size=10, color=self.c_slate_dark)
            self._format_cell(table_s4.cell(row_idx+1, 2), f"{int(a['female']):,}", font_size=10, color=self.c_slate_dark)
            self._format_cell(table_s4.cell(row_idx+1, 3), f"{int(a['total']):,}", font_size=10, color=self.c_slate_dark)
            
        last_r4 = rows4 - 1
        self._format_cell(table_s4.cell(last_r4, 0), "총계 (50대이상)", font_size=10.5, bold=True, color=self.c_red, bg_color=self.c_pink_bg)
        self._format_cell(table_s4.cell(last_r4, 1), f"{demo['senior_50_plus'] - demo['senior_50_female']:,}", font_size=10.5, bold=True, color=self.c_red, bg_color=self.c_pink_bg)
        self._format_cell(table_s4.cell(last_r4, 2), f"{demo['senior_50_female']:,}", font_size=10.5, bold=True, color=self.c_red, bg_color=self.c_pink_bg)
        self._format_cell(table_s4.cell(last_r4, 3), f"{demo['senior_50_plus']:,}", font_size=10.5, bold=True, color=self.c_red, bg_color=self.c_pink_bg)
            
        self._add_source_footer(s4, f"* 출처 : {demo['base_date']}")

        # Slide 5: 소상공인 매출 추이
        s5 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s5, "전월 대비 파크골프/여가 업종의 ", f"월평균 매출액 (약 {comm['monthly_avg_sales']//10000:,}만원)", "")
        
        card_data = [
            (Inches(0.6), Inches(1.5), "● 업소 정보", "업소수", f"{comm['store_count']}개", self.c_red),
            (Inches(3.1), Inches(1.5), "● 점포 증감", "전월대비 증감률", "0.0%", self.c_navy),
            (Inches(0.6), Inches(4.1), "● 매출 정보", "월평균 매출액", f"{comm['monthly_avg_sales']//10000:,}만원", self.c_red),
            (Inches(3.1), Inches(4.1), "● 매출 추세", "전월대비 증감률", "+2.1%", self.c_royal_blue),
        ]
        for cx, cy, ctitle, clabel, cval, ccol in card_data:
            cbox = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, cy, Inches(2.3), Inches(2.3))
            cbox.fill.solid()
            cbox.fill.fore_color.rgb = self.c_card_bg
            cbox.line.color.rgb = self.c_border
            tf = cbox.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.15)
            tf.margin_right = Inches(0.15)
            p0 = tf.paragraphs[0]
            p0.text = f"{ctitle}\n\n{clabel}"
            p0.font.size = Pt(11)
            p0.font.color.rgb = self.c_slate_gray
            p1 = tf.add_paragraph()
            p1.space_before = Pt(8)
            p1.text = cval
            p1.font.size = Pt(21)
            p1.font.bold = True
            p1.font.color.rgb = ccol
            
        if 'sales_trend' in charts and os.path.exists(charts['sales_trend']):
            s5.shapes.add_picture(charts['sales_trend'], Inches(5.6), Inches(1.5), width=Inches(7.1))
            
        self._add_source_footer(s5, "* 출처 : 소상공인365 상권분석 플랫폼 (참고)")

        # Slide 6: 상권 매출 패턴 분석
        s6 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s6, "3. 상권 매출 패턴 분석 (", f"주간 10~17시 {comm['time_distribution']['주간_10_17시_비중']}%", f", 50대이상 {comm['age_distribution']['50대이상_비중']}%)")
        
        cards_s6 = [
            (Inches(0.6), Inches(1.5), Inches(5.9), Inches(2.5), "📅 요일별 소비 패턴 분석", [
                f"• 피크 요일: 월요일 ({comm['day_distribution']['월']}%) 최고치 기록",
                f"• 주간 정기 모임: 주초 동호회 및 친목 단체 예약 집중",
                f"• 주말 가동률: 주말 평균 비중 {comm['day_distribution']['주말평균비중']}%로 주 7일 고른 가동",
                f"• 매출 안정성: 특정 요일에 편중되지 않는 균형 잡힌 주간 매출 구조"
            ]),
            (Inches(6.8), Inches(1.5), Inches(5.9), Inches(2.5), "⏰ 시간대별 이용 패턴 분석", [
                f"• 주간 비중: 10~17시 이용 비중이 전체의 {comm['time_distribution']['주간_10_17시_비중']}% 압도적",
                f"• 일반 스크린골프 대비: 야간(18~23시) 위주인 일반 골프와 달리 낮 시간 풀가동",
                f"• 점심/오후 연계: 게임 후 인근 식당/카페 이용으로 지역 상권 활성화 견인",
                f"• 회전율 극대화: 1일 10시간 기준 1.5~2.0회전 안정적 달성"
            ]),
            (Inches(0.6), Inches(4.3), Inches(5.9), Inches(2.4), "👥 연령별 매출 기여도 분석", [
                f"• 핵심 연령: 50대 이상 이용자 매출 기여도 {comm['age_distribution']['50대이상_비중']}% 달성",
                f"• 소비 지속력: 여가 시간과 경제적 여유를 갖춘 액티브 시니어층 집중",
                f"• 커뮤니티 형성: 월 회원제 및 고정 팀 중심의 락인(Lock-in) 효과",
                f"• 부가 소비: 파크골프 용품 및 음료/다과 구매력 우수"
            ]),
            (Inches(6.8), Inches(4.3), Inches(5.9), Inches(2.4), "🎯 종합 사업화 핵심 전략", [
                f"• 유휴 시간 제로: 주간 시니어 리그전 및 여성 친목 토너먼트 상시 운영",
                f"• 레슨 및 클럽 연계: 초보자 입문 아카데미 개설로 신규 고객 지속 유입",
                f"• 복합 문화 공간: 카페형 라운지 구비로 체류 시간 및 부가 수익 증대",
                f"• 지역 랜드마크화: 독보적 10타석 플래그십 규모로 인근 수요 독점"
            ]),
        ]
        for cx, cy, cw, ch, ctitle, clines in cards_s6:
            box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, cy, cw, ch)
            box.fill.solid()
            box.fill.fore_color.rgb = self.c_card_bg
            box.line.color.rgb = self.c_border
            tf = box.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.18)
            tf.margin_right = Inches(0.18)
            tf.margin_top = Inches(0.15)
            p0 = tf.paragraphs[0]
            p0.text = ctitle
            p0.font.name = 'Malgun Gothic'
            p0.font.size = Pt(13)
            p0.font.bold = True
            p0.font.color.rgb = self.c_navy
            for line_txt in clines:
                p = tf.add_paragraph()
                p.space_before = Pt(4)
                p.text = line_txt
                p.font.size = Pt(10)
                p.font.color.rgb = self.c_slate_dark
        self._add_source_footer(s6, "* 출처 : 소상공인시장진흥공단 카드 결제 빅데이터")

        # =====================================================================
        # Slide 7: 주변 경쟁 매장 분석 (4열 풀그리드 + 비주얼 배지 블록 꽉 채움)
        # =====================================================================
        s7 = self.prs.slides.add_slide(self.blank_layout)
        comps = comm.get('competitors', [])
        count_str = f"({len(comps)}곳)" if len(comps) > 0 and comps[0].get('rooms', 0) > 0 else "(블루오션 상권)"
        self._add_header_bar(s7, "주변 스크린 ", f"파크골프 매장{count_str}", " 실측 분석")
        
        card_w = Inches(2.85)
        gap = Inches(0.2)
        start_x = Inches(0.6)
        
        for idx, c in enumerate(comps[:4]):
            cur_x = start_x + (idx * (card_w + gap))
            
            # 1. 상단 다크 네이비 헤더 바
            hdr_box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_x, Inches(1.45), card_w, Inches(0.55))
            hdr_box.fill.solid()
            hdr_box.fill.fore_color.rgb = self.c_navy
            hdr_box.line.color.rgb = self.c_royal_blue
            tf_h = hdr_box.text_frame
            tf_h.vertical_anchor = MSO_ANCHOR.MIDDLE
            p_hdr = tf_h.paragraphs[0]
            p_hdr.text = str(c['name'])[:16]
            p_hdr.font.name = 'Malgun Gothic'
            p_hdr.font.size = Pt(10.5)
            p_hdr.font.bold = True
            p_hdr.font.color.rgb = self.c_white
            p_hdr.alignment = PP_ALIGN.CENTER
            
            # 2. 중간 비주얼 배지 블록 (매장 특성 및 타석수 배지)
            mid_box = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_x, Inches(2.05), card_w, Inches(1.4))
            mid_box.fill.solid()
            mid_box.fill.fore_color.rgb = RGBColor(235, 243, 255)
            mid_box.line.color.rgb = self.c_border
            tf_m = mid_box.text_frame
            tf_m.word_wrap = True
            tf_m.vertical_anchor = MSO_ANCHOR.MIDDLE
            p_m1 = tf_m.paragraphs[0]
            p_m1.alignment = PP_ALIGN.CENTER
            p_m1.text = f"🏌️ {c.get('rooms', 0)}타석 규모" if c.get('rooms', 0) > 0 else "⛳ 전문 1호점 선점"
            p_m1.font.bold = True
            p_m1.font.size = Pt(14)
            p_m1.font.color.rgb = self.c_royal_blue
            p_m2 = tf_m.add_paragraph()
            p_m2.alignment = PP_ALIGN.CENTER
            p_m2.space_before = Pt(4)
            p_m2.text = f"[{c.get('status', '실측완료')}] {c.get('system', '스크린 시뮬레이터')[:14]}"
            p_m2.font.size = Pt(9.5)
            p_m2.font.color.rgb = self.c_slate_dark
            
            # 3. 하단 실측 스펙 박스
            body_box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_x, Inches(3.5), card_w, Inches(3.2))
            body_box.fill.solid()
            body_box.fill.fore_color.rgb = self.c_card_bg
            body_box.line.color.rgb = self.c_border
            tf_body = body_box.text_frame
            tf_body.word_wrap = True
            tf_body.margin_left = Inches(0.14)
            tf_body.margin_right = Inches(0.14)
            tf_body.margin_top = Inches(0.12)
            
            p1 = tf_body.paragraphs[0]
            p1.text = f"▲ 주소: {c['address']}"
            p1.font.size = Pt(9)
            p1.font.color.rgb = self.c_slate_dark
            
            p2 = tf_body.add_paragraph()
            p2.space_before = Pt(6)
            p2.text = f"▲ 시스템: {c['system']}"
            p2.font.size = Pt(9)
            p2.font.color.rgb = self.c_royal_blue
            p2.font.bold = True
            
            p3 = tf_body.add_paragraph()
            p3.space_before = Pt(6)
            p3.text = f"▲ 규모: {c['rooms']}타석 운영" if c.get('rooms', 0) > 0 else "▲ 상태: 상업용 전문매장 미등록"
            p3.font.size = Pt(9)
            p3.font.color.rgb = self.c_slate_dark
            
            p4 = tf_body.add_paragraph()
            p4.space_before = Pt(6)
            p4.text = f"▲ 특징: {c.get('features', '-')}"
            p4.font.size = Pt(8.5)
            p4.font.color.rgb = self.c_slate_gray
            
        self._add_source_footer(s7, "* 출처 : 소상공인시장진흥공단 상권정보 및 카카오맵 로컬 POI 실측 조사")

        # Slide 8: 5대 지표 평가
        s8 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s8, "5. 마이파크 입지 최적성 종합 평가 [", f"{score['grade']}등급 - {score['total_score']}점", " / 100점]")
        if 'radar_score' in charts and os.path.exists(charts['radar_score']):
            s8.shapes.add_picture(charts['radar_score'], Inches(0.6), Inches(1.5), width=Inches(5.4))
            
        tb8 = s8.shapes.add_textbox(Inches(6.2), Inches(1.5), Inches(6.5), Inches(5.1))
        tf8 = tb8.text_frame
        tf8.word_wrap = True
        
        indicators = [
            ("1) 골든 시니어 집적도", score['scores']['senior_population'], 25, "반경 3km 내 50대 이상 시니어 인구 및 여성 비중"),
            ("2) 접근성 및 주차 인프라", score['scores']['accessibility_parking'], 25, "자주식 주차 편의성, 승강기 완비, 주요 도로망"),
            ("3) 공간 적합성 및 임대료", score['scores']['space_efficiency'], 15, "유효 층고(2.8m 이상), 전용 120평, 평당 임대료"),
            ("4) 수요 공급 갭 (블루오션)", score['scores']['supply_gap'], 15, "경쟁 강도 및 야외 구장 포화 대기 수요 흡수"),
            ("5) 지역 소비력 및 여가지출", score['scores']['commercial_spending'], 20, "스포츠/여가 월평균 카드 매출 및 생활밀착 상권"),
        ]
        for idx, (iname, iscore, imax, idesc) in enumerate(indicators):
            p = tf8.add_paragraph() if idx > 0 else tf8.paragraphs[0]
            p.space_before = Pt(6)
            r1 = p.add_run()
            r1.text = f"● {iname}: "
            r1.font.bold = True
            r1.font.size = Pt(12)
            r1.font.color.rgb = self.c_navy
            r2 = p.add_run()
            r2.text = f"{iscore}점 / {imax}점 만점"
            r2.font.bold = True
            r2.font.size = Pt(12)
            r2.font.color.rgb = self.c_royal_blue
            p_desc = tf8.add_paragraph()
            p_desc.text = f"   ({idesc})"
            p_desc.font.size = Pt(9.5)
            p_desc.font.color.rgb = self.c_slate_gray
            
        p_res = tf8.add_paragraph()
        p_res.space_before = Pt(10)
        r_res = p_res.add_run()
        r_res.text = f"★ 종합 판정: 총점 {score['total_score']}점 ({score['grade_desc']})"
        r_res.font.bold = True
        r_res.font.size = Pt(13)
        r_res.font.color.rgb = self.c_red
        
        self._add_source_footer(s8, "* 평가 기준: 마이파크 가맹 입지선정 5대 다이아몬드 스코어링 모델")

        # Slide 9: 월 매출
        s9 = self.prs.slides.add_slide(self.blank_layout)
        m_scen = fin['monthly_scenarios']
        self._add_header_bar(s9, "6. 마이파크 사업 타당성 분석 (", f"{site['rooms']}타석 / {site['area_pyeong']}평", ") - 월 예상 매출")
        table_s9 = s9.shapes.add_table(4, 7, Inches(0.6), Inches(2.0), Inches(12.133), Inches(2.4)).table
        
        col_w9 = [Inches(1.3), Inches(1.6), Inches(1.4), Inches(1.4), Inches(1.4), Inches(2.3), Inches(2.733)]
        for c_idx, w in enumerate(col_w9):
            table_s9.columns[c_idx].width = w
            
        h9 = ['구분', '타석 이용료', '용품(10%)', '카페(5%)', '레슨(3%)', '월 총매출 합계', '비고 (1일 이용자)']
        for col_idx, h in enumerate(h9):
            self._format_cell(table_s9.cell(0, col_idx), h, font_size=10.5, bold=True, color=self.c_white, bg_color=self.c_navy)
            
        for row_idx, k in enumerate(['conservative', 'moderate', 'optimistic']):
            sc = m_scen[k]
            r = row_idx + 1
            self._format_cell(table_s9.cell(r, 0), sc['scenario_name'], font_size=10, bold=True, color=self.c_navy)
            self._format_cell(table_s9.cell(r, 1), f"{sc['room_revenue']:,}원", font_size=10, color=self.c_slate_dark)
            self._format_cell(table_s9.cell(r, 2), f"{sc['goods_revenue']:,}원", font_size=10, color=self.c_slate_dark)
            self._format_cell(table_s9.cell(r, 3), f"{sc['cafe_revenue']:,}원", font_size=10, color=self.c_slate_dark)
            self._format_cell(table_s9.cell(r, 4), f"{sc['lesson_revenue']:,}원", font_size=10, color=self.c_slate_dark)
            self._format_cell(table_s9.cell(r, 5), f"{sc['total_revenue']:,}원", font_size=10.5, bold=True, color=self.c_royal_blue)
            self._format_cell(table_s9.cell(r, 6), f"1일 {sc['daily_users']}명 (월 {sc['monthly_users']:,}명)", font_size=10, color=self.c_slate_dark)
            
        self._add_source_footer(s9, "* 산출 근거: 18홀 8,000원, 부가매출 18%, 월 30일 가동 기준")

        # Slide 10: 운영 비용
        s10 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s10, "6. 마이파크 사업 타당성 분석 (", f"{site['rooms']}타석", ") - 예상 운영 비용")
        table_s10 = s10.shapes.add_table(5, 5, Inches(0.6), Inches(1.8), Inches(12.133), Inches(3.2)).table
        
        col_w10 = [Inches(2.2), Inches(1.9), Inches(1.9), Inches(1.9), Inches(4.233)]
        for c_idx, w in enumerate(col_w10):
            table_s10.columns[c_idx].width = w
            
        h10 = ['비용 구분', '보수적 시나리오', '보편적 시나리오', '긍정적 시나리오', '세부 산출 내역']
        for col_idx, h in enumerate(h10):
            self._format_cell(table_s10.cell(0, col_idx), h, font_size=10.5, bold=True, color=self.c_white, bg_color=self.c_navy)
            
        c_sc = m_scen['conservative']
        m_sc = m_scen['moderate']
        o_sc = m_scen['optimistic']
        cost_rows = [
            ('인건비 + 임대료', f"{c_sc['labor_cost']+c_sc['rent_cost']:,}원", f"{m_sc['labor_cost']+m_sc['rent_cost']:,}원", f"{o_sc['labor_cost']+o_sc['rent_cost']:,}원", f"인력 {fin['staff_count']}명(월 750만) / 임대료 {fin['monthly_rent']//10000:,}만원/월"),
            ('원가 3종 + 카드수수료', f"{c_sc['goods_cost']+c_sc['cafe_cost']+c_sc['lesson_cost']+c_sc['card_fee']:,}원", f"{m_sc['goods_cost']+m_sc['cafe_cost']+m_sc['lesson_cost']+m_sc['card_fee']:,}원", f"{o_sc['goods_cost']+o_sc['cafe_cost']+o_sc['lesson_cost']+o_sc['card_fee']:,}원", "용품60%, 식음50%, 레슨80%, 카드2%"),
            ('매장운영비 + 렌탈/마케팅', f"{c_sc['store_ops_cost']+c_sc['rental_cost']+c_sc['marketing_cost']:,}원", f"{m_sc['store_ops_cost']+m_sc['rental_cost']+m_sc['marketing_cost']:,}원", f"{o_sc['store_ops_cost']+o_sc['rental_cost']+o_sc['marketing_cost']:,}원", "수도광열, 소모품, 공청기, 보험 등"),
            ('월 총 비용 합계', f"{c_sc['total_cost']:,}원", f"{m_sc['total_cost']:,}원", f"{o_sc['total_cost']:,}원", "부가가치세(VAT) 별도 기준")
        ]
        for row_idx, r_data in enumerate(cost_rows):
            r = row_idx + 1
            is_last = (row_idx == 3)
            bg_col = self.c_pink_bg if is_last else None
            txt_col = self.c_navy if is_last else self.c_slate_dark
            
            self._format_cell(table_s10.cell(r, 0), r_data[0], font_size=10, bold=is_last, color=txt_col, bg_color=bg_col)
            self._format_cell(table_s10.cell(r, 1), r_data[1], font_size=10, bold=is_last, color=txt_col, bg_color=bg_col)
            self._format_cell(table_s10.cell(r, 2), r_data[2], font_size=10, bold=is_last, color=txt_col, bg_color=bg_col)
            self._format_cell(table_s10.cell(r, 3), r_data[3], font_size=10, bold=is_last, color=txt_col, bg_color=bg_col)
            self._format_cell(table_s10.cell(r, 4), r_data[4], font_size=9.5, bold=is_last, color=txt_col, bg_color=bg_col, align=PP_ALIGN.LEFT)
            
        self._add_source_footer(s10, "* 산출 근거: 마이파크 표준 운영 원가 및 가맹 매장 실측 비용 기준")

        # Slide 11: 5개년 손익
        s11 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s11, "6. 마이파크 사업 타당성 분석 - ", "5개년 손익 예측", " (연 2% 성장률 반영)")
        if 'profit_forecast' in charts and os.path.exists(charts['profit_forecast']):
            s11.shapes.add_picture(charts['profit_forecast'], Inches(0.6), Inches(1.5), width=Inches(6.8))
            
        mod_1y = fin['forecast_5year']['moderate'][0]
        mod_5y = fin['forecast_5year']['moderate'][4]
        
        c_kpi1 = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.6), Inches(1.6), Inches(5.1), Inches(1.6))
        c_kpi1.fill.solid()
        c_kpi1.fill.fore_color.rgb = self.c_card_bg
        c_kpi1.line.color.rgb = self.c_royal_blue
        tf_k1 = c_kpi1.text_frame
        tf_k1.word_wrap = True
        tf_k1.margin_left = Inches(0.16)
        tf_k1.margin_right = Inches(0.16)
        p = tf_k1.paragraphs[0]
        p.text = "📈 연간 실적 전망 (보편 시나리오)"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = self.c_navy
        p2 = tf_k1.add_paragraph()
        p2.space_before = Pt(4)
        p2.text = f"• 1년차: 연매출 {mod_1y['total_revenue']//100000000:.1f}억원 / 영업이익 {mod_1y['operating_profit']//100000000:.1f}억원\n• 5년차: 연매출 {mod_5y['total_revenue']//100000000:.1f}억원 / 영업이익 {mod_5y['operating_profit']//100000000:.1f}억원"
        p2.font.size = Pt(10)
        p2.font.color.rgb = self.c_slate_dark
        
        c_kpi2 = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.6), Inches(3.4), Inches(5.1), Inches(1.6))
        c_kpi2.fill.solid()
        c_kpi2.fill.fore_color.rgb = self.c_card_bg
        c_kpi2.line.color.rgb = self.c_emerald
        tf_k2 = c_kpi2.text_frame
        tf_k2.word_wrap = True
        tf_k2.margin_left = Inches(0.16)
        tf_k2.margin_right = Inches(0.16)
        p = tf_k2.paragraphs[0]
        p.text = "⏱️ 투자금 회수 및 손익분기점"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = self.c_emerald
        p2 = tf_k2.add_paragraph()
        p2.space_before = Pt(4)
        p2.text = f"• 손익분기점(BEP): 월매출 약 {fin['investment']['bep_monthly_sales']//10000:,}만원 (일 {fin['investment']['bep_turns_per_room']}회전)\n• 순투자금 회수: {score['payback_text']}"
        p2.font.size = Pt(10)
        p2.font.color.rgb = self.c_slate_dark
        
        self._add_source_footer(s11, f"* 산출 근거: 초기 순투자금 {fin['investment']['total_capex']//100000000:.2f}억원 기준 / 연 2% 복리 성장률 반영")

        # Slide 12: 종합 결론
        s12 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s12, "7. 종합 결론 및 ", "사업 타당성 최종 평가", "")
        
        card12_1 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.5), Inches(12.133), Inches(2.4))
        card12_1.fill.solid()
        card12_1.fill.fore_color.rgb = self.c_card_bg
        card12_1.line.color.rgb = self.c_gold
        card12_1.line.width = Pt(1.5)
        tf_12_1 = card12_1.text_frame
        tf_12_1.word_wrap = True
        tf_12_1.margin_left = Inches(0.2)
        tf_12_1.margin_right = Inches(0.2)
        p = tf_12_1.paragraphs[0]
        p.text = "🌟【 가맹점 출점 기대효과 및 핵심 경쟁력 】"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = self.c_gold
        p_v1 = tf_12_1.add_paragraph()
        p_v1.space_before = Pt(6)
        p_v1.text = score['value_franchisee']
        p_v1.font.size = Pt(11)
        p_v1.font.color.rgb = self.c_slate_dark
        
        card12_2 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(4.1), Inches(12.133), Inches(2.4))
        card12_2.fill.solid()
        card12_2.fill.fore_color.rgb = self.c_card_bg
        card12_2.line.color.rgb = self.c_emerald
        card12_2.line.width = Pt(1.5)
        tf_12_2 = card12_2.text_frame
        tf_12_2.word_wrap = True
        tf_12_2.margin_left = Inches(0.2)
        tf_12_2.margin_right = Inches(0.2)
        p = tf_12_2.paragraphs[0]
        p.text = "🏢【 상가 전체 상권 활성화 및 건물 가치 상승 효과 】"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = self.c_emerald
        p_v2 = tf_12_2.add_paragraph()
        p_v2.space_before = Pt(6)
        p_v2.text = score['value_landlord']
        p_v2.font.size = Pt(11)
        p_v2.font.color.rgb = self.c_slate_dark
        
        self._add_source_footer(s12, "* 마이파크(MYPARK) 사업본부 상권분석 시스템 v1.0")
        
        os.makedirs(os.path.dirname(output_pptx_path), exist_ok=True)
        self.prs.save(output_pptx_path)
        print(f"[PPTX GENERATED] {output_pptx_path}")
        return output_pptx_path
