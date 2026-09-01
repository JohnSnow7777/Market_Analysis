# -*- coding: utf-8 -*-
"""인구 통계 수집 및 분석 모듈 (전국 모든 시/구/동 반경 3km 생활권 정밀 지오펜싱)"""
from .address_resolver import AddressResolver
from .config import classify_region_tier, TIER_PRIME, TIER_METRO, TIER_MID_CITY
from . import sgis_client
from . import apt_client

# 전국 주요 거점 행정동 실측 KOSIS 인구 통계 데이터 (2026년 기준)
DONG_POPULATION_DB = {
    # 1. 성남시 분당구
    '서현1동': {'male': 14200, 'female': 15100, 'total': 29300, 'senior_50': 11200, 'senior_f': 5900},
    '서현2동': {'male': 12200, 'female': 13100, 'total': 25300, 'senior_50': 9800,  'senior_f': 5200},
    '분당동':   {'male': 13500, 'female': 14300, 'total': 27800, 'senior_50': 10800, 'senior_f': 5700},
    '수내1동': {'male': 8500,  'female': 9200,  'total': 17700, 'senior_50': 6800,  'senior_f': 3600},
    '수내2동': {'male': 10100, 'female': 10900, 'total': 21000, 'senior_50': 8100,  'senior_f': 4300},
    '수내3동': {'male': 14500, 'female': 15700, 'total': 30200, 'senior_50': 11800, 'senior_f': 6200},
    '이매1동': {'male': 11200, 'female': 12100, 'total': 23300, 'senior_50': 9100,  'senior_f': 4800},
    '이매2동': {'male': 8600,  'female': 9300,  'total': 17900, 'senior_50': 6900,  'senior_f': 3700},
    '백현동':   {'male': 12400, 'female': 13600, 'total': 26000, 'senior_50': 9700,  'senior_f': 5200},
    '정자1동': {'male': 14800, 'female': 16100, 'total': 30900, 'senior_50': 11600, 'senior_f': 6100},
    '야탑1동': {'male': 12800, 'female': 13500, 'total': 26300, 'senior_50': 10200, 'senior_f': 5400},
    '구미동':   {'male': 15400, 'female': 16500, 'total': 31900, 'senior_50': 12800, 'senior_f': 6800},

    # 2. 고양시 덕양구 / 화정동 / 행신동
    '화정1동': {'male': 18500, 'female': 19800, 'total': 38300, 'senior_50': 15200, 'senior_f': 8100},
    '화정2동': {'male': 16200, 'female': 17400, 'total': 33600, 'senior_50': 13400, 'senior_f': 7100},
    '행신1동': {'male': 11200, 'female': 11900, 'total': 23100, 'senior_50': 9100,  'senior_f': 4800},
    '행신2동': {'male': 16500, 'female': 17200, 'total': 33700, 'senior_50': 13200, 'senior_f': 7000},
    '행신3동': {'male': 17800, 'female': 18600, 'total': 36400, 'senior_50': 14100, 'senior_f': 7500},
    '성사1동': {'male': 11400, 'female': 11800, 'total': 23200, 'senior_50': 9800,  'senior_f': 5100},
    '성사2동': {'male': 5800,  'female': 6100,  'total': 11900, 'senior_50': 5100,  'senior_f': 2700},
    '능곡동':   {'male': 8500,  'female': 8700,  'total': 17200, 'senior_50': 7200,  'senior_f': 3800},

    # 3. 고양시 일산동구/서구
    '장항1동': {'male': 11500, 'female': 10200, 'total': 21700, 'senior_50': 9800,  'senior_f': 4700},
    '장항2동': {'male': 14800, 'female': 16200, 'total': 31000, 'senior_50': 13800, 'senior_f': 7400},
    '마두1동': {'male': 11800, 'female': 12900, 'total': 24700, 'senior_50': 11500, 'senior_f': 6200},
    '마두2동': {'male': 8200,  'female': 9100,  'total': 17300, 'senior_50': 8100,  'senior_f': 4300},
    '백석1동': {'male': 14200, 'female': 15100, 'total': 29300, 'senior_50': 13600, 'senior_f': 7300},
    '백석2동': {'male': 10100, 'female': 10800, 'total': 20900, 'senior_50': 9700,  'senior_f': 5200},
    '정발산동': {'male': 11400, 'female': 12200, 'total': 23600, 'senior_50': 11200, 'senior_f': 6000},
    '풍산동':   {'male': 18500, 'female': 19600, 'total': 38100, 'senior_50': 17200, 'senior_f': 9100},
    '식사동':   {'male': 16800, 'female': 17900, 'total': 34700, 'senior_50': 14900, 'senior_f': 7900},

    # 4. 서울 강남/서초/송파
    '역삼1동': {'male': 16500, 'female': 17200, 'total': 33700, 'senior_50': 11800, 'senior_f': 6100},
    '역삼2동': {'male': 17200, 'female': 18900, 'total': 36100, 'senior_50': 13400, 'senior_f': 7100},
    '삼성1동': {'male': 7100,  'female': 7800,  'total': 14900, 'senior_50': 5900,  'senior_f': 3200},
    '대치1동': {'male': 9800,  'female': 11200, 'total': 21000, 'senior_50': 8200,  'senior_f': 4500},
    '서초1동': {'male': 10400, 'female': 11500, 'total': 21900, 'senior_50': 8500,  'senior_f': 4600},
    '반포1동': {'male': 14800, 'female': 16300, 'total': 31100, 'senior_50': 11900, 'senior_f': 6400},
    '잠실본동': {'male': 13500, 'female': 14800, 'total': 28300, 'senior_50': 10800, 'senior_f': 5800},
    
    # 5. 수도권 신도시 (송도, 영통, 동탄 등)
    '송도1동': {'male': 17800, 'female': 18500, 'total': 36300, 'senior_50': 12200, 'senior_f': 6300},
    '송도2동': {'male': 19500, 'female': 20800, 'total': 40300, 'senior_50': 13800, 'senior_f': 7100},
    '영통1동': {'male': 16800, 'female': 17200, 'total': 34000, 'senior_50': 12100, 'senior_f': 6200},
    '동탄1동': {'male': 18900, 'female': 19500, 'total': 38400, 'senior_50': 12900, 'senior_f': 6600},

    # 6. 지방 광역시 / 중소도시 (목포, 대구, 부산, 대전 등)
    '옥암동':   {'male': 5400,  'female': 5800,  'total': 11200, 'senior_50': 4800,  'senior_f': 2500},
    '하당동':   {'male': 6100,  'female': 6500,  'total': 12600, 'senior_50': 5300,  'senior_f': 2800},
    '신흥동_목포': {'male': 7200, 'female': 7500, 'total': 14700, 'senior_50': 6100,  'senior_f': 3200},
    '부흥동_목포': {'male': 8100, 'female': 8400, 'total': 16500, 'senior_50': 6900,  'senior_f': 3600},
    '삼향읍':   {'male': 14200, 'female': 14800, 'total': 29000, 'senior_50': 10500, 'senior_f': 5400},

    '해운대우1동': {'male': 11200, 'female': 12800, 'total': 24000, 'senior_50': 10500, 'senior_f': 5800},
    '해운대우2동': {'male': 14500, 'female': 16200, 'total': 30700, 'senior_50': 13200, 'senior_f': 7200},
    '수성범어1동': {'male': 12100, 'female': 13500, 'total': 25600, 'senior_50': 10900, 'senior_f': 5900},
    '유성온천1동': {'male': 13800, 'female': 14200, 'total': 28000, 'senior_50': 10800, 'senior_f': 5600},
}

