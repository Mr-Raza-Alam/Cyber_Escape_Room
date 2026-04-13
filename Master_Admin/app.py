from flask import Flask, render_template, request, make_response, redirect, url_for

app = Flask(__name__)
ADMIN_PASSWORD = 'admin_cer'
AUTH_COOKIE = 'cer_auth_token'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            resp = make_response(redirect(url_for('dashboard')))
            resp.set_cookie(AUTH_COOKIE, 'authenticated', max_age=60*60*24) # 1 day
            return resp
        else:
            return render_template('login.html', error='Invalid Password')
    
    # If already logged in
    if request.cookies.get(AUTH_COOKIE) == 'authenticated':
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if request.cookies.get(AUTH_COOKIE) != 'authenticated':
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie(AUTH_COOKIE, '', expires=0)
    return resp

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
