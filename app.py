import os
import sys
from flask import Flask, render_template, request, jsonify

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dinajpur_engine import DinajpurUnifiedEngine
from institutes_data import search_institutes, INSTITUTES
from nu_engine import NuResultEngine
from tracker import track_request, get_stats

app = Flask(__name__)
engine = DinajpurUnifiedEngine()
nu_engine = NuResultEngine()

@app.before_request
def log_incoming_visitor():
    track_request(request)

@app.after_request
def add_client_hints(response):
    response.headers['Accept-CH'] = 'Sec-CH-UA-Model, Sec-CH-UA-Platform, Sec-CH-UA-Platform-Version'
    return response

@app.route('/api/nu_student', methods=['POST'])
def api_nu_student():
    data = request.get_json(force=True, silent=True) or {}
    roll = str(data.get('roll', '')).strip()
    reg = str(data.get('reg', '')).strip()
    year = str(data.get('year', '2024')).strip()
    course = str(data.get('course', 'honours')).strip()
    exam_code = str(data.get('exam_code', '2204')).strip()

    if not roll or not reg:
        return jsonify({"success": False, "error": "পরীক্ষার রোল এবং রেজিস্ট্রেশন নম্বর দুটোই আবশ্যক।"}), 400

    try:
        result = nu_engine.get_result(course=course, exam_code=exam_code, roll=roll, reg=reg, year=year)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"জাতীয় বিশ্ববিদ্যালয় সার্ভার অতিরিক্ত ট্রাফিকের কারণে সংযোগ বিচ্ছিন্ন করেছে। অনুগ্রহ করে ১ মিনিট পর পুনরায় চেষ্টা করুন। ({str(e)})"
        }), 200

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

@app.route('/admin-stats')
@app.route('/visitors')
def admin_visitors_page():
    return render_template('admin_visitors.html')

@app.route('/api/admin/visitors')
def api_admin_visitors():
    pin = request.args.get('pin', '')
    if pin != '7860':
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    stats = get_stats(limit=150)
    return jsonify(stats)

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
