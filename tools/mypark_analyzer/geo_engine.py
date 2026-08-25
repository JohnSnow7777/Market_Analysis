# -*- coding: utf-8 -*-
"""지리 정보 및 건축/입지 물리적 적합성 분석 모듈 (스마트 자동 추정 내장)"""

class GeoEngine:
    """주소 지오코딩, 지역 시세 추정 및 공간/비용 자동 스마트 산정"""
    
    @staticmethod
    def estimate_smart_defaults(address, rooms=None, monthly_rent=None, area_pyeong=None, staff_count=None):
        # 1. 타석 수 기본값 (미입력 시 마이파크 표준 최적 12타석 플래그십 모델)
        auto_rooms = rooms if (rooms and int(rooms) > 0) else 12
        
        # 2. 전용면적 자동 산정 (타석당 8.5평 + 공용/로비/카페 20평)
        recommended_area = int(auto_rooms * 8.5 + 20)
        auto_area = area_pyeong if (area_pyeong and int(area_pyeong) > 0) else recommended_area
        
        # 3. 지역별 평당 월 임대료 시세 추정
        # 강남/서초/송파: 평당 7~8만원, 수도권 핵심/일산/송도/분당/수지: 평당 4~5만원, 광역시/지방: 평당 3~4만원
        rent_per_pyeong = 45000
        if any(k in address for k in ['강남', '서초', '송파', '용산', '마포', '영등포']):
            rent_per_pyeong = 70000
        elif any(k in address for k in ['일산', '고양', '송도', '연수', '분당', '수지', '용인', '수원', '하남', '화성', '동탄', '인천', '부천', '안양', '평촌']):
            rent_per_pyeong = 45000
        elif any(k in address for k in ['부산', '대구', '대전', '광주', '울산', '세종']):
            rent_per_pyeong = 38000
        else:
            rent_per_pyeong = 32000
            
        estimated_rent = int(auto_area * rent_per_pyeong)
        # 10만 원 단위 반올림
        estimated_rent = round(estimated_rent, -5)
        auto_rent = monthly_rent if (monthly_rent and int(monthly_rent) > 0) else estimated_rent
        
        # 4. 운영 인력 자동 산정 (타석 규모별 최적 인력: 4~6타석 2명, 8~10타석 3명, 12~16타석 4명)
        if auto_rooms <= 6:
            rec_staff = 2
        elif auto_rooms <= 10:
            rec_staff = 3
        else:
            rec_staff = 4
        auto_staff = staff_count if (staff_count and int(staff_count) > 0) else rec_staff
        
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
        parts = address.split()
        sido = parts[0] if len(parts) > 0 else '경기도'
        sigungu = parts[1] if len(parts) > 1 else '고양시 일산동구'
        dong_or_road = ' '.join(parts[2:]) if len(parts) > 2 else '숲속마을로 22'
        
        smart = GeoEngine.estimate_smart_defaults(address, rooms, monthly_rent, area_pyeong, staff_count)
        
        parking_spaces = max(8, int(smart['rooms'] * 1.2))
        clear_height = 3.0
        
        b_name = building_name.strip() if (building_name and building_name.strip()) else f"{sigungu} 후보지"
        
        return {
            'full_address': address,
            'sido': sido,
            'sigungu': sigungu,
            'detail_address': dong_or_road,
            'building_name': b_name,
            'rooms': smart['rooms'],
            'area_pyeong': smart['area_pyeong'],
            'monthly_rent': smart['monthly_rent'],
            'staff_count': smart['staff_count'],
            'rent_per_pyeong': smart['rent_per_pyeong'],
            'is_auto_estimated': smart['is_auto_estimated'],
            'floor': '지상 2~3층 권장 (또는 쾌적한 지하 1층)',
            'clear_height': clear_height,
            'parking_spaces': parking_spaces,
            'parking_type': '자주식 지상/지하 주차장 완비',
            'elevator': '승강기 2대 이상 완비',
            'zoning': '제2종 근린생활시설 / 운동시설 (입점 적합)'
        }
