# -*- coding: utf-8 -*-
"""Vercel Serverless Python Handler"""
import os
import sys
import json
import base64
from http.server import BaseHTTPRequestHandler

# Set current dir to path
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
            'service': 'MYPARK Commercial & Feasibility Analysis API',
            'version': '1.0.0'
        }).encode('utf-8'))

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))
            
            # Vercel /tmp writable output directory
            output_dir = '/tmp/output' if os.path.exists('/tmp') else 'output'
            os.makedirs(output_dir, exist_ok=True)
            
            generator = MyParkReportGenerator(output_dir=output_dir)
            result = generator.analyze_and_generate(
                address=params['address'],
                building_name=params.get('name'),
                rooms=int(params.get('rooms', 12)),
                monthly_rent=int(params.get('rent', 5000000)),
                staff_count=int(params.get('staff', 4)),
                area_pyeong=int(params.get('area', 100))
            )
            
            # Read generated PPTX and DOCX into base64 for direct browser download
            pptx_b64 = None
            docx_b64 = None
            if os.path.exists(result['pptx_path']):
                with open(result['pptx_path'], 'rb') as f:
                    pptx_b64 = base64.b64encode(f.read()).decode('utf-8')
            if os.path.exists(result['docx_path']):
                with open(result['docx_path'], 'rb') as f:
                    docx_b64 = base64.b64encode(f.read()).decode('utf-8')
                    
            result['pptx_base64'] = pptx_b64
            result['docx_base64'] = docx_b64
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
