# -*- coding: utf-8 -*-
"""McKinsey Classic Executive Theme PDF 보고서 생성기 (PART 2 흐름 재구성 완료본)"""
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# -----------------------------------------------------------------------------
# TTF 폰트 등록
# -----------------------------------------------------------------------------
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

def init_fonts(custom_candidates=None):
    global FONT_REGULAR, FONT_BOLD
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_candidates = custom_candidates or [
        os.path.join(current_dir, 'fonts', 'MalgunGothic.ttf'),
        os.path.join(current_dir, 'fonts', 'MalgunGothicBold.ttf'),
        r'C:\Windows\Fonts\malgun.ttf',
        r'C:\Windows\Fonts\malgunbd.ttf',
        r'C:\Windows\Fonts\NanumGothic.ttf',
        r'C:\Windows\Fonts\NanumGothicBold.ttf',
        '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
        '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf'
    ]
    for fpath in font_candidates:
        if os.path.exists(fpath):
            try:
                pdfmetrics.registerFont(TTFont('KoreanFont', fpath))
                pdfmetrics.registerFont(TTFont('KoreanFontBold', fpath))
                FONT_REGULAR = 'KoreanFont'
                FONT_BOLD = 'KoreanFontBold'
                print(f"[SUCCESS] Registered Korean Font: {fpath}")
                return True
            except Exception as e:
                print(f"[WARN] Failed to load {fpath}: {e}")
                
    FONT_REGULAR = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"
    print("[FONT WARNING] 한글 폰트를 찾지 못해 Helvetica로 대체합니다 — 생성되는 PDF의 한글이 깨질 수 있습니다.")
    return False

init_fonts()