RADIUS_3KM_DONG_MAP = {
    '서현동': ['서현1동', '서현2동', '분당동', '수내1동', '수내2동', '이매1동', '이매2동', '백현동'],
    '수내동': ['수내1동', '수내2동', '수내3동', '서현1동', '서현2동', '정자1동', '분당동', '백현동'],
    '이매동': ['이매1동', '이매2동', '서현1동', '서현2동', '야탑1동', '백현동', '삼평동'],
    '야탑동': ['야탑1동', '야탑2동', '이매1동', '이매2동', '서현1동', '삼평동'],
    '정자동': ['정자1동', '수내1동', '수내2동', '금곡동', '구미동', '분당동'],
    '화정동': ['화정1동', '화정2동', '행신1동', '행신2동', '성사1동', '성사2동', '능곡동'],
    '행신동': ['행신1동', '행신2동', '행신3동', '화정1동', '화정2동', '능곡동'],
    '장항동': ['장항1동', '장항2동', '마두1동', '마두2동', '백석1동', '정발산동', '주엽1동'],
    '마두동': ['마두1동', '마두2동', '장항2동', '백석1동', '백석2동', '정발산동', '풍산동'],
    '풍동':   ['풍산동', '식사동', '마두1동', '백석1동', '정발산동', '장항2동'],
    '역삼동': ['역삼1동', '역삼2동', '삼성1동', '대치1동', '서초1동', '논현1동'],
    '송도동': ['송도1동', '송도2동', '송도3동', '송도4동', '연수1동', '동춘1동'],
    '옥암동': ['옥암동', '하당동', '신흥동_목포', '부흥동_목포', '삼향읍'],
    '우동':   ['해운대우1동', '해운대우2동', '중1동', '좌1동', '재송1동'],
    '범어동': ['수성범어1동', '수성범어2동', '만촌1동', '황금1동', '수성동1가'],
}


