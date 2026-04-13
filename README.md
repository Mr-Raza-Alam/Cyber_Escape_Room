# 🔐 Cyber Escape Room
### A Microservices-Based Competitive Hacking Event Platform

## 📖 Overview
Cyber Escape Room is a full-stack, real-time competitive platform designed to host a multi-round "Cyber Hacker" themed escape room challenge at a university tech fest. The system was designed, built, and coordinated entirely by a single developer under a hard event deadline.

The architecture consists of 5 independent Flask microservices — one Master Orchestration server and four isolated puzzle servers — running cohesively on a Local Area Network to serve live participants simultaneously during a high-pressure competition.

## 🏗️ System Architecture
```text
┌─────────────────────────────────────────────────────┐
│              MASTER ADMIN PORTAL                    │
│         (Cross-Service Auth · Progress Monitor      │
│          · Time Management · Server Routing)        │
│                  Port: 5000                         │
└──────┬──────────┬──────────┬──────────┬────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
  │ Round 1 │ │ Round 2 │ │ Round 3 │ │ Round 4 │
  │  Flask  │ │  Flask  │ │  Flask  │ │  Flask  │
  │ :5005   │ │ :3300   │ │ :5010   │ │ :5015   │
  └─────────┘ └─────────┘ └─────────┘ └─────────┘
  IP Payload  Firewall    Circuit     Hack the
  Assembly    Decryption  Breach      Network
```
Each microservice node operates independently — failure of one puzzle server does not affect the others, ensuring the competition never goes down mid-event.

## 🧩 Puzzle Domains

| Round | Domain | Theme |
| :--- | :--- | :--- |
| **🟢 Round 1** | IP Payload Assembly | **Aptitude & IP Routing** - Assemble fragmented IP packets to reconstruct the payload |
| **🔐 Round 2** | Firewall Decryption Protocol | **Cryptography** - Break through encrypted firewall rules to extract the key |
| **⚡ Round 3** | Circuit Breach | **Hardware / Logic** - Identify faults in logic gate circuits to trigger the breach |
| **💀 Round 4** | Hack the Network | **Final Intrusion** - Navigate a simulated network topology and execute the final hack |

## 🔒 Why LAN Deployment? (Not Public Cloud)
This is a deliberate architectural decision, not a limitation. Three reasons:

1. **🛡️ Anti-Cheat Security**
Hiding the system behind the campus LAN physically restricts access to designated lab machines only. Participants cannot share live URLs with friends outside the room — enforcing a fair, closed competition environment.
2. **⚡ Zero-Latency Reliability**
University tech fests run on heavily congested, unreliable shared Wi-Fi. A LAN deployment bypasses internet bandwidth entirely, guaranteeing uninterrupted, millisecond-level connections to all 5 microservices throughout the event.
3. **🎭 Thematic Authenticity**
Participants connect via raw internal IPs and local ports (e.g., `192.168.x.x:5005`) rather than a polished `.com` domain — immersing them in a genuine "network intrusion" experience that matches the Cyber Hacker theme.

## 🚀 Running Locally (LAN Setup)

**Prerequisites**
* Python 3.8+
* pip

**Installation**
```bash
# Clone the repository
git clone https://github.com/Mr-Raza-Alam/Cyber_Escape_Room.git
cd Cyber_Escape_Room

# Install dependencies
pip install -r requirements.txt
```

**Starting the Servers**
```bash
# Start Master Admin Portal (run first)
python Master_Admin/app.py    # Runs on :5000

# Start each puzzle server (in separate terminals)
python Round1/app.py          # IP Payload Assembly   → :5005
python Round2/app.py          # Firewall Decryption   → :3300
python Round3/app.py          # Circuit Breach        → :5010
python Round4/app.py          # Hack the Network      → :5015
```

**Accessing on LAN**
Once all servers are running, participants connect via:
* `http://<your-local-ip>:5005`   ← Round 1
* `http://<your-local-ip>:3300`   ← Round 2
* `http://<your-local-ip>:5010`   ← Round 3
* `http://<your-local-ip>:5015`   ← Round 4
* `http://<your-local-ip>:5000`   ← Admin Portal (coordinator only)

*Find your local IP:*
```bash
# Windows
ipconfig

# Linux / Mac
ifconfig
```

## 📁 Project Structure
```text
Cyber_Escape_Room/
│
├── Master_Admin/            # Master Admin Portal (Port 5000)
│   ├── app.py
│   ├── templates/
│
├── Round1/                  # IP Payload Assembly (Port 5005)
│   ├── app.py
│   ├── templates/
│   └── static/
│
├── Round2/                  # Firewall Decryption (Port 3300)
│   ├── app.py
│   ├── templates/
│   └── static/
│
├── Round3/                  # Circuit Breach (Port 5010)
│   ├── app.py
│   ├── templates/
│
├── Round4/                  # Hack the Network (Port 5015)
│   ├── app.py
│   ├── templates/
│   └── static/
│
└── README.md
```

## 🛠️ Tech Stack
| Layer | Technology |
| :--- | :--- |
| **Backend** | Python, Flask |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Architecture** | Microservices (5 independent servers) |
| **Session Management** | Flask Sessions |
| **Deployment** | LAN Server (Local Area Network) |
| **Event** | Yantraksh 2026, Assam University Silchar |

## 👨💻 About the Developer
**Raza Alam** — Event Coordinator & Sole Developer  
🎓 B.Tech CSE, 3rd Year — Assam University, Silchar  
💼 [LinkedIn](#)  
🐙 [GitHub](https://github.com/Mr-Raza-Alam)  
📧 alam.raza23.27@gmail.com  

> *"I coordinated the event AND built the platform — because if you want something done right, sometimes you have to build it yourself."*

## 📄 License
This project was built for Yantraksh 2026, Assam University. Feel free to fork and adapt for your own university tech fest.
