# -*- coding: utf-8 -*-
"""상세 출점 타당성 검토 기획서 DOCX 생성기 (객관적 실측 체크리스트 반영)"""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

class DOCXGenerator:
    """마이파크 상세 상권 및 사업타당성 보고서 DOCX 빌더"""
    
    @staticmethod
    def generate(data, output_docx_path):
        doc = docx.Document()
        
        for section in doc.sections:
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)
            
        site = data['site']
        demo = data['demographics']
        comm = data['commercial']
        fin = data['financials']
        score = data['scores']
        charts = data['charts']
        
        # 표지 타이틀
        title_p = doc.add_paragraph()
        title_run = title_p.add_run(f"마이파크(MYPARK) 스크린 파크골프\n{site.get('building_name', '사업지')} 상권 및 사업성 분석 보고서")
        title_run.font.name = 'Malgun Gothic'
        title_run.font.size = Pt(22)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(0, 51, 102)
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_p.paragraph_format.space_after = Pt(20)
        
        # 메타 테이블
        meta_table = doc.add_table(rows=4, cols=2)
        meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        meta_data = [
            ("대상 사업지 주소", site['full_address']),
            ("분석 공간 규모", f"전용면적 {site['area_pyeong']}평 / {site['rooms']}타석 플래그십 기준"),
            ("입지 최적성 등급", f"{score['grade']}등급 ({score['total_score']}점 / 100점 만점 - {score['grade_desc']})"),
            ("예상 월 영업이익 (보편)", f"약 {fin['monthly_scenarios']['moderate']['operating_profit']//10000:,}만원 (영업이익률 {fin['monthly_scenarios']['moderate']['profit_margin']:.1f}%)")
        ]
        for r_idx, (k, v) in enumerate(meta_data):
            c1 = meta_table.cell(r_idx, 0)
            c2 = meta_table.cell(r_idx, 1)
            c1.text = k
            c2.text = v
            c1.paragraphs[0].runs[0].font.bold = True
            c1.paragraphs[0].runs[0].font.size = Pt(10)
            c2.paragraphs[0].runs[0].font.size = Pt(10)
        
        doc.add_paragraph().paragraph_format.space_after = Pt(15)
        
        # 1. 개요 및 출점 점검 기준
        h1 = doc.add_heading("1. 사업지 개요 및 출점 점검 요건 (현장 실측 기준)", level=1)
        h1.runs[0].font.color.rgb = RGBColor(0, 51, 102)
        p = doc.add_paragraph()
        p.add_run(f"본 사업지는 {site['full_address']}에 위치하며, 전용면적 약 {site['area_pyeong']}평 공간에 {site['rooms']}개의 마이파크 스크린 파크골프 타석 및 라운지/카페가 구축되는 구조입니다.\n\n")
        p.add_run(f"• 층고 요건: {site['clear_height_spec']}\n")
        p.add_run(f"• 주차 요건: {site['parking_spec']}\n")
        p.add_run(f"• 이동 편의: {site['accessibility_spec']}\n")
        p.add_run(f"• 인허가 및 용도: {site['zoning_spec']}")
        
        # 2. 인구
        h2 = doc.add_heading("2. 배후 상권 인구 및 시니어 타겟 분석", level=1)
        h2.runs[0].font.color.rgb = RGBColor(0, 51, 102)
        p = doc.add_paragraph()
        p.add_run(f"사업지 반경 3km(자동차 10분 생활권) 내 거주 총인구는 {demo['total_pop']:,}명(남 {demo['male_pop']:,}명 / 여 {demo['female_pop']:,}명)입니다. ")
        p.add_run(f"이 중 스크린 파크골프의 핵심 타겟인 50대 이상 장·노년층 인구는 약 {demo['senior_50_plus']:,}명으로 전체 인구의 {demo['senior_ratio']}%를 차지합니다.\n")
        p.add_run(f"특히 주간 시간대 소비를 주도하는 50대 이상 여성 인구가 {demo['senior_50_female']:,}명에 달해 평일 낮 동호회 및 친목 모임 유치에 최적의 환경을 형성하고 있습니다.")
        
        # 3. 상권
        h3 = doc.add_heading("3. 상권 매출 동향 및 경쟁 환경", level=1)
        h3.runs[0].font.color.rgb = RGBColor(0, 51, 102)
        p = doc.add_paragraph()
        p.add_run(f"소상공인 365 플랫폼 데이터 분석 결과, 해당 권역 내 스포츠/골프 업종의 월평균 매출액은 약 {comm['monthly_avg_sales']//10000:,}만원 수준으로 안정적인 여가 소비력을 입증하고 있습니다. ")
        p.add_run(f"요일별로는 주말 평균 비중이 {comm['day_distribution']['주말평균비중']}%, 평일 월요일이 {comm['day_distribution']['월']}%로 높게 나타나며, ")
        p.add_run(f"시간대별로는 주간(10~17시) 이용 비중이 {comm['time_distribution']['주간_10_17시_비중']}%로 일반 스크린골프 대비 주간 가동률이 압도적으로 높습니다.")
        
        # 4. 재무
        h4 = doc.add_heading("4. 재무 타당성 및 3대 시나리오 손익 추정", level=1)
        h4.runs[0].font.color.rgb = RGBColor(0, 51, 102)
        c_sc = fin['monthly_scenarios']['conservative']
        m_sc = fin['monthly_scenarios']['moderate']
        o_sc = fin['monthly_scenarios']['optimistic']
        p = doc.add_paragraph()
        p.add_run(f"{site['rooms']}타석 운영 기준, 3대 시나리오별 월간 예상 손익 및 연간 전망은 다음과 같습니다:\n")
        p.add_run(f"• 보수적 시나리오: 월매출 {c_sc['total_revenue']//10000:,}만원 / 월비용 {c_sc['total_cost']//10000:,}만원 / 월 영업이익 {c_sc['operating_profit']//10000:,}만원 (연 {(c_sc['operating_profit']*12)//100000000:.1f}억원)\n")
        p.add_run(f"• 보편적 시나리오: 월매출 {m_sc['total_revenue']//10000:,}만원 / 월비용 {m_sc['total_cost']//10000:,}만원 / 월 영업이익 {m_sc['operating_profit']//10000:,}만원 (연 {(m_sc['operating_profit']*12)//100000000:.1f}억원)\n")
        p.add_run(f"• 긍정적 시나리오: 월매출 {o_sc['total_revenue']//10000:,}만원 / 월비용 {o_sc['total_cost']//10000:,}만원 / 월 영업이익 {o_sc['operating_profit']//10000:,}만원 (연 {(o_sc['operating_profit']*12)//100000000:.1f}억원)\n\n")
        p.add_run(f"손익분기점(BEP)은 월 매출 약 {fin['investment']['bep_monthly_sales']//10000:,}만원(기기당 1일 {fin['investment']['bep_turns_per_room']}회전)으로, 초기 순투자금 회수 기간은 {score['payback_text']}로 산출되었습니다.")
        
        # 5. 결론
        h5 = doc.add_heading("5. 입지 최적성 5대 지표 평가 및 최종 제안", level=1)
        h5.runs[0].font.color.rgb = RGBColor(0, 51, 102)
        p = doc.add_paragraph()
        p.add_run(f"마이파크 입지 최적성 5대 다이아몬드 지표 평가 결과, 종합 점수 {score['total_score']}점({score['grade']}등급)을 획득하여 마이파크 스크린 파크골프 매장 출점에 가장 적합한 특급 상권으로 판정되었습니다.\n\n")
        p.add_run(f"【 가맹점 출점 기대효과 및 핵심 경쟁력 】\n{score['value_franchisee']}\n\n")
        p.add_run(f"【 상가 전체 상권 활성화 및 건물 가치 상승 효과 】\n{score['value_landlord']}")
        
        os.makedirs(os.path.dirname(output_docx_path), exist_ok=True)
        doc.save(output_docx_path)
        print(f"[DOCX GENERATED] {output_docx_path}")
        return output_docx_path
