# -*- coding: utf-8 -*-
"""마이파크 분석기 회귀 테스트.

오늘(2026-09-02)까지 실제로 서비스에서 잘못된 값이 나갔던 사례를 그대로
테스트로 고정한다. 같은 유형의 버그가 세 번 반복됐기 때문에, 수정할 때마다
사람이 눈으로 확인하는 방식으로는 재발을 막지 못한다는 것이 확인됐다.

외부 API 키가 없어도 전부 통과해야 한다(키가 없으면 추정 모델로 폴백하며,
그 폴백 경로 자체도 검증 대상이다).

실행:
    python -m pytest tests/ -v
    python tests/test_regression.py      # pytest 없이도 실행 가능
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.mypark_analyzer.address_resolver import (
    AddressResolver, AddressNotResolvedError, validate_address)
from tools.mypark_analyzer.config import (
    classify_region_tier, TIER_PRIME, TIER_METRO, TIER_MID_CITY, TIER_RURAL)
from tools.mypark_analyzer.demographics import DemographicsEngine
from tools.mypark_analyzer.competitor_engine import CompetitorEngine
from tools.mypark_analyzer.geo_engine import GeoEngine


# ---------------------------------------------------------------------------
# 1. 주소 파싱 — 다른 지역으로 뒤바뀌던 사례
# ---------------------------------------------------------------------------

def test_address_does_not_jump_region():
    """'화정동'이 들어있다는 이유로 광주 주소가 경기 고양시로 바뀌면 안 된다."""
    r = AddressResolver.resolve("광주광역시 서구 화정동 123")
    assert r['sido'] == '광주광역시', r
    assert r['sigungu'] == '서구', r
    assert r['dong'] == '화정동', r


def test_address_does_not_invent_dong():
    """시/군/구까지만 입력하면 dong은 비어 있어야 한다.

    상위 로직이 dong=='' 을 '구 전체 분석' 신호로 쓰므로, 임의로 채우면
    사용자가 요청하지 않은 특정 동을 분석해버린다.
    """
    r = AddressResolver.resolve("경기도 성남시 분당구")
    assert r['dong'] == '', r
    assert r['admin_level'] == 'sigungu', r


def test_address_road_name_is_not_treated_as_dong():
    """도로명('상무중앙로')이 행정동 자리에 들어가면 안 된다."""
    r = AddressResolver.resolve("광주광역시 서구 상무중앙로 36")
    assert r['dong'] == '', r
    assert r['road_name'] == '상무중앙로', r


def test_address_sido_only_has_no_fake_sigungu():
    """'○○ 중심권역' 같은 실존하지 않는 행정구역명을 만들면 안 된다."""
    r = AddressResolver.resolve("광주광역시")
    assert r['sigungu'] == '', r
    assert '권역' not in (r['sigungu'] or ''), r


def test_address_without_sido_is_not_guessed():
    """시/도 없는 입력을 두 글자 단서로 추측해 채우면 안 된다."""
    for addr in ["수원시 장안구 정자동", "서구 화정동 12", "정자동 152"]:
        r = AddressResolver.resolve(addr)
        assert r['sido'] == '', f"{addr} -> {r}"


def test_address_known_mapping_still_works_within_same_region():
    """정상 매핑(도로명 별칭)은 계속 동작해야 한다."""
    r = AddressResolver.resolve("경기도 고양시 덕양구 화신로272번길 11")
    assert r['sido'] == '경기도' and r['sigungu'] == '고양시 덕양구', r
    assert r['dong'] == '화정동', r


# ---------------------------------------------------------------------------
# 2. 주소 검증 — 존재하지 않는 주소로 보고서가 나가던 사례
# ---------------------------------------------------------------------------

def test_invalid_address_is_rejected():
    """무효 입력에 등급·회수기간이 붙은 보고서가 생성되면 안 된다."""
    for junk in ["asdfqwer1234", "", "   ", "ㅁㄴㅇㄹ", "1234567890"]:
        try:
            validate_address(junk)
            raise AssertionError(f"거부되지 않음: {junk!r}")
        except AddressNotResolvedError:
            pass


def test_valid_address_passes_validation():
    for addr in ["광주광역시 서구 화정동 123", "광주광역시 서구",
                 "경기도 고양시 덕양구 화정동 123"]:
        r = validate_address(addr)
        assert r['sido'], addr


# ---------------------------------------------------------------------------
# 3. 지역등급 — 매출·임대료 20여 개 수치를 좌우하는 판정
# ---------------------------------------------------------------------------

def _tier(addr):
    r = AddressResolver.resolve(addr)
    return classify_region_tier(addr, r.get('sigungu', ''), r.get('sido', ''))


def test_tier_does_not_match_by_substring():
    """지명 조각이 우연히 일치한다고 최상위 등급을 주면 안 된다."""
    assert _tier("경상남도 진주시 강남동") == TIER_MID_CITY      # '강남' 오탐
    assert _tier("충청북도 충주시 중원대로 3324") == TIER_MID_CITY  # '중원' 오탐
    assert _tier("경기도 광주시 송정동") == TIER_MID_CITY        # 광주광역시 오탐


def test_tier_gun_inside_metro_city_is_rural():
    """광역시 안의 군은 광역시 등급이 아니라 군 등급이어야 한다."""
    for addr in ["울산광역시 울주군", "부산광역시 기장군", "인천광역시 강화군"]:
        assert _tier(addr) == TIER_RURAL, addr


def test_tier_accepts_abbreviated_sido():
    """지도 API가 돌려주는 축약 표기('경기','서울')로도 같은 등급이 나와야 한다.

    카카오는 region_1depth_name을 '경기'로 축약해 준다. 정규화 없이 비교하면
    분당구가 최상위 상권에 걸리지 않고 지방 중소도시로 떨어져, 임대료가
    절반으로 잡히고 손익·회수기간까지 어긋난다(실제 발생 사례).
    """
    pairs = [
        ('서울', '서울특별시', '강남구'),
        ('서울시', '서울특별시', '강남구'),
        ('경기', '경기도', '성남시 분당구'),
        ('부산', '부산광역시', '해운대구'),
        ('대구', '대구광역시', '수성구'),
        ('광주', '광주광역시', '서구'),
        ('울산', '울산광역시', '울주군'),
        ('전북', '전북특별자치도', '전주시 완산구'),
    ]
    for short, full, sigungu in pairs:
        assert classify_region_tier('', sigungu, short) == classify_region_tier('', sigungu, full),             f"{short} vs {full} ({sigungu}) 등급 불일치"


def test_park_golf_excludes_screen_golf_brands():
    """스크린골프 브랜드를 파크골프 경쟁매장으로 세면 안 된다.

    '골프존파크'는 골프존의 스크린골프 브랜드로 파크골프장이 아닌데
    이름에 '파크'가 들어가 경쟁매장으로 실렸던 사례가 있다.
    반대로 '마실파크골프 분당점'은 상호에 '스크린'이 없어 검색에서
    누락됐었다 — 둘 다 판정이 정확해야 한다.
    """
    from tools.mypark_analyzer.sbiz_client import is_park_golf
    assert is_park_golf('마실파크골프 분당점', '파크골프장') is True
    assert is_park_golf('아르피아스포츠센터 스크린파크골프장', '') is True
    assert is_park_golf('골프존파크 수내JUN스크린점', '스크린골프장') is False
    assert is_park_golf('골프존파크 야탑명품스크린점', '') is False
    assert is_park_golf('파크스포츠센터', '스크린골프장') is False


def test_tier_prime_regions():
    for addr in ["서울특별시 강남구 역삼동", "경기도 성남시 분당구 서현동",
                 "부산광역시 해운대구 우동", "대구광역시 수성구 범어동"]:
        assert _tier(addr) == TIER_PRIME, addr


def test_tier_metro_and_mid_city():
    assert _tier("광주광역시 서구 화정동") == TIER_METRO
    assert _tier("경기도 고양시 덕양구 화정동") == TIER_METRO
    assert _tier("전라남도 목포시 옥암동") == TIER_MID_CITY
    assert _tier("전라남도 무안군 삼향읍") == TIER_RURAL


def test_rent_follows_tier_not_keywords():
    """임대료가 지명 조각이 아니라 지역등급을 따라야 한다.

    진주시 강남동이 서울 도심 시세(7만원/평)를 받아 월 임대료가 실제의 두 배
    이상으로 잡히던 문제.
    """
    jinju = GeoEngine.analyze_site("경상남도 진주시 강남동 12")
    gangnam = GeoEngine.analyze_site("서울특별시 강남구 역삼동 736")
    assert jinju['rent_per_pyeong'] < gangnam['rent_per_pyeong'], (jinju, gangnam)
    assert jinju['rent_per_pyeong'] == 38000, jinju['rent_per_pyeong']


# ---------------------------------------------------------------------------
# 4. 동명 중복 — 다른 지역 인구/매장이 섞여 들어가던 사례
# ---------------------------------------------------------------------------

def test_duplicate_dong_names_do_not_cross_regions():
    """같은 동 이름이라도 시/도가 다르면 다른 지역 데이터를 쓰면 안 된다."""
    goyang = DemographicsEngine.get_demographics("경기도 고양시 덕양구 화정동 123")
    gwangju = DemographicsEngine.get_demographics("광주광역시 서구 화정동 123")
    goyang_names = {d['dong'] for d in goyang['dongs']}
    gwangju_names = {d['dong'] for d in gwangju['dongs']}
    # 고양시는 실측 DB의 화정1동/화정2동을 써야 한다
    assert '화정1동' in goyang_names, goyang_names
    # 광주 주소에 고양시 동이 붙으면 안 된다
    assert '화정1동' not in gwangju_names, gwangju_names
    assert '행신1동' not in gwangju_names, gwangju_names


def test_competitor_search_does_not_cross_sido():
    """'서구'는 전국에 여러 개다. 광주 검색에 인천·고양 매장이 나오면 안 된다."""
    res = CompetitorEngine.search_competitors("광주광역시 서구", "서구", "")
    for store in res['stores']:
        addr = store.get('address', '')
        if store.get('status') == '예시 시나리오 (미확인)':
            continue
        assert '경기도' not in addr and '인천' not in addr, store


def test_no_fabricated_dong_names():
    """'사업권역1동', '인접동 A' 같은 존재하지 않는 동 이름을 만들면 안 된다."""
    for addr in ["광주광역시 서구", "경기도 성남시", "전라남도 무안군"]:
        demo = DemographicsEngine.get_demographics(addr)
        for d in demo['dongs']:
            name = d['dong']
            assert '사업권역' not in name, (addr, name)
            assert '인접동' not in name, (addr, name)


# ---------------------------------------------------------------------------
# 5. 채점 — 모호하게 입력할수록 점수가 오르던 왜곡
# ---------------------------------------------------------------------------

def test_district_wide_does_not_inflate_catchment():
    """구 전체 분석에서 구 인구 전체를 배후인구로 쓰면 안 된다.

    매장 하나의 상권은 구 전체가 아니라 생활권이므로, 주소를 모호하게 적을수록
    점수가 오르는 구조가 되면 안 된다.
    """
    demo = DemographicsEngine.get_demographics("광주광역시 서구")
    if not demo.get('district_wide_analysis'):
        return  # SGIS 키가 없으면 구 전체 경로를 타지 않는다 — 검증 대상 아님
    assert demo['catchment_senior_50'] < demo['senior_50_plus'], demo


# ---------------------------------------------------------------------------
# 6. 광역 주소 — 예외 없이 처리되어야 하는 입력 형태
# ---------------------------------------------------------------------------

def test_broad_addresses_do_not_crash():
    """시/도만, 시만, 군만 입력해도 예외 없이 결과가 나와야 한다."""
    for addr in ["광주광역시 서구", "경기도 성남시", "경기도 이천시",
                 "전라남도 무안군", "경기도 성남시 분당구", "광주광역시"]:
        demo = DemographicsEngine.get_demographics(addr)
        assert demo['total_pop'] > 0, addr
        assert demo['region_name'].strip(), addr
        # 지역명이 중복되어 "서구 서구"처럼 찍히면 안 된다
        assert ' 서구 서구' not in demo['region_name'], demo['region_name']


def _run_all():
    """pytest 없이 직접 실행할 때 쓰는 러너."""
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith('test_') and callable(f)]
    failed = []
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except Exception as e:
            failed.append((name, e))
            print(f"  FAIL  {name}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - len(failed)}/{len(tests)} 통과")
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(_run_all())
