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

# 시/도 약칭 → 법정 정식 명칭 정규화 표.
# (반환 sido 값을 항상 정식 명칭으로 통일하기 위한 표기 정규화용이며, 새로운 지역 추론에는 쓰지 않는다.)
SIDO_CANONICAL = {
    '서울': '서울특별시', '서울시': '서울특별시',
    '부산': '부산광역시', '부산시': '부산광역시',
    '대구': '대구광역시', '대구시': '대구광역시',
    '인천': '인천광역시', '인천시': '인천광역시',
    '광주': '광주광역시', '광주시': '광주광역시',
    '대전': '대전광역시', '대전시': '대전광역시',
    '울산': '울산광역시', '울산시': '울산광역시',
    '세종': '세종특별자치시', '세종시': '세종특별자치시',
    '경기': '경기도',
    '강원': '강원특별자치도', '강원도': '강원특별자치도',
    '충북': '충청북도', '충남': '충청남도',
    '전북': '전북특별자치도', '전라북도': '전북특별자치도',
    '전남': '전라남도',
    '경북': '경상북도', '경남': '경상남도',
    '제주': '제주특별자치도', '제주도': '제주특별자치도',
}

# 접미사 규칙 (하드코딩된 개별 지명 대신 행정구역 접미사로 단계를 판별한다)
SIGUNGU_SUFFIXES = ('시', '군', '구')
DONG_SUFFIXES = ('동', '읍', '면', '가', '리')
ROAD_SUFFIXES = ('대로', '로', '길')
ROAD_NUMBERED_RE = re.compile(r'\d+(번길|길|로)$')


def _is_road_token(token):
    """도로명(~로/~길/~번길/~대로)인지 판별. 행정동이 아니므로 dong 자리에 넣으면 안 된다."""
    return token.endswith(ROAD_SUFFIXES) or bool(ROAD_NUMBERED_RE.search(token))


def _is_dong_token(token):
    """읍/면/동 등 행정동 접미사 판별. 도로명이 우선 판정되므로 도로명은 여기서 제외된다."""
    if _is_road_token(token):
        return False
    return token.endswith(DONG_SUFFIXES)


def _match_known_mapping(clean, found_sido, found_sigungu=None):
    """KNOWN_MAPPINGS를 지역 검증과 함께 조회한다. 확신이 없으면 None.

    이 표의 키는 '화정', '정자', '대화'처럼 두 글자 조각이라 주소 어디에든
    우연히 걸리기 쉽다. 그래서 다음 두 조건을 모두 만족할 때만 인정한다.

      1) 입력에 시/도가 있으면 매핑의 시/도와 일치해야 한다.
      2) 입력에 시/군/구가 있으면 매핑의 시/군/구와도 일치해야 한다.

    2번이 없으면 같은 도 안의 다른 시에 남의 동이 붙는다
    (예: '경기도 광주시 대화로 12' -> 고양시 일산서구 대화동,
          '경기도 시흥시 정자로 5' -> 성남시 분당구 정자동).

    시/도조차 파악되지 않은 입력에는 아예 적용하지 않는다. 두 글자 조각만
    보고 시/도·시군구·동을 통째로 지어내면(예: '수원시 장안구 정자동' ->
    성남시 분당구) 이후 모든 분석이 다른 지역 것이 되기 때문이다.
    """
    if not found_sido:
        return None
    best = None
    for k, v in KNOWN_MAPPINGS.items():
        if k not in clean:
            continue
        if v['sido'] != found_sido:
            continue  # 시/도 불일치 → 동명이지명이므로 무시
        if found_sigungu and not _same_sigungu(v['sigungu'], found_sigungu):
            continue  # 같은 도 안의 다른 시/군/구 → 무시
        # 더 긴 키가 더 구체적인 단서다('화신로' > '화정')
        if best is None or len(k) > best[0]:
            best = (len(k), v)
    return best[1] if best else None


def _same_sigungu(a, b):
    """'고양시 덕양구' vs '덕양구'처럼 상위 시 표기 유무만 다른 경우를 같다고 본다."""
    a = ' '.join((a or '').split())
    b = ' '.join((b or '').split())
    if not a or not b:
        return False
    if a == b:
        return True
    a_last, b_last = a.split()[-1], b.split()[-1]
    if a_last != b_last:
        return False
    a_head, b_head = ' '.join(a.split()[:-1]), ' '.join(b.split()[:-1])
    if a_head and b_head:
        return a_head == b_head
    return True


