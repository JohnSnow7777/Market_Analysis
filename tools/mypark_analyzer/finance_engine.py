# -*- coding: utf-8 -*-
"""정밀 재무 타당성 및 3대 시나리오 손익 계산 엔진"""
from .config import DEFAULT_SETTINGS, SCENARIO_CONFIG

class FinanceEngine:
    """마이파크 재무 모델링 및 5개년 손익/BEP 시뮬레이터"""
    
    @staticmethod
    def calculate_scenario_monthly(scenario_key, rooms=12, monthly_rent=5000000, staff_count=4):
        cfg = SCENARIO_CONFIG[scenario_key]
        price = DEFAULT_SETTINGS['game_price_18hole']
        
        # 1. 타석 이용료 및 이용자 수
        avg_daily_users = cfg['avg_daily_users_per_room'] * rooms
        monthly_users = int(avg_daily_users * 30)
        room_revenue = monthly_users * price
        
        # 2. 부가 매출
        goods_revenue = int(room_revenue * DEFAULT_SETTINGS['ratio_goods'])
        cafe_revenue = int(room_revenue * DEFAULT_SETTINGS['ratio_cafe'])
        lesson_revenue = int(room_revenue * DEFAULT_SETTINGS['ratio_lesson'])
        total_revenue = room_revenue + goods_revenue + cafe_revenue + lesson_revenue
        
        # 3. 운영 비용
        staff = staff_count if staff_count else max(2, int(rooms / 3))
        labor_cost = staff * DEFAULT_SETTINGS['labor_cost_per_person']
        rent_cost = monthly_rent if monthly_rent else DEFAULT_SETTINGS['default_monthly_rent']
        
        goods_cost = int(goods_revenue * DEFAULT_SETTINGS['cost_rate_goods'])
        cafe_cost = int(cafe_revenue * DEFAULT_SETTINGS['cost_rate_cafe'])
        lesson_cost = int(lesson_revenue * DEFAULT_SETTINGS['cost_rate_lesson'])
        card_fee = int(total_revenue * DEFAULT_SETTINGS['card_fee_rate'])
        
        consumables = int(rooms * (DEFAULT_SETTINGS['sensor_consumables_monthly']))
        utilities = int(rooms * (DEFAULT_SETTINGS['sensor_utilities_monthly']))
        telecom = DEFAULT_SETTINGS['monthly_telecom']
        welfare = DEFAULT_SETTINGS['monthly_welfare']
        maintenance = DEFAULT_SETTINGS['monthly_maintenance']
        store_ops_cost = consumables + utilities + telecom + welfare + maintenance
        
        air_cleaner = int((rooms / 5.0) * DEFAULT_SETTINGS['monthly_air_cleaner_per_5rooms']) if rooms >= 5 else DEFAULT_SETTINGS['monthly_air_cleaner_per_5rooms']
        water_purifier = DEFAULT_SETTINGS['monthly_water_purifier']
        insurance = DEFAULT_SETTINGS['monthly_insurance']
        rental_cost = air_cleaner + water_purifier + insurance
        
        marketing_cost = DEFAULT_SETTINGS['monthly_marketing']
        
        total_cost = (labor_cost + rent_cost + goods_cost + cafe_cost + lesson_cost + 
                      card_fee + store_ops_cost + rental_cost + marketing_cost)
        
        operating_profit = total_revenue - total_cost
        op_margin = (operating_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0
        
        return {
            'scenario_name': cfg['name'],
            'scenario_name_en': cfg['name_en'],
            'daily_users': int(avg_daily_users),
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
            'consumables': consumables,
            'utilities': utilities,
            'telecom': telecom,
            'welfare': welfare,
            'maintenance': maintenance,
            'rental_cost': rental_cost,
            'air_cleaner': air_cleaner,
            'water_purifier': water_purifier,
            'insurance': insurance,
            'marketing_cost': marketing_cost,
            'total_cost': total_cost,
            'operating_profit': operating_profit,
            'op_margin': op_margin,
            'annual_revenue': total_revenue * 12,
            'annual_cost': total_cost * 12,
            'annual_operating_profit': operating_profit * 12
        }

    @staticmethod
    def calculate_5year_forecast(scenario_key, rooms=12, monthly_rent=5000000, staff_count=4):
        base = FinanceEngine.calculate_scenario_monthly(scenario_key, rooms, monthly_rent, staff_count)
        growth = DEFAULT_SETTINGS['annual_growth_rate']
        
        years = []
        for i in range(5):
            year_label = f'N+{i+1}년'
            factor = (1.0 + growth) ** i
            
            y_room_rev = int(base['room_revenue'] * 12 * factor)
            y_goods_rev = int(base['goods_revenue'] * 12 * factor)
            y_cafe_rev = int(base['cafe_revenue'] * 12 * factor)
            y_lesson_rev = int(base['lesson_revenue'] * 12 * factor)
            y_total_rev = y_room_rev + y_goods_rev + y_cafe_rev + y_lesson_rev
            
            y_labor = base['labor_cost'] * 12
            y_rent = base['rent_cost'] * 12
            y_goods_cost = int(y_goods_rev * DEFAULT_SETTINGS['cost_rate_goods'])
            y_cafe_cost = int(y_cafe_rev * DEFAULT_SETTINGS['cost_rate_cafe'])
            y_lesson_cost = int(y_lesson_rev * DEFAULT_SETTINGS['cost_rate_lesson'])
            y_card_fee = int(y_total_rev * DEFAULT_SETTINGS['card_fee_rate'])
            y_store_ops = base['store_ops_cost'] * 12
            y_rental = base['rental_cost'] * 12
            y_marketing = base['marketing_cost'] * 12
            
            y_total_cost = (y_labor + y_rent + y_goods_cost + y_cafe_cost + 
                            y_lesson_cost + y_card_fee + y_store_ops + y_rental + y_marketing)
            y_op = y_total_rev - y_total_cost
            
            years.append({
                'year': year_label,
                'room_revenue': y_room_rev,
                'goods_revenue': y_goods_rev,
                'cafe_revenue': y_cafe_rev,
                'lesson_revenue': y_lesson_rev,
                'total_revenue': y_total_rev,
                'labor_cost': y_labor,
                'rent_cost': y_rent,
                'goods_cost': y_goods_cost,
                'cafe_cost': y_cafe_cost,
                'lesson_cost': y_lesson_cost,
                'card_fee': y_card_fee,
                'store_ops_cost': y_store_ops,
                'rental_cost': y_rental,
                'marketing_cost': y_marketing,
                'total_cost': y_total_cost,
                'operating_profit': y_op
            })
            
        return years

    @staticmethod
    def get_full_financial_analysis(rooms=10, monthly_rent=5000000, staff_count=3, area_pyeong=120):
        actual_rent = monthly_rent if monthly_rent else DEFAULT_SETTINGS['default_monthly_rent']
        actual_rooms = rooms if rooms else DEFAULT_SETTINGS['default_rooms']
        actual_staff = staff_count if staff_count else DEFAULT_SETTINGS['default_staff_count']
        actual_area = area_pyeong if area_pyeong else DEFAULT_SETTINGS['default_area_pyeong']
        
        conservative_m = FinanceEngine.calculate_scenario_monthly('conservative', actual_rooms, actual_rent, actual_staff)
        moderate_m = FinanceEngine.calculate_scenario_monthly('moderate', actual_rooms, actual_rent, actual_staff)
        optimistic_m = FinanceEngine.calculate_scenario_monthly('optimistic', actual_rooms, actual_rent, actual_staff)
        
        conservative_5y = FinanceEngine.calculate_5year_forecast('conservative', actual_rooms, actual_rent, actual_staff)
        moderate_5y = FinanceEngine.calculate_5year_forecast('moderate', actual_rooms, actual_rent, actual_staff)
        optimistic_5y = FinanceEngine.calculate_5year_forecast('optimistic', actual_rooms, actual_rent, actual_staff)
        
        capex_equipment = actual_rooms * 20000000
        capex_interior = int(actual_area * 1300000)
        capex_etc = 30000000
        deposit = actual_rent * 10
        total_capex = capex_equipment + capex_interior + capex_etc
        
        fixed_cost = moderate_m['labor_cost'] + moderate_m['rent_cost'] + moderate_m['store_ops_cost'] + moderate_m['rental_cost'] + moderate_m['marketing_cost']
        vc_ratio = (moderate_m['goods_cost'] + moderate_m['cafe_cost'] + moderate_m['lesson_cost'] + moderate_m['card_fee']) / moderate_m['total_revenue']
        bep_monthly_sales = int(fixed_cost / (1.0 - vc_ratio))
        bep_daily_users = int(bep_monthly_sales / (DEFAULT_SETTINGS['game_price_18hole'] * 1.18 * 30))
        bep_turns_per_room = round(bep_daily_users / rooms, 2)
        
        payback_months_mod = round((total_capex / (moderate_m['operating_profit'])) if moderate_m['operating_profit'] > 0 else 99, 1)
        payback_months_cons = round((total_capex / (conservative_m['operating_profit'])) if conservative_m['operating_profit'] > 0 else 99, 1)
        
        return {
            'rooms': rooms,
            'monthly_rent': monthly_rent,
            'staff_count': staff_count,
            'monthly_scenarios': {
                'conservative': conservative_m,
                'moderate': moderate_m,
                'optimistic': optimistic_m
            },
            'forecast_5year': {
                'conservative': conservative_5y,
                'moderate': moderate_5y,
                'optimistic': optimistic_5y
            },
            'investment': {
                'capex_equipment': capex_equipment,
                'capex_interior': capex_interior,
                'capex_etc': capex_etc,
                'deposit': deposit,
                'total_capex': total_capex,
                'total_budget': total_capex + deposit,
                'bep_monthly_sales': bep_monthly_sales,
                'bep_daily_users': bep_daily_users,
                'bep_turns_per_room': bep_turns_per_room,
                'payback_months_moderate': payback_months_mod,
                'payback_months_conservative': payback_months_cons
            }
        }
