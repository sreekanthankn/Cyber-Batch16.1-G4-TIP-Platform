# Cyber-Batch16.1-G4-TIP-Platform

## 🏢 Project Overview
[cite_start]This repository contains the **Advanced Threat Intelligence Platform (TIP) & Dynamic Policy Enforcer**, developed for the **Infotact Technical Internship Program**[cite: 3]. [cite_start]Designed for the **Finance & Banking** sector, this system automates the collection of global threat data and enforces defensive configurations autonomously to mitigate zero-day exploits and Advanced Persistent Threats (APTs)[cite: 12, 14, 15].

## 🧑‍💻 Group 4 | Batch 16.1
* **Project Lead:** [Your Name]
* **Team Members:** [Member 2], [Member 3], [Member 4], [Member 5]

---

## 🏗️ Architectural Directives
[cite_start]The system follows a modular architecture to ensure high-volume processing without introducing latency[cite: 23, 34].

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Data Aggregation** | Python (Requests, BeautifulSoup) | [cite_start]Rapid API integrations and OSINT scraping[cite: 35]. |
| **Data Storage** | MongoDB (NoSQL) | [cite_start]Ideal for storing and querying highly variable threat data[cite: 35]. |
| **Policy Enforcement** | Linux iptables / Python Subprocess | [cite_start]Programmatic translation of intelligence into system-level rules[cite: 35]. |
| **Visualization** | ELK Stack (Elasticsearch, Kibana) | [cite_start]Creates a searchable, visual threat landscape for SOC analysts[cite: 42]. |

---

## 📅 4-Week Engineering Roadmap
1. [cite_start]**Week 1: OSINT Ingestion & Database Design** [cite: 37]
   * [cite_start]Python scripts to connect to AlienVault OTX, VirusTotal, and other feeds[cite: 38].
   * [cite_start]Data cleaning, deduplication, and insertion into MongoDB[cite: 39].
2. [cite_start]**Week 2: Normalization & SIEM Integration** [cite: 40]
   * [cite_start]Risk scoring schema and pipe MongoDB data into Elasticsearch[cite: 41, 42].
3. [cite_start]**Week 3: Dynamic Policy Enforcement Engine** [cite: 43]
   * [cite_start]Python daemon to continuously monitor indicators and blacklist threats via `iptables`[cite: 45].
4. [cite_start]**Week 4: Alerting, Testing, & Final Reporting** [cite: 49]
   * [cite_start]Implementation of rollback mechanisms and final Kibana dashboards[cite: 50, 51].

---

## ⚠️ Mandatory Operational Standards
[cite_start]To satisfy the **Evaluation Protocol**, all contributors must adhere to the following[cite: 135]:

* **Commit Consistency:** Evaluation requires all 4 weeks of consistent GitHub commits. [cite_start]Monolithic pushes result in disqualification[cite: 136, 137].
* [cite_start]**Semantic Versioning:** Use prefixes (e.g., `feat:`, `fix:`) and the imperative present tense for messages[cite: 147, 148].
* **Branching Strategy:** Direct commits to `main` are **strictly forbidden**. [cite_start]All changes must use feature branches and squash merges[cite: 150, 152].
* **Data Privacy:** Hardcoding API keys or database credentials is grounds for failure. [cite_start]Use `.env` or GitHub Secrets[cite: 155, 156].

---

## 🚀 Installation & Setup
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/sreekanthankn/Cyber-Batch16.1-G4-TIP-Platform.git](https://github.com/sreekanthankn/Cyber-Batch16.1-G4-TIP-Platform.git)

***2. Configure Environment:***

Create a .env file in the root directory:
```bash
OTX_API_KEY=your_key_here
VT_API_KEY=your_key_here
MONGO_URI=mongodb://localhost:27017/
```
***3. Install Dependencies:***
```bash
pip install -r requirements.txt
```




