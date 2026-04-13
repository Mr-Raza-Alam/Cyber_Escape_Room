document.addEventListener('DOMContentLoaded', () => {
  for(let i=0; i<6; i++) addParticipantRow(i+1); // default 6 rows
});
function addParticipantRow(num = null) {
  const list = document.getElementById('participants-list');
  const count = num || list.children.length + 1;
  const row = document.createElement('div');
  row.className = 'participant-row';
  row.innerHTML = `
    <span class="p-num">${count}</span>
    <input type="text" placeholder="P${count}" class="p-name-input" autocomplete="off"/>
    <input type="number" class="p-ip-input" placeholder="IP 1" min="0" max="255"/>
    <span class="p-dot">.</span>
    <input type="number" class="p-ip-input" placeholder="IP 2" min="0" max="255"/>
    <span class="p-dot">.</span>
    <input type="number" class="p-ip-input" placeholder="IP 3" min="0" max="255"/>
    <span class="p-dot">.</span>
    <input type="number" class="p-ip-input" placeholder="IP 4" min="0" max="255"/>
  `;
  list.appendChild(row);
}

async function setupRound() {
  const rows = document.querySelectorAll('.participant-row');
  const err = document.getElementById('admin-error');
  const succ = document.getElementById('admin-success');
  err.textContent = ''; succ.textContent = '';

  let dict = {};
  for (let r of rows) {
    const name = r.querySelector('.p-name-input').value.trim();
    if (!name) continue;
    const ipInputs = r.querySelectorAll('.p-ip-input');
    const octets = Array.from(ipInputs).map(i => parseInt(i.value));
    if (octets.some(o => isNaN(o) || o < 0 || o > 255)) {
      err.textContent = `Invalid IPv4 for ${name}. Values must be 0-255.`;
      return;
    }
    dict[name] = octets;
  }

  if (Object.keys(dict).length === 0) {
    err.textContent = 'Add at least 1 participant.'; return;
  }

  const res = await fetch('/api/setup', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ participants: dict })
  });
  const data = await res.json();
  if (data.success) {
    succ.textContent = 'Setup saved successfully. Ready to start round.';
    document.getElementById('start-btn').style.display = 'block';
  } else {
    err.textContent = data.error || 'Failed to setup.';
  }
}

async function startRound() {
  const res = await fetch('/api/start', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({})
  });
  const data = await res.json();
  if (data.success) {
    document.getElementById('admin-success').textContent = 'TIMER STARTED!';
    document.getElementById('start-btn').style.display = 'none';
    document.getElementById('log-card').style.display = 'block';
    startPolling();
  }
}

function startPolling() {
  setInterval(async () => {
    const res = await fetch('/api/status');
    const data = await res.json();
    
    const el = document.getElementById('timer-display');
    if (data.round_active) {
      const m = Math.floor(data.remaining_seconds / 60);
      const s = data.remaining_seconds % 60;
      el.textContent = `Time Remaining: ${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
      el.style.color = data.remaining_seconds <= 60 ? '#ef4444' : '#00e5a0';
    } else if (data.round_ended) {
      el.textContent = 'ROUND ENDED';
      el.style.color = '#ef4444';
    }

    // Update logs
    const tbody = document.getElementById('log-body');
    tbody.innerHTML = '';
    data.logs.forEach(l => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${l.num}</td>
        <td>${l.name}</td>
        <td style="font-family:monospace;">${l.ip}</td>
        <td>${l.score}/4</td>
        <td><span class="${l.perfect ? 'badge-correct' : 'badge-wrong'}">${l.perfect ? 'PERFECT' : 'PARTIAL'}</span></td>
        <td>${l.clockTime}</td>
        <td>${l.elapsed}</td>
      `;
      tbody.appendChild(tr);
    });
  }, 1000);
}
