from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import time
import os
import random

app = Flask(__name__)
# Secure random key for session encryption
app.secret_key = os.urandom(24)

# Global Configuration
ROUND_TIME_LIMIT = 12 * 60  # 12 minutes in seconds
PENALTY_TIME = 10  # 10 seconds penalty for wrong answers

# True Content - C and Python questions (8 questions)
QUESTIONS = {
    'c': [
        {'id': 'c1', 'answer': '12', 'difficulty': 'easy'},
        {'id': 'c2', 'answer': 'F', 'difficulty': 'easy'},
        {'id': 'c3', 'answer': 'DATA', 'difficulty': 'easy'},
        {'id': 'c4', 'answer': '20', 'difficulty': 'medium'},
        {'id': 'c5', 'answer': 'HaCKER', 'difficulty': 'medium'},
        {'id': 'c6', 'answer': '8', 'difficulty': 'medium'},
        {'id': 'c7', 'answer': '11', 'difficulty': 'medium'},
        {'id': 'c8', 'answer': 'ReCt10N', 'difficulty': 'hard'},
        {'id': 'c9', 'answer': '7', 'difficulty': 'easy'},
        {'id': 'c10', 'answer': '100', 'difficulty': 'easy'},
        {'id': 'c11', 'answer': 'AYBYCY', 'difficulty': 'medium'},
        {'id': 'c12', 'answer': '24', 'difficulty': 'hard'},
    ],
    'py': [
        {'id': 'py1', 'answer': 'KEYKEYKE', 'difficulty': 'easy'},
        {'id': 'py2', 'answer': '464', 'difficulty': 'easy'},
        {'id': 'py3', 'answer': '19210', 'difficulty': 'easy'},
        {'id': 'py4', 'answer': 'SFW', 'difficulty': 'medium'},
        {'id': 'py5', 'answer': '8', 'difficulty': 'medium'},
        {'id': 'py6', 'answer': '-2', 'difficulty': 'medium'},
        {'id': 'py7', 'answer': 'RCYBE', 'difficulty': 'medium'},
        {'id': 'py8', 'answer': 'CCOCOD', 'difficulty': 'hard'},
        {'id': 'py9', 'answer': '24', 'difficulty': 'easy'},
        {'id': 'py10', 'answer': '2', 'difficulty': 'easy'},
        {'id': 'py11', 'answer': '5', 'difficulty': 'medium'},
        {'id': 'py12', 'answer': '2', 'difficulty': 'hard'},
    ]
}

# Each URL maps to a fixed set number (1-5) for anti-cheat
VALID_SECRET_URLS = {
    "http://3.3.10.28:3939":   1,  # set-1
    "http://36.53.10.3:1300":  2,  # set-2
    "http://34.104.10.6:247":  3,  # set-3
    "http://13.53.73.224:216": 4,  # set-4
    "http://7.53.3.28:4":      5,  # set-5
}

# Fixed 8-question sets per language — each set uses a different slice
# so participants with different URLs cannot share answers
QUESTION_SETS = {
    'c': {
        1: ['c1',  'c2',  'c3',  'c4',  'c5',  'c6',  'c7',  'c8' ],
        2: ['c2',  'c3',  'c4',  'c5',  'c6',  'c7',  'c8',  'c9' ],
        3: ['c3',  'c4',  'c5',  'c6',  'c7',  'c8',  'c9',  'c10'],
        4: ['c4',  'c5',  'c6',  'c7',  'c8',  'c9',  'c10', 'c11'],
        5: ['c5',  'c6',  'c7',  'c8',  'c9',  'c10', 'c11', 'c12'],
    },
    'py': {
        1: ['py1',  'py2',  'py3',  'py4',  'py5',  'py6',  'py7',  'py8' ],
        2: ['py2',  'py3',  'py4',  'py5',  'py6',  'py7',  'py8',  'py9' ],
        3: ['py3',  'py4',  'py5',  'py6',  'py7',  'py8',  'py9',  'py10'],
        4: ['py4',  'py5',  'py6',  'py7',  'py8',  'py9',  'py10', 'py11'],
        5: ['py5',  'py6',  'py7',  'py8',  'py9',  'py10', 'py11', 'py12'],
    }
}

@app.route('/')
def home_page():
    """Entry page asking for Round-1 Secret URL."""
    error = request.args.get('error')
    return render_template('home.html', error=error)

@app.route('/verify_code', methods=['POST'])
def verify_code():
    """Verify the Round-1 Secret URL and assign the participant's question set."""
    code = request.form.get('secret_code', '').strip().lower()

    # Auto-prepend http:// if the participant forgets it
    if not code.startswith("http://"):
        code = "http://" + code

    if code in VALID_SECRET_URLS:
        session['verified_round1'] = True
        session['set_number'] = VALID_SECRET_URLS[code]  # Store their assigned set
        return redirect(url_for('wait_page'))
    else:
        return redirect(url_for('home_page', error=f'ACCESS DENIED: Invalid URL ({code}).'))

@app.route('/wait')
def wait_page():
    """Wait page telling participants to wait for briefing."""
    if not session.get('verified_round1'):
        return redirect(url_for('home_page'))
        
    error = request.args.get('error')
    return render_template('wait.html', error=error)

@app.route('/start', methods=['POST'])
def start_round():
    """Transition from Wait Page to Language Selection after Briefing."""
    pin = request.form.get('pin')
    if pin != '4159':
        return redirect(url_for('wait_page', error='ACCESS DENIED: Invalid PIN.'))
        
    return render_template('select.html')

