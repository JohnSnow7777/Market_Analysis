# -*- coding: utf-8 -*-
"""McKinsey Classic Executive Theme 차트 및 상권 지도 생성기"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# -----------------------------------------------------------------------------
# TTF 폰트 등록
# -----------------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
font_pairs = [
    (os.path.join(current_dir, 'fonts', 'IBMPlexSansKR-Regular.ttf'), os.path.join(current_dir, 'fonts', 'IBMPlexSansKR-Bold.ttf')),
    (os.path.join(current_dir, 'fonts', 'MalgunGothic.ttf'), os.path.join(current_dir, 'fonts', 'MalgunGothicBold.ttf')),
    (r'C:\Windows\Fonts\malgun.ttf', r'C:\Windows\Fonts\malgunbd.ttf'),
    (r'C:\Windows\Fonts\NanumGothic.ttf', r'C:\Windows\Fonts\NanumGothicBold.ttf'),
    ('/usr/share/fonts/truetype/nanum/NanumGothic.ttf', '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf'),
]

korean_font_name = None
for regular_path, bold_path in font_pairs:
    if os.path.exists(regular_path):
        try:
            fm.fontManager.addfont(regular_path)
            prop = fm.FontProperties(fname=regular_path)
            korean_font_name = prop.get_name()
            if os.path.exists(bold_path):
                fm.fontManager.addfont(bold_path)
            plt.rcParams['font.family'] = korean_font_name
            plt.rcParams['font.sans-serif'] = [korean_font_name, 'Malgun Gothic', 'DejaVu Sans', 'Arial']
            break
        except Exception:
            pass

if korean_font_name is None:
    print("[FONT WARNING] 한글 폰트를 찾지 못해 matplotlib 기본 폰트로 대체합니다. 차트의 한글이 깨질 수 있습니다.")

plt.rcParams['axes.unicode_minus'] = False


class Visualizer:
    """맥킨지 클래식 이그제큐티브 차트 생성기"""

    @staticmethod
    def generate_sales_trend_chart(commercial_data, output_path):
        months = commercial_data['months']
        selected = commercial_data['selected_area_sales']
        dong = commercial_data['dong_avg_sales']
        city = commercial_data['city_avg_sales']
        
        fig, ax = plt.subplots(figsize=(7.6, 4.4), dpi=200)
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')
        
        ax.plot(months, selected, marker='o', markersize=6, color='#14181F', linewidth=2.5, label='선택영역 (반경 3km)', zorder=4)
        ax.plot(months, dong, marker='s', markersize=5, color='#1F5A44', linewidth=2.0, label='해당 행정동 평균', zorder=3)
        ax.plot(months, city, marker='^', markersize=5, color='#9BA79E', linewidth=1.8, linestyle='--', label='시군구 전체 평균', zorder=2)
        
        for i, (m, v) in enumerate(zip(months, selected)):
            if i in [0, 3, 6, 8, 11, 12]:
                ax.annotate(f"{v:,}", (m, v), textcoords="offset points", xytext=(0, 8),
                            ha='center', fontsize=8, fontweight='bold', color='#14181F')
                
        ax.set_title("■ 월평균 매출액 추이 (단위: 만원)", fontsize=11, fontweight='bold', pad=14, loc='left', color='#14181F')
        ax.set_ylabel("월평균 매출 (만원)", fontsize=9, fontweight='bold', color='#6B6F76')
        ax.tick_params(axis='x', rotation=30, labelsize=8.5, colors='#6B6F76')
        ax.tick_params(axis='y', labelsize=8.5, colors='#6B6F76')
        
        ax.grid(True, linestyle='-', alpha=0.3, color='#D3D1CB', lw=0.8)
        for spine in ax.spines.values():
            spine.set_color('#D3D1CB')
            spine.set_linewidth(0.8)
            
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.26), ncol=3, frameon=True, facecolor='#FFFFFF', edgecolor='#D3D1CB', fontsize=8.5)
        
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        return output_path

    @staticmethod
    def generate_radius_map(site_info, competitors_data, output_path, district_wide=False):
        """맥킨지 스타일 상권 분석 지도.

        district_wide=True(구 전체 분석)면 특정 지점이 없으므로 '사업지 핀 + 3km'가
        아니라 구 전역 범위를 나타내는 지도로 라벨과 반경을 바꾼다.
        """
        fig, ax = plt.subplots(figsize=(6.2, 5.4), dpi=200)
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')

        outer_r = 3.0
        # 3km / 1.5km 반경 영역 (맥킨지 틸/네이비 틴트)
        circle_3km = plt.Circle((0, 0), outer_r, facecolor='#14181F', fill=True, alpha=0.08, linestyle='-', linewidth=1.2, edgecolor='#14181F')
        circle_1km = plt.Circle((0, 0), 1.5, facecolor='#1F5A44', fill=True, alpha=0.06, linestyle='--', linewidth=1.0, edgecolor='#1F5A44')
        ax.add_patch(circle_3km)
        ax.add_patch(circle_1km)
        
        # 중심 사업지 핀
        ax.plot(0, 0, marker='*', markersize=18, color='#B23A2E', markeredgecolor='#FFFFFF', markeredgewidth=1.2, zorder=6)
        if district_wide:
            b_name = f"{site_info.get('sigungu', '')} 전역"
            s_dong = "구 전체 상권 분석"
        else:
            b_name = site_info.get('building_name', '사업지')
            s_dong = site_info.get('dong', '서현동')
        ax.text(0, -0.48, f"★ {b_name}\n({s_dong})",
                ha='center', va='top', fontsize=9, fontweight='bold', color='#14181F', zorder=7,
                bbox=dict(boxstyle='square,pad=0.35', facecolor='#FFFFFF', edgecolor='#B23A2E', lw=1.2, alpha=0.95))
        
        # 경쟁 매장 마킹
        stores = competitors_data.get('stores', [])
        angles = [45, 135, 225, 315, 90]
        for idx, store in enumerate(stores[:4]):
            if store.get('rooms', 0) > 0:
                ang = np.radians(angles[idx % len(angles)])
                dist = 1.75 + (idx * 0.35)
                x = dist * np.cos(ang)
                y = dist * np.sin(ang)
                ax.plot(x, y, marker='o', markersize=10, color='#1F5A44', markeredgecolor='#FFFFFF', markeredgewidth=1.2, zorder=5)
                
                raw_name = store['name'].replace(' (', '\n(').replace('(', '\n(')
                if len(raw_name) > 12 and '\n' not in raw_name:
                    raw_name = raw_name[:7] + '\n' + raw_name[7:]
                label_txt = f"{idx+1}. {raw_name}"
                
                va_pos = 'bottom' if y >= 0 else 'top'
                y_off = 0.35 if y >= 0 else -0.35
                ax.text(x, y + y_off, label_txt, ha='center', va=va_pos, fontsize=8, fontweight='bold', color='#14181F', zorder=7,
                        bbox=dict(boxstyle='square,pad=0.25', facecolor='#EBEAE5', edgecolor='#D3D1CB', lw=0.8, alpha=0.95))
        
        if district_wide:
            ax.text(0, 3.2, f"{site_info.get('sigungu', '')} 전역 (관할 행정동 전체)", ha='center', fontsize=8.5, color='#6B6F76', fontweight='bold')
            ax.text(0, 1.6, "중심 상권", ha='center', fontsize=7.5, color='#6B6F76')
        else:
            ax.text(0, 3.2, "반경 3km (차량 10분 생활권)", ha='center', fontsize=8.5, color='#6B6F76', fontweight='bold')
            ax.text(0, 1.6, "1.5km", ha='center', fontsize=7.5, color='#6B6F76')
        
        ax.set_xlim(-4.2, 4.2)
        ax.set_ylim(-4.2, 4.2)
        ax.set_aspect('equal')
        ax.axis('off')
        
        _map_title = f"스크린 파크골프 상권 분석 지도 ({site_info.get('sigungu', '')} 전역)" if district_wide else "스크린 파크골프 상권 분석 지도 (반경 3km)"
        plt.title(_map_title, fontsize=11.5, fontweight='bold', pad=12, color='#14181F')
        
        addr_text = f"■ 대상지: {site_info['full_address']}"
        fig.text(0.5, 0.02, addr_text, ha='center', fontsize=8.5, fontweight='bold', color='#14181F',
                 bbox=dict(boxstyle='square,pad=0.4', facecolor='#EBEAE5', edgecolor='#D3D1CB', lw=1))
        
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        return output_path

    @staticmethod
    def generate_radar_score_chart(scores_data, output_path):
        """맥킨지 스타일 레이더 다이아몬드 차트 (글자 겹침 0%)"""
        labels = [
            '시니어 인구\n밀집도 (25)',
            '접근성 &\n주차 인프라 (25)',
            '공간 적합성\n& 층고 (15)',
            '경쟁 매장\n여유도 (15)',
            '지역 소비력\n& 매출 (20)'
        ]
        s = scores_data['scores']
        values = [
            (s['senior_population'] / 25.0) * 100,
            (s['accessibility_parking'] / 25.0) * 100,
            (s['space_efficiency'] / 15.0) * 100,
            (s['supply_gap'] / 15.0) * 100,
            (s['commercial_spending'] / 20.0) * 100
        ]
        
        num_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values_loop = values + values[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(6.2, 5.2), subplot_kw=dict(polar=True), dpi=200)
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        plt.xticks(angles[:-1], labels, color='#14181F', size=9.5, fontweight='bold')
        ax.tick_params(axis='x', pad=22)
        
        ax.set_rlabel_position(36)
        plt.yticks([40, 60, 80, 100], ["40", "60", "80", "100"], color='#9BA79E', size=7.5)
        plt.ylim(0, 125)
        
        ax.plot(angles, values_loop, linewidth=2.5, linestyle='solid', color='#1F5A44', zorder=4)
        ax.fill(angles, values_loop, color='#1F5A44', alpha=0.20, zorder=3)
        
        for a_val, v_val in zip(angles[:-1], values):
            ax.plot(a_val, v_val, marker='s', markersize=6, color='#14181F', zorder=5)
            
        plt.title(f"입지 최적성 5대 지표 [{scores_data['grade']}등급 - {scores_data['total_score']}점]",
                  size=11.5, fontweight='bold', color='#14181F', pad=28)
                  
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        return output_path

    @staticmethod
    def generate_industry_growth_chart(commercial_data, output_path):
        """업종 성장률 및 골프 특화도 페이지용 — TOP 5 매출 증가 업종 가로 막대 차트"""
        industries = commercial_data.get('top_growth_industries', [])
        names = [it['name'] for it in industries][::-1]
        growths = [float(str(it['growth']).replace('%', '').replace('+', '')) for it in industries][::-1]

        fig, ax = plt.subplots(figsize=(7.5, 4.4), dpi=200)
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')

        colors = ['#1F5A44' if i == len(growths) - 1 else '#9BA79E' for i in range(len(growths))]
        bars = ax.barh(names, growths, color=colors, zorder=3, height=0.55)

        for bar, g in zip(bars, growths):
            ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height() / 2, f"+{g:.1f}%",
                    va='center', fontsize=9.5, fontweight='bold', color='#14181F')

        ax.set_title('업종별 매출 성장률 TOP 5 (전년 대비)', fontsize=11.5, fontweight='bold', pad=14, loc='left', color='#14181F')
        ax.set_xlabel('매출 성장률 (%)', fontsize=9, fontweight='bold', color='#6B6F76')
        ax.tick_params(axis='y', labelsize=9.5, colors='#14181F')
        ax.tick_params(axis='x', labelsize=8.5, colors='#6B6F76')
        ax.grid(True, linestyle='-', alpha=0.3, axis='x', color='#D3D1CB', lw=0.8)
        for spine in ax.spines.values():
            spine.set_color('#D3D1CB')
            spine.set_linewidth(0.8)
        ax.set_xlim(0, max(growths) * 1.25 if growths else 100)

        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        return output_path

    @staticmethod
    def generate_cost_waterfall_chart(monthly_scenario, output_path):
        """비용 구조 및 순영업이익 페이지용 — 보편 시나리오 매출→비용→순이익 워터폴 차트"""
        sc = monthly_scenario
        steps = [
            ('총매출', sc['total_revenue'], 'total'),
            ('인건비', -sc['labor_cost'], 'cost'),
            ('임대료', -sc['rent_cost'], 'cost'),
            ('용품원가', -sc['cost_goods'], 'cost'),
            ('음료원가', -sc['cost_beverage'], 'cost'),
            ('카드수수료', -sc['card_fee'], 'cost'),
            ('운영비', -sc['store_ops_cost'], 'cost'),
            ('마케팅비', -sc['marketing_cost'], 'cost'),
            ('순영업이익', sc['operating_profit'], 'total'),
        ]

        fig, ax = plt.subplots(figsize=(7.5, 4.4), dpi=200)
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')

        cum = 0
        labels = []
        for i, (name, val, kind) in enumerate(steps):
            man = val / 10000.0
            if kind == 'total' and i == 0:
                bottom = 0
                height = man
                color = '#14181F'
            elif kind == 'total':
                bottom = 0
                height = man
                color = '#1F5A44'
            else:
                bottom = cum + min(man, 0)
                height = abs(man)
                color = '#B23A2E'
            ax.bar(i, height, bottom=bottom, color=color, width=0.6, zorder=3)
            if kind != 'total':
                cum += man
            else:
                cum = man
            labels.append(name)
            label_y = bottom + height + (max(steps, key=lambda s: abs(s[1]))[1] / 10000.0) * 0.02
            ax.text(i, label_y, f"{man:,.0f}", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#14181F')

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=8.5, rotation=20, ha='right', color='#14181F')
        ax.set_ylabel('금액 (만원)', fontsize=9, fontweight='bold', color='#6B6F76')
        ax.set_title('보편적 시나리오 매출 → 비용 → 순영업이익 구조', fontsize=11.5, fontweight='bold', pad=14, loc='left', color='#14181F')
        ax.grid(True, linestyle='-', alpha=0.3, axis='y', color='#D3D1CB', lw=0.8)
        ax.axhline(0, color='#9BA79E', linewidth=0.8)
        for spine in ax.spines.values():
            spine.set_color('#D3D1CB')
            spine.set_linewidth(0.8)

        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        return output_path

    @staticmethod
    def generate_bep_chart(financial_data, output_path):
        """손익분기점(BEP) 및 투자금 회수기간 페이지용 — 3대 시나리오 회수기간 비교 차트"""
        inv = financial_data['investment']
        scenarios = [
            ('보수적', inv['payback_months_conservative'], '#9BA79E'),
            ('보편적', inv['payback_months_moderate'], '#1F5A44'),
            ('긍정적', inv['payback_months_optimistic'], '#14181F'),
        ]
        names = [s[0] for s in scenarios]
        months = [s[1] for s in scenarios]
        colors = [s[2] for s in scenarios]

        fig, ax = plt.subplots(figsize=(7.5, 4.4), dpi=200)
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')

        bars = ax.bar(names, months, color=colors, width=0.5, zorder=3)
        for bar, m in zip(bars, months):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(months) * 0.02,
                    f"{m:.1f}개월", ha='center', va='bottom', fontsize=10, fontweight='bold', color='#14181F')

        ax.axhline(12, color='#B23A2E', linestyle='--', linewidth=1.2, zorder=2)
        ax.text(len(names) - 0.4, 12 + max(months) * 0.02, '1년', fontsize=8.5, color='#B23A2E', fontweight='bold')

        ax.set_ylabel('투자금 회수 기간 (개월)', fontsize=9, fontweight='bold', color='#6B6F76')
        ax.set_title(f"시나리오별 투자금({inv['total_capex']/100000000:.3g}억원) 회수 기간 비교", fontsize=11.5, fontweight='bold', pad=14, loc='left', color='#14181F')
        ax.grid(True, linestyle='-', alpha=0.3, axis='y', color='#D3D1CB', lw=0.8)
        for spine in ax.spines.values():
            spine.set_color('#D3D1CB')
            spine.set_linewidth(0.8)

        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        return output_path

    @staticmethod
    def generate_profit_forecast_chart(forecast_data, output_path, rooms=10):
        years = [f"{item['year']}년차" for item in forecast_data['moderate']]
        mod_rev = [item['total_revenue'] / 100000000 for item in forecast_data['moderate']]
        mod_op = [item['operating_profit'] / 100000000 for item in forecast_data['moderate']]
        opt_op = [item['operating_profit'] / 100000000 for item in forecast_data['optimistic']]
        con_op = [item['operating_profit'] / 100000000 for item in forecast_data['conservative']]
        
        fig, ax = plt.subplots(figsize=(7.5, 4.4), dpi=200)
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')
        
        x = np.arange(len(years))
        width = 0.35
        
        rects1 = ax.bar(x - width/2, mod_rev, width, label='연간 총매출 (보편)', color='#14181F', alpha=0.9, zorder=3)
        rects2 = ax.bar(x + width/2, mod_op, width, label='연간 영업이익 (보편)', color='#1F5A44', alpha=0.9, zorder=3)
        
        ax.plot(x, opt_op, color='#A6813C', marker='o', markersize=6, linewidth=2.0, label='긍정 시나리오 영업이익', zorder=4)
        ax.plot(x, con_op, color='#9BA79E', marker='s', markersize=5, linewidth=1.8, linestyle='--', label='보수 시나리오 영업이익', zorder=4)
        
        for rect in rects2:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}억',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 4),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1F5A44')
                        
        ax.set_ylabel('금액 (억원)', fontsize=9, fontweight='bold', color='#6B6F76')
        ax.set_title(f'마이파크 {rooms}타석 5개년 손익 예측 (연 2% 성장률 반영)', fontsize=11.5, fontweight='bold', pad=14, color='#14181F')
        ax.set_xticks(x)
        ax.set_xticklabels(years, fontsize=9, fontweight='bold', color='#14181F')
        ax.grid(True, linestyle='-', alpha=0.3, axis='y', color='#D3D1CB', lw=0.8)
        for spine in ax.spines.values():
            spine.set_color('#D3D1CB')
            spine.set_linewidth(0.8)
            
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.26), ncol=2, frameon=True, facecolor='#FFFFFF', edgecolor='#D3D1CB', fontsize=8.5)
        
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        return output_path
