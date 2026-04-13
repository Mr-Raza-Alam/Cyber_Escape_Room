from flask import Flask, render_template, request, jsonify, redirect
import time

app = Flask(__name__)

ADMIN_PASSWORD = 'cyber2026'

# Global State
game_state = {
    'participants': {},
    'round_active': False,
    'round_ended': False,
    'start_time': 0,
    'duration': 15 * 60,
    'attempt_log': []
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    if request.cookies.get('cer_auth_token') != 'authenticated':
        return redirect('http://localhost:5000/')
    return render_template('admin.html')

@app.route('/api/setup', methods=['POST'])
def api_setup():
    if request.cookies.get('cer_auth_token') != 'authenticated':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    participants = data.get('participants') # dict: { "P1": [192, 168, 1, 100], "P2": ... }
    
    if not participants:
        return jsonify({'error': 'No participants provided'}), 400

    # Reset state
    game_state['participants'] = {}
    for name, ip_arr in participants.items():
        game_state['participants'][name] = {
            'target_ip': ip_arr,
            'score': 0,
            'time_taken': 0,
            'submitted_ip': [],
            'submitted_at_formatted': '',
            'completed': False,
            'attempts': 0
        }
    game_state['attempt_log'] = []
    game_state['round_active'] = False
    game_state['round_ended'] = False
    game_state['start_time'] = 0

    return jsonify({'success': True})

@app.route('/api/start', methods=['POST'])
def api_start():
    if request.cookies.get('cer_auth_token') != 'authenticated':
        return jsonify({'error': 'Unauthorized'}), 401
    
    game_state['start_time'] = time.time()
    game_state['round_active'] = True
    game_state['round_ended'] = False
    
    return jsonify({'success': True})

@app.route('/api/status', methods=['GET'])
def api_status():
    now = time.time()
    remaining = 0
    if game_state['round_active'] and not game_state['round_ended']:
        elapsed = now - game_state['start_time']
        remaining = max(0, game_state['duration'] - elapsed)
        if remaining <= 0:
            game_state['round_ended'] = True
            game_state['round_active'] = False
            remaining = 0
    elif game_state['round_ended']:
        remaining = 0
    elif game_state['start_time'] == 0:
        remaining = game_state['duration']

    # Leaderboard logic
    leaderboard = []
    for name, p in game_state['participants'].items():
        if p['completed']:
            leaderboard.append({
                'name': name,
                'score': p['score'],
                'time_taken': p['time_taken'],
                'submitted_ip': p['submitted_ip'],
                'clock_time': p['submitted_at_formatted']
            })
    
    # Sort: Higher score first, then lower time_taken
    leaderboard.sort(key=lambda x: (-x['score'], x['time_taken']))

    return jsonify({
        'round_active': game_state['round_active'],
        'round_ended': game_state['round_ended'],
        'remaining_seconds': int(remaining),
        'participants': {name: p['completed'] for name, p in game_state['participants'].items()},
        'leaderboard': leaderboard,
        'logs': game_state['attempt_log']
    })

@app.route('/api/submit', methods=['POST'])
def api_submit():
    if not game_state['round_active'] and not game_state['round_ended']:
        return jsonify({'error': 'Round not active'})
    if game_state['round_ended']:
        return jsonify({'error': 'Round has ended'})

    data = request.json
    name = data.get('name')
    submitted_ip = data.get('ip') # Should be an array of length 4, empty values are None or ''

    if name not in game_state['participants']:
        return jsonify({'error': 'Participant not found'}), 404

    p = game_state['participants'][name]
    if p['completed']:
        return jsonify({'error': 'Already submitted'}), 400

    p['attempts'] += 1

    target_ip = p['target_ip']  # e.g. [192, 168, 1, 100]
    expected_reversed = list(reversed(target_ip)) # e.g. [100, 1, 168, 192]

    # Calculate score
    score = 0
    for i in range(4):
        try:
            val = submitted_ip[i]
            if val != '' and val is not None and int(val) == expected_reversed[i]:
                score += 1
        except (IndexError, ValueError, TypeError):
            pass

    # Record submission
    now = time.time()
    elapsed = now - game_state['start_time']
    # Even if they got 0 points, we record it if they submit it. Or should we allow multiple attempts?
    # User said "score out of 4... select top 3". And in CER_Round4.html, wrong attempts were just counted, but they could retry until correct.
    # WAIT! Since they can submit partial scores, if they submit a partial score, they are locked in.
    # To prevent locking them if they accidentally make a typo, maybe we should let them submit anytime before round ends?
    # Yes! If they submit, they should be done. Or... The user's HTML allowed retries if it wasn't PERFECT.
    # But now they get points out of 4. So if they submit [100, "", "", ""], they get 1/4. They should probably be able to submit once and that's it, OR retry?
    # If they submit for partial points, they are done. 

    timestamp_str = time.strftime("%I:%M:%S %p")
    
    p['completed'] = True
    p['score'] = score
    p['time_taken'] = elapsed
    p['submitted_ip'] = submitted_ip
    p['submitted_at_formatted'] = timestamp_str

    is_perfect = (score == 4)

    # Convert submitted IP array to string for log
    ip_str_arr = [str(x) if x != '' and x is not None else '_' for x in submitted_ip]
    ip_str = ".".join(ip_str_arr)

    # Log attempt
    time_min = int(elapsed // 60)
    time_sec = int(elapsed % 60)
    game_state['attempt_log'].append({
        'num': len(game_state['attempt_log']) + 1,
        'name': name,
        'ip': ip_str,
        'score': score,
        'perfect': is_perfect,
        'clockTime': timestamp_str,
        'elapsed': f"{time_min:02d}:{time_sec:02d}",
        'attempt': p['attempts']
    })

    return jsonify({
        'success': True,
        'score': score,
        'perfect': is_perfect
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5015)
