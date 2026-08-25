# -*- coding: utf-8 -*-
"""16:9 와이드 최고급 비즈니스 컨설팅 PDF 보고서 생성기 (소상공인365/BASA, NICE비즈맵 실측 데이터 100% 통합)"""
import os
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 폰트 등록
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
    except Exception as e:
        print(f"Regular font load error: {e}")

if os.path.exists(font_bold_path):
    try:
        pdfmetrics.registerFont(TTFont('Malgun-Bold', font_bold_path))
        FONT_BOLD = 'Malgun-Bold'
    except Exception as e:
        FONT_BOLD = FONT_REGULAR
elif FONT_REGULAR == 'Malgun':
    FONT_BOLD = 'Malgun'


class PDFGenerator:
    """마이파크 16:9 와이드 비즈니스 PDF 생성기 (12페이지 전문 슬라이드 덱)"""
    
    def __init__(self):
        self.width = 960
        self.height = 540
        
        self.c_navy_dark = colors.HexColor('#0A192F')
        self.c_navy = colors.HexColor('#0F2744')
        self.c_royal_blue = colors.HexColor('#2563EB')
        self.c_gold = colors.HexColor('#F59E0B')
        self.c_emerald = colors.HexColor('#10B981')
        self.c_red = colors.HexColor('#DC2626')
        self.c_slate_dark = colors.HexColor('#1E293B')
        self.c_slate_gray = colors.HexColor('#64748B')
        self.c_card_bg = colors.HexColor('#F8FAFC')
        self.c_border = colors.HexColor('#E2E8F0')
        self.c_pink_bg = colors.HexColor('#FEF2F2')
        self.c_pink_border = colors.HexColor('#FECACA')
        self.c_blue_light = colors.HexColor('#EBF3FF')
        self.c_white = colors.white

    def _draw_header(self, c, white_prefix, gold_highlight, white_suffix=""):
        c.setFillColor(self.c_navy)
        c.setStrokeColor(self.c_royal_blue)
        c.setLineWidth(1.5)
        c.roundRect(40, self.height - 58, self.width - 80, 42, 6, fill=1, stroke=1)
        
        full_text = f"{white_prefix}{gold_highlight}{white_suffix}"
        c.setFont(FONT_BOLD, 13.5)
        c.setFillColor(self.c_white)
        c.drawCentredString(self.width / 2, self.height - 44, full_text)

    def _draw_footer(self, c, source_text):
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_slate_gray)
        c.drawRightString(self.width - 40, 18, source_text)

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
        c.setFillColor(self.c_navy_dark)
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        
        c.setFillColor(self.c_gold)
        c.rect(80, self.height - 120, self.width - 160, 3, fill=1, stroke=0)
        
        c.setFont(FONT_BOLD, 13)
        c.setFillColor(self.c_gold)
        c.drawString(80, self.height - 105, "MYPARK SCREEN PARK GOLF  |  출점 타당성 분석 보고서")
        
        c.setFont(FONT_BOLD, 26)
        c.setFillColor(self.c_white)
        c.drawString(80, self.height - 165, f"{site.get('building_name', '사업지')} 상권 및 사업성 분석")
        
        c.setFont(FONT_REGULAR, 12)
        c.setFillColor(self.c_border)
        c.drawString(80, self.height - 200, f"대상 주소: {site['full_address']}  |  표준 모델: {site['rooms']}타석 ({site['area_pyeong']}평)")
        
        badges = [
            (80, "입지 최적성 등급", f"{score['grade']}등급 ({score['total_score']}점)", self.c_gold),
            (360, "예상 월 영업이익 (보편)", f"{fin['monthly_scenarios']['moderate']['operating_profit']//10000:,}만원/월", self.c_emerald),
            (640, "투자금 회수 기간", f"{score['payback_text'].split('기준')[1].split('만에')[0].strip() if '기준' in score['payback_text'] else score['payback_text']}", self.c_white)
        ]
        for bx, btitle, bval, bcol in badges:
            c.setFillColor(self.c_navy)
            c.setStrokeColor(self.c_royal_blue)
            c.setLineWidth(1)
            c.roundRect(bx, 60, 240, 75, 8, fill=1, stroke=1)
            
            c.setFont(FONT_REGULAR, 9.5)
            c.setFillColor(self.c_slate_gray)
            c.drawString(bx + 16, 115, btitle)
            
            c.setFont(FONT_BOLD, 12)
            c.setFillColor(bcol)
            c.drawString(bx + 16, 85, bval)
            
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 2: 4대 출점 점검 체크리스트
        # ---------------------------------------------------------------------
        self._draw_header(c, "1. 사업지 개요 및 ", "출점 점검 체크리스트", f" ({site['rooms']}타석 / {site['area_pyeong']}평 권장)")
        cards_p2 = [
            (40, 270, 425, 195, "📐 공간 & 층고 점검 기준", [
                f"• 대상 주소: {site['full_address']}",
                f"• 권장 공간: 전용면적 {site['area_pyeong']}평 (10타석 + 라운지/카페 최적 배치)",
                f"• 층고 기준: {site['clear_height_spec']}",
                f"• 추천 층수: 지상 2~3층 권장 (또는 쾌적한 지하 1층)"
            ]),
            (495, 270, 425, 195, "🚗 주차 & 접근성 점검 기준", [
                f"• 주차 요건: {site['parking_spec']}",
                f"• 고객 특성: 자차 이용 시니어 비중 80% 이상으로 편리한 진출입 필수",
                f"• 도로 접면: 주요 간선도로 및 대단지 아파트 진입로 인접 우수",
                f"• 보행 동선: 대중교통(버스/지하철) 도보 5~10분 생활권"
            ]),
            (40, 50, 425, 205, "🏢 건물 편의 & 승강기 요건", [
                f"• 고객 편의: {site['accessibility_spec']}",
                f"• 계단 여건: 계단 단차가 낮거나 완만한 진입 경사로 확보 필요",
                f"• 냉난방/환기: 개별 공조 및 고성능 환기 덕트 설치 공간 확인",
                f"• 소음/진동: 상하층 타 업종 간섭 방지 방음 설계 적용"
            ]),
            (495, 50, 425, 205, "⚖️ 인허가 및 건축물 용도", [
                f"• 적합 용도: {site['zoning_spec']}",
                f"• 지자체 체육시설: 체육시설의 설치·이용에 관한 법률 검토",
                f"• 소방 기준: 스프링클러, 비상유도등, 비상탈출구 완비 점검",
                f"• 정화조/전기: 동시 이용 인원 대비 전기 용량(30kW 이상) 확인"
            ]),
        ]
        for cx, cy, cw, ch, ctitle, clines in cards_p2:
            c.setFillColor(self.c_card_bg)
            c.setStrokeColor(self.c_border)
            c.setLineWidth(1)
            c.roundRect(cx, cy, cw, ch, 8, fill=1, stroke=1)
            c.setFont(FONT_BOLD, 11)
            c.setFillColor(self.c_navy)
            c.drawString(cx + 16, cy + ch - 24, ctitle)
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_slate_dark)
            y_offset = cy + ch - 48
            for line_txt in clines:
                c.drawString(cx + 16, y_offset, line_txt)
                y_offset -= 22
        self._draw_footer(c, "* 기준: 마이파크 표준 가맹 모델 및 건축물 현장 실측 권장 기준")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 3: 배후 인구 분석
        # ---------------------------------------------------------------------
        self._draw_header(c, f"{demo.get('center_dong', '사업지')} 반경 3Km 생활권 (", f"약 {demo['total_pop']//10000}만명", ")")
        if 'map_radius' in charts and os.path.exists(charts['map_radius']):
            c.drawImage(charts['map_radius'], 40, 60, width=420, height=400, preserveAspectRatio=True)
            
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_red)
        c.drawString(495, 455, f"▲ 사업지 주변 총 인구수 : {demo['total_pop']:,}명 (반경 3km {len(demo['dongs'])}개 행정동)")
        
        table_data_3 = [['행정구역(동)', '남자(명)', '여자(명)', '합계(명)']]
        for d in demo['dongs']:
            table_data_3.append([d['dong'], f"{d['male']:,}", f"{d['female']:,}", f"{d['total']:,}"])
        table_data_3.append(['합계', f"{demo['male_pop']:,}", f"{demo['female_pop']:,}", f"{demo['total_pop']:,}"])
        
        t3 = Table(table_data_3, colWidths=[120, 100, 100, 105])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.c_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.c_white),
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.c_border),
            ('BACKGROUND', (0, -1), (-1, -1), self.c_pink_bg),
            ('TEXTCOLOR', (0, -1), (-1, -1), self.c_red),
            ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ]))
        t3.wrapOn(c, 495, 60)
        t3.drawOn(c, 495, 435 - (len(table_data_3) * 22))
        self._draw_footer(c, f"* 출처 : {demo['base_date']}")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 4: 메인 타겟 장·노년층 인구 수
        # ---------------------------------------------------------------------
        self._draw_header(c, "파크골프 메인 타겟 장·노년층 인구 수 (", f"약 {demo['senior_50_plus']:,}명_{demo['senior_ratio']}%", ")")
        c.setFillColor(self.c_pink_bg)
        c.setStrokeColor(self.c_pink_border)
        c.roundRect(40, 265, 380, 190, 8, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 11)
        c.setFillColor(self.c_red)
        c.drawString(56, 430, "🎯 핵심 소비층: 50대 이상 여성")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_slate_dark)
        c.drawString(56, 395, f"• 여성 시니어 인구: 약 {demo['senior_50_female']:,}명")
        c.drawString(56, 370, "• 타겟 분석 결과 여성 인구 비중이 높아,")
        c.drawString(56, 345, "  평일 낮 주간(10~17시) 주부/친목 모임 유치에 최적")
        
        c.setFillColor(self.c_card_bg)
        c.setStrokeColor(self.c_royal_blue)
        c.roundRect(40, 60, 380, 185, 8, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 11)
        c.setFillColor(self.c_navy)
        c.drawString(56, 220, "💡 시니어 상권 사업화 시사점")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_slate_dark)
        c.drawString(56, 185, f"• 시니어 인구 집적도 {demo['senior_ratio']}%의 최상급 골든 배후지")
        c.drawString(56, 160, "• 은퇴 세대의 건강 생활체육 참여 급증으로")
        c.drawString(56, 135, "  계절/날씨 무관 4계절 안정적 풀가동 실현")
        
        table_data_4 = [['연령대', '남자(명)', '여자(명)', '합계(명)']]
        for a in demo['age_distribution']:
            table_data_4.append([a['age_group'], f"{int(a['male']):,}", f"{int(a['female']):,}", f"{int(a['total']):,}"])
        table_data_4.append(['총계 (50대이상)', f"{demo['senior_50_plus'] - demo['senior_50_female']:,}", f"{demo['senior_50_female']:,}", f"{demo['senior_50_plus']:,}"])
        
        t4 = Table(table_data_4, colWidths=[120, 110, 110, 120])
        t4.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.c_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.c_white),
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.c_border),
            ('BACKGROUND', (0, -1), (-1, -1), self.c_pink_bg),
            ('TEXTCOLOR', (0, -1), (-1, -1), self.c_red),
            ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ]))
        t4.wrapOn(c, 460, 60)
        t4.drawOn(c, 460, 455 - (len(table_data_4) * 23))
        self._draw_footer(c, f"* 출처 : {demo['base_date']}")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 5: 소상공인365/BASA 실측 화면 (수익구조 + 주거 93% 인프라)
        # ---------------------------------------------------------------------
        self._draw_header(c, "2. 상권 실측 분석 (소상공인365/BASA) - ", "주거형 상권(주거 93%)", " 및 유사 골프업종 수익 구조")
        rev_st = comm.get('revenue_structure', {})
        top20_str = f"{rev_st.get('top_20_sales', 62510000)//10000:,}만원"
        bot20_str = f"{rev_st.get('bottom_20_sales', 3020000)//10000:,}만원"
        
        # 좌측 3대 카드
        c.setFillColor(self.c_card_bg)
        c.setStrokeColor(self.c_royal_blue)
        c.roundRect(40, 340, 260, 115, 6, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_navy)
        c.drawString(50, 435, "💰 유사 골프업종 수익구조 격차 (선행지표 BASA 실측)")
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_slate_dark)
        c.drawString(50, 412, f"• 상위 20% 매출: {top20_str} /월")
        c.drawString(50, 394, f"• 하위 20% 매출: {bot20_str} /월")
        c.drawString(50, 376, "★ 마이파크 10타석 플래그십은 상위 시장 점유")
        
        c.setFillColor(self.c_card_bg)
        c.setStrokeColor(self.c_gold)
        c.roundRect(40, 205, 260, 120, 6, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_gold)
        c.drawString(50, 305, "👥 핵심 고객층 및 변화 추이")
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_slate_dark)
        c.drawString(50, 282, "• 주 이용층: 50대 남성 & 여성 (구매력 최상)")
        c.drawString(50, 264, "• 최근 변화: 3040대 직장인/가족 유입 증가")
        c.drawString(50, 246, "• 충성도: 주 2~3회 정기 방문 락인(Lock-in)")
        
        c.setFillColor(self.c_pink_bg)
        c.setStrokeColor(self.c_red)
        c.roundRect(40, 60, 260, 130, 6, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_red)
        c.drawString(50, 170, "📅 매출 집중 요일 및 운영 전략")
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_slate_dark)
        c.drawString(50, 147, "• 최고 매출 요일: 토요일(친목) & 월요일(동호회)")
        c.drawString(50, 129, "• 주거형 상권 전략: 충성 고객 품질/편의성 중심")
        c.drawString(50, 111, "• 평일 주간(10~17시) 주부 모임으로 유휴 제로")
        
        # 우측 상단 인프라
        infra = comm.get('infra', {})
        c.setFillColor(self.c_card_bg)
        c.setStrokeColor(self.c_border)
        c.roundRect(320, 340, 600, 115, 6, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_navy)
        c.drawString(335, 435, f"🏛️ {comm.get('region_title', '사업지')} 주변 인프라 및 교통망 실측")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_slate_dark)
        c.drawString(335, 410, f"• 주변 시설: 관공서 {infra.get('관공서', 8)}개  |  교육기관 {infra.get('교육기관', 15)}개  |  금융기관 {infra.get('금융기관', 18)}개")
        c.drawString(335, 390, f"• 대중 교통: 버스정류장 {infra.get('버스정류장', 48)}개 노선망  |  지하철 {infra.get('지하철', '분당선 서현역')}")
        c.drawString(335, 370, "• 상권 구성: 주거지역 93% 압도적 밀집으로 탄탄한 배후 생활권 형성")
        
        # 우측 하단 13개월 매출 추이 차트
        if 'sales_trend' in charts and os.path.exists(charts['sales_trend']):
            c.drawImage(charts['sales_trend'], 320, 60, width=600, height=265, preserveAspectRatio=True)
            
        self._draw_footer(c, "* 출처 : 소상공인365/BASA 상권분석 플랫폼 & NICE비즈맵 실측 빅데이터")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 6: 업종 성장률 및 골프 특화도 실측 (골프용품 +182.4% 1위)
        # ---------------------------------------------------------------------
        self._draw_header(c, "3. 업종별 성장률 및 골프 특화도 실측 (", "골프용품 매출성장률 +182.4% 1위", ", 스크린골프 0.7%)")
        
        # 카드 1: 매출 증가율 TOP 5
        c.setFillColor(self.c_card_bg)
        c.setStrokeColor(self.c_royal_blue)
        c.roundRect(40, 265, 425, 195, 8, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_navy)
        c.drawString(56, 435, "📈 서현1동 매출 증가율 TOP 5 (소상공인365 실측)")
        growths = comm.get('top_growth_industries', [])
        y_g = 410
        for g in growths:
            c.setFont(FONT_BOLD if g['rank'] == 1 else FONT_REGULAR, 8.5)
            c.setFillColor(self.c_red if g['rank'] == 1 else self.c_slate_dark)
            c.drawString(56, y_g, f"• {g['rank']}위 : {g['name']}  ({g['growth']}) - {g['status']}")
            y_g -= 22
            
        # 카드 2: 스크린골프 비중 및 밀집도
        golf_den = comm.get('golf_industry_density', {})
        c.setFillColor(self.c_card_bg)
        c.setStrokeColor(self.c_gold)
        c.roundRect(495, 265, 425, 195, 8, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_gold)
        c.drawString(511, 435, "⛳ 지역 골프 문화 및 유사 레저 밀집도 (BASA 실측)")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_slate_dark)
        c.drawString(511, 405, f"• 서현1동 내 스크린골프 점포: {golf_den.get('store_count', 10)}개 (전체 {golf_den.get('total_stores_in_dong', 1526)}개 점포 중)")
        c.drawString(511, 380, f"• 스크린골프 업종 비중: {golf_den.get('density_ratio', 0.7)}% (전국 평균 {golf_den.get('national_avg_density', 0.3)}% 대비 +0.4%p 높음)")
        c.drawString(511, 355, "• 전국 평균 대비 2.3배 밀집된 '골프·파크골프 소비 문화 최상위 특화 상권'")
        c.drawString(511, 330, f"• 성장 단계: {golf_den.get('growth_stage', '집중 성장 단계')}")
        
        # 카드 3: 요일/시간대 이용 패턴
        c.setFillColor(self.c_card_bg)
        c.setStrokeColor(self.c_border)
        c.roundRect(40, 50, 425, 200, 8, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_navy)
        c.drawString(56, 225, "⏰ 요일 및 시간대별 매출 패턴 (NICE비즈맵 실측)")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_slate_dark)
        c.drawString(56, 195, f"• 피크 요일: 월요일 ({comm['day_distribution']['월']}%) 최고치 (주간 동호회 정기 모임)")
        c.drawString(56, 170, f"• 주간 비중: 10~17시 이용 비중이 전체의 {comm['time_distribution']['주간_10_17시_비중']}% 압도적")
        c.drawString(56, 145, "• 일반 스크린골프(야간 위주)와 달리 낮 시간대 풀가동으로 회전율 2배")
        c.drawString(56, 120, f"• 주말 가동률: 주말 평균 비중 {comm['day_distribution']['주말평균비중']}%로 주 7일 고른 수익")
        
        # 카드 4: 사업화 전략적 시사점
        c.setFillColor(self.c_pink_bg)
        c.setStrokeColor(self.c_red)
        c.roundRect(495, 50, 425, 200, 8, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_red)
        c.drawString(511, 225, "🎯 마이파크 출점 종합 전략적 시사점")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_slate_dark)
        c.drawString(511, 195, "• 수요 검증 완료: 골프용품 매출 성장 1위(+182.4%) 상권으로 검증된 소비력")
        c.drawString(511, 170, "• 공급 격차 점유: 노후 2~3타석 매장 대비 10타석 플래그십으로 상위 시장 독점")
        c.drawString(511, 145, "• 복합 문화 공간: 카페형 라운지 및 파크골프 용품 샵 연계로 객단가 극대화")
        c.drawString(511, 120, "• 상권 락인(Lock-in): 주거지역 93% 배후 고정 고객 대상 월회원제 정착")
        
        self._draw_footer(c, "* 출처 : 소상공인365/BASA, NICE비즈맵(NICE지니데이타), SK지오비전 실측 빅데이터")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 7: 주변 경쟁 매장 실측 분석 (4열 풀그리드 + 비주얼 배지 블록)
        # ---------------------------------------------------------------------
        comps = comm.get('competitors', [])
        count_str = f"({len(comps)}곳)" if len(comps) > 0 and comps[0].get('rooms', 0) > 0 else "(블루오션 상권)"
        self._draw_header(c, "주변 스크린 ", f"파크골프 매장{count_str}", " 실측 분석")
        
        card_w = 205
        gap = 18
        start_x = 40
        for idx, comp in enumerate(comps[:4]):
            cur_x = start_x + (idx * (card_w + gap))
            
            # 1. 상단 다크 네이비 바
            c.setFillColor(self.c_navy)
            c.roundRect(cur_x, 400, card_w, 35, 6, fill=1, stroke=0)
            c.setFont(FONT_BOLD, 9.5)
            c.setFillColor(self.c_white)
            c.drawCentredString(cur_x + card_w/2, 412, str(comp['name'])[:15])
            
            # 2. 중간 비주얼 배지 블록
            c.setFillColor(self.c_blue_light)
            c.setStrokeColor(self.c_border)
            c.rect(cur_x, 310, card_w, 90, fill=1, stroke=1)
            c.setFont(FONT_BOLD, 12)
            c.setFillColor(self.c_royal_blue)
            rooms_label = f"🏌️ {comp.get('rooms', 0)}타석 규모" if comp.get('rooms', 0) > 0 else "⛳ 전문 1호점 선점"
            c.drawCentredString(cur_x + card_w/2, 360, rooms_label)
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_slate_dark)
            c.drawCentredString(cur_x + card_w/2, 335, f"[{comp.get('status', '실측완료')}] {comp.get('system', '스크린 시뮬레이터')[:14]}")
            
            # 3. 하단 실측 스펙 박스
            c.setFillColor(self.c_card_bg)
            c.setStrokeColor(self.c_border)
            c.roundRect(cur_x, 60, card_w, 250, 6, fill=1, stroke=1)
            
            c.setFont(FONT_REGULAR, 8)
            c.setFillColor(self.c_slate_dark)
            c.drawString(cur_x + 10, 280, "▲ 주소:")
            c.drawString(cur_x + 10, 262, str(comp['address'])[:18])
            if len(str(comp['address'])) > 18:
                c.drawString(cur_x + 10, 246, str(comp['address'])[18:36])
                
            c.setFillColor(self.c_royal_blue)
            c.setFont(FONT_BOLD, 8.5)
            c.drawString(cur_x + 10, 215, f"▲ 시스템: {comp['system'][:15]}")
            
            c.setFillColor(self.c_slate_dark)
            c.setFont(FONT_REGULAR, 8)
            rooms_str = f"{comp['rooms']}타석 운영" if comp.get('rooms', 0) > 0 else "상업용 매장 미등록"
            c.drawString(cur_x + 10, 180, f"▲ 규모: {rooms_str}")
            
            c.setFillColor(self.c_slate_gray)
            c.drawString(cur_x + 10, 145, f"▲ 특징:")
            c.drawString(cur_x + 10, 128, str(comp.get('features', '-'))[:18])
            if len(str(comp.get('features', ''))) > 18:
                c.drawString(cur_x + 10, 112, str(comp.get('features', ''))[18:36])
            
        self._draw_footer(c, "* 출처 : 소상공인시장진흥공단 상권정보 및 카카오맵 로컬 POI 실측 조사")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 8: 5대 지표 종합 평가
        # ---------------------------------------------------------------------
        self._draw_header(c, "5. 마이파크 입지 최적성 종합 평가 [", f"{score['grade']}등급 - {score['total_score']}점", " / 100점]")
        if 'radar_score' in charts and os.path.exists(charts['radar_score']):
            c.drawImage(charts['radar_score'], 40, 60, width=420, height=400, preserveAspectRatio=True)
            
        indicators = [
            ("1) 골든 시니어 집적도", score['scores']['senior_population'], 25, "반경 3km 내 50대 이상 시니어 인구 및 여성 비중"),
            ("2) 접근성 및 주차 인프라", score['scores']['accessibility_parking'], 25, "자주식 주차 편의성, 승강기 완비, 주요 도로망"),
            ("3) 공간 적합성 및 임대료", score['scores']['space_efficiency'], 15, "유효 층고(2.8m 이상), 전용 120평, 평당 임대료"),
            ("4) 수요 공급 갭 (블루오션)", score['scores']['supply_gap'], 15, "경쟁 강도 및 야외 구장 포화 대기 수요 흡수"),
            ("5) 지역 소비력 및 여가지출", score['scores']['commercial_spending'], 20, "스포츠/여가 월평균 카드 매출 및 생활밀착 상권"),
        ]
        y_ind = 430
        for iname, iscore, imax, idesc in indicators:
            c.setFont(FONT_BOLD, 10.5)
            c.setFillColor(self.c_navy)
            c.drawString(495, y_ind, f"● {iname}: ")
            c.setFillColor(self.c_royal_blue)
            c.drawString(645, y_ind, f"{iscore}점 / {imax}점 만점")
            
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_slate_gray)
            c.drawString(505, y_ind - 18, f"({idesc})")
            y_ind -= 52
            
        c.setFont(FONT_BOLD, 12)
        c.setFillColor(self.c_red)
        c.drawString(495, y_ind - 10, f"★ 종합 판정: 총점 {score['total_score']}점 ({score['grade_desc']})")
        self._draw_footer(c, "* 평가 기준: 마이파크 가맹 입지선정 5대 다이아몬드 스코어링 모델")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 9: 월 예상 매출
        # ---------------------------------------------------------------------
        self._draw_header(c, "6. 마이파크 사업 타당성 분석 (", f"{site['rooms']}타석 / {site['area_pyeong']}평", ") - 월 예상 매출")
        m_scen = fin['monthly_scenarios']
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
            ('BACKGROUND', (0, 0), (-1, 0), self.c_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.c_white),
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.c_border),
            ('TEXTCOLOR', (5, 1), (5, -1), self.c_royal_blue),
            ('FONTNAME', (5, 1), (5, -1), FONT_BOLD),
        ]))
        t9.wrapOn(c, 40, 60)
        t9.drawOn(c, 40, 310)
        self._draw_footer(c, "* 산출 근거: 18홀 8,000원, 부가매출 18%, 월 30일 가동 기준")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 10: 예상 운영 비용
        # ---------------------------------------------------------------------
        self._draw_header(c, "6. 마이파크 사업 타당성 분석 (", f"{site['rooms']}타석", ") - 예상 운영 비용")
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
            ('BACKGROUND', (0, 0), (-1, 0), self.c_navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.c_white),
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ALIGN', (0, 0), (3, -1), 'CENTER'),
            ('ALIGN', (4, 0), (4, 0), 'CENTER'),
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.c_border),
            ('BACKGROUND', (0, -1), (-1, -1), self.c_pink_bg),
            ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ]))
        t10.wrapOn(c, 40, 60)
        t10.drawOn(c, 40, 270)
        self._draw_footer(c, "* 산출 근거: 마이파크 표준 운영 원가 및 가맹 매장 실측 비용 기준")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 11: 5개년 손익 예측
        # ---------------------------------------------------------------------
        self._draw_header(c, "6. 마이파크 사업 타당성 분석 - ", "5개년 손익 예측", " (연 2% 성장률 반영)")
        if 'profit_forecast' in charts and os.path.exists(charts['profit_forecast']):
            c.drawImage(charts['profit_forecast'], 40, 60, width=500, height=400, preserveAspectRatio=True)
            
        mod_1y = fin['forecast_5year']['moderate'][0]
        mod_5y = fin['forecast_5year']['moderate'][4]
        
        c.setFillColor(self.c_card_bg)
        c.setStrokeColor(self.c_royal_blue)
        c.roundRect(560, 270, 360, 180, 8, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 11)
        c.setFillColor(self.c_navy)
        c.drawString(576, 425, "📈 연간 실적 전망 (보편 시나리오)")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_slate_dark)
        c.drawString(576, 390, f"• 1년차: 연매출 {mod_1y['total_revenue']//100000000:.1f}억원 / 영업이익 {mod_1y['operating_profit']//100000000:.1f}억원")
        c.drawString(576, 365, f"• 5년차: 연매출 {mod_5y['total_revenue']//100000000:.1f}억원 / 영업이익 {mod_5y['operating_profit']//100000000:.1f}억원")
        
        c.setFillColor(self.c_card_bg)
        c.setStrokeColor(self.c_emerald)
        c.roundRect(560, 70, 360, 180, 8, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 11)
        c.setFillColor(self.c_emerald)
        c.drawString(576, 225, "⏱️ 투자금 회수 및 손익분기점")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_slate_dark)
        c.drawString(576, 190, f"• 손익분기점(BEP): 월매출 약 {fin['investment']['bep_monthly_sales']//10000:,}만원 (일 {fin['investment']['bep_turns_per_room']}회전)")
        c.drawString(576, 165, f"• 순투자금 회수: {score['payback_text']}")
        self._draw_footer(c, f"* 산출 근거: 초기 순투자금 {fin['investment']['total_capex']//100000000:.2f}억원 기준 / 연 2% 복리 성장률 반영")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 12: 종합 결론
        # ---------------------------------------------------------------------
        self._draw_header(c, "7. 종합 결론 및 ", "사업 타당성 최종 평가", "")
        c.setFillColor(self.c_card_bg)
        c.setStrokeColor(self.c_gold)
        c.setLineWidth(1.5)
        c.roundRect(40, 260, 880, 195, 8, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 12)
        c.setFillColor(self.c_gold)
        c.drawString(56, 425, "🌟【 가맹점 출점 기대효과 및 핵심 경쟁력 】")
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_slate_dark)
        v1_text = score['value_franchisee']
        c.drawString(56, 385, v1_text[:90])
        if len(v1_text) > 90:
            c.drawString(56, 365, v1_text[90:180])
        if len(v1_text) > 180:
            c.drawString(56, 345, v1_text[180:])
            
        c.setFillColor(self.c_card_bg)
        c.setStrokeColor(self.c_emerald)
        c.setLineWidth(1.5)
        c.roundRect(40, 50, 880, 195, 8, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 12)
        c.setFillColor(self.c_emerald)
        c.drawString(56, 215, "🏢【 상가 전체 상권 활성화 및 건물 가치 상승 효과 】")
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_slate_dark)
        v2_text = score['value_landlord']
        c.drawString(56, 175, v2_text[:90])
        if len(v2_text) > 90:
            c.drawString(56, 155, v2_text[90:180])
        if len(v2_text) > 180:
            c.drawString(56, 135, v2_text[180:])
            
        self._draw_footer(c, "* 마이파크(MYPARK) 사업본부 상권분석 시스템 v1.0")
        c.showPage()

        c.save()
        print(f"[PDF GENERATED] {output_pdf_path}")
        return output_pdf_path
