from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import json
import time
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

PARTICIPANTS_FILE = 'participants.json'
ADMIN_PASSWORD = 'admin_cer'
ROUND_TIME_LIMIT = 12 * 60  # 12 minutes

CORRECT_CODES = {
    "1": "-14",
    "2": "10",
    "3": "23",
    "4": "8"
}

def load_participants():
    if not os.path.exists(PARTICIPANTS_FILE):
        return []
    with open(PARTICIPANTS_FILE, 'r') as f:
        return json.load(f)

def save_participants(data):
    with open(PARTICIPANTS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def participant_login():
    name = request.form.get('name').strip().upper()
    participants = load_participants()
    
    user = next((p for p in participants if p['name'] == name), None)
    if user:
        session['user_name'] = name
        if not user.get('start_time'):
            user['start_time'] = time.time()
            save_participants(participants)
        return redirect(url_for('dashboard'))
    
    return render_template('login.html', error="ACCESS DENIED: Agent Name not found in system.")

@app.route('/dashboard')
def dashboard():
    if 'user_name' not in session:
        return redirect(url_for('home'))
        
    name = session['user_name']
    participants = load_participants()
    user = next((p for p in participants if p['name'] == name), None)
    
    if not user:
        return redirect(url_for('home'))
        
    elapsed = time.time() - user.get('start_time', time.time())
    remaining = max(0, ROUND_TIME_LIMIT - elapsed)
    
    return render_template('circuit_verification.html', 
                           name=name, 
                           set_number=user['set'], 
                           remaining=int(remaining),
                           status=user.get('status', 'pending'),
                           time_taken=user.get('time_taken', 0))

@app.route('/verify', methods=['POST'])
def verify():
    if 'user_name' not in session:
        return jsonify({"status": "error", "message": "Session expired."}), 401
        
    data = request.json
    set_num = str(data.get('set_num'))
    code = str(data.get('code')).strip()
    
    name = session['user_name']
    participants = load_participants()
    user = next((p for p in participants if p['name'] == name), None)
    
    if not user:
        return jsonify({"status": "error", "message": "User not found."}), 404
        
    # Check if time is up
    elapsed = time.time() - user.get('start_time', time.time())
    if elapsed > ROUND_TIME_LIMIT:
        user['status'] = 'failed_timeout'
        save_participants(participants)
        return jsonify({"status": "timeout", "message": "SYSTEM LOCKDOWN: TIME EXPIRED."})

    # Validate Set and Code
    if set_num == str(user['set']) and code == CORRECT_CODES.get(set_num):
        user['status'] = 'success'
        user['time_taken'] = int(elapsed)
        save_participants(participants)
        return jsonify({
            "status": "success", 
            "message": "You have successfully breached the circuit \n Your last packet location is Central System Room at AE dept."
        })
    else:
        return jsonify({"status": "error", "message": "ACCESS DENIED: INVALID CIRCUIT CODE."})

# Admin Routes
@app.route('/admin')
def admin():
    if request.cookies.get('cer_auth_token') != 'authenticated':
        return redirect('http://localhost:5000/')
    return render_template('admin.html', participants=load_participants())

@app.route('/api/admin/add', methods=['POST'])
def add_participant():
    if request.cookies.get('cer_auth_token') != 'authenticated': return jsonify({"status": "failed"}), 401
    
    name = request.form.get('name').strip().upper()
    set_num = int(request.form.get('set'))
    
    participants = load_participants()
    if any(p['name'] == name for p in participants):
        return jsonify({"status": "error", "message": "Agent already exists."})
        
    participants.append({
        "name": name,
        "set": set_num,
        "status": "pending",
        "start_time": None
    })
    save_participants(participants)
    return redirect(url_for('admin'))

@app.route('/api/admin/clear', methods=['POST'])
def clear_data():
    if request.cookies.get('cer_auth_token') != 'authenticated': return jsonify({"status": "failed"}), 401
    save_participants([])
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)
