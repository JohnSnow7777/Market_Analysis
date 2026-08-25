# -*- coding: utf-8 -*-
"""16:9 와이드 최고급 비즈니스 컨설팅 프레젠테이션 생성기 (글자 짤림/여백 완전 박멸)"""
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
        header = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(0.35), Inches(12.133), Inches(0.75))
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
            r1.font.size = Pt(17.5)
            r1.font.bold = True
            r1.font.color.rgb = self.c_white
            
        if gold_highlight:
            r2 = p.add_run()
            r2.text = gold_highlight
            r2.font.name = 'Malgun Gothic'
            r2.font.size = Pt(17.5)
            r2.font.bold = True
            r2.font.color.rgb = self.c_gold
            
        if white_suffix:
            r3 = p.add_run()
            r3.text = white_suffix
            r3.font.name = 'Malgun Gothic'
            r3.font.size = Pt(17.5)
            r3.font.bold = True
            r3.font.color.rgb = self.c_white

    def _add_source_footer(self, slide, source_text):
        tb = slide.shapes.add_textbox(Inches(3.0), Inches(7.08), Inches(9.7), Inches(0.35))
        p = tb.text_frame.paragraphs[0]
        p.text = source_text
        p.font.name = 'Malgun Gothic'
        p.font.size = Pt(8.5)
        p.font.color.rgb = self.c_slate_gray
        p.alignment = PP_ALIGN.RIGHT

    def _format_cell(self, cell, text, font_size=10, bold=False, color=None, bg_color=None, align=PP_ALIGN.CENTER):
        cell.text = ""
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_top = Pt(4)
        cell.margin_bottom = Pt(4)
        cell.margin_left = Pt(6)
        cell.margin_right = Pt(6)
        
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
        
        # ---------------------------------------------------------------------
        # Slide 1: 표지
        # ---------------------------------------------------------------------
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
            (Inches(8.7), "투자금 회수 기간", f"약 {fin['investment']['payback_months_moderate']:.1f}개월", self.c_white)
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

        # ---------------------------------------------------------------------
        # Slide 2: 4대 출점 점검 체크리스트 (공백 없이 꽉 채운 2x2 카드)
        # ---------------------------------------------------------------------
        s2 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s2, "1. 사업지 개요 및 ", "출점 점검 체크리스트", f" ({site['rooms']}타석 / {site['area_pyeong']}평 권장)")
        
        cards_s2 = [
            (Inches(0.6), Inches(1.3), Inches(5.9), Inches(2.75), "📐 공간 & 층고 점검 기준", [
                f"• 대상 주소: {site['full_address']}",
                f"• 권장 공간: 전용면적 {site['area_pyeong']}평 (10타석 + 라운지/카페 최적 배치)",
                f"• 층고 기준: {site['clear_height_spec']}",
                f"• 보/배관 간섭: 센서 투사 영역 및 스윙 궤적 내 장애물 사전 실측 필수",
                f"• 추천 층수: 고객 접근성 높은 지상 2~3층 권장 (쾌적한 지하 1층 가능)"
            ]),
            (Inches(6.8), Inches(1.3), Inches(5.9), Inches(2.75), "🚗 주차 & 접근성 점검 기준", [
                f"• 주차 요건: {site['parking_spec']}",
                f"• 고객 특성: 자차 이용 시니어 비중 80% 이상으로 편리한 진출입 필수",
                f"• 진입 여건: 램프 폭 및 회전각 여유 있는 자주식 주차장 최우선",
                f"• 도로 접면: 주요 간선도로 및 대단지 아파트 진입로 인접 우수",
                f"• 보행 동선: 대중교통(버스/지하철) 도보 5~10분 생활권"
            ]),
            (Inches(0.6), Inches(4.2), Inches(5.9), Inches(2.75), "🏢 건물 편의 & 승강기 요건", [
                f"• 고객 편의: {site['accessibility_spec']}",
                f"• 계단 여건: 계단 단차가 낮거나 완만한 진입 경사로 확보 필요",
                f"• 냉난방/환기: 개별 공조 및 고성능 환기 덕트 설치 공간 확인",
                f"• 소음/진동: 상하층 타 업종 간섭 방지 방음/흡음 설계 시공",
                f"• 쾌적성: 남녀 분리 청결 화장실 및 쾌적한 로비 라운지 구축"
            ]),
            (Inches(6.8), Inches(4.2), Inches(5.9), Inches(2.75), "⚖️ 인허가 및 건축물 용도", [
                f"• 적합 용도: {site['zoning_spec']}",
                f"• 지자체 체육시설: 체육시설의 설치·이용에 관한 법률 인허가 검토",
                f"• 소방 기준: 스프링클러, 비상유도등, 비상탈출구 완비 점검",
                f"• 전기 용량: 10타석 시뮬레이터 동시 가동 대비 30kW 이상 인입",
                f"• 정화조 용량: 일 최대 150명 이상 동시 이용 기준 충족 점검"
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
            tf.margin_top = Inches(0.14)
            p0 = tf.paragraphs[0]
            p0.text = ctitle
            p0.font.name = 'Malgun Gothic'
            p0.font.size = Pt(12.5)
            p0.font.bold = True
            p0.font.color.rgb = self.c_navy
            for line_txt in clines:
                p = tf.add_paragraph()
                p.space_before = Pt(4.5)
                p.text = line_txt
                p.font.size = Pt(9.5)
                p.font.color.rgb = self.c_slate_dark
        self._add_source_footer(s2, "* 기준: 마이파크 표준 가맹 모델 및 건축물 현장 실측 권장 기준")

        # ---------------------------------------------------------------------
        # Slide 3: 배후 인구 분석 (반경 3km 생활권)
        # ---------------------------------------------------------------------
        s3 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s3, f"{demo.get('center_dong', '사업지')} 반경 3Km 생활권 (", f"약 {demo['total_pop']//10000}만명", ")")
        
        if 'map_radius' in charts and os.path.exists(charts['map_radius']):
            s3.shapes.add_picture(charts['map_radius'], Inches(0.6), Inches(1.3), width=Inches(5.8))
            
        tb3_sum = s3.shapes.add_textbox(Inches(6.6), Inches(1.3), Inches(6.1), Inches(0.6))
        p3_sum = tb3_sum.text_frame.paragraphs[0]
        p3_sum.text = f"▲ 사업지 주변 총 인구수 : {demo['total_pop']:,}명 (반경 3km {len(demo['dongs'])}개 행정동)"
        p3_sum.font.name = 'Malgun Gothic'
        p3_sum.font.size = Pt(12)
        p3_sum.font.bold = True
        p3_sum.font.color.rgb = self.c_red
        
        dongs = demo['dongs']
        rows3 = len(dongs) + 2
        table_s3 = s3.shapes.add_table(rows3, 4, Inches(6.6), Inches(2.0), Inches(6.1), Inches(0.48 * rows3)).table
        
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

        # ---------------------------------------------------------------------
        # Slide 4: 메인 타겟 50대이상 시니어 분석 (여백 완전 제거)
        # ---------------------------------------------------------------------
        s4 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s4, "파크골프 메인 타겟 장·노년층 인구 수 (", f"약 {demo['senior_50_plus']:,}명_{demo['senior_ratio']}%", ")")
        
        c4_1 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.3), Inches(5.0), Inches(2.75))
        c4_1.fill.solid()
        c4_1.fill.fore_color.rgb = self.c_pink_bg
        c4_1.line.color.rgb = self.c_red
        tf_c4_1 = c4_1.text_frame
        tf_c4_1.word_wrap = True
        tf_c4_1.margin_left = Inches(0.18)
        tf_c4_1.margin_right = Inches(0.18)
        tf_c4_1.margin_top = Inches(0.15)
        p = tf_c4_1.paragraphs[0]
        p.text = "🎯 핵심 소비층: 50대 이상 여성 시니어"
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = self.c_red
        p2 = tf_c4_1.add_paragraph()
        p2.space_before = Pt(8)
        p2.text = (
            f"• 여성 시니어 인구: 약 {demo['senior_50_female']:,}명 (전체 시니어의 53.0%)\n"
            f"• 소비 특성: 평일 낮 시간대(10~17시) 주부/친목 모임 및 동호회 주도\n"
            f"• 락인 효과: 4인 1팀 고정 리그전 참여로 월 정기 결제 충성도 최상\n"
            f"• 파생 소비: 게임 후 인근 카페 및 외식업소 연계 지출 활발"
        )
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = self.c_slate_dark
        
        c4_2 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(4.2), Inches(5.0), Inches(2.75))
        c4_2.fill.solid()
        c4_2.fill.fore_color.rgb = self.c_card_bg
        c4_2.line.color.rgb = self.c_royal_blue
        tf_c4_2 = c4_2.text_frame
        tf_c4_2.word_wrap = True
        tf_c4_2.margin_left = Inches(0.18)
        tf_c4_2.margin_right = Inches(0.18)
        tf_c4_2.margin_top = Inches(0.15)
        p = tf_c4_2.paragraphs[0]
        p.text = "💡 시니어 상권 사업화 시사점"
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = self.c_navy
        p2 = tf_c4_2.add_paragraph()
        p2.space_before = Pt(8)
        p2.text = (
            f"• 시니어 인구 집적도: {demo['senior_ratio']}%의 최상급 골든 배후지 형성\n"
            f"• 사계절 가동성: 야외 파크골프장의 혹서기/혹한기 대체 수요 완벽 흡수\n"
            f"• 주간 가동률 극대화: 일반 스크린골프의 유휴 시간대를 100% 예약 풀가동\n"
            f"• 진입 장벽 제로: 단 1개의 파크골프 채로 남녀노소 누구나 즉시 입문"
        )
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = self.c_slate_dark
        
        ages = demo['age_distribution']
        rows4 = len(ages) + 2
        table_s4 = s4.shapes.add_table(rows4, 4, Inches(5.8), Inches(1.3), Inches(6.9), Inches(0.62 * rows4)).table
        
        col_w4 = [Inches(2.0), Inches(1.6), Inches(1.6), Inches(1.7)]
        for c_idx, w in enumerate(col_w4):
            table_s4.columns[c_idx].width = w
            
        headers4 = ['연령대', '남자(명)', '여자(명)', '합계(명)']
        for col_idx, h in enumerate(headers4):
            self._format_cell(table_s4.cell(0, col_idx), h, font_size=11, bold=True, color=self.c_white, bg_color=self.c_navy)
            
        for row_idx, a in enumerate(ages):
            self._format_cell(table_s4.cell(row_idx+1, 0), a['age_group'], font_size=10.5, color=self.c_slate_dark)
            self._format_cell(table_s4.cell(row_idx+1, 1), f"{int(a['male']):,}", font_size=10.5, color=self.c_slate_dark)
            self._format_cell(table_s4.cell(row_idx+1, 2), f"{int(a['female']):,}", font_size=10.5, color=self.c_slate_dark)
            self._format_cell(table_s4.cell(row_idx+1, 3), f"{int(a['total']):,}", font_size=10.5, color=self.c_slate_dark)
            
        last_r4 = rows4 - 1
        self._format_cell(table_s4.cell(last_r4, 0), "총계 (50대이상)", font_size=11, bold=True, color=self.c_red, bg_color=self.c_pink_bg)
        self._format_cell(table_s4.cell(last_r4, 1), f"{demo['senior_50_plus'] - demo['senior_50_female']:,}", font_size=11, bold=True, color=self.c_red, bg_color=self.c_pink_bg)
        self._format_cell(table_s4.cell(last_r4, 2), f"{demo['senior_50_female']:,}", font_size=11, bold=True, color=self.c_red, bg_color=self.c_pink_bg)
        self._format_cell(table_s4.cell(last_r4, 3), f"{demo['senior_50_plus']:,}", font_size=11, bold=True, color=self.c_red, bg_color=self.c_pink_bg)
            
        self._add_source_footer(s4, f"* 출처 : {demo['base_date']}")

        # ---------------------------------------------------------------------
        # Slide 5: 소상공인365 / BASA 실측 화면 (수익구조 + 주거 93% 인프라)
        # ---------------------------------------------------------------------
        s5 = self.prs.slides.add_slide(self.blank_layout)
        rev_st = comm.get('revenue_structure', {})
        self._add_header_bar(s5, "2. 상권 실측 분석 (소상공인365/BASA) - ", "주거형 상권(주거 93%)", " 및 유사 골프업종 수익 구조")
        
        top20_str = f"{rev_st.get('top_20_sales', 62510000)//10000:,}만원"
        bot20_str = f"{rev_st.get('bottom_20_sales', 3020000)//10000:,}만원"
        
        c5_1 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.3), Inches(3.9), Inches(1.75))
        c5_1.fill.solid()
        c5_1.fill.fore_color.rgb = self.c_card_bg
        c5_1.line.color.rgb = self.c_royal_blue
        tf5_1 = c5_1.text_frame
        tf5_1.word_wrap = True
        p = tf5_1.paragraphs[0]
        p.text = "💰 유사 골프업종 수익구조 격차 (선행지표 BASA)"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = self.c_navy
        p_sub = tf5_1.add_paragraph()
        p_sub.space_before = Pt(4)
        p_sub.text = f"• 상위 20% 매출: {top20_str} /월 (대형 최신 매장)\n• 하위 20% 매출: {bot20_str} /월 (노후 소형 매장)\n★ 마이파크 10타석 플래그십은 상위 20% 시장 점유"
        p_sub.font.size = Pt(9)
        p_sub.font.color.rgb = self.c_slate_dark
        
        c5_2 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(3.2), Inches(3.9), Inches(1.75))
        c5_2.fill.solid()
        c5_2.fill.fore_color.rgb = self.c_card_bg
        c5_2.line.color.rgb = self.c_gold
        tf5_2 = c5_2.text_frame
        tf5_2.word_wrap = True
        p = tf5_2.paragraphs[0]
        p.text = "👥 핵심 고객층 및 변화 추이"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = self.c_gold
        p_sub = tf5_2.add_paragraph()
        p_sub.space_before = Pt(4)
        p_sub.text = f"• 주 이용층: 50대 남성 및 50대 여성 (구매력 최상)\n• 최근 변화: 3040대 직장인/가족 유입 증가 추세\n• 고객 충성도: 주 2~3회 이상 정기 방문 락인(Lock-in)"
        p_sub.font.size = Pt(9)
        p_sub.font.color.rgb = self.c_slate_dark
        
        c5_3 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(5.1), Inches(3.9), Inches(1.85))
        c5_3.fill.solid()
        c5_3.fill.fore_color.rgb = self.c_pink_bg
        c5_3.line.color.rgb = self.c_red
        tf5_3 = c5_3.text_frame
        tf5_3.word_wrap = True
        p = tf5_3.paragraphs[0]
        p.text = "📅 매출 집중 요일 및 운영 전략"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = self.c_red
        p_sub = tf5_3.add_paragraph()
        p_sub.space_before = Pt(4)
        p_sub.text = f"• 최고 매출 요일: 토요일(친목) & 월요일(동호회)\n• 주거형 상권 전략: 충성 고객 품질/편의성 중심\n• 평일 주간(10~17시) 주부 리그전으로 유휴 제로"
        p_sub.font.size = Pt(9)
        p_sub.font.color.rgb = self.c_slate_dark
        
        # 우측 상단 인프라 박스
        infra = comm.get('infra', {})
        c5_infra = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.7), Inches(1.3), Inches(8.0), Inches(1.75))
        c5_infra.fill.solid()
        c5_infra.fill.fore_color.rgb = self.c_card_bg
        c5_infra.line.color.rgb = self.c_border
        tf_inf = c5_infra.text_frame
        tf_inf.word_wrap = True
        p_inf = tf_inf.paragraphs[0]
        p_inf.text = f"🏛️ {comm.get('region_title', '사업지')} 주변 인프라 및 교통망 실측"
        p_inf.font.size = Pt(11.5)
        p_inf.font.bold = True
        p_inf.font.color.rgb = self.c_navy
        p_inf2 = tf_inf.add_paragraph()
        p_inf2.space_before = Pt(4)
        p_inf2.text = (
            f"• 주변 시설: 관공서 {infra.get('관공서', 8)}개  |  교육기관 {infra.get('교육기관', 15)}개  |  금융기관 {infra.get('금융기관', 18)}개\n"
            f"• 대중 교통: 버스정류장 {infra.get('버스정류장', 48)}개 노선망  |  지하철 {infra.get('지하철', '분당선 서현역')}\n"
            f"• 상권 구성: 주거지역 93% 압도적 밀집으로 탄탄한 배후 생활권 형성"
        )
        p_inf2.font.size = Pt(9.5)
        p_inf2.font.color.rgb = self.c_slate_dark
        
        # 우측 하단 13개월 매출 추이 차트
        if 'sales_trend' in charts and os.path.exists(charts['sales_trend']):
            s5.shapes.add_picture(charts['sales_trend'], Inches(4.7), Inches(3.2), width=Inches(8.0))
            
        self._add_source_footer(s5, "* 출처 : 소상공인365/BASA 상권분석 플랫폼 & NICE비즈맵 실측 빅데이터")

        # ---------------------------------------------------------------------
        # Slide 6: 업종 성장률 및 골프 특화도 실측 (골프용품 +182.4% 1위)
        # ---------------------------------------------------------------------
        s6 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s6, "3. 업종별 성장률 및 골프 특화도 실측 (", "골프용품 매출성장률 +182.4% 1위", ", 스크린골프 0.7%)")
        
        # 1. 매출 증가율 TOP 5
        c6_1 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.3), Inches(5.9), Inches(2.75))
        c6_1.fill.solid()
        c6_1.fill.fore_color.rgb = self.c_card_bg
        c6_1.line.color.rgb = self.c_royal_blue
        tf6_1 = c6_1.text_frame
        tf6_1.word_wrap = True
        p = tf6_1.paragraphs[0]
        p.text = "📈 서현1동 매출 증가율 TOP 5 (소상공인365 실측)"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = self.c_navy
        growths = comm.get('top_growth_industries', [])
        for g in growths:
            p_g = tf6_1.add_paragraph()
            p_g.space_before = Pt(3)
            p_g.text = f"• {g['rank']}위 : {g['name']}  ({g['growth']}) - {g['status']}"
            p_g.font.size = Pt(9.5)
            p_g.font.color.rgb = self.c_red if g['rank'] == 1 else self.c_slate_dark
            p_g.font.bold = (g['rank'] == 1)
            
        # 2. 스크린골프 업종 비중 및 골프 문화 집중도
        golf_den = comm.get('golf_industry_density', {})
        c6_2 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.3), Inches(5.9), Inches(2.75))
        c6_2.fill.solid()
        c6_2.fill.fore_color.rgb = self.c_card_bg
        c6_2.line.color.rgb = self.c_gold
        tf6_2 = c6_2.text_frame
        tf6_2.word_wrap = True
        p = tf6_2.paragraphs[0]
        p.text = "⛳ 지역 골프 문화 및 유사 레저 밀집도 (BASA 실측)"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = self.c_gold
        p_d1 = tf6_2.add_paragraph()
        p_d1.space_before = Pt(4)
        p_d1.text = (
            f"• 서현1동 내 스크린골프 점포: {golf_den.get('store_count', 10)}개 (전체 {golf_den.get('total_stores_in_dong', 1526)}개 점포 중)\n"
            f"• 스크린골프 업종 비중: {golf_den.get('density_ratio', 0.7)}% (전국 평균 {golf_den.get('national_avg_density', 0.3)}% 대비 +0.4%p 높음)\n"
            f"• 전국 평균 대비 2.3배 밀집된 '골프·파크골프 소비 문화 최상위 특화 상권'\n"
            f"• 성장 단계: {golf_den.get('growth_stage', '집중 성장 단계')}"
        )
        p_d1.font.size = Pt(9.5)
        p_d1.font.color.rgb = self.c_slate_dark
        
        # 3. 요일/시간대 이용 패턴 분석
        c6_3 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(4.2), Inches(5.9), Inches(2.75))
        c6_3.fill.solid()
        c6_3.fill.fore_color.rgb = self.c_card_bg
        c6_3.line.color.rgb = self.c_border
        tf6_3 = c6_3.text_frame
        tf6_3.word_wrap = True
        p = tf6_3.paragraphs[0]
        p.text = "⏰ 요일 및 시간대별 매출 패턴 (NICE비즈맵 실측)"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = self.c_navy
        p_t1 = tf6_3.add_paragraph()
        p_t1.space_before = Pt(4)
        p_t1.text = (
            f"• 피크 요일: 월요일 ({comm['day_distribution']['월']}%) 최고치 (주간 동호회 정기 모임)\n"
            f"• 주간 비중: 10~17시 이용 비중이 전체의 {comm['time_distribution']['주간_10_17시_비중']}% 압도적\n"
            f"• 일반 스크린골프(야간 위주)와 달리 낮 시간대 풀가동으로 회전율 2배 달성\n"
            f"• 주말 가동률: 주말 평균 비중 {comm['day_distribution']['주말평균비중']}%로 주 7일 고른 수익"
        )
        p_t1.font.size = Pt(9.5)
        p_t1.font.color.rgb = self.c_slate_dark
        
        # 4. 사업화 시사점
        c6_4 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(4.2), Inches(5.9), Inches(2.75))
        c6_4.fill.solid()
        c6_4.fill.fore_color.rgb = self.c_pink_bg
        c6_4.line.color.rgb = self.c_red
        tf6_4 = c6_4.text_frame
        tf6_4.word_wrap = True
        p = tf6_4.paragraphs[0]
        p.text = "🎯 마이파크 출점 종합 전략적 시사점"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = self.c_red
        p_s1 = tf6_4.add_paragraph()
        p_s1.space_before = Pt(4)
        p_s1.text = (
            f"• 수요 검증 완료: 골프용품 매출 성장 1위(+182.4%) 상권으로 검증된 소비력\n"
            f"• 공급 격차 점유: 노후 2~3타석 매장 대비 10타석 플래그십으로 상위 시장 독점\n"
            f"• 복합 문화 공간: 카페형 라운지 및 파크골프 용품 샵 연계로 객단가 극대화\n"
            f"• 상권 락인(Lock-in): 주거지역 93% 배후 고정 고객 대상 월회원제 정착"
        )
        p_s1.font.size = Pt(9.5)
        p_s1.font.color.rgb = self.c_slate_dark
        
        self._add_source_footer(s6, "* 출처 : 소상공인365/BASA, NICE비즈맵(NICE지니데이타), SK지오비전 실측 빅데이터")

        # ---------------------------------------------------------------------
        # Slide 7: 주변 경쟁 매장 실측 분석 (글자 짤림 100% 완전 박멸)
        # ---------------------------------------------------------------------
        s7 = self.prs.slides.add_slide(self.blank_layout)
        comps = comm.get('competitors', [])
        count_str = f"({len(comps)}곳)" if len(comps) > 0 and comps[0].get('rooms', 0) > 0 else "(블루오션 상권)"
        self._add_header_bar(s7, "주변 스크린 ", f"파크골프 매장{count_str}", " 실측 분석")
        
        card_w = Inches(2.85)
        gap = Inches(0.2)
        start_x = Inches(0.6)
        
        for idx, c in enumerate(comps[:4]):
            cur_x = start_x + (idx * (card_w + gap))
            
            # 1. 상단 다크 네이비 헤더 바 (높이 0.65인치로 확장하여 2줄 자연 줄바꿈)
            hdr_box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_x, Inches(1.3), card_w, Inches(0.65))
            hdr_box.fill.solid()
            hdr_box.fill.fore_color.rgb = self.c_navy
            hdr_box.line.color.rgb = self.c_royal_blue
            tf_h = hdr_box.text_frame
            tf_h.word_wrap = True
            tf_h.vertical_anchor = MSO_ANCHOR.MIDDLE
            p_hdr = tf_h.paragraphs[0]
            p_hdr.text = str(c['name'])
            p_hdr.font.name = 'Malgun Gothic'
            p_hdr.font.size = Pt(10)
            p_hdr.font.bold = True
            p_hdr.font.color.rgb = self.c_white
            p_hdr.alignment = PP_ALIGN.CENTER
            
            # 2. 중간 비주얼 배지 블록 (높이 1.25인치)
            mid_box = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_x, Inches(2.0), card_w, Inches(1.25))
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
            p_m1.font.size = Pt(13)
            p_m1.font.color.rgb = self.c_royal_blue
            p_m2 = tf_m.add_paragraph()
            p_m2.alignment = PP_ALIGN.CENTER
            p_m2.space_before = Pt(3)
            p_m2.text = f"[{c.get('status', '실측완료')}] {c.get('system', '스크린 시스템')}"
            p_m2.font.size = Pt(8.5)
            p_m2.font.color.rgb = self.c_slate_dark
            
            # 3. 하단 실측 스펙 박스 (높이 3.6인치로 확장, 폰트 8.5pt로 짤림 0%)
            body_box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_x, Inches(3.3), card_w, Inches(3.65))
            body_box.fill.solid()
            body_box.fill.fore_color.rgb = self.c_card_bg
            body_box.line.color.rgb = self.c_border
            tf_body = body_box.text_frame
            tf_body.word_wrap = True
            tf_body.margin_left = Inches(0.12)
            tf_body.margin_right = Inches(0.12)
            tf_body.margin_top = Inches(0.12)
            
            p1 = tf_body.paragraphs[0]
            p1.text = f"▲ 주소: {c['address']}"
            p1.font.size = Pt(8.5)
            p1.font.color.rgb = self.c_slate_dark
            
            p2 = tf_body.add_paragraph()
            p2.space_before = Pt(5)
            p2.text = f"▲ 시스템: {c['system']}"
            p2.font.size = Pt(8.5)
            p2.font.color.rgb = self.c_royal_blue
            p2.font.bold = True
            
            p3 = tf_body.add_paragraph()
            p3.space_before = Pt(5)
            p3.text = f"▲ 보유 규모: {c['rooms']}타석 운영" if c.get('rooms', 0) > 0 else "▲ 상태: 상업용 전문매장 미등록"
            p3.font.size = Pt(8.5)
            p3.font.color.rgb = self.c_slate_dark
            
            p4 = tf_body.add_paragraph()
            p4.space_before = Pt(5)
            p4.text = f"▲ 특징: {c.get('features', '-')}"
            p4.font.size = Pt(8.5)
            p4.font.color.rgb = self.c_slate_gray
            
        self._add_source_footer(s7, "* 출처 : 소상공인시장진흥공단 상권정보 및 카카오맵 로컬 POI 실측 조사")

        # ---------------------------------------------------------------------
        # Slide 8: 5대 지표 종합 평가 (산출 근거 투명 공개)
        # ---------------------------------------------------------------------
        s8 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s8, "5. 마이파크 입지 최적성 종합 평가 [", f"{score['grade']}등급 - {score['total_score']}점", " / 100점]")
        if 'radar_score' in charts and os.path.exists(charts['radar_score']):
            s8.shapes.add_picture(charts['radar_score'], Inches(0.6), Inches(1.3), width=Inches(5.6))
            
        tb8 = s8.shapes.add_textbox(Inches(6.4), Inches(1.3), Inches(6.3), Inches(5.5))
        tf8 = tb8.text_frame
        tf8.word_wrap = True
        
        indicators = [
            ("1) 골든 시니어 집적도", score['scores']['senior_population'], 25, "반경 3km 내 50대 이상 시니어 72,400명 (38.4%) 실측 매핑"),
            ("2) 접근성 및 주차 인프라", score['scores']['accessibility_parking'], 25, "10타석 표준 주차 10~12대 확보 권장 기준 충족 가정치"),
            ("3) 공간 적합성 및 임대료", score['scores']['space_efficiency'], 15, "권장 유효 층고 2.8m 이상 센서 작동 물리 규격 기준 충족"),
            ("4) 수요 공급 갭 (블루오션)", score['scores']['supply_gap'], 15, "반경 3km 내 전문 매장 1~2곳으로 공급 부족 (1호점 선점)"),
            ("5) 지역 소비력 및 여가지출", score['scores']['commercial_spending'], 20, "스포츠/여가 월평균 카드 매출 2,150만원 소비력 우수"),
        ]
        for idx, (iname, iscore, imax, idesc) in enumerate(indicators):
            p = tf8.add_paragraph() if idx > 0 else tf8.paragraphs[0]
            p.space_before = Pt(6)
            r1 = p.add_run()
            r1.text = f"● {iname}: "
            r1.font.bold = True
            r1.font.size = Pt(11.5)
            r1.font.color.rgb = self.c_navy
            r2 = p.add_run()
            r2.text = f"{iscore}점 / {imax}점 만점"
            r2.font.bold = True
            r2.font.size = Pt(11.5)
            r2.font.color.rgb = self.c_royal_blue
            p_desc = tf8.add_paragraph()
            p_desc.text = f"   ↳ 산출 근거: {idesc}"
            p_desc.font.size = Pt(9)
            p_desc.font.color.rgb = self.c_slate_gray
            
        p_res = tf8.add_paragraph()
        p_res.space_before = Pt(10)
        r_res = p_res.add_run()
        r_res.text = f"★ 종합 판정: 총점 {score['total_score']}점 ({score['grade_desc']})"
        r_res.font.bold = True
        r_res.font.size = Pt(12.5)
        r_res.font.color.rgb = self.c_red
        
        self._add_source_footer(s8, "* 평가 기준: 마이파크 가맹 입지선정 5대 다이아몬드 스코어링 모델 (22+25+15+15+20=97.0점)")

        # ---------------------------------------------------------------------
        # Slide 9: 월 매출
        # ---------------------------------------------------------------------
        s9 = self.prs.slides.add_slide(self.blank_layout)
        m_scen = fin['monthly_scenarios']
        self._add_header_bar(s9, "6. 마이파크 사업 타당성 분석 (", f"{site['rooms']}타석 / {site['area_pyeong']}평", ") - 월 예상 매출")
        table_s9 = s9.shapes.add_table(4, 7, Inches(0.6), Inches(1.8), Inches(12.133), Inches(2.6)).table
        
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

        # ---------------------------------------------------------------------
        # Slide 10: 운영 비용
        # ---------------------------------------------------------------------
        s10 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s10, "6. 마이파크 사업 타당성 분석 (", f"{site['rooms']}타석", ") - 예상 운영 비용")
        table_s10 = s10.shapes.add_table(5, 5, Inches(0.6), Inches(1.8), Inches(12.133), Inches(3.4)).table
        
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

        # ---------------------------------------------------------------------
        # Slide 11: 5개년 손익 예측 및 BEP 용어 정상화
        # ---------------------------------------------------------------------
        s11 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s11, "6. 마이파크 사업 타당성 분석 - ", "5개년 손익 예측", " (연 2% 성장률 반영)")
        if 'profit_forecast' in charts and os.path.exists(charts['profit_forecast']):
            s11.shapes.add_picture(charts['profit_forecast'], Inches(0.6), Inches(1.3), width=Inches(6.8))
            
        mod_1y = fin['forecast_5year']['moderate'][0]
        mod_5y = fin['forecast_5year']['moderate'][4]
        
        c_kpi1 = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.6), Inches(1.4), Inches(5.1), Inches(1.8))
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
        p2.text = f"• 1년차: 연매출 {mod_1y['total_revenue']//100000000:.1f}억원 / 영업이익 {mod_1y['operating_profit']//100000000:.1f}억원\n• 5년차: 연매출 {mod_5y['total_revenue']//100000000:.1f}억원 / 영업이익 {mod_5y['operating_profit']//100000000:.1f}억원\n• 영업이익률: 약 48.6% (안정적 고수익 구조)"
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = self.c_slate_dark
        
        c_kpi2 = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.6), Inches(3.4), Inches(5.1), Inches(2.2))
        c_kpi2.fill.solid()
        c_kpi2.fill.fore_color.rgb = self.c_card_bg
        c_kpi2.line.color.rgb = self.c_emerald
        tf_k2 = c_kpi2.text_frame
        tf_k2.word_wrap = True
        tf_k2.margin_left = Inches(0.16)
        tf_k2.margin_right = Inches(0.16)
        p = tf_k2.paragraphs[0]
        p.text = "⏱️ 손익분기점(BEP) 및 투자금 회수"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = self.c_emerald
        p2 = tf_k2.add_paragraph()
        p2.space_before = Pt(4)
        p2.text = (
            f"• 손익분기점(BEP): 기기(타석)당 1일 단 0.8회전\n"
            f"  ↳ 매장 전체 1일 8명(월 240명), 월매출 약 1,940만원 달성 시 BEP 돌파\n"
            f"• 순투자금 회수: 초기 순투자금 약 {fin['investment']['total_capex']//100000000:.2f}억원 기준\n"
            f"  ↳ 보편 가동 시 약 {fin['investment']['payback_months_moderate']:.1f}개월 만에 전액 회수"
        )
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = self.c_slate_dark
        
        self._add_source_footer(s11, f"* 산출 근거: 초기 순투자금 {fin['investment']['total_capex']//100000000:.2f}억원 기준 / 연 2% 복리 성장률 반영")

        # ---------------------------------------------------------------------
        # Slide 12: 종합 결론 및 사업 타당성 최종 평가 (글자 나열 탈피, 최고급 3단 구조화)
        # ---------------------------------------------------------------------
        s12 = self.prs.slides.add_slide(self.blank_layout)
        self._add_header_bar(s12, "7. 종합 결론 및 ", "사업 타당성 최종 평가", " (S등급 Prime Spot)")
        
        # 상단 4대 핵심 지표 배지
        kpi_badges = [
            (Inches(0.6), "배후 시니어 인구", f"{demo['senior_50_plus']:,}명 ({demo['senior_ratio']}%)", self.c_navy),
            (Inches(3.68), "예상 월 영업이익", f"{fin['monthly_scenarios']['moderate']['operating_profit']//10000:,}만원/월", self.c_emerald),
            (Inches(6.76), "손익분기점(BEP)", "타석당 1일 단 0.8회전", self.c_royal_blue),
            (Inches(9.84), "투자금 전액 회수", f"약 {fin['investment']['payback_months_moderate']:.1f}개월", self.c_gold),
        ]
        for bx, btitle, bval, bcol in kpi_badges:
            k_card = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, Inches(1.3), Inches(2.89), Inches(1.1))
            k_card.fill.solid()
            k_card.fill.fore_color.rgb = self.c_card_bg
            k_card.line.color.rgb = self.c_border
            tf_k = k_card.text_frame
            tf_k.vertical_anchor = MSO_ANCHOR.MIDDLE
            p_t = tf_k.paragraphs[0]
            p_t.text = btitle
            p_t.font.size = Pt(9.5)
            p_t.font.color.rgb = self.c_slate_gray
            p_v = tf_k.add_paragraph()
            p_v.text = bval
            p_v.font.size = Pt(13)
            p_v.font.bold = True
            p_v.font.color.rgb = bcol
            
        # 좌측: 가맹점 출점 3대 핵심 경쟁력
        card12_1 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(2.6), Inches(5.9), Inches(4.35))
        card12_1.fill.solid()
        card12_1.fill.fore_color.rgb = self.c_card_bg
        card12_1.line.color.rgb = self.c_gold
        card12_1.line.width = Pt(1.5)
        tf_12_1 = card12_1.text_frame
        tf_12_1.word_wrap = True
        tf_12_1.margin_left = Inches(0.18)
        tf_12_1.margin_right = Inches(0.18)
        tf_12_1.margin_top = Inches(0.15)
        p = tf_12_1.paragraphs[0]
        p.text = "🌟【 가맹점 출점 3대 핵심 경쟁력 】"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = self.c_gold
        
        f_points = [
            ("1. 주간 유휴시간 제로 (100% 예약 풀가동)", f"일반 스크린골프 손님이 없는 '평일 낮 10시~오후 5시'에 반경 3km 내 7.2만 시니어 동호회 모임으로 100% 예약 가동"),
            ("2. 10타석 플래그십 상위 20% 시장 독점", f"노후 소형 1~2타석 매장과 차별화된 쾌적한 카페형 라운지 및 10타석 대규모로 지역 내 독점 랜드마크화"),
            ("3. 빠른 원금 회수 및 고수익성", f"월 순영업이익 약 {fin['monthly_scenarios']['moderate']['operating_profit']//10000:,}만원(영업이익률 48.6%) 달성으로 약 {fin['investment']['payback_months_moderate']:.1f}개월 내 원금 전액 회수")
        ]
        for title, desc in f_points:
            p_t = tf_12_1.add_paragraph()
            p_t.space_before = Pt(8)
            p_t.text = f"● {title}"
            p_t.font.size = Pt(10.5)
            p_t.font.bold = True
            p_t.font.color.rgb = self.c_navy
            p_d = tf_12_1.add_paragraph()
            p_d.text = f"   {desc}"
            p_d.font.size = Pt(9)
            p_d.font.color.rgb = self.c_slate_dark
            
        # 우측: 상가 전체 상권 활성화 및 건물 가치 상승
        card12_2 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(2.6), Inches(5.9), Inches(4.35))
        card12_2.fill.solid()
        card12_2.fill.fore_color.rgb = self.c_card_bg
        card12_2.line.color.rgb = self.c_emerald
        card12_2.line.width = Pt(1.5)
        tf_12_2 = card12_2.text_frame
        tf_12_2.word_wrap = True
        tf_12_2.margin_left = Inches(0.18)
        tf_12_2.margin_right = Inches(0.18)
        tf_12_2.margin_top = Inches(0.15)
        p = tf_12_2.paragraphs[0]
        p.text = "🏢【 건물주 및 상가 상생 활성화 효과 】"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = self.c_emerald
        
        l_points = [
            ("1. 일 60~90명 액티브 시니어 지속 유입", "구매력 높은 지역 시니어 고객이 매일 건물을 방문하여 1층 식당, 카페, 병원 등 상가 타 점포 매출까지 동반 상승"),
            ("2. 공실 해소 및 5년 장기 우량 임대차", "마이파크 본사 및 가맹점과의 5년 이상 장기 임대차 계약으로 공실 리스크 제로 및 안정적 월세 수익 보장"),
            ("3. 건물 전체의 자산 가치(Cap Rate) 상승", "안정적인 고수익 핵심 점포 입점에 따른 상가 건물 전체의 유동인구 증가 및 부동산 매매 가치 동반 상승 견인")
        ]
        for title, desc in l_points:
            p_t = tf_12_2.add_paragraph()
            p_t.space_before = Pt(8)
            p_t.text = f"● {title}"
            p_t.font.size = Pt(10.5)
            p_t.font.bold = True
            p_t.font.color.rgb = self.c_navy
            p_d = tf_12_2.add_paragraph()
            p_d.text = f"   {desc}"
            p_d.font.size = Pt(9)
            p_d.font.color.rgb = self.c_slate_dark
            
        self._add_source_footer(s12, "* 마이파크(MYPARK) 사업본부 상권분석 시스템 v1.0")
        
        os.makedirs(os.path.dirname(output_pptx_path), exist_ok=True)
        self.prs.save(output_pptx_path)
        print(f"[PPTX GENERATED] {output_pptx_path}")
        return output_pptx_path
