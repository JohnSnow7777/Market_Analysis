# -*- coding: utf-8 -*-
"""지리 정보 및 건축/입지 물리적 적합성 분석 모듈 (현장 실측 체크리스트 기반)"""
from .config import DEFAULT_SETTINGS
from .address_resolver import AddressResolver

class GeoEngine:
    """주소 정밀 지오코딩 및 건축 출점 기준 분석"""
    
    @staticmethod
    def estimate_smart_defaults(address, rooms=None, monthly_rent=None, area_pyeong=None, staff_count=None):
        auto_rooms = int(rooms) if (rooms and int(rooms) > 0) else DEFAULT_SETTINGS['default_rooms']
        
        if auto_rooms == 10:
            recommended_area = DEFAULT_SETTINGS['default_area_pyeong']
        else:
            recommended_area = int(auto_rooms * 10.0 + 20)
        auto_area = int(area_pyeong) if (area_pyeong and int(area_pyeong) > 0) else recommended_area
        
        # 권역별 평당 월 임대료 시세 추정
        rent_per_pyeong = 45000
        if any(k in address for k in ['강남', '서초', '송파', '용산', '마포', '영등포']):
            rent_per_pyeong = 70000
        elif any(k in address for k in ['분당', '판교', '서현', '정자', '성남', '일산', '고양', '송도', '연수', '수지', '용인', '수원', '영통', '광교', '하남', '동탄', '안양', '평촌']):
            rent_per_pyeong = 45000
        elif any(k in address for k in ['부산', '대구', '대전', '광주', '울산', '세종']):
            rent_per_pyeong = 38000
        else:
            rent_per_pyeong = 32000
            
        estimated_rent = int(auto_area * rent_per_pyeong)
        estimated_rent = round(estimated_rent, -5)
        auto_rent = int(monthly_rent) if (monthly_rent and int(monthly_rent) > 0) else estimated_rent
        
        if auto_rooms <= 6:
            rec_staff = 2
        elif auto_rooms <= 10:
            rec_staff = 3
        else:
            rec_staff = 4
        auto_staff = int(staff_count) if (staff_count and int(staff_count) > 0) else rec_staff
        
        return {
            'rooms': auto_rooms,
            'area_pyeong': auto_area,
            'monthly_rent': auto_rent,
            'staff_count': auto_staff,
            'rent_per_pyeong': rent_per_pyeong,
            'is_auto_estimated': (rooms is None or monthly_rent is None or area_pyeong is None or staff_count is None)
        }

    @staticmethod
    def analyze_site(address, building_name=None, area_pyeong=None, rooms=None, monthly_rent=None, staff_count=None):
        resolved = AddressResolver.resolve(address)
        smart = GeoEngine.estimate_smart_defaults(address, rooms, monthly_rent, area_pyeong, staff_count)
        
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
            
            # 단정적 표현 완전 제거 -> 출점 기준 및 현장 실측 체크리스트로 객관화
            'floor_recommendation': '지상 2~3층 권장 (또는 쾌적한 지하 1층 상가)',
            'clear_height_spec': '권장 유효 층고 2.8m 이상 (※ 보/배관 간섭 현장 실측 필수)',
            'parking_spec': f"타석당 1~1.2대(약 {max(8, int(smart['rooms']*1.2))}대 이상) 주차 공간 확보 권장 (※ 건축물대장 확인 필요)",
            'accessibility_spec': '시니어 고객 특성상 승강기 완비 또는 완만한 접근 동선 점검 권장',
            'zoning_spec': '제2종 근린생활시설 또는 운동시설 (※ 지자체 체육시설 인허가 및 건축물 용도 검토 필요)',
            'electrical_spec': f"계약전력 최소 {max(25, smart['rooms']*3)}kW 이상 (타석당 1.5kW + 냉난방)",
            'building_use_spec': '제2종 근린생활시설 또는 운동시설 (※ 건축물대장 용도 확인 필요)'
        }
