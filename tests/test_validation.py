# -*- coding: utf-8 -*-
import os, sys, pptx, docx

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.abspath('.'))
from tools.mypark_analyzer import MyParkReportGenerator

def run_tests():
    print("=" * 65)
    print("[MYPARK] 10타석 120평 플래그십 모델 및 고객용 보고서 검증 시작")
    print("=" * 65)
    
    test_cases = [
        {
            "name": "Case 1: 주소 단독 입력 (플래그십 표준 10타석 120평 자동 산정)",
            "address": "경기도 고양시 일산동구 숲속마을로 22",
            "building": "일산풍동점",
            "rooms": None,
            "rent": None,
            "area": None
        },
        {
            "name": "Case 2: 일산 장항동 (10타석 120평 명시)",
            "address": "경기도 고양시 일산동구 장항동 736-6",
            "building": "일산장항점",
            "rooms": 10,
            "rent": 5000000,
            "area": 120
        },
        {
            "name": "Case 3: 송도국제도시 (10타석 120평 플래그십)",
            "address": "인천광역시 연수구 하모니로177번길 49",
            "building": "송도점",
            "rooms": 10,
            "rent": 5400000,
            "area": 120
        },
        {
            "name": "Case 4: 신규 용인 수지구 (주소 단독 입력)",
            "address": "경기도 용인시 수지구 풍덕천동 1082",
            "building": "용인수지점",
            "rooms": None,
            "rent": None,
            "area": None
        }
    ]
    
    generator = MyParkReportGenerator(output_dir="output")
    
    for tc in test_cases:
        print(f"\n--- [검증 실행] {tc['name']} ---")
        res = generator.analyze_and_generate(
            address=tc['address'],
            building_name=tc['building'],
            rooms=tc['rooms'],
            monthly_rent=tc['rent'],
            area_pyeong=tc['area']
        )
        
        site = res['bundle']['site']
        pptx_path = res['pptx_path']
        docx_path = res['docx_path']
        
        # 1. 플래그십 기준 10타석 120평 확인
        assert site['rooms'] == 10, f"Expected 10 rooms, got {site['rooms']}"
        assert site['area_pyeong'] == 120, f"Expected 120 pyeong, got {site['area_pyeong']}"
        
        # 2. 파일 실존 및 구조 검증
        assert os.path.exists(pptx_path), f"PPTX file missing: {pptx_path}"
        assert os.path.exists(docx_path), f"DOCX file missing: {docx_path}"
        
        prs = pptx.Presentation(pptx_path)
        slide_count = len(prs.slides)
        assert slide_count == 12, f"Expected 12 slides, got {slide_count}"
        
        doc = docx.Document(docx_path)
        para_count = len(doc.paragraphs)
        table_count = len(doc.tables)
        
        # 3. 비즈니스 텍스트 검증 (설득/피칭 단어 완전 제거 확인)
        for s in prs.slides:
            for shp in s.shapes:
                if shp.has_text_frame:
                    assert "설득 피칭" not in shp.text_frame.text, "Found forbidden phrase in PPTX"
        for p in doc.paragraphs:
            assert "설득 피칭" not in p.text, "Found forbidden phrase in DOCX"
            
        print(f"[PASS] {tc['name']}")
        print(f"  * 규모: {site['rooms']}타석 / {site['area_pyeong']}평 | 월 임대료: {site['monthly_rent']:,}원")
        print(f"  * 등급 및 점수: {res['grade']}등급 ({res['total_score']}점 / 100점)")
        print(f"  * 월 총매출(보편): {res['total_revenue_moderate']:,}원 | 월 영업이익: {res['operating_profit_moderate']:,}원")
        print(f"  * 투자 회수 기간: {res['payback_months']}개월")
        print(f"  * PPTX 파일: {os.path.basename(pptx_path)} (12 슬라이드)")
        print(f"  * DOCX 파일: {os.path.basename(docx_path)} ({para_count} 문단, {table_count} 표)")
        
    print("\n" + "=" * 65)
    print("[SUCCESS] 10타석 120평 플래그십 기준 및 용어 정제 검증 100% PASS 완료!")
    print("=" * 65)

if __name__ == '__main__':
    run_tests()
