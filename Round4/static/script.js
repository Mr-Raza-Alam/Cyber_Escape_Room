let currentParticipant = '';
let roundActive = false;
let roundEnded = false;
let participantsStatus = {}; // { P1: completed_boolean }

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

// Polling loop
setInterval(async () => {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    
    roundActive = data.round_active;
    roundEnded = data.round_ended;
    participantsStatus = data.participants;
    
    // Update timer displays
    const m = Math.floor(data.remaining_seconds / 60);
    const s = data.remaining_seconds % 60;
    const tStr = String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
    
    ['timer-display-1','timer-display-2'].forEach(id => {
      const el = document.getElementById(id);
      if(!el) return;
      el.textContent = tStr;
      el.className = 'timer-value';
      if (data.remaining_seconds <= 300 && data.remaining_seconds > 60) el.classList.add('warning');
      if (data.remaining_seconds <= 60 && data.remaining_seconds > 0) el.classList.add('danger');
    });

    if (roundActive && !roundEnded) {
      const dTitle = document.getElementById('dash-title-text');
      if(dTitle) dTitle.textContent = 'Select your name to access your dashboard';
      buildNameGrid();
    } else if (roundEnded) {
      document.querySelectorAll('.round-ended-banner').forEach(b => b.style.display = 'block');
      ['timer-display-1','timer-display-2'].forEach(id => {
        const el = document.getElementById(id);
        if(!el) return;
        el.textContent = '00:00';
        el.className = 'timer-value danger';
      });
      showLeaderboard(data.leaderboard);
    }

  } catch (e) {
    console.error('Polling error', e);
  }
}, 1000);

function buildNameGrid() {
  const grid = document.getElementById('name-grid');
  if (!grid) return;

  if (grid.children.length === 0 && Object.keys(participantsStatus).length > 0) {
    // First time grid build
    for (const name in participantsStatus) {
      const btn = document.createElement('button');
      btn.className = 'name-btn';
      btn.id = 'namebtn-' + name;
      btn.textContent = name;
      btn.onclick = () => openEntry(name);
      grid.appendChild(btn);
    }
  }
  
  // Update states
  for (const name in participantsStatus) {
    const btn = document.getElementById('namebtn-' + name);
    if (btn && participantsStatus[name]) {
      btn.classList.add('submitted');
      btn.textContent = name + ' ✓';
      btn.onclick = null;
    }
  }
}

function openEntry(name) {
  if (participantsStatus[name] || roundEnded || !roundActive) return;
  currentParticipant = name;
  document.getElementById('entry-participant-name').textContent = name;
  document.getElementById('e1').value = '';
  document.getElementById('e2').value = '';
  document.getElementById('e3').value = '';
  document.getElementById('e4').value = '';
  document.getElementById('ip-preview').textContent = '___.___.___.___';
  document.getElementById('feedback-box').style.display = 'none';
  document.getElementById('submit-btn').style.display = 'block';
  showScreen('screen-entry');
}

function goToDashboard() {
  currentParticipant = '';
  showScreen('screen-dashboard');
}

function updatePreview() {
  const vals = ['e1','e2','e3','e4'].map(id => {
    const el = document.getElementById(id);
    return el && el.value !== '' ? el.value : '___';
  });
  document.getElementById('ip-preview').textContent = vals.join('.');
}

async function submitIP() {
  if (roundEnded) return;
  const vals = ['e1','e2','e3','e4'].map(id => document.getElementById(id).value); // strings, empty if blank

  const fb = document.getElementById('feedback-box');
  fb.style.display = 'none';

  // Validate if entered ranges are valid
  for (let v of vals) {
      if (v !== '') {
          let n = parseInt(v);
          if (isNaN(n) || n < 0 || n > 255) {
              fb.className = 'feedback-box wrong';
              fb.style.background = 'rgba(239,68,68,0.12)';
              fb.style.color = '#ef4444';
              fb.style.border = '1px solid rgba(239,68,68,0.3)';
              fb.textContent = 'Invalid value — each octet must be between 0 and 255.';
              fb.style.display = 'block';
              return;
          }
      }
  }

  if (!confirm('Are you sure you want to submit? You cannot change your answers after submission!')) {
      return;
  }

  // Submit
  const res = await fetch('/api/submit', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ name: currentParticipant, ip: vals })
  });
  const data = await res.json();
  if (data.success) {
    fb.className = 'feedback-box success';
    fb.style.background = 'rgba(0,229,160,0.12)';
    fb.style.color = '#00e5a0';
    fb.style.border = '1px solid rgba(0,229,160,0.3)';
    fb.textContent = `Submission Received! Score: ${data.score}/4`;
    fb.style.display = 'block';
    document.getElementById('submit-btn').style.display = 'none';
    setTimeout(() => goToDashboard(), 3000);
  } else {
    alert(data.error);
  }
}

function showLeaderboard(lb) {
  const sc = document.getElementById('screen-leaderboard');
  if (!sc || sc.classList.contains('active')) return;
  showScreen('screen-leaderboard');
  
  const tbody = document.getElementById('lb-body');
  tbody.innerHTML = '';
  lb.forEach((p, idx) => {
    const tr = document.createElement('tr');
    const rank = idx + 1;
    if (rank <= 3) tr.className = 'rank-' + rank;
    
    const ipStr = p.submitted_ip.map(v => v !== '' && v !== null ? v : '_').join('.');
    const m = Math.floor(p.time_taken / 60);
    const s = Math.floor(p.time_taken % 60);
    const tStr = String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');

    tr.innerHTML = `
      <td>${rank <= 3 ? ['🥇','🥈','🥉'][rank-1] : rank}</td>
      <td>${p.name}</td>
      <td style="font-family:monospace;">${ipStr}</td>
      <td>${p.score}/4</td>
      <td>${tStr}</td>
    `;
    tbody.appendChild(tr);
  });
}
