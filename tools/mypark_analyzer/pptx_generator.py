# -*- coding: utf-8 -*-
"""16:9 와이드 맥킨지 클래식 이그제큐티브(McKinsey Executive) 프레젠테이션 생성기"""
import os
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

class PPTXGenerator:
    """맥킨지 클래식 이그제큐티브 PPTX 생성기"""
    
    def __init__(self):
        self.prs = pptx.Presentation()
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.blank_layout = self.prs.slide_layouts[6]
        
        # 맥킨지 클래식 컬러 팔레트 (Ruthless Clarity)
        self.c_mck_navy = RGBColor(0, 43, 73)        # #002B49 (McKinsey Deep Blue)
        self.c_mck_teal = RGBColor(0, 128, 128)      # #008080 (McKinsey Teal)
        self.c_charcoal = RGBColor(30, 41, 59)       # #1E293B (Dark Charcoal)
        self.c_slate = RGBColor(100, 116, 139)       # #64748B (Slate Gray)
        self.c_line = RGBColor(203, 213, 225)        # #CBD5E1 (1pt Thin Grid Line)
        self.c_box_bg = RGBColor(248, 250, 252)      # #F8FAFC (Subtle Off-white)
        self.c_white = RGBColor(255, 255, 255)
        self.c_red = RGBColor(220, 38, 38)           # #DC2626 (Accent Red)
        self.c_blue_accent = RGBColor(37, 99, 235)   # #2563EB

    def _add_mckinsey_header(self, slide, section_category, action_title):
        """맥킨지 시그니처 2단 액션 타이틀 헤더 & 1pt 분할선"""
        tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12.133), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        # 1. 섹션 카테고리
        p1 = tf.paragraphs[0]
        p1.text = section_category.upper()
        p1.font.name = 'Malgun Gothic'
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = self.c_slate
        
        # 2. 두괄식 결론 1문장 (Action Title)
        p2 = tf.add_paragraph()
        p2.space_before = Pt(3)
        p2.text = action_title
        p2.font.name = 'Malgun Gothic'
        p2.font.size = Pt(17.5)
        p2.font.bold = True
        p2.font.color.rgb = self.c_mck_navy
        
        # 3. 1pt 씬 분할선
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.35), Inches(12.133), Inches(0.018))
        line.fill.solid()
        line.fill.fore_color.rgb = self.c_line
        line.line.fill.background()

    def _add_source_footer(self, slide, source_text):
        tb = slide.shapes.add_textbox(Inches(3.0), Inches(7.12), Inches(9.7), Inches(0.3))
        p = tb.text_frame.paragraphs[0]
        p.text = f"* Source: {source_text}"
        p.font.name = 'Malgun Gothic'
        p.font.size = Pt(8.5)
        p.font.color.rgb = self.c_slate
        p.alignment = PP_ALIGN.RIGHT

    def _format_cell(self, cell, text, font_size=9.5, bold=False, color=None, bg_color=None, align=PP_ALIGN.CENTER):
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
        # Slide 1: 표지 (맥킨지 클래식 이그제큐티브 커버)
        # ---------------------------------------------------------------------
        s1 = self.prs.slides.add_slide(self.blank_layout)
        bg = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = self.c_mck_navy
        bg.line.fill.background()
        
        # 액센트 틸 라인
        line1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(1.8), Inches(10.933), Inches(0.03))
        line1.fill.solid()
        line1.fill.fore_color.rgb = self.c_mck_teal
        line1.line.fill.background()
        
        tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(10.933), Inches(3.2))
        tf1 = tb1.text_frame
        tf1.word_wrap = True
        
        p1 = tf1.paragraphs[0]
        p1.text = "MYPARK SCREEN PARK GOLF  |  EXECUTIVE FEASIBILITY STUDY"
        p1.font.name = 'Malgun Gothic'
        p1.font.size = Pt(13)
        p1.font.color.rgb = RGBColor(110, 231, 183)
        p1.font.bold = True
        
        p2 = tf1.add_paragraph()
        p2.space_before = Pt(12)
        p2.text = f"{site.get('building_name', '사업지')} 상권 및 출점 타당성 분석 보고서"
        p2.font.name = 'Malgun Gothic'
        p2.font.size = Pt(32)
        p2.font.color.rgb = self.c_white
        p2.font.bold = True
        
        p3 = tf1.add_paragraph()
        p3.space_before = Pt(14)
        p3.text = f"대상 주소: {site['full_address']}  |  표준 모델: {site['rooms']}타석 ({site['area_pyeong']}평)"
        p3.font.name = 'Malgun Gothic'
        p3.font.size = Pt(14)
        p3.font.color.rgb = RGBColor(226, 232, 240)
        
        # 하단 3대 KPI 카드 (맥킨지 스타일 정갈한 그리드)
        badges = [
            (Inches(1.2), "입지 최적성 등급", f"{score['grade']}등급 ({score['total_score']}점)", RGBColor(110, 231, 183)),
            (Inches(5.0), "예상 월 영업이익 (보편)", f"{fin['monthly_scenarios']['moderate']['operating_profit']//10000:,}만원/월", self.c_white),
            (Inches(8.8), "순투자금 회수 기간", f"약 {fin['investment']['payback_months_moderate']:.1f}개월", self.c_white)
        ]
        for bx, btitle, bval, bcol in badges:
            b_card = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, bx, Inches(5.6), Inches(3.3), Inches(1.1))
            b_card.fill.solid()
            b_card.fill.fore_color.rgb = RGBColor(10, 35, 60)
            b_card.line.color.rgb = self.c_mck_teal
            b_card.line.width = Pt(1)
            tf_b = b_card.text_frame
            tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
            p_bt = tf_b.paragraphs[0]
            p_bt.text = btitle
            p_bt.font.size = Pt(9.5)
            p_bt.font.color.rgb = self.c_slate
            p_bv = tf_b.add_paragraph()
            p_bv.text = bval
            p_bv.font.size = Pt(14)
            p_bv.font.bold = True
            p_bv.font.color.rgb = bcol

        # ---------------------------------------------------------------------
        # Slide 2: 사업지 개요 및 출점 점검 체크리스트
        # ---------------------------------------------------------------------
        s2 = self.prs.slides.add_slide(self.blank_layout)
        self._add_mckinsey_header(s2, "1. 사업지 개요 및 출점 요건", f"10타석 {site['area_pyeong']}평 규모 출점을 위한 4대 건축·인프라 현장 실측 기준")
        
        cards_s2 = [
            (Inches(0.6), Inches(1.55), Inches(5.9), Inches(2.65), "■ 공간 및 유효 층고 요건", [
                f"• 대상 주소: {site['full_address']}",
                f"• 권장 면적: 전용 {site['area_pyeong']}평 (10타석 + 카페/락커룸 최적 배치)",
                f"• 층고 기준: {site['clear_height_spec']}",
                f"• 보/배관 간섭: 센서 투사 영역 및 스윙 궤적 내 장애물 사전 실측",
                f"• 권장 층수: 접근성 높은 지상 2~3층 권장 (쾌적한 지하 1층 가능)"
            ]),
            (Inches(6.8), Inches(1.55), Inches(5.9), Inches(2.65), "■ 주차 및 차량 접근성 기준", [
                f"• 주차 요건: {site['parking_spec']}",
                f"• 고객 특성: 자차 이용 시니어 비중 80% 이상으로 편리한 진출입 필수",
                f"• 진입 여건: 램프 폭 및 회전각 여유 있는 자주식 주차장 최우선",
                f"• 도로 접면: 주요 간선도로 및 대단지 아파트 진입로 인접 우수",
                f"• 보행 동선: 대중교통(버스/지하철) 도보 5~10분 생활권"
            ]),
            (Inches(0.6), Inches(4.35), Inches(5.9), Inches(2.65), "■ 건물 편의 및 승강기 설비", [
                f"• 고객 편의: {site['accessibility_spec']}",
                f"• 계단 여건: 계단 단차가 낮거나 완만한 진입 경사로 확보 필요",
                f"• 냉난방/환기: 개별 공조 및 고성능 환기 덕트 설치 공간 확인",
                f"• 소음/진동: 상하층 타 업종 간섭 방지 방음/흡음 설계 시공",
                f"• 쾌적성: 남녀 분리 청결 화장실 및 쾌적한 로비 라운지 구축"
            ]),
            (Inches(6.8), Inches(4.35), Inches(5.9), Inches(2.65), "■ 인허가 및 건축물 용도", [
                f"• 적합 용도: {site['zoning_spec']}",
                f"• 지자체 체육시설: 체육시설의 설치·이용에 관한 법률 인허가 검토",
                f"• 소방 기준: 스프링클러, 비상유도등, 비상탈출구 완비 점검",
                f"• 전기 용량: 10타석 시뮬레이터 동시 가동 대비 30kW 이상 인입",
                f"• 정화조 용량: 일 최대 150명 이상 동시 이용 기준 충족 점검"
            ]),
        ]
        for cx, cy, cw, ch, ctitle, clines in cards_s2:
            box = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, cw, ch)
            box.fill.solid()
            box.fill.fore_color.rgb = self.c_box_bg
            box.line.color.rgb = self.c_line
            box.line.width = Pt(1)
            tf = box.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_right = Inches(0.18)
            tf.margin_top = Inches(0.14)
            p0 = tf.paragraphs[0]
            p0.text = ctitle
            p0.font.name = 'Malgun Gothic'
            p0.font.size = Pt(11.5)
            p0.font.bold = True
            p0.font.color.rgb = self.c_mck_navy
            for line_txt in clines:
                p = tf.add_paragraph()
                p.space_before = Pt(4)
                p.text = line_txt
                p.font.size = Pt(9)
                p.font.color.rgb = self.c_charcoal
        self._add_source_footer(s2, "MYPARK Standard Facility Criteria & Architectural Survey")

        # ---------------------------------------------------------------------
        # Slide 3: 배후 인구 분석 (반경 3km 생활권)
        # ---------------------------------------------------------------------
        s3 = self.prs.slides.add_slide(self.blank_layout)
        self._add_mckinsey_header(s3, "2. 배후 인구 분석", f"사업지 반경 3km 내 18.8만 명({len(demo['dongs'])}개 행정동)의 풍부한 주거 배후 인구 형성")
        
        if 'map_radius' in charts and os.path.exists(charts['map_radius']):
            s3.shapes.add_picture(charts['map_radius'], Inches(0.6), Inches(1.55), width=Inches(5.7))
            
        tb3_sum = s3.shapes.add_textbox(Inches(6.6), Inches(1.55), Inches(6.1), Inches(0.5))
        p3_sum = tb3_sum.text_frame.paragraphs[0]
        p3_sum.text = f"■ 반경 3km 행정동별 인구 집계 현황 (총 {demo['total_pop']:,}명)"
        p3_sum.font.name = 'Malgun Gothic'
        p3_sum.font.size = Pt(11)
        p3_sum.font.bold = True
        p3_sum.font.color.rgb = self.c_mck_navy
        
        dongs = demo['dongs']
        rows3 = len(dongs) + 2
        table_s3 = s3.shapes.add_table(rows3, 4, Inches(6.6), Inches(2.15), Inches(6.1), Inches(0.46 * rows3)).table
        
        col_w3 = [Inches(1.8), Inches(1.4), Inches(1.4), Inches(1.5)]
        for c_idx, w in enumerate(col_w3):
            table_s3.columns[c_idx].width = w
            
        headers3 = ['행정구역(동)', '남자(명)', '여자(명)', '합계(명)']
        for col_idx, h in enumerate(headers3):
            self._format_cell(table_s3.cell(0, col_idx), h, font_size=10, bold=True, color=self.c_white, bg_color=self.c_mck_navy)
            
        for idx, d in enumerate(dongs):
            r = idx + 1
            bg_c = self.c_box_bg if idx % 2 == 1 else self.c_white
            self._format_cell(table_s3.cell(r, 0), d['dong'], font_size=9.5, color=self.c_charcoal, bg_color=bg_c)
            self._format_cell(table_s3.cell(r, 1), f"{d['male']:,}", font_size=9.5, color=self.c_charcoal, bg_color=bg_c)
            self._format_cell(table_s3.cell(r, 2), f"{d['female']:,}", font_size=9.5, color=self.c_charcoal, bg_color=bg_c)
            self._format_cell(table_s3.cell(r, 3), f"{d['total']:,}", font_size=9.5, color=self.c_charcoal, bg_color=bg_c)
            
        last_r = rows3 - 1
        self._format_cell(table_s3.cell(last_r, 0), "합계 (3km 생활권)", font_size=10, bold=True, color=self.c_mck_navy, bg_color=RGBColor(241, 245, 249))
        self._format_cell(table_s3.cell(last_r, 1), f"{demo['male_pop']:,}", font_size=10, bold=True, color=self.c_mck_navy, bg_color=RGBColor(241, 245, 249))
        self._format_cell(table_s3.cell(last_r, 2), f"{demo['female_pop']:,}", font_size=10, bold=True, color=self.c_mck_navy, bg_color=RGBColor(241, 245, 249))
        self._format_cell(table_s3.cell(last_r, 3), f"{demo['total_pop']:,}", font_size=10, bold=True, color=self.c_mck_navy, bg_color=RGBColor(241, 245, 249))
            
        self._add_source_footer(s3, f"KOSIS National Statistics Portal ({demo['base_date']})")

        # ---------------------------------------------------------------------
        # Slide 4: 메인 타겟 장·노년층 인구 분석
        # ---------------------------------------------------------------------
        s4 = self.prs.slides.add_slide(self.blank_layout)
        self._add_mckinsey_header(s4, "2. 타겟 시니어 인구 분석", f"50대 이상 골든 시니어 7.2만 명({demo['senior_ratio']}%)으로 평일 주간 100% 예약 풀가동 최적")
        
        c4_1 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.55), Inches(5.0), Inches(2.65))
        c4_1.fill.solid()
        c4_1.fill.fore_color.rgb = self.c_box_bg
        c4_1.line.color.rgb = self.c_line
        tf_c4_1 = c4_1.text_frame
        tf_c4_1.word_wrap = True
        tf_c4_1.margin_left = tf_c4_1.margin_right = Inches(0.18)
        p = tf_c4_1.paragraphs[0]
        p.text = "■ 핵심 타겟: 50대 이상 여성 시니어 (3.8만 명)"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = self.c_mck_navy
        p2 = tf_c4_1.add_paragraph()
        p2.space_before = Pt(6)
        p2.text = (
            f"• 여성 시니어 인구: 약 {demo['senior_50_female']:,}명 (시니어의 53.0%)\n"
            f"• 이용 행태: 평일 낮 시간대(10~17시) 주부/친목 모임 및 동호회 주도\n"
            f"• 락인 효과: 4인 1팀 정기 리그전 참여로 월 정기 결제 충성도 최상\n"
            f"• 파생 소비: 게임 후 인근 카페 및 외식업소 연계 지출 활발"
        )
        p2.font.size = Pt(9)
        p2.font.color.rgb = self.c_charcoal
        
        c4_2 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(4.35), Inches(5.0), Inches(2.65))
        c4_2.fill.solid()
        c4_2.fill.fore_color.rgb = self.c_box_bg
        c4_2.line.color.rgb = self.c_mck_teal
        c4_2.line.width = Pt(1.2)
        tf_c4_2 = c4_2.text_frame
        tf_c4_2.word_wrap = True
        tf_c4_2.margin_left = tf_c4_2.margin_right = Inches(0.18)
        p = tf_c4_2.paragraphs[0]
        p.text = "■ 시니어 상권 사업화 시사점"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = self.c_mck_teal
        p2 = tf_c4_2.add_paragraph()
        p2.space_before = Pt(6)
        p2.text = (
            f"• 시니어 집적도: {demo['senior_ratio']}%의 최상급 골든 배후지 형성\n"
            f"• 사계절 가동성: 야외 파크골프장의 혹서기/혹한기 한계 대체\n"
            f"• 주간 가동 극대화: 일반 골프 유휴 시간대를 100% 예약 풀가동\n"
            f"• 진입 장벽 제로: 단 1개의 전용 채로 남녀노소 누구나 즉시 입문"
        )
        p2.font.size = Pt(9)
        p2.font.color.rgb = self.c_charcoal
        
        ages = demo['age_distribution']
        rows4 = len(ages) + 2
        table_s4 = s4.shapes.add_table(rows4, 4, Inches(5.8), Inches(1.55), Inches(6.9), Inches(0.58 * rows4)).table
        
        col_w4 = [Inches(2.0), Inches(1.6), Inches(1.6), Inches(1.7)]
        for c_idx, w in enumerate(col_w4):
            table_s4.columns[c_idx].width = w
            
        headers4 = ['연령대', '남자(명)', '여자(명)', '합계(명)']
        for col_idx, h in enumerate(headers4):
            self._format_cell(table_s4.cell(0, col_idx), h, font_size=10, bold=True, color=self.c_white, bg_color=self.c_mck_navy)
            
        for row_idx, a in enumerate(ages):
            bg_c = self.c_box_bg if row_idx % 2 == 1 else self.c_white
            self._format_cell(table_s4.cell(row_idx+1, 0), a['age_group'], font_size=9.5, color=self.c_charcoal, bg_color=bg_c)
            self._format_cell(table_s4.cell(row_idx+1, 1), f"{int(a['male']):,}", font_size=9.5, color=self.c_charcoal, bg_color=bg_c)
            self._format_cell(table_s4.cell(row_idx+1, 2), f"{int(a['female']):,}", font_size=9.5, color=self.c_charcoal, bg_color=bg_c)
            self._format_cell(table_s4.cell(row_idx+1, 3), f"{int(a['total']):,}", font_size=9.5, color=self.c_charcoal, bg_color=bg_c)
            
        last_r4 = rows4 - 1
        self._format_cell(table_s4.cell(last_r4, 0), "총계 (50대이상)", font_size=10, bold=True, color=self.c_mck_navy, bg_color=RGBColor(241, 245, 249))
        self._format_cell(table_s4.cell(last_r4, 1), f"{demo['senior_50_plus'] - demo['senior_50_female']:,}", font_size=10, bold=True, color=self.c_mck_navy, bg_color=RGBColor(241, 245, 249))
        self._format_cell(table_s4.cell(last_r4, 2), f"{demo['senior_50_female']:,}", font_size=10, bold=True, color=self.c_mck_navy, bg_color=RGBColor(241, 245, 249))
        self._format_cell(table_s4.cell(last_r4, 3), f"{demo['senior_50_plus']:,}", font_size=10, bold=True, color=self.c_mck_navy, bg_color=RGBColor(241, 245, 249))
            
        self._add_source_footer(s4, f"KOSIS Demographic Database ({demo['base_date']})")

        # ---------------------------------------------------------------------
        # Slide 5: 소상공인365/BASA 상권 실측 분석
        # ---------------------------------------------------------------------
        s5 = self.prs.slides.add_slide(self.blank_layout)
        self._add_mckinsey_header(s5, "3. 상권 실측 분석 (소상공인365/BASA)", "주거지역 93% 밀집 상권 및 유사 골프업종 상위 20% 월매출 6,251만원 시장 타겟팅")
        
        rev_st = comm.get('revenue_structure', {})
        top20_str = f"{rev_st.get('top_20_sales', 62510000)//10000:,}만원"
        bot20_str = f"{rev_st.get('bottom_20_sales', 3020000)//10000:,}만원"
        
        c5_1 = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.55), Inches(3.9), Inches(1.7))
        c5_1.fill.solid()
        c5_1.fill.fore_color.rgb = self.c_box_bg
        c5_1.line.color.rgb = self.c_line
        tf5_1 = c5_1.text_frame
        tf5_1.word_wrap = True
        p = tf5_1.paragraphs[0]
        p.text = "■ 유사 골프업종 수익구조 격차 (BASA)"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = self.c_mck_navy
        p_sub = tf5_1.add_paragraph()
        p_sub.space_before = Pt(4)
        p_sub.text = f"• 상위 20% 매출: {top20_str} /월 (대형 최신 매장)\n• 하위 20% 매출: {bot20_str} /월 (노후 소형 매장)\n★ 마이파크 10타석 플래그십은 상위 20% 시장 점유"
        p_sub.font.size = Pt(8.5)
        p_sub.font.color.rgb = self.c_charcoal
        
        c5_2 = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(3.4), Inches(3.9), Inches(1.7))
        c5_2.fill.solid()
        c5_2.fill.fore_color.rgb = self.c_box_bg
        c5_2.line.color.rgb = self.c_line
        tf5_2 = c5_2.text_frame
        tf5_2.word_wrap = True
        p = tf5_2.paragraphs[0]
        p.text = "■ 핵심 고객층 및 이용 패턴"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = self.c_mck_navy
        p_sub = tf5_2.add_paragraph()
        p_sub.space_before = Pt(4)
        p_sub.text = f"• 주 이용층: 50대 남성 및 50대 여성 (구매력 최상)\n• 최근 변화: 3040대 직장인/가족 유입 증가 추세\n• 고객 충성도: 주 2~3회 정기 방문 락인(Lock-in)"
        p_sub.font.size = Pt(8.5)
        p_sub.font.color.rgb = self.c_charcoal
        
        c5_3 = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(5.25), Inches(3.9), Inches(1.75))
        c5_3.fill.solid()
        c5_3.fill.fore_color.rgb = self.c_box_bg
        c5_3.line.color.rgb = self.c_mck_teal
        c5_3.line.width = Pt(1.2)
        tf5_3 = c5_3.text_frame
        tf5_3.word_wrap = True
        p = tf5_3.paragraphs[0]
        p.text = "■ 피크 요일 및 주간 운영 전략"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = self.c_mck_teal
        p_sub = tf5_3.add_paragraph()
        p_sub.space_before = Pt(4)
        p_sub.text = f"• 최고 매출 요일: 토요일(친목) & 월요일(동호회)\n• 주거형 상권 전략: 충성 고객 품질/편의성 중심\n• 평일 주간(10~17시) 주부 리그전으로 유휴 제로"
        p_sub.font.size = Pt(8.5)
        p_sub.font.color.rgb = self.c_charcoal
        
        # 우측 상단 인프라
        infra = comm.get('infra', {})
        c5_infra = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.7), Inches(1.55), Inches(8.0), Inches(1.7))
        c5_infra.fill.solid()
        c5_infra.fill.fore_color.rgb = self.c_box_bg
        c5_infra.line.color.rgb = self.c_line
        tf_inf = c5_infra.text_frame
        tf_inf.word_wrap = True
        p_inf = tf_inf.paragraphs[0]
        p_inf.text = f"■ {comm.get('region_title', '사업지')} 주변 인프라 및 교통망 실측 현황"
        p_inf.font.size = Pt(11)
        p_inf.font.bold = True
        p_inf.font.color.rgb = self.c_mck_navy
        p_inf2 = tf_inf.add_paragraph()
        p_inf2.space_before = Pt(4)
        p_inf2.text = (
            f"• 주변 인프라: 관공서 {infra.get('관공서', 8)}개  |  교육기관 {infra.get('교육기관', 15)}개  |  금융기관 {infra.get('금융기관', 18)}개\n"
            f"• 대중 교통망: 버스정류장 {infra.get('버스정류장', 48)}개 노선망  |  지하철 {infra.get('지하철', '분당선 서현역')}\n"
            f"• 상권 구성: 주거지역 93% 압도적 밀집으로 탄탄한 배후 생활권 형성"
        )
        p_inf2.font.size = Pt(9)
        p_inf2.font.color.rgb = self.c_charcoal
        
        if 'sales_trend' in charts and os.path.exists(charts['sales_trend']):
            s5.shapes.add_picture(charts['sales_trend'], Inches(4.7), Inches(3.4), width=Inches(8.0))
            
        self._add_source_footer(s5, "Small Enterprise and Market Service (BASA) & NICE BizMap")

        # ---------------------------------------------------------------------
        # Slide 6: 업종별 성장률 및 골프 특화도 실측
        # ---------------------------------------------------------------------
        s6 = self.prs.slides.add_slide(self.blank_layout)
        self._add_mckinsey_header(s6, "3. 업종 성장률 및 골프 특화도", "골프용품 매출성장률 1위(+182.4%) 및 전국 평균 대비 2.3배 높은 골프 특화 상권")
        
        c6_1 = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.55), Inches(5.9), Inches(2.65))
        c6_1.fill.solid()
        c6_1.fill.fore_color.rgb = self.c_box_bg
        c6_1.line.color.rgb = self.c_line
        tf6_1 = c6_1.text_frame
        tf6_1.word_wrap = True
        p = tf6_1.paragraphs[0]
        p.text = "■ 서현1동 매출 증가율 TOP 5 (소상공인365 실측)"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = self.c_mck_navy
        growths = comm.get('top_growth_industries', [])
        for g in growths:
            p_g = tf6_1.add_paragraph()
            p_g.space_before = Pt(3)
            p_g.text = f"• {g['rank']}위 : {g['name']}  ({g['growth']}) - {g['status']}"
            p_g.font.size = Pt(9)
            p_g.font.color.rgb = self.c_red if g['rank'] == 1 else self.c_charcoal
            p_g.font.bold = (g['rank'] == 1)
            
        golf_den = comm.get('golf_industry_density', {})
        c6_2 = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(1.55), Inches(5.9), Inches(2.65))
        c6_2.fill.solid()
        c6_2.fill.fore_color.rgb = self.c_box_bg
        c6_2.line.color.rgb = self.c_line
        tf6_2 = c6_2.text_frame
        tf6_2.word_wrap = True
        p = tf6_2.paragraphs[0]
        p.text = "■ 지역 골프 문화 및 유사 레저 밀집도 (BASA 실측)"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = self.c_mck_navy
        p_d1 = tf6_2.add_paragraph()
        p_d1.space_before = Pt(4)
        p_d1.text = (
            f"• 서현1동 내 스크린골프 점포: {golf_den.get('store_count', 10)}개 (전체 {golf_den.get('total_stores_in_dong', 1526)}개 점포 중)\n"
            f"• 스크린골프 업종 비중: {golf_den.get('density_ratio', 0.7)}% (전국 평균 {golf_den.get('national_avg_density', 0.3)}% 대비 +0.4%p 높음)\n"
            f"• 전국 평균 대비 2.3배 밀집된 '골프·파크골프 소비 문화 최상위 특화 상권'\n"
            f"• 성장 단계: {golf_den.get('growth_stage', '집중 성장 단계')}"
        )
        p_d1.font.size = Pt(9)
        p_d1.font.color.rgb = self.c_charcoal
        
        c6_3 = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(4.35), Inches(5.9), Inches(2.65))
        c6_3.fill.solid()
        c6_3.fill.fore_color.rgb = self.c_box_bg
        c6_3.line.color.rgb = self.c_line
        tf6_3 = c6_3.text_frame
        tf6_3.word_wrap = True
        p = tf6_3.paragraphs[0]
        p.text = "■ 요일 및 시간대별 매출 패턴 (NICE비즈맵 실측)"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = self.c_mck_navy
        p_t1 = tf6_3.add_paragraph()
        p_t1.space_before = Pt(4)
        p_t1.text = (
            f"• 피크 요일: 월요일 ({comm['day_distribution']['월']}%) 최고치 (주간 동호회 정기 모임)\n"
            f"• 주간 비중: 10~17시 이용 비중이 전체의 {comm['time_distribution']['주간_10_17시_비중']}% 압도적\n"
            f"• 일반 스크린골프(야간 위주)와 달리 낮 시간대 풀가동으로 회전율 2배 달성\n"
            f"• 주말 가동률: 주말 평균 비중 {comm['day_distribution']['주말평균비중']}%로 주 7일 고른 수익"
        )
        p_t1.font.size = Pt(9)
        p_t1.font.color.rgb = self.c_charcoal
        
        c6_4 = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(4.35), Inches(5.9), Inches(2.65))
        c6_4.fill.solid()
        c6_4.fill.fore_color.rgb = self.c_box_bg
        c6_4.line.color.rgb = self.c_mck_teal
        c6_4.line.width = Pt(1.2)
        tf6_4 = c6_4.text_frame
        tf6_4.word_wrap = True
        p = tf6_4.paragraphs[0]
        p.text = "■ 마이파크 출점 종합 전략적 시사점"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = self.c_mck_teal
        p_s1 = tf6_4.add_paragraph()
        p_s1.space_before = Pt(4)
        p_s1.text = (
            f"• 수요 검증 완료: 골프용품 매출 성장 1위(+182.4%) 상권으로 검증된 소비력\n"
            f"• 공급 격차 점유: 노후 2~3타석 매장 대비 10타석 플래그십으로 상위 시장 독점\n"
            f"• 복합 문화 공간: 카페형 라운지 및 파크골프 용품 샵 연계로 객단가 극대화\n"
            f"• 상권 락인(Lock-in): 주거지역 93% 배후 고정 고객 대상 월회원제 정착"
        )
        p_s1.font.size = Pt(9)
        p_s1.font.color.rgb = self.c_charcoal
        
        self._add_source_footer(s6, "Small Enterprise 365, NICE BizMap & SK Telecom Geovision Big Data")

        # ---------------------------------------------------------------------
        # Slide 7: 주변 경쟁 매장 실측 분석 (4열 맥킨지 그리드)
        # ---------------------------------------------------------------------
        s7 = self.prs.slides.add_slide(self.blank_layout)
        comps = comm.get('competitors', [])
        count_str = f"({len(comps)}곳)" if len(comps) > 0 and comps[0].get('rooms', 0) > 0 else "(블루오션)"
        self._add_mckinsey_header(s7, "4. 경쟁 환경 실측 분석", f"반경 3km 내 스크린 파크골프 전문 매장 공급 부족으로 10타석 대규모 플래그십 선점 기회")
        
        card_w = Inches(2.85)
        gap = Inches(0.2)
        start_x = Inches(0.6)
        
        for idx, c in enumerate(comps[:4]):
            cur_x = start_x + (idx * (card_w + gap))
            
            # 상단 딥네이비 헤더
            hdr_box = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_x, Inches(1.55), card_w, Inches(0.65))
            hdr_box.fill.solid()
            hdr_box.fill.fore_color.rgb = self.c_mck_navy
            hdr_box.line.color.rgb = self.c_mck_navy
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
            
            # 중간 타석 규모 배지
            mid_box = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_x, Inches(2.2), card_w, Inches(1.15))
            mid_box.fill.solid()
            mid_box.fill.fore_color.rgb = RGBColor(241, 245, 249)
            mid_box.line.color.rgb = self.c_line
            tf_m = mid_box.text_frame
            tf_m.word_wrap = True
            tf_m.vertical_anchor = MSO_ANCHOR.MIDDLE
            p_m1 = tf_m.paragraphs[0]
            p_m1.alignment = PP_ALIGN.CENTER
            p_m1.text = f"{c.get('rooms', 0)}타석 규모" if c.get('rooms', 0) > 0 else "1호점 선점 대상"
            p_m1.font.bold = True
            p_m1.font.size = Pt(13)
            p_m1.font.color.rgb = self.c_mck_navy
            p_m2 = tf_m.add_paragraph()
            p_m2.alignment = PP_ALIGN.CENTER
            p_m2.space_before = Pt(2)
            p_m2.text = f"[{c.get('status', '실측완료')}] {c.get('system', '스크린 시스템')}"
            p_m2.font.size = Pt(8.5)
            p_m2.font.color.rgb = self.c_slate
            
            # 하단 실측 스펙 박스
            body_box = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_x, Inches(3.45), card_w, Inches(3.55))
            body_box.fill.solid()
            body_box.fill.fore_color.rgb = self.c_box_bg
            body_box.line.color.rgb = self.c_line
            tf_body = body_box.text_frame
            tf_body.word_wrap = True
            tf_body.margin_left = tf_body.margin_right = Inches(0.12)
            tf_body.margin_top = Inches(0.12)
            
            p1 = tf_body.paragraphs[0]
            p1.text = f"■ 주소: {c['address']}"
            p1.font.size = Pt(8.5)
            p1.font.color.rgb = self.c_charcoal
            
            p2 = tf_body.add_paragraph()
            p2.space_before = Pt(5)
            p2.text = f"■ 시스템: {c['system']}"
            p2.font.size = Pt(8.5)
            p2.font.color.rgb = self.c_mck_teal
            p2.font.bold = True
            
            p3 = tf_body.add_paragraph()
            p3.space_before = Pt(5)
            p3.text = f"■ 보유 규모: {c['rooms']}타석 운영" if c.get('rooms', 0) > 0 else "■ 상태: 상업용 매장 미등록"
            p3.font.size = Pt(8.5)
            p3.font.color.rgb = self.c_charcoal
            
            p4 = tf_body.add_paragraph()
            p4.space_before = Pt(5)
            p4.text = f"■ 특징: {c.get('features', '-')}"
            p4.font.size = Pt(8.5)
            p4.font.color.rgb = self.c_slate
            
        self._add_source_footer(s7, "Small Enterprise Market Service & Kakao Map Local POI Survey")

        # ---------------------------------------------------------------------
        # Slide 8: 5대 지표 종합 평가
        # ---------------------------------------------------------------------
        s8 = self.prs.slides.add_slide(self.blank_layout)
        self._add_mckinsey_header(s8, "5. 입지 최적성 종합 평가", f"5대 다이아몬드 스코어링 총점 {score['total_score']}점({score['grade']}등급)으로 출점 최우선 추천 판정")
        
        if 'radar_score' in charts and os.path.exists(charts['radar_score']):
            s8.shapes.add_picture(charts['radar_score'], Inches(0.6), Inches(1.55), width=Inches(5.6))
            
        tb8 = s8.shapes.add_textbox(Inches(6.4), Inches(1.55), Inches(6.3), Inches(5.4))
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
            r1.text = f"■ {iname}: "
            r1.font.bold = True
            r1.font.size = Pt(11)
            r1.font.color.rgb = self.c_mck_navy
            r2 = p.add_run()
            r2.text = f"{iscore}점 / {imax}점 만점"
            r2.font.bold = True
            r2.font.size = Pt(11)
            r2.font.color.rgb = self.c_mck_teal
            p_desc = tf8.add_paragraph()
            p_desc.text = f"   ↳ 산출 근거: {idesc}"
            p_desc.font.size = Pt(9)
            p_desc.font.color.rgb = self.c_slate
            
        p_res = tf8.add_paragraph()
        p_res.space_before = Pt(10)
        r_res = p_res.add_run()
        r_res.text = f"★ 종합 판정: 총점 {score['total_score']}점 ({score['grade_desc']})"
        r_res.font.bold = True
        r_res.font.size = Pt(12)
        r_res.font.color.rgb = self.c_red
        
        self._add_source_footer(s8, "MYPARK 5-Dimension Diamond Scoring Methodology (22+25+15+15+20=97.0)")

        # ---------------------------------------------------------------------
        # Slide 9: 월 예상 매출
        # ---------------------------------------------------------------------
        s9 = self.prs.slides.add_slide(self.blank_layout)
        m_scen = fin['monthly_scenarios']
        self._add_mckinsey_header(s9, "6. 사업 타당성 분석 - 매출 추정", f"10타석 기준 보편 가동 시 월매출 {m_scen['moderate']['total_revenue']//10000:,}만원(연간 5.2억원) 달성 전망")
        
        table_s9 = s9.shapes.add_table(4, 7, Inches(0.6), Inches(2.0), Inches(12.133), Inches(2.8)).table
        col_w9 = [Inches(1.3), Inches(1.6), Inches(1.4), Inches(1.4), Inches(1.4), Inches(2.3), Inches(2.733)]
        for c_idx, w in enumerate(col_w9):
            table_s9.columns[c_idx].width = w
            
        h9 = ['구분', '타석 이용료', '용품(10%)', '카페(5%)', '레슨(3%)', '월 총매출 합계', '비고 (1일 이용자)']
        for col_idx, h in enumerate(h9):
            self._format_cell(table_s9.cell(0, col_idx), h, font_size=10, bold=True, color=self.c_white, bg_color=self.c_mck_navy)
            
        for row_idx, k in enumerate(['conservative', 'moderate', 'optimistic']):
            sc = m_scen[k]
            r = row_idx + 1
            bg_c = self.c_box_bg if row_idx % 2 == 1 else self.c_white
            self._format_cell(table_s9.cell(r, 0), sc['scenario_name'], font_size=9.5, bold=True, color=self.c_mck_navy, bg_color=bg_c)
            self._format_cell(table_s9.cell(r, 1), f"{sc['room_revenue']:,}원", font_size=9.5, color=self.c_charcoal, bg_color=bg_c)
            self._format_cell(table_s9.cell(r, 2), f"{sc['goods_revenue']:,}원", font_size=9.5, color=self.c_charcoal, bg_color=bg_c)
            self._format_cell(table_s9.cell(r, 3), f"{sc['cafe_revenue']:,}원", font_size=9.5, color=self.c_charcoal, bg_color=bg_c)
            self._format_cell(table_s9.cell(r, 4), f"{sc['lesson_revenue']:,}원", font_size=9.5, color=self.c_charcoal, bg_color=bg_c)
            self._format_cell(table_s9.cell(r, 5), f"{sc['total_revenue']:,}원", font_size=10, bold=True, color=self.c_mck_navy, bg_color=bg_c)
            self._format_cell(table_s9.cell(r, 6), f"1일 {sc['daily_users']}명 (월 {sc['monthly_users']:,}명)", font_size=9.5, color=self.c_slate, bg_color=bg_c)
            
        self._add_source_footer(s9, "Base Assumptions: 18 Holes 8,000 KRW, Secondary Sales 18%, 30 Operating Days/Month")

        # ---------------------------------------------------------------------
        # Slide 10: 예상 운영 비용
        # ---------------------------------------------------------------------
        s10 = self.prs.slides.add_slide(self.blank_layout)
        self._add_mckinsey_header(s10, "6. 사업 타당성 분석 - 비용 구조", "월 고정·변동비 2,246만원 지출로 보편 가동 시 높은 영업이익률(48.6%) 확보")
        
        table_s10 = s10.shapes.add_table(5, 5, Inches(0.6), Inches(2.0), Inches(12.133), Inches(3.6)).table
        col_w10 = [Inches(2.2), Inches(1.9), Inches(1.9), Inches(1.9), Inches(4.233)]
        for c_idx, w in enumerate(col_w10):
            table_s10.columns[c_idx].width = w
            
        h10 = ['비용 구분', '보수적 시나리오', '보편적 시나리오', '긍정적 시나리오', '세부 산출 내역']
        for col_idx, h in enumerate(h10):
            self._format_cell(table_s10.cell(0, col_idx), h, font_size=10, bold=True, color=self.c_white, bg_color=self.c_mck_navy)
            
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
            bg_col = RGBColor(241, 245, 249) if is_last else (self.c_box_bg if row_idx % 2 == 1 else self.c_white)
            txt_col = self.c_mck_navy if is_last else self.c_charcoal
            
            self._format_cell(table_s10.cell(r, 0), r_data[0], font_size=9.5, bold=is_last, color=txt_col, bg_color=bg_col)
            self._format_cell(table_s10.cell(r, 1), r_data[1], font_size=9.5, bold=is_last, color=txt_col, bg_color=bg_col)
            self._format_cell(table_s10.cell(r, 2), r_data[2], font_size=9.5, bold=is_last, color=txt_col, bg_color=bg_col)
            self._format_cell(table_s10.cell(r, 3), r_data[3], font_size=9.5, bold=is_last, color=txt_col, bg_color=bg_col)
            self._format_cell(table_s10.cell(r, 4), r_data[4], font_size=9, bold=is_last, color=txt_col, bg_color=bg_col, align=PP_ALIGN.LEFT)
            
        self._add_source_footer(s10, "MYPARK Standard Operating Cost Model")

        # ---------------------------------------------------------------------
        # Slide 11: 5개년 손익 예측 및 BEP 회수 분석
        # ---------------------------------------------------------------------
        s11 = self.prs.slides.add_slide(self.blank_layout)
        self._add_mckinsey_header(s11, "6. 손익 예측 및 BEP 분석", "기기당 1일 0.8회전 달성 시 BEP 돌파 및 18.1개월 내 순투자금 3.86억원 전액 회수")
        
        if 'profit_forecast' in charts and os.path.exists(charts['profit_forecast']):
            s11.shapes.add_picture(charts['profit_forecast'], Inches(0.6), Inches(1.55), width=Inches(6.8))
            
        mod_1y = fin['forecast_5year']['moderate'][0]
        mod_5y = fin['forecast_5year']['moderate'][4]
        
        c_kpi1 = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.6), Inches(1.55), Inches(5.1), Inches(2.2))
        c_kpi1.fill.solid()
        c_kpi1.fill.fore_color.rgb = self.c_box_bg
        c_kpi1.line.color.rgb = self.c_line
        tf_k1 = c_kpi1.text_frame
        tf_k1.word_wrap = True
        tf_k1.margin_left = tf_k1.margin_right = Inches(0.16)
        p = tf_k1.paragraphs[0]
        p.text = "■ 연간 실적 전망 (보편 시나리오)"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = self.c_mck_navy
        p2 = tf_k1.add_paragraph()
        p2.space_before = Pt(4)
        p2.text = (
            f"• 1년차: 연매출 {mod_1y['total_revenue']//100000000:.1f}억원 / 영업이익 {mod_1y['operating_profit']//100000000:.1f}억원\n"
            f"• 5년차: 연매출 {mod_5y['total_revenue']//100000000:.1f}억원 / 영업이익 {mod_5y['operating_profit']//100000000:.1f}억원\n"
            f"• 연평균 영업이익률: 약 48.6% (안정적 고수익 구조)"
        )
        p2.font.size = Pt(9)
        p2.font.color.rgb = self.c_charcoal
        
        c_kpi2 = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.6), Inches(3.95), Inches(5.1), Inches(2.6))
        c_kpi2.fill.solid()
        c_kpi2.fill.fore_color.rgb = self.c_box_bg
        c_kpi2.line.color.rgb = self.c_mck_teal
        c_kpi2.line.width = Pt(1.2)
        tf_k2 = c_kpi2.text_frame
        tf_k2.word_wrap = True
        tf_k2.margin_left = tf_k2.margin_right = Inches(0.16)
        p = tf_k2.paragraphs[0]
        p.text = "■ 손익분기점(BEP) 및 투자금 회수 기간"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = self.c_mck_teal
        p2 = tf_k2.add_paragraph()
        p2.space_before = Pt(4)
        p2.text = (
            f"• 손익분기점(BEP): 기기(타석)당 1일 단 0.8회전\n"
            f"  ↳ 매장 전체 1일 8명(월 240명), 월매출 약 1,940만원 달성 시 BEP 돌파\n"
            f"• 순투자금 회수: 초기 순투자금 약 {fin['investment']['total_capex']//100000000:.2f}억원 기준\n"
            f"  ↳ 보편 가동 시 약 {fin['investment']['payback_months_moderate']:.1f}개월 만에 전액 회수"
        )
        p2.font.size = Pt(9)
        p2.font.color.rgb = self.c_charcoal
        
        self._add_source_footer(s11, f"CAPEX {fin['investment']['total_capex']//100000000:.2f} Billion KRW / Compound Growth Rate 2% p.a.")

        # ---------------------------------------------------------------------
        # Slide 12: 종합 결론 및 사업 타당성 최종 평가 (맥킨지 클래식 레이아웃)
        # ---------------------------------------------------------------------
        s12 = self.prs.slides.add_slide(self.blank_layout)
        self._add_mckinsey_header(s12, "7. 종합 결론 및 사업 타당성 최종 평가", "반경 3km 내 7.2만 시니어 배후 수요와 주간 풀가동으로 18개월 내 투자금 전액 회수 가능")
        
        kpis = [
            ("배후 시니어 인구", f"{demo['senior_50_plus']:,}명", f"({demo['senior_ratio']}% 점유)"),
            ("예상 월 영업이익", f"{fin['monthly_scenarios']['moderate']['operating_profit']//10000:,}만원", "(영업이익률 48.6%)"),
            ("손익분기점 (BEP)", "타석당 0.8회전", "(월 240명 시 돌파)"),
            ("순투자금 회수", f"약 {fin['investment']['payback_months_moderate']:.1f}개월", f"({fin['investment']['total_capex']//100000000:.2f}억원 기준)")
        ]
        for i, (title, val, sub) in enumerate(kpis):
            x = Inches(0.6 + (i * 3.08))
            rect = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.55), Inches(2.9), Inches(1.1))
            rect.fill.solid()
            rect.fill.fore_color.rgb = self.c_box_bg
            rect.line.color.rgb = self.c_line
            rect.line.width = Pt(1)
            tf_k = rect.text_frame
            tf_k.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf_k.margin_left = tf_k.margin_right = Inches(0.12)
            p_t = tf_k.paragraphs[0]
            p_t.text = title
            p_t.font.size = Pt(9)
            p_t.font.color.rgb = self.c_slate
            p_v = tf_k.add_paragraph()
            p_v.text = f"{val}  {sub}"
            p_v.font.size = Pt(12)
            p_v.font.bold = True
            p_v.font.color.rgb = self.c_mck_navy
            
        # 좌측: 가맹점 3대 핵심 경쟁력
        rect_l = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(2.8), Inches(5.9), Inches(4.2))
        rect_l.fill.solid()
        rect_l.fill.fore_color.rgb = self.c_white
        rect_l.line.color.rgb = self.c_line
        rect_l.line.width = Pt(1.2)
        
        top_bar_l = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(2.8), Inches(5.9), Inches(0.45))
        top_bar_l.fill.solid()
        top_bar_l.fill.fore_color.rgb = self.c_mck_navy
        top_bar_l.line.fill.background()
        tf_tbl = top_bar_l.text_frame
        tf_tbl.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_tbl = tf_tbl.paragraphs[0]
        p_tbl.text = "【 가맹점 출점 3대 핵심 경쟁력 】"
        p_tbl.font.size = Pt(11)
        p_tbl.font.bold = True
        p_tbl.font.color.rgb = self.c_white
        
        tb_l_body = s12.shapes.add_textbox(Inches(0.7), Inches(3.35), Inches(5.7), Inches(3.5))
        tf_lb = tb_l_body.text_frame
        tf_lb.word_wrap = True
        
        f_points = [
            ("1. 주간 유휴시간 제로 (100% 예약 풀가동)", "• 일반 스크린골프 손님이 없는 '평일 낮 10시~오후 5시'에\n  반경 3km 내 7.2만 시니어 동호회 모임으로 100% 가동"),
            ("2. 10타석 플래그십 상위 20% 시장 독점", "• 노후 소형 1~2타석 매장과 차별화된 쾌적한 카페형 라운지 및\n  10타석 대규모로 지역 내 독점 랜드마크화"),
            ("3. 빠른 원금 회수 및 고수익성", f"• 월 순영업이익 약 {fin['monthly_scenarios']['moderate']['operating_profit']//10000:,}만원(이익률 48.6%) 달성으로\n  약 1년 6개월({fin['investment']['payback_months_moderate']:.1f}개월) 내 순투자금 전액 회수")
        ]
        for idx, (title, desc) in enumerate(f_points):
            p_t = tf_lb.add_paragraph() if idx > 0 else tf_lb.paragraphs[0]
            p_t.space_before = Pt(6) if idx > 0 else Pt(0)
            p_t.text = f"● {title}"
            p_t.font.size = Pt(10)
            p_t.font.bold = True
            p_t.font.color.rgb = self.c_mck_navy
            p_d = tf_lb.add_paragraph()
            p_d.text = f"  {desc}"
            p_d.font.size = Pt(8.5)
            p_d.font.color.rgb = self.c_charcoal
            
        # 우측: 건물주 및 상가 상생
        rect_r = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(2.8), Inches(5.9), Inches(4.2))
        rect_r.fill.solid()
        rect_r.fill.fore_color.rgb = self.c_white
        rect_r.line.color.rgb = self.c_line
        rect_r.line.width = Pt(1.2)
        
        top_bar_r = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(2.8), Inches(5.9), Inches(0.45))
        top_bar_r.fill.solid()
        top_bar_r.fill.fore_color.rgb = self.c_mck_teal
        top_bar_r.line.fill.background()
        tf_tbr = top_bar_r.text_frame
        tf_tbr.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_tbr = tf_tbr.paragraphs[0]
        p_tbr.text = "【 건물주 및 상가 상생 활성화 효과 】"
        p_tbr.font.size = Pt(11)
        p_tbr.font.bold = True
        p_tbr.font.color.rgb = self.c_white
        
        tb_r_body = s12.shapes.add_textbox(Inches(6.9), Inches(3.35), Inches(5.7), Inches(3.5))
        tf_rb = tb_r_body.text_frame
        tf_rb.word_wrap = True
        
        l_points = [
            ("1. 일 60~90명 액티브 시니어 지속 유입", "• 구매력 높은 지역 시니어 고객이 매일 건물을 방문하여\n  1층 식당, 카페, 병원 등 상가 타 점포 매출까지 동반 상승"),
            ("2. 공실 해소 및 5년 장기 우량 임대차", "• 마이파크와의 5년 이상 장기 임대차 계약 체결로\n  공실 리스크 제로 및 매월 안정적이고 우량한 월세 수익 보장"),
            ("3. 건물 전체의 자산 가치(Cap Rate) 상승", "• 안정적인 고수익 핵심 점포 입점에 따른 유동인구 증가 및\n  부동산 매매 가치 및 상가 자산 가치 동반 상승 견인")
        ]
        for idx, (title, desc) in enumerate(l_points):
            p_t = tf_rb.add_paragraph() if idx > 0 else tf_rb.paragraphs[0]
            p_t.space_before = Pt(6) if idx > 0 else Pt(0)
            p_t.text = f"● {title}"
            p_t.font.size = Pt(10)
            p_t.font.bold = True
            p_t.font.color.rgb = self.c_mck_teal
            p_d = tf_rb.add_paragraph()
            p_d.text = f"  {desc}"
            p_d.font.size = Pt(8.5)
            p_d.font.color.rgb = self.c_charcoal
            
        self._add_source_footer(s12, "McKinsey Executive Format | MYPARK Business Intelligence")
        
        os.makedirs(os.path.dirname(output_pptx_path), exist_ok=True)
        self.prs.save(output_pptx_path)
        print(f"[PPTX GENERATED] {output_pptx_path}")
        return output_pptx_path
