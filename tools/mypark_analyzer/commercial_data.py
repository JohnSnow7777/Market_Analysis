# -*- coding: utf-8 -*-
"""상권 및 소상공인 매출/업종/경쟁 분석 모듈"""

BENCHMARK_COMPETITORS = {
    '일산': [
        {
            'name': '레저로 파크골프(일산 풍동점)',
            'address': '경기도 고양시 일산동구 백마로 478 오토갤러리 A동 204,206호',
            'system': '레저로 스크린 파크골프',
            'rooms': 6,
            'features': '오토갤러리 입점, 주차 편리'
        },
        {
            'name': '더조은파크골프(일산 동구점)',
            'address': '경기도 고양시 일산동구 고일로 12 타임시티 3층',
            'system': '더조은 스크린 파크골프',
            'rooms': 9,
            'features': '중형 규모 타석, 동호회 위주'
        },
        {
            'name': '아리 파크골프',
            'address': '경기도 고양시 일산서구 한류월드로 300 원마운트스포츠클럽 7층',
            'system': '온파크 시스템',
            'rooms': 4,
            'features': '원마운트 스포츠클럽 연계'
        },
        {
            'name': '오케이 파크골프 스크린',
            'address': '경기도 고양시 일산서구 중앙로 1496 1층',
            'system': 'GTR 시스템',
            'rooms': 5,
            'features': '1층 로드샵 매장'
        }
    ],
    '송도': [
        {
            'name': '프렌즈스크린 송도형 지점',
            'address': '인천 연수구 하모니로177번길 49 형지판매시설 2층 216~220호',
            'system': '카카오 프렌즈스크린',
            'rooms': 5,
            'features': '역세권 대형 복합 매장'
        },
        {
            'name': '더블에이치 골프아카데미',
            'address': '인천 연수구 하모니로177번길 49 형지판매시설 2층',
            'system': '임팩트 골프 아카데미',
            'rooms': 21,
            'features': '연습 타석 위주 (파크골프 전환 검토)'
        }
    ]
}

class CommercialDataEngine:
    """소상공인 매출 및 상권 분석 데이터 엔진"""
    
    @staticmethod
    def get_commercial_trends(address):
        months = ['25.04', '25.05', '25.06', '25.07', '25.08', '25.09', '25.10', '25.11', '25.12', '26.01', '26.02', '26.03', '26.04']
        
        if '일산' in address or '고양' in address:
            selected_area_sales = [1381, 1467, 1593, 1744, 1630, 1610, 1768, 1781, 1898, 1794, 1783, 1724, 1570]
            dong_avg_sales = [1583, 1555, 1662, 1475, 1610, 1598, 1561, 1382, 1557, 1622, 1563, 1538, 1432]
            city_avg_sales = [2257, 2319, 2316, 2157, 2188, 2326, 2328, 1781, 1622, 1794, 1783, 2376, 2157]
            competitor_list = BENCHMARK_COMPETITORS['일산']
            store_count = 4
            monthly_avg_sales = 15700000
        elif '송도' in address or '연수' in address or '인천' in address:
            selected_area_sales = [2100, 2150, 2200, 2280, 2250, 2310, 2350, 2290, 2400, 2380, 2320, 2306, 2147]
            dong_avg_sales = [1950, 2000, 2050, 2100, 2120, 2150, 2180, 2150, 2200, 2210, 2190, 2180, 2100]
            city_avg_sales = [2300, 2350, 2380, 2400, 2420, 2450, 2480, 2450, 2500, 2520, 2510, 2500, 2480]
            competitor_list = BENCHMARK_COMPETITORS['송도']
            store_count = 20
            monthly_avg_sales = 23060000
        else:
            selected_area_sales = [1600, 1650, 1720, 1800, 1750, 1780, 1850, 1820, 1950, 1920, 1890, 1850, 1780]
            dong_avg_sales = [1500, 1520, 1580, 1620, 1600, 1630, 1670, 1650, 1700, 1710, 1690, 1680, 1620]
            city_avg_sales = [2100, 2150, 2200, 2250, 2230, 2280, 2300, 2280, 2350, 2360, 2340, 2330, 2290]
            competitor_list = [
                {'name': '인근 실내 스크린파크골프 A', 'address': '사업지 반경 1.2km 지점', 'system': '레저로 시스템', 'rooms': 6, 'features': '상가 3층'},
                {'name': '인근 실내 스크린파크골프 B', 'address': '사업지 반경 2.5km 지점', 'system': 'GTR 시스템', 'rooms': 5, 'features': '지하 1층'},
            ]
            store_count = 6
            monthly_avg_sales = 18500000
            
        day_distribution = {
            '월': 32.1, '화': 11.2, '수': 12.5, '목': 13.0, '금': 14.2, '토': 8.5, '일': 8.5,
            '주말평균비중': 61.7, '평일주요비중': '월요일 32.1% (주간 정기 모임)'
        }
        time_distribution = {
            '09~12시': 22.4, '12~15시': 28.6, '15~18시': 19.5, '18~23시': 29.5,
            '주간_10_17시_비중': 65.5, '야간_18_23시_비중': 34.5
        }
        age_distribution = {
            '2030대': 8.5, '40대': 18.2, '50대': 42.8, '60대이상': 30.5,
            '50대이상_비중': 73.3
        }
        
        return {
            'months': months,
            'selected_area_sales': selected_area_sales,
            'dong_avg_sales': dong_avg_sales,
            'city_avg_sales': city_avg_sales,
            'monthly_avg_sales': monthly_avg_sales,
            'store_count': store_count,
            'competitors': competitor_list,
            'day_distribution': day_distribution,
            'time_distribution': time_distribution,
            'age_distribution': age_distribution,
        }
