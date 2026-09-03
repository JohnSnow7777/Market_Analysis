# -*- coding: utf-8 -*-
"""지리 정보 및 건축/입지 물리적 적합성 분석 모듈 (현장 실측 체크리스트 기반)"""
from .config import (DEFAULT_SETTINGS, classify_region_tier,
                     TIER_PRIME, TIER_METRO, TIER_MID_CITY, TIER_RURAL)
from .address_resolver import AddressResolver

class GeoEngine:
    """주소 정밀 지오코딩 및 건축 출점 기준 분석"""
    
    @staticmethod
    def estimate_smart_defaults(address, rooms=None, monthly_rent=None, area_pyeong=None, staff_count=None,
                                sigungu='', sido=''):
        auto_rooms = int(rooms) if (rooms and int(rooms) > 0) else DEFAULT_SETTINGS['default_rooms']
        
        if auto_rooms == 10:
            recommended_area = DEFAULT_SETTINGS['default_area_pyeong']
        else:
            recommended_area = int(auto_rooms * 10.0 + 20)
        auto_area = int(area_pyeong) if (area_pyeong and int(area_pyeong) > 0) else recommended_area

        # 권역별 평당 월 임대료 시세 추정.
        # 예전에는 여기서 주소 문자열을 자체 키워드 목록으로 훑었는데, 그 결과
        # (1) 경남 진주시 강남동이 '강남'에 걸려 서울 도심 시세(7만원/평)를 받아
        #     월 임대료가 실제의 두 배 이상으로 잡히고,
        # (2) config의 지역등급과 목록이 서로 달라 같은 주소가 모듈마다 다른
        #     등급을 갖는 문제가 있었다.
        # 이제 지역등급 판정을 config 한 곳(SSoT)에서만 받아 쓴다.
        rent_source_label = None
        _tier = classify_region_tier(address, sigungu, sido)
        rent_per_pyeong = {
            TIER_PRIME: 70000,
            TIER_METRO: 45000,
            TIER_MID_CITY: 38000,
            TIER_RURAL: 32000,
        }.get(_tier, 38000)

        estimated_rent = int(auto_area * rent_per_pyeong)
        estimated_rent = round(estimated_rent, -5)
        auto_rent = int(monthly_rent) if (monthly_rent and int(monthly_rent) > 0) else estimated_rent
        
        # 기본 표준: 점주(실장) 1인 상주 운영 체제 (엑셀 원본 일치)
        rec_staff = 1
        auto_staff = int(staff_count) if (staff_count and int(staff_count) > 0) else rec_staff
        
        return {
            'rooms': auto_rooms,
            'area_pyeong': auto_area,
            'monthly_rent': auto_rent,
            'staff_count': auto_staff,
            'rent_per_pyeong': rent_per_pyeong,
            'is_auto_estimated': (rooms is None or monthly_rent is None or area_pyeong is None or staff_count is None),
            'rent_is_estimated': not (monthly_rent and int(monthly_rent) > 0),
            'rent_source_label': rent_source_label
        }

    @staticmethod
    def analyze_site(address, building_name=None, area_pyeong=None, rooms=None, monthly_rent=None,
                     staff_count=None, special_notes=None, resolved=None):
        # resolved를 받으면 그대로 쓴다. 모듈마다 다시 판정하면 지도 API가
        # 한 번만 실패해도 이 모듈만 다른 지역으로 계산하게 된다.
        resolved = resolved or AddressResolver.resolve(address)
        smart = GeoEngine.estimate_smart_defaults(
            address, rooms, monthly_rent, area_pyeong, staff_count,
            sigungu=resolved.get('sigungu', ''), sido=resolved.get('sido', ''))
        
        b_name = building_name.strip() if (building_name and building_name.strip()) else f"{resolved['sigungu']} 매장"
        
        return {
            'full_address': resolved['full_address'],
            'sido': resolved['sido'],
            'sigungu': resolved['sigungu'],
            'dong': resolved['dong'],
            'building_name': b_name,
            'rooms': smart['rooms'],
            'area_pyeong': smart['area_pyeong'],
            'monthly_rent': smart['monthly_rent'],
            'staff_count': smart['staff_count'],
            'rent_per_pyeong': smart['rent_per_pyeong'],
            'is_auto_estimated': smart['is_auto_estimated'],
            'rent_is_estimated': smart['rent_is_estimated'],
            'rent_source_label': smart['rent_source_label'],

            # 단정적 표현 완전 제거 -> 출점 기준 및 현장 실측 체크리스트로 객관화
            'floor_recommendation': '지상 2~3층 권장 (또는 쾌적한 지하 1층 상가)',
            'clear_height_spec': '권장 유효 층고 2.8m 이상 (※ 보/배관 간섭 현장 실측 필수)',
            'parking_spec': f"타석당 1~1.2대(약 {max(8, int(smart['rooms']*1.2))}대 이상) 주차 공간 확보 권장 (※ 건축물대장 확인 필요)",
            'accessibility_spec': '시니어 고객 특성상 승강기 완비 또는 완만한 접근 동선 점검 권장',
            'zoning_spec': '제2종 근린생활시설 또는 운동시설 (※ 지자체 체육시설 인허가 및 건축물 용도 검토 필요)',
            'electrical_spec': f"계약전력 최소 {max(25, smart['rooms']*3)}kW 이상 (타석당 1.5kW + 냉난방)",
            'building_use_spec': '제2종 근린생활시설 또는 운동시설 (※ 건축물대장 용도 확인 필요)',
            'special_notes': special_notes.strip() if (special_notes and special_notes.strip()) else ''
        }