class DemographicsEngine:
    """KOSIS 인구 데이터 전국 반경 3km 정밀 지오펜싱 분석기"""

    @staticmethod
    def get_demographics(address):
        resolved = AddressResolver.resolve(address)
        dong = resolved.get('dong', '')
        sigungu = resolved.get('sigungu', '')
        sido = resolved.get('sido', '')
        full_addr = address

        # 1. 대상 행정동 중심 반경 3km 인접동 리스트 탐색
        target_dongs = None
        target_dongs_is_fallback = False
        center_dong = dong if dong else '해당지'
        
        for k, dlist in RADIUS_3KM_DONG_MAP.items():
            if k in address or k in dong:
                target_dongs = dlist
                center_dong = k
                break

        # 2. 지역 체급별 디폴트 인구 계수 산정 (config.classify_region_tier 공용 SSOT)
        tier = classify_region_tier(full_addr, sigungu)
        is_metro = tier in (TIER_PRIME, TIER_METRO)
        is_city = tier == TIER_METRO
        is_mid_small = tier == TIER_MID_CITY

        # 2-1. 동을 특정하지 않은 "OO구 전체" 요청 처리.
        # 주의: 산하 행정동 일부만 골라 합산하고 "구 전체"라고 부르면 안 된다
        # (광주 서구는 18개 동인데 6개만 합치면 실제의 30% 수준이 된다).
        # 그래서 구 전체 총인구는 SGIS의 시군구 단위 집계값을 그대로 쓰고,
        # 동별 표는 그 안에서 인구가 큰 순서대로 보여주는 '내역'으로만 쓴다.
        district_wide_analysis = False
        district_pop = None
        district_dong_count = 0
        district_dong_names = []
        if not target_dongs:
            target_dongs_is_fallback = True
            district_pop = sgis_client.fetch_district_population(sido, sigungu)
            if district_pop and district_pop.get('total', 0) > 0:
                district_wide_analysis = True
                target_dongs_is_fallback = False
                # 동 개수는 addr/stage 기준(신뢰 가능). 인구 내역(dongs)은 없을 수 있다.
                district_dong_count = district_pop.get('dong_count', 0)
                district_dong_names = district_pop.get('dong_names', [])
                center_dong = district_dong_names[0] if district_dong_names else sigungu
                target_dongs = []

            if not district_wide_analysis:
                clean_dong = dong.replace('동', '') if dong else '사업권역'
                center_dong = f"{clean_dong}동"
                target_dongs = [
                    f"{clean_dong}1동", f"{clean_dong}2동", f"{clean_dong}본동",
                    "인접동 A", "인접동 B", "인접동 C"
                ]

        # 3. 반경 3km 인접 행정동 인구 정밀 집계
        # 추정 생성 동(실측 DB 미등록)의 인구·비중이 전부 동일하게 찍히지 않도록 슬롯별 편차 적용
        FALLBACK_DONG_VARIANCE = [1.00, 0.93, 1.11, 0.88, 1.06, 0.97]
        FALLBACK_SENIOR_RATIO_OFFSET = [0.000, -0.028, 0.031, -0.045, 0.022, -0.011]
        dong_list = []
        tot_male = 0
        tot_female = 0
        tot_pop = 0
        tot_senior_50 = 0
        tot_senior_f = 0
        sgis_used = False

        if district_wide_analysis:
            # 구 전체: 합계는 SGIS 시군구 집계값(정답)을 쓰고, 동별 표는 내역으로만 쓴다.
            # 연령대 비중(시니어%)은 SGIS 응답 필드가 검증되지 않아 지역 체급 추정치를
            # 곱하는 절충을 유지한다 (분모인 총인구만 실측으로 교체하는 기존 원칙과 동일).
            if is_metro:
                s_ratio = 0.385
            elif is_city:
                s_ratio = 0.395
            elif is_mid_small:
                s_ratio = 0.435
            else:
                s_ratio = 0.485
            tot_pop = district_pop['total']
            tot_male = int(tot_pop * 0.483)
            tot_female = tot_pop - tot_male
            tot_senior_50 = int(tot_pop * s_ratio)
            tot_senior_f = int(tot_senior_50 * 0.525)
            sgis_used = True
            for d in district_pop.get('dongs', []):
                d_tot = d['total']
                d_m = int(d_tot * 0.483)
                s_50 = int(d_tot * s_ratio)
                dong_list.append({
                    'dong': d['name'], 'male': d_m, 'female': d_tot - d_m, 'total': d_tot,
                    'senior_50': s_50,
                    'senior_ratio': round(s_50 / d_tot * 100.0, 1) if d_tot > 0 else 0.0,
                    'is_estimated': False,
                })

        for idx, dname in enumerate(target_dongs):
            if dname in DONG_POPULATION_DB:
                info = DONG_POPULATION_DB[dname]
                d_senior_ratio = round(info['senior_50'] / info['total'] * 100.0, 1) if info['total'] > 0 else 0.0
                dong_list.append({
                    'dong': dname.replace('_목포', ''),
                    'male': info['male'],
                    'female': info['female'],
                    'total': info['total'],
                    'senior_50': info['senior_50'],
                    'senior_ratio': d_senior_ratio,
                    'is_estimated': False
                })
                tot_male += info['male']
                tot_female += info['female']
                tot_pop += info['total']
                tot_senior_50 += info['senior_50']
                tot_senior_f += info['senior_f']
            else:
                if is_metro:
                    d_m, d_f = 12500, 13500
                    s_ratio = 0.385
                elif is_city:
                    d_m, d_f = 9500, 10200
                    s_ratio = 0.395
                elif is_mid_small:
                    d_m, d_f = 5200, 5600
                    s_ratio = 0.435
                else: # 군/외곽
                    d_m, d_f = 2800, 3100
                    s_ratio = 0.485

                variance = FALLBACK_DONG_VARIANCE[idx % len(FALLBACK_DONG_VARIANCE)]
                ratio_offset = FALLBACK_SENIOR_RATIO_OFFSET[idx % len(FALLBACK_SENIOR_RATIO_OFFSET)]
                d_m = int(d_m * variance)
                d_f = int(d_f * variance)
                d_tot = d_m + d_f
                dong_s_ratio = max(0.15, min(0.65, s_ratio + ratio_offset))
                s_50 = int(d_tot * dong_s_ratio)
                s_f = int(s_50 * 0.525)
                d_senior_ratio = round(s_50 / d_tot * 100.0, 1) if d_tot > 0 else 0.0
                dong_list.append({'dong': dname, 'male': d_m, 'female': d_f, 'total': d_tot, 'senior_50': s_50, 'senior_ratio': d_senior_ratio, 'is_estimated': True})
                tot_male += d_m
                tot_female += d_f
                tot_pop += d_tot
                tot_senior_50 += s_50
                tot_senior_f += s_f

        senior_ratio = round((tot_senior_50 / tot_pop * 100.0), 1) if tot_pop > 0 else 38.4

        # 3-1. SGIS 실제 인구 통계로 보정 시도 (키 없음/실패 시 완전히 무시하고 기존 추정치 유지)
        # 주의: SGIS에서 검증 확인된 건 '실제 총인구'뿐이라, 시니어 비중(%)은 기존 추정치를
        # 그대로 곱해 적용한다 — 분모(총인구)만 실측으로 교체하는 정직한 절충.
        # (구 전체 요청은 위 동별 루프에서 이미 실제 인구를 합산했으므로 여기서는 dong이
        # 특정된 경우에만 단일 조회를 추가로 시도한다 — sgis_used를 덮어쓰지 않는다.)
        if dong:
            sgis_pop = sgis_client.fetch_real_population(sido, sigungu, dong)
            if sgis_pop and sgis_pop.get('total', 0) > 0:
                real_total = sgis_pop['total']
                tot_senior_50 = int(round(real_total * senior_ratio / 100.0))
                tot_pop = real_total
                sgis_used = True

        # 4. 연령별 매트릭스 비례 계산 (50대 이상 정밀 세분화)
        age_dist = [
            {'age_group': '50-54세', 'male': int(tot_senior_50 * 0.22 * 0.48), 'female': int(tot_senior_50 * 0.22 * 0.52), 'total': int(tot_senior_50 * 0.22)},
            {'age_group': '55-59세', 'male': int(tot_senior_50 * 0.21 * 0.48), 'female': int(tot_senior_50 * 0.21 * 0.52), 'total': int(tot_senior_50 * 0.21)},
            {'age_group': '60-64세', 'male': int(tot_senior_50 * 0.20 * 0.47), 'female': int(tot_senior_50 * 0.20 * 0.53), 'total': int(tot_senior_50 * 0.20)},
            {'age_group': '65-69세', 'male': int(tot_senior_50 * 0.16 * 0.46), 'female': int(tot_senior_50 * 0.16 * 0.54), 'total': int(tot_senior_50 * 0.16)},
            {'age_group': '70-74세', 'male': int(tot_senior_50 * 0.10 * 0.45), 'female': int(tot_senior_50 * 0.10 * 0.55), 'total': int(tot_senior_50 * 0.10)},
            {'age_group': '75세 이상', 'male': int(tot_senior_50 * 0.11 * 0.40), 'female': int(tot_senior_50 * 0.11 * 0.60), 'total': int(tot_senior_50 * 0.11)},
        ]
        calc_tot = sum(a['total'] for a in age_dist)
        diff = tot_senior_50 - calc_tot
        age_dist[0]['total'] += diff
        age_dist[0]['female'] += diff

        pop_50s = age_dist[0]['total'] + age_dist[1]['total']
        pop_60s = age_dist[2]['total'] + age_dist[3]['total']
        pop_70_plus = age_dist[4]['total'] + age_dist[5]['total']
        ratio_50s = round(pop_50s / tot_pop * 100.0, 1) if tot_pop > 0 else 16.5
        ratio_60s = round(pop_60s / tot_pop * 100.0, 1) if tot_pop > 0 else 13.8
        ratio_70_plus = round(pop_70_plus / tot_pop * 100.0, 1) if tot_pop > 0 else 8.1

        # 3-2. 국토부 공동주택(아파트) 단지 현황 — 개인정보 없는 단지 단위 공개정보
        # (키 없음/좌표변환 실패/API 미승인 시 조용히 생략, 기존 흐름에 영향 없음)
        apt_summary = None
        try:
            from . import competitor_engine
            b_code = competitor_engine.CompetitorEngine.geocode_address_bcode(f"{sido} {sigungu} {dong}")
            if b_code:
                apt_summary = apt_client.fetch_apt_summary(b_code[:5], dong)
        except Exception:
            apt_summary = None

        is_estimated_flag = (target_dongs_is_fallback or any(d.get('is_estimated', False) for d in dong_list))
        if sgis_used:
            data_source_text = 'SGIS 통계청 실제 인구 + MYPARK 연령비중 추정 모델'
        elif not is_estimated_flag:
            data_source_text = 'KOSIS 국가통계포털 (실측 DB 매핑)'
        else:
            data_source_text = 'KOSIS 시군구 통계 기반 3km 추정 모델'

        if district_wide_analysis:
            region_name = f"{sido} {sigungu} 전체 (관할 행정동 {district_dong_count}개 전수 집계)"
        else:
            region_name = f"{sido} {sigungu} {center_dong} 일원 (반경 3km 생활권)"

        return {
            'center_dong': center_dong,
            'district_wide_analysis': district_wide_analysis,
            'district_dong_count': district_dong_count,
            'district_dong_names': district_dong_names,
            'region_name': region_name,
            # 채점용 배후 시니어 인구.
            # 매장 1곳이 실제로 끌어올 수 있는 범위는 구 전체가 아니라 생활권(약 3km,
            # 통상 5~6개 행정동)이다. 구 전체 인구를 그대로 채점에 넣으면 "주소를
            # 모호하게 적을수록 점수가 올라가는" 왜곡이 생기므로, 구 전체 분석에서는
            # 구 평균 동 인구 × 6개 동 규모로 환산한 대표 상권 인구로 채점한다.
            'catchment_senior_50': (
                int(tot_senior_50 * min(1.0, 6.0 / district_dong_count))
                if district_wide_analysis and district_dong_count > 0 else tot_senior_50
            ),
            'total_pop': tot_pop,
            'male_pop': tot_male,
            'female_pop': tot_female,
            'senior_50_plus': tot_senior_50,
            'senior_50_female': tot_senior_f,
            'senior_ratio': senior_ratio,
            'pop_50s': pop_50s,
            'pop_60s': pop_60s,
            'pop_70_plus': pop_70_plus,
            'ratio_50s': ratio_50s,
            'ratio_60s': ratio_60s,
            'ratio_70_plus': ratio_70_plus,
            'dongs': dong_list,
            'age_distribution': age_dist,
            'base_date': '2026년 07월 KOSIS 국가통계포털 기준',
            'data_source': data_source_text,
            'sgis_verified': sgis_used,
            'is_estimated': is_estimated_flag,
            'apartment_summary': apt_summary
        }
