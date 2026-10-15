import os
import sys
from flask import Flask, render_template, request, jsonify

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dinajpur_engine import DinajpurUnifiedEngine
from institutes_data import search_institutes, INSTITUTES

app = Flask(__name__)
engine = DinajpurUnifiedEngine()

@app.route('/api/institutes')
def api_institutes():
    query = request.args.get('q', '').strip()
    board = request.args.get('board', '').strip()
    district = request.args.get('district', '').strip()
    res = search_institutes(query=query, board=board, district=district)
    return jsonify({"success": True, "count": len(res), "institutes": res})

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/captcha')
def api_captcha():
    try:
        b64, raw_bytes = engine.get_archive_captcha_base64()
        suggested = engine._solve_archive_captcha(raw_bytes)
        return jsonify({"success": True, "captcha_img": b64, "suggested_captcha": suggested})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/student', methods=['POST'])
def api_student():
    data = request.get_json(force=True, silent=True) or {}
    roll = data.get('roll')
    reg = data.get('reg', '')
    exam = data.get('exam', 'HSC')
    year = str(data.get('year', '2025')).strip()
    board = str(data.get('board', 'dinajpur')).strip()
    captcha = data.get('captcha', '')

    if not roll:
        return jsonify({"success": False, "error": "রোল নম্বর প্রদান করুন।"}), 400

    result = engine.get_student_result(roll_no=roll, regi_no=reg, exam=exam, year=year, board=board, captcha=captcha)
    return jsonify(result)

@app.route('/api/institute', methods=['POST'])
def api_institute():
    data = request.get_json(force=True, silent=True) or {}
    eiin = data.get('eiin')
    exam = data.get('exam', 'HSC')
    year = str(data.get('year', '2025')).strip()
    board = str(data.get('board', 'dinajpur')).strip()

    if not eiin:
        return jsonify({"success": False, "error": "প্রতিষ্ঠানের EIIN নম্বর প্রদান করুন।"}), 400

    result = engine.get_institute_result(eiin_no=eiin, exam=exam, year=year, board=board)
    return jsonify(result)

@app.route('/api/institute/pdf')
def api_institute_pdf():
    pdf_bytes, filename = engine.download_institution_pdf()
    if pdf_bytes:
        from flask import Response
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
    return jsonify({"success": False, "error": "PDF রেজাল্ট শিট পাওয়া যায়নি।"}), 404

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "service": "Dinajpur Unified Multi-Year Engine (2015-2026)", "board": "DINAJPUR"})

if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    port = int(os.environ.get('PORT', 5000))
    print("\n=======================================================")
    print(">> Dinajpur All-Years Result Portal (2015-2026) Started!")
    print(f">> Open your browser at: http://127.0.0.1:{port}")
    print("=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=False)
