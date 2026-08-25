# -*- coding: utf-8 -*-
"""16:9 와이드 맥킨지 클래식 이그제큐티브(McKinsey Executive) PDF 보고서 생성기"""
import os
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_REGULAR = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'

current_dir = os.path.dirname(os.path.abspath(__file__))
font_reg_path = os.path.join(current_dir, 'fonts', 'MalgunGothic.ttf')
font_bold_path = os.path.join(current_dir, 'fonts', 'MalgunGothicBold.ttf')

if not os.path.exists(font_reg_path) and os.path.exists(r'C:\Windows\Fonts\malgun.ttf'):
    font_reg_path = r'C:\Windows\Fonts\malgun.ttf'
if not os.path.exists(font_bold_path) and os.path.exists(r'C:\Windows\Fonts\malgunbd.ttf'):
    font_bold_path = r'C:\Windows\Fonts\malgunbd.ttf'

if os.path.exists(font_reg_path):
    try:
        pdfmetrics.registerFont(TTFont('Malgun', font_reg_path))
        FONT_REGULAR = 'Malgun'
    except Exception:
        pass

if os.path.exists(font_bold_path):
    try:
        pdfmetrics.registerFont(TTFont('Malgun-Bold', font_bold_path))
        FONT_BOLD = 'Malgun-Bold'
    except Exception:
        FONT_BOLD = FONT_REGULAR
elif FONT_REGULAR == 'Malgun':
    FONT_BOLD = 'Malgun'


