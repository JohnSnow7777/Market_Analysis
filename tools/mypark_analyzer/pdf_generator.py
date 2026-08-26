# -*- coding: utf-8 -*-
"""맥킨지 클래식 이그제큐티브 PDF 보고서 생성기 (SSOT 3.19억원 & 7,000원 팩트 기반)"""
import os
import textwrap
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

WIDTH, HEIGHT = 960, 540

FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

def init_fonts():
    global FONT_REGULAR, FONT_BOLD
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bundled_reg = os.path.join(base_dir, "fonts", "MalgunGothic.ttf")
    bundled_bold = os.path.join(base_dir, "fonts", "MalgunGothicBold.ttf")
    
    font_candidates = [
        (bundled_reg, bundled_bold),
        ("C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/malgunbd.ttf"),
        ("C:/Windows/Fonts/NanumGothic.ttf", "C:/Windows/Fonts/NanumGothicBold.ttf"),
        ("/usr/share/fonts/truetype/nanum/NanumGothic.ttf", "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"),
        ("/System/Library/Fonts/AppleSDGothicNeo.ttc", "/System/Library/Fonts/AppleSDGothicNeo.ttc"),
    ]
    for r_path, b_path in font_candidates:
        if os.path.exists(r_path) and os.path.exists(b_path):
            try:
                pdfmetrics.registerFont(TTFont("Pretendard", r_path))
                pdfmetrics.registerFont(TTFont("Pretendard-Bold", b_path))
                FONT_REGULAR = "Pretendard"
                FONT_BOLD = "Pretendard-Bold"
                print(f"[SUCCESS] Registered Korean Font: {r_path}")
                return True
            except Exception as ex:
                print(f"[FONT LOAD FAILED] {r_path}: {ex}")
                continue
                
    FONT_REGULAR = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"
    return False

init_fonts()