@app.route('/select_language', methods=['POST'])
def select_language():
    """Participant selects C or Python, initializing their secure session."""
    lang = request.form.get('language')
    if lang not in ['c', 'py']:
        return redirect(url_for('wait_page'))
    
    # Initialize the session state securely on the server
    session['language'] = lang
    session['start_time'] = time.time()
    session['solved'] = []
    session['penalty_until'] = 0
    session['wrong_attempts'] = 0  # Track wrong submissions for tiebreaking

    # Use the pre-assigned set (from URL verification) to pick exactly 8 questions
    set_number = session.get('set_number', 1)
    session['question_ids'] = QUESTION_SETS[lang][set_number]

    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Main challenge arena where codes are displayed."""
    # Ensure they went through the proper start flow
    if 'start_time' not in session or 'language' not in session:
        return redirect(url_for('wait_page'))
    
    elapsed = time.time() - session['start_time']
    remaining = ROUND_TIME_LIMIT - elapsed
    
    # Check if timer expired — redirect to scorecard
    if remaining <= 0:
        return redirect(url_for('result'))
        
    lang = session['language']
    
    # Retrieve the unique 8 questions assigned to this participant
    q_ids = session.get('question_ids', [])
    all_questions = QUESTIONS[lang]
    
    # Rebuild the dynamically shuffled list of 8
    questions = []
    for target_id in q_ids:
        for q in all_questions:
            if q['id'] == target_id:
                questions.append(q)
                break
    
    # If they somehow access dashboard after finishing all
    if len(session['solved']) == len(questions):
        return redirect(url_for('result'))
        
    return render_template('dashboard.html', 
                          questions=questions, 
                          solved=session['solved'],
                          solved_count=len(session['solved']),
                          remaining=int(remaining),
                          lang=lang)

@app.route('/submit', methods=['POST'])
def submit_answer():
    """Ajax endpoint for verifying submitted answers."""
    if 'start_time' not in session:
        return jsonify({'status': 'error', 'message': 'Session expired. Please refresh.'})
        
    elapsed = time.time() - session['start_time']
    if elapsed > ROUND_TIME_LIMIT:
        return jsonify({'status': 'timeout', 'message': 'Time is up!'})
        
    # Check for active 5-second penalty cooldown
    current_time = time.time()
    if session.get('penalty_until', 0) > current_time:
        wait_time = int(session['penalty_until'] - current_time)
        return jsonify({'status': 'penalty', 'message': f'Wait {wait_time}s'})

    data = request.json
    q_id = data.get('question_id')
    user_answer = str(data.get('answer')).strip()
    
    lang = session['language']
    
    # Find the target question from server-side dictionary (cannot be inspected)
    target_q = next((q for q in QUESTIONS[lang] if q['id'] == q_id), None)
    
    if not target_q:
        return jsonify({'status': 'error', 'message': 'Invalid question ID'})
        
    # Validate Answer
    if user_answer == target_q['answer']:
        if q_id not in session['solved']:
            # Mark as solved
            solved_list = session.get('solved', [])
            solved_list.append(q_id)
            session['solved'] = solved_list
            
        is_complete = len(session['solved']) == len(session.get('question_ids', []))
        return jsonify({'status': 'correct', 'is_complete': is_complete})
    else:
        # Apply the penalty and track wrong attempts for tiebreaking
        session['wrong_attempts'] = session.get('wrong_attempts', 0) + 1
        session['penalty_until'] = current_time + PENALTY_TIME
        return jsonify({'status': 'incorrect', 'penalty': PENALTY_TIME})

@app.route('/result')
def result():
    """Intermediate scorecard screen shown after Final Submit/Decrypt."""
    if 'start_time' not in session:
        return redirect(url_for('wait_page'))

    elapsed = time.time() - session['start_time']
    time_taken = int(min(elapsed, ROUND_TIME_LIMIT))
    score = len(session.get('solved', []))
    total = len(session.get('question_ids', [8]))
    wrong = session.get('wrong_attempts', 0)

    return render_template('result.html',
                           score=score,
                           total=total,
                           time_taken=time_taken,
                           wrong_attempts=wrong)

@app.route('/verdict')
def verdict():
    """Final verdict screen — tiered by score (8/8, 6-7, <6)."""
    if 'start_time' not in session:
        return redirect(url_for('wait_page'))

    score = len(session.get('solved', []))
    elapsed = time.time() - session['start_time']
    time_taken = int(min(elapsed, ROUND_TIME_LIMIT))
    wrong = session.get('wrong_attempts', 0)

    # Assign random physical location only for perfect score
    packet_id = None
    if score == 8:
        if 'packet_id' not in session:
            locations = {
                'Subnet-2': [3, 6, 9, 16, 25, 38, 45, 52, 37],
                'Subnet-4': [11, 4, 6, 19, 25, 34, 29]
            }
            hall = random.choice(list(locations.keys()))
            seat = random.choice(locations[hall])
            session['packet_id'] = f"{hall}, Node {seat}"
        packet_id = session['packet_id']

    return render_template('verdict.html',
                           score=score,
                           time_taken=time_taken,
                           wrong_attempts=wrong,
                           packet_id=packet_id)

@app.route('/success')
def success():
    """Legacy redirect — now points to result screen."""
    return redirect(url_for('result'))

if __name__ == '__main__':
    # Listen on all active interfaces to allow lab computers to connect
    app.run(host='0.0.0.0', port=3300, debug=True)
