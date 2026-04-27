# Cyber-Batch16.1-G4-TIP-Platform

## 🏢 Project Overview
This repository contains the **Advanced Threat Intelligence Platform (TIP) & Dynamic Policy Enforcer**, developed for the **Infotact Technical Internship Program**. Designed for the **Finance & Banking** sector, this system automates the collection of global threat data and enforces defensive configurations autonomously to mitigate zero-day exploits and Advanced Persistent Threats (APTs).

## 🧑‍💻 Group 4 | Batch 16.1
* **Project Lead:** Sreekanthan K N
* **Team Members:** Nikhil S, Sudarshan Mahto, Amaan Roshan, Akanksha Sharma

### ✅ Completed Milestones:
* **DNS Resolution Engine**: Integrated logic to resolve malicious domains and phishing URLs into numerical IPv4 addresses for infrastructure-level blocking.
* **Geo-IP & ASN Enrichment**: Automated mapping of indicators to geographic locations (Country, City) and network providers (ISP, ASN).
* **Modular Pipeline**: Updated the core orchestrator to handle multi-stage processing (Ingestion -> Normalization -> Enrichment).
* **Database Auditing**: Implemented a verification tool to monitor data health and enrichment success rates.

### 📁 Updated Project Structure:
```text
src/
├── database/
│   ├── db_connection.py       # MongoDB Connection logic
│   └── verify_enrichment.py   # NEW: Enrichment health auditor
├── processors/
│   ├── normalizer.py          # Schema standardization
│   └── enricher.py            # NEW: Geo-IP & DNS Resolution Engine
├── scrapers/                  # OSINT Data Collectors (OTX, AbuseIPDB, PhishTank)
└── main.py                    # Core Platform Orchestrator
```
How to Run:
Full Pipeline (Ingestion + Enrichment):

Bash
python3 -m src.main
Verify Data Health:

Bash
python3 -m src.database.verify_enrichment
📅 Previous Progress (Week 2)
AlienVault OTX: Integrated and normalized.

AbuseIPDB: Integrated and normalized.

PhishTank: Integrated and normalized.

Database: MongoDB (CyberTIP_Platform) established.
Team : CYBER_SECURITY_THREE_MONTHS_BATCH-16.1  Group : G-4

### Contributors :
1. Sreekanthan K N
2. Amaan Roshan
3. Sudarshan Mahto
4. Nikhil S
>>>>>>> Stashed changes
