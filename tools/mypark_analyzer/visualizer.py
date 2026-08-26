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
font_candidates = [
    os.path.join(current_dir, 'fonts', 'MalgunGothic.ttf'),
    os.path.join(current_dir, 'fonts', 'MalgunGothicBold.ttf'),
    r'C:\Windows\Fonts\malgun.ttf',
    r'C:\Windows\Fonts\NanumGothic.ttf',
    '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
]

korean_font_name = None
for fpath in font_candidates:
    if os.path.exists(fpath):
        try:
            fm.fontManager.addfont(fpath)
            prop = fm.FontProperties(fname=fpath)
            korean_font_name = prop.get_name()
            plt.rcParams['font.family'] = korean_font_name
            plt.rcParams['font.sans-serif'] = [korean_font_name, 'Malgun Gothic', 'DejaVu Sans', 'Arial']
            break
        except Exception:
            pass

if korean_font_name is None:
    print("[FONT WARNING] 한글 폰트를 찾지 못해 matplotlib 기본 폰트로 대체합니다 — 차트의 한글이 깨질 수 있습니다.")

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
        
        ax.plot(months, selected, marker='o', markersize=6, color='#002B49', linewidth=2.5, label='선택영역 (반경 3km)', zorder=4)
        ax.plot(months, dong, marker='s', markersize=5, color='#008080', linewidth=2.0, label='해당 행정동 평균', zorder=3)
        ax.plot(months, city, marker='^', markersize=5, color='#94A3B8', linewidth=1.8, linestyle='--', label='시군구 전체 평균', zorder=2)
        
        for i, (m, v) in enumerate(zip(months, selected)):
            if i in [0, 3, 6, 8, 11, 12]:
                ax.annotate(f"{v:,}", (m, v), textcoords="offset points", xytext=(0, 8),
                            ha='center', fontsize=8, fontweight='bold', color='#002B49')
                
        ax.set_title("■ 월평균 매출액 추이 (단위: 만원)", fontsize=11, fontweight='bold', pad=14, loc='left', color='#002B49')
        ax.set_ylabel("월평균 매출 (만원)", fontsize=9, fontweight='bold', color='#475569')
        ax.tick_params(axis='x', rotation=30, labelsize=8.5, colors='#475569')
        ax.tick_params(axis='y', labelsize=8.5, colors='#475569')
        
        ax.grid(True, linestyle='-', alpha=0.3, color='#CBD5E1', lw=0.8)
        for spine in ax.spines.values():
            spine.set_color('#CBD5E1')
            spine.set_linewidth(0.8)
            
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.26), ncol=3, frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=8.5)
        
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        return output_path

    @staticmethod
    def generate_radius_map(site_info, competitors_data, output_path):
        """맥킨지 스타일 정밀 반경 3km 상권 분석 지도"""
        fig, ax = plt.subplots(figsize=(6.2, 5.4), dpi=200)
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')
        
        # 3km / 1.5km 반경 영역 (맥킨지 틸/네이비 틴트)
        circle_3km = plt.Circle((0, 0), 3.0, facecolor='#002B49', fill=True, alpha=0.08, linestyle='-', linewidth=1.2, edgecolor='#002B49')
        circle_1km = plt.Circle((0, 0), 1.5, facecolor='#008080', fill=True, alpha=0.06, linestyle='--', linewidth=1.0, edgecolor='#008080')
        ax.add_patch(circle_3km)
        ax.add_patch(circle_1km)
        
        # 중심 사업지 핀
        ax.plot(0, 0, marker='*', markersize=18, color='#DC2626', markeredgecolor='#FFFFFF', markeredgewidth=1.2, zorder=6)
        b_name = site_info.get('building_name', '사업지')
        s_dong = site_info.get('dong', '서현동')
        ax.text(0, -0.48, f"★ {b_name}\n({s_dong})",
                ha='center', va='top', fontsize=9, fontweight='bold', color='#002B49', zorder=7,
                bbox=dict(boxstyle='square,pad=0.35', facecolor='#FFFFFF', edgecolor='#DC2626', lw=1.2, alpha=0.95))
        
        # 경쟁 매장 마킹
        stores = competitors_data.get('stores', [])
        angles = [45, 135, 225, 315, 90]
        for idx, store in enumerate(stores[:4]):
            if store.get('rooms', 0) > 0:
                ang = np.radians(angles[idx % len(angles)])
                dist = 1.75 + (idx * 0.35)
                x = dist * np.cos(ang)
                y = dist * np.sin(ang)
                ax.plot(x, y, marker='o', markersize=10, color='#008080', markeredgecolor='#FFFFFF', markeredgewidth=1.2, zorder=5)
                
                raw_name = store['name'].replace(' (', '\n(').replace('(', '\n(')
                if len(raw_name) > 12 and '\n' not in raw_name:
                    raw_name = raw_name[:7] + '\n' + raw_name[7:]
                label_txt = f"{idx+1}. {raw_name}"
                
                va_pos = 'bottom' if y >= 0 else 'top'
                y_off = 0.35 if y >= 0 else -0.35
                ax.text(x, y + y_off, label_txt, ha='center', va=va_pos, fontsize=8, fontweight='bold', color='#002B49', zorder=7,
                        bbox=dict(boxstyle='square,pad=0.25', facecolor='#F8FAFC', edgecolor='#CBD5E1', lw=0.8, alpha=0.95))
        
        ax.text(0, 3.2, "반경 3km (차량 10분 생활권)", ha='center', fontsize=8.5, color='#475569', fontweight='bold')
        ax.text(0, 1.6, "1.5km", ha='center', fontsize=7.5, color='#64748B')
        
        ax.set_xlim(-4.2, 4.2)
        ax.set_ylim(-4.2, 4.2)
        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.title("스크린 파크골프 상권 분석 지도 (반경 3km)", fontsize=11.5, fontweight='bold', pad=12, color='#002B49')
        
        addr_text = f"■ 대상지: {site_info['full_address']}"
        fig.text(0.5, 0.02, addr_text, ha='center', fontsize=8.5, fontweight='bold', color='#002B49',
                 bbox=dict(boxstyle='square,pad=0.4', facecolor='#F8FAFC', edgecolor='#CBD5E1', lw=1))
        
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        return output_path

    @staticmethod
    def generate_radar_score_chart(scores_data, output_path):
        """맥킨지 스타일 레이더 다이아몬드 차트 (글자 겹침 0%)"""
        labels = [
            '골든 시니어\n집적도 (25)',
            '접근성 &\n주차 인프라 (25)',
            '공간 적합성\n& 층고 (15)',
            '수요공급 갭\n블루오션 (15)',
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
        
        plt.xticks(angles[:-1], labels, color='#002B49', size=9.5, fontweight='bold')
        ax.tick_params(axis='x', pad=22)
        
        ax.set_rlabel_position(36)
        plt.yticks([40, 60, 80, 100], ["40", "60", "80", "100"], color='#94A3B8', size=7.5)
        plt.ylim(0, 125)
        
        ax.plot(angles, values_loop, linewidth=2.5, linestyle='solid', color='#008080', zorder=4)
        ax.fill(angles, values_loop, color='#008080', alpha=0.20, zorder=3)
        
        for a_val, v_val in zip(angles[:-1], values):
            ax.plot(a_val, v_val, marker='s', markersize=6, color='#002B49', zorder=5)
            
        plt.title(f"입지 최적성 5대 지표 [{scores_data['grade']}등급 - {scores_data['total_score']}점]",
                  size=11.5, fontweight='bold', color='#002B49', pad=28)
                  
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        return output_path

    @staticmethod
    def generate_profit_forecast_chart(forecast_data, output_path):
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
        
        rects1 = ax.bar(x - width/2, mod_rev, width, label='연간 총매출 (보편)', color='#002B49', alpha=0.9, zorder=3)
        rects2 = ax.bar(x + width/2, mod_op, width, label='연간 영업이익 (보편)', color='#008080', alpha=0.9, zorder=3)
        
        ax.plot(x, opt_op, color='#2563EB', marker='o', markersize=6, linewidth=2.0, label='긍정 시나리오 영업이익', zorder=4)
        ax.plot(x, con_op, color='#94A3B8', marker='s', markersize=5, linewidth=1.8, linestyle='--', label='보수 시나리오 영업이익', zorder=4)
        
        for rect in rects2:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}억',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 4),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#008080')
                        
        ax.set_ylabel('금액 (억원)', fontsize=9, fontweight='bold', color='#475569')
        ax.set_title('마이파크 10타석 5개년 손익 예측 (연 2% 성장률 반영)', fontsize=11.5, fontweight='bold', pad=14, color='#002B49')
        ax.set_xticks(x)
        ax.set_xticklabels(years, fontsize=9, fontweight='bold', color='#334155')
        ax.grid(True, linestyle='-', alpha=0.3, axis='y', color='#CBD5E1', lw=0.8)
        for spine in ax.spines.values():
            spine.set_color('#CBD5E1')
            spine.set_linewidth(0.8)
            
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.26), ncol=2, frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=8.5)
        
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        return output_path
