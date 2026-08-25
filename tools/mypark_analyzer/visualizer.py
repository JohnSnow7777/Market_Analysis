# -*- coding: utf-8 -*-
"""Matplotlib 기반 상권/인구/재무 시각화 차트 생성 모듈"""
import os
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class Visualizer:
    """차트 및 그래프 렌더러"""
    
    @staticmethod
    def create_radar_chart(scores, output_path):
        categories = ['골든 시니어\n집적도(25)', '접근성 및\n주차(25)', '공간적합성\n임대료(15)', '공급 갭\n블루오션(15)', '지역 소비력\n여가지출(20)']
        max_scores = [25.0, 25.0, 15.0, 15.0, 20.0]
        actual_scores = [
            scores['senior_population'],
            scores['accessibility_parking'],
            scores['space_efficiency'],
            scores['supply_gap'],
            scores['commercial_spending']
        ]
        
        ratios = [(a / m) * 100 for a, m in zip(actual_scores, max_scores)]
        ratios += ratios[:1]
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor('#FFFFFF')
        
        ax.fill(angles, ratios, color='#003366', alpha=0.3)
        ax.plot(angles, ratios, color='#003366', linewidth=2.5, marker='o', markersize=7)
        
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10, fontweight='bold', color='#333333')
        ax.set_ylim(0, 100)
        ax.grid(color='#CCCCCC', linestyle='--', linewidth=0.8)
        
        plt.title('마이파크 입지 최적성 5대 다이아몬드 평가', fontsize=13, fontweight='bold', pad=20, color='#003366')
        plt.tight_layout()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        return output_path

    @staticmethod
    def create_sales_trend_chart(commercial_data, output_path):
        months = commercial_data['months']
        selected = commercial_data['selected_area_sales']
        dong = commercial_data['dong_avg_sales']
        city = commercial_data['city_avg_sales']
        
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('#FFFFFF')
        
        ax.plot(months, city, marker='o', color='#FF9800', label='시/구 평균', linewidth=2)
        ax.plot(months, dong, marker='o', color='#E91E63', label='행정동 평균', linewidth=2)
        ax.plot(months, selected, marker='s', color='#2196F3', label='선택 상권 (사업지 반경)', linewidth=2.5)
        
        ax.set_title('업소당 월평균 매출액 추이 (단위: 만원)', fontsize=12, fontweight='bold', pad=12, color='#003366')
        ax.set_xlabel('기준 년월', fontsize=9, color='#666666')
        ax.set_ylabel('월평균 매출 (만원)', fontsize=9, color='#666666')
        ax.legend(loc='upper left', frameon=True, facecolor='#F5F7FA')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        plt.xticks(rotation=45, fontsize=8)
        plt.tight_layout()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        return output_path

    @staticmethod
    def create_5year_profit_chart(financials, output_path):
        years = ['1년차(N+1)', '2년차(N+2)', '3년차(N+3)', '4년차(N+4)', '5년차(N+5)']
        cons_ops = [y['operating_profit'] / 100000000.0 for y in financials['forecast_5year']['conservative']]
        mod_ops = [y['operating_profit'] / 100000000.0 for y in financials['forecast_5year']['moderate']]
        opt_ops = [y['operating_profit'] / 100000000.0 for y in financials['forecast_5year']['optimistic']]
        
        x = np.arange(len(years))
        width = 0.25
        
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('#FFFFFF')
        
        r1 = ax.bar(x - width, cons_ops, width, label='보수적 시나리오', color='#78909C')
        r2 = ax.bar(x, mod_ops, width, label='보편적 시나리오 (기준)', color='#1E88E5')
        r3 = ax.bar(x + width, opt_ops, width, label='긍정적 시나리오', color='#43A047')
        
        ax.set_title('신규 마이파크 5개년 연간 영업이익 추정 (단위: 억원)', fontsize=12, fontweight='bold', pad=12, color='#003366')
        ax.set_ylabel('영업이익 (억원)', fontsize=9, color='#666666')
        ax.set_xticks(x)
        ax.set_xticklabels(years, fontsize=9, fontweight='bold')
        ax.legend(loc='upper left', frameon=True)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        
        for bar in r2:
            h = bar.get_height()
            ax.annotate(f'{h:.1f}억',
                        xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold', color='#0D47A1')
            
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        return output_path
