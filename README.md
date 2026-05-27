# 🛡️ CyberKill Exposure Platform — Backend

> Αυτόματη χαρτογράφηση και αξιολόγηση ασφάλειας εκτεθειμένων υποδομών στο Διαδίκτυο με χρήση LLM Agent και ανοιχτών OSINT πηγών.

---

## 📖 Περιγραφή

Το **CyberKill Exposure Platform** είναι ένα ολοκληρωμένο σύστημα κυβερνοασφάλειας που αναπτύχθηκε στο πλαίσιο πτυχιακής εργασίας. Επιτρέπει την αυτόματη ανακάλυψη, εμπλουτισμό και αξιολόγηση εκτεθειμένων ψηφιακών υποδομών αξιοποιώντας αποκλειστικά δημόσια διαθέσιμα δεδομένα.

Το κύριο στοιχείο καινοτομίας είναι ο **LLM Agent** — ένας αυτόνομος πράκτορας που δέχεται ερωτήματα φυσικής γλώσσας (ελληνικά ή αγγλικά), τα αναλύει σημασιολογικά και τα μετατρέπει ταυτόχρονα σε queries για τρεις διαφορετικές πλατφόρμες OSINT.

---

## 🏗️ Αρχιτεκτονική

```
User (Natural Language Query)
        ↓
   LLM Agent (Groq/LLaMA-3)
        ↓
┌───────────────────────────┐
│  Shodan  │ ZoomEye │ FOFA │  ← Parallel execution
└───────────────────────────┘
        ↓
   Risk Scoring Engine
        ↓
   CVE Enrichment (NVD)
        ↓
   SQLite Database
        ↓
   REST API (FastAPI)
        ↓
   NEX Dashboard (React)
```

---

## 🚀 Τεχνολογίες

| Κατηγορία | Τεχνολογία |
|-----------|------------|
| Backend Framework | FastAPI |
| LLM Agent | Groq API (LLaMA-3.3-70b) |
| OSINT Sources | Shodan, ZoomEye, FOFA |
| CVE Database | NVD (NIST) |
| Database | SQLite + SQLAlchemy |
| Server | Uvicorn |
| Language | Python 3.12+ |

---

## 📁 Δομή Project

```
cyber-exposure-backend/
├── src/
│   ├── main.py                 # FastAPI app & middleware
│   ├── settings.py             # Configuration
│   ├── database.py             # SQLAlchemy models & DB setup
│   ├── routers/
│   │   ├── scans.py            # Scan endpoints
│   │   ├── assets.py           # Asset endpoints
│   │   └── vulnerability.py    # Vulnerability endpoints
│   ├── services/
│   │   ├── llm_agent.py        # LLM Agent (NL → queries)
│   │   ├── shodan_client.py    # Shodan API client
│   │   ├── zoomeye_client.py   # ZoomEye API client
│   │   ├── fofa_client.py      # FOFA API client
│   │   └── cve_client.py       # NVD CVE enrichment
│   └── utils/
│       └── risk_scoring.py     # Risk scoring algorithm
├── .env                        # API keys (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Εγκατάσταση

### Προαπαιτούμενα
- Python 3.12+
- pip

### Βήματα

```bash
# 1. Clone το repository
git clone https://github.com/ManosBiliouris/cyber-exposure-backend.git
cd cyber-exposure-backend

# 2. Δημιούργησε virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Εγκατάστησε dependencies
pip install -r requirements.txt

# 4. Δημιούργησε .env αρχείο
cp .env.example .env
# Συμπλήρωσε τα API keys σου
```

### .env αρχείο
```env
SHODAN_API_KEY=your_shodan_key
ZOOMEYE_API_KEY=your_zoomeye_key
FOFA_EMAIL=your_fofa_email
FOFA_API_KEY=your_fofa_key
GROQ_API_KEY=your_groq_key
```

### Εκκίνηση
```bash
uvicorn src.main:app --reload
```

Το API είναι διαθέσιμο στο: `http://127.0.0.1:8000`  
Swagger UI: `http://127.0.0.1:8000/docs`

---

## 🔌 API Endpoints

### Scans
| Method | Endpoint | Περιγραφή |
|--------|----------|-----------|
| `POST` | `/scan/run` | Εκτέλεση νέου scan με NL query |
| `GET` | `/scan/last` | Τελευταίο scan |
| `GET` | `/scan/history` | Ιστορικό όλων των scans |

### Assets
| Method | Endpoint | Περιγραφή |
|--------|----------|-----------|
| `GET` | `/assets/` | Όλα τα assets |
| `GET` | `/assets/{id}` | Λεπτομέρειες asset |
| `POST` | `/assets/ingest` | Εισαγωγή assets από scan |

### Vulnerabilities
| Method | Endpoint | Περιγραφή |
|--------|----------|-----------|
| `GET` | `/vulnerabilities/` | Όλες οι ευπάθειες |
| `POST` | `/vulnerabilities/ingest` | Εισαγωγή ευπαθειών |

---

## 🧠 LLM Agent

Ο LLM Agent χρησιμοποιεί το **LLaMA-3.3-70b** μέσω Groq API για να μετατρέπει φυσική γλώσσα σε OSINT queries:

**Παράδειγμα:**
```
Input:  "εκτεθειμένοι Redis servers στην Ελλάδα"

Output:
  Shodan:  "redis port:6379 country:GR"
  ZoomEye: "app:redis port:6379 country:GR"
  FOFA:    "app=\"Redis\" && port=\"6379\" && country=\"GR\""
```

Τα queries εκτελούνται **παράλληλα** με `ThreadPoolExecutor` για μέγιστη ταχύτητα.

---

## 📊 Risk Scoring

Ο αλγόριθμος βαθμολόγησης λαμβάνει υπόψη:
- **Port risk** (π.χ. RDP=90, Redis=95, HTTPS=10)
- **Service risk** (π.χ. Telnet=95, SSH=35)
- **Vulnerability findings**

```
Risk Score = max(port_risk, service_risk) × 0.7 + vuln_score × 0.3
```

| Score | Level |
|-------|-------|
| 75-100 | 🔴 Critical |
| 50-74 | 🟠 High |
| 25-49 | 🟡 Medium |
| 0-24 | 🟢 Low |

---

## 🔍 CVE Enrichment

Αυτόματος εμπλουτισμός ευπαθειών με δεδομένα από το **NIST NVD**:
- CVE ID
- CVSS Score
- Περιγραφή
- Severity level

---

## 🖥️ Frontend

Το dashboard (NEX Security Platform) βρίσκεται στο:  
👉 https://github.com/ManosBiliouris/nex-dashboard-hub

---

## 👨‍💻 Ανάπτυξη

**Manos Biliouris**  
Πτυχιακή Εργασία — Τμήμα Πληροφορικής  
2025-2026

---

## 📄 Άδεια

MIT License