class AddressResolver:
    @staticmethod
    def resolve(raw_address):
        clean = (raw_address or '').strip()
        tokens = clean.split()

        # 1. 시/도 탐지 (주소 선두 토큰만 검사해 '제주시' 같은 하위 지명 오인식을 막는다)
        found_sido = None
        sido_idx = -1
        for idx, token in enumerate(tokens[:2]):
            # 긴 이름부터 비교해야 '광주'가 '광주광역시'보다 먼저 걸리지 않는다
            for s in sorted(SIDO_NAMES, key=len, reverse=True):
                if token.startswith(s):
                    found_sido = SIDO_CANONICAL.get(s, s)
                    sido_idx = idx
                    break
            if found_sido:
                break

        if found_sido:
            rem = tokens[sido_idx + 1:]

            # 2. 시/군/구 파싱: '성남시 분당구'처럼 2단계인 경우만 두 토큰을 합친다
            sigungu = ''
            cursor = 0
            if rem and rem[0].endswith(SIGUNGU_SUFFIXES) and not _is_road_token(rem[0]):
                sigungu = rem[0]
                cursor = 1
                if (len(rem) >= 2 and rem[0].endswith(('시', '군'))
                        and rem[1].endswith('구') and not _is_road_token(rem[1])):
                    sigungu = f"{rem[0]} {rem[1]}"
                    cursor = 2

            # 3. 동/도로명 판별: 사용자가 입력하지 않은 동은 절대 만들어내지 않는다
            dong = ''
            road_name = ''
            for token in rem[cursor:]:
                if not dong and _is_dong_token(token):
                    dong = token
                    break
                if not road_name and _is_road_token(token):
                    road_name = token
                    # 도로명 뒤에 동이 괄호 없이 오는 경우를 위해 탐색은 계속한다
                    continue

            # 4. 도로명만 있는 경우에 한해 KNOWN_MAPPINGS의 실제 동을 보완한다.
            #    (시/군/구까지만 입력된 주소에는 적용하지 않는다 — dong='' 이 '구 전체 분석' 신호이기 때문)
            if not dong and road_name:
                mapped = _match_known_mapping(clean, found_sido, sigungu)
                if mapped:
                    dong = mapped['dong']
                    if not sigungu:
                        sigungu = mapped['sigungu']

            # 5. 행정구역 단계 판정
            if dong:
                admin_level = 'dong'
            elif road_name:
                admin_level = 'road'
            elif sigungu:
                admin_level = 'sigungu'
            else:
                # 시/도만 입력된 경우 — '○○ 중심권역' 같은 가짜 이름을 만들지 않는다
                admin_level = 'sido'

            # 입력에 옛 명칭(전라북도 등)이 쓰였으면 표기를 공식 명칭으로 맞춘다.
            _display_addr = clean
            _first = clean.split()[0] if clean.split() else ''
            if _first and _first != found_sido:
                for _alias in SIDO_NAMES:
                    if _first.startswith(_alias) and SIDO_CANONICAL.get(_alias) == found_sido:
                        _display_addr = found_sido + clean[len(_first):]
                        break

            return {
                'sido': found_sido,
                'sigungu': sigungu,
                'dong': dong,
                'road_name': road_name,
                'admin_level': admin_level,
                'full_address': _display_addr,
                'is_resolved': True
            }

        # 6. 시/도가 없는 입력.
        # 두 글자 조각 매칭으로 지역을 추측하지 않는다 — '서구 화정동'을 고양시로,
        # '정자동 152'를 분당으로 단정해버리면 이후 인구·경쟁사·재무가 전부 다른
        # 지역 것이 된다. 시/도를 알 수 없으면 알 수 없다고 반환하고, 상위 단계가
        # 지오코딩으로 확인하거나 추정임을 명시하도록 한다.
        mapped = None
        if mapped:
            return {
                'sido': mapped['sido'],
                'sigungu': mapped['sigungu'],
                'dong': mapped['dong'],
                'road_name': next((t for t in tokens if _is_road_token(t)), ''),
                'admin_level': 'dong' if mapped['dong'] else 'sigungu',
                'full_address': f"{mapped['sido']} {mapped['sigungu']} {clean}".strip(),
                'is_resolved': True
            }

        # 7. 문자열만으로는 시/도를 알 수 없는 경우(도로명만 입력 등)
        # 지도 API로 실제 행정구역을 조회한다. 이름 조각으로 추측하는 것이 아니라
        # 실제 좌표 기반 조회이므로 지어내는 것이 아니다.
        #
        # 이 보완을 resolve() 안에서 하는 이유: 사업지 정보·인구·경쟁사 모듈이
        # 각각 resolve()를 다시 호출하기 때문에, 상위에서 한 번 보완해도 그 값이
        # 버려진다(실제로 '안골로48번길14' 입력 시 분당구가 계속 지방 상권으로
        # 분류되던 원인). 조회 결과는 캐시되어 반복 호출 비용이 없다.
        _geo = _geocode_region(clean)
        if _geo and _geo.get('sido'):
            _g_sigungu = _geo.get('sigungu', '')
            _g_dong = _geo.get('dong', '')
            _g_road = next((t for t in tokens if _is_road_token(t)), '')
            if _g_dong:
                _lvl = 'dong'
            elif _g_road:
                _lvl = 'road'
            else:
                _lvl = 'sigungu'
            _g_full = clean
            if _geo['sido'] not in _g_full:
                _g_full = f"{_geo['sido']} {_g_sigungu} {clean}".strip()
            return {
                'sido': _geo['sido'],
                'sigungu': _g_sigungu,
                'dong': _g_dong,
                'road_name': _g_road,
                'admin_level': _lvl,
                'full_address': _g_full,
                'is_resolved': True,
            }

        # 8. 최종 fallback: 모르면 비워 둔다 (추측으로 채우지 않는다)
        return {
            'sido': '',
            'sigungu': '',
            'dong': '',
            'road_name': next((t for t in tokens if _is_road_token(t)), ''),
            'admin_level': 'unknown',
            'full_address': clean,
            'is_resolved': False,
            'fallback_warning': '시/도를 식별하지 못해 행정구역 매핑 미확인 (지오코딩 단계에서 좌표 확인 필요)'
        }