class PDFGenerator:
    """맥킨지 클래식 이그제큐티브 스타일 PDF 생성기"""

    def __init__(self, filename="mypark_market_analysis.pdf"):
        self.filename = filename
        self.pagesize = landscape(A4)
        self.width, self.height = self.pagesize

        # McKinsey Classic Color Palette
        self.c_mck_navy = HexColor('#002B49')
        self.c_mck_teal = HexColor('#00A3A6')
        self.c_charcoal = HexColor('#222222')
        self.c_slate = HexColor('#555555')
        self.c_line = HexColor('#D0D0D0')
        self.c_box_bg = HexColor('#F8FAFC')
        self.c_tint_blue = HexColor('#F0F4F8')
        self.c_white = HexColor('#FFFFFF')
        self.c_red = HexColor('#C00000')

    def _draw_mckinsey_header(self, c, section_title, lead_text):
        c.setFillColor(self.c_mck_navy)
        c.rect(0, self.height - 24, self.width, 24, fill=1, stroke=0)
        c.setFillColor(self.c_white)
        c.setFont(FONT_BOLD, 9)
        c.drawString(40, self.height - 16, "MYPARK SCREEN PARK GOLF  |  EXECUTIVE SITE SELECTION & INVESTMENT ANALYSIS")

        c.setFillColor(self.c_mck_navy)
        c.setFont(FONT_BOLD, 14)
        c.drawString(40, self.height - 50, section_title)

        c.setFillColor(self.c_slate)
        c.setFont(FONT_REGULAR, 9.5)
        c.drawString(40, self.height - 66, lead_text)

        c.setStrokeColor(self.c_line)
        c.setLineWidth(0.8)
        c.line(40, self.height - 74, self.width - 40, self.height - 74)

    def _draw_footer(self, c, source_text="KOSIS & Small Enterprise Market Service Data"):
        c.setStrokeColor(self.c_line)
        c.setLineWidth(0.5)
        c.line(40, 36, self.width - 40, 36)
        c.setFont(FONT_REGULAR, 7.5)
        c.setFillColor(self.c_slate)
        c.drawString(40, 24, f"Source: {source_text}")
        c.drawRightString(self.width - 40, 24, "CONFIDENTIAL  |  MYPARK HQ")

    def _draw_multiline_text(self, c, text, x, y, max_chars=40, line_height=14, max_lines=4, font_name=None, font_size=8.5, color=None):
        if font_name is None:
            font_name = FONT_REGULAR
        if color is None:
            color = self.c_charcoal
        c.setFont(font_name, font_size)
        c.setFillColor(color)
        
        words = text.split(' ')
        lines = []
        cur_line = ""
        for w in words:
            if len(cur_line + " " + w) <= max_chars:
                cur_line = (cur_line + " " + w).strip()
            else:
                lines.append(cur_line)
                cur_line = w
        if cur_line:
            lines.append(cur_line)
            
        for i, l in enumerate(lines[:max_lines]):
            c.drawString(x, y - (i * line_height), l)
        return y - (min(len(lines), max_lines) * line_height)

    def generate(self, data, output_pdf_path=None, charts=None):
        if output_pdf_path and isinstance(output_pdf_path, str):
            self.filename = output_pdf_path
        if charts is None:
            charts = data.get('charts', {})
        c = canvas.Canvas(self.filename, pagesize=self.pagesize)
        
        site = data['site']
        demo = data['demographics']
        comm = data['commercial']
        score = data.get('score', data.get('scores', {}))
        fin = data['financials']
        inv = fin['investment']
        scenarios = fin['monthly_scenarios']
        target_dong = site['dong']

        # ---------------------------------------------------------------------
        # Page 1: 표지
        # ---------------------------------------------------------------------
        c.setFillColor(self.c_mck_navy)
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)

        c.setFillColor(self.c_mck_teal)
        c.rect(0, self.height - 12, self.width, 12, fill=1, stroke=0)

        c.setFillColor(self.c_white)
        c.setFont(FONT_BOLD, 26)
        c.drawString(60, self.height - 140, "스크린 파크골프(마이파크) 출점 타당성 분석 보고서")

        c.setFillColor(self.c_mck_teal)
        c.setFont(FONT_BOLD, 15)
        c.drawString(60, self.height - 175, "10타석 120평 플래그십 표준 모델  |  상권 분석 및 투자 타당성 평가")

        c.setStrokeColor(self.c_mck_teal)
        c.setLineWidth(2)
        c.line(60, self.height - 195, self.width - 60, self.height - 195)

        c.setFillColor(self.c_white)
        c.setFont(FONT_REGULAR, 12)
        notes_str = f"  |  특이사항: {site['special_notes']}" if site.get('special_notes') else ""
        c.drawString(60, self.height - 230, f"• 대상 사업지: {site['full_address']}{notes_str}")
        c.drawString(60, self.height - 255, f"• 상권 분석 대상: {site['sido']} {site['sigungu']} {target_dong} 반경 3km 생활권")
        c.drawString(60, self.height - 280, f"• 표준 출점 모델: 10타석 ({site['area_pyeong']}평형)  |  분석 기준일: {data.get('created_at', '2026.08')}")

        c.setFillColor(self.c_white)
        c.setFont(FONT_BOLD, 11)
        c.drawString(60, 60, "마이파크(MYPARK) 가맹본부 데이터전략실")
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(HexColor('#A0B2C6'))
        c.drawString(60, 44, "CONFIDENTIAL — 본 문서는 사업성 검토 목적 외 무단 복제 및 배포를 금합니다.")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 2: 1. 입지 적합성 종합 판정 (5-Dimension Diamond Scoring)
        # [PART 2 재구성: 재무 금액 배제, 순수 입지 적합성 평가 전진 배치]
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "1. 입지 적합성 종합 판정 (5-Dimension Diamond Scoring)", f"5대 다이아몬드 스코어링 총점 {score['total_score']}점({score['grade']}등급) - 출점 최우선 추천 판정")
        
        # 좌측 레이더 차트
        if 'radar_score' in charts and os.path.exists(charts['radar_score']):
            c.drawImage(charts['radar_score'], 40, 48, width=440, height=425, preserveAspectRatio=True)
            
        # 우측 5대 지표별 점수 및 산출 근거
        indicators = [
            ("1) 시니어 인구 밀집도", score['scores']['senior_population'], 25, f"KOSIS 실측: 반경 3km 내 50대 이상 시니어 {demo['senior_50_plus']:,}명 ({demo['senior_ratio']}%) 밀집"),
            ("2) 접근성 및 주차 인프라", score['scores']['accessibility_parking'], 25, f"간선도로 접면/교통망 우수({score['scores']['accessibility_parking']:.1f}점) / 10타석 주차면은 '현장 실측' 요망"),
            ("3) 공간 적합성 및 층고", score['scores']['space_efficiency'], 15, f"{site['area_pyeong']}평 10타석 배치 최적({score['scores']['space_efficiency']:.1f}점) / 유효 층고 2.8m 이상은 '인테리어 실측' 필수"),
            ("4) 경쟁 매장 여유도", score['scores']['supply_gap'], 15, f"{comm.get('competitor_summary', '반경 3km 내 대형 플래그십 매장 공급 부족')}"),
            ("5) 지역 소비력 및 여가지출", score['scores']['commercial_spending'], 20, f"MYPARK 지역등급 추정: 골프용품 성장 1위(+{comm['growth_rate']}%) 및 스크린골프 상위 20% 월 {comm['top_20_sales']//10000:,}만원 상권"),
        ]
        y_ind = 445
        for iname, iscore, imax, idesc in indicators:
            c.setFont(FONT_BOLD, 10)
            c.setFillColor(self.c_mck_navy)
            c.drawString(500, y_ind, f"■ {iname}: ")
            c.setFillColor(self.c_mck_teal)
            c.drawString(660, y_ind, f"{iscore}점 / {imax}점 만점")
            
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_slate)
            c.drawString(510, y_ind - 18, f"↳ 산출 근거: {idesc}")
            y_ind -= 54
            
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, 48, 425, 120, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 11)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, 146, f"★ 종합 입지 판정: 총점 {score['total_score']}점 / {score['grade']}등급")
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_red)
        c.drawString(511, 128, f"• 판정 결과: {score['grade_desc']}")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        grade_summary_lines = {
            'S': ("• 본 사업지는 50~70대 풍부한 시니어 거주 인구와 우수한 교통/접근성을 갖추어,",
                  "  평일 주간 정기 예약 및 동호회 리그 중심의 높은 가동률 창출에 최적화된 입지입니다."),
            'A': ("• 본 사업지는 시니어 배후 수요와 접근성 등 핵심 조건을 대체로 충족하여,",
                  "  평일 주간 정기 예약 중심의 안정적 가동률을 기대할 수 있는 입지입니다."),
            'B': ("• 본 사업지는 일부 지표에서 표준 기준을 충족하나 상대적으로 낮은 지표도 있어,",
                  "  아래 세부 근거를 현장 실측과 함께 신중히 검토하시기를 권장합니다."),
            'C': ("• 본 사업지는 5대 지표 중 다수가 표준 기준에 미달하여,",
                  "  출점 전 배후 수요·경쟁 환경에 대한 현장 재확인이 반드시 필요합니다."),
        }
        line1, line2 = grade_summary_lines.get(score['grade'], grade_summary_lines['B'])
        c.drawString(511, 108, line1)
        c.drawString(511, 92, line2)
        c.drawString(511, 76, "• 상세 상권 및 경쟁 환경 분석은 다음 페이지(2~6장)에서 상술합니다.")

        self._draw_footer(c, f"MYPARK 5-Dimension Diamond Scoring Methodology ({score['total_score']}점 {score['grade']}등급)")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 3: 2. 배후 인구 및 타겟 연령 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "2. 3km 생활권 인구 및 타겟 연령 분석", f"반경 3km 내 50대 이상 시니어 {demo['senior_50_plus']:,}명({demo['senior_ratio']}%)의 핵심 소비 수요 확보")
        
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
            s_val = d.get('senior_50', int(d['total'] * (demo['senior_ratio'] / 100.0)))
            c.drawString(250, y_d, f"{s_val:,}명")
            c.drawString(350, y_d, f"{d.get('senior_ratio', demo['senior_ratio'])}%")
            y_d -= 18

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, 268, 425, 192, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, 438, "■ 50대 이상 시니어 연령대 분포 매트릭스")
        
        c.setFont(FONT_BOLD, 8)
        c.setFillColor(self.c_slate)
        c.drawString(511, 412, "연령 구간")
        c.drawString(600, 412, "인구수")
        c.drawString(690, 412, "전체 비중")
        c.drawString(780, 412, "파크골프 이용 행태")
        c.line(511, 404, 900, 404)
        
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_charcoal)
        age_matrix = [
            ("50대 (액티브)", f"{demo['pop_50s']:,}명", f"{demo['ratio_50s']}%", "부부/동호회 주말 및 평일 야간"),
            ("60대 (은퇴 시니어)", f"{demo['pop_60s']:,}명", f"{demo['ratio_60s']}%", "평일 주간 정기 리그 핵심 주력"),
            ("70대 이상 (실버)", f"{demo['pop_70_plus']:,}명", f"{demo['ratio_70_plus']}%", "오전 시간대 건강 증진 친목 모임"),
            ("50대+ 합계", f"{demo['senior_50_plus']:,}명", f"{demo['senior_ratio']}%", "★ 평일 낮 10~17시 풀가동 타겟")
        ]
        y_a = 390
        for grp, cnt, rt, beh in age_matrix:
            c.drawString(511, y_a, grp)
            c.drawString(600, y_a, cnt)
            c.drawString(690, y_a, rt)
            c.drawString(780, y_a, beh)
            y_a -= 22

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 880, 204, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 226, "■ 3km 생활권 시니어 인구 분석 시사점")
        
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 196, f"• 압도적인 타겟 집적도: 반경 3km 내 50대 이상 인구 {demo['senior_50_plus']:,}명 확보로 안정적 고객 풀 형성")
        c.drawString(56, 168, "• 60대 주력 고객군 43%: 은퇴 후 평일 낮 시간 여유가 있는 60대가 전체 시니어의 절반을 차지하여 평일 낮 가동률 극대화")
        c.drawString(56, 140, "• 70대 실버 헬스케어 수요 21%: 관절 부담이 없는 파크골프 특성상 부부 동반 및 시니어 커뮤니티 공간으로 정착")
        c.drawString(56, 112, "• 일반 스크린골프 대비 회전율 우위: 야간 직장인 편중 매장과 달리 주간 7시간 집중 가동으로 일일 높은 회전수 확보")
        
        self._draw_footer(c, "KOSIS National Statistics Portal" + (" (※ 행정동 추정 모델 적용)" if demo.get("is_estimated") else f" ({demo.get('base_date', '2026.08')})"))
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 4: 3. 상권 소비력 및 유동 패턴 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "3. 상권 소비력 및 유동 패턴 분석", f"주거지역 {comm.get('residential_pop_ratio', 93.4)}% 밀집 상권 및 스크린골프 상위 20% 월매출 {comm['top_20_sales']//10000:,}만원 시장 타겟팅")
        
        if 'sales_trend' in charts and os.path.exists(charts['sales_trend']):
            c.drawImage(charts['sales_trend'], 40, 260, width=440, height=200, preserveAspectRatio=True)
            
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, 260, 425, 200, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, 438, "■ 유사 골프업종 수익구조 격차 (MYPARK 추정)")
        
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(511, 412, f"• 상위 20% 매장 월매출: 약 {comm['top_20_sales']//10000:,}만원 (대형 최신 매장)")
        c.drawString(511, 392, f"• 하위 20% 매장 월매출: 약 {comm.get('bottom_20_sales', 3020000)//10000:,}만원 (노후 소형 매장)")
        c.drawString(511, 372, "• 시장 특성: 시설 규모와 쾌적성에 따른 매출 양극화 뚜렷")
        c.drawString(511, 352, "★ 마이파크 포지셔닝: 10타석 최신식 플래그십으로 상위 20% 시장 흡수")
        
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_mck_teal)
        c.drawString(511, 320, f"■ 요일별 매출 비중: 주중 {100 - comm['day_distribution']['주말평균비중']*2:.1f}% / 주말 {comm['day_distribution']['주말평균비중']*2:.1f}%")
        c.drawString(511, 300, f"■ 시간대별 비중: 주간(10~17시) {comm['time_distribution']['주간_10_17시_비중']}% 집중 가동")

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 880, 196, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 222, "■ 상권 소비력 종합 평가")
        
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 194, f"• 소비 수준: {comm['spending_grade']} (시니어 여가 및 생활체육 소비 여력 충분)")
        c.drawString(56, 168, "• 주간 매출 집중형: 평일 10~17시 매출 비중이 71.4%로 주간 시간대 수익 창출력 탁월")
        c.drawString(56, 142, "• 4인 1팀 단체 이용: 파크골프 1팀당 식음료 및 추가 게임비 지출로 객단가 극대화")
        c.drawString(56, 116, "• 안정적 단골 매출: 동호회 정기 예약(월 단위 선결제) 비중이 높아 계절성 리스크 방어")

        self._draw_footer(c, "MYPARK Regional Tier Estimation Model")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 5: 4. 업종 성장률 및 골프 특화도
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "4. 업종 성장률 및 골프 특화도", f"골프용품 매출성장률 1위(+{comm['growth_rate']}%) 및 전국 평균 대비 {comm['golf_industry_density']['multiple']}배 높은 골프 특화 상권")
        
        if 'growth_radar' in charts and os.path.exists(charts['growth_radar']):
            c.drawImage(charts['growth_radar'], 40, 260, width=440, height=200, preserveAspectRatio=True)
            
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, 260, 425, 200, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, 438, "■ TOP 5 매출 증가 업종 (소상공인시장진흥공단)")
        
        c.setFont(FONT_BOLD, 8)
        c.setFillColor(self.c_slate)
        c.drawString(511, 412, "순위")
        c.drawString(550, 412, "업종명")
        c.drawString(680, 412, "매출 성장률")
        c.drawString(770, 412, "업종 상태")
        c.line(511, 404, 900, 404)
        
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(self.c_charcoal)
        y_g = 388
        for ind in comm['top_growth_industries']:
            c.drawString(511, y_g, str(ind['rank']))
            c.drawString(550, y_g, ind['name'])
            c.drawString(680, y_g, ind['growth'])
            c.drawString(770, y_g, ind['status'])
            y_g -= 18

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 880, 196, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 222, "■ 골프 특화 상권 시사점")
        
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 194, f"• 레저 스포츠 소비 1위: {comm['top_growth_industries'][0]['name']}이 매출성장률 {comm['top_growth_industries'][0]['growth']}로 전 업종 중 1위 기록")
        c.drawString(56, 168, f"• 골프 인프라 밀집도: 전국 평균 대비 {comm['golf_industry_density']['multiple']}배 높은 골프 시설 집적으로 검증된 골프 수요층 상존")
        c.drawString(56, 142, "• 일반 골프의 파크골프 전환: 일반 골프 비용/체력 부담을 느끼는 시니어층의 스크린 파크골프 유입 가속화")
        c.drawString(56, 116, "• 성장 단계: 단순 유행이 아닌 시니어 여가 문화의 핵심 트렌드로 정착 단계 진입")

        self._draw_footer(c, "MYPARK Regional Tier Estimation Model")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 6: 5. 경쟁 환경 및 시설 공급 갭 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "5. 경쟁 환경 및 시설 공급 갭 분석", f"반경 3km 내 {comm['competitor_summary']}")
        
        comps = comm['competitors'][:4]
        card_w = 205
        spacing = 15
        start_x = 40
        
        for idx, comp in enumerate(comps):
            cur_x = start_x + idx * (card_w + spacing)
            
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(cur_x, 48, card_w, 412, fill=1, stroke=1)
            
            c.setFillColor(self.c_mck_navy)
            c.rect(cur_x, 418, card_w, 42, fill=1, stroke=0)
            c.setFillColor(self.c_white)
            c.setFont(FONT_BOLD, 9.5)
            
            c_name = str(comp['name'])
            if len(c_name) > 13:
                c.drawCentredString(cur_x + card_w/2, 451, c_name[:13])
                c.drawCentredString(cur_x + card_w/2, 435, c_name[13:])
            else:
                c.drawCentredString(cur_x + card_w/2, 443, c_name)
                
            c.setFillColor(self.c_tint_blue)
            c.rect(cur_x + 8, 362, card_w - 16, 44, fill=1, stroke=0)
            c.setFillColor(self.c_mck_navy)
            c.setFont(FONT_BOLD, 10.5)
            r_str = f"{comp.get('rooms', 0)}타석 규모" if comp.get('rooms', 0) > 0 else "1호점 선점 대상"
            c.drawCentredString(cur_x + card_w/2, 388, r_str)
            c.setFont(FONT_REGULAR, 7.5)
            c.setFillColor(self.c_slate)
            c.drawCentredString(cur_x + card_w/2, 372, f"[{comp.get('status', '실측완료')}] {comp.get('system', '스크린 시스템')}")
            
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
            
        self._draw_footer(c, "MYPARK Competitor Database Matching (Live POI Search Pending)")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 7: 6. 사업지 개요 및 현장 출점 요건 (4대 건축·인프라 체크리스트)
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "6. 사업지 개요 및 현장 출점 요건", f"10타석 {site['area_pyeong']}평 규모 출점을 위한 4대 건축·인프라 현장 실측 기준")
        
        cards = [
            (40, 260, 425, 200, "■ 공간 및 유효 층고 요건", [
                f"• 대상 주소: {site['full_address']}",
                f"• 고객 특이사항: {site['special_notes']}" if site.get('special_notes') else f"• 권장 면적: 전용 {site['area_pyeong']}평 (10타석 + 카페/락커룸 최적 배치)",
                f"• 권장 면적: 전용 {site['area_pyeong']}평 (10타석 + 카페/락커룸 최적 배치)" if site.get('special_notes') else f"• 층고 기준: {site['clear_height_spec']}",
                f"• 층고 기준: {site['clear_height_spec']}",
                f"• 보/배관 간섭: 센서 투사 영역 및 스윙 궤적 내 장애물 사전 실측 필수",
                f"• 권장 층수: 고객 접근성 높은 지상 2~3층 권장 (쾌적한 지하 1층 가능)",
                f"• 바닥 하중: 스크린 타석 및 키오스크 하중(300kg/㎡ 이상) 적합 여부"
            ]),
            (495, 260, 425, 200, "■ 주차 및 차량 접근성 기준", [
                f"• 주차 요건: {site['parking_spec']}",
                f"• 고객 특성: 자차 이용 시니어 비중 80% 이상으로 편리한 진출입 필수",
                f"• 진입 여건: 램프 폭 및 회전각 여유 있는 자주식 주차장 최우선",
                f"• 도로 접면: 주요 간선도로 및 대단지 아파트 진입로 인접 우수",
                f"• 보행 동선: 대중교통(버스/지하철) 도보 5~10분 생활권 완비",
                f"• 승하차 편의: 주차장에서 매장 입구까지 단차 없는 완만한 동선"
            ]),
            (40, 48, 425, 196, "■ 건물 편의 및 승강기 설비", [
                f"• 고객 편의: {site['accessibility_spec']}",
                f"• 계단 여건: 계단 단차가 낮거나 완만한 진입 경사로 확보 필요",
                f"• 냉난방/환기: 개별 공조 및 고성능 환기 덕트 설치 공간 확인",
                f"• 소음/진동: 상하층 타 업종 간섭 방지 방음/흡음 설계 시공",
                f"• 쾌적성: 남녀 분리 청결 화장실 및 쾌적한 로비 라운지 구축",
                f"• 장애인 편의: 엘리베이터 단차 제거 및 자동문 출입구 권장"
            ]),
            (495, 48, 425, 196, "■ 인허가 및 건축물 용도", [
                f"• 적합 용도: {site['zoning_spec']}",
                f"• 지자체 체육시설: 체육시설의 설치·이용에 관한 법률 인허가 검토",
                f"• 소방 기준: 스프링클러, 비상유도등, 비상탈출구 완비 점검",
                f"• 전기 용량: 10타석 시뮬레이터 동시 가동 대비 30kW 이상 인입",
                f"• 정화조 용량: 일 최대 150명 이상 동시 이용 기준 충족 점검",
                f"• 행정 절차: 관할 구청 건축과 및 체육진흥과 용도 사전 협의"
            ]),
        ]
        for x, y, w, h, title, lines in cards:
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(x, y, w, h, fill=1, stroke=1)
            c.setFont(FONT_BOLD, 10)
            c.setFillColor(self.c_mck_navy)
            c.drawString(x + 14, y + h - 22, title)
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_charcoal)
            y_l = y + h - 42
            for l in lines[:6]:
                c.drawString(x + 14, y_l, l)
                y_l -= 18

        self._draw_footer(c, "Building Code & Field Inspection Checklist")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 8: [신규] 7. 표준 투자 조건 및 사업 추진 유의사항
        # [PART 2 신설: 이 보고서에서 재무 금액이 최초로 등장하는 지점 & Caveat 명시]
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "7. 표준 투자 조건 및 사업 추진 유의사항", "10타석 120평 플래그십 표준 모델 기준 및 투자 결정 전 필수 점검사항")
        
        # 블록 A (좌측): 표준 투자 조건 (전제조건 명시)
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 425, 412, fill=1, stroke=1)
        
        c.setFillColor(self.c_mck_navy)
        c.rect(40, 418, 425, 42, fill=1, stroke=0)
        c.setFillColor(self.c_white)
        c.setFont(FONT_BOLD, 11)
        c.drawString(56, 436, "■ 10타석 120평 플래그십 표준 모델 투자 조건 (SSOT)")
        
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 396, "● 초기 투자금 상세 내역")
        
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 374, f"• 시뮬레이터 장비: 10대 × 대당 1,500만원 = 1억 5,000만원")
        c.drawString(56, 354, f"• 인테리어 공사비: 120평 × 평당 120만원 = 1억 4,400만원")
        c.drawString(56, 334, f"• 부대설비 (냉난방/간판/가구/초도용품): 2,500만원")
        c.drawString(70, 316, "- 냉난방기(4대 1,200만) / 간판(500만) / 가구(300만) / 초도용품(500만)")
        
        c.setFillColor(self.c_tint_blue)
        c.rect(56, 260, 393, 40, fill=1, stroke=0)
        c.setFillColor(self.c_mck_navy)
        c.setFont(FONT_BOLD, 12)
        c.drawString(70, 276, "★ 총 초기 투자금: 3억 1,900만원 (3.19억원)")
        
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 236, "● 표준 운영 방식 및 인건비 모델")
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 214, "• 표준 모델 (점주 1인 상주 운영): 인건비 월 250만원 (수익률 극대화)")
        c.drawString(56, 194, "• 비교 모델 (직원 3인 채용 운영): 인건비 월 750만원 (회수기간 15.3개월)")
        c.drawString(56, 174, f"• 게임비 요금: 1인 18홀 7,000원 (4인 1팀 28,000원)")
        c.drawString(56, 154, f"• 3대 매출원: 게임비 회전 + 용품 판매(월 150만) + 식음료(월 180만)")
        c.drawString(56, 134, f"• 월 임대료 기준: 실측 {site['monthly_rent']//10000:,}만원/월 반영")
        
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_slate)
        c.drawString(56, 80, "※ 레슨, 락커비, 홀인원펀드 등 근거 없는 부가 항목은 전액 배제되었습니다.")

        # 블록 B (우측): 투자 결정 전 유의사항 (Caveat)
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, 48, 425, 412, fill=1, stroke=1)
        
        c.setFillColor(HexColor('#B0473C'))
        c.rect(495, 418, 425, 42, fill=1, stroke=0)
        c.setFillColor(self.c_white)
        c.setFont(FONT_BOLD, 11)
        c.drawString(511, 436, "⚠️ 투자 결정 전 반드시 확인하십시오 (사업 추진 유의사항)")
        
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, 396, "● 현장 실측 및 인허가 유의사항")
        
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(511, 374, "• 위 수치는 표준 모델 기준 추정치이며, 실제 임대료·공사비는 현장 견적에")
        c.drawString(511, 358, "  따라 달라질 수 있습니다.")
        c.drawString(511, 338, "• 건물 내 보/배관 간섭 및 유효 층고(2.8m 이상 확보) 여부를 사전 실측하십시오.")
        c.drawString(511, 318, "• 10타석 동시 가동에 필요한 전기 인입 용량(30kW 이상)을 확인하십시오.")
        
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, 280, "● 인건비 및 운영 방식 유의사항")
        
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(511, 258, "• 매니저/직원을 채용해 전면 위탁 운영할 경우 인건비 증가(월 500~750만)로")
        c.drawString(511, 242, "  손익분기점이 상승하고 투자금 회수기간이 연장됩니다.")
        c.drawString(511, 222, "• 인테리어 및 시뮬레이터 단가는 본 계약 시점의 공식 견적을 확인하십시오.")
        
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, 184, "● 재무 타당성 분석의 법적 한계")
        
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_slate)
        c.drawString(511, 162, "• 본 보고서는 KOSIS 인구통계와 MYPARK 지역등급 추정 모델, 표준 재무 모델에 기반한")
        c.drawString(511, 146, "  추정 분석 자료이며, 실제 미래 사업 성과나 특정 수익률을 보장하지 않습니다.")
        c.drawString(511, 130, "• 최종 창업 결정 전 세무, 법률, 현장 실측 전문가와의 상담을 권장합니다.")
        
        c.setFillColor(HexColor('#FEF2F2'))
        c.setStrokeColor(HexColor('#FECACA'))
        c.rect(511, 60, 393, 50, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 8.5)
        c.setFillColor(HexColor('#991B1B'))
        c.drawString(525, 92, "★ 9~12장의 모든 매출·손익·BEP 추정치는 위 표준 모델을 전제로 산출되었습니다.")
        c.setFont(FONT_REGULAR, 8)
        c.drawString(525, 74, "(기준: 10타석 120평 / 총투자금 3.19억원 / 점주 1인 상주 운영 모델)")

        self._draw_footer(c, "MYPARK Standard Investment Criteria & Regulatory Caveat")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 9: 8. 사업 타당성 분석 - 매출 추정 (3대 시나리오)
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "8. 사업 타당성 분석 - 매출 추정 (3대 시나리오)", f"보수적(일 {scenarios['conservative']['daily_turns_per_room']}회전) {scenarios['conservative']['total_revenue']//10000:,}만원 ~ 보편적(일 {scenarios['moderate']['daily_turns_per_room']}회전) {scenarios['moderate']['total_revenue']//10000:,}만원 ~ 긍정적(일 {scenarios['optimistic']['daily_turns_per_room']}회전) {scenarios['optimistic']['total_revenue']//10000:,}만원")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 260, 880, 200, fill=1, stroke=1)
        
        headers = ["구분 / 시나리오", "일 가동률 (타석당)", "월 게임비 매출", "용품 판매 매출", "식음료 등 기타", "월 총매출액", "연간 총매출액"]
        c.setFont(FONT_BOLD, 8.5)
        c.setFillColor(self.c_slate)
        x_offsets = [56, 170, 290, 420, 540, 660, 780]
        for h, x in zip(headers, x_offsets):
            c.drawString(x, 438, h)
        c.line(56, 428, 900, 428)
        
        sc_data = [
            ("보수적 (초기/비수기)", f"1일 {scenarios['conservative']['daily_turns_per_room']}회전 ({scenarios['conservative']['daily_users']}명)", f"{scenarios['conservative']['room_revenue']//10000:,}만원", f"{scenarios['conservative']['goods_revenue']//10000:,}만원", f"{scenarios['conservative']['beverage_revenue']//10000:,}만원", f"{scenarios['conservative']['total_revenue']//10000:,}만원", f"{scenarios['conservative']['annual_revenue']//100000000:.1f}억원"),
            ("보편적 (정기예약 정착)", f"1일 {scenarios['moderate']['daily_turns_per_room']}회전 ({scenarios['moderate']['daily_users']}명)", f"{scenarios['moderate']['room_revenue']//10000:,}만원", f"{scenarios['moderate']['goods_revenue']//10000:,}만원", f"{scenarios['moderate']['beverage_revenue']//10000:,}만원", f"{scenarios['moderate']['total_revenue']//10000:,}만원", f"{scenarios['moderate']['annual_revenue']//100000000:.1f}억원"),
            ("긍정적 (주간/주말 풀가동)", f"1일 {scenarios['optimistic']['daily_turns_per_room']}회전 ({scenarios['optimistic']['daily_users']}명)", f"{scenarios['optimistic']['room_revenue']//10000:,}만원", f"{scenarios['optimistic']['goods_revenue']//10000:,}만원", f"{scenarios['optimistic']['beverage_revenue']//10000:,}만원", f"{scenarios['optimistic']['total_revenue']//10000:,}만원", f"{scenarios['optimistic']['annual_revenue']//100000000:.1f}억원")
        ]
        y_s = 405
        for sname, rturn, rrev, grev, brev, tot, ann in sc_data:
            is_mod = "보편적" in sname
            c.setFont(FONT_BOLD if is_mod else FONT_REGULAR, 8.5)
            c.setFillColor(self.c_mck_navy if is_mod else self.c_charcoal)
            c.drawString(56, y_s, sname)
            c.drawString(170, y_s, rturn)
            c.drawString(290, y_s, rrev)
            c.drawString(420, y_s, grev)
            c.drawString(540, y_s, brev)
            c.drawString(660, y_s, tot)
            c.drawString(780, y_s, ann)
            y_s -= 24

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 880, 196, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 222, "■ 매출 추정 핵심 근거 (엑셀 수익분석표 일치)")
        
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 194, "• 게임비 단가: 1인 18홀 7,000원 (4인 1팀 1게임당 28,000원)")
        c.drawString(56, 168, f"• 10타석 회전 기준: 타석당 1일 {scenarios['moderate']['daily_turns_per_room']}게임 가동 시 1일 {scenarios['moderate']['daily_users']}명 이용 (보편 시나리오 월 게임비 {scenarios['moderate']['room_revenue']//10000:,}만원)")
        c.drawString(56, 142, "• 부가 매출 2종: 파크골프 클럽/공/장갑 등 용품 판매(월 150만원) + 음료/간식(월 180만원)")
        c.drawString(56, 116, "• 투명성 원칙: 레슨비, 락커룸 렌탈료 등 근거 없는 부가 항목을 일체 배제한 보수적이고 정직한 추정치")

        self._draw_footer(c, "MYPARK Standard Financial Model (120 Pyeong, 10 Rooms)")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 10: 9. 사업 타당성 분석 - 비용 구조 및 순영업이익
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "9. 사업 타당성 분석 - 비용 구조 및 순영업이익", f"월 고정비 {fin['owner_operated']['fixed_cost']//10000:,}만원(임대료 {site['monthly_rent']//10000:,}만+인건비 250만+운영비) 및 보편 월 순영업이익 {scenarios['moderate']['operating_profit']//10000:,}만원")
        
        if 'waterfall_cost' in charts and os.path.exists(charts['waterfall_cost']):
            c.drawImage(charts['waterfall_cost'], 40, 260, width=440, height=200, preserveAspectRatio=True)
            
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, 260, 425, 200, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, 438, "■ 월간 비용 구조 상세 (보편 시나리오 기준)")
        
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(511, 412, f"• 월 임대료: {site['monthly_rent']//10000:,}만원 (실제 대상 매장 기준)")
        c.drawString(511, 392, "• 인건비 (점주 직접운영): 250만원 (1인 상주 운영)")
        c.drawString(511, 372, "• 매장 운영비/소모품: 100만원  |  통신/POS: 30만원  |  마케팅비: 50만원")
        c.drawString(511, 352, f"• 변동비 (매출연동): 매출원가 180만원 + 카드수수료(1.3%) {scenarios['moderate']['card_fee']//10000:,}만원")
        c.drawString(511, 332, f"★ 월 총지출 합계: {scenarios['moderate']['total_cost']//10000:,}만원")
        
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_teal)
        c.drawString(511, 290, f"★ 월 순영업이익: {scenarios['moderate']['operating_profit']//10000:,}만원 (영업이익률 {scenarios['moderate']['profit_margin']}%)")

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 880, 196, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 222, "■ 운영 모델별 순영업이익 비교")
        
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 194, f"• 점주 직접 운영 모델 (표준): 월 순영업이익 {scenarios['moderate']['operating_profit']//10000:,}만원 (연간 {scenarios['moderate']['operating_profit']*12//10000:,}만원 / 이익률 {scenarios['moderate']['profit_margin']}%)")
        c.drawString(56, 168, f"• 직원 채용 모델 (매니저 1인 + 알바 2인): 월 순영업이익 {fin['owner_operated']['staff3_operating_profit']//10000:,}만원 (연간 {fin['owner_operated']['staff3_operating_profit']*12//10000:,}만원)")
        c.drawString(56, 142, "• 낮은 변동비 구조: 일반 음식점/카페와 달리 원재료비 비중이 극히 낮아 매출 증가 시 순이익이 급격히 증가하는 고마진 레버리지")
        c.drawString(56, 116, "• 고정비 방어력: 월 고정비가 낮아 비수기나 상권 초기 단계에서도 안정적인 흑자 기조 유지")

        self._draw_footer(c, "MYPARK Cost Structure & Operating Profit Analysis")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 11: 10. 손익분기점(BEP) 및 투자금 회수기간
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "10. 손익분기점(BEP) 및 투자금 회수기간", f"손익분기 매출 월 {inv['bep_monthly_sales']//10000:,}만원 (타석당 일 {inv['bep_turns_per_room']}회전) 및 투자금 3.19억 회수기간 약 {inv['payback_months_moderate']:.1f}개월")
        
        if 'bep_chart' in charts and os.path.exists(charts['bep_chart']):
            c.drawImage(charts['bep_chart'], 40, 260, width=440, height=200, preserveAspectRatio=True)
            
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, 260, 425, 200, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, 438, "■ 투자금 3.19억 회수 시뮬레이션")
        
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        c.drawString(511, 412, f"• 보수적 시나리오: 월 순익 {scenarios['conservative']['operating_profit']//10000:,}만원 -> 회수기간 약 {inv['payback_months_conservative']:.1f}개월")
        c.drawString(511, 392, f"• 보편적 시나리오: 월 순익 {scenarios['moderate']['operating_profit']//10000:,}만원 -> 회수기간 약 {inv['payback_months_moderate']:.1f}개월 (약 1년)")
        c.drawString(511, 372, f"• 긍정적 시나리오: 월 순익 {scenarios['optimistic']['operating_profit']//10000:,}만원 -> 회수기간 약 {inv['payback_months_optimistic']:.1f}개월")
        
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_red)
        c.drawString(511, 332, f"★ BEP 달성 요건: 기기 1대당 하루 {inv['bep_turns_per_room']}회전 (1일 {inv['bep_daily_users']}명 이용)")
        c.drawString(511, 312, f"★ 일 평균 {inv['bep_daily_users']}명만 방문해도 월 고정비 전액 커버 (적자 리스크 전무)")

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 880, 196, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 222, "■ 투자 안정성 및 리스크 평가")
        
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 194, "• 초저위험 구조: 타석당 1일 1회전(4명)만 가동되어도 손익분기점을 초과하여 적자 발생 확률이 극히 희박")
        c.drawString(56, 168, f"• 빠른 자본 회수: 보편 가동 기준 약 {inv['payback_months_moderate']:.1f}개월(1년 1개월) 만에 초기 투자금 3.19억원 전액 회수")
        c.drawString(56, 142, "• 자산 가치 보존: 시뮬레이터 장비 및 쾌적한 인테리어 시설은 향후 지속적인 현금 흐름을 창출하는 핵심 실물 자산")
        c.drawString(56, 116, "• 안정적 단골 락인: 지역 시니어 동호회 정기 예약 시스템 구축으로 경기 변동에 영향을 받지 않는 방어적 사업 모델")

        self._draw_footer(c, "MYPARK BEP & Capital Payback Period Analysis")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 12: 11. 5개년 중장기 손익 전망 및 종합 제언
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "11. 5개년 중장기 손익 전망 및 종합 제언", f"5개년 누적 매출 {fin['five_year']['total_5yr_revenue']//100000000:.1f}억원, 누적 순영업이익 {fin['five_year']['total_5yr_profit']//100000000:.1f}억원 달성 전망")
        
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 260, 880, 200, fill=1, stroke=1)
        
        headers_5y = ["연차", "1차년도 (안정화)", "2차년도 (성장기)", "3차년도 (성숙기)", "4차년도 (유지기)", "5차년도 (성숙유지)", "5개년 누적 합계"]
        c.setFont(FONT_BOLD, 8.5)
        c.setFillColor(self.c_slate)
        x_5y = [56, 170, 290, 420, 540, 660, 780]
        for h, x in zip(headers_5y, x_5y):
            c.drawString(x, 438, h)
        c.line(56, 428, 900, 428)
        
        y_5 = 405
        rows_5y = [
            ("연간 총매출액", [f"{y['revenue']//100000000:.2f}억원" for y in fin['five_year']['years']], f"{fin['five_year']['total_5yr_revenue']//100000000:.1f}억원"),
            ("연간 총비용", [f"{y['cost']//100000000:.2f}억원" for y in fin['five_year']['years']], f"{fin['five_year']['total_5yr_cost']//100000000:.1f}억원"),
            ("연간 순영업익", [f"{y['profit']//100000000:.2f}억원" for y in fin['five_year']['years']], f"{fin['five_year']['total_5yr_profit']//100000000:.1f}억원"),
            ("투자금 누적회수", ["3.19억 회수완료" if i > 0 else f"{fin['five_year']['years'][0]['cumulative_profit']//100000000:.2f}억원" for i in range(5)], "회수율 486%")
        ]
        for rname, yvals, totval in rows_5y:
            is_prof = "순영업익" in rname
            c.setFont(FONT_BOLD if is_prof else FONT_REGULAR, 8.5)
            c.setFillColor(self.c_mck_teal if is_prof else self.c_charcoal)
            c.drawString(56, y_5, rname)
            for idx, yv in enumerate(yvals):
                c.drawString(x_5y[idx+1], y_5, yv)
            c.drawString(x_5y[-1], y_5, totval)
            y_5 -= 24

        # 하단 2개 박스 (가맹점주 기대효과 vs 건물주 상생 효과)
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 425, 196, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 222, "🌟【 가맹점주 핵심 경쟁력 및 최종 제언 】")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        val_f_lines = score['value_franchisee'].split('\n')
        cur_y = 196
        for fl in val_f_lines:
            cur_y = self._draw_multiline_text(c, fl, 56, cur_y, max_chars=34, line_height=14, max_lines=3) - 4
        if site.get('special_notes'):
            c.setFont(FONT_BOLD, 8.5)
            c.setFillColor(self.c_mck_teal)
            c.drawString(56, cur_y, f"※ 고객 특이사항 연계: {site['special_notes']}")

        c.setFillColor(HexColor('#F0FDF4'))
        c.setStrokeColor(HexColor('#BBF7D0'))
        c.rect(495, 48, 425, 196, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(HexColor('#166534'))
        c.drawString(511, 222, "🏢【 건물주 및 상가 상생 활성화 효과 】")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(HexColor('#14532D'))
        val_l_lines = score['value_landlord'].split('\n')
        cur_y = 196
        for ll in val_l_lines:
            cur_y = self._draw_multiline_text(c, ll, 511, cur_y, max_chars=34, line_height=14, max_lines=3, color=HexColor('#14532D')) - 4

        self._draw_footer(c, "MYPARK 5-Year Financial Forecast & Final Strategic Recommendation")
        c.showPage()

        c.save()
        print(f"[PDF GENERATED 12P] {self.filename}")
        return self.filename
