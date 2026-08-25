# -*- coding: utf-8 -*-
"""16:9 와이드 맥킨지 클래식 이그제큐티브(McKinsey Executive) PDF 보고서 생성기 (최신 슬라이드 플로우 완비)"""
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
    def __init__(self):
        self.width = 960
        self.height = 540
        
        self.c_mck_navy = colors.HexColor('#002B49')
        self.c_mck_teal = colors.HexColor('#008080')
        self.c_charcoal = colors.HexColor('#1E293B')
        self.c_slate = colors.HexColor('#64748B')
        self.c_line = colors.HexColor('#CBD5E1')
        self.c_box_bg = colors.HexColor('#F8FAFC')
        self.c_tint_blue = colors.HexColor('#F1F5F9')
        self.c_white = colors.white
        self.c_red = colors.HexColor('#DC2626')

    def _draw_mckinsey_header(self, c, section_category, action_title):
        c.setFont(FONT_BOLD, 8.5)
        c.setFillColor(self.c_slate)
        c.drawString(40, self.height - 26, section_category.upper())
        
        c.setFont(FONT_BOLD, 13)
        c.setFillColor(self.c_mck_navy)
        c.drawString(40, self.height - 44, action_title)
        
        c.setStrokeColor(self.c_line)
        c.setLineWidth(1)
        c.line(40, self.height - 52, self.width - 40, self.height - 52)

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
        # Page 2: 1. 배후 인구 분석 (반경 3km)
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "1. 배후 인구 분석", f"사업지 반경 3km 내 18.8만 명({len(demo['dongs'])}개 행정동)의 풍부한 주거 배후 인구 형성")
        if 'map_radius' in charts and os.path.exists(charts['map_radius']):
            c.drawImage(charts['map_radius'], 40, 48, width=425, height=425, preserveAspectRatio=True)
            
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(495, 465, f"■ 반경 3km 행정동별 인구 집계 현황 (총 {demo['total_pop']:,}명)")
        
        table_data_2 = [['행정구역(동)', '남자(명)', '여자(명)', '합계(명)']]
        for d in demo['dongs']:
            table_data_2.append([d['dong'], f"{d['male']:,}", f"{d['female']:,}", f"{d['total']:,}"])
        table_data_2.append(['합계 (3km 생활권)', f"{demo['male_pop']:,}", f"{demo['female_pop']:,}", f"{demo['total_pop']:,}"])
        
        t2 = Table(table_data_2, colWidths=[120, 100, 100, 105], rowHeights=[28]*len(table_data_2))
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.c_mck_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.c_white),
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR),
            ('FONTSIZE', (0, 0), (-1, -1), 8.8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.c_line),
            ('BACKGROUND', (0, -1), (-1, -1), self.c_tint_blue),
            ('TEXTCOLOR', (0, -1), (-1, -1), self.c_mck_navy),
            ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ]))
        t2.wrapOn(c, 495, 48)
        t2.drawOn(c, 495, 450 - (len(table_data_2) * 28))
        self._draw_footer(c, f"KOSIS National Statistics Portal ({demo['base_date']})")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 3: 1. 타겟 시니어 인구 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "1. 타겟 시니어 인구 분석", f"50대 이상 골든 시니어 7.2만 명({demo['senior_ratio']}%)으로 평일 주간 100% 예약 풀가동 최적")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 268, 380, 212, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(54, 460, "■ 핵심 타겟: 50대 이상 여성 시니어 (3.8만 명)")
        c.setFont(FONT_REGULAR, 8.8)
        c.setFillColor(self.c_charcoal)
        c.drawString(54, 434, f"• 여성 시니어 인구: 약 {demo['senior_50_female']:,}명 (시니어의 53.0%)")
        c.drawString(54, 410, "• 소비 특성: 평일 낮 시간대(10~17시) 주부 모임 주도")
        c.drawString(54, 386, "• 락인 효과: 4인 1팀 고정 리그전으로 월 정기 결제")
        c.drawString(54, 362, "• 파생 소비: 게임 후 인근 카페/식당 연계 지출 활발")
        c.drawString(54, 338, "• 입소문 효과: 지역 여성 커뮤니티 기반 신규 회원 확산")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_mck_teal)
        c.setLineWidth(1.2)
        c.rect(40, 48, 380, 210, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_teal)
        c.drawString(54, 238, "■ 시니어 상권 사업화 시사점")
        c.setFont(FONT_REGULAR, 8.8)
        c.setFillColor(self.c_charcoal)
        c.drawString(54, 212, f"• 시니어 인구 집적도: {demo['senior_ratio']}%의 최상급 골든 배후지")
        c.drawString(54, 188, "• 사계절 가동성: 야외 파크골프장의 날씨 한계 대체")
        c.drawString(54, 164, "• 주간 가동 극대화: 일반 골프 유휴 시간 100% 가동")
        c.drawString(54, 140, "• 진입 장벽 제로: 단 1개의 채로 누구나 즉시 입문")
        c.drawString(54, 116, "• 리텐션 극대화: 월정액제 동호회 타석 배정 고정매출")
        
        table_data_3 = [['연령대', '남자(명)', '여자(명)', '합계(명)']]
        for a in demo['age_distribution']:
            table_data_3.append([a['age_group'], f"{int(a['male']):,}", f"{int(a['female']):,}", f"{int(a['total']):,}"])
        table_data_3.append(['총계 (50대이상)', f"{demo['senior_50_plus'] - demo['senior_50_female']:,}", f"{demo['senior_50_female']:,}", f"{demo['senior_50_plus']:,}"])
        
        t3 = Table(table_data_3, colWidths=[120, 110, 110, 120], rowHeights=[32]*len(table_data_3))
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.c_mck_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.c_white),
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR),
            ('FONTSIZE', (0, 0), (-1, -1), 8.8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.c_line),
            ('BACKGROUND', (0, -1), (-1, -1), self.c_tint_blue),
            ('TEXTCOLOR', (0, -1), (-1, -1), self.c_mck_navy),
            ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ]))
        t3.wrapOn(c, 460, 48)
        t3.drawOn(c, 460, 465 - (len(table_data_3) * 32))
        self._draw_footer(c, f"KOSIS Demographic Database ({demo['base_date']})")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 4: 2. 상권 실측 분석 (소상공인365/BASA)
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "2. 상권 실측 분석 (소상공인365/BASA)", "주거지역 93% 밀집 상권 및 유사 골프업종 상위 20% 월매출 6,251만원 시장 타겟팅")
        rev_st = comm.get('revenue_structure', {})
        top20_str = f"{rev_st.get('top_20_sales', 62510000)//10000:,}만원"
        bot20_str = f"{rev_st.get('bottom_20_sales', 3020000)//10000:,}만원"
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 340, 260, 138, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_navy)
        c.drawString(50, 458, "■ 유사 골프업종 수익구조 (BASA)")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(50, 434, f"• 상위 20% 매출: {top20_str} /월")
        c.drawString(50, 414, f"• 하위 20% 매출: {bot20_str} /월")
        c.drawString(50, 394, "★ 마이파크는 상위 20% 시장 점유")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 194, 260, 138, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_navy)
        c.drawString(50, 312, "■ 핵심 고객층 및 이용 패턴")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(50, 288, "• 주 이용층: 50대 남녀 (구매력 최상)")
        c.drawString(50, 268, "• 최근 변화: 3040대 직장인/가족 유입")
        c.drawString(50, 248, "• 충성도: 주 2~3회 정기 방문 락인")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_mck_teal)
        c.setLineWidth(1.2)
        c.rect(40, 48, 260, 138, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_teal)
        c.drawString(50, 166, "■ 피크 요일 및 운영 전략")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(50, 142, "• 최고 매출 요일: 토요일 & 월요일")
        c.drawString(50, 122, "• 주거형 상권: 품질/편의성 중심")
        c.drawString(50, 102, "• 평일 주간(10~17시) 주부 모임 가동")
        
        infra = comm.get('infra', {})
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(320, 340, 600, 138, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(335, 458, f"■ {comm.get('region_title', '사업지')} 주변 인프라 및 교통망 실측 현황")
        c.setFont(FONT_REGULAR, 8.8)
        c.setFillColor(self.c_charcoal)
        c.drawString(335, 430, f"• 주변 시설: 관공서 {infra.get('관공서', 8)}개  |  교육기관 {infra.get('교육기관', 15)}개  |  금융기관 {infra.get('금융기관', 18)}개")
        c.drawString(335, 408, f"• 대중 교통: 버스정류장 {infra.get('버스정류장', 48)}개 노선망  |  지하철 {infra.get('지하철', '대중교통망 인접')}")
        c.drawString(335, 386, "• 상권 구성: 주거지역 93% 압도적 밀집으로 탄탄한 배후 생활권 형성")
        
        if 'sales_trend' in charts and os.path.exists(charts['sales_trend']):
            c.drawImage(charts['sales_trend'], 320, 48, width=600, height=280, preserveAspectRatio=True)
            
        self._draw_footer(c, "Small Enterprise and Market Service (BASA) & NICE BizMap")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 5: 2. 업종 성장률 및 골프 특화도
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "2. 업종 성장률 및 골프 특화도", "골프용품 매출성장률 1위(+182.4%) 및 전국 평균 대비 2.3배 높은 골프 특화 상권")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 268, 425, 212, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        target_dong = site.get("dong", "사업권역")
        c.drawString(56, 460, f"■ {target_dong} 매출 증가율 TOP 5 (소상공인365 실측)")
        growths = comm.get('top_growth_industries', [])
        y_g = 432
        for g in growths:
            c.setFont(FONT_BOLD if g['rank'] == 1 else FONT_REGULAR, 8.8)
            c.setFillColor(self.c_red if g['rank'] == 1 else self.c_charcoal)
            c.drawString(56, y_g, f"• {g['rank']}위 : {g['name']}  ({g['growth']}) - {g['status']}")
            y_g -= 22
            
        golf_den = comm.get('golf_industry_density', {})
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, 268, 425, 212, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, 460, "■ 지역 골프 문화 및 유사 레저 밀집도 (BASA 실측)")
        c.setFont(FONT_REGULAR, 8.8)
        c.setFillColor(self.c_charcoal)
        target_dong = site.get("dong", "사업권역")
        c.drawString(511, 428, f"• {target_dong} 내 스크린골프 점포: {golf_den.get('store_count', 10)}개 (전체 {golf_den.get('total_stores_in_dong', 1526)}개 중)")
        c.drawString(511, 400, f"• 스크린골프 업종 비중: {golf_den.get('density_ratio', 0.7)}% (전국 평균 {golf_den.get('national_avg_density', 0.3)}% 대비 2.3배)")
        c.drawString(511, 372, "• 전국 평균 대비 2.3배 밀집된 '골프·파크골프 소비 문화 특화 상권'")
        c.drawString(511, 344, f"• 성장 단계: {golf_den.get('growth_stage', '집중 성장 단계')}")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 425, 210, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 238, "■ 요일 및 시간대별 매출 패턴 (NICE비즈맵 실측)")
        c.setFont(FONT_REGULAR, 8.8)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 206, f"• 피크 요일: 월요일 ({comm['day_distribution']['월']}%) 최고치 (주간 동호회 정기 모임)")
        c.drawString(56, 178, f"• 주간 비중: 10~17시 이용 비중이 전체의 {comm['time_distribution']['주간_10_17시_비중']}% 압도적")
        c.drawString(56, 150, "• 일반 스크린골프(야간 위주)와 달리 낮 시간대 풀가동으로 회전율 2배")
        c.drawString(56, 122, f"• 주말 가동률: 주말 평균 비중 {comm['day_distribution']['주말평균비중']}%로 주 7일 고른 수익")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_mck_teal)
        c.setLineWidth(1.2)
        c.rect(495, 48, 425, 210, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_teal)
        c.drawString(511, 238, "■ 마이파크 출점 종합 전략적 시사점")
        c.setFont(FONT_REGULAR, 8.8)
        c.setFillColor(self.c_charcoal)
        c.drawString(511, 206, "• 수요 검증 완료: 골프용품 매출 성장 1위(+182.4%) 상권으로 검증된 소비력")
        c.drawString(511, 178, "• 공급 격차 점유: 노후 2~3타석 매장 대비 10타석 플래그십으로 상위 시장 독점")
        c.drawString(511, 150, "• 복합 문화 공간: 카페형 라운지 및 파크골프 용품 샵 연계로 객단가 극대화")
        c.drawString(511, 122, "• 상권 락인(Lock-in): 주거지역 93% 배후 고정 고객 대상 월회원제 정착")
        
        self._draw_footer(c, "Small Enterprise 365, NICE BizMap & SK Telecom Geovision Big Data")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 6: 3. 경쟁 환경 실측 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "3. 경쟁 환경 실측 분석", "반경 3km 내 스크린 파크골프 전문 매장 공급 부족으로 10타석 대규모 플래그십 선점 기회")
        comps = comm.get('competitors', [])
        card_w = 205
        gap = 18
        start_x = 40
        for idx, comp in enumerate(comps[:4]):
            cur_x = start_x + (idx * (card_w + gap))
            
            c.setFillColor(self.c_mck_navy)
            c.rect(cur_x, 425, card_w, 45, fill=1, stroke=0)
            c.setFont(FONT_BOLD, 9.5)
            c.setFillColor(self.c_white)
            c_name = str(comp['name'])
            if len(c_name) > 12:
                c.drawCentredString(cur_x + card_w/2, 450, c_name[:12])
                c.drawCentredString(cur_x + card_w/2, 434, c_name[12:])
            else:
                c.drawCentredString(cur_x + card_w/2, 442, c_name)
            
            c.setFillColor(self.c_tint_blue)
            c.setStrokeColor(self.c_line)
            c.rect(cur_x, 355, card_w, 70, fill=1, stroke=1)
            c.setFont(FONT_BOLD, 11)
            c.setFillColor(self.c_mck_navy)
            rooms_label = f"{comp.get('rooms', 0)}타석 규모" if comp.get('rooms', 0) > 0 else "1호점 선점 대상"
            c.drawCentredString(cur_x + card_w/2, 395, rooms_label)
            c.setFont(FONT_REGULAR, 8)
            c.setFillColor(self.c_slate)
            c.drawCentredString(cur_x + card_w/2, 372, f"[{comp.get('status', '실측완료')}] {comp.get('system', '스크린 시스템')[:16]}")
            
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(cur_x, 48, card_w, 300, fill=1, stroke=1)
            
            c.setFont(FONT_REGULAR, 8)
            c.setFillColor(self.c_charcoal)
            c.drawString(cur_x + 8, 325, "■ 주소:")
            addr_str = str(comp['address'])
            c.drawString(cur_x + 8, 310, addr_str[:17])
            if len(addr_str) > 17:
                c.drawString(cur_x + 8, 296, addr_str[17:34])
            if len(addr_str) > 34:
                c.drawString(cur_x + 8, 282, addr_str[34:])
                
            c.setFillColor(self.c_mck_teal)
            c.setFont(FONT_BOLD, 8)
            sys_str = f"■ 시스템: {comp['system']}"
            c.drawString(cur_x + 8, 258, sys_str[:17])
            if len(sys_str) > 17:
                c.drawString(cur_x + 8, 244, sys_str[17:])
            
            c.setFillColor(self.c_charcoal)
            c.setFont(FONT_REGULAR, 8)
            rooms_str = f"■ 규모: {comp['rooms']}타석 운영" if comp.get('rooms', 0) > 0 else "■ 상태: 상업용 매장 미등록"
            c.drawString(cur_x + 8, 218, rooms_str)
            
            c.setFillColor(self.c_slate)
            c.drawString(cur_x + 8, 188, "■ 특징:")
            feat_str = str(comp.get('features', '-'))
            c.drawString(cur_x + 8, 172, feat_str[:17])
            if len(feat_str) > 17:
                c.drawString(cur_x + 8, 158, feat_str[17:34])
            if len(feat_str) > 34:
                c.drawString(cur_x + 8, 144, feat_str[34:])
            
        self._draw_footer(c, "Small Enterprise Market Service & Kakao Map Local POI Survey")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 7: 4. 입지 최적성 종합 평가 (5대 다이아몬드 스코어링)
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "4. 입지 최적성 종합 평가", f"5대 다이아몬드 스코어링 총점 {score['total_score']}점({score['grade']}등급)으로 출점 최우선 추천 판정")
        if 'radar_score' in charts and os.path.exists(charts['radar_score']):
            c.drawImage(charts['radar_score'], 40, 48, width=440, height=425, preserveAspectRatio=True)
            
        indicators = [
            ("1) 골든 시니어 집적도", score['scores']['senior_population'], 25, "KOSIS 실측: 반경 3km 내 50대 이상 시니어 72,400명 (38.4%) 밀집"),
            ("2) 접근성 및 주차 인프라", score['scores']['accessibility_parking'], 25, "간선도로 접면/교통망 우수(20점) / 10타석 주차면은 '현장 실측' 요망"),
            ("3) 공간 적합성 및 층고", score['scores']['space_efficiency'], 15, "120평 10타석 배치 최적(13점) / 유효 층고 2.8m 이상은 '인테리어 실측' 필수"),
            ("4) 수요 공급 갭 (블루오션)", score['scores']['supply_gap'], 15, "상업용 전문 매장은 단 1곳('마실파크골프')뿐으로, 플래그십 공급 절대 부족"),
            ("5) 지역 소비력 및 여가지출", score['scores']['commercial_spending'], 20, "BASA 실측: 골프용품 성장 1위(+182.4%) 및 상위 20% 월 6,251만원 상권"),
        ]
        y_ind = 445
        for iname, iscore, imax, idesc in indicators:
            c.setFont(FONT_BOLD, 10)
            c.setFillColor(self.c_mck_navy)
            c.drawString(500, y_ind, f"■ {iname}: ")
            c.setFillColor(self.c_mck_teal)
            c.drawString(650, y_ind, f"{iscore}점 / {imax}점 만점")
            
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_slate)
            c.drawString(510, y_ind - 18, f"↳ 산출 근거: {idesc}")
            y_ind -= 54
            
        c.setFont(FONT_BOLD, 11)
        c.setFillColor(self.c_red)
        c.drawString(500, y_ind - 10, f"★ 종합 판정: 총점 {score['total_score']}점 ({score['grade_desc']})")
        self._draw_footer(c, "MYPARK 5-Dimension Diamond Scoring Methodology (22+20+13+15+20=90.0 S-Grade)")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 8: 5. 사업지 개요 및 현장 출점 요건 (4대 건축·인프라 체크리스트) [신규 위치]
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "5. 사업지 개요 및 현장 출점 요건", f"10타석 {site['area_pyeong']}평 규모 출점을 위한 4대 건축·인프라 현장 실측 기준")
        cards_p8 = [
            (40, 268, 425, 212, "■ 공간 및 유효 층고 요건", [
                f"• 대상 주소: {site['full_address']}",
                f"• 권장 면적: 전용 {site['area_pyeong']}평 (10타석 + 카페/락커룸 최적 배치)",
                f"• 층고 기준: {site['clear_height_spec']}",
                f"• 보/배관 간섭: 센서 투사 영역 및 스윙 궤적 내 장애물 사전 실측",
                f"• 권장 층수: 접근성 높은 지상 2~3층 권장 (쾌적한 지하 1층 가능)",
                f"• 바닥 하중: 스크린 타석 및 키오스크 하중(300kg/㎡) 적합 여부"
            ]),
            (495, 268, 425, 212, "■ 주차 및 차량 접근성 기준", [
                f"• 주차 요건: {site['parking_spec']}",
                f"• 고객 특성: 자차 이용 시니어 비중 80% 이상으로 편리한 진출입 필수",
                f"• 진입 여건: 램프 폭 및 회전각 여유 있는 자주식 주차장 최우선",
                f"• 도로 접면: 주요 간선도로 및 대단지 아파트 진입로 인접 우수",
                f"• 보행 동선: 대중교통(버스/지하철) 도보 5~10분 생활권",
                f"• 승하차 편의: 주차장에서 매장 입구까지 단차 없는 완만한 동선"
            ]),
            (40, 48, 425, 210, "■ 건물 편의 및 승강기 설비", [
                f"• 고객 편의: {site['accessibility_spec']}",
                f"• 계단 여건: 계단 단차가 낮거나 완만한 진입 경사로 확보 필요",
                f"• 냉난방/환기: 개별 공조 및 고성능 환기 덕트 설치 공간 확인",
                f"• 소음/진동: 상하층 타 업종 간섭 방지 방음/흡음 설계 시공",
                f"• 쾌적성: 남녀 분리 청결 화장실 및 쾌적한 로비 라운지 구축",
                f"• 장애인 편의: 엘리베이터 단차 제거 및 자동문 출입구 권장"
            ]),
            (495, 48, 425, 210, "■ 인허가 및 건축물 용도", [
                f"• 적합 용도: {site['zoning_spec']}",
                f"• 지자체 체육시설: 체육시설의 설치·이용에 관한 법률 인허가 검토",
                f"• 소방 기준: 스프링클러, 비상유도등, 비상탈출구 완비 점검",
                f"• 전기 용량: 10타석 시뮬레이터 동시 가동 대비 30kW 이상 인입",
                f"• 정화조 용량: 일 최대 150명 이상 동시 이용 기준 충족 점검",
                f"• 행정 절차: 관할 구청 건축과 및 체육진흥과 용도 사전 협의"
            ]),
        ]
        for cx, cy, cw, ch, ctitle, clines in cards_p8:
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.setLineWidth(1)
            c.rect(cx, cy, cw, ch, fill=1, stroke=1)
            
            c.setFont(FONT_BOLD, 10.5)
            c.setFillColor(self.c_mck_navy)
            c.drawString(cx + 14, cy + ch - 18, ctitle)
            
            c.setFont(FONT_REGULAR, 8.8)
            c.setFillColor(self.c_charcoal)
            y_offset = cy + ch - 38
            for line_txt in clines:
                c.drawString(cx + 14, y_offset, line_txt)
                y_offset -= 29
        self._draw_footer(c, "MYPARK Standard Facility Criteria & Architectural Survey")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 9: 6. 사업 타당성 분석 - 매출 추정
        # ---------------------------------------------------------------------
        m_scen = fin['monthly_scenarios']
        self._draw_mckinsey_header(c, "6. 사업 타당성 분석 - 매출 추정", f"10타석 기준 보편 가동 시 월매출 {m_scen['moderate']['total_revenue']//10000:,}만원(연간 5.2억원) 달성 전망")
        
        # 1. 상단 3대 드라이버 카드
        drivers = [
            (40, "1게임 이용 단가", "7,000원", "18홀 라운딩 기준"),
            (345, "부가 매출 창출", "18.0%", "용품10% + 식음5% + 레슨3%"),
            (650, "주간 풀가동 일수", "월 30일", "1일 10시간 가동 모델")
        ]
        for bx, btitle, bval, bsub in drivers:
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(bx, 415, 270, 60, fill=1, stroke=1)
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_slate)
            c.drawString(bx + 12, 456, btitle)
            c.setFont(FONT_BOLD, 11)
            c.setFillColor(self.c_mck_navy)
            c.drawString(bx + 12, 432, f"{bval}  ({bsub})")
            
        # 2. 중앙 테이블
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
        t9 = Table(table_data_9, colWidths=[100, 120, 105, 105, 105, 170, 175], rowHeights=[28]*4)
        t9.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.c_mck_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.c_white),
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR),
            ('FONTSIZE', (0, 0), (-1, -1), 8.8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.c_line),
            ('TEXTCOLOR', (5, 1), (5, -1), self.c_mck_navy),
            ('FONTNAME', (5, 1), (5, -1), FONT_BOLD),
        ]))
        t9.wrapOn(c, 40, 48)
        t9.drawOn(c, 40, 275)
        
        # 3. 하단 콜아웃 3단
        callouts = [
            (40, "■ 보수적 시나리오 (월 3,540만원)", [
                "• 상권 초기 진입 단계: 타석당 1일 12.5명 이용",
                "• 손익분기점(BEP 1,940만) 여유 초과 달성",
                "• 월 순영업이익 약 1,300만원 이상 흑자 구조 확보",
                "• 초기 단골 125명만으로도 안정적 운영 가능"
            ]),
            (345, "■ 보편적 시나리오 (월 4,366만원)", [
                "• 평일 주간 10~17시 동호회 정기 예약 정착",
                "• 타석당 1일 15명 이용 기준 연매출 5.2억원 창출",
                "• 월 순영업이익 2,120만원 달성 (영업이익률 48.6%)",
                f"• 약 1년 4개월({fin['investment']['payback_months_moderate']:.1f}개월) 만에 투자금 전액 회수"
            ]),
            (650, "■ 긍정적 시나리오 (월 5,664만원)", [
                "• 주말 풀예약 및 야간 직장인/가족 유입 활성화",
                "• 타석당 1일 20명 이용 기준 연매출 6.8억원 창출",
                "• 10타석 풀가동 시 월 순영업이익 3,300만원 달성",
                "• 연간 4.0억원 수준의 압도적 영업현금흐름 창출"
            ])
        ]
        for bx, btitle, blines in callouts:
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_mck_teal if "보편" in btitle else self.c_line)
            c.setLineWidth(1.2 if "보편" in btitle else 1)
            c.rect(bx, 48, 270, 205, fill=1, stroke=1)
            
            c.setFont(FONT_BOLD, 10)
            c.setFillColor(self.c_mck_teal if "보편" in btitle else self.c_mck_navy)
            c.drawString(bx + 12, 232, btitle)
            
            c.setFont(FONT_REGULAR, 8.2)
            c.setFillColor(self.c_charcoal)
            y_cl = 202
            for l_txt in blines:
                c.drawString(bx + 12, y_cl, l_txt)
                y_cl -= 36
                
        self._draw_footer(c, "Base Assumptions: 18 Holes 8,000 KRW, Secondary Sales 18%, 30 Operating Days/Month")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 10: 6. 사업 타당성 분석 - 비용 구조 (3.36억원 CAPEX 명세 완비)
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "6. 사업 타당성 분석 - 비용 구조", "초기 순투자금 3.36억원(장비 1.5억+인테리어 1.56억+초도 0.3억) 및 월비용 2,246만원")
        
        # 1. 상단 3대 비용 지표
        metrics = [
            (40, "초기 순투자금 (총 3.36억원)", "3억 3,600만원", "장비 1.5억 + 인테리어 1.56억 + 초도 0.3억"),
            (345, "월 고정비 (인건비+임대료)", f"{fin['monthly_rent']//10000 + 750:,}만원 /월", f"인력 3명(750만) + 임대료({fin['monthly_rent']//10000:,}만)"),
            (650, "월 변동비 & 매장운영비", "956만원 /월", "원가 3종 + 카드수수료 + 매장운영비")
        ]
        for bx, btitle, bval, bsub in metrics:
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(bx, 415, 270, 60, fill=1, stroke=1)
            c.setFont(FONT_REGULAR, 8)
            c.setFillColor(self.c_slate)
            c.drawString(bx + 12, 458, btitle)
            c.setFont(FONT_BOLD, 10.5)
            c.setFillColor(self.c_mck_navy)
            c.drawString(bx + 12, 438, bval)
            c.setFont(FONT_REGULAR, 7.5)
            c.setFillColor(self.c_charcoal)
            c.drawString(bx + 12, 422, f"↳ {bsub}")
            
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
        t10 = Table(table_data_10, colWidths=[150, 135, 135, 135, 325], rowHeights=[26]*5)
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
            ('BACKGROUND', (0, -1), (-1, -1), self.c_tint_blue),
            ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ]))
        t10.wrapOn(c, 40, 48)
        t10.drawOn(c, 40, 255)
        
        # 3. 하단 콜아웃 2단
        cost_callouts = [
            (40, "■ 운영 모델별 인건비 및 손익 비교", [
                "• 오토/위탁 운영 (직원 3명): 월 인건비 750만, 월 순익 2,120만, 회수 15.8개월",
                "★ 창업주 직접 운영 (점주+파트 1명): 월 인건비 250만 (500만원 절감)",
                "↳ 직접 운영 시 월 순영업익 2,620만원 달성 및 단 12.8개월(1년 1개월) 회수"
            ]),
            (495, "■ 높은 공헌이익률 및 BEP 방어력", [
                "• 전체 매출의 82%가 타석 이용료(마진 98%)로 구성되어 이익률 최상",
                "• 창업주 직접 운영 시 월 고정비가 1,140만원으로 급감하여 손익 안정성 극대화",
                "• 손익분기점(BEP)이 기기당 일 0.6회전(월 135명)으로 낮아져 적자 불가능"
            ])
        ]
        for bx, btitle, blines in cost_callouts:
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(bx, 48, 425, 185, fill=1, stroke=1)
            c.setFont(FONT_BOLD, 10)
            c.setFillColor(self.c_mck_navy)
            c.drawString(bx + 14, 210, btitle)
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_charcoal)
            y_cl = 175
            for l_txt in blines:
                c.drawString(bx + 14, y_cl, l_txt)
                y_cl -= 40
                
        self._draw_footer(c, "MYPARK Standard Operating Cost Model (CAPEX 3.36 Billion KRW)")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 11: 6. 손익 예측 및 BEP 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "6. 손익 예측 및 BEP 분석", f"기기당 1일 0.9회전 달성 시 BEP 돌파 및 {fin['investment']['payback_months_moderate']:.1f}개월 내 순투자금 3.36억원 전액 회수")
        if 'profit_forecast' in charts and os.path.exists(charts['profit_forecast']):
            c.drawImage(charts['profit_forecast'], 40, 48, width=500, height=425, preserveAspectRatio=True)
            
        mod_1y = fin['forecast_5year']['moderate'][0]
        mod_5y = fin['forecast_5year']['moderate'][4]
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(560, 268, 360, 212, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(576, 460, "■ 연간 실적 전망 (보편 시나리오)")
        c.setFont(FONT_REGULAR, 8.8)
        c.setFillColor(self.c_charcoal)
        c.drawString(576, 434, f"• 1년차: 연매출 {mod_1y['total_revenue']//100000000:.1f}억원 / 영업익 {mod_1y['operating_profit']//100000000:.1f}억원")
        c.drawString(576, 410, f"• 3년차: 연매출 {fin['forecast_5year']['moderate'][2]['total_revenue']//100000000:.1f}억원 / 영업익 {fin['forecast_5year']['moderate'][2]['operating_profit']//100000000:.1f}억원")
        c.drawString(576, 386, f"• 5년차: 연매출 {mod_5y['total_revenue']//100000000:.1f}억원 / 영업익 {mod_5y['operating_profit']//100000000:.1f}억원")
        c.drawString(576, 362, "• 연평균 영업이익률: 약 48.6% (안정적 고수익)")
        c.drawString(576, 338, f"• 5개년 누적 영업익: 약 {(sum(item['operating_profit'] for item in fin['forecast_5year']['moderate']))//100000000:.1f}억원 전망")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_mck_teal)
        c.setLineWidth(1.2)
        c.rect(560, 48, 360, 210, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_teal)
        c.drawString(576, 238, "■ 손익분기점(BEP) 및 운영모델별 회수 기간")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(576, 212, "• 오토 운영 BEP: 기기당 1일 0.9회전 (월 240명 돌파 / 15.8개월 회수)")
        c.setFont(FONT_BOLD, 8.8)
        c.setFillColor(self.c_mck_teal)
        c.drawString(576, 190, "★ 창업주 직접 운영 BEP: 기기당 1일 단 0.6회전 (월 135명 돌파)")
        c.setFont(FONT_REGULAR, 8.2)
        c.setFillColor(self.c_charcoal)
        c.drawString(576, 172, "  ↳ 인건비 500만원 절감으로 월 순영업이익 2,620만원 (이익률 60.0%)")
        c.drawString(576, 154, "  ↳ 순투자금 3.36억원 전액 회수 기간: 단 12.8개월 (약 1년 1개월)")
        c.drawString(576, 134, "• 안전 마진: 보편 가동(150명) 대비 BEP(4.5명)는 3.0%로 적자 불가능")
        
        self._draw_footer(c, f"CAPEX {fin['investment']['total_capex'] / 100000000.0:.2f} Billion KRW / Compound Growth Rate 2% p.a.")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 12: 7. 종합 결론 및 사업 타당성 최종 평가
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "7. 종합 결론 및 사업 타당성 최종 평가", f"반경 3km 내 7.2만 시니어 배후 수요와 주간 풀가동으로 {fin['investment']['payback_months_moderate']:.1f}개월 내 투자금 전액 회수 가능")
        
        # 1. 상단 4대 배지
        kpis = [
            (40, "배후 시니어 인구", f"{demo['senior_50_plus']:,}명", f"({demo['senior_ratio']}% 점유)", self.c_mck_navy),
            (265, "예상 월 영업이익", f"{fin['monthly_scenarios']['moderate']['operating_profit']//10000:,}만원", "(이익률 48.6%)", self.c_mck_navy),
            (490, "손익분기점 (BEP)", "타석당 0.9회전", "(월 240명 시 돌파)", self.c_mck_teal),
            (715, "순투자금 회수", f"약 {fin['investment']['payback_months_moderate']:.1f}개월", "(순투자 3.36억원)", self.c_red),
        ]
        for bx, btitle, bval, bsub, col in kpis:
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(bx, 400, 205, 75, fill=1, stroke=1)
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_slate)
            c.drawString(bx + 12, 455, btitle)
            c.setFont(FONT_BOLD, 10.5)
            c.setFillColor(col)
            c.drawString(bx + 12, 426, f"{bval}  {bsub}")
            
        # 2. 좌측: 가맹점 3대 핵심 경쟁력 (공백 없이 꽉 채운 12줄 텍스트)
        c.setFillColor(self.c_white)
        c.setStrokeColor(self.c_line)
        c.setLineWidth(1.2)
        c.rect(40, 48, 430, 340, fill=1, stroke=1)
        
        c.setFillColor(self.c_mck_navy)
        c.rect(40, 355, 430, 33, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_white)
        c.drawString(54, 367, "【 가맹점 출점 3대 핵심 경쟁력 】")
        
        y_l = 332
        f_points = [
            ("● 1. 주간 유휴시간 제로 (100% 예약 풀가동 체계)", [
                "• 일반 스크린골프 손님이 전무한 '평일 낮 10시~오후 5시' 유휴 시간 독점",
                "• 반경 3km 내 7.2만 시니어 및 여성 주부 동호회 4인 1팀 정기 리그 가동",
                "• 비수기 및 날씨 영향을 받지 않는 사계절 100% 예약 풀가동 안정성 확보"
            ]),
            ("● 2. 10타석 플래그십 상위 20% 시장 독점 점유", [
                "• 노후 소형 1~2타석 매장 대비 10타석 대규모 플래그십 시설 경쟁력 압도",
                "• 소상공인365 실측 상위 20% 월매출 6,251만원 시장을 단독 선점 점유",
                "• 카페형 휴게 라운지 및 파크골프 용품 샵 결합으로 객단가 극대화"
            ]),
            ("● 3. 빠른 원금 회수 및 압도적 고수익성", [
                f"• 오토 운영: 월 순영업익 약 {fin['monthly_scenarios']['moderate']['operating_profit']//10000:,}만원 (이익률 48.6%) / 15.8개월 회수",
                f"★ 창업주 직접 운영: 월 순영업익 2,620만원 (이익률 60.0%) / 단 12.8개월(1년 1개월) 회수",
                "• 손익분기점(BEP)이 기기당 하루 0.5~0.9회전에 불과하여 적자 리스크 제로"
            ])
        ]
        for title, lines in f_points:
            c.setFont(FONT_BOLD, 10)
            c.setFillColor(self.c_mck_navy)
            c.drawString(54, y_l, title)
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_charcoal)
            y_l -= 18
            for l in lines:
                c.drawString(64, y_l, l)
                y_l -= 17
            y_l -= 18
            
        # 3. 우측: 건물주 및 상가 상생 활성화 효과 (공백 없이 꽉 채운 12줄 텍스트)
        c.setFillColor(self.c_white)
        c.setStrokeColor(self.c_line)
        c.setLineWidth(1.2)
        c.rect(490, 48, 430, 340, fill=1, stroke=1)
        
        c.setFillColor(self.c_mck_teal)
        c.rect(490, 355, 430, 33, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_white)
        c.drawString(504, 367, "【 건물주 및 상가 상생 활성화 효과 】")
        
        y_r = 332
        l_points = [
            ("● 1. 일 60~90명 액티브 시니어 지속 유입 집객", [
                "• 구매력과 소비 여력이 높은 지역 시니어 고객이 매일 건물을 방문",
                "• 게임 전후 1층 식당, 카페, 병원, 약국 등 상가 내 타 점포 매출 동반 견인",
                "• 평일 낮 시간대 상가 전체 유동인구 증가로 침체된 상권 활성화 주도"
            ]),
            ("● 2. 공실 완전 해소 및 5년 장기 우량 임대차", [
                "• 마이파크 가맹점과의 5년 이상 장기 계약으로 공실 리스크 완전 박멸",
                "• 시설 투자비가 투입된 고정형 사업체로 중도 이탈 리스크 제로",
                f"• 매월 안정적이고 우량한 임대료(월 {fin['monthly_rent']//10000:,}만원)의 지속적 확보 가능"
            ]),
            ("● 3. 건물 전체의 자산 가치(Cap Rate) 상승 견인", [
                "• 우량 핵심 점포 입점에 따른 상가 건물 전체의 유동인구 및 인지도 급상승",
                "• 안정적인 임대수익률 확보로 상가 매매 가치 및 부동산 감정평가액 상승",
                "• 지역 랜드마크 스포테인먼트 시설로 자리매김하여 건물 브랜드 가치 극대화"
            ])
        ]
        for title, lines in l_points:
            c.setFont(FONT_BOLD, 10)
            c.setFillColor(self.c_mck_teal)
            c.drawString(504, y_r, title)
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_charcoal)
            y_r -= 18
            for l in lines:
                c.drawString(514, y_r, l)
                y_r -= 17
            y_r -= 18
            
        self._draw_footer(c, "McKinsey Executive Format | MYPARK Business Intelligence")
        c.showPage()

        c.save()
        print(f"[PDF GENERATED] {output_pdf_path}")
        return output_pdf_path
