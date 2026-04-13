let timeRemaining = typeof initialRemaining !== 'undefined' ? initialRemaining : 0;
let solvedCount = typeof initialSolved !== 'undefined' ? initialSolved : 0;
let penaltyCooldown = 0;

// Update timer display
function updateTimer() {
    if (timeRemaining <= 0) {
        // Time's up — go to scorecard instead of blank reload
        window.location.href = '/result';
        return;
    }
    
    let mins = Math.floor(timeRemaining / 60);
    let secs = Math.floor(timeRemaining % 60);
    
    document.getElementById('timer').innerText = 
        `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    
    timeRemaining--;
}

// Global Penalty Cooldown Display
function updateCooldowns() {
    if (penaltyCooldown > 0) {
        let buttons = document.querySelectorAll('.submit-btn');
        buttons.forEach(btn => {
            btn.disabled = true;
            btn.innerText = `LOCKED (${Math.ceil(penaltyCooldown)}s)`;
        });
        penaltyCooldown--;
    } else {
        let buttons = document.querySelectorAll('.submit-btn');
        buttons.forEach(btn => {
            btn.disabled = false;
            btn.innerText = `Verify`;
        });
    }
}

// Start intervals if we are on the dashboard
if (document.getElementById('timer')) {
    updateTimer();
    setInterval(updateTimer, 1000);
    setInterval(updateCooldowns, 1000);
}

// Submit via AJAX to prevent page reload and keep timer smooth
function submitAnswer(questionId) {
    if (penaltyCooldown > 0) return; // Prevent double clicks during cooldown
    
    const answerInput = document.getElementById(`ans_${questionId}`);
    const answer = answerInput.value;
    const msgDiv = document.getElementById(`msg_${questionId}`);
    
    if (answer.trim() === '') {
        msgDiv.innerText = "Please enter an output.";
        msgDiv.className = "status-msg error-text";
        return;
    }

    // Indicate loading
    msgDiv.innerText = "Verifying...";
    msgDiv.className = "status-msg";

    // Attempt Verification via AJAX
    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question_id: questionId, answer: answer })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'correct') {
            msgDiv.innerText = "ACCESS GRANTED. Module decrypted.";
            msgDiv.className = "status-msg correct-text";
            answerInput.disabled = true;
            document.querySelector(`#card_${questionId} .submit-btn`).style.display = 'none';
            document.getElementById(`card_${questionId}`).style.borderColor = '#39ff14';
            document.getElementById(`card_${questionId}`).style.opacity = '0.7';
            
            if (data.is_complete) {
                // All 8 solved — show green Final Decrypt, hide amber partial button
                solvedCount = 8;
                document.getElementById('partial-submit').style.display = 'none';
                document.getElementById('final-submit').style.display = 'block';
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            } else {
                // Update solved count and show/hide appropriate buttons
                solvedCount++;
                if (solvedCount >= 6) {
                    document.getElementById('partial-submit').style.display = 'block';
                    // Update the button text to reflect current count
                    const partialBtn = document.querySelector('#partial-submit button');
                    if (partialBtn) partialBtn.innerText = `⚡ SUBMIT FINAL SCORE (${solvedCount}/8 Solved)`;
                }
            }
        } else if (data.status === 'incorrect') {
            msgDiv.innerText = "ACCESS DENIED. Incorrect Output.";
            msgDiv.className = "status-msg error-text";
            penaltyCooldown = data.penalty; // Trigger global cooldown
            answerInput.value = '';
        } else if (data.status === 'penalty') {
            msgDiv.innerText = data.message;
            msgDiv.className = "status-msg error-text";
        } else if (data.status === 'timeout') {
            window.location.reload();
        } else {
            msgDiv.innerText = data.message;
            msgDiv.className = "status-msg error-text";
        }
    })
    .catch(error => {
        console.error('Error:', error);
        msgDiv.innerText = "Connection Error.";
        msgDiv.className = "status-msg error-text";
    });
}

// Intense Anti-Cheat: Block Keyboard Shortcuts
document.addEventListener('keydown', function(e) {
    // Block F12, Ctrl+Shift+I (DevTools), Ctrl+U (View Source), Ctrl+S (Save), Ctrl+C (Copy), Ctrl+P (Print)
    if (e.key === 'F12' || 
       (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J' || e.key === 'C')) || 
       (e.ctrlKey && (e.key === 'u' || e.key === 'U' || e.key === 's' || e.key === 'S' || e.key === 'c' || e.key === 'C' || e.key === 'p' || e.key === 'P'))) {
        e.preventDefault();
        return false;
    }
});

// Full-Screen Immersion Helper
function enterFullScreen() {
    let elem = document.documentElement;
    if (elem.requestFullscreen) {
        elem.requestFullscreen().catch(err => console.warn("Fullscreen blocked until next click."));
    } else if (elem.webkitRequestFullscreen) { /* Safari */
        elem.webkitRequestFullscreen();
    }
}
