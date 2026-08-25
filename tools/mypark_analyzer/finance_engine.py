# -*- coding: utf-8 -*-
"""재무 타당성 및 3개 시나리오, 5개년 손익 예측 엔진 (BEP 계산 정상화)"""
from .config import DEFAULT_SETTINGS, SCENARIO_CONFIG

class FinanceEngine:
    """마이파크 재무 분석 및 3개 시나리오 손익 계산기"""
    
    @staticmethod
    def calculate_investment(rooms=10, area_pyeong=120):
        # 10타석 120평 플래그십 표준 CAPEX
        system_cost = rooms * 20000000          # 타석당 2,000만원 = 2.0억원
        interior_cost = area_pyeong * 1300000   # 평당 130만원 = 1.56억원
        signage_cost = 15000000                 # 간판/사인물 1,500만원
        furniture_cost = 15000000               # 가구/키오스크 1,500만원
        subtotal_capex = system_cost + interior_cost + signage_cost + furniture_cost  # 3.86억원
        
        deposit = area_pyeong * 45000 * 10      # 임차보증금 (월세 10개월분)
        total_initial_cash = subtotal_capex + deposit
        
        return {
            'system_cost': system_cost,
            'interior_cost': interior_cost,
            'signage_cost': signage_cost,
            'furniture_cost': furniture_cost,
            'subtotal_capex': subtotal_capex,
            'deposit': deposit,
            'total_initial_cash': total_initial_cash,
            'total_capex': subtotal_capex
        }

    @staticmethod
    def calculate_monthly_scenario(rooms, monthly_rent, staff_count, scenario_type='moderate'):
        cfg = DEFAULT_SETTINGS
        sc_cfg = SCENARIO_CONFIG[scenario_type]
        
        users_per_room = sc_cfg['avg_daily_users_per_room']
        daily_users = int(rooms * users_per_room)
        monthly_users = int(daily_users * 30)
        fee = cfg['game_price_18hole']  # 8,000원
        
        room_revenue = int(monthly_users * fee)
        goods_revenue = int(room_revenue * cfg['ratio_goods'])
        cafe_revenue = int(room_revenue * cfg['ratio_cafe'])
        lesson_revenue = int(room_revenue * cfg['ratio_lesson'])
        total_revenue = room_revenue + goods_revenue + cafe_revenue + lesson_revenue
        
        labor_cost = staff_count * cfg['labor_cost_per_person']
        rent_cost = monthly_rent
        goods_cost = int(goods_revenue * cfg['cost_rate_goods'])
        cafe_cost = int(cafe_revenue * cfg['cost_rate_cafe'])
        lesson_cost = int(lesson_revenue * cfg['cost_rate_lesson'])
        card_fee = int(total_revenue * cfg['card_fee_rate'])
        
        # 매장 운영비 + 렌탈 + 마케팅
        store_ops_cost = 2000000
        rental_cost = 800000
        marketing_cost = 700000
        
        total_cost = (labor_cost + rent_cost + goods_cost + cafe_cost + 
                      lesson_cost + card_fee + store_ops_cost + rental_cost + marketing_cost)
        operating_profit = total_revenue - total_cost
        profit_margin = round((operating_profit / total_revenue) * 100, 1) if total_revenue > 0 else 0
        
        return {
            'scenario_name': sc_cfg['name'],
            'daily_users': daily_users,
            'monthly_users': monthly_users,
            'room_revenue': room_revenue,
            'goods_revenue': goods_revenue,
            'cafe_revenue': cafe_revenue,
            'lesson_revenue': lesson_revenue,
            'total_revenue': total_revenue,
            'labor_cost': labor_cost,
            'rent_cost': rent_cost,
            'goods_cost': goods_cost,
            'cafe_cost': cafe_cost,
            'lesson_cost': lesson_cost,
            'card_fee': card_fee,
            'store_ops_cost': store_ops_cost,
            'rental_cost': rental_cost,
            'marketing_cost': marketing_cost,
            'total_cost': total_cost,
            'operating_profit': operating_profit,
            'profit_margin': profit_margin
        }

    @staticmethod
    def get_full_financial_analysis(rooms=10, monthly_rent=5400000, area_pyeong=120, staff_count=3):
        inv = FinanceEngine.calculate_investment(rooms, area_pyeong)
        
        scenarios = {
            'conservative': FinanceEngine.calculate_monthly_scenario(rooms, monthly_rent, staff_count, 'conservative'),
            'moderate': FinanceEngine.calculate_monthly_scenario(rooms, monthly_rent, staff_count, 'moderate'),
            'optimistic': FinanceEngine.calculate_monthly_scenario(rooms, monthly_rent, staff_count, 'optimistic'),
        }
        
        # 정확한 BEP 손익분기점 계산 (고정비 커버 기준)
        fixed_cost = (staff_count * 2500000) + monthly_rent + 2000000 + 800000 + 700000
        # 1인당 평균 결제액(18홀 8천원 + 부가매출 18% = 9,440원) 중 공헌이익(약 7,552원)
        margin_per_user = 8000 * 0.98 + (8000 * 0.10 * 0.40) + (8000 * 0.05 * 0.50) + (8000 * 0.03 * 0.20)
        bep_monthly_users = int(fixed_cost / margin_per_user)
        bep_daily_users = round(bep_monthly_users / 30.0, 1)
        bep_turns_per_room = round(bep_daily_users / float(rooms), 2)
        bep_monthly_sales = int(bep_monthly_users * (8000 * 1.18))
        
        capex = inv['subtotal_capex']
        op_mod = scenarios['moderate']['operating_profit']
        op_opt = scenarios['optimistic']['operating_profit']
        op_con = scenarios['conservative']['operating_profit']
        
        payback_months_mod = round(capex / op_mod, 1) if op_mod > 0 else 99.0
        payback_months_opt = round(capex / op_opt, 1) if op_opt > 0 else 99.0
        payback_months_con = round(capex / op_con, 1) if op_con > 0 else 99.0
        
        inv['bep_monthly_sales'] = bep_monthly_sales
        inv['bep_turns_per_room'] = bep_turns_per_room  # 타석당 1일 0.7~0.8회전
        inv['bep_daily_users'] = int(bep_daily_users)   # 매장 전체 1일 약 7~8명
        inv['payback_months_moderate'] = payback_months_mod
        inv['payback_months_optimistic'] = payback_months_opt
        inv['payback_months_conservative'] = payback_months_con
        
        growth_rate = 0.02
        forecast_5y = {}
        for sc_key, sc_val in scenarios.items():
            sc_list = []
            base_rev = sc_val['total_revenue'] * 12
            base_cost = sc_val['total_cost'] * 12
            for yr in range(1, 6):
                y_factor = (1 + growth_rate) ** (yr - 1)
                y_rev = int(base_rev * y_factor)
                y_cost = int(base_cost * ((1 + 0.015) ** (yr - 1)))
                y_op = y_rev - y_cost
                sc_list.append({
                    'year': yr,
                    'total_revenue': y_rev,
                    'total_cost': y_cost,
                    'operating_profit': y_op,
                    'margin': round((y_op / y_rev) * 100, 1)
                })
            forecast_5y[sc_key] = sc_list
            
        return {
            'investment': inv,
            'monthly_scenarios': scenarios,
            'forecast_5year': forecast_5y,
            'staff_count': staff_count,
            'monthly_rent': monthly_rent,
            'area_pyeong': area_pyeong,
            'rooms': rooms
        }