def _geocode_region(address):
    """지도 API로 (시/도, 시군구, 행정동)을 확인한다. 키 없음/실패 시 None.

    competitor_engine을 모듈 최상단에서 import 하면 순환 참조가 되므로
    호출 시점에 가져온다. 결과는 그쪽 캐시를 그대로 활용한다.
    """
    try:
        from .competitor_engine import CompetitorEngine
        return CompetitorEngine.resolve_region_by_geocode(address)
    except Exception:
        return None


class AddressNotResolvedError(ValueError):
    """주소를 행정구역으로 확인하지 못했을 때 발생.

    확인되지 않은 주소로 보고서를 만들면 존재하지 않는 사업지에 대해
    등급·회수기간까지 붙은 완성된 문서가 나가게 된다. 상용 서비스에서는
    그 자체가 신뢰를 무너뜨리므로, 만들지 않고 분명히 알리는 편이 낫다.
    """
    pass


def validate_address(raw_address):
    """분석 가능한 주소인지 확인한다. 불가하면 AddressNotResolvedError.

    1차로 문자열 파싱, 실패하면 카카오 지오코딩으로 한 번 더 확인한다
    (건물명만 입력하는 등 파서가 못 잡는 실제 주소를 구제하기 위함).
    둘 다 실패하면 추측하지 않고 사용자에게 다시 입력을 요청한다.
    반환: resolve() 결과 dict (지오코딩으로 보완된 경우 그 값이 반영됨)
    """
    resolved = AddressResolver.resolve(raw_address)
    if resolved.get('sido'):
        return resolved

    # resolve()가 이미 지도 API 보완까지 시도한다. 여기서는 좌표로 실재 여부만
    # 한 번 더 확인해, 지도에 있는 주소인데 행정구역 파싱만 실패한 경우를 구제한다.
    try:
        from .competitor_engine import CompetitorEngine
        x, _y = CompetitorEngine.geocode_address(raw_address)
    except Exception:
        x = None
    if x is not None:
        resolved['is_resolved'] = True
        return resolved

    raise AddressNotResolvedError(
        "입력하신 주소에서 행정구역(시/도 · 시군구)을 확인하지 못했습니다. "
        "'광주광역시 서구 화정동 123' 또는 '광주광역시 서구'처럼 "
        "시/도부터 포함해 다시 입력해 주십시오."
    )
