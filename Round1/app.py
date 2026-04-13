from flask import Flask, request, jsonify, render_template, session, redirect, url_for

import json
import time

app = Flask(__name__)
app.secret_key = 'super_secret_escape_room_key'

GLOBAL_PIN = '1532'
ADMIN_PASSWORD = 'admin_cer'
MAX_ADVANCE = 25
nxtCount = 0

sets_solutions = {
    "1": ["3", "3", "10", "28", "3939"],
    "2": ["36", "53", "10", "3", "1300"],
    "3": ["34", "104", "10", "6", "247"],
    "4": ["13", "53", "73", "224", "216"],
    "5": ["7", "53", "3", "28", "4"]
}

set_formats = {
    "1": "http://[Q3].[Q5].[Q1].[Q4]:[Q2]",
    "2": "http://[Q2].[Q4].[Q1].[Q3]:[Q5]",
    "3": "http://[Q2].[Q4].[Q1].[Q3]:[Q5]",
    "4": "http://[Q3].[Q4].[Q1].[Q5]:[Q2]",
    "5": "http://[Q5].[Q2].[Q3].[Q4]:[Q1]"
}

timeout_pool = []
pool_evaluated = False

# load questions silently catching errors if missing
try:
    with open('questions.json', 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
except FileNotFoundError:
    questions_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify_pin', methods=['POST'])
def verify_pin():
    data = request.json
    if data.get('pin') == GLOBAL_PIN:
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 401

@app.route('/round1')
def round1():
    return render_template('round1.html')

@app.route('/admin')
def admin():
    if request.cookies.get('cer_auth_token') != 'authenticated':
        return redirect('http://localhost:5000/')
    # Simple organizer dashboard
    return render_template('admin.html')

@app.route('/get_set/<set_num>')
def get_set(set_num):
    if set_num in questions_data and set_num in set_formats:
        q_dict = questions_data[set_num]
        questions_list = [{"id": k, "text": v} for k, v in q_dict.items()]
        return jsonify({
            "status": "success", 
            "questions": questions_list, 
            "url_format": set_formats[set_num]
        })
    return jsonify({"status": "error", "message": "Invalid Set Number"}), 400

@app.route('/submit', methods=['POST'])
def submit():
    global nxtCount, pool_evaluated
    data = request.json
    set_num = str(data.get('set_num'))
    user_answers = data.get('answers', [])
    is_timeout = data.get('is_timeout', False)
    user_id = data.get('user_id')
    
    if not set_num or set_num not in sets_solutions:
        return jsonify({"status": "error", "message": "Invalid configuration"}), 400
        
    correct_answers = sets_solutions[set_num]
    score = sum(1 for i, ans in enumerate(user_answers) if i < 5 and str(ans).strip() == correct_answers[i])
    
    # 1. PERFECT SCORE
    if score == 5:
        if nxtCount < MAX_ADVANCE:
            nxtCount += 1
            correct_url = f"http://{correct_answers[0]}.{correct_answers[1]}.{correct_answers[2]}.{correct_answers[3]}:{correct_answers[4]}"
            return jsonify({
                "status": "advance_instant", 
                "score": 5, 
                "correct_url": correct_url
            })
        else:
            return jsonify({"status": "wait", "score": 5, "message": "Well try! Please wait on your sit for a while"})
            
    # 2. TIMEOUT -> POOL
    if is_timeout:
        # Check if already evaluated, ignore late arrivals or auto-pool them? 
        # Best to just queue them.
        timeout_pool.append({
            "user_id": user_id,
            "score": score,
            "set_num": set_num,
            "time": time.time(),
            "status": "pending",
            "correct_url": f"http://{correct_answers[0]}.{correct_answers[1]}.{correct_answers[2]}.{correct_answers[3]}:{correct_answers[4]}"
        })
        return jsonify({"status": "pooled", "score": score})
        
    # 3. NORMAL SUBMIT -> RETRY
    return jsonify({
        "status": "retry", 
        "score": score, 
        "message": "Access Denied: Incorrect Secret URL. Try again!"
    })

@app.route('/api/admin/status', methods=['GET'])
def admin_status():
    if request.cookies.get('cer_auth_token') != 'authenticated':
        return jsonify({"status": "unauthorized"}), 401
    return jsonify({
        "nxtCount": nxtCount,
        "pool_size": len(timeout_pool),
        "pool_evaluated": pool_evaluated
    })

@app.route('/api/admin/evaluate', methods=['POST'])
def evaluate_pool():
    if request.cookies.get('cer_auth_token') != 'authenticated':
        return jsonify({"status": "unauthorized"}), 401
    global nxtCount, pool_evaluated
    
    if pool_evaluated:
        return jsonify({"status": "already_evaluated"})
        
    sorted_pool = sorted(timeout_pool, key=lambda x: (-x['score'], x['time']))
    
    for p in sorted_pool:
        if p['score'] >= 3 and nxtCount < MAX_ADVANCE:
            p['status'] = 'advance'
            nxtCount += 1
        else:
            p['status'] = 'wait'
            
    pool_evaluated = True
    return jsonify({"status": "success", "total_advanced": nxtCount})

@app.route('/poll_result', methods=['POST'])
def poll_result():
    data = request.json
    user_id = data.get('user_id')
    
    if not pool_evaluated:
        return jsonify({"status": "pending"})
        
    for p in timeout_pool:
        if p['user_id'] == user_id:
            if p['status'] == 'advance':
                return jsonify({"status": "advance_partial", "score": p['score'], "correct_url": p['correct_url']})
            else:
                return jsonify({"status": "wait", "score": p['score']})
                
    return jsonify({"status": "error", "message": "Not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