class PDFGenerator:
    """맥킨지 클래식 이그제큐티브 16:9 와이드 PDF 생성기"""
    
    def __init__(self):
        self.width = 960
        self.height = 540
        
        # 맥킨지 클래식 팔레트
        self.c_mck_navy = colors.HexColor('#002B49')
        self.c_mck_teal = colors.HexColor('#008080')
        self.c_charcoal = colors.HexColor('#1E293B')
        self.c_slate = colors.HexColor('#64748B')
        self.c_line = colors.HexColor('#CBD5E1')
        self.c_box_bg = colors.HexColor('#F8FAFC')
        self.c_white = colors.white
        self.c_red = colors.HexColor('#DC2626')

    def _draw_mckinsey_header(self, c, section_category, action_title):
        """맥킨지 2단 액션 타이틀 & 1pt 분할선"""
        c.setFont(FONT_BOLD, 8.5)
        c.setFillColor(self.c_slate)
        c.drawString(40, self.height - 30, section_category.upper())
        
        c.setFont(FONT_BOLD, 13)
        c.setFillColor(self.c_mck_navy)
        c.drawString(40, self.height - 48, action_title)
        
        c.setStrokeColor(self.c_line)
        c.setLineWidth(1)
        c.line(40, self.height - 56, self.width - 40, self.height - 56)

    def _draw_footer(self, c, source_text):
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_slate)
        c.drawRightString(self.width - 40, 16, f"* Source: {source_text}")

    def generate(self, data, output_pdf_path):
        site = data['site']
        demo = data['demographics']
        comm = data['commercial']
        fin = data['financials']
        score = data['scores']
        charts = data['charts']
        
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
        c = canvas.Canvas(output_pdf_path, pagesize=(self.width, self.height))
        
        # ---------------------------------------------------------------------
        # Page 1: 표지
        # ---------------------------------------------------------------------
        c.setFillColor(self.c_mck_navy)
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        
        c.setFillColor(self.c_mck_teal)
        c.rect(80, self.height - 120, self.width - 160, 2.5, fill=1, stroke=0)
        
        c.setFont(FONT_BOLD, 12)
        c.setFillColor(colors.HexColor('#6EE7B7'))
        c.drawString(80, self.height - 105, "MYPARK SCREEN PARK GOLF  |  EXECUTIVE FEASIBILITY STUDY")
        
        c.setFont(FONT_BOLD, 24)
        c.setFillColor(self.c_white)
        c.drawString(80, self.height - 165, f"{site.get('building_name', '사업지')} 상권 및 출점 타당성 분석 보고서")
        
        c.setFont(FONT_REGULAR, 11)
        c.setFillColor(colors.HexColor('#E2E8F0'))
        c.drawString(80, self.height - 198, f"대상 주소: {site['full_address']}  |  표준 모델: {site['rooms']}타석 ({site['area_pyeong']}평)")
        
        badges = [
            (80, "입지 최적성 등급", f"{score['grade']}등급 ({score['total_score']}점)", colors.HexColor('#6EE7B7')),
            (360, "예상 월 영업이익 (보편)", f"{fin['monthly_scenarios']['moderate']['operating_profit']//10000:,}만원/월", self.c_white),
            (640, "순투자금 회수 기간", f"약 {fin['investment']['payback_months_moderate']:.1f}개월", self.c_white)
        ]
        for bx, btitle, bval, bcol in badges:
            c.setFillColor(colors.HexColor('#0A233C'))
            c.setStrokeColor(self.c_mck_teal)
            c.setLineWidth(1)
            c.rect(bx, 60, 240, 75, fill=1, stroke=1)
            
            c.setFont(FONT_REGULAR, 9)
            c.setFillColor(self.c_slate)
            c.drawString(bx + 16, 115, btitle)
            
            c.setFont(FONT_BOLD, 12)
            c.setFillColor(bcol)
            c.drawString(bx + 16, 85, bval)
            
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 2: 사업지 개요 및 출점 점검 체크리스트
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "1. 사업지 개요 및 출점 요건", f"10타석 {site['area_pyeong']}평 규모 출점을 위한 4대 건축·인프라 현장 실측 기준")
        cards_p2 = [
            (40, 265, 425, 205, "■ 공간 및 유효 층고 요건", [
                f"• 대상 주소: {site['full_address']}",
                f"• 권장 면적: 전용 {site['area_pyeong']}평 (10타석 + 카페/락커룸 최적 배치)",
                f"• 층고 기준: {site['clear_height_spec']}",
                f"• 보/배관 간섭: 센서 투사 영역 및 스윙 궤적 내 장애물 사전 실측",
                f"• 권장 층수: 접근성 높은 지상 2~3층 권장 (쾌적한 지하 1층 가능)"
            ]),
            (495, 265, 425, 205, "■ 주차 및 차량 접근성 기준", [
                f"• 주차 요건: {site['parking_spec']}",
                f"• 고객 특성: 자차 이용 시니어 비중 80% 이상으로 편리한 진출입 필수",
                f"• 진입 여건: 램프 폭 및 회전각 여유 있는 자주식 주차장 최우선",
                f"• 도로 접면: 주요 간선도로 및 대단지 아파트 진입로 인접 우수",
                f"• 보행 동선: 대중교통(버스/지하철) 도보 5~10분 생활권"
            ]),
            (40, 48, 425, 205, "■ 건물 편의 및 승강기 설비", [
                f"• 고객 편의: {site['accessibility_spec']}",
                f"• 계단 여건: 계단 단차가 낮거나 완만한 진입 경사로 확보 필요",
                f"• 냉난방/환기: 개별 공조 및 고성능 환기 덕트 설치 공간 확인",
                f"• 소음/진동: 상하층 타 업종 간섭 방지 방음/흡음 설계 시공",
                f"• 쾌적성: 남녀 분리 청결 화장실 및 쾌적한 로비 라운지 구축"
            ]),
            (495, 48, 425, 205, "■ 인허가 및 건축물 용도", [
                f"• 적합 용도: {site['zoning_spec']}",
                f"• 지자체 체육시설: 체육시설의 설치·이용에 관한 법률 인허가 검토",
                f"• 소방 기준: 스프링클러, 비상유도등, 비상탈출구 완비 점검",
                f"• 전기 용량: 10타석 시뮬레이터 동시 가동 대비 30kW 이상 인입",
                f"• 정화조 용량: 일 최대 150명 이상 동시 이용 기준 충족 점검"
            ]),
        ]
        for cx, cy, cw, ch, ctitle, clines in cards_p2:
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.setLineWidth(1)
            c.rect(cx, cy, cw, ch, fill=1, stroke=1)
            
            c.setFont(FONT_BOLD, 10)
            c.setFillColor(self.c_mck_navy)
            c.drawString(cx + 14, cy + ch - 20, ctitle)
            
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_charcoal)
            y_offset = cy + ch - 42
            for line_txt in clines:
                c.drawString(cx + 14, y_offset, line_txt)
                y_offset -= 18
        self._draw_footer(c, "MYPARK Standard Facility Criteria & Architectural Survey")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 3: 배후 인구 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "2. 배후 인구 분석", f"사업지 반경 3km 내 18.8만 명({len(demo['dongs'])}개 행정동)의 풍부한 주거 배후 인구 형성")
        if 'map_radius' in charts and os.path.exists(charts['map_radius']):
            c.drawImage(charts['map_radius'], 40, 48, width=420, height=420, preserveAspectRatio=True)
            
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_navy)
        c.drawString(495, 460, f"■ 반경 3km 행정동별 인구 집계 현황 (총 {demo['total_pop']:,}명)")
        
        table_data_3 = [['행정구역(동)', '남자(명)', '여자(명)', '합계(명)']]
        for d in demo['dongs']:
            table_data_3.append([d['dong'], f"{d['male']:,}", f"{d['female']:,}", f"{d['total']:,}"])
        table_data_3.append(['합계 (3km 생활권)', f"{demo['male_pop']:,}", f"{demo['female_pop']:,}", f"{demo['total_pop']:,}"])
        
        t3 = Table(table_data_3, colWidths=[120, 100, 100, 105])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.c_mck_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.c_white),
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.c_line),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (0, -1), (-1, -1), self.c_mck_navy),
            ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ]))
        t3.wrapOn(c, 495, 48)
        t3.drawOn(c, 495, 440 - (len(table_data_3) * 23))
        self._draw_footer(c, f"KOSIS National Statistics Portal ({demo['base_date']})")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 4: 메인 타겟 장·노년층 인구 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "2. 타겟 시니어 인구 분석", f"50대 이상 골든 시니어 7.2만 명({demo['senior_ratio']}%)으로 평일 주간 100% 예약 풀가동 최적")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 260, 380, 210, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(54, 445, "■ 핵심 타겟: 50대 이상 여성 시니어 (3.8만 명)")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(54, 420, f"• 여성 시니어 인구: 약 {demo['senior_50_female']:,}명 (시니어의 53.0%)")
        c.drawString(54, 395, "• 소비 특성: 평일 낮 시간대(10~17시) 주부 모임 주도")
        c.drawString(54, 370, "• 락인 효과: 4인 1팀 고정 리그전으로 월 정기 결제")
        c.drawString(54, 345, "• 파생 소비: 게임 후 인근 카페/식당 연계 지출 활발")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_mck_teal)
        c.setLineWidth(1.2)
        c.rect(40, 48, 380, 200, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_teal)
        c.drawString(54, 225, "■ 시니어 상권 사업화 시사점")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(54, 200, f"• 시니어 인구 집적도: {demo['senior_ratio']}%의 최상급 골든 배후지")
        c.drawString(54, 175, "• 사계절 가동성: 야외 파크골프장의 날씨 한계 대체")
        c.drawString(54, 150, "• 주간 가동 극대화: 일반 골프 유휴 시간 100% 가동")
        c.drawString(54, 125, "• 진입 장벽 제로: 단 1개의 채로 누구나 즉시 입문")
        
        table_data_4 = [['연령대', '남자(명)', '여자(명)', '합계(명)']]
        for a in demo['age_distribution']:
            table_data_4.append([a['age_group'], f"{int(a['male']):,}", f"{int(a['female']):,}", f"{int(a['total']):,}"])
        table_data_4.append(['총계 (50대이상)', f"{demo['senior_50_plus'] - demo['senior_50_female']:,}", f"{demo['senior_50_female']:,}", f"{demo['senior_50_plus']:,}"])
        
        t4 = Table(table_data_4, colWidths=[120, 110, 110, 120])
        t4.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.c_mck_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.c_white),
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.c_line),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (0, -1), (-1, -1), self.c_mck_navy),
            ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ]))
        t4.wrapOn(c, 460, 48)
        t4.drawOn(c, 460, 465 - (len(table_data_4) * 25))
        self._draw_footer(c, f"KOSIS Demographic Database ({demo['base_date']})")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 5: 소상공인365/BASA 상권 실측 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "3. 상권 실측 분석 (소상공인365/BASA)", "주거지역 93% 밀집 상권 및 유사 골프업종 상위 20% 월매출 6,251만원 시장 타겟팅")
        rev_st = comm.get('revenue_structure', {})
        top20_str = f"{rev_st.get('top_20_sales', 62510000)//10000:,}만원"
        bot20_str = f"{rev_st.get('bottom_20_sales', 3020000)//10000:,}만원"
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 340, 260, 120, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(50, 440, "■ 유사 골프업종 수익구조 격차 (BASA)")
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_charcoal)
        c.drawString(50, 418, f"• 상위 20% 매출: {top20_str} /월 (대형 최신)")
        c.drawString(50, 400, f"• 하위 20% 매출: {bot20_str} /월 (노후 소형)")
        c.drawString(50, 382, "★ 마이파크 10타석 플래그십은 상위 시장 점유")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 205, 260, 125, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(50, 310, "■ 핵심 고객층 및 이용 패턴")
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_charcoal)
        c.drawString(50, 288, "• 주 이용층: 50대 남성 & 여성 (구매력 최상)")
        c.drawString(50, 270, "• 최근 변화: 3040대 직장인/가족 유입 증가")
        c.drawString(50, 252, "• 충성도: 주 2~3회 정기 방문 락인(Lock-in)")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_mck_teal)
        c.setLineWidth(1.2)
        c.rect(40, 48, 260, 145, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_mck_teal)
        c.drawString(50, 172, "■ 피크 요일 및 주간 운영 전략")
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_charcoal)
        c.drawString(50, 150, "• 최고 매출 요일: 토요일(친목) & 월요일(동호회)")
        c.drawString(50, 132, "• 주거형 상권 전략: 충성 고객 품질/편의성 중심")
        c.drawString(50, 114, "• 평일 주간(10~17시) 주부 모임으로 유휴 제로")
        
        infra = comm.get('infra', {})
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(320, 340, 600, 120, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_navy)
        c.drawString(335, 440, f"■ {comm.get('region_title', '사업지')} 주변 인프라 및 교통망 실측 현황")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(335, 415, f"• 주변 시설: 관공서 {infra.get('관공서', 8)}개  |  교육기관 {infra.get('교육기관', 15)}개  |  금융기관 {infra.get('금융기관', 18)}개")
        c.drawString(335, 395, f"• 대중 교통: 버스정류장 {infra.get('버스정류장', 48)}개 노선망  |  지하철 {infra.get('지하철', '분당선 서현역')}")
        c.drawString(335, 375, "• 상권 구성: 주거지역 93% 압도적 밀집으로 탄탄한 배후 생활권 형성")
        
        if 'sales_trend' in charts and os.path.exists(charts['sales_trend']):
            c.drawImage(charts['sales_trend'], 320, 48, width=600, height=275, preserveAspectRatio=True)
            
        self._draw_footer(c, "Small Enterprise and Market Service (BASA) & NICE BizMap")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 6: 업종별 성장률 및 골프 특화도 실측
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "3. 업종 성장률 및 골프 특화도", "골프용품 매출성장률 1위(+182.4%) 및 전국 평균 대비 2.3배 높은 골프 특화 상권")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 265, 425, 205, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 445, "■ 서현1동 매출 증가율 TOP 5 (소상공인365 실측)")
        growths = comm.get('top_growth_industries', [])
        y_g = 420
        for g in growths:
            c.setFont(FONT_BOLD if g['rank'] == 1 else FONT_REGULAR, 8.5)
            c.setFillColor(self.c_red if g['rank'] == 1 else self.c_charcoal)
            c.drawString(56, y_g, f"• {g['rank']}위 : {g['name']}  ({g['growth']}) - {g['status']}")
            y_g -= 20
            
        golf_den = comm.get('golf_industry_density', {})
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, 265, 425, 205, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, 445, "■ 지역 골프 문화 및 유사 레저 밀집도 (BASA 실측)")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(511, 415, f"• 서현1동 내 스크린골프 점포: {golf_den.get('store_count', 10)}개 (전체 {golf_den.get('total_stores_in_dong', 1526)}개 중)")
        c.drawString(511, 390, f"• 스크린골프 업종 비중: {golf_den.get('density_ratio', 0.7)}% (전국 평균 {golf_den.get('national_avg_density', 0.3)}% 대비 2.3배)")
        c.drawString(511, 365, "• 전국 평균 대비 2.3배 밀집된 '골프·파크골프 소비 문화 특화 상권'")
        c.drawString(511, 340, f"• 성장 단계: {golf_den.get('growth_stage', '집중 성장 단계')}")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 425, 205, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 230, "■ 요일 및 시간대별 매출 패턴 (NICE비즈맵 실측)")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 200, f"• 피크 요일: 월요일 ({comm['day_distribution']['월']}%) 최고치 (주간 동호회 정기 모임)")
        c.drawString(56, 175, f"• 주간 비중: 10~17시 이용 비중이 전체의 {comm['time_distribution']['주간_10_17시_비중']}% 압도적")
        c.drawString(56, 150, "• 일반 스크린골프(야간 위주)와 달리 낮 시간대 풀가동으로 회전율 2배")
        c.drawString(56, 125, f"• 주말 가동률: 주말 평균 비중 {comm['day_distribution']['주말평균비중']}%로 주 7일 고른 수익")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_mck_teal)
        c.setLineWidth(1.2)
        c.rect(495, 48, 425, 205, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_teal)
        c.drawString(511, 230, "■ 마이파크 출점 종합 전략적 시사점")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(511, 200, "• 수요 검증 완료: 골프용품 매출 성장 1위(+182.4%) 상권으로 검증된 소비력")
        c.drawString(511, 175, "• 공급 격차 점유: 노후 2~3타석 매장 대비 10타석 플래그십으로 상위 시장 독점")
        c.drawString(511, 150, "• 복합 문화 공간: 카페형 라운지 및 파크골프 용품 샵 연계로 객단가 극대화")
        c.drawString(511, 125, "• 상권 락인(Lock-in): 주거지역 93% 배후 고정 고객 대상 월회원제 정착")
        
        self._draw_footer(c, "Small Enterprise 365, NICE BizMap & SK Telecom Geovision Big Data")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 7: 주변 경쟁 매장 실측 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "4. 경쟁 환경 실측 분석", "반경 3km 내 스크린 파크골프 전문 매장 공급 부족으로 10타석 대규모 플래그십 선점 기회")
        comps = comm.get('competitors', [])
        card_w = 205
        gap = 18
        start_x = 40
        for idx, comp in enumerate(comps[:4]):
            cur_x = start_x + (idx * (card_w + gap))
            
            c.setFillColor(self.c_mck_navy)
            c.rect(cur_x, 415, card_w, 42, fill=1, stroke=0)
            c.setFont(FONT_BOLD, 9)
            c.setFillColor(self.c_white)
            c_name = str(comp['name'])
            if len(c_name) > 12:
                c.drawCentredString(cur_x + card_w/2, 440, c_name[:12])
                c.drawCentredString(cur_x + card_w/2, 424, c_name[12:])
            else:
                c.drawCentredString(cur_x + card_w/2, 432, c_name)
            
            c.setFillColor(colors.HexColor('#F1F5F9'))
            c.setStrokeColor(self.c_line)
            c.rect(cur_x, 345, card_w, 65, fill=1, stroke=1)
            c.setFont(FONT_BOLD, 10.5)
            c.setFillColor(self.c_mck_navy)
            rooms_label = f"{comp.get('rooms', 0)}타석 규모" if comp.get('rooms', 0) > 0 else "1호점 선점 대상"
            c.drawCentredString(cur_x + card_w/2, 385, rooms_label)
            c.setFont(FONT_REGULAR, 7.5)
            c.setFillColor(self.c_slate)
            c.drawCentredString(cur_x + card_w/2, 362, f"[{comp.get('status', '실측완료')}] {comp.get('system', '스크린 시스템')[:16]}")
            
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(cur_x, 48, card_w, 290, fill=1, stroke=1)
            
            c.setFont(FONT_REGULAR, 7.5)
            c.setFillColor(self.c_charcoal)
            c.drawString(cur_x + 8, 315, "■ 주소:")
            addr_str = str(comp['address'])
            c.drawString(cur_x + 8, 300, addr_str[:17])
            if len(addr_str) > 17:
                c.drawString(cur_x + 8, 286, addr_str[17:34])
            if len(addr_str) > 34:
                c.drawString(cur_x + 8, 272, addr_str[34:])
                
            c.setFillColor(self.c_mck_teal)
            c.setFont(FONT_BOLD, 7.5)
            sys_str = f"■ 시스템: {comp['system']}"
            c.drawString(cur_x + 8, 250, sys_str[:17])
            if len(sys_str) > 17:
                c.drawString(cur_x + 8, 236, sys_str[17:])
            
            c.setFillColor(self.c_charcoal)
            c.setFont(FONT_REGULAR, 7.5)
            rooms_str = f"■ 규모: {comp['rooms']}타석 운영" if comp.get('rooms', 0) > 0 else "■ 상태: 상업용 매장 미등록"
            c.drawString(cur_x + 8, 210, rooms_str)
            
            c.setFillColor(self.c_slate)
            c.drawString(cur_x + 8, 180, "■ 특징:")
            feat_str = str(comp.get('features', '-'))
            c.drawString(cur_x + 8, 164, feat_str[:17])
            if len(feat_str) > 17:
                c.drawString(cur_x + 8, 150, feat_str[17:34])
            if len(feat_str) > 34:
                c.drawString(cur_x + 8, 136, feat_str[34:])
            
        self._draw_footer(c, "Small Enterprise Market Service & Kakao Map Local POI Survey")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 8: 5대 지표 종합 평가
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "5. 입지 최적성 종합 평가", f"5대 다이아몬드 스코어링 총점 {score['total_score']}점({score['grade']}등급)으로 출점 최우선 추천 판정")
        if 'radar_score' in charts and os.path.exists(charts['radar_score']):
            c.drawImage(charts['radar_score'], 40, 48, width=440, height=425, preserveAspectRatio=True)
            
        indicators = [
            ("1) 골든 시니어 집적도", score['scores']['senior_population'], 25, "반경 3km 내 50대 이상 시니어 72,400명 (38.4%) 실측"),
            ("2) 접근성 및 주차 인프라", score['scores']['accessibility_parking'], 25, "10타석 표준 주차 10~12대 확보 권장 기준 충족 가정치"),
            ("3) 공간 적합성 및 임대료", score['scores']['space_efficiency'], 15, "권장 유효 층고 2.8m 이상 센서 작동 물리 규격 기준 충족"),
            ("4) 수요 공급 갭 (블루오션)", score['scores']['supply_gap'], 15, "반경 3km 내 전문 매장 1~2곳으로 공급 부족 (1호점 선점)"),
            ("5) 지역 소비력 및 여가지출", score['scores']['commercial_spending'], 20, "스포츠/여가 월평균 카드 매출 2,150만원 소비력 우수"),
        ]
        y_ind = 440
        for iname, iscore, imax, idesc in indicators:
            c.setFont(FONT_BOLD, 9.5)
            c.setFillColor(self.c_mck_navy)
            c.drawString(500, y_ind, f"■ {iname}: ")
            c.setFillColor(self.c_mck_teal)
            c.drawString(650, y_ind, f"{iscore}점 / {imax}점 만점")
            
            c.setFont(FONT_REGULAR, 8)
            c.setFillColor(self.c_slate)
            c.drawString(510, y_ind - 16, f"↳ 산출 근거: {idesc}")
            y_ind -= 50
            
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_red)
        c.drawString(500, y_ind - 10, f"★ 종합 판정: 총점 {score['total_score']}점 ({score['grade_desc']})")
        self._draw_footer(c, "MYPARK 5-Dimension Diamond Scoring Methodology (22+25+15+15+20=97.0)")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 9: 월 예상 매출
        # ---------------------------------------------------------------------
        m_scen = fin['monthly_scenarios']
        self._draw_mckinsey_header(c, "6. 사업 타당성 분석 - 매출 추정", f"10타석 기준 보편 가동 시 월매출 {m_scen['moderate']['total_revenue']//10000:,}만원(연간 5.2억원) 달성 전망")
        
        table_data_9 = [['구분', '타석 이용료', '용품(10%)', '카페(5%)', '레슨(3%)', '월 총매출 합계', '비고 (1일 이용자)']]
        for k in ['conservative', 'moderate', 'optimistic']:
            sc = m_scen[k]
            table_data_9.append([
                sc['scenario_name'],
                f"{sc['room_revenue']:,}원",
                f"{sc['goods_revenue']:,}원",
                f"{sc['cafe_revenue']:,}원",
                f"{sc['lesson_revenue']:,}원",
                f"{sc['total_revenue']:,}원",
                f"1일 {sc['daily_users']}명 (월 {sc['monthly_users']:,}명)"
            ])
        t9 = Table(table_data_9, colWidths=[100, 120, 105, 105, 105, 170, 175])
        t9.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.c_mck_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.c_white),
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.c_line),
            ('TEXTCOLOR', (5, 1), (5, -1), self.c_mck_navy),
            ('FONTNAME', (5, 1), (5, -1), FONT_BOLD),
        ]))
        t9.wrapOn(c, 40, 48)
        t9.drawOn(c, 40, 300)
        self._draw_footer(c, "Base Assumptions: 18 Holes 8,000 KRW, Secondary Sales 18%, 30 Operating Days/Month")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 10: 예상 운영 비용
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "6. 사업 타당성 분석 - 비용 구조", "월 고정·변동비 2,246만원 지출로 보편 가동 시 높은 영업이익률(48.6%) 확보")
        c_sc = m_scen['conservative']
        m_sc = m_scen['moderate']
        o_sc = m_scen['optimistic']
        table_data_10 = [
            ['비용 구분', '보수적 시나리오', '보편적 시나리오', '긍정적 시나리오', '세부 산출 내역'],
            ['인건비 + 임대료', f"{c_sc['labor_cost']+c_sc['rent_cost']:,}원", f"{m_sc['labor_cost']+m_sc['rent_cost']:,}원", f"{o_sc['labor_cost']+o_sc['rent_cost']:,}원", f"인력 {fin['staff_count']}명(월 750만) / 임대료 {fin['monthly_rent']//10000:,}만원/월"],
            ['원가 3종 + 카드수수료', f"{c_sc['goods_cost']+c_sc['cafe_cost']+c_sc['lesson_cost']+c_sc['card_fee']:,}원", f"{m_sc['goods_cost']+m_sc['cafe_cost']+m_sc['lesson_cost']+m_sc['card_fee']:,}원", f"{o_sc['goods_cost']+o_sc['cafe_cost']+o_sc['lesson_cost']+o_sc['card_fee']:,}원", "용품60%, 식음50%, 레슨80%, 카드2%"],
            ['매장운영비 + 렌탈/마케팅', f"{c_sc['store_ops_cost']+c_sc['rental_cost']+c_sc['marketing_cost']:,}원", f"{m_sc['store_ops_cost']+m_sc['rental_cost']+m_sc['marketing_cost']:,}원", f"{o_sc['store_ops_cost']+o_sc['rental_cost']+o_sc['marketing_cost']:,}원", "수도광열, 소모품, 공청기, 보험 등"],
            ['월 총 비용 합계', f"{c_sc['total_cost']:,}원", f"{m_sc['total_cost']:,}원", f"{o_sc['total_cost']:,}원", "부가가치세(VAT) 별도 기준"]
        ]
        t10 = Table(table_data_10, colWidths=[150, 135, 135, 135, 325])
        t10.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.c_mck_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.c_white),
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ALIGN', (0, 0), (3, -1), 'CENTER'),
            ('ALIGN', (4, 0), (4, 0), 'CENTER'),
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.c_line),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F1F5F9')),
            ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ]))
        t10.wrapOn(c, 40, 48)
        t10.drawOn(c, 40, 260)
        self._draw_footer(c, "MYPARK Standard Operating Cost Model")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 11: 5개년 손익 예측 및 BEP 회수 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "6. 손익 예측 및 BEP 분석", "기기당 1일 0.8회전 달성 시 BEP 돌파 및 18.1개월 내 순투자금 3.86억원 전액 회수")
        if 'profit_forecast' in charts and os.path.exists(charts['profit_forecast']):
            c.drawImage(charts['profit_forecast'], 40, 48, width=500, height=420, preserveAspectRatio=True)
            
        mod_1y = fin['forecast_5year']['moderate'][0]
        mod_5y = fin['forecast_5year']['moderate'][4]
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(560, 265, 360, 200, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_navy)
        c.drawString(576, 445, "■ 연간 실적 전망 (보편 시나리오)")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(576, 415, f"• 1년차: 연매출 {mod_1y['total_revenue']//100000000:.1f}억원 / 영업이익 {mod_1y['operating_profit']//100000000:.1f}억원")
        c.drawString(576, 390, f"• 5년차: 연매출 {mod_5y['total_revenue']//100000000:.1f}억원 / 영업이익 {mod_5y['operating_profit']//100000000:.1f}억원")
        c.drawString(576, 365, "• 연평균 영업이익률: 약 48.6% (안정적 고수익 구조)")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_mck_teal)
        c.setLineWidth(1.2)
        c.rect(560, 48, 360, 205, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_teal)
        c.drawString(576, 230, "■ 손익분기점(BEP) 및 투자금 회수 기간")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(576, 205, "• 손익분기점(BEP): 기기(타석)당 1일 단 0.8회전")
        c.drawString(576, 185, "  ↳ 1일 8명(월 240명), 월매출 약 1,940만원 시 돌파")
        c.drawString(576, 160, f"• 순투자금 회수: 초기 순투자금 약 {fin['investment']['total_capex']//100000000:.2f}억원 기준")
        c.drawString(576, 140, f"  ↳ 보편 가동 시 약 {fin['investment']['payback_months_moderate']:.1f}개월 만에 전액 회수")
        self._draw_footer(c, f"CAPEX {fin['investment']['total_capex']//100000000:.2f} Billion KRW / Compound Growth Rate 2% p.a.")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 12: 종합 결론 및 사업 타당성 최종 평가
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "7. 종합 결론 및 사업 타당성 최종 평가", "반경 3km 내 7.2만 시니어 배후 수요와 주간 풀가동으로 18개월 내 투자금 전액 회수 가능")
        
        kpis = [
            (40, "배후 시니어 인구", f"{demo['senior_50_plus']:,}명", f"({demo['senior_ratio']}% 점유)"),
            (265, "예상 월 영업이익", f"{fin['monthly_scenarios']['moderate']['operating_profit']//10000:,}만원", "(이익률 48.6%)"),
            (490, "손익분기점 (BEP)", "타석당 0.8회전", "(월 240명 시 돌파)"),
            (715, "순투자금 회수", f"약 {fin['investment']['payback_months_moderate']:.1f}개월", f"({fin['investment']['total_capex']//100000000:.2f}억원)"),
        ]
        for bx, btitle, bval, bsub in kpis:
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(bx, 395, 205, 75, fill=1, stroke=1)
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_slate)
            c.drawString(bx + 12, 448, btitle)
            c.setFont(FONT_BOLD, 10)
            c.setFillColor(self.c_mck_navy)
            c.drawString(bx + 12, 420, f"{bval}  {bsub}")
            
        # 좌측 박스
        c.setFillColor(self.c_white)
        c.setStrokeColor(self.c_line)
        c.setLineWidth(1)
        c.rect(40, 48, 430, 335, fill=1, stroke=1)
        
        c.setFillColor(self.c_mck_navy)
        c.rect(40, 350, 430, 33, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_white)
        c.drawString(54, 362, "【 가맹점 출점 3대 핵심 경쟁력 】")
        
        c.setFont(FONT_BOLD, 9)
        c.setFillColor(self.c_mck_navy)
        c.drawString(54, 325, "● 1. 주간 유휴시간 제로 (100% 예약 풀가동)")
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_charcoal)
        c.drawString(54, 307, "   평일 낮 10시~오후 5시 시니어 동호회 모임으로 100% 가동")
        
        c.setFont(FONT_BOLD, 9)
        c.setFillColor(self.c_mck_navy)
        c.drawString(54, 270, "● 2. 10타석 플래그십 상위 20% 시장 독점")
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_charcoal)
        c.drawString(54, 252, "   소형 노후 매장과 차별화된 카페형 라운지로 지역 랜드마크화")
        
        c.setFont(FONT_BOLD, 9)
        c.setFillColor(self.c_mck_navy)
        c.drawString(54, 215, "● 3. 빠른 원금 회수 및 고수익성")
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_charcoal)
        c.drawString(54, 197, f"   월 영업익 {fin['monthly_scenarios']['moderate']['operating_profit']//10000:,}만 달성으로 약 {fin['investment']['payback_months_moderate']:.1f}개월 내 원금 회수")
        
        # 우측 박스
        c.setFillColor(self.c_white)
        c.setStrokeColor(self.c_line)
        c.setLineWidth(1)
        c.rect(490, 48, 430, 335, fill=1, stroke=1)
        
        c.setFillColor(self.c_mck_teal)
        c.rect(490, 350, 430, 33, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_white)
        c.drawString(504, 362, "【 건물주 및 상가 상생 활성화 효과 】")
        
        c.setFont(FONT_BOLD, 9)
        c.setFillColor(self.c_mck_teal)
        c.drawString(504, 325, "● 1. 일 60~90명 액티브 시니어 지속 유입")
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_charcoal)
        c.drawString(504, 307, "   구매력 높은 시니어 매일 방문으로 1층 식당/카페 매출 동반 상승")
        
        c.setFont(FONT_BOLD, 9)
        c.setFillColor(self.c_mck_teal)
        c.drawString(504, 270, "● 2. 공실 해소 및 5년 장기 우량 임대차")
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_charcoal)
        c.drawString(504, 252, "   5년 이상 장기 임대차 계약으로 공실 리스크 제로 및 월세 보장")
        
        c.setFont(FONT_BOLD, 9)
        c.setFillColor(self.c_mck_teal)
        c.drawString(504, 215, "● 3. 건물 전체의 자산 가치(Cap Rate) 상승")
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_charcoal)
        c.drawString(504, 197, "   상가 유동인구 증가 및 부동산 매매 가치 동반 상승 견인")
        
        self._draw_footer(c, "McKinsey Executive Format | MYPARK Business Intelligence")
        c.showPage()

        c.save()
        print(f"[PDF GENERATED] {output_pdf_path}")
        return output_pdf_path
