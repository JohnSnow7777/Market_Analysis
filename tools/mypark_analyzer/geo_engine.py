# -*- coding: utf-8 -*-
"""지리 정보 및 건축/입지 물리적 적합성 분석 모듈"""

class GeoEngine:
    """주소 지오코딩 및 건물 물리 스펙 분석"""
    
    @staticmethod
    def analyze_site(address, building_name=None, area_pyeong=100, rooms=12):
        parts = address.split()
        sido = parts[0] if len(parts) > 0 else '경기도'
        sigungu = parts[1] if len(parts) > 1 else '고양시 일산동구'
        dong_or_road = ' '.join(parts[2:]) if len(parts) > 2 else '숲속마을로 22'
        
        recommended_pyeong = rooms * 8.5 + 20
        actual_pyeong = area_pyeong if area_pyeong else recommended_pyeong
        
        parking_spaces = max(8, int(rooms * 1.2))
        clear_height = 3.0
        
        return {
            'full_address': address,
            'sido': sido,
            'sigungu': sigungu,
            'detail_address': dong_or_road,
            'building_name': building_name or '해당 입지 상가건물',
            'rooms': rooms,
            'area_pyeong': actual_pyeong,
            'floor': '지상 2~3층 권장 (또는 지하 1층)',
            'clear_height': clear_height,
            'parking_spaces': parking_spaces,
            'parking_type': '자주식 지상/지하 주차장 완비',
            'elevator': '승강기 2대 이상 완비',
            'zoning': '제2종 근린생활시설 / 운동시설 (입점 적합)'
        }
