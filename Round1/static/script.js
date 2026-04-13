let timerInterval;
let timeLeft = 600; // 10 minutes in seconds
let currentSetNum = null;
let pollInterval;

const setupPanel = document.getElementById('phase-setup');
const taskPanel = document.getElementById('phase-task');
const resultPanel = document.getElementById('phase-result');
const staticOverlay = document.getElementById('tv-static');
const fetchBtn = document.getElementById('btn-fetch');
const submitBtn = document.getElementById('btn-submit');
const setInput = document.getElementById('set-input');

setInput.addEventListener('input', () => {
    const val = parseInt(setInput.value);
    if(val >= 1 && val <= 5) {
        fetchBtn.style.display = 'inline-block';
        document.getElementById('setup-error').classList.add('hidden');
    } else {
        fetchBtn.style.display = 'none';
        if(setInput.value !== "") document.getElementById('setup-error').classList.remove('hidden');
    }
});

fetchBtn.addEventListener('click', () => {
    currentSetNum = setInput.value;
    fetch(`/get_set/${currentSetNum}`)
    .then(r => r.json())
    .then(data => {
        if(data.status === 'success') {
            document.getElementById('display-set').innerText = currentSetNum;
            document.getElementById('dynamic-format').innerText = data.url_format;
            const qContainer = document.getElementById('q-container');
            qContainer.innerHTML = '';
            data.questions.forEach(q => {
                qContainer.innerHTML += `
                    <div class="question">
                        <div class="q-id">[ ${q.id} ]</div>
                        <div class="q-text">${q.text}</div>
                    </div>
                `;
            });
            setupPanel.classList.add('hidden');
            taskPanel.classList.remove('hidden');
            startTimer();
        } else {
            document.getElementById('setup-error').innerText = "System Error fetching set data.";
            document.getElementById('setup-error').classList.remove('hidden');
        }
    });
});

function startTimer() {
    const display = document.getElementById('timer-display');
    timerInterval = setInterval(() => {
        timeLeft--;
        let min = Math.floor(timeLeft / 60);
        let sec = timeLeft % 60;
        display.innerText = `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
        
        if (timeLeft <= 60) {
            display.parentElement.classList.add('hurry');
        }
        
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            display.innerText = "00:00";
            handleSubmission(true);
        }
    }, 1000);
}

function getAnswers() {
    return [
        document.getElementById('o1').value,
        document.getElementById('o2').value,
        document.getElementById('o3').value,
        document.getElementById('o4').value,
        document.getElementById('port').value
    ];
}

let finalTimeTaken = "";

function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

submitBtn.addEventListener('click', () => {
    handleSubmission(false);
});

function handleSubmission(isTimeout) {
    finalTimeTaken = isTimeout ? "10:00" : formatTime(600 - Math.max(0, timeLeft));

    if(!isTimeout) {
        submitBtn.innerText = "VERIFYING...";
        submitBtn.disabled = true;
    } else {
        staticOverlay.classList.remove('hidden'); // Intimidating timeout effect
        submitBtn.style.display = 'none';
        document.getElementById('task-feedback').innerText = "TIME LIMIT EXCEEDED. LOCKING FIREWALL AND TRANSMITTING DATA...";
        document.getElementById('task-feedback').className = 'feedback-msg error-msg shake';
    }

    const payload = {
        set_num: currentSetNum,
        answers: getAnswers(),
        is_timeout: isTimeout,
        user_id: USER_ID
    };

    fetch('/submit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        if(!isTimeout) { submitBtn.innerText = "INITIATE CONNECTION"; submitBtn.disabled = false; }
        
        if(data.status === 'advance_instant') {
            clearInterval(timerInterval);
            showSuccess(data.correct_url, `CLEARED: SCORE 5/5<br><span style="color:var(--primary);">TIME: ${finalTimeTaken}</span>`);
        } 
        else if (data.status === 'retry') {
            const fb = document.getElementById('task-feedback');
            fb.innerText = data.message;
            fb.className = 'feedback-msg error-msg shake';
            setTimeout(() => fb.classList.remove('shake'), 400);
        }
        else if (data.status === 'pooled') {
            // Waitlist state
            taskPanel.classList.add('hidden');
            resultPanel.classList.remove('hidden');
            document.getElementById('res-title').innerText = "PROCESSING";
            document.getElementById('res-desc').innerHTML = `Final Score: ${data.score}/5<br><span style="color:var(--primary);">TIME: ${finalTimeTaken}</span><br><br>Waiting for global round completion to determine standing... Do not close this window.`;
            pollInterval = setInterval(pollEvaluation, 3000);
        }
        else if (data.status === 'wait') {
            clearInterval(timerInterval);
            showFailure(data.score, data.message || "Well try! Please wait on your sit for a while.");
        }
    });
}

function pollEvaluation() {
    fetch('/poll_result', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({user_id: USER_ID})
    })
    .then(r => r.json())
    .then(data => {
        if(data.status === 'advance_partial') {
            clearInterval(pollInterval);
            staticOverlay.classList.add('hidden');
            showSuccess(data.correct_url, `CLEARED: POOL PRIORITY GRANTED<br>SCORE: ${data.score}/5 | <span style="color:var(--primary);">TIME: ${finalTimeTaken}</span>`);
        } else if (data.status === 'wait') {
            clearInterval(pollInterval);
            staticOverlay.classList.add('hidden');
            showFailure(data.score, "Well try! Please wait on your sit for a while.");
        }
    });
}

function showSuccess(url, subText) {
    taskPanel.classList.add('hidden');
    resultPanel.classList.remove('hidden');
    document.getElementById('res-title').innerText = "ACCESS GRANTED";
    document.getElementById('res-title').classList.add('success-color');
    document.getElementById('res-title').style.textShadow = "0 0 10px #0f0";
    document.getElementById('res-desc').innerHTML = subText;
    document.getElementById('res-url-box').classList.remove('hidden');
    document.getElementById('res-url').innerText = url;
}

function showFailure(score, msg) {
    taskPanel.classList.add('hidden');
    resultPanel.classList.remove('hidden');
    document.getElementById('res-title').innerText = "ACCESS DENIED";
    document.getElementById('res-title').style.color = "var(--secondary)";
    document.getElementById('res-title').style.textShadow = "0 0 10px var(--secondary)";
    document.getElementById('res-desc').innerHTML = `Final Score: ${score}/5<br><span style="color:var(--primary);">TIME: ${finalTimeTaken}</span><br><br>${msg}`;
}
