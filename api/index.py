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

def _read_b64(path):
    """생성된 파일을 base64로 읽는다. 없으면 None."""
    if path and os.path.exists(path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    return None


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

    def _emit(self, obj):
        """진행 상황 한 건을 SSE 형식으로 즉시 내려보낸다.

        Vercel Python 런타임이 조각 전송을 지원하는 것을 실측으로 확인했다
        (2초 간격 전송이 그대로 2초 간격에 도착).
        """
        self.wfile.write(("data: " + json.dumps(obj, ensure_ascii=False) + "\n\n").encode("utf-8"))
        self.wfile.flush()

    def _handle_stream(self, params):
        """진행 상황을 실시간으로 보내면서 보고서를 생성한다.

        타이머로 화면만 넘기는 연출이 아니라, 각 단계가 실제로 끝난 시점에
        이벤트를 보낸다. 마지막 이벤트에 결과 전체를 실어 보낸다.
        """
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('X-Accel-Buffering', 'no')
        self.end_headers()
        try:
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
                special_notes=params.get('special_notes'),
                progress=lambda stage, pct: self._emit({'stage': stage, 'pct': pct}),
            )
            result['pdf_base64'] = _read_b64(result.get('pdf_path'))
            result['pptx_base64'] = _read_b64(result.get('pptx_path'))
            self._emit({'done': True, 'result': result})
        except AddressNotResolvedError as e:
            self._emit({'error': str(e), 'status': 400})
        except Exception as e:
            print('[SERVER ERROR]', traceback.format_exc())
            self._emit({'error': '보고서 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해 주십시오.',
                        'status': 500})

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))

            # 진행 상황 스트리밍을 요청한 경우 별도 경로로 처리한다.
            if params.get('stream'):
                return self._handle_stream(params)

            
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
