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
        except Exception as e:
            err_trace = traceback.format_exc()
            print("[SERVER ERROR]", err_trace)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': str(e),
                'traceback': err_trace
            }, ensure_ascii=False).encode('utf-8'))
