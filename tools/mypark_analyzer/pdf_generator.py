# -*- coding: utf-8 -*-
"""McKinsey Classic Executive Theme PDF 보고서 생성기 (PART 2 흐름 재구성 완료본)"""
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .config import DEFAULT_SETTINGS, fmt_eok, fmt_won_full, fmt_months
from .finance_engine import FinanceEngine

# -----------------------------------------------------------------------------
# TTF 폰트 등록
# -----------------------------------------------------------------------------
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

def init_fonts(custom_candidates=None):
    global FONT_REGULAR, FONT_BOLD
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_pairs = custom_candidates or [
        (os.path.join(current_dir, 'fonts', 'IBMPlexSansKR-Regular.ttf'), os.path.join(current_dir, 'fonts', 'IBMPlexSansKR-Bold.ttf')),
        (os.path.join(current_dir, 'fonts', 'MalgunGothic.ttf'), os.path.join(current_dir, 'fonts', 'MalgunGothicBold.ttf')),
        (r'C:\Windows\Fonts\malgun.ttf', r'C:\Windows\Fonts\malgunbd.ttf'),
        (r'C:\Windows\Fonts\NanumGothic.ttf', r'C:\Windows\Fonts\NanumGothicBold.ttf'),
        ('/usr/share/fonts/truetype/nanum/NanumGothic.ttf', '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf'),
    ]
    for regular_path, bold_path in font_pairs:
        if os.path.exists(regular_path):
            try:
                pdfmetrics.registerFont(TTFont('KoreanFont', regular_path))
                bold_source = bold_path if os.path.exists(bold_path) else regular_path
                pdfmetrics.registerFont(TTFont('KoreanFontBold', bold_source))
                FONT_REGULAR = 'KoreanFont'
                FONT_BOLD = 'KoreanFontBold'
                print(f"[SUCCESS] Registered Korean Font: {regular_path} (bold: {bold_source})")
                return True
            except Exception as e:
                print(f"[WARN] Failed to load {regular_path}: {e}")

    FONT_REGULAR = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"
    print("[FONT WARNING] 한글 폰트를 찾지 못해 Helvetica로 대체합니다. 생성되는 PDF의 한글이 깨질 수 있습니다.")
    return False

init_fonts()