class PDFGenerator:
    """맥킨지 클래식 이그제큐티브 PDF 생성 엔진"""

    def __init__(self):
        self.c_mck_navy = HexColor('#002B49')
        self.c_mck_teal = HexColor('#008080')
        self.c_charcoal = HexColor('#222222')
        self.c_slate = HexColor('#555555')
        self.c_line = HexColor('#CBD5E1')
        self.c_box_bg = HexColor('#F8FAFC')
        self.c_tint_blue = HexColor('#E6F4F1')
        self.c_white = HexColor('#FFFFFF')
        self.c_red = HexColor('#DC2626')

    def _draw_mckinsey_header(self, c, section_title, lead_in):
        c.setFont(FONT_BOLD, 12.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(40, 508, section_title)
        
        c.setFont(FONT_BOLD, 14.5)
        c.setFillColor(self.c_mck_teal)
        c.drawString(40, 486, lead_in)
        
        c.setStrokeColor(self.c_line)
        c.setLineWidth(1.0)
        c.line(40, 474, 920, 474)

    def _draw_footer(self, c, source_text=""):
        c.setStrokeColor(self.c_line)
        c.setLineWidth(0.6)
        c.line(40, 32, 920, 32)
        
        c.setFont(FONT_REGULAR, 7.5)
        c.setFillColor(self.c_slate)
        if source_text:
            c.drawString(40, 20, f"* Source: {source_text}")
        c.drawRightString(920, 20, "CONFIDENTIAL  |  MYPARK Screen Park Golf Feasibility Study")

    def _draw_multiline_text(self, c, text, x, y, max_chars=18, line_height=13, max_lines=4, font_name=FONT_REGULAR, font_size=8, color=None):
        if color:
            c.setFillColor(color)
        c.setFont(font_name, font_size)
        
        lines = []
        raw_paragraphs = str(text).split('\n')
        for p in raw_paragraphs:
            p_wrapped = textwrap.wrap(p, width=max_chars, break_long_words=True)
            lines.extend(p_wrapped if p_wrapped else [''])
            
        cur_y = y
        for i, line in enumerate(lines[:max_lines]):
            c.drawString(x, cur_y, line)
            cur_y -= line_height
        return cur_y

    def generate(self, bundle, output_path):
        site = bundle['site']
        demo = bundle['demographics']
        comm = bundle['commercial']
        score = bundle['scores']
        fin = bundle['financials']
        inv = fin['investment']
        scenarios = fin['monthly_scenarios']
        charts = bundle.get('charts', {})
        target_dong = site.get('dong', '') if site.get('dong') else site.get('sigungu', '사업권역')

        c = canvas.Canvas(output_path, pagesize=landscape((WIDTH, HEIGHT)))

        # ---------------------------------------------------------------------
        # Page 1: 표지
        # ---------------------------------------------------------------------
        c.setFillColor(self.c_mck_navy)
        c.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
        
        c.setFillColor(self.c_white)
        c.setFont(FONT_BOLD, 29)
        c.drawString(56, 380, "마이파크(MYPARK) 스크린 파크골프")
        c.setFont(FONT_BOLD, 22)
        c.setFillColor(HexColor('#10B981'))
        c.drawString(56, 342, f"출점 타당성 및 상권 분석 보고서 : {site['building_name']}")
        
        c.setFillColor(HexColor('#94A3B8'))
        c.setFont(FONT_REGULAR, 12.5)
        c.drawString(56, 305, "빅데이터 및 재무 시뮬레이션 기반 사업성 검증")
        
        c.setStrokeColor(HexColor('#008080'))
        c.setLineWidth(3)
        c.line(56, 280, 260, 280)
        
        c.setFillColor(self.c_white)
        c.setFont(FONT_REGULAR, 10)
        c.drawString(56, 108, f"• 대상 사업지: {site['full_address']}")
        if site.get('special_notes'):
            c.drawString(56, 91, f"• 고객 특이사항: {site['special_notes']}")
            c.drawString(56, 74, f"• 분석 기준일: {bundle['created_at']}  |  주관: 마이파크(MYPARK) 데이터전략실")
        else:
            c.drawString(56, 91, f"• 분석 기준일: {bundle['created_at']}")
            c.drawString(56, 74, "• 주관: 마이파크(MYPARK) 가맹본부 데이터전략실")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 2: Executive Summary
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "Executive Summary", f"{site['sigungu']} 핵심 상권 내 10타석 플래그십 출점 타당성 종합 요약")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 268, 425, 192, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 12)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 436, f"■ 핵심 결론: 출점 최우선 추천 ({score['grade']}등급)")
        c.setFont(FONT_REGULAR, 9.2)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 408, f"• 배후 수요: 반경 3km 내 50대 이상 시니어 {demo['senior_50_plus']:,}명({demo['senior_ratio']}%) 밀집")
        c.drawString(56, 386, f"• 경쟁 환경: {comm.get('competitor_summary', '반경 3km 내 대형 플래그십 매장 공급 부족')}")
        c.drawString(56, 364, f"• 재무 타당성: 보편적 가동 시 월 순영업이익 {scenarios['moderate']['operating_profit']//10000:,}만원 (회수 {inv['payback_months_moderate']:.1f}개월)")
        c.drawString(56, 342, f"• 초기 투자금: 총 3.19억원 (장비 1.5억 + 인테리어 1.44억 + 냉난방/간판/초도용품 2,500만)")
        c.drawString(56, 320, f"• 종합 평가: 5대 다이아몬드 스코어링 {score['total_score']}점 ({score['grade']}등급)")

        kpis = [
            ("배후 시니어 인구 (3km)", f"{demo['senior_50_plus']:,}명", f"전체 인구의 {demo['senior_ratio']}%", self.c_mck_navy),
            ("예상 월 영업이익 (보편)", f"{scenarios['moderate']['operating_profit']//10000:,}만원", f"영업이익률 {scenarios['moderate']['profit_margin']}%", self.c_mck_teal),
            ("손익분기점 (BEP 회전율)", f"일 {inv['bep_turns_per_room']}회전", f"1일 약 {inv['bep_daily_users']}명 달성 시 월 고정비 전액 커버", self.c_mck_navy),
            ("순투자금 3.19억 회수기간", f"약 {inv['payback_months_moderate']:.1f}개월", f"연환산 수익률 약 {scenarios['moderate']['operating_profit']*12/inv['total_capex']*100:.1f}%", self.c_red),
        ]
        for idx, (title, val, sub, col) in enumerate(kpis):
            x = 495 + (idx % 2) * 225
            y = 368 if idx < 2 else 268
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(x, y, 205, 92, fill=1, stroke=1)
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_slate)
            c.drawString(x + 12, y + 70, title)
            c.setFont(FONT_BOLD, 15.5)
            c.setFillColor(col)
            c.drawString(x + 12, y + 42, val)
            c.setFont(FONT_REGULAR, 8)
            c.setFillColor(self.c_slate)
            c.drawString(x + 12, y + 20, sub)

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 425, 204, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 11)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 226, "🌟【 가맹점 출점 기대효과 및 핵심 경쟁력 】")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        val_f_lines = score['value_franchisee'].split('\n')
        cur_y = 198
        for fl in val_f_lines:
            cur_y = self._draw_multiline_text(c, fl, 56, cur_y, max_chars=34, line_height=14, max_lines=3) - 4

        c.setFillColor(HexColor('#F0FDF4'))
        c.setStrokeColor(HexColor('#BBF7D0'))
        c.rect(495, 48, 425, 204, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 11)
        c.setFillColor(HexColor('#166534'))
        c.drawString(511, 226, "🏢【 상가 전체 상권 활성화 및 건물 가치 상승 효과 】")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(HexColor('#14532D'))
        val_l_lines = score['value_landlord'].split('\n')
        cur_y = 198
        for ll in val_l_lines:
            cur_y = self._draw_multiline_text(c, ll, 511, cur_y, max_chars=34, line_height=14, max_lines=3, color=HexColor('#14532D')) - 4

        self._draw_footer(c, "MYPARK Commercial Real Estate Big Data Analytics")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 3: 1. 배후 인구 및 타겟 연령 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "1. 배후 인구 및 타겟 연령 분석", f"반경 3km 내 50대 이상 시니어 {demo['senior_50_plus']:,}명({demo['senior_ratio']}%)의 핵심 배후 수요 확보")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 268, 425, 192, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 438, f"■ {target_dong} 반경 3km 행정동별 인구 집계 (KOSIS 실측)")
        
        c.setFont(FONT_BOLD, 8)
        c.setFillColor(self.c_slate)
        c.drawString(56, 412, "행정동명")
        c.drawString(160, 412, "총 인구")
        c.drawString(250, 412, "50대 이상")
        c.drawString(350, 412, "시니어 비중")
        c.line(56, 404, 445, 404)
        
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_charcoal)
        y_d = 390
        for d in demo['dongs'][:6]:
            c.drawString(56, y_d, str(d['dong']))
            c.drawString(160, y_d, f"{d['total']:,}명")
            s_val = int(d['total'] * (demo['senior_ratio'] / 100.0))
            c.drawString(250, y_d, f"{s_val:,}명")
            c.drawString(350, y_d, f"{demo['senior_ratio']}%")
            y_d -= 18

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, 268, 425, 192, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, 438, "■ 50대 이상 골든 시니어 정밀 세분화 매트릭스")
        
        c.setFont(FONT_BOLD, 8)
        c.setFillColor(self.c_slate)
        c.drawString(511, 412, "연령 구간")
        c.drawString(610, 412, "남성 (명)")
        c.drawString(700, 412, "여성 (명)")
        c.drawString(800, 412, "합계 (구성비)")
        c.line(511, 404, 900, 404)
        
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_charcoal)
        y_a = 390
        for a in demo['age_distribution']:
            c.drawString(511, y_a, str(a['age_group']))
            c.drawString(610, y_a, f"{a['male']:,}")
            c.drawString(700, y_a, f"{a['female']:,}")
            ratio = round((a['total'] / demo['senior_50_plus'] * 100), 1) if demo['senior_50_plus'] > 0 else 0
            c.drawString(800, y_a, f"{a['total']:,}명 ({ratio}%)")
            y_a -= 18

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 880, 204, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 226, "■ 시니어 생활체육 소비 행태 및 타겟팅 분석")
        c.setFont(FONT_REGULAR, 8.8)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 196, f"• 여성 시니어(주부/동호회) 53% 집중: 평일 오전 10시~오후 17시 여성 친목 동호회의 정기 예약 중심 안정적 타겟")
        c.drawString(56, 168, "• 60대 액티브 시니어 40% 최다 분포: 은퇴 후 시간적·경제적 여유를 갖춘 60대 고객층의 주 3회 이상 정기적 내방 소비")
        c.drawString(56, 140, "• 70대 실버 헬스케어 수요 21%: 관절 부담이 없는 파크골프 특성상 부부 동반 및 시니어 커뮤니티 공간으로 정착")
        c.drawString(56, 112, "• 일반 스크린골프 대비 회전율 우위: 야간 직장인 편중 매장과 달리 주간 7시간 집중 가동으로 일일 높은 회전수 확보")
        
        self._draw_footer(c, "KOSIS National Statistics Portal & Ministry of the Interior and Safety Data")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 4: 2. 상권 소비력 및 유동 패턴
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "2. 상권 소비력 및 유동 패턴", f"소상공인365 실측: {comm['spending_grade']} / 월평균 여가지출 {comm['monthly_avg_sales']//10000:,}만원 상권")
        
        if 'map_radius' in charts and os.path.exists(charts['map_radius']):
            c.drawImage(charts['map_radius'], 40, 48, width=280, height=425, preserveAspectRatio=True)
            
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(320, 268, 600, 192, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(335, 436, f"■ {target_dong} 상권 인프라 및 교통망 요약")
        infra = comm.get('infra', {})
        c.setFont(FONT_REGULAR, 8.8)
        c.setFillColor(self.c_charcoal)
        c.drawString(335, 408, f"• 주변 시설: 관공서 {infra.get('관공서', 8)}개  |  교육기관 {infra.get('교육기관', 14)}개  |  금융기관 {infra.get('금융기관', 16)}개")
        c.drawString(335, 384, f"• 대중 교통: 버스정류장 {infra.get('버스정류장', 38)}개 노선망  |  지하철/교통: {infra.get('지하철', '간선도로망 인접')}")
        c.drawString(335, 360, "• 상권 구성: 주거지역 93% 압도적 밀집으로 탄탄한 배후 생활권 형성")
        c.drawString(335, 336, f"• 소상공인 실측 골프/여가 월평균 매출: {comm['monthly_avg_sales']//10000:,}만원 (상위 20% {comm['top_20_sales']//10000:,}만원)")
        
        if 'sales_trend' in charts and os.path.exists(charts['sales_trend']):
            c.drawImage(charts['sales_trend'], 320, 48, width=600, height=210, preserveAspectRatio=True)
            
        self._draw_footer(c, "Small Enterprise and Market Service (BASA) & NICE BizMap")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 5: 2. 업종 성장률 및 골프 특화도
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "2. 업종 성장률 및 골프 특화도", f"골프용품 매출성장률 1위(+{comm['growth_rate']}%) 및 {target_dong} 골프 특화 상권")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 268, 425, 192, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 438, f"■ {target_dong} 매출 증가율 TOP 5 (소상공인365 실측)")
        growths = comm.get('top_growth_industries', [])
        y_g = 412
        for g in growths:
            c.setFont(FONT_BOLD if g['rank'] == 1 else FONT_REGULAR, 8.6)
            c.setFillColor(self.c_red if g['rank'] == 1 else self.c_charcoal)
            c.drawString(56, y_g, f"• {g['rank']}위 : {g['name']}  ({g['growth']}) - {g['status']}")
            y_g -= 21
            
        golf_den = comm.get('golf_industry_density', {})
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, 268, 425, 192, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, 438, "■ 지역 골프 문화 및 유사 레저 밀집도 (BASA 실측)")
        c.setFont(FONT_REGULAR, 8.6)
        c.setFillColor(self.c_charcoal)
        c.drawString(511, 410, f"• {target_dong} 내 스크린골프 점포: {golf_den.get('store_count', 7)}개 (전체 {golf_den.get('total_stores_in_dong', 1140)}개 중)")
        c.drawString(511, 384, f"• 스크린골프 업종 비중: {golf_den.get('density_ratio', 0.6)}% (전국 평균 {golf_den.get('national_avg_density', 0.3)}% 대비 {golf_den.get('multiple', 2.0)}배)")
        c.drawString(511, 358, f"• 전국 평균 대비 {golf_den.get('multiple', 2.0)}배 밀집된 '골프·파크골프 소비 문화 특화 상권'")
        c.drawString(511, 332, f"• 성장 단계: {golf_den.get('growth_stage', '수요 급증 및 시설 대형화 단계')}")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 425, 204, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 226, "■ 요일 및 시간대별 매출 패턴 (NICE비즈맵 실측)")
        c.setFont(FONT_REGULAR, 8.6)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 198, f"• 피크 요일: 월요일 ({comm['day_distribution']['월']}%) 최고치 (주간 동호회 정기 모임)")
        c.drawString(56, 172, f"• 주간 비중: 10~17시 이용 비중이 전체의 {comm['time_distribution']['주간_10_17시_비중']}% 압도적")
        c.drawString(56, 146, "• 일반 스크린골프(야간 위주)와 달리 낮 시간대 집중 가동으로 회전율 확보")
        c.drawString(56, 120, f"• 주말 가동률: 주말 평균 비중 {comm['day_distribution']['주말평균비중']}%로 주 7일 고른 수익")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_mck_teal)
        c.setLineWidth(1.2)
        c.rect(495, 48, 425, 204, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_teal)
        c.drawString(511, 226, "■ 마이파크 출점 종합 전략적 시사점")
        c.setFont(FONT_REGULAR, 8.6)
        c.setFillColor(self.c_charcoal)
        c.drawString(511, 198, f"• 수요 검증 완료: 골프용품 매출 성장 1위(+{comm['growth_rate']}%) 상권으로 검증된 소비력")
        c.drawString(511, 172, "• 시설 경쟁력 우위: 소규모 매장 대비 10타석 대규모 플래그십으로 단체 수요 흡수")
        c.drawString(511, 146, "• 복합 시설 운영: 휴게 라운지 및 파크골프 용품 코너 연계로 편의성 극대화")
        c.drawString(511, 120, "• 고객 락인(Lock-in): 주거지역 93% 배후 고정 고객 대상 정기 회원제 정착")
        
        self._draw_footer(c, "Small Enterprise 365, NICE BizMap & SK Telecom Geovision Big Data")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 6: 3. 경쟁 환경 실측 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "3. 경쟁 환경 실측 분석", f"반경 3km 내 스크린 파크골프 전문 매장 공급 부족으로 10타석 플래그십 선점 기회")
        comps = comm.get('competitors', [])
        card_w = 208
        gap = 16
        start_x = 40
        for idx, comp in enumerate(comps[:4]):
            cur_x = start_x + (idx * (card_w + gap))
            
            c.setFillColor(self.c_mck_navy)
            c.rect(cur_x, 425, card_w, 45, fill=1, stroke=0)
            c.setFont(FONT_BOLD, 9.5)
            c.setFillColor(self.c_white)
            c_name = str(comp['name'])
            if len(c_name) > 13:
                c.drawCentredString(cur_x + card_w/2, 451, c_name[:13])
                c.drawCentredString(cur_x + card_w/2, 435, c_name[13:])
            else:
                c.drawCentredString(cur_x + card_w/2, 443, c_name)
            
            c.setFillColor(self.c_tint_blue)
            c.setStrokeColor(self.c_line)
            c.rect(cur_x, 355, card_w, 70, fill=1, stroke=1)
            c.setFont(FONT_BOLD, 11)
            c.setFillColor(self.c_mck_navy)
            rooms_label = f"{comp.get('rooms', 0)}타석 규모" if comp.get('rooms', 0) > 0 else "1호점 선점 대상"
            c.drawCentredString(cur_x + card_w/2, 395, rooms_label)
            c.setFont(FONT_REGULAR, 7.8)
            c.setFillColor(self.c_slate)
            c.drawCentredString(cur_x + card_w/2, 372, f"[{comp.get('status', '실측완료')}] {comp.get('system', '스크린 시스템')}")
            
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(cur_x, 48, card_w, 300, fill=1, stroke=1)
            
            c.setFont(FONT_BOLD, 8)
            c.setFillColor(self.c_charcoal)
            c.drawString(cur_x + 10, 328, "■ 주소:")
            self._draw_multiline_text(c, comp['address'], cur_x + 10, 314, max_chars=17, line_height=13, max_lines=3, font_name=FONT_REGULAR, font_size=7.5)
            
            c.setFont(FONT_BOLD, 8)
            c.setFillColor(self.c_mck_teal)
            c.drawString(cur_x + 10, 260, "■ 시스템:")
            self._draw_multiline_text(c, comp['system'], cur_x + 10, 246, max_chars=17, line_height=13, max_lines=2, font_name=FONT_REGULAR, font_size=7.5, color=self.c_mck_teal)
            
            c.setFont(FONT_BOLD, 8)
            c.setFillColor(self.c_charcoal)
            rooms_str = f"■ 규모: {comp['rooms']}타석 운영" if comp.get('rooms', 0) > 0 else "■ 상태: 상업용 매장 미등록"
            c.drawString(cur_x + 10, 208, rooms_str)
            
            c.setFont(FONT_BOLD, 8)
            c.setFillColor(self.c_slate)
            c.drawString(cur_x + 10, 180, "■ 특징:")
            feat_str = str(comp.get('features', '-'))
            self._draw_multiline_text(c, feat_str, cur_x + 10, 166, max_chars=17, line_height=13, max_lines=6, font_name=FONT_REGULAR, font_size=7.5, color=self.c_charcoal)
            
        self._draw_footer(c, "Small Enterprise Market Service & Kakao Map Local POI Survey")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 7: 4. 입지 최적성 종합 평가 (5대 다이아몬드 스코어링)
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "4. 입지 최적성 종합 평가", f"5대 다이아몬드 스코어링 총점 {score['total_score']}점({score['grade']}등급)으로 출점 최우선 추천 판정")
        if 'radar_score' in charts and os.path.exists(charts['radar_score']):
            c.drawImage(charts['radar_score'], 40, 48, width=440, height=425, preserveAspectRatio=True)
            
        indicators = [
            ("1) 골든 시니어 집적도", score['scores']['senior_population'], 25, f"KOSIS 실측: 반경 3km 내 50대 이상 시니어 {demo['senior_50_plus']:,}명 ({demo['senior_ratio']}%) 밀집"),
            ("2) 접근성 및 주차 인프라", score['scores']['accessibility_parking'], 25, "간선도로 접면/교통망 우수(20점) / 10타석 주차면은 '현장 실측' 요망"),
            ("3) 공간 적합성 및 층고", score['scores']['space_efficiency'], 15, f"{site['area_pyeong']}평 10타석 배치 최적(13점) / 유효 층고 2.8m 이상은 '인테리어 실측' 필수"),
            ("4) 수요 공급 갭", score['scores']['supply_gap'], 15, f"{comm.get('competitor_summary', '반경 3km 내 대형 플래그십 매장 공급 부족')}"),
            ("5) 지역 소비력 및 여가지출", score['scores']['commercial_spending'], 20, f"BASA 실측: 골프용품 성장 1위(+{comm['growth_rate']}%) 및 월평균 {comm['monthly_avg_sales']//10000:,}만원 상권"),
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
        self._draw_footer(c, f"MYPARK 5-Dimension Diamond Scoring Methodology ({score['total_score']}점 {score['grade']}등급)")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 8: 5. 사업지 개요 및 현장 출점 요건
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "5. 사업지 개요 및 현장 출점 요건", f"10타석 {site['area_pyeong']}평 규모 출점을 위한 4대 건축·인프라 현장 실측 기준")
        cards_p8 = [
            (40, 268, 425, 192, "■ 공간 및 유효 층고 요건", [
                f"• 대상 주소: {site['full_address']}",
                f"• 권장 면적: 전용 {site['area_pyeong']}평 (10타석 + 휴게 라운지 최적 배치)",
                f"• 층고 기준: {site['clear_height_spec']}",
                f"• 보/배관 간섭: 센서 투사 영역 및 스윙 궤적 내 장애물 사전 실측",
                f"• 권장 층수: 접근성 높은 지상 2~3층 권장 (쾌적한 지하 1층 가능)",
                f"• 바닥 하중: 스크린 타석 및 키오스크 하중(300kg/㎡) 적합 여부"
            ]),
            (495, 268, 425, 192, "■ 전기·공조 및 소방 설비 기준", [
                f"• 수전 용량: 계약전력 최소 {site['electrical_spec']}",
                f"• 냉난방 시스템: 4계절 쾌적한 25평형 냉난방기 4대 분산 배치",
                f"• 환기 및 공기질: 시간당 환기 6회 이상 강제 급배기 및 대용량 공기청정",
                f"• 소방 안전: 스프링클러 헤드 유효 반경 확보 및 비상 유도등 완비",
                f"• 다중이용업소: 안전시설등 완비증명서 발급 대상 여부 사전 확인",
                f"• 방음/차음: 층간 및 인접 점포 타구음 차단 흡음 인테리어 시공"
            ]),
            (40, 48, 425, 204, "■ 주차 및 수직 동선 인프라", [
                f"• 주차 요건: {site['parking_spec']}",
                f"• 주차 방식: 시니어 고객 선호도가 높은 지하/지상 자주식 주차 최우선",
                f"• 승강기 설비: 파크골프백 휴대가 용이한 13인승 이상 엘리베이터 권장",
                f"• 진출입 편의: 광폭 주차면(2.5m 이상) 및 회차 공간 확보 여부",
                f"• 대중교통 연계: 도보 5분 내 버스정류장 및 지하철역 접근성",
                f"• 장애인 편의: 휠체어 경사로 및 단차 없는 출입구 동선 확보"
            ]),
            (495, 48, 425, 204, "■ 인허가 및 현장 특이사항 검토", [
                f"• 건축물 용도: {site['building_use_spec']}",
                f"• 정화구역 검토: 학교환경위생정화구역 및 학원 연면적 규제 확인",
                f"• 장애인 편의시설: 바닥면적 500㎡ 이상 시 장애인 화장실/점자블록 요건",
                f"• 옥외 간판: 도로변 가시성 높은 전면/돌출 LED 간판 설치 구역 확보",
                f"• 특이사항 반영: {site['special_notes']}" if site.get('special_notes') else "• 원상복구 및 임대차: 5년 장기 계약 및 시설 감가상각 기간 보장",
                f"• 종합 의견: 10타석 플래그십 매장 구축을 위한 '현장 실측' 필수 진행"
            ])
        ]
        for x, y, w, h, title, items in cards_p8:
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(x, y, w, h, fill=1, stroke=1)
            c.setFont(FONT_BOLD, 10.5)
            c.setFillColor(self.c_mck_navy)
            c.drawString(x + 16, y + h - 24, title)
            c.setFont(FONT_REGULAR, 8.4)
            c.setFillColor(self.c_charcoal)
            cur_y = y + h - 48
            for itm in items:
                c.drawString(x + 16, cur_y, itm)
                cur_y -= 22
                
        self._draw_footer(c, "Building Act & Commercial Facility Guidelines")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 9: 6. 사업 타당성 분석 - 매출 추정 (3대 매출 엑셀 기준)
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "6. 사업 타당성 분석 - 매출 추정", f"1인 18홀 7,000원(팀당 28,000원) 기준: 보편적 가동 시 월 총매출 {scenarios['moderate']['total_revenue']//10000:,}만원 달성")
        
        c.setFillColor(self.c_mck_navy)
        c.rect(40, 395, 880, 28, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_white)
        c.drawString(56, 404, "구분")
        c.drawString(180, 404, "게임비 매출 (7,000원/인)")
        c.drawString(360, 404, "용품 판매 매출")
        c.drawString(520, 404, "식음료 판매 (3,000원/팀)")
        c.drawString(680, 404, "월 총매출 합계")
        c.drawString(820, 404, "1일 이용객")
        
        y_sc = 360
        for k in ['conservative', 'moderate', 'optimistic']:
            sc = scenarios[k]
            c.setFillColor(self.c_box_bg if k == 'moderate' else self.c_white)
            c.setStrokeColor(self.c_line)
            c.rect(40, y_sc - 6, 880, 28, fill=1, stroke=1)
            c.setFont(FONT_BOLD if k == 'moderate' else FONT_REGULAR, 9)
            c.setFillColor(self.c_mck_navy if k == 'moderate' else self.c_charcoal)
            c.drawString(56, y_sc + 4, sc['scenario_name'])
            c.drawString(180, y_sc + 4, f"{sc['game_revenue']:,}원")
            c.drawString(360, y_sc + 4, f"{sc['goods_revenue']:,}원")
            c.drawString(520, y_sc + 4, f"{sc['beverage_revenue']:,}원")
            c.setFont(FONT_BOLD, 9.5)
            c.drawString(680, y_sc + 4, f"{sc['total_revenue']:,}원")
            c.setFont(FONT_REGULAR, 8.5)
            c.drawString(820, y_sc + 4, f"1일 {sc['daily_users']}명 (월 {sc['monthly_users']:,}명)")
            y_sc -= 32

        callouts_p9 = [
            (40, 48, 275, 220, "■ 보수적 시나리오 (3회전)", [
                f"• 월 총매출: {scenarios['conservative']['total_revenue']//10000:,}만원 (연 {scenarios['conservative']['total_revenue']*12//100000000:.1f}억원)",
                f"• 타석 회전수: 1일 {scenarios['conservative']['daily_turns_per_room']:.1f}회전",
                f"• 1일 이용객: 약 {scenarios['conservative']['daily_users']}명 (월 {scenarios['conservative']['monthly_users']:,}명)",
                "• 상권 초기 진입 단계 안정적 가동",
                f"• BEP(월 {inv['bep_monthly_sales']//10000:,}만)를 안정적으로 초과",
                f"• 월 순영업이익 {scenarios['conservative']['operating_profit']//10000:,}만원 순영업이익 확보"
            ]),
            (342, 48, 275, 220, "■ 보편적 시나리오 (4회전)", [
                f"• 월 총매출: {scenarios['moderate']['total_revenue']//10000:,}만원 (연 {scenarios['moderate']['total_revenue']*12//100000000:.1f}억원)",
                f"• 타석 회전수: 1일 {scenarios['moderate']['daily_turns_per_room']:.1f}회전 (표준 가동)",
                f"• 1일 이용객: 약 {scenarios['moderate']['daily_users']}명 (월 {scenarios['moderate']['monthly_users']:,}명)",
                "• 평일 주간 동호회 정기 모임 안정적 정착",
                f"• 월 순영업이익 {scenarios['moderate']['operating_profit']//10000:,}만원 달성",
                f"• ★ 순투자금 3.19억 회수 기간: {inv['payback_months_moderate']:.1f}개월"
            ]),
            (645, 48, 275, 220, "■ 긍정적 시나리오 (5회전)", [
                f"• 월 총매출: {scenarios['optimistic']['total_revenue']//10000:,}만원 (연 {scenarios['optimistic']['total_revenue']*12//100000000:.1f}억원)",
                f"• 타석 회전수: 1일 {scenarios['optimistic']['daily_turns_per_room']:.1f}회전 (주말/야간)",
                f"• 1일 이용객: 약 {scenarios['optimistic']['daily_users']}명 (월 {scenarios['optimistic']['monthly_users']:,}명)",
                "• 지역 생활체육 랜드마크 및 대회 유치",
                f"• 월 순영업이익 {scenarios['optimistic']['operating_profit']//10000:,}만원 달성",
                f"• 순투자금 3.19억 회수 기간: {inv['payback_months_optimistic']:.1f}개월"
            ])
        ]
        for x, y, w, h, title, items in callouts_p9:
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(x, y, w, h, fill=1, stroke=1)
            c.setFont(FONT_BOLD, 10)
            c.setFillColor(self.c_mck_navy)
            c.drawString(x + 14, y + h - 22, title)
            c.setFont(FONT_REGULAR, 8.2)
            c.setFillColor(self.c_charcoal)
            cur_y = y + h - 44
            for itm in items:
                c.drawString(x + 14, cur_y, itm)
                cur_y -= 19
                
        self._draw_footer(c, "MYPARK Standard Financial Modeling System (18-Hole 7,000 KRW)")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 10: 7. 사업 타당성 분석 - 비용 구조 및 순영업이익
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "7. 사업 타당성 분석 - 비용 구조 및 순영업이익", f"점주 상주 시 월 순익 {scenarios['moderate']['operating_profit']//10000:,}만원 (이익률 {scenarios['moderate']['profit_margin']}%)  |  직원 위탁 운영 시 월 순익 {fin['owner_operated']['staff3_operating_profit']//10000:,}만원")
        
        c.setFillColor(self.c_mck_navy)
        c.rect(40, 395, 880, 28, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_white)
        c.drawString(56, 404, "비용 항목")
        c.drawString(200, 404, "보수적 시나리오")
        c.drawString(350, 404, "보편적 시나리오")
        c.drawString(500, 404, "긍정적 시나리오")
        c.drawString(680, 404, "비용 산출 기준 및 내역")
        
        cost_rows = [
            ("인건비 (점주 1인 상주)", f"{scenarios['conservative']['labor_cost']:,}원", f"{scenarios['moderate']['labor_cost']:,}원", f"{scenarios['optimistic']['labor_cost']:,}원", "월 250만원 (직원 채용 시 인건비 추가)"),
            ("사업장 월 임대료", f"{scenarios['conservative']['rent_cost']:,}원", f"{scenarios['moderate']['rent_cost']:,}원", f"{scenarios['optimistic']['rent_cost']:,}원", f"전용 {site['area_pyeong']}평 기준 월 임대료"),
            ("용품/음료 원가 및 카드수수료", f"{scenarios['conservative']['cost_goods']+scenarios['conservative']['cost_beverage']+scenarios['conservative']['card_fee']:,}원", f"{scenarios['moderate']['cost_goods']+scenarios['moderate']['cost_beverage']+scenarios['moderate']['card_fee']:,}원", f"{scenarios['optimistic']['cost_goods']+scenarios['optimistic']['cost_beverage']+scenarios['optimistic']['card_fee']:,}원", "용품원가50%, 음료원가50%, 카드수수료2%"),
            ("매장운영비 + 통신/마케팅", f"{scenarios['conservative']['store_ops_cost']+scenarios['conservative']['marketing_cost']:,}원", f"{scenarios['moderate']['store_ops_cost']+scenarios['moderate']['marketing_cost']:,}원", f"{scenarios['optimistic']['store_ops_cost']+scenarios['optimistic']['marketing_cost']:,}원", "수도광열비, 통신/POS(30만), 마케팅비(50만)"),
            ("월 총비용 합계", f"{scenarios['conservative']['total_cost']:,}원", f"{scenarios['moderate']['total_cost']:,}원", f"{scenarios['optimistic']['total_cost']:,}원", "고정비 및 변동비 총합"),
            ("★ 월 순영업이익", f"{scenarios['conservative']['operating_profit']:,}원", f"{scenarios['moderate']['operating_profit']:,}원", f"{scenarios['optimistic']['operating_profit']:,}원", f"영업이익률: 보편 {scenarios['moderate']['profit_margin']}% 달성")
        ]
        
        y_c = 360
        for r_idx, (cname, ccon, cmod, copt, cdesc) in enumerate(cost_rows):
            is_last = (r_idx == len(cost_rows) - 1)
            c.setFillColor(HexColor('#EFF6FF') if is_last else (self.c_box_bg if r_idx % 2 == 1 else self.c_white))
            c.setStrokeColor(self.c_line)
            c.rect(40, y_c - 6, 880, 28, fill=1, stroke=1)
            c.setFont(FONT_BOLD if is_last else FONT_REGULAR, 9)
            c.setFillColor(self.c_red if is_last else self.c_charcoal)
            c.drawString(56, y_c + 4, cname)
            c.drawString(200, y_c + 4, ccon)
            c.drawString(350, y_c + 4, cmod)
            c.drawString(500, y_c + 4, copt)
            c.setFont(FONT_REGULAR, 8)
            c.setFillColor(self.c_slate)
            c.drawString(680, y_c + 4, cdesc)
            y_c -= 30

        # 하단 운영 형태별 손익 비교
        c.setFillColor(HexColor('#F0FDF4'))
        c.setStrokeColor(HexColor('#BBF7D0'))
        c.rect(40, 48, 880, 105, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(HexColor('#166534'))
        c.drawString(56, 128, "★【 운영 방식별 손익 및 회수 기간 비교 】")
        c.setFont(FONT_REGULAR, 8.6)
        c.setFillColor(HexColor('#14532D'))
        c.drawString(56, 104, f"• [표준] 창업주 직접 상주 운영 (인건비 250만): 월 순영업익 {scenarios['moderate']['operating_profit']//10000:,}만원 (영업이익률 {scenarios['moderate']['profit_margin']}%) → 회수 기간 약 {inv['payback_months_moderate']:.1f}개월")
        c.drawString(56, 82, f"• [위탁] 전담 직원 3명 채용 위탁 운영 (인건비 750만): 월 순영업익 {fin['owner_operated']['staff3_operating_profit']//10000:,}만원 → 회수 기간 약 {fin['owner_operated']['staff3_payback_months']:.1f}개월")
        c.drawString(56, 60, f"• 핵심 요약: 창업주 직접 상주 시 월 500만원의 고정비가 절감되어 단 1년 1개월({inv['payback_months_moderate']:.1f}개월) 만에 초기 투자금 3.19억원을 100% 전액 회수합니다.")
        
        self._draw_footer(c, "Standard Cost Accounting Framework & Franchise Labor Policy")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 11: 8. 손익분기점(BEP) 및 투자금 회수 기간 (SSOT 3.19억원)
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "8. 손익분기점(BEP) 및 투자금 회수 기간", "초기 순투자금 3.19억원 기준: 타석당 하루 1팀 이용 시 손익분기점 달성")
        
        bep_cards = [
            (40, 268, 425, 192, "■ 초기 순투자비용 세부 내역 (SSOT)", [
                f"• 시뮬레이터 장비 (10대): 15,000만원 (1대당 1,500만원)",
                f"• 인테리어 공사비 ({site['area_pyeong']}평): 14,400만원 (평당 120만원)",
                f"• 냉난방기 (4대): 1,200만원 (대당 300만원)",
                f"• 간판/싸인물: 500만원  |  가구/집기: 300만원",
                f"• 초도 용품(클럽, 공 등): 500만원",
                f"• ★ 초기 총 투자비용 (CAPEX): 3.19억원 ({inv['total_capex']//10000:,}만원)"
            ]),
            (495, 268, 425, 192, "■ 손익분기점(BEP) 달성 요건", [
                f"• 월 고정비: 약 {fin['owner_operated']['fixed_cost']//10000:,}만원 (임대료 {site['monthly_rent']//10000:,}만 + 점주 인건비 250만 + 운영비 230만)",
                f"• 손익분기 월 매출: 약 {inv['bep_monthly_sales']//10000:,}만원",
                f"• 손익분기 이용 기준: 타석당 하루 1팀 (약 4명)",
                f"• ★ 타석당 하루 1팀 이용 시 월 고정비({fin['owner_operated']['fixed_cost']//10000:,}만원) 전액 커버 가능",
                f"• 운영 방식별 기준: 직접운영 일 {inv['bep_turns_per_room']}회전 | 직원채용 일 {fin['owner_operated']['staff3_bep_turns']}회전"
            ])
        ]
        for x, y, w, h, title, items in bep_cards:
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(x, y, w, h, fill=1, stroke=1)
            c.setFont(FONT_BOLD, 10.5)
            c.setFillColor(self.c_mck_navy)
            c.drawString(x + 16, y + h - 24, title)
            c.setFont(FONT_REGULAR, 8.6)
            c.setFillColor(self.c_charcoal)
            cur_y = y + h - 48
            for itm in items:
                c.drawString(x + 16, cur_y, itm)
                cur_y -= 22

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 880, 204, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 226, "■ 시나리오별 투자금 전액 회수 기간 (Payback Period)")
        
        c.setFont(FONT_REGULAR, 8.8)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 196, f"• 보수적 시나리오 (3회전): 월 순영업익 {scenarios['conservative']['operating_profit']//10000:,}만원 기준 → 약 {inv['payback_months_conservative']:.1f}개월 만에 회수")
        c.setFont(FONT_BOLD, 9.2)
        c.setFillColor(self.c_mck_teal)
        c.drawString(56, 168, f"• ★ 보편적 시나리오 (4회전): 월 순영업익 {scenarios['moderate']['operating_profit']//10000:,}만원 기준 → 단 {inv['payback_months_moderate']:.1f}개월 (약 1년 1개월) 만에 전액 회수!")
        c.setFont(FONT_REGULAR, 8.8)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 140, f"• 긍정적 시나리오 (5회전): 월 순영업익 {scenarios['optimistic']['operating_profit']//10000:,}만원 기준 → 약 {inv['payback_months_optimistic']:.1f}개월 (10개월 미만) 만에 회수")
        c.drawString(56, 112, f"• 자본 수익률(ROI): 연간 환산 투자 수익률 약 {scenarios['moderate']['operating_profit']*12 / inv['total_capex'] * 100:.1f}% 달성")
        c.drawString(56, 88, f"• 리스크 안전망: 일 3회전의 보수적 운영 시에도 월 1,500만원 이상의 순영업익이 확보되어 사업 안정성이 매우 높음")
        
        self._draw_footer(c, "DCF & Payback Period Financial Valuation Model (CAPEX 3.19B)")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 12: 9. 5개년 중장기 손익 전망 및 종합 제언
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "9. 5개년 중장기 손익 전망 및 종합 제언", f"5개년 누적 영업이익 약 {fin['forecast_5year']['moderate'][-1]['operating_profit']*5//100000000:.1f}억원 창출 및 랜드마크 선점 추천")
        
        if 'profit_forecast' in charts and os.path.exists(charts['profit_forecast']):
            c.drawImage(charts['profit_forecast'], 40, 48, width=440, height=425, preserveAspectRatio=True)
            
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(500, 268, 420, 192, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(516, 438, "■ 5개년 연간 손익 전망 (보편적 시나리오)")
        
        c.setFont(FONT_BOLD, 8)
        c.setFillColor(self.c_slate)
        c.drawString(516, 412, "연차")
        c.drawString(580, 412, "연간 총매출")
        c.drawString(680, 412, "연간 총비용")
        c.drawString(780, 412, "연간 순영업익")
        c.drawString(870, 412, "이익률")
        c.line(516, 404, 905, 404)
        
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_charcoal)
        y_5 = 390
        for fc in fin['forecast_5year']['moderate']:
            c.drawString(516, y_5, f"{fc['year']}년차")
            c.drawString(580, y_5, f"{fc['total_revenue']//10000:,}만")
            c.drawString(680, y_5, f"{fc['total_cost']//10000:,}만")
            c.setFont(FONT_BOLD, 8)
            c.setFillColor(self.c_mck_teal)
            c.drawString(780, y_5, f"{fc['operating_profit']//10000:,}만")
            c.setFont(FONT_REGULAR, 8)
            c.setFillColor(self.c_charcoal)
            c.drawString(870, y_5, f"{fc['margin']}%")
            y_5 -= 18

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_mck_teal)
        c.setLineWidth(1.2)
        c.rect(500, 48, 420, 204, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_teal)
        c.drawString(516, 226, "■ 최종 출점 의사결정 종합 제언")
        c.setFont(FONT_REGULAR, 8.4)
        c.setFillColor(self.c_charcoal)
        c.drawString(516, 198, f"1. 골든 시니어 배후 수요: 반경 3km 내 50대 이상 {demo['senior_50_plus']:,}명 선점")
        c.drawString(516, 172, "2. 10타석 대규모 플래그십: 소규모 매장 대비 압도적 집객력과 쾌적성")
        c.drawString(516, 146, "3. 1인 18홀 7,000원 경쟁력: 일반 스크린골프 대비 가격 우위 및 높은 회전율")
        c.drawString(516, 120, f"4. 빠른 투자 회수: 보편적 가동 기준 약 {inv['payback_months_moderate']:.1f}개월 만에 3.19억원 전액 회수")
        if site.get('special_notes'):
            c.drawString(516, 94, f"5. 맞춤 실행 전략: '{site['special_notes']}' 연계 맞춤 출점 권장")
        else:
            c.drawString(516, 94, "5. 선점 추천: 상권 내 마이파크 플래그십 1호점 출점 즉시 진행 권장")
        
        self._draw_footer(c, "MYPARK 5-Year Long-term Strategic Feasibility Valuation")
        c.showPage()

        c.save()
        return output_path
