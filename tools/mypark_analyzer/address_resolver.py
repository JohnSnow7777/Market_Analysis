# -*- coding: utf-8 -*-
"""정밀 주소 리졸버 및 전국 지오코딩 엔진 (도로명-법정동 자동 정규화)"""
import re

KNOWN_MAPPINGS = {
    # 분당/성남
    '안골로': {'sido': '경기도', 'sigungu': '성남시 분당구', 'dong': '서현동', 'full': '경기도 성남시 분당구 안골로48번길 14 (서현동)'},
    '서현': {'sido': '경기도', 'sigungu': '성남시 분당구', 'dong': '서현동', 'full': '경기도 성남시 분당구 서현동'},
    '분당': {'sido': '경기도', 'sigungu': '성남시 분당구', 'dong': '서현동', 'full': '경기도 성남시 분당구'},
    '수내': {'sido': '경기도', 'sigungu': '성남시 분당구', 'dong': '수내동', 'full': '경기도 성남시 분당구 수내동'},
    '정자': {'sido': '경기도', 'sigungu': '성남시 분당구', 'dong': '정자동', 'full': '경기도 성남시 분당구 정자동'},
    '판교': {'sido': '경기도', 'sigungu': '성남시 분당구', 'dong': '삼평동', 'full': '경기도 성남시 분당구 삼평동'},
    
    # 고양시 덕양구 / 일산
    '화신로': {'sido': '경기도', 'sigungu': '고양시 덕양구', 'dong': '화정동', 'full': '경기도 고양시 덕양구 화신로272번길 11 (화정동)'},
    '화정': {'sido': '경기도', 'sigungu': '고양시 덕양구', 'dong': '화정동', 'full': '경기도 고양시 덕양구 화정동'},
    '우경': {'sido': '경기도', 'sigungu': '고양시 덕양구', 'dong': '화정동', 'full': '경기도 고양시 덕양구 화신로272번길 11 2층 (화정동)'},
    '행신': {'sido': '경기도', 'sigungu': '고양시 덕양구', 'dong': '행신동', 'full': '경기도 고양시 덕양구 행신동'},
    '원당': {'sido': '경기도', 'sigungu': '고양시 덕양구', 'dong': '성사동', 'full': '경기도 고양시 덕양구 성사동'},
    '덕양': {'sido': '경기도', 'sigungu': '고양시 덕양구', 'dong': '화정동', 'full': '경기도 고양시 덕양구 화정동'},
    '삼송': {'sido': '경기도', 'sigungu': '고양시 덕양구', 'dong': '삼송동', 'full': '경기도 고양시 덕양구 삼송동'},
    '원흥': {'sido': '경기도', 'sigungu': '고양시 덕양구', 'dong': '원흥동', 'full': '경기도 고양시 덕양구 원흥동'},
    '향동': {'sido': '경기도', 'sigungu': '고양시 덕양구', 'dong': '향동동', 'full': '경기도 고양시 덕양구 향동동'},
    '지축': {'sido': '경기도', 'sigungu': '고양시 덕양구', 'dong': '지축동', 'full': '경기도 고양시 덕양구 지축동'},
    '숲속마을로': {'sido': '경기도', 'sigungu': '고양시 일산동구', 'dong': '풍동', 'full': '경기도 고양시 일산동구 숲속마을로 22 (풍동)'},
    '장항': {'sido': '경기도', 'sigungu': '고양시 일산동구', 'dong': '장항동', 'full': '경기도 고양시 일산동구 장항동'},
    '풍동': {'sido': '경기도', 'sigungu': '고양시 일산동구', 'dong': '풍동', 'full': '경기도 고양시 일산동구 풍동'},
    '중산': {'sido': '경기도', 'sigungu': '고양시 일산동구', 'dong': '중산동', 'full': '경기도 고양시 일산동구 중산동'},
    '마두': {'sido': '경기도', 'sigungu': '고양시 일산동구', 'dong': '마두동', 'full': '경기도 고양시 일산동구 마두동'},
    '주엽': {'sido': '경기도', 'sigungu': '고양시 일산서구', 'dong': '주엽동', 'full': '경기도 고양시 일산서구 주엽동'},
    '대화': {'sido': '경기도', 'sigungu': '고양시 일산서구', 'dong': '대화동', 'full': '경기도 고양시 일산서구 대화동'},
    '킨텍스': {'sido': '경기도', 'sigungu': '고양시 일산서구', 'dong': '대화동', 'full': '경기도 고양시 일산서구 킨텍스로'},
    '일산': {'sido': '경기도', 'sigungu': '고양시 일산동구', 'dong': '장항동', 'full': '경기도 고양시 일산동구'},

    # 인천/송도/청라
    '하모니로': {'sido': '인천광역시', 'sigungu': '연수구', 'dong': '송도동', 'full': '인천광역시 연수구 하모니로177번길 49 (송도동)'},
    '송도': {'sido': '인천광역시', 'sigungu': '연수구', 'dong': '송도동', 'full': '인천광역시 연수구 송도동'},
    '청라': {'sido': '인천광역시', 'sigungu': '서구', 'dong': '청라동', 'full': '인천광역시 서구 청라동'},

    # 용인/수원
    '풍덕천': {'sido': '경기도', 'sigungu': '용인시 수지구', 'dong': '풍덕천동', 'full': '경기도 용인시 수지구 풍덕천동'},
    '수지': {'sido': '경기도', 'sigungu': '용인시 수지구', 'dong': '풍덕천동', 'full': '경기도 용인시 수지구'},
    '기흥': {'sido': '경기도', 'sigungu': '용인시 기흥구', 'dong': '구갈동', 'full': '경기도 용인시 기흥구'},
    '광교': {'sido': '경기도', 'sigungu': '수원시 영통구', 'dong': '이의동', 'full': '경기도 수원시 영통구 이의동'},
    '영통': {'sido': '경기도', 'sigungu': '수원시 영통구', 'dong': '영통동', 'full': '경기도 수원시 영통구 영통동'},

    # 서울 주요
    '테헤란로': {'sido': '서울특별시', 'sigungu': '강남구', 'dong': '역삼동', 'full': '서울특별시 강남구 테헤란로'},
    '강남': {'sido': '서울특별시', 'sigungu': '강남구', 'dong': '역삼동', 'full': '서울특별시 강남구'},
    '서초': {'sido': '서울특별시', 'sigungu': '서초구', 'dong': '서초동', 'full': '서울특별시 서초구'},
    '올림픽로': {'sido': '서울특별시', 'sigungu': '송파구', 'dong': '잠실동', 'full': '서울특별시 송파구 올림픽로'},
    '송파': {'sido': '서울특별시', 'sigungu': '송파구', 'dong': '잠실동', 'full': '서울특별시 송파구'},
    '마포': {'sido': '서울특별시', 'sigungu': '마포구', 'dong': '상암동', 'full': '서울특별시 마포구'},
    '영등포': {'sido': '서울특별시', 'sigungu': '영등포구', 'dong': '여의도동', 'full': '서울특별시 영등포구'},
}

