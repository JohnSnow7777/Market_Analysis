# -*- coding: utf-8 -*-
"""Vercel Serverless Python Handler (Smart Auto-Estimates)"""
import os
import sys
import json
import base64
import traceback
from http.server import BaseHTTPRequestHandler

curr_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, curr_dir)

from tools.mypark_analyzer import MyParkReportGenerator
from tools.mypark_analyzer.address_resolver import AddressNotResolvedError

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'OK',
            'service': 'MYPARK Commercial & Feasibility Analysis API (Smart Estimates)',
            'version': '1.2.0'
        }).encode('utf-8'))

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))
            
            output_dir = '/tmp/output' if os.path.exists('/tmp') else 'output'
            os.makedirs(output_dir, exist_ok=True)
            
            generator = MyParkReportGenerator(output_dir=output_dir)
            result = generator.analyze_and_generate(
                address=params['address'],
                building_name=params.get('name'),
                rooms=int(params['rooms']) if params.get('rooms') else None,
                monthly_rent=int(params['rent']) if params.get('rent') else None,
                staff_count=int(params['staff']) if params.get('staff') else None,
                area_pyeong=int(params['area']) if params.get('area') else None,
                special_notes=params.get('special_notes')
            )
            
            pptx_b64 = None
            pdf_b64 = None
            if 'pdf_path' in result and os.path.exists(result['pdf_path']):
                with open(result['pdf_path'], 'rb') as f:
                    pdf_b64 = base64.b64encode(f.read()).decode('utf-8')
            if 'pptx_path' in result and os.path.exists(result['pptx_path']):
                with open(result['pptx_path'], 'rb') as f:
                    pptx_b64 = base64.b64encode(f.read()).decode('utf-8')

            result['pdf_base64'] = pdf_b64
            result['pptx_base64'] = pptx_b64
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        except AddressNotResolvedError as e:
            # 사용자가 고칠 수 있는 입력 문제 — 400으로 알리고 안내 문구만 준다.
            self.send_response(400)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            # 서버 오류의 상세(파일 경로·코드 구조)는 로그에만 남긴다.
            # 예전에는 traceback을 그대로 응답에 실어 내부 구조가 외부에 노출됐다.
            err_trace = traceback.format_exc()
            print("[SERVER ERROR]", err_trace)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': '보고서 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해 주시고, '
                         '문제가 계속되면 담당자에게 문의해 주십시오.'
            }, ensure_ascii=False).encode('utf-8'))
