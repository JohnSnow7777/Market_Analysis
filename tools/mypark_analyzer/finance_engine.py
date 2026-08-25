# -*- coding: utf-8 -*-
"""재무 타당성 분석 및 3대 시나리오 손익/BEP/ROI 계산 엔진 (1인 18홀 7,000원 기준 정밀 모델)"""

class FinanceEngine:
    """재무 모델링 엔진"""

    @staticmethod
    def calculate_investment(rooms=10, area_pyeong=120):
        simulator_cost = rooms * 15000000
        interior_cost = area_pyeong * 1300000
        initial_supplies_cost = 30000000
        subtotal_capex = simulator_cost + interior_cost + initial_supplies_cost
        
        return {
            'rooms': rooms,
            'area_pyeong': area_pyeong,
            'simulator_unit_price': 15000000,
            'simulator_cost': simulator_cost,
            'interior_cost_per_pyeong': 1300000,
            'interior_cost': interior_cost,
            'initial_supplies_cost': initial_supplies_cost,
            'subtotal_capex': subtotal_capex,
            'total_capex': subtotal_capex
        }

    @staticmethod
    def calculate_monthly_scenario(rooms=10, monthly_rent=5400000, staff_count=3, scenario_type='moderate', regional_demand_multiplier=1.0):
        game_fee = 7000
        
        if scenario_type == 'conservative':
            base_turns = 3.2 * regional_demand_multiplier
        elif scenario_type == 'optimistic':
            base_turns = 5.6 * regional_demand_multiplier
        else: # moderate
            base_turns = 4.5 * regional_demand_multiplier
            
        daily_turns = round(base_turns, 2)
        daily_users = int(rooms * daily_turns * 3.33)
        monthly_users = daily_users * 30
        
        game_revenue = monthly_users * game_fee
        beverage_revenue = int(game_revenue * 0.10)
        goods_revenue = int(game_revenue * 0.05)
        lesson_revenue = int(game_revenue * 0.03)
        total_revenue = game_revenue + beverage_revenue + goods_revenue + lesson_revenue
        
        labor_cost = staff_count * 2500000
        rent_cost = monthly_rent
        cost_beverage = int(beverage_revenue * 0.40)
        cost_goods = int(goods_revenue * 0.60)
        cost_lesson = int(lesson_revenue * 0.80)
        card_fee = int(total_revenue * 0.02)
        utilities_cost = 2000000
        maintenance_cost = 800000
        store_ops_cost = utilities_cost + maintenance_cost
        rental_cost = 700000
        marketing_cost = 1000000 if scenario_type == 'optimistic' else (700000 if scenario_type == 'moderate' else 500000)
        
        total_cost = (labor_cost + rent_cost + cost_beverage + cost_goods + 
                      cost_lesson + card_fee + store_ops_cost + 
                      rental_cost + marketing_cost)
                      
        operating_profit = total_revenue - total_cost
        profit_margin = round((operating_profit / total_revenue) * 100, 1) if total_revenue > 0 else 0.0
        
        sc_names = {'conservative': '보수적 시나리오', 'moderate': '보편적 시나리오', 'optimistic': '긍정적 시나리오'}
        
        return {
            'scenario_type': scenario_type,
            'scenario_name': sc_names.get(scenario_type, scenario_type),
            'daily_turns_per_room': daily_turns,
            'daily_users': daily_users,
            'monthly_users': monthly_users,
            'game_revenue': game_revenue,
            'room_revenue': game_revenue,
            'beverage_revenue': beverage_revenue,
            'cafe_revenue': beverage_revenue,
            'goods_revenue': goods_revenue,
            'lesson_revenue': lesson_revenue,
            'total_revenue': total_revenue,
            'labor_cost': labor_cost,
            'rent_cost': rent_cost,
            'cost_beverage': cost_beverage,
            'cafe_cost': cost_beverage,
            'cost_goods': cost_goods,
            'goods_cost': cost_goods,
            'cost_lesson': cost_lesson,
            'lesson_cost': cost_lesson,
            'card_fee': card_fee,
            'utilities_cost': utilities_cost,
            'maintenance_cost': maintenance_cost,
            'store_ops_cost': store_ops_cost,
            'rental_cost': rental_cost,
            'marketing_cost': marketing_cost,
            'total_cost': total_cost,
            'operating_profit': operating_profit,
            'profit_margin': profit_margin
        }

    @staticmethod
    def get_full_financial_analysis(rooms=10, monthly_rent=5400000, area_pyeong=120, staff_count=3, demographics=None, commercial=None):
        inv = FinanceEngine.calculate_investment(rooms, area_pyeong)
        
        senior_pop = demographics.get('senior_50_plus', 72400) if demographics else 72400
        comm_sales = commercial.get('monthly_avg_sales', 20500000) if commercial else 20500000
        
        if senior_pop >= 65000 and comm_sales >= 22000000:
            reg_mult = 1.08
        elif senior_pop >= 45000:
            reg_mult = 1.00
        elif senior_pop >= 25000:
            reg_mult = 0.82
        else:
            reg_mult = 0.68

        scenarios = {
            'conservative': FinanceEngine.calculate_monthly_scenario(rooms, monthly_rent, staff_count, 'conservative', reg_mult),
            'moderate': FinanceEngine.calculate_monthly_scenario(rooms, monthly_rent, staff_count, 'moderate', reg_mult),
            'optimistic': FinanceEngine.calculate_monthly_scenario(rooms, monthly_rent, staff_count, 'optimistic', reg_mult),
        }
        
        # 고정비 (직원 3명 기준 약 1,560~1,640만원)
        fixed_cost = (staff_count * 2500000) + monthly_rent + 2000000 + 800000 + 700000
        # 1인 18홀 7,000원 기준 공헌이익: 7,462원
        margin_per_user = 7000 * 0.98 + (7000 * 0.10 * 0.60) + (7000 * 0.05 * 0.40) + (7000 * 0.03 * 0.20)
        bep_monthly_users = int(fixed_cost / margin_per_user)
        bep_daily_users = round(bep_monthly_users / 30.0, 1)
        # 타석당 1일 회전수 (1타석당 1일 10시간 중 몇 회전 필요한가: bep_daily_users / (rooms * 3.33))
        bep_turns_per_room = round(bep_daily_users / (float(rooms) * 10.0), 2)
        bep_monthly_sales = int(bep_monthly_users * (7000 * 1.18))
        
        capex = inv['subtotal_capex']
        op_mod = scenarios['moderate']['operating_profit']
        op_opt = scenarios['optimistic']['operating_profit']
        op_con = scenarios['conservative']['operating_profit']
        
        payback_months_mod = round(capex / op_mod, 1) if op_mod > 0 else 99.0
        payback_months_opt = round(capex / op_opt, 1) if op_opt > 0 else 99.0
        payback_months_con = round(capex / op_con, 1) if op_con > 0 else 99.0
        
        inv['bep_monthly_sales'] = bep_monthly_sales
        inv['bep_turns_per_room'] = bep_turns_per_room # 0.70회전
        inv['bep_daily_users'] = int(bep_daily_users)   # 1일 69명
        inv['payback_months_moderate'] = payback_months_mod
        inv['payback_months_optimistic'] = payback_months_opt
        inv['payback_months_conservative'] = payback_months_con
        
        # 창업주 직접 운영 모델 (점주 1명 상주 + 파트 1명 = 인건비 250만, 월 500만원 절감)
        owner_fixed_cost = (1 * 2500000) + monthly_rent + 2000000 + 800000 + 700000
        owner_bep_monthly_users = int(owner_fixed_cost / margin_per_user)
        owner_bep_daily_users = round(owner_bep_monthly_users / 30.0, 1)
        owner_bep_turns = round(owner_bep_daily_users / (float(rooms) * 10.0), 2) # 0.47회전
        owner_op_mod = op_mod + 5000000
        owner_payback = round(capex / owner_op_mod, 1)
        
        inv['owner_operated'] = {
            'fixed_cost': owner_fixed_cost,
            'bep_monthly_sales': int(owner_bep_monthly_users * (7000 * 1.18)),
            'bep_turns_per_room': owner_bep_turns,
            'bep_monthly_users': owner_bep_monthly_users,
            'bep_daily_users': int(owner_bep_daily_users),
            'monthly_operating_profit_moderate': owner_op_mod,
            'profit_margin_moderate': round((owner_op_mod / scenarios['moderate']['total_revenue']) * 100, 1),
            'payback_months': owner_payback,
            'labor_savings_monthly': 5000000
        }
        
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
            'rooms': rooms,
            'owner_operated': inv['owner_operated']
        }
