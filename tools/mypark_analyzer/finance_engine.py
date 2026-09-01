# -*- coding: utf-8 -*-
"""재무 타당성 분석 및 3대 시나리오 손익/BEP/ROI 계산 엔진 (SSOT 3.19억원 & 7,000원 모델)"""
from .config import DEFAULT_SETTINGS

class FinanceEngine:
    """재무 모델링 엔진 (SSOT 기준)"""

    @staticmethod
    def calculate_investment(rooms=10, area_pyeong=120):
        simulator_cost = rooms * DEFAULT_SETTINGS['simulator_unit_price'] # 1.5억
        interior_cost = area_pyeong * DEFAULT_SETTINGS['interior_cost_per_pyeong']
        # 냉난방 설비는 기존 상가 설비 승계 여부에 따라 유무가 갈리는 선택 항목이라
        # 총 투자금 확정치에는 포함하지 않고, 참고용 별도 안내로만 제공한다.
        hvac_cost_optional = DEFAULT_SETTINGS['hvac_cost']
        signage_cost = DEFAULT_SETTINGS['signage_cost']
        furniture_cost = DEFAULT_SETTINGS['furniture_cost']
        supplies_cost = DEFAULT_SETTINGS['supplies_cost']
        other_facilities = signage_cost + furniture_cost + supplies_cost

        total_capex = simulator_cost + interior_cost + other_facilities

        return {
            'rooms': rooms,
            'area_pyeong': area_pyeong,
            'simulator_unit_price': DEFAULT_SETTINGS['simulator_unit_price'],
            'simulator_cost': simulator_cost,
            'interior_cost_per_pyeong': DEFAULT_SETTINGS['interior_cost_per_pyeong'],
            'interior_cost': interior_cost,
            'hvac_cost_optional': hvac_cost_optional,
            'signage_cost': signage_cost,
            'furniture_cost': furniture_cost,
            'supplies_cost': supplies_cost,
            'other_facilities': other_facilities,
            'subtotal_capex': total_capex,
            'total_capex': total_capex
        }

    @staticmethod
    def calculate_monthly_scenario(rooms=10, monthly_rent=4600000, staff_count=1, scenario_type='moderate', regional_demand_multiplier=1.0):
        game_fee = DEFAULT_SETTINGS['game_price_18hole']
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
        
        # 비용 구조 (SSOT config DEFAULT_SETTINGS 대괄호 참조)
        labor_cost = staff_count * DEFAULT_SETTINGS['labor_cost_manager']
        rent_cost = monthly_rent
        cost_goods = int(goods_revenue * DEFAULT_SETTINGS['cost_rate_goods'])
        cost_beverage = int(beverage_revenue * DEFAULT_SETTINGS['cost_rate_beverage'])
        card_fee = int(total_revenue * DEFAULT_SETTINGS['card_fee_rate'])
        store_ops_cost = DEFAULT_SETTINGS['store_ops_monthly']
        pos_telecom = DEFAULT_SETTINGS['pos_telecom_monthly']
        marketing_cost = DEFAULT_SETTINGS['marketing_monthly']
        
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
            'fnb_revenue': beverage_revenue,
            'cafe_revenue': beverage_revenue,
            'total_revenue': total_revenue,
            'annual_revenue': total_revenue * 12,
            'labor_cost': labor_cost,
            'rent_cost': rent_cost,
            'cost_goods': cost_goods,
            'goods_cost': cost_goods,
            'cost_beverage': cost_beverage,
            'fnb_cost': cost_beverage,
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

        # [2026-09-01] 지역수요배율(reg_mult) 제거: 보수적 시나리오(3회전) 자체가
        # 이미 최소 가정인데, 여기에 시니어 인구 기준 배율(최저 0.72배)을 추가로
        # 곱해 같은 '수요가 약함'을 이중으로 할인하던 문제가 있었다. 시나리오
        # 3단계(보수/보편/긍정) 하나만으로 수요 범위를 표현한다.
        scenarios = {
            'conservative': FinanceEngine.calculate_monthly_scenario(rooms, monthly_rent, staff_count, 'conservative'),
            'moderate': FinanceEngine.calculate_monthly_scenario(rooms, monthly_rent, staff_count, 'moderate'),
            'optimistic': FinanceEngine.calculate_monthly_scenario(rooms, monthly_rent, staff_count, 'optimistic'),
        }
        
        # 월 고정비 (점주 1인 상주 250만 + 임대료 + 운영비 180만 + 마케팅 50만)
        fixed_cost = (staff_count * DEFAULT_SETTINGS['labor_cost_manager']) + monthly_rent + DEFAULT_SETTINGS['store_ops_monthly'] + DEFAULT_SETTINGS['pos_telecom_monthly'] + DEFAULT_SETTINGS['marketing_monthly']
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
        # 초고가 임대료 상권(예: 강남·해운대 프라임 상권)은 보수적 시나리오(3회전) 매출로
        # 고정비를 못 덮어 월 순익이 음수가 될 수 있다. 이 경우 99.0개월 같은 무의미한
        # 숫자를 그대로 보여주면 안 되므로, 호출부에서 이 플래그로 분기해 캐베앗을 띄운다.
        inv['conservative_viable'] = op_con > 0
        
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

        # 5개년 누적 및 연차별 요약 데이터 (보편적 시나리오 기준)
        mod_5y = forecast_5y.get('moderate', [])
        years_summary = []
        cum_profit = 0
        tot_5yr_rev = 0
        tot_5yr_cost = 0
        tot_5yr_profit = 0
        for y in mod_5y:
            cum_profit += y['operating_profit']
            tot_5yr_rev += y['total_revenue']
            tot_5yr_cost += y['total_cost']
            tot_5yr_profit += y['operating_profit']
            years_summary.append({
                'year': y['year'],
                'revenue': y['total_revenue'],
                'cost': y['total_cost'],
                'profit': y['operating_profit'],
                'cumulative_profit': cum_profit
            })
            
        five_year = {
            'years': years_summary,
            'total_5yr_revenue': tot_5yr_rev,
            'total_5yr_cost': tot_5yr_cost,
            'total_5yr_profit': tot_5yr_profit
        }

        return {
            'investment': inv,
            'monthly_scenarios': scenarios,
            'forecast_5year': forecast_5y,
            'five_year': five_year,
            'staff_count': staff_count,
            'monthly_rent': monthly_rent,
            'area_pyeong': area_pyeong,
            'rooms': rooms,
            'owner_operated': inv['owner_operated']
        }
