# -*- coding: utf-8 -*-
"""재무 타당성 분석 및 3대 시나리오 손익/BEP/ROI 계산 엔진 (SSOT 3.19억원 & 7,000원 모델)"""
from .config import DEFAULT_SETTINGS

class FinanceEngine:
    """재무 모델링 엔진 (SSOT 기준)"""

    @staticmethod
    def calculate_investment(rooms=10, area_pyeong=120):
        simulator_cost = rooms * DEFAULT_SETTINGS['simulator_unit_price'] # 1.5억
        interior_cost = area_pyeong * DEFAULT_SETTINGS['interior_cost_per_pyeong'] # 1.44억
        hvac_cost = DEFAULT_SETTINGS['hvac_cost'] # 1200만
        signage_cost = DEFAULT_SETTINGS['signage_cost'] # 500만
        furniture_cost = DEFAULT_SETTINGS['furniture_cost'] # 300만
        supplies_cost = DEFAULT_SETTINGS['supplies_cost'] # 500만
        other_facilities = hvac_cost + signage_cost + furniture_cost + supplies_cost # 2500만
        
        total_capex = simulator_cost + interior_cost + other_facilities # 3.19억
        
        return {
            'rooms': rooms,
            'area_pyeong': area_pyeong,
            'simulator_unit_price': DEFAULT_SETTINGS['simulator_unit_price'],
            'simulator_cost': simulator_cost,
            'interior_cost_per_pyeong': DEFAULT_SETTINGS['interior_cost_per_pyeong'],
            'interior_cost': interior_cost,
            'hvac_cost': hvac_cost,
            'signage_cost': signage_cost,
            'furniture_cost': furniture_cost,
            'supplies_cost': supplies_cost,
            'other_facilities': other_facilities,
            'subtotal_capex': total_capex,
            'total_capex': total_capex
        }

    @staticmethod
    def calculate_monthly_scenario(rooms=10, monthly_rent=4600000, staff_count=1, scenario_type='moderate', regional_demand_multiplier=1.0):
        game_fee = 7000
        team_fee = game_fee * 4 # 28,000원
        
        if scenario_type == 'conservative':
            base_turns = 3.0 * regional_demand_multiplier
            goods_daily = 25000 * regional_demand_multiplier
        elif scenario_type == 'optimistic':
            base_turns = 5.0 * regional_demand_multiplier
            goods_daily = 50000 * regional_demand_multiplier
        else: # moderate
            base_turns = 4.0 * regional_demand_multiplier
            goods_daily = 40000 * regional_demand_multiplier
            
        daily_turns = round(base_turns, 2)
        daily_teams = rooms * daily_turns
        daily_users = int(daily_teams * 4)
        monthly_users = daily_users * 30
        
        # 1) 파크골프 룸 회전 매출 (게임비)
        game_revenue = int(daily_teams * team_fee * 30)
        # 2) 파크골프 용품 판매 매출
        goods_revenue = int(goods_daily * 30)
        # 3) 기타 판매 (음료 등 - 팀당 3,000원)
        beverage_revenue = int(daily_teams * 3000 * 30)
        
        total_revenue = game_revenue + goods_revenue + beverage_revenue
        
        # 비용 구조 (점주 1인 상주 기준: 인건비 250만)
        labor_cost = staff_count * 2500000
        rent_cost = monthly_rent
        cost_goods = int(goods_revenue * 0.50)
        cost_beverage = int(beverage_revenue * 0.50)
        card_fee = int(total_revenue * 0.02)
        store_ops_cost = 1500000 # 수도광열비 및 매장 유지비
        pos_telecom = 300000     # 통신/POS
        marketing_cost = 500000  # 마케팅비
        
        total_cost = (labor_cost + rent_cost + cost_goods + cost_beverage + 
                      card_fee + store_ops_cost + pos_telecom + marketing_cost)
                      
        operating_profit = total_revenue - total_cost
        profit_margin = round((operating_profit / total_revenue) * 100, 1) if total_revenue > 0 else 0.0
        
        sc_names = {'conservative': '보수적 시나리오 (3회전)', 'moderate': '보편적 시나리오 (4회전)', 'optimistic': '긍정적 시나리오 (5회전)'}
        
        return {
            'scenario_type': scenario_type,
            'scenario_name': sc_names.get(scenario_type, scenario_type),
            'daily_turns_per_room': daily_turns,
            'daily_users': daily_users,
            'monthly_users': monthly_users,
            'game_revenue': game_revenue,
            'room_revenue': game_revenue,
            'goods_revenue': goods_revenue,
            'beverage_revenue': beverage_revenue,
            'cafe_revenue': beverage_revenue,
            'total_revenue': total_revenue,
            'labor_cost': labor_cost,
            'rent_cost': rent_cost,
            'cost_goods': cost_goods,
            'goods_cost': cost_goods,
            'cost_beverage': cost_beverage,
            'cafe_cost': cost_beverage,
            'card_fee': card_fee,
            'store_ops_cost': store_ops_cost + pos_telecom,
            'rental_cost': pos_telecom,
            'marketing_cost': marketing_cost,
            'total_cost': total_cost,
            'operating_profit': operating_profit,
            'profit_margin': profit_margin
        }

    @staticmethod
    def get_full_financial_analysis(rooms=10, monthly_rent=4600000, area_pyeong=120, staff_count=1, demographics=None, commercial=None):
        inv = FinanceEngine.calculate_investment(rooms, area_pyeong)
        
        senior_pop = demographics.get('senior_50_plus', 72400) if demographics else 72400
        comm_sales = commercial.get('monthly_avg_sales', 20500000) if commercial else 20500000
        
        if senior_pop >= 65000 and comm_sales >= 22000000:
            reg_mult = 1.05
        elif senior_pop >= 45000:
            reg_mult = 1.00
        elif senior_pop >= 25000:
            reg_mult = 0.85
        else:
            reg_mult = 0.72

        scenarios = {
            'conservative': FinanceEngine.calculate_monthly_scenario(rooms, monthly_rent, staff_count, 'conservative', reg_mult),
            'moderate': FinanceEngine.calculate_monthly_scenario(rooms, monthly_rent, staff_count, 'moderate', reg_mult),
            'optimistic': FinanceEngine.calculate_monthly_scenario(rooms, monthly_rent, staff_count, 'optimistic', reg_mult),
        }
        
        # 월 고정비 (점주 1인 상주 250만 + 임대료 + 운영비 180만 + 마케팅 50만)
        fixed_cost = (staff_count * 2500000) + monthly_rent + 1800000 + 500000
        # 팀당 손익분기 마진: 게임비(28,000*0.98) + 음료마진(1,500*0.98) = 약 28,910원
        margin_per_team = 28000 * 0.98 + (3000 * 0.50 * 0.98)
        bep_monthly_teams = int(fixed_cost / margin_per_team)
        bep_daily_teams = round(bep_monthly_teams / 30.0, 1)
        bep_daily_users = int(bep_daily_teams * 4)
        bep_turns_per_room = round(bep_daily_teams / float(rooms), 2)
        bep_monthly_sales = int(bep_monthly_teams * 31000)
        
        capex = inv['total_capex'] # 3.19억원
        op_mod = scenarios['moderate']['operating_profit']
        op_opt = scenarios['optimistic']['operating_profit']
        op_con = scenarios['conservative']['operating_profit']
        
        payback_months_mod = round(capex / op_mod, 1) if op_mod > 0 else 99.0
        payback_months_opt = round(capex / op_opt, 1) if op_opt > 0 else 99.0
        payback_months_con = round(capex / op_con, 1) if op_con > 0 else 99.0
        
        inv['bep_monthly_sales'] = bep_monthly_sales
        inv['bep_turns_per_room'] = bep_turns_per_room
        inv['bep_daily_users'] = bep_daily_users
        inv['payback_months_moderate'] = payback_months_mod
        inv['payback_months_optimistic'] = payback_months_opt
        inv['payback_months_conservative'] = payback_months_con
        
        # 직원 위탁 운영 모델 (직원 2명 추가 채용 = 인건비 500만원 추가)
        staff3_fixed_cost = fixed_cost + 5000000
        staff3_bep_teams = int(staff3_fixed_cost / margin_per_team)
        staff3_bep_turns = round((staff3_bep_teams / 30.0) / float(rooms), 2)
        staff3_op_mod = max(0, op_mod - 5000000)
        staff3_payback = round(capex / staff3_op_mod, 1) if staff3_op_mod > 0 else 99.0
        
        inv['owner_operated'] = {
            'fixed_cost': fixed_cost,
            'bep_monthly_sales': bep_monthly_sales,
            'bep_turns_per_room': bep_turns_per_room,
            'bep_monthly_users': bep_monthly_teams * 4,
            'bep_daily_users': bep_daily_users,
            'monthly_operating_profit_moderate': op_mod,
            'profit_margin_moderate': scenarios['moderate']['profit_margin'],
            'payback_months': payback_months_mod,
            'staff3_operating_profit': staff3_op_mod,
            'staff3_payback_months': staff3_payback,
            'staff3_bep_turns': staff3_bep_turns
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
