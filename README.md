# Cyber-Batch16.1-G4-TIP-Platform

## 🏢 ## 📖 Overview
The Cyber-TIP (Threat Intelligence Platform) is a specialized SOC dashboard designed to bridge the gap between threat reconnaissance and active network defense. It automates the scraping, scoring, and kernel-level enforcement of malicious indicators while providing a transparent administrative interface.

## 🧑‍💻 Group 4 | Batch 16.1
* **Project Lead:** Sreekanthan K N
* **Team Members:** Nikhil S, Sudarshan Mahto, Amaan Roshan, Akanksha Sharma

---
## ✨ Key FeaturesAutomated Intelligence Ingestion: 
Scrapes high-fidelity threat data from AbuseIPDB, AlienVault OTX, and PhishTank.Kernel-Level Enforcement: Automatically pushes high-risk indicators (Score $\ge$ 90) directly to Linux iptables.Ares Pentest Suite: A validation module optimized for 20-IP batch cycles to verify firewall integrity.Live Kernel Visualization: A real-time blocklist that correlates iptables rules with their original intelligence sources and URLs.Surgical Unblocking: Allows administrators to review and remove specific IP blocks without flushing the entire policy.

## 🏗️ System Architecture
The platform utilizes a modular Python/Flask architecture:

Intel Module: Handles data scraping and MongoDB ingestion.

Enforcer Module: Translates DB records into live kernel DROP rules.

Ares Suite: Provides feedback loops through automated penetration testing simulation.

Web GUI: A Flask-based dashboard for real-time monitoring and granular review.
## 📂 Project Structure
```Plaintext
cyber-tip/
├── app.py                      # Main Flask application and GUI routes
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
├── src/                        # Source code directory
│   ├── main.py                 # Entry point for the Intel Update module
│   ├── database/
│   │   └── db_connection.py    # MongoDB connection and configuration
│   ├── processors/
│   │   └── policy_enforcer.py  # Logic for pushing DB records to iptables
│   ├── tests/
│   │   ├── pen_test_sim.py     # Ares Pentest validation logic
│   │   └── auto_pentest.py     # Automated batch testing module
│   ├── utils/
│   │   └── rollback.py         # Script to flush/reset firewall rules
│   └── scrapers/               # Individual intelligence source scripts
│       ├── abuseipdb.py
│       ├── phishtank.py
│       └── alienvault.py
├── templates/                  # Flask HTML templates
│   └── index.html              # Main SOC Dashboard UI
└── static/                     # CSS, JS, and image assets
    ├── css/
    └── js/
```
---
## 🛠️ Installation & Setup
Prerequisites
Python 3.x

MongoDB (local or remote instance)

Linux Environment (required for iptables and sudo permissions)

Deployment
Clone the Repository

```bash
git clone [https://github.com/Infotact-Intern-3Month-F16-1-G4/Cyber-Batch16.1-G4-TIP-Platform.git](https://github.com/Infotact-Intern-3Month-F16-1-G4/Cyber-Batch16.1-G4-TIP-Platform.git)
```
Install Dependencies

```bash
pip install -r requirements.txt
```
Database Configuration
```bash
Update src/database/db_connection.py with your MongoDB URI.
```
Launch the Dashboard

```bash
sudo python3 app.py
```
---

## ⚖️ Governance Model
This project follows a "Rule of Law" governance approach. Every defensive action taken by the platform is backed by an auditable intelligence trail, ensuring that administrators can justify every block and maintain zero collateral impact on legitimate traffic.

---

## 💼 Internship Context
This project was finalized during my internship at Infotact Solutions. It represents a transition from academic research into practical, industry-standard cybersecurity tool development, focusing on automated threat response and network security.
## License: 
MIT / GPLv3

## 🛠️ Prerequisites
Before starting, ensure your system meets these technical requirements:

Operating System: Linux (Ubuntu/Kali preferred) is required for iptables and sudo command execution.

Python: Version 3.x must be installed.

Database: A running instance of MongoDB.

Permissions: You must have sudo privileges to modify kernel firewall rules.

## 🚀 Execution Steps
1. Clone and Prepare the Environment
Open your terminal in VS Code or a standard Linux shell and navigate to your project directory.


# Navigate to your project folder
```bash
cd Cyber-Tip
```

# Install necessary Python libraries
```bash
pip install -r requirements.txt
```
# 2. Configure Database Connectivity
Ensure your src/database/db_connection.py file is pointed to your MongoDB instance so the dashboard can retrieve the AbuseIPDB and AlienVault intelligence records.

# 3. Launch the Platform
Since the platform interacts directly with the Linux kernel to manage the blocklist, you must run it with root privileges.

```bash
sudo python3 -m src.app
```
## 🖥️ Dashboard Operations
Once the script is running, a browser window will automatically open to [http://127.0.0.1:5000](http://127.0.0.1:5000).

Intel Update: Click this to trigger the scraping modules for PhishTank, AbuseIPDB, and AlienVault OTX.

Push Defense: This module analyzes the database and pushes IPs with a Risk Score of 90 or higher to the firewall.

Ares Pentest: Use this to verify that the 20-IP batch is successfully blocked. The process will timeout after 300 seconds if any issues occur.

View Blocklist: Click this to see the Top 50 active blocks correlated with their source names and risk scores.



