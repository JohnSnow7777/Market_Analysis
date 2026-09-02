# -*- coding: utf-8 -*-
"""행정구역 식별 공용 모듈 (지역명 중복으로 인한 오매칭 방지).

한국의 행정구역 이름은 전국에 광범위하게 중복된다.
  - '서구'  : 광주/인천/대구/대전/부산
  - '중구','남구','북구','동구' : 여러 광역시에 동시 존재
  - '화정동': 경기 고양시 덕양구 / 광주 서구
  - '신흥동': 경기 성남시 수정구 / 전남 목포시 / 인천 동구
  - '중앙동','신흥동','대신동' 등 이름만으로는 어느 지역인지 알 수 없음

그동안 이 코드베이스에서 반복적으로 발생한 버그는 전부 같은 원인이었다:
"이름이 같으면 같은 지역"이라고 가정하고 문자열 부분일치로 지역을 판별한 것.
그래서 광주 주소에 고양시 인구가 붙거나, 광주 검색에 인천 매장이 섞여 나왔다.

이 모듈은 그 가정을 구조적으로 불가능하게 만드는 것이 목적이다.
지역은 항상 (시/도, 시군구, 읍면동) 3요소로 식별하고, 조회 표의 키도
3요소 튜플로 둔다. 이름 하나만으로 조회하는 API는 의도적으로 제공하지 않는다.
"""

# 시/도 표기 흔들림을 흡수하기 위한 정규화 표.
# ('광주', '광주시', '광주광역시'가 모두 같은 곳을 가리켜야 한다.)
_SIDO_ALIASES = {
    '서울': '서울특별시', '서울시': '서울특별시', '서울특별시': '서울특별시',
    '부산': '부산광역시', '부산시': '부산광역시', '부산광역시': '부산광역시',
    '대구': '대구광역시', '대구시': '대구광역시', '대구광역시': '대구광역시',
    '인천': '인천광역시', '인천시': '인천광역시', '인천광역시': '인천광역시',
    '광주': '광주광역시', '광주시': '광주광역시', '광주광역시': '광주광역시',
    '대전': '대전광역시', '대전시': '대전광역시', '대전광역시': '대전광역시',
    '울산': '울산광역시', '울산시': '울산광역시', '울산광역시': '울산광역시',
    '세종': '세종특별자치시', '세종시': '세종특별자치시', '세종특별자치시': '세종특별자치시',
    '경기': '경기도', '경기도': '경기도',
    '강원': '강원특별자치도', '강원도': '강원특별자치도', '강원특별자치도': '강원특별자치도',
    '충북': '충청북도', '충청북도': '충청북도',
    '충남': '충청남도', '충청남도': '충청남도',
    '전북': '전북특별자치도', '전라북도': '전북특별자치도', '전북특별자치도': '전북특별자치도',
    '전남': '전라남도', '전라남도': '전라남도',
    '경북': '경상북도', '경상북도': '경상북도',
    '경남': '경상남도', '경상남도': '경상남도',
    '제주': '제주특별자치도', '제주도': '제주특별자치도', '제주특별자치도': '제주특별자치도',
}


def normalize_sido(sido):
    """시/도 표기를 정식 명칭으로 통일. 모르는 값은 공백만 정리해 그대로 둔다."""
    if not sido:
        return ''
    s = str(sido).strip()
    return _SIDO_ALIASES.get(s, s)


def normalize_sigungu(sigungu):
    """시군구 표기 정리.

    '고양시 덕양구'처럼 두 토큰인 경우와 '덕양구'처럼 마지막 토큰만 온 경우를
    같은 것으로 볼 수 있도록, 비교는 same_sigungu()에서 처리하고 여기서는
    공백만 정규화한다(이름 자체를 변형하면 원본 표기를 잃는다).
    """
    if not sigungu:
        return ''
    return ' '.join(str(sigungu).split())


def same_sigungu(a, b):
    """두 시군구 표기가 같은 곳을 가리키는지 판단.

    '고양시 덕양구' vs '덕양구'처럼 상위 시 표기 유무만 다른 경우를 같다고 본다.
    단, 마지막 토큰(자치구 이름)이 반드시 일치해야 하므로 '덕양구' vs '일산서구'는
    다르다고 판정된다. 시/도 확인은 별도로 하므로 여기서는 시군구만 본다.
    """
    a, b = normalize_sigungu(a), normalize_sigungu(b)
    if not a or not b:
        return False
    if a == b:
        return True
    a_last, b_last = a.split()[-1], b.split()[-1]
    if a_last != b_last:
        return False
    # 마지막 토큰이 같다면, 상위 시 표기가 둘 다 있을 때만 그것도 비교한다.
    a_head = ' '.join(a.split()[:-1])
    b_head = ' '.join(b.split()[:-1])
    if a_head and b_head:
        return a_head == b_head
    return True


def region_key(sido, sigungu, dong):
    """조회 표의 표준 키. 지역명만으로는 절대 조회하지 못하게 3요소를 강제한다."""
    return (normalize_sido(sido), normalize_sigungu(sigungu), (dong or '').strip())


def same_region(sido_a, sigungu_a, sido_b, sigungu_b):
    """두 (시/도, 시군구)가 같은 행정구역인지 판단.

    한쪽에 시/도 정보가 없으면 시/도 비교는 건너뛴다(정보 부족을 불일치로
    단정하지 않되, 있는 정보는 반드시 일치해야 한다).
    """
    sa, sb = normalize_sido(sido_a), normalize_sido(sido_b)
    if sa and sb and sa != sb:
        return False
    if sigungu_a and sigungu_b:
        return same_sigungu(sigungu_a, sigungu_b)
    return True


def lookup_by_region(table, sido, sigungu, dong):
    """(시/도, 시군구, 동) 키 표에서 조회. 없으면 None.

    표기 흔들림('고양시 덕양구' vs '덕양구')을 흡수하기 위해, 정확 키가 없으면
    같은 동 이름을 가진 항목 중 same_region()을 통과하는 것만 후보로 본다.
    이름만 같고 지역이 다른 항목은 절대 반환하지 않는다 — 이 모듈의 존재 이유다.
    """
    exact = table.get(region_key(sido, sigungu, dong))
    if exact is not None:
        return exact
    target_dong = (dong or '').strip()
    if not target_dong:
        return None
    for (k_sido, k_sigungu, k_dong), value in table.items():
        if k_dong != target_dong:
            continue
        if same_region(sido, sigungu, k_sido, k_sigungu):
            return value
    return None
