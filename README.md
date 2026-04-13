# Cyber Escape Room (Microservices Web Application)

**Tech Stack:** Python, Flask, Javascript, HTML/CSS

Architected and developed a full-stack technical escape room using a Microservices ecosystem for Yantraksh 2026. The backend consists of 5 independent Flask web servers interacting cohesively, ensuring resilient fail-safes and session handling to manage concurrent users during an intense, high-pressure competitive event.

## 🧩 The Puzzle Domains
Implemented decentralized application logic across 4 distinct, independent puzzle domains matching the "Cyber Hacker" theme:
* **Round 1:** IP Payload Assembly (Aptitude & IP Routing)
* **Round 2:** Firewall Decryption Protocol (Cryptography)
* **Round 3:** Circuit Breach (Hardware/Logic Verification)
* **Round 4:** Hack the Network (Final Intrusion)

## 🎛️ Master Orchestration
Designed a centralized **Master Admin Portal** to handle cross-service authentication, globally monitor participant progress, and orchestrate time-sensitive server routing. The decentralized microservice nodes prevent a single point of failure from ever taking down the entire tournament.

## 🔒 Deployment Architecture (LAN-Only)
This project is designed specifically to run on a **Local Area Network (LAN Server)** rather than being deployed to the public World Wide Web. 

**Why Local Deployment over Global Web Deployment?**
1. **Anti-Cheat Security:** By strictly hiding the system from the global internet, we eliminate the risk of participants sharing their live URLs with friends outside the designated escape room (who could otherwise cheat on their behalf). Access is physically restricted to the designated lab machines inside the room.
2. **Zero-Latency Reliability:** Campus festivals always suffer from heavily congested, unreliable Wi-Fi. A local deployment bypasses the college's internet bandwidth, guaranteeing uninterrupted, lightning-fast connections to the microservices.
3. **Thematic Authenticity:** Forcing participants to navigate raw internal IP Addresses and local ports (e.g., connecting to `192.168.x.x:5001`) rather than a polished `.com` domain provides a much more authentic, raw "network intrusion" experience.