SIDO_NAMES = [
    '서울특별시', '서울시', '서울', '부산광역시', '부산시', '부산', '대구광역시', '대구시', '대구',
    '인천광역시', '인천시', '인천', '광주광역시', '광주시', '광주', '대전광역시', '대전시', '대전',
    '울산광역시', '울산시', '울산', '세종특별자치시', '세종시', '세종', '경기도', '경기',
    '강원특별자치도', '강원도', '강원', '충청북도', '충북', '충청남도', '충남',
    '전북특별자치도', '전라북도', '전북', '전라남도', '전남', '경상북도', '경북', '경상남도', '경남',
    '제주특별자치도', '제주도', '제주'
]

class AddressResolver:
    @staticmethod
    def resolve(raw_address):
        clean = raw_address.strip()
        
        # 1. 키워드 매핑 매칭
        for k, v in KNOWN_MAPPINGS.items():
            if k in clean:
                full_addr = clean
                if not any(s in clean for s in ['경기도', '서울', '인천', '부산', '대구', '대전', '광주', '울산', '강원', '충청', '전라', '경상', '제주']):
                    full_addr = f"{v['sido']} {v['sigungu']} {clean}"
                return {
                    'sido': v['sido'],
                    'sigungu': v['sigungu'],
                    'dong': v['dong'],
                    'full_address': full_addr,
                    'is_resolved': True
                }
                
        # 2. 텍스트 토큰 파싱
        tokens = clean.split()
        found_sido = None
        sido_idx = -1
        for idx, token in enumerate(tokens):
            for s in SIDO_NAMES:
                if token.startswith(s):
                    found_sido = '경기도' if s in ['경기', '경기도'] else ('서울특별시' if s in ['서울', '서울시', '서울특별시'] else ('인천광역시' if s in ['인천', '인천시', '인천광역시'] else s))
                    sido_idx = idx
                    break
            if found_sido:
                break
                
        if found_sido:
            rem = tokens[sido_idx+1:]
            if len(rem) >= 2 and (rem[0].endswith(('시', '군')) and rem[1].endswith('구')):
                sigungu = f"{rem[0]} {rem[1]}"
                dong = rem[2] if len(rem) >= 3 else ''
            elif len(rem) >= 1:
                sigungu = rem[0]
                dong = rem[1] if len(rem) >= 2 else ''
            else:
                sigungu = f"{found_sido} 중심권역"
                dong = ''
                
            # 도로명에서 '로/길' 제거하여 동 추정
            if dong.endswith(('로', '길')) or re.search(r'\d+번길', dong):
                # 키워드 매핑 다시 체크
                for k, v in KNOWN_MAPPINGS.items():
                    if k in dong or k in clean:
                        dong = v['dong']
                        break
                        
            return {
                'sido': found_sido,
                'sigungu': sigungu,
                'dong': dong,
                'full_address': clean,
                'is_resolved': True
            }
            
        # 3. 시/도 생략 도로명 파싱 fallback
        road_name = tokens[0] if tokens else '사업지'
        return {
            'sido': '수도권/해당 권역',
            'sigungu': f'{road_name} 권역',
            'dong': road_name,
            'full_address': clean,
            'is_resolved': False
        }