class PDFGenerator:
    """맥킨지 클래식 이그제큐티브 스타일 PDF 생성기"""

    def __init__(self, filename="mypark_market_analysis.pdf"):
        self.filename = filename
        self.pagesize = landscape(A4)
        self.width, self.height = self.pagesize

        # Monochrome Ledger Color Palette
        self.c_mck_navy = HexColor('#14181F')      # ink (was navy)
        self.c_mck_teal = HexColor('#1F5A44')       # emerald accent (was teal)
        self.c_charcoal = HexColor('#14181F')
        self.c_slate = HexColor('#6B6F76')
        self.c_line = HexColor('#D3D1CB')
        self.c_box_bg = HexColor('#EBEAE5')
        self.c_tint_blue = HexColor('#E3ECE7')      # emerald-tinted card bg (was blue tint)
        self.c_white = HexColor('#FFFFFF')
        self.c_red = HexColor('#B23A2E')
        self.c_paper = HexColor('#F4F3F0')          # page background (ledger paper)

    def _wrap_text_to_width(self, c, text, font_name, font_size, max_width, max_lines=2):
        """긴 텍스트를 max_width 안에 들어오도록 줄바꿈. max_lines 초과분은 말줄임표 처리."""
        words = text.split(' ')
        lines = []
        cur = ''
        for w in words:
            candidate = f"{cur} {w}".strip()
            if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
                cur = candidate
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            last = lines[-1]
            while pdfmetrics.stringWidth(last + '…', font_name, font_size) > max_width and len(last) > 1:
                last = last[:-1]
            lines[-1] = last + '…'
        return lines

    def _draw_mckinsey_header(self, c, section_title, lead_text):
        c.setFillColor(self.c_paper)
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
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
        pop_source_tag = "MYPARK 추정 모델" if demo.get('is_estimated') else "KOSIS 실측"
        right_col_w = (self.width - 40) - 495  # 495 = 우측 카드 표준 시작 x좌표, self.width=841.89(A4 가로)

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
        c.drawString(60, self.height - 175, f"{site['rooms']}타석 {site['area_pyeong']}평 표준 모델  |  상권 분석 및 투자 타당성 평가")

        c.setStrokeColor(self.c_mck_teal)
        c.setLineWidth(2)
        c.line(60, self.height - 195, self.width - 60, self.height - 195)

        c.setFillColor(self.c_white)
        c.setFont(FONT_REGULAR, 12)
        notes_str = f"  |  특이사항: {site['special_notes']}" if site.get('special_notes') else ""
        c.drawString(60, self.height - 230, f"• 대상 사업지: {site['full_address']}{notes_str}")
        _cover_scope = f"{site['sigungu']} 전체 (관할 행정동 {demo.get('district_dong_count', 0)}개 전수)" if demo.get('district_wide_analysis') else f"{site['sido']} {site['sigungu']} {target_dong} 반경 3km 생활권"
        c.drawString(60, self.height - 255, f"• 상권 분석 대상: {_cover_scope}")
        c.drawString(60, self.height - 280, f"• 출점 모델: {site['rooms']}타석 ({site['area_pyeong']}평형)  |  분석 기준일: {data.get('created_at', '2026.08')}")

        c.setFillColor(self.c_white)
        c.setFont(FONT_BOLD, 11)
        c.drawString(60, 60, "마이파크(MYPARK) 가맹본부 데이터전략실")
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(HexColor('#9BA79E'))
        c.drawString(60, 44, "CONFIDENTIAL: 본 문서는 사업성 검토 목적 외 무단 복제 및 배포를 금합니다.")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 3: 2. 배후 인구 및 타겟 연령 분석
        # ---------------------------------------------------------------------
        is_district_wide = demo.get('district_wide_analysis', False)
        _sec1_sub = f"관할 행정동 {demo.get('district_dong_count', 0)}개 전수 기준 50대 이상 시니어 {demo['senior_50_plus']:,}명({demo['senior_ratio']}%)의 핵심 소비 수요 확보" if is_district_wide else f"반경 3km 내 50대 이상 시니어 {demo['senior_50_plus']:,}명({demo['senior_ratio']}%)의 핵심 소비 수요 확보"
        self._draw_mckinsey_header(c, "1. 구 전체 인구 및 타겟 연령 분석" if is_district_wide else "1. 3km 생활권 인구 및 타겟 연령 분석", _sec1_sub)

        tbl_bottom = 268
        tbl_top = 500
        tbl_h = tbl_top - tbl_bottom
        head_h = 28

        # 좌측: 행정동별 인구 집계 (렛저 테이블)
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, tbl_bottom, 425, tbl_h, fill=1, stroke=1)
        c.setFillColor(self.c_mck_navy)
        c.rect(40, tbl_top - head_h, 425, head_h, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_white)
        _dcnt = demo.get('district_dong_count', 0)
        _has_dong_rows = bool(demo.get('dongs'))
        if is_district_wide:
            if _has_dong_rows:
                _tbl_title = f"{site['sigungu']} 전체 {_dcnt}개 행정동 중 인구 상위 {min(6, len(demo['dongs']))}개 ({pop_source_tag})"
            else:
                _tbl_title = f"{site['sigungu']} 전체 {_dcnt}개 행정동 통합 인구 ({pop_source_tag})"
        else:
            _tbl_title = f"{target_dong} 반경 3km 행정동별 인구 집계 ({pop_source_tag})"
        c.drawString(56, tbl_top - 19, _tbl_title)

        col_y = tbl_top - head_h - 20
        c.setFont(FONT_BOLD, 8)
        c.setFillColor(self.c_slate)
        c.drawString(56, col_y, "행정동명")
        c.drawRightString(230, col_y, "총 인구")
        c.drawRightString(330, col_y, "50대 이상")
        c.drawRightString(429, col_y, "시니어 비중")
        c.setStrokeColor(self.c_line)
        c.setLineWidth(0.8)
        c.line(56, col_y - 8, 429, col_y - 8)

        # 동별 인구 내역을 못 받은 구 전체 분석에서는 빈 표를 남기지 않고,
        # 실제 관할 행정동 이름을 그대로 나열해 집계 범위를 보여준다.
        if is_district_wide and not _has_dong_rows:
            _names = demo.get('district_dong_names', [])
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_charcoal)
            _ny = col_y - 26
            for _ln in self._wrap_text_to_width(c, "집계 대상 행정동: " + ', '.join(_names), FONT_REGULAR, 8.5, 373, max_lines=5):
                c.drawString(56, _ny, _ln)
                _ny -= 13
            c.setFont(FONT_BOLD, 9)
            c.setFillColor(self.c_mck_navy)
            c.drawString(56, _ny - 8, f"{site['sigungu']} 전체 인구")
            c.drawRightString(230, _ny - 8, f"{demo['total_pop']:,}명")
            c.drawRightString(330, _ny - 8, f"{demo['senior_50_plus']:,}명")
            c.setFillColor(self.c_mck_teal)
            c.drawRightString(429, _ny - 8, f"{demo['senior_ratio']}%")

        row_h1 = min(24, (col_y - 8 - (tbl_bottom + 12)) / max(1, len(demo['dongs'][:6])))
        y_d = col_y - 8 - row_h1 + 7
        for ridx, d in enumerate(demo['dongs'][:6]):
            if ridx % 2 == 1:
                c.setFillColor(self.c_box_bg)
            else:
                c.setFillColor(self.c_paper)
            c.rect(41, y_d - 7, 423, row_h1, fill=1, stroke=0)
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_charcoal)
            c.drawString(56, y_d, str(d['dong']))
            c.drawRightString(230, y_d, f"{d['total']:,}명")
            s_val = d.get('senior_50', int(d['total'] * (demo['senior_ratio'] / 100.0)))
            c.drawRightString(330, y_d, f"{s_val:,}명")
            c.setFillColor(self.c_mck_teal)
            c.setFont(FONT_BOLD, 8.5)
            c.drawRightString(429, y_d, f"{d.get('senior_ratio', demo['senior_ratio'])}%")
            y_d -= row_h1

        # 구 전체 분석에서는 위 6개 행이 구 전체 합계가 아니므로, 합계 기준이
        # 무엇인지 표 안에 명시해 오해(6개 동 = 구 전체)를 막는다.
        if is_district_wide and _has_dong_rows:
            c.setFont(FONT_BOLD, 8)
            c.setFillColor(self.c_mck_navy)
            c.drawString(56, tbl_bottom + 9, f"{site['sigungu']} 전체 {_dcnt}개 행정동 합계")
            c.drawRightString(230, tbl_bottom + 9, f"{demo['total_pop']:,}명")
            c.drawRightString(330, tbl_bottom + 9, f"{demo['senior_50_plus']:,}명")
            c.setFillColor(self.c_mck_teal)
            c.drawRightString(429, tbl_bottom + 9, f"{demo['senior_ratio']}%")

        # 우측: 연령대 분포 매트릭스 (렛저 테이블)
        box2_right = self.width - 40
        box2_w = box2_right - 495
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, tbl_bottom, box2_w, tbl_h, fill=1, stroke=1)
        c.setFillColor(self.c_mck_navy)
        c.rect(495, tbl_top - head_h, box2_w, head_h, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_white)
        c.drawString(511, tbl_top - 19, "50대 이상 시니어 연령대 분포 매트릭스")

        col_y2 = tbl_top - head_h - 20
        c.setFont(FONT_BOLD, 8)
        c.setFillColor(self.c_slate)
        c.drawString(511, col_y2, "연령 구간")
        c.drawRightString(635, col_y2, "인구수")
        c.drawRightString(685, col_y2, "비중")
        c.drawString(708, col_y2, "파크골프 이용 행태")
        c.setStrokeColor(self.c_line)
        c.line(511, col_y2 - 8, box2_right - 16, col_y2 - 8)

        age_matrix = [
            ("50대 (액티브)", f"{demo['pop_50s']:,}명", f"{demo['ratio_50s']}%", "부부/동호회 주말 및 평일 야간"),
            ("60대 (은퇴 시니어)", f"{demo['pop_60s']:,}명", f"{demo['ratio_60s']}%", "평일 주간 정기 리그 핵심 주력"),
            ("70대 이상 (실버)", f"{demo['pop_70_plus']:,}명", f"{demo['ratio_70_plus']}%", "오전 시간대 건강 증진 친목 모임"),
            ("50대+ 합계", f"{demo['senior_50_plus']:,}명", f"{demo['senior_ratio']}%", "평일 낮 10~17시 풀가동 타겟"),
        ]
        beh_col_w = box2_right - 16 - 708
        row_h2 = (col_y2 - 8 - (tbl_bottom + 10)) / len(age_matrix)
        y_a = col_y2 - 8 - row_h2 + 20
        for ridx, (grp, cnt, rt, beh) in enumerate(age_matrix):
            is_total = (ridx == len(age_matrix) - 1)
            if is_total:
                c.setFillColor(self.c_tint_blue)
            elif ridx % 2 == 1:
                c.setFillColor(self.c_box_bg)
            else:
                c.setFillColor(self.c_paper)
            c.rect(496, y_a - row_h2 + 13, box2_w - 2, row_h2, fill=1, stroke=0)
            c.setFont(FONT_BOLD if is_total else FONT_REGULAR, 8.5)
            c.setFillColor(self.c_mck_navy if is_total else self.c_charcoal)
            c.drawString(511, y_a, grp)
            c.drawRightString(635, y_a, cnt)
            c.setFillColor(self.c_mck_teal)
            c.drawRightString(685, y_a, rt)
            c.setFont(FONT_REGULAR, 7.5)
            c.setFillColor(self.c_slate)
            beh_lines = self._wrap_text_to_width(c, beh, FONT_REGULAR, 7.5, beh_col_w, max_lines=2)
            by = y_a
            for bl in beh_lines:
                c.drawString(708, by, bl)
                by -= 9
            y_a -= row_h2

        _senior_total = max(1, demo['senior_50_plus'])
        _60s_share = demo['pop_60s'] / _senior_total * 100
        _70s_share = demo['pop_70_plus'] / _senior_total * 100
        _insight_scope_txt = "구 전체 관할 행정동" if is_district_wide else "반경 3km 내"
        _insight_bullets = [
            f"• 타겟 집적도: {_insight_scope_txt} 50대 이상 인구 {demo['senior_50_plus']:,}명({demo['senior_ratio']}%) 확보로 안정적 고객 풀 형성",
            f"• 60대 주력 고객군 {_60s_share:.0f}%: 은퇴 후 평일 낮 시간 여유가 있는 60대가 전체 시니어 중 {_60s_share:.0f}%를 차지하여 평일 낮 가동률 극대화",
            f"• 70대 실버 헬스케어 수요 {_70s_share:.0f}%: 관절 부담이 없는 파크골프 특성상 부부 동반 및 시니어 커뮤니티 공간으로 정착",
            "• 일반 스크린골프 대비 회전율 우위: 야간 직장인 편중 매장과 달리 주간 7시간 집중 가동으로 일일 높은 회전수 확보",
        ]
        apt_sum = demo.get('apartment_summary')
        if apt_sum:
            yr_txt = f"{apt_sum['year_min']}년~{apt_sum['year_max']}년 준공" if apt_sum.get('year_min') else "준공년도 확인 중"
            _insight_bullets.append(f"• 배후 주거 기반: {apt_sum['scope_label']} 공동주택 {apt_sum['complex_count']}개 단지 (표본 {apt_sum['sample_count']}개 단지 합산 {apt_sum['total_households_sample']:,}세대, {yr_txt}) — 국토교통부 공동주택 기본정보 기준")

        # 박스 높이를 실제 불릿 수에 맞춰 계산한다 (아파트 정보 유무에 따라 줄 수가
        # 달라지는데 높이가 고정이면 하단에 죽은 여백이 크게 남는다).
        _ins_top = 252
        _ins_line_h = 28
        _ins_h = 26 + 30 + len(_insight_bullets) * _ins_line_h
        _ins_bottom = _ins_top - _ins_h
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, _ins_bottom, self.width - 80, _ins_h, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, _ins_top - 26, "■ 구 전체 시니어 인구 분석 시사점" if is_district_wide else "■ 3km 생활권 시니어 인구 분석 시사점")

        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        _ins_y = _ins_top - 56
        for _ib in _insight_bullets:
            c.drawString(56, _ins_y, _ib)
            _ins_y -= _ins_line_h

        self._draw_footer(c, "KOSIS National Statistics Portal" + (" (※ 행정동 추정 모델 적용)" if demo.get("is_estimated") else f" ({demo.get('base_date', '2026.08')})"))
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 4: 3. 상권 소비력 및 유동 패턴 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "2. 상권 소비력 및 유동 패턴 분석", f"주거지역 {comm.get('residential_pop_ratio', 93.4)}% 밀집 상권 및 스크린골프 상위 20% 월매출 {comm['top_20_sales']//10000:,}만원 시장 타겟팅")

        chart_bottom, chart_top = 260, 500
        chart_h = chart_top - chart_bottom
        if 'sales_trend' in charts and os.path.exists(charts['sales_trend']):
            c.drawImage(charts['sales_trend'], 40, chart_bottom, width=440, height=chart_h, preserveAspectRatio=True, anchor='n')

        head_h = 28
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, chart_bottom, right_col_w, chart_h, fill=1, stroke=1)
        c.setFillColor(self.c_mck_navy)
        c.rect(495, chart_top - head_h, right_col_w, head_h, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_white)
        c.drawString(511, chart_top - 19, "유사 골프업종 수익구조 격차 (MYPARK 추정)")

        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        ry = chart_top - head_h - 22
        c.drawString(511, ry, f"• 상위 20% 매장 월매출: 약 {comm['top_20_sales']//10000:,}만원 (대형 최신 매장)")
        ry -= 20
        c.drawString(511, ry, f"• 하위 20% 매장 월매출: 약 {comm.get('bottom_20_sales', 3020000)//10000:,}만원 (노후 소형 매장)")
        ry -= 20
        c.drawString(511, ry, "• 시장 특성: 시설 규모와 쾌적성에 따른 매출 양극화 뚜렷")
        ry -= 20
        c.setFillColor(self.c_mck_teal)
        c.drawString(511, ry, f"★ 마이파크 포지셔닝: {site['rooms']}타석 최신식 플래그십으로 상위 20% 시장 흡수")
        ry -= 30

        c.setStrokeColor(self.c_line)
        c.setLineWidth(0.6)
        c.line(511, ry + 14, 495 + right_col_w - 16, ry + 14)
        ry -= 4

        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_mck_teal)
        c.drawString(511, ry, f"■ 요일별 매출 비중: 주중 {100 - comm['day_distribution']['주말평균비중']*2:.1f}% / 주말 {comm['day_distribution']['주말평균비중']*2:.1f}%")
        ry -= 20
        c.drawString(511, ry, f"■ 시간대별 비중: 주간(10~17시) {comm['time_distribution']['주간_10_17시_비중']}% 집중 가동")

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 96, self.width - 80, 148, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 222, "■ 상권 소비력 종합 평가")

        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 194, f"• 소비 수준: {comm['spending_grade']} (시니어 여가 및 생활체육 소비 여력 충분)")
        c.drawString(56, 168, f"• 주간 매출 집중형: 평일 10~17시 매출 비중이 {comm['time_distribution']['주간_10_17시_비중']}%로 주간 시간대 수익 창출력 탁월")
        c.drawString(56, 142, "• 4인 1팀 단체 이용: 파크골프 1팀당 식음료 및 추가 게임비 지출로 객단가 극대화")
        c.drawString(56, 116, "• 안정적 단골 매출: 동호회 정기 예약(월 단위 선결제) 비중이 높아 계절성 리스크 방어")

        self._draw_footer(c, "MYPARK Regional Tier Estimation Model")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 5: 4. 업종 성장률 및 골프 특화도
        # ---------------------------------------------------------------------
        _top_ind = comm['top_growth_industries'][0]
        self._draw_mckinsey_header(c, "3. 업종 성장률 및 골프 특화도", f"성장률 1위 업종 {_top_ind['name']}({_top_ind['growth']}) 및 전국 평균 대비 {comm['golf_industry_density']['multiple']}배 높은 골프 특화 상권")

        if 'growth_radar' in charts and os.path.exists(charts['growth_radar']):
            c.drawImage(charts['growth_radar'], 40, chart_bottom, width=440, height=chart_h, preserveAspectRatio=True, anchor='n')

        box4_right = self.width - 40
        box4_w = box4_right - 495
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, chart_bottom, box4_w, chart_h, fill=1, stroke=1)
        c.setFillColor(self.c_mck_navy)
        c.rect(495, chart_top - head_h, box4_w, head_h, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_white)
        c.drawString(511, chart_top - 19, "TOP 5 매출 증가 업종 (MYPARK 지역등급 추정)")

        col_y5 = chart_top - head_h - 22
        c.setFont(FONT_BOLD, 8)
        c.setFillColor(self.c_slate)
        c.drawString(511, col_y5, "순위")
        c.drawString(535, col_y5, "업종명")
        c.drawRightString(670, col_y5, "성장률")
        c.drawString(693, col_y5, "업종 상태")
        c.setStrokeColor(self.c_line)
        c.line(511, col_y5 - 8, box4_right - 16, col_y5 - 8)

        status_col_w = box4_right - 16 - 693
        n_ind = max(1, len(comm['top_growth_industries']))
        row_h5 = (col_y5 - 8 - (chart_bottom + 10)) / n_ind
        y_g = col_y5 - 8 - row_h5 + 18
        for ridx, ind in enumerate(comm['top_growth_industries']):
            if ridx % 2 == 1:
                c.setFillColor(self.c_box_bg)
            else:
                c.setFillColor(self.c_paper)
            c.rect(496, y_g - row_h5 + 11, box4_w - 2, row_h5, fill=1, stroke=0)
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_charcoal)
            c.drawString(511, y_g, str(ind['rank']))
            c.drawString(535, y_g, ind['name'])
            c.setFillColor(self.c_mck_teal)
            c.setFont(FONT_BOLD, 8.5)
            c.drawRightString(670, y_g, ind['growth'])
            c.setFont(FONT_REGULAR, 7.5)
            c.setFillColor(self.c_slate)
            status_lines = self._wrap_text_to_width(c, ind['status'], FONT_REGULAR, 7.5, status_col_w, max_lines=2)
            sy = y_g
            for sl in status_lines:
                c.drawString(693, sy, sl)
                sy -= 9
            y_g -= row_h5

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 96, self.width - 80, 148, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 222, "■ 골프 특화 상권 시사점")

        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        _golf_ind = next((d for d in comm['top_growth_industries'] if '골프' in d['name']), comm['top_growth_industries'][0])
        c.drawString(56, 194, f"• 레저 스포츠 소비 상위권: {comm['top_growth_industries'][0]['name']}({comm['top_growth_industries'][0]['growth']})이 1위, {_golf_ind['name']}({_golf_ind['growth']})이 {_golf_ind['rank']}위로 시니어 여가 업종이 성장 상위 점유")
        c.drawString(56, 168, f"• 골프 인프라 밀집도: 전국 평균 대비 {comm['golf_industry_density']['multiple']}배 높은 골프 시설 집적으로 검증된 골프 수요층 상존")
        c.drawString(56, 142, "• 일반 골프의 파크골프 전환: 일반 골프 비용/체력 부담을 느끼는 시니어층의 스크린 파크골프 유입 가속화")
        c.drawString(56, 116, "• 성장 단계: 단순 유행이 아닌 시니어 여가 문화의 핵심 트렌드로 정착 단계 진입")

        self._draw_footer(c, "MYPARK Regional Tier Estimation Model")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 6: 5. 경쟁 환경 및 시설 공급 갭 분석
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "4. 경쟁 환경 및 시설 공급 갭 분석", comm['competitor_summary'])

        # 카드 개수/너비는 실제로 확인된 경쟁사 수에 맞춰 동적으로 계산한다.
        # (하드코딩된 4칸 틀에 3곳만 채워 오른쪽이 비는 문제 방지)
        comps_all = comm['competitors']
        MAX_CARDS = 5
        comps = comps_all[:MAX_CARDS]
        start_x = 40
        gap_x = 10
        avail_w = (self.width - 40) - start_x
        n = max(1, len(comps))
        card_w = (avail_w - (n - 1) * gap_x) / n

        # 카드 높이는 고정값이 아니라 실제 내용 길이에 맞춰 계산한다.
        # (내용은 짧은데 박스만 크면 하단에 빈 여백이 크게 남는 문제 방지)
        card_bottom = 48
        head_h = 46
        stat_h = 58
        FEAT_MAX_LINES = 4
        body_w_probe = card_w - 20

        def _measure_card_content_h(comp):
            name_lines = self._wrap_text_to_width(c, str(comp['name']), FONT_BOLD, 9.5, card_w - 16, max_lines=2)
            addr_lines = self._wrap_text_to_width(c, comp['address'], FONT_REGULAR, 7.5, body_w_probe, max_lines=3)
            sys_lines = self._wrap_text_to_width(c, comp['system'], FONT_REGULAR, 7.5, body_w_probe, max_lines=2)
            feat_lines = self._wrap_text_to_width(c, str(comp.get('features', '-')), FONT_REGULAR, 7.5, body_w_probe, max_lines=FEAT_MAX_LINES)
            h = head_h + 10 + stat_h + 16
            h += 13 + len(addr_lines) * 12 + 6
            h += 13 + len(sys_lines) * 12 + 6
            h += 20
            h += 13 + len(feat_lines) * 12
            h += 16  # 하단 여백
            return h

        content_heights = [_measure_card_content_h(comp) for comp in comps] or [260]
        card_h = max(260, min(452, max(content_heights)))
        card_top = 500
        card_bottom = card_top - card_h
        head_bottom = card_top - head_h

        if not comps:
            # 확인된 경쟁사가 0곳(블루오션 판정)인 경우 빈 화면 대신 실제 요약 문구를 카드 자리에 표시
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(start_x, card_bottom, avail_w, card_h, fill=1, stroke=1)
            c.setFont(FONT_BOLD, 11)
            c.setFillColor(self.c_mck_navy)
            msg_lines = self._wrap_text_to_width(c, comm.get('competitor_summary', '반경 3km 내 확인된 경쟁 매장이 없습니다.'), FONT_BOLD, 11, avail_w - 80, max_lines=4)
            my = card_bottom + card_h/2 + (len(msg_lines) - 1) * 9
            for ml in msg_lines:
                c.drawCentredString(start_x + avail_w/2, my, ml)
                my -= 18

        for idx, comp in enumerate(comps):
            cur_x = start_x + idx * (card_w + gap_x)

            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(cur_x, card_bottom, card_w, card_h, fill=1, stroke=1)

            c.setFillColor(self.c_mck_navy)
            c.rect(cur_x, head_bottom, card_w, head_h, fill=1, stroke=0)
            c.setFillColor(self.c_white)
            c.setFont(FONT_BOLD, 9.5)

            # 상호명은 글자수로 자르지 않고 단어(공백) 경계에서 줄바꿈한다.
            name_lines = self._wrap_text_to_width(c, str(comp['name']), FONT_BOLD, 9.5, card_w - 16, max_lines=2)
            if len(name_lines) > 1:
                c.drawCentredString(cur_x + card_w/2, head_bottom + 30, name_lines[0])
                c.drawCentredString(cur_x + card_w/2, head_bottom + 13, name_lines[1])
            else:
                c.drawCentredString(cur_x + card_w/2, head_bottom + 21, name_lines[0])

            stat_h = 58
            stat_top = head_bottom - 10
            stat_bottom = stat_top - stat_h
            c.setFillColor(self.c_tint_blue)
            c.rect(cur_x + 8, stat_bottom, card_w - 16, stat_h, fill=1, stroke=0)
            c.setFillColor(self.c_mck_navy)
            c.setFont(FONT_BOLD, 10.5)
            is_hypothetical = '예시 시나리오' in comp.get('status', '')
            if comp.get('rooms', 0) > 0:
                r_str = f"{comp.get('rooms', 0)}타석 규모"
            elif is_hypothetical:
                r_str = "1호점 선점 대상"
            else:
                r_str = "타석 규모 미확인"
            c.drawCentredString(cur_x + card_w/2, stat_top - 22, r_str)
            c.setFont(FONT_REGULAR, 7.5)
            c.setFillColor(self.c_slate)
            status_txt = f"[{comp.get('status', '실측완료')}] {comp.get('system', '스크린 시스템')}"
            status_lines = self._wrap_text_to_width(c, status_txt, FONT_REGULAR, 7.5, card_w - 22, max_lines=2)
            sty = stat_top - 38
            for stl in status_lines:
                c.drawCentredString(cur_x + card_w/2, sty, stl)
                sty -= 10

            body_x = cur_x + 10
            body_w = card_w - 20
            body_y = stat_bottom - 16

            c.setFont(FONT_BOLD, 8)
            c.setFillColor(self.c_charcoal)
            c.drawString(body_x, body_y, "■ 주소:")
            body_y -= 13
            c.setFont(FONT_REGULAR, 7.5)
            addr_lines = self._wrap_text_to_width(c, comp['address'], FONT_REGULAR, 7.5, body_w, max_lines=3)
            for al in addr_lines:
                c.drawString(body_x, body_y, al)
                body_y -= 12
            body_y -= 6

            c.setFont(FONT_BOLD, 8)
            c.setFillColor(self.c_mck_teal)
            c.drawString(body_x, body_y, "■ 시스템:")
            body_y -= 13
            c.setFont(FONT_REGULAR, 7.5)
            sys_lines = self._wrap_text_to_width(c, comp['system'], FONT_REGULAR, 7.5, body_w, max_lines=2)
            for sl in sys_lines:
                c.drawString(body_x, body_y, sl)
                body_y -= 12
            body_y -= 6

            c.setFont(FONT_BOLD, 8)
            c.setFillColor(self.c_charcoal)
            if comp.get('rooms', 0) > 0:
                rooms_str = f"■ 규모: {comp['rooms']}타석 운영"
            elif '예시 시나리오' in comp.get('status', ''):
                rooms_str = "■ 상태: 상업용 매장 미등록"
            else:
                rooms_str = "■ 규모: 타석수 미확인"
            c.drawString(body_x, body_y, rooms_str)
            body_y -= 20

            c.setFont(FONT_BOLD, 8)
            c.setFillColor(self.c_slate)
            c.drawString(body_x, body_y, "■ 특징:")
            body_y -= 13
            feat_str = str(comp.get('features', '-'))
            feat_lines = self._wrap_text_to_width(c, feat_str, FONT_REGULAR, 7.5, body_w, max_lines=FEAT_MAX_LINES)
            c.setFont(FONT_REGULAR, 7.5)
            c.setFillColor(self.c_charcoal)
            for fl in feat_lines:
                c.drawString(body_x, body_y, fl)
                body_y -= 12
            
        _comp_summary = comm.get('competitor_summary', '')
        if '예시 시나리오' in _comp_summary:
            _comp_source = "MYPARK Competitor Database Matching (Hypothetical Scenario, Live Search Unavailable)"
        elif '소상공인시장진흥공단' in _comp_summary:
            _comp_source = "SBIZ (Small Business Market Promotion Agency) Public Data"
        elif '지도 API 실시간 검색' in _comp_summary:
            _comp_source = "Live POI Search (Kakao/TMap/Naver Cross-Verified)"
        else:
            _comp_source = "MYPARK Verified National Store Database"
        self._draw_footer(c, _comp_source)
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 7: 6. 사업지 개요 및 현장 출점 요건 (4대 건축·인프라 체크리스트)
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "5. 사업지 개요 및 현장 출점 요건", f"{site['rooms']}타석 {site['area_pyeong']}평 규모 출점을 위한 4대 건축·인프라 현장 실측 기준")
        
        space_card_lines = [f"• 대상 주소: {site['full_address']}"]
        if site.get('special_notes'):
            space_card_lines.append(f"• 고객 특이사항: {site['special_notes']}")
        space_card_lines += [
            f"• 권장 면적: 전용 {site['area_pyeong']}평 ({site['rooms']}타석 + 카페/락커룸 최적 배치)",
            f"• 층고 기준: {site['clear_height_spec']}",
            f"• 보/배관 간섭: 센서 투사 영역 및 스윙 궤적 내 장애물 사전 실측 필수",
            f"• 권장 층수: 고객 접근성 높은 지상 2~3층 권장 (쾌적한 지하 1층 가능)",
            f"• 바닥 하중: 스크린 타석 및 키오스크 하중(300kg/㎡ 이상) 적합 여부"
        ]
        cards = [
            (40, 260, 425, 240, "공간 및 유효 층고 요건", space_card_lines),
            (495, 260, 425, 240, "주차 및 차량 접근성 기준", [
                f"• 주차 요건: {site['parking_spec']}",
                f"• 고객 특성: 자차 이용 시니어 비중 80% 이상으로 편리한 진출입 필수",
                f"• 진입 여건: 램프 폭 및 회전각 여유 있는 자주식 주차장 최우선",
                f"• 도로 접면: 주요 간선도로 및 대단지 아파트 진입로 인접 우수",
                f"• 보행 동선: 대중교통(버스/지하철) 도보 5~10분 생활권 완비",
                f"• 승하차 편의: 주차장에서 매장 입구까지 단차 없는 완만한 동선"
            ]),
            (40, 48, 425, 196, "건물 편의 및 승강기 설비", [
                f"• 고객 편의: {site['accessibility_spec']}",
                f"• 계단 여건: 계단 단차가 낮거나 완만한 진입 경사로 확보 필요",
                f"• 냉난방/환기: 개별 공조 및 고성능 환기 덕트 설치 공간 확인",
                f"• 소음/진동: 상하층 타 업종 간섭 방지 방음/흡음 설계 시공",
                f"• 쾌적성: 남녀 분리 청결 화장실 및 쾌적한 로비 라운지 구축",
                f"• 장애인 편의: 엘리베이터 단차 제거 및 자동문 출입구 권장"
            ]),
            (495, 48, 425, 196, "인허가 및 건축물 용도", [
                f"• 적합 용도: {site['zoning_spec']}",
                f"• 지자체 체육시설: 체육시설의 설치·이용에 관한 법률 인허가 검토",
                f"• 소방 기준: 스프링클러, 비상유도등, 비상탈출구 완비 점검",
                f"• 전기 용량: {site['rooms']}타석 시뮬레이터 동시 가동 대비 {max(25, site['rooms']*3)}kW 이상 인입",
                f"• 정화조 용량: 일 최대 150명 이상 동시 이용 기준 충족 점검",
                f"• 행정 절차: 관할 구청 건축과 및 체육진흥과 용도 사전 협의"
            ]),
        ]
        for x, y, w, h, title, lines in cards:
            card_right = min(x + w, self.width - 40)
            card_w_actual = card_right - x
            head_h_c = 26
            c.setFillColor(self.c_box_bg)
            c.setStrokeColor(self.c_line)
            c.rect(x, y, card_w_actual, h, fill=1, stroke=1)
            c.setFillColor(self.c_mck_navy)
            c.rect(x, y + h - head_h_c, card_w_actual, head_h_c, fill=1, stroke=0)
            c.setFont(FONT_BOLD, 9.5)
            c.setFillColor(self.c_white)
            c.drawString(x + 14, y + h - head_h_c + 9, title)
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_charcoal)
            y_l = y + h - head_h_c - 20
            text_w = card_w_actual - 24
            for l in lines[:6]:
                wrapped = self._wrap_text_to_width(c, l, FONT_REGULAR, 8.5, text_w, max_lines=2)
                for wl in wrapped:
                    c.drawString(x + 14, y_l, wl)
                    y_l -= 13
                y_l -= 5

        self._draw_footer(c, "Building Code & Field Inspection Checklist")
        c.showPage()
        # ---------------------------------------------------------------------
        # Page 2: 1. 입지 적합성 종합 판정 (5-Dimension Diamond Scoring)
        # [PART 2 재구성: 재무 금액 배제, 순수 입지 적합성 평가 전진 배치]
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "6. 입지 적합성 종합 판정 (5-Dimension Diamond Scoring)", f"앞선 5개 항목 분석을 종합한 다이아몬드 스코어링 총점 {score['total_score']}점({score['grade']}등급) - {score['grade_desc']}")

        # 접근성 지표: infra(버스정류장 수 등)는 실측 API가 아니라 지역등급(4단계)별
        # 고정값 테이블(commercial_data.py)에서 나온다 — 같은 등급이면 어느 주소든
        # 동일한 숫자가 나오므로, 이 주소만의 실측치인 것처럼 문구를 쓰지 않는다.
        _infra = comm.get('infra', {})
        _bus_count = _infra.get('버스정류장', 30)
        _subway_info = _infra.get('지하철', '')
        _has_subway = '지하철' in _subway_info or '역세권' in _subway_info or _subway_info.endswith('역')
        if _has_subway or _bus_count >= 35:
            _access_desc = f"{comm.get('spending_grade', '')} 지역등급 기준 대중교통망 우수 추정(버스정류장 약 {_bus_count}개소 수준)"
        elif _bus_count >= 20:
            _access_desc = f"{comm.get('spending_grade', '')} 지역등급 기준 표준 수준 교통망 추정(버스정류장 약 {_bus_count}개소 수준)"
        elif _bus_count >= 10:
            _access_desc = f"{comm.get('spending_grade', '')} 지역등급 기준 교통망 다소 협소 추정(버스정류장 약 {_bus_count}개소 수준)"
        else:
            _access_desc = f"{comm.get('spending_grade', '')} 지역등급 기준 대중교통 접근성 열위 추정(버스정류장 약 {_bus_count}개소 수준)"
        _access_desc += " / 실제 건물 주차면·지하철 도보거리는 '현장 실측' 필요"

        # 공간 적합성 지표: 실제 채점에 사용된 타석당 평수 구간을 그대로 근거 문구에 반영
        _pyeong_per_room = site['area_pyeong'] / max(1, site['rooms'])
        if _pyeong_per_room >= 12.0:
            _space_desc = f"타석당 {_pyeong_per_room:.1f}평, 여유로운 플래그십 규모"
        elif _pyeong_per_room >= 10.0:
            _space_desc = f"타석당 {_pyeong_per_room:.1f}평, 표준 배치 규모"
        elif _pyeong_per_room >= 8.0:
            _space_desc = f"타석당 {_pyeong_per_room:.1f}평, 다소 협소한 배치"
        else:
            _space_desc = f"타석당 {_pyeong_per_room:.1f}평, 초협소 배치로 별도 검토 필요"
        _space_desc += " / 유효 층고 2.8m 이상은 현장 실측 필수"

        indicators = [
            ("시니어 인구 밀집도", score['scores']['senior_population'], 25, f"{pop_source_tag}: {'구 전체' if is_district_wide else '반경 3km 내'} 50대 이상 {demo['senior_50_plus']:,}명({demo['senior_ratio']}%) / 본 매장 운영에 필요한 단골 약 {score.get('senior_customers_needed', 1200):,}명은 배후 시니어의 {score.get('senior_penetration', 0)}% 수준", not demo.get('is_estimated', False)),
            ("접근성 및 주차 인프라", score['scores']['accessibility_parking'], 25, _access_desc + " (※ 건물 자체 주차·엘리베이터 아닌 상권 대중교통 통계 기준)", False),
            ("공간 적합성 및 층고", score['scores']['space_efficiency'], 15, _space_desc if score.get('space_is_verified', True) else "룸/평수 미입력으로 표준값 대신 중립 점수 적용 (현장 실측 시 정밀 산정)", score.get('space_is_verified', True)),
            ("경쟁 매장 여유도", score['scores']['supply_gap'], 15, f"{comm.get('competitor_summary', '반경 3km 내 대형 플래그십 매장 공급 부족')}", score.get('gap_is_verified', False)),
            ("지역 소비력 및 여가지출", score['scores']['commercial_spending'], 20, f"MYPARK 지역등급(4단계 분류) 추정치: 골프용품 성장 +{comm['growth_rate']}% 및 스크린골프 상위 20% 월 {comm['top_20_sales']//10000:,}만원 상권 (동일 등급 지역은 동일 수치 적용, 개별 카드매출 실측 아님)", False),
        ]

        # ===== 렛저 스타일 레이아웃: 좌측 반전 히어로 셀(종합 등급) + 우측 5대 지표 막대 목록 =====
        content_top = 500
        content_bottom = 48
        summary_strip_h = 56
        bars_top = content_top
        bars_bottom = content_bottom + summary_strip_h + 8

        hero_x, hero_w = 40, 220
        bars_x = hero_x + hero_w + 20
        bars_right = self.width - 40
        bars_w = bars_right - bars_x

        # 히어로 셀 (반전 배경: 종합 등급)
        c.setFillColor(self.c_mck_navy)
        c.rect(hero_x, bars_bottom, hero_w, bars_top - bars_bottom, fill=1, stroke=0)
        c.setFillColor(self.c_white)
        c.setFont(FONT_BOLD, 9)
        c.drawCentredString(hero_x + hero_w/2, bars_top - 34, "종합 입지 판정")
        c.setFont(FONT_BOLD, 60)
        c.drawCentredString(hero_x + hero_w/2, bars_top - 108, score['grade'])
        c.setFont(FONT_BOLD, 13)
        c.drawCentredString(hero_x + hero_w/2, bars_top - 130, f"{score['total_score']}점 / 100점")
        c.setStrokeColor(self.c_mck_teal)
        c.setLineWidth(1.2)
        c.line(hero_x + 28, bars_top - 146, hero_x + hero_w - 28, bars_top - 146)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_teal)
        desc_lines_hero = self._wrap_text_to_width(c, score['grade_desc'], FONT_BOLD, 10.5, hero_w - 32, max_lines=2)
        hy = bars_top - 168
        for hl in desc_lines_hero:
            c.drawCentredString(hero_x + hero_w/2, hy, hl)
            hy -= 15

        # 우측: 5대 지표를 렛저 스타일 막대 목록으로 표시 (레이더 차트 대신 실제 점수 구간을 그대로 시각화)
        row_h = (bars_top - bars_bottom) / len(indicators)
        for i, (iname, iscore, imax, idesc, iverified) in enumerate(indicators):
            row_top = bars_top - i * row_h
            row_bottom = row_top - row_h
            if i > 0:
                c.setStrokeColor(self.c_line)
                c.setLineWidth(0.5)
                c.line(bars_x, row_top, bars_right, row_top)

            bar_color = self.c_mck_teal if iverified else HexColor('#9AA5B1')
            badge_text = "실측·확인" if iverified else "추정·정밀분석 권장"

            c.setFont(FONT_BOLD, 10.5)
            c.setFillColor(self.c_mck_navy)
            c.drawString(bars_x, row_top - 18, iname)
            badge_w = c.stringWidth(badge_text, FONT_BOLD, 7) + 10
            badge_x = bars_x + c.stringWidth(iname, FONT_BOLD, 10.5) + 10
            c.setFillColor(bar_color)
            c.roundRect(badge_x, row_top - 24, badge_w, 12, 2, fill=1, stroke=0)
            c.setFont(FONT_BOLD, 7)
            c.setFillColor(self.c_white)
            c.drawCentredString(badge_x + badge_w / 2, row_top - 20.5, badge_text)
            c.setFont(FONT_BOLD, 10.5)
            c.setFillColor(bar_color)
            c.drawRightString(bars_right, row_top - 18, f"{iscore}점 / {imax}점")

            track_y = row_top - 30
            track_h = 7
            c.setFillColor(self.c_line)
            c.roundRect(bars_x, track_y - track_h, bars_w, track_h, 2, fill=1, stroke=0)
            fill_w = max(6, bars_w * (iscore / imax))
            c.setFillColor(bar_color)
            c.roundRect(bars_x, track_y - track_h, fill_w, track_h, 2, fill=1, stroke=0)

            c.setFont(FONT_REGULAR, 8)
            c.setFillColor(self.c_slate)
            desc_lines = self._wrap_text_to_width(c, f"· 산출 근거: {idesc}", FONT_REGULAR, 8, bars_w, max_lines=2)
            dy = track_y - track_h - 13
            for dl in desc_lines:
                c.drawString(bars_x, dy, dl)
                dy -= 10

        # 하단 요약 스트립 (전체 폭)
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, content_bottom, bars_right - 40, summary_strip_h, fill=1, stroke=1)
        grade_summary_text = {
            'S': "본 사업지는 50~70대 풍부한 시니어 거주 인구와 우수한 교통/접근성을 갖추어, 평일 주간 정기 예약 및 동호회 리그 중심의 높은 가동률 창출에 최적화된 입지입니다.",
            'A': "본 사업지는 시니어 배후 수요와 접근성 등 핵심 조건을 대체로 충족하여, 평일 주간 정기 예약 중심의 안정적 가동률을 기대할 수 있는 입지입니다.",
            'B': "본 사업지는 일부 지표에서 표준 기준을 충족하나 상대적으로 낮은 지표도 있어, 아래 세부 근거를 현장 실측과 함께 신중히 검토하시기를 권장합니다.",
            'C': "본 사업지는 5대 지표 중 다수가 표준 기준에 미달하여, 출점 전 배후 수요·경쟁 환경에 대한 현장 재확인이 반드시 필요합니다.",
        }
        summary_text = grade_summary_text.get(score['grade'], grade_summary_text['B'])
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        summary_lines = self._wrap_text_to_width(c, summary_text, FONT_REGULAR, 8.5, bars_right - 40 - 32, max_lines=2)
        gy = content_bottom + summary_strip_h - 16
        for gl in summary_lines:
            c.drawString(56, gy, gl)
            gy -= 12
        c.setFillColor(self.c_slate)
        c.drawString(56, content_bottom + 6, "위 5개 지표의 상세 근거는 앞선 1~5장(인구·상권·업종·경쟁·사업지 개요)을 참조하십시오.")

        self._draw_footer(c, f"MYPARK 5-Dimension Diamond Scoring Methodology ({score['total_score']}점 {score['grade']}등급)")
        c.showPage()


        # ---------------------------------------------------------------------
        # Page 8: [신규] 7. 표준 투자 조건 및 사업 추진 유의사항
        # [PART 2 신설: 이 보고서에서 재무 금액이 최초로 등장하는 지점 & Caveat 명시]
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "7. 표준 투자 조건 및 사업 추진 유의사항", f"{site['rooms']}타석 {site['area_pyeong']}평 표준 모델 기준 및 투자 결정 전 필수 점검사항")
        
        # 블록 A (좌측): 표준 투자 조건 (전제조건 명시)
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 425, 452, fill=1, stroke=1)

        c.setFillColor(self.c_mck_navy)
        c.rect(40, 458, 425, 42, fill=1, stroke=0)
        c.setFillColor(self.c_white)
        c.setFont(FONT_BOLD, 11)
        c.drawString(56, 476, f"■ {site['rooms']}타석 {site['area_pyeong']}평 표준 모델 투자 조건 (SSOT)")

        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 436, "● 초기 투자금 상세 내역")

        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 414, f"• 시뮬레이터 장비: {site['rooms']}대 × 대당 {DEFAULT_SETTINGS['simulator_unit_price']//10000:,}만원 = {fmt_won_full(inv['simulator_cost'])}")
        c.drawString(56, 394, f"• 인테리어 공사비: {site['area_pyeong']}평 × 평당 {DEFAULT_SETTINGS['interior_cost_per_pyeong']//10000:,}만원 = {fmt_won_full(inv['interior_cost'])}")
        c.drawString(56, 374, f"• 부대설비 (간판/가구/초도용품): {fmt_won_full(inv['other_facilities'])}")
        c.drawString(70, 356, f"- 간판({DEFAULT_SETTINGS['signage_cost']//10000:,}만) / 가구({DEFAULT_SETTINGS['furniture_cost']//10000:,}만) / 초도용품({DEFAULT_SETTINGS['supplies_cost']//10000:,}만)")
        c.drawString(56, 338, f"• 냉난방 설비 (선택): 기존 상가 설비 승계 시 추가 비용 없음, 신규 설치 시 약 {inv['hvac_cost_optional']//10000:,}만원 별도")

        c.setFillColor(self.c_tint_blue)
        c.rect(56, 276, 393, 40, fill=1, stroke=0)
        c.setFillColor(self.c_mck_navy)
        c.setFont(FONT_BOLD, 12)
        c.drawString(70, 292, f"★ 총 초기 투자금: {fmt_won_full(inv['total_capex'])} ({fmt_eok(inv['total_capex'])})")

        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 252, "● 표준 운영 방식 및 인건비 모델")
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 230, f"• 표준 모델 (점주 {site['staff_count']}인 상주 운영): 인건비 월 {site['staff_count']*DEFAULT_SETTINGS['labor_cost_manager']//10000:,}만원 (운영 형태별 조정 가능한 대표값)")
        c.drawString(56, 210, f"• 비교 모델 (직원 3인 채용 운영): 인건비 월 {3*DEFAULT_SETTINGS['labor_cost_manager']//10000:,}만원 (회수기간 {fin['owner_operated']['staff3_payback_months']:.1f}개월)")
        c.drawString(56, 190, f"• 게임비 요금: 1인 18홀 7,000원 (4인 1팀 28,000원)")
        c.drawString(56, 170, f"• 3대 매출원: 게임비 회전 + 용품 판매(월 {scenarios['moderate']['goods_revenue']//10000:,}만) + 식음료(월 {scenarios['moderate']['beverage_revenue']//10000:,}만)")
        rent_tag = "입력하신 실측" if not site.get('rent_is_estimated') else "지역 시세 추정"
        c.drawString(56, 150, f"• 월 임대료 기준(임차인): {rent_tag} {site['monthly_rent']//10000:,}만원/월 반영")
        _owner_s = FinanceEngine.calculate_monthly_scenario(site['rooms'], 0, site['staff_count'], 'moderate')
        _owner_pb = inv['total_capex'] / _owner_s['operating_profit'] if _owner_s['operating_profit'] > 0 else 0
        c.drawString(56, 130, f"• 건물주(자가 소유) 시 참고: 임대료 없이 운영 시 보편적 시나리오 회수기간 약 {_owner_pb:.1f}개월")

        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_slate)
        c.drawString(56, 96, "※ 레슨, 락커비, 홀인원펀드 등 근거 없는 부가 항목은 전액 배제되었습니다.")

        # 블록 B (우측): 투자 결정 전 유의사항 (Caveat)
        rb_right = 495 + right_col_w
        rb_text_w = rb_right - 16 - 511
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, 48, right_col_w, 452, fill=1, stroke=1)

        c.setFillColor(self.c_mck_navy)
        c.rect(495, 458, right_col_w, 42, fill=1, stroke=0)
        c.setFillColor(self.c_white)
        c.setFont(FONT_BOLD, 10.5)
        hdr_lines = self._wrap_text_to_width(c, "참고사항 (사업 검토 시 확인해 주십시오)", FONT_BOLD, 10.5, rb_text_w, max_lines=2)
        hy = 482 if len(hdr_lines) > 1 else 476
        for hl in hdr_lines:
            c.drawString(511, hy, hl)
            hy -= 13

        def draw_wrapped_bullets(start_y, bullets):
            yy = start_y
            for b in bullets:
                b_text, b_max_lines = b if isinstance(b, tuple) else (b, 2)
                lines_b = self._wrap_text_to_width(c, b_text, FONT_REGULAR, 8.5, rb_text_w, max_lines=b_max_lines)
                for bl in lines_b:
                    c.drawString(511, yy, bl)
                    yy -= 13
                yy -= 2
            return yy

        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, 436, "● 현장 실측 및 인허가 유의사항")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        y_after = draw_wrapped_bullets(414, [
            "• 위 수치는 표준 모델 기준 추정치이며, 실제 임대료·공사비는 현장 견적에 따라 달라질 수 있습니다.",
            "• 건물 내 보/배관 간섭 및 유효 층고(2.8m 이상 확보) 여부를 사전 실측하십시오.",
            f"• {site['rooms']}타석 동시 가동에 필요한 전기 인입 용량({max(25, site['rooms']*3)}kW 이상)을 확인하십시오.",
        ])

        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, y_after - 8, "● 인건비 및 운영 방식 유의사항")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        y_after2 = draw_wrapped_bullets(y_after - 30, [
            "• 매니저/직원을 채용해 전면 위탁 운영할 경우 인건비 증가(월 500~750만)로 손익분기점이 상승하고 투자금 회수기간이 연장됩니다.",
            "• 인테리어 및 시뮬레이터 단가는 본 계약 시점의 공식 견적을 확인하십시오.",
        ])

        _comp_summary8 = comm.get('competitor_summary', '')
        if '예시 시나리오' in _comp_summary8:
            _methodology_txt = "본 보고서는 KOSIS 인구통계, MYPARK 지역등급 추정 모델, 표준 재무 모델에 기반한 추정 분석 자료입니다."
        else:
            _methodology_txt = "본 보고서는 인구통계, 실측 경쟁사 데이터, MYPARK 지역등급 추정 모델, 표준 재무 모델을 결합한 종합분석자료입니다."

        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, y_after2 - 8, "● 분석 방법론 및 활용 안내")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_slate)
        draw_wrapped_bullets(y_after2 - 30, [
            f"• {_methodology_txt}",
            "• 마이파크 사업부서 전문가와의 상담을 권장하며, 특정 수익률을 보장하지 않습니다.",
        ])

        alert_h = 54
        c.setFillColor(self.c_tint_blue)
        c.setStrokeColor(self.c_line)
        c.rect(511, 60, rb_right - 16 - 511, alert_h, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 8.5)
        c.setFillColor(self.c_mck_navy)
        alert_lines = self._wrap_text_to_width(c, "참고: 9~12장의 모든 매출·손익·BEP 추정치는 위 표준 모델을 전제로 산출되었습니다.", FONT_BOLD, 8.5, rb_text_w - 14, max_lines=2)
        ay = 60 + alert_h - 16
        for al in alert_lines:
            c.drawString(525, ay, al)
            ay -= 12
        c.setFont(FONT_REGULAR, 7.5)
        c.drawString(525, ay - 4, f"(기준: {site['rooms']}타석 {site['area_pyeong']}평 / 총투자금 {fmt_eok(inv['total_capex'])} / 점주 {site['staff_count']}인 상주 운영 모델)")

        self._draw_footer(c, "MYPARK Standard Investment Criteria & Reference Notes")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 9: 8. 사업 타당성 분석 - 매출 추정 (3대 시나리오)
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "8. 사업 타당성 분석 - 매출 추정 (3대 시나리오)", f"보수적(일 {scenarios['conservative']['daily_turns_per_room']}회전) {scenarios['conservative']['total_revenue']//10000:,}만원 ~ 보편적(일 {scenarios['moderate']['daily_turns_per_room']}회전) {scenarios['moderate']['total_revenue']//10000:,}만원 ~ 긍정적(일 {scenarios['optimistic']['daily_turns_per_room']}회전) {scenarios['optimistic']['total_revenue']//10000:,}만원")

        full_box_w = (self.width - 40) - 40
        tbl_bottom9, tbl_top9 = 260, 500
        head_h9 = 30
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, tbl_bottom9, full_box_w, tbl_top9 - tbl_bottom9, fill=1, stroke=1)
        c.setFillColor(self.c_mck_navy)
        c.rect(40, tbl_top9 - head_h9, full_box_w, head_h9, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_white)
        c.drawString(56, tbl_top9 - 20, "시나리오별 매출 구조 상세")

        headers = ["구분 / 시나리오", "일 가동률 (타석당)", "월 게임비 매출", "용품 판매 매출", "식음료 등 기타", "월 총매출액", "연간 총매출액"]
        x_offsets = [48, 155, 270, 380, 480, 580, 690]
        col_y9 = tbl_top9 - head_h9 - 22
        c.setFont(FONT_BOLD, 8.5)
        c.setFillColor(self.c_slate)
        for h, x in zip(headers, x_offsets):
            c.drawString(x, col_y9, h)
        c.setStrokeColor(self.c_line)
        c.line(48, col_y9 - 8, 40 + full_box_w - 16, col_y9 - 8)

        sc_data = [
            ("보수적 (초기/비수기)", f"1일 {scenarios['conservative']['daily_turns_per_room']}회전 ({scenarios['conservative']['daily_users']}명)", f"{scenarios['conservative']['room_revenue']//10000:,}만원", f"{scenarios['conservative']['goods_revenue']//10000:,}만원", f"{scenarios['conservative']['beverage_revenue']//10000:,}만원", f"{scenarios['conservative']['total_revenue']//10000:,}만원", f"{scenarios['conservative']['annual_revenue']//100000000:.1f}억원"),
            ("보편적 (정기예약 정착)", f"1일 {scenarios['moderate']['daily_turns_per_room']}회전 ({scenarios['moderate']['daily_users']}명)", f"{scenarios['moderate']['room_revenue']//10000:,}만원", f"{scenarios['moderate']['goods_revenue']//10000:,}만원", f"{scenarios['moderate']['beverage_revenue']//10000:,}만원", f"{scenarios['moderate']['total_revenue']//10000:,}만원", f"{scenarios['moderate']['annual_revenue']//100000000:.1f}억원"),
            ("긍정적 (주간/주말 풀가동)", f"1일 {scenarios['optimistic']['daily_turns_per_room']}회전 ({scenarios['optimistic']['daily_users']}명)", f"{scenarios['optimistic']['room_revenue']//10000:,}만원", f"{scenarios['optimistic']['goods_revenue']//10000:,}만원", f"{scenarios['optimistic']['beverage_revenue']//10000:,}만원", f"{scenarios['optimistic']['total_revenue']//10000:,}만원", f"{scenarios['optimistic']['annual_revenue']//100000000:.1f}억원"),
        ]
        row_h9 = (col_y9 - 8 - (tbl_bottom9 + 12)) / len(sc_data)
        y_s = col_y9 - 8 - row_h9 + 18
        for ridx, (sname, rturn, rrev, grev, brev, tot, ann) in enumerate(sc_data):
            is_mod = "보편적" in sname
            if is_mod:
                c.setFillColor(self.c_tint_blue)
            elif ridx % 2 == 1:
                c.setFillColor(self.c_box_bg)
            else:
                c.setFillColor(self.c_paper)
            c.rect(41, y_s - row_h9 + 15, full_box_w - 2, row_h9, fill=1, stroke=0)
            c.setFont(FONT_BOLD if is_mod else FONT_REGULAR, 8.5)
            c.setFillColor(self.c_mck_navy if is_mod else self.c_charcoal)
            c.drawString(48, y_s, sname)
            c.drawString(155, y_s, rturn)
            c.drawString(270, y_s, rrev)
            c.drawString(380, y_s, grev)
            c.drawString(480, y_s, brev)
            c.setFillColor(self.c_mck_teal if is_mod else self.c_charcoal)
            c.drawString(580, y_s, tot)
            c.drawString(690, y_s, ann)
            y_s -= row_h9

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, full_box_w, 196, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 222, "■ 매출 추정 산출 기준")

        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 194, "• 게임비 단가: 1인 18홀 7,000원 (4인 1팀 1게임당 28,000원)")
        c.drawString(56, 168, f"• {site['rooms']}타석 회전 기준: 타석당 1일 {scenarios['moderate']['daily_turns_per_room']}게임 가동 시 1일 {scenarios['moderate']['daily_users']}명 이용 (보편 시나리오 월 게임비 {scenarios['moderate']['room_revenue']//10000:,}만원)")
        c.drawString(56, 142, f"• 부가 매출 2종: 파크골프 클럽/공/장갑 등 용품 판매(월 {scenarios['moderate']['goods_revenue']//10000:,}만원) + 음료/간식(월 {scenarios['moderate']['beverage_revenue']//10000:,}만원)")
        c.drawString(56, 116, "• 투명성 원칙: 레슨비, 락커룸 렌탈료 등 근거 없는 부가 항목을 일체 배제한 보수적이고 정직한 추정치")

        self._draw_footer(c, "MYPARK Standard Financial Model (120 Pyeong, 10 Rooms)")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 10: 9. 사업 타당성 분석 - 비용 구조 및 순영업이익
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "9. 사업 타당성 분석 - 비용 구조 및 순영업이익", f"월 고정비 {fin['owner_operated']['fixed_cost']//10000:,}만원(임대료 {site['monthly_rent']//10000:,}만+인건비 250만+운영비) 및 보편 월 순영업이익 {scenarios['moderate']['operating_profit']//10000:,}만원")

        chart_bottom10, chart_top10 = 260, 500
        chart_h10 = chart_top10 - chart_bottom10
        if 'waterfall_cost' in charts and os.path.exists(charts['waterfall_cost']):
            c.drawImage(charts['waterfall_cost'], 40, chart_bottom10, width=440, height=chart_h10, preserveAspectRatio=True, anchor='n')

        head_h10 = 28
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, chart_bottom10, right_col_w, chart_h10, fill=1, stroke=1)
        c.setFillColor(self.c_mck_navy)
        c.rect(495, chart_top10 - head_h10, right_col_w, head_h10, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_white)
        c.drawString(511, chart_top10 - 19, "월간 비용 구조 상세 (보편 시나리오 기준)")

        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        ry10 = chart_top10 - head_h10 - 22
        rent_basis = "입력하신 임대료" if not site.get('rent_is_estimated') else "지역 시세 추정 임대료"
        c.drawString(511, ry10, f"• 월 임대료: {site['monthly_rent']//10000:,}만원 ({rent_basis})")
        ry10 -= 20
        c.drawString(511, ry10, f"• 인건비 (점주 직접운영): {scenarios['moderate']['labor_cost']//10000:,}만원 ({site['staff_count']}인 상주 운영)")
        ry10 -= 20
        c.drawString(511, ry10, f"• 매장 운영비/소모품: {DEFAULT_SETTINGS['store_ops_monthly']//10000:,}만원  |  통신/POS: {DEFAULT_SETTINGS['pos_telecom_monthly']//10000:,}만원  |  마케팅비: {DEFAULT_SETTINGS['marketing_monthly']//10000:,}만원")
        ry10 -= 20
        c.drawString(511, ry10, f"• 변동비 (매출연동): 매출원가 {(scenarios['moderate']['cost_goods']+scenarios['moderate']['cost_beverage'])//10000:,}만원 + 카드수수료({DEFAULT_SETTINGS['card_fee_rate']*100:.1f}%) {scenarios['moderate']['card_fee']//10000:,}만원")
        ry10 -= 24
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(511, ry10, f"★ 월 총지출 합계: {scenarios['moderate']['total_cost']//10000:,}만원")

        ry10 -= 40
        c.setFillColor(self.c_tint_blue)
        c.rect(505, ry10 - 12, right_col_w - 10, 34, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 11)
        c.setFillColor(self.c_mck_teal)
        c.drawString(515, ry10, f"★ 월 순영업이익: {scenarios['moderate']['operating_profit']//10000:,}만원 (영업이익률 {scenarios['moderate']['profit_margin']}%)")

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, full_box_w, 196, fill=1, stroke=1)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(56, 222, "■ 운영 모델별 순영업이익 비교")

        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(self.c_charcoal)
        c.drawString(56, 194, f"• 점주 직접 운영 모델 (표준): 월 순영업이익 {scenarios['moderate']['operating_profit']//10000:,}만원 (연간 {scenarios['moderate']['operating_profit']*12//10000:,}만원 / 이익률 {scenarios['moderate']['profit_margin']}%)")
        c.drawString(56, 168, f"• 직원 채용 모델 (매니저 1인 + 알바 2인): 월 순영업이익 {fin['owner_operated']['staff3_operating_profit']//10000:,}만원 (연간 {fin['owner_operated']['staff3_operating_profit']*12//10000:,}만원)")
        c.drawString(56, 142, "• 낮은 변동비 구조: 일반 음식점/카페와 달리 원재료비 비중이 극히 낮아 매출 증가 시 순이익이 급격히 증가하는 고마진 레버리지")
        c.drawString(56, 116, "• 고정비 방어력: 월 고정비가 낮아 비수기나 상권 초기 단계에서도 안정적 순영업이익 기반 유지")

        self._draw_footer(c, "MYPARK Cost Structure & Operating Profit Analysis")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 11: 10. 손익분기점(BEP) 및 투자금 회수기간
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "10. 손익분기점(BEP) 및 투자금 회수기간", f"손익분기 매출 월 {inv['bep_monthly_sales']//10000:,}만원 (타석당 일 {inv['bep_turns_per_room']}회전) 및 투자금 {fmt_eok(inv['total_capex'])} 회수기간 약 {inv['payback_months_moderate']:.1f}개월")

        chart_bottom11, chart_top11 = 260, 500
        chart_h11 = chart_top11 - chart_bottom11
        if 'bep_chart' in charts and os.path.exists(charts['bep_chart']):
            c.drawImage(charts['bep_chart'], 40, chart_bottom11, width=440, height=chart_h11, preserveAspectRatio=True, anchor='n')

        head_h11 = 28
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(495, chart_bottom11, right_col_w, chart_h11, fill=1, stroke=1)
        c.setFillColor(self.c_mck_navy)
        c.rect(495, chart_top11 - head_h11, right_col_w, head_h11, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_white)
        c.drawString(511, chart_top11 - 19, f"투자금 {fmt_eok(inv['total_capex'])} 회수 시뮬레이션")

        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        ry11 = chart_top11 - head_h11 - 22
        if inv.get('conservative_viable', True):
            c.drawString(511, ry11, f"• 보수적 시나리오: 월 순익 {scenarios['conservative']['operating_profit']//10000:,}만원 -> 회수기간 약 {inv['payback_months_conservative']:.1f}개월")
            ry11 -= 20
        else:
            con_lines = self._wrap_text_to_width(c, "보수적 시나리오(3회전)는 추가 매출 확보 전략이 필요한 구간이며, 최소 4회전 이상 가동 시 안정적 순익 구조로 전환됩니다", FONT_REGULAR, 8.5, right_col_w - 16, max_lines=2)
            for cl in con_lines:
                c.drawString(511, ry11, f"• {cl}" if cl == con_lines[0] else f"  {cl}")
                ry11 -= 13
            ry11 -= 7
        c.drawString(511, ry11, f"• 보편적 시나리오: 월 순익 {scenarios['moderate']['operating_profit']//10000:,}만원 -> 회수기간 약 {inv['payback_months_moderate']:.1f}개월 ({fmt_months(inv['payback_months_moderate'])})")
        ry11 -= 20
        c.drawString(511, ry11, f"• 긍정적 시나리오: 월 순익 {scenarios['optimistic']['operating_profit']//10000:,}만원 -> 회수기간 약 {inv['payback_months_optimistic']:.1f}개월")
        ry11 -= 34

        c.setFillColor(self.c_tint_blue)
        c.rect(505, ry11 - 34, right_col_w - 10, 56, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(self.c_mck_navy)
        c.drawString(515, ry11, f"★ BEP 달성 요건: 타석당 하루 {inv['bep_turns_per_room']}회전 (1일 {inv['bep_daily_users']}명 이용)")
        c.drawString(515, ry11 - 20, f"★ 일 평균 {inv['bep_daily_users']}명 방문 시 월 고정비 전액 커버 (보편 시나리오의 {inv['bep_daily_users']/max(1,scenarios['moderate']['daily_users'])*100:.0f}% 수준)")

        # 하단: 회수기간을 실제로 움직이는 레버를 정량 비교한다.
        # (회수기간이 길게 나오는 사업지에서 '무엇을 바꾸면 얼마나 개선되는지'를
        #  숫자로 제시. 각 수치는 동일 재무엔진으로 재계산한 실제 값이다.)
        # 보수적 시나리오가 적자(고임대료 상권)면 회수기간 레버 계산 자체가 무의미
        # 하므로, 그 경우엔 보편적 시나리오를 기준선으로 전환해 레버표를 계산한다.
        _lv_use_moderate = not inv.get('conservative_viable', True)
        _lv_base_label = "보편적" if _lv_use_moderate else "보수적"
        _lv_base_op = scenarios['moderate']['operating_profit'] if _lv_use_moderate else scenarios['conservative']['operating_profit']
        _lv_capex = inv['total_capex']
        _lv_base_pb = (_lv_capex / _lv_base_op) if _lv_base_op > 0 else 0
        _lv_turn_op = scenarios['optimistic']['operating_profit'] if _lv_use_moderate else scenarios['moderate']['operating_profit']
        _lv_turn_pb = (_lv_capex / _lv_turn_op) if _lv_turn_op > 0 else 0
        _lv_turn_label = "4회전 → 5회전" if _lv_use_moderate else "3회전 → 4회전"
        _lv_rent_op = _lv_base_op + 1000000
        _lv_rent_pb = (_lv_capex / _lv_rent_op) if _lv_rent_op > 0 else 0
        _lv_int_capex = _lv_capex - int(site['area_pyeong'] * 300000)
        _lv_int_pb = (_lv_int_capex / _lv_base_op) if _lv_base_op > 0 else 0

        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, self.width - 80, 196, fill=1, stroke=1)
        c.setFillColor(self.c_mck_navy)
        c.rect(40, 216, self.width - 80, 28, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_white)
        c.drawString(56, 225, f"■ 투자금 회수기간 단축 레버 ({_lv_base_label} 시나리오 기준 민감도 분석)")

        _lv_rows = [
            (f"가동률 상향 ({_lv_turn_label})", f"{_lv_base_pb:.1f}개월", f"{_lv_turn_pb:.1f}개월", f"-{_lv_base_pb - _lv_turn_pb:.1f}개월", "본사 오픈 초기 홍보·커뮤니티 형성 지원 + 동호회 정기예약 유치가 가장 강력한 레버"),
            ("인테리어 단가 조정 (평당 -30만원)", f"{_lv_base_pb:.1f}개월", f"{_lv_int_pb:.1f}개월", f"-{_lv_base_pb - _lv_int_pb:.1f}개월", "기존 상가 시설 승계·부분 시공으로 초기 투자비 절감"),
            ("임대료 협상 (월 -100만원)", f"{_lv_base_pb:.1f}개월", f"{_lv_rent_pb:.1f}개월", f"-{_lv_base_pb - _lv_rent_pb:.1f}개월", "장기계약·렌트프리 조건 협상 시 매월 순익에 직접 반영"),
        ]
        _lv_cols = [56, 268, 344, 424, 512]
        c.setFont(FONT_BOLD, 8.5)
        c.setFillColor(self.c_slate)
        for _t, _x in zip(["개선 레버", "현재", "개선 후", "단축폭", "실행 방법"], _lv_cols):
            c.drawString(_x, 198, _t)
        _lv_y = 176
        for _i, (_nm, _cur, _aft, _gap, _how) in enumerate(_lv_rows):
            if _i % 2 == 0:
                c.setFillColor(self.c_paper)
                c.rect(48, _lv_y - 10, self.width - 96, 30, fill=1, stroke=0)
            c.setFont(FONT_BOLD, 9)
            c.setFillColor(self.c_mck_navy)
            c.drawString(_lv_cols[0], _lv_y, _nm)
            c.setFont(FONT_REGULAR, 9)
            c.setFillColor(self.c_slate)
            c.drawString(_lv_cols[1], _lv_y, _cur)
            c.setFont(FONT_BOLD, 9)
            c.setFillColor(self.c_mck_teal)
            c.drawString(_lv_cols[2], _lv_y, _aft)
            c.drawString(_lv_cols[3], _lv_y, _gap)
            c.setFont(FONT_REGULAR, 8.5)
            c.setFillColor(self.c_charcoal)
            c.drawString(_lv_cols[4], _lv_y, _how)
            _lv_y -= 30

        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_slate)
        c.drawString(56, 62, f"※ 타석 수를 줄이면 투자비는 낮아지나 인건비·관리비 등 고정비는 그대로 남아 회수기간이 오히려 길어집니다. 본 {site['rooms']}타석 모델이 고정비 분산 측면에서 유리한 구조입니다.")

        self._draw_footer(c, "MYPARK BEP & Capital Payback Period Analysis")
        c.showPage()

        # ---------------------------------------------------------------------
        # Page 12: 11. 5개년 중장기 손익 전망 및 종합 제언
        # ---------------------------------------------------------------------
        self._draw_mckinsey_header(c, "11. 5개년 중장기 손익 전망 및 종합 제언", f"5개년 누적 매출 {fin['five_year']['total_5yr_revenue']//100000000:.1f}억원, 누적 순영업이익 {fin['five_year']['total_5yr_profit']//100000000:.1f}억원 달성 전망")

        tbl_bottom12, tbl_top12 = 260, 500
        head_h12 = 30
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, tbl_bottom12, full_box_w, tbl_top12 - tbl_bottom12, fill=1, stroke=1)
        c.setFillColor(self.c_mck_navy)
        c.rect(40, tbl_top12 - head_h12, full_box_w, head_h12, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(self.c_white)
        c.drawString(56, tbl_top12 - 20, "5개년 손익 전망 요약")

        headers_5y = ["연차", "1차년도 (안정화)", "2차년도 (성장기)", "3차년도 (성숙기)", "4차년도 (유지기)", "5차년도 (성숙유지)", "5개년 누적 합계"]
        x_5y = [48, 145, 240, 335, 430, 525, 625]
        col_y12 = tbl_top12 - head_h12 - 22
        c.setFont(FONT_BOLD, 8.5)
        c.setFillColor(self.c_slate)
        for h, x in zip(headers_5y, x_5y):
            c.drawString(x, col_y12, h)
        c.setStrokeColor(self.c_line)
        c.line(48, col_y12 - 8, 40 + full_box_w - 16, col_y12 - 8)

        rows_5y = [
            ("연간 총매출액", [f"{y['revenue']/100000000:.2f}억원" for y in fin['five_year']['years']], f"{fin['five_year']['total_5yr_revenue']//100000000:.1f}억원"),
            ("연간 총비용", [f"{y['cost']/100000000:.2f}억원" for y in fin['five_year']['years']], f"{fin['five_year']['total_5yr_cost']//100000000:.1f}억원"),
            ("연간 순영업익", [f"{y['profit']/100000000:.2f}억원" for y in fin['five_year']['years']], f"{fin['five_year']['total_5yr_profit']//100000000:.1f}억원"),
            ("투자금 누적회수", [f"{fmt_eok(inv['total_capex'])} 회수완료" if fin['five_year']['years'][i]['cumulative_profit'] >= inv['total_capex'] else f"{fin['five_year']['years'][i]['cumulative_profit']/100000000:.2f}억원" for i in range(5)], f"회수율 {fin['five_year']['total_5yr_profit']/inv['total_capex']*100:.0f}%"),
        ]
        row_h12 = (col_y12 - 8 - (tbl_bottom12 + 12)) / len(rows_5y)
        y_5 = col_y12 - 8 - row_h12 + 18
        for ridx, (rname, yvals, totval) in enumerate(rows_5y):
            is_prof = "순영업익" in rname
            if is_prof:
                c.setFillColor(self.c_tint_blue)
            elif ridx % 2 == 1:
                c.setFillColor(self.c_box_bg)
            else:
                c.setFillColor(self.c_paper)
            c.rect(41, y_5 - row_h12 + 15, full_box_w - 2, row_h12, fill=1, stroke=0)
            c.setFont(FONT_BOLD if is_prof else FONT_REGULAR, 8.5)
            c.setFillColor(self.c_mck_teal if is_prof else self.c_charcoal)
            c.drawString(48, y_5, rname)
            for idx, yv in enumerate(yvals):
                c.drawString(x_5y[idx+1], y_5, yv)
            c.setFont(FONT_BOLD, 8.5)
            c.drawString(x_5y[-1], y_5, totval)
            y_5 -= row_h12

        # 하단 2개 박스 (가맹점주 기대효과 vs 건물주 상생 효과)
        head_h12b = 26
        c.setFillColor(self.c_box_bg)
        c.setStrokeColor(self.c_line)
        c.rect(40, 48, 425, 196, fill=1, stroke=1)
        c.setFillColor(self.c_mck_navy)
        c.rect(40, 48 + 196 - head_h12b, 425, head_h12b, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_white)
        c.drawString(56, 48 + 196 - head_h12b + 9, "가맹점주 핵심 경쟁력 및 최종 제언")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        val_f_lines = score['value_franchisee'].split('\n')
        cur_y = 48 + 196 - head_h12b - 16
        for fl in val_f_lines:
            cur_y = self._draw_multiline_text(c, fl, 56, cur_y, max_chars=40, line_height=13, max_lines=4) - 3
        if site.get('special_notes'):
            c.setFont(FONT_BOLD, 8.5)
            c.setFillColor(self.c_mck_teal)
            c.drawString(56, cur_y, f"※ 고객 특이사항 연계: {site['special_notes']}")

        c.setFillColor(self.c_tint_blue)
        c.setStrokeColor(self.c_mck_teal)
        c.rect(495, 48, right_col_w, 196, fill=1, stroke=1)
        c.setFillColor(self.c_mck_teal)
        c.rect(495, 48 + 196 - head_h12b, right_col_w, head_h12b, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(self.c_white)
        c.drawString(511, 48 + 196 - head_h12b + 9, "건물주 및 상가 상생 활성화 효과")
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(self.c_charcoal)
        val_l_lines = score['value_landlord'].split('\n')
        cur_y = 48 + 196 - head_h12b - 16
        for ll in val_l_lines:
            cur_y = self._draw_multiline_text(c, ll, 511, cur_y, max_chars=26, line_height=10.5, max_lines=5, color=self.c_charcoal) - 3

        self._draw_footer(c, "MYPARK 5-Year Financial Forecast & Final Strategic Recommendation")
        c.showPage()

        c.save()
        print(f"[PDF GENERATED 12P] {self.filename}")
        return self.filename
