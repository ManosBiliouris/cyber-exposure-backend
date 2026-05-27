# 🛡️ CyberKill Exposure Platform — Backend

> Αυτόματη χαρτογράφηση και αξιολόγηση ασφάλειας εκτεθειμένων υποδομών στο Διαδίκτυο με χρήση LLM Agent, ML προγνωστικών μοντέλων και ανοιχτών OSINT πηγών.

---

## 📖 Περιγραφή

Το **CyberKill Exposure Platform** είναι ένα ολοκληρωμένο σύστημα κυβερνοασφάλειας που αναπτύχθηκε στο πλαίσιο πτυχιακής εργασίας. Επιτρέπει την αυτόματη ανακάλυψη, εμπλουτισμό και αξιολόγηση εκτεθειμένων ψηφιακών υποδομών αξιοποιώντας αποκλειστικά δημόσια διαθέσιμα δεδομένα.

Το κύριο στοιχείο καινοτομίας είναι ο **LLM Agent** — ένας αυτόνομος πράκτορας που δέχεται ερωτήματα φυσικής γλώσσας (ελληνικά ή αγγλικά), τα αναλύει σημασιολογικά και τα μετατρέπει ταυτόχρονα σε queries για τρεις διαφορετικές πλατφόρμες OSINT, σε συνδυασμό με **ML μοντέλο** που προβλέπει την πιθανότητα compromise κάθε asset.

---

## 🏗️ Αρχιτεκτονική

```
User (Natural Language Query)
        ↓
   LLM Agent (Groq/LLaMA-3.3-70b)
        ↓
┌─────────────────────────────────────┐
│  Shodan  │  ZoomEye  │    FOFA      │  ← Parallel execution
└─────────────────────────────────────┘
        ↓
   Credential Manager (Rotating Keys)
        ↓
   Proxy Manager (Proxy Pool)
        ↓
   Risk Scoring Engine
        ↓
   CVE Enrichment (NVD/NIST)
        ↓
   ML Predictor (Random Forest)
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
| LLM Agent | Groq API (LLaMA-3.3-70b-versatile) |
| OSINT Sources | Shodan, ZoomEye, FOFA |
| CVE Database | NVD (NIST) |
| ML Model | scikit-learn (Random Forest) |
| Database | SQLite + SQLAlchemy |
| Server | Uvicorn |
| Language | Python 3.12+ |

---

## 📁 Δομή Project

```
cyber-exposure-backend/
├── src/
│   ├── main.py                    # FastAPI app, middleware & ML endpoints
│   ├── settings.py                # Configuration
│   ├── database.py                # SQLAlchemy models & DB setup
│   ├── routers/
│   │   ├── scans.py               # Scan endpoints + history
│   │   ├── assets.py              # Asset endpoints
│   │   └── vulnerability.py       # Vulnerability + CVE endpoints
│   ├── services/
│   │   ├── llm_agent.py           # LLM Agent (NL → queries, parallel exec)
│   │   ├── shodan_client.py       # Shodan API client
│   │   ├── zoomeye_client.py      # ZoomEye API client
│   │   ├── fofa_client.py         # FOFA API client
│   │   ├── cve_client.py          # NVD CVE enrichment
│   │   ├── credential_manager.py  # Rotating API credentials
│   │   ├── proxy_manager.py       # Proxy pool management
│   │   └── ml_predictor.py        # ML risk prediction model
│   └── utils/
│       └── risk_scoring.py        # Risk scoring algorithm
├── cyberexposure.db               # SQLite database (auto-created)
├── .env                           # API keys (not committed)
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
```

### .env αρχείο
```env
# OSINT API Keys (primary)
SHODAN_API_KEY=your_shodan_key
ZOOMEYE_API_KEY=your_zoomeye_key
FOFA_EMAIL=your_fofa_email
FOFA_API_KEY=your_fofa_key
GROQ_API_KEY=your_groq_key

# Optional: Additional keys for rotation
SHODAN_API_KEY_2=second_shodan_key
GROQ_API_KEY_2=second_groq_key

# Optional: Proxy pool
PROXY_1=http://user:pass@host:port
PROXY_2=socks5://user:pass@host:port
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
| `GET` | `/vulnerabilities/` | Όλες οι ευπάθειες με CVE data |
| `POST` | `/vulnerabilities/ingest` | Εισαγωγή & εμπλουτισμός ευπαθειών |

### ML Predictions
| Method | Endpoint | Περιγραφή |
|--------|----------|-----------|
| `GET` | `/ml/predict` | ML predictions για όλα τα assets |
| `GET` | `/ml/predict/{id}` | ML prediction για συγκεκριμένο asset |

### System
| Method | Endpoint | Περιγραφή |
|--------|----------|-----------|
| `GET` | `/credentials/stats` | Στατιστικά API keys |
| `GET` | `/proxy/stats` | Στατιστικά proxy pool |

---

## 🧠 LLM Agent

Ο LLM Agent χρησιμοποιεί το **LLaMA-3.3-70b** μέσω Groq API για να μετατρέπει φυσική γλώσσα σε OSINT queries:

**Παράδειγμα:**
```
Input:  "εκτεθειμένοι Redis servers στην Ελλάδα"

Output:
  Shodan:  "redis port:6379 country:GR"
  ZoomEye: "app:redis port:6379 country:GR"
  FOFA:    "app="Redis" && port="6379" && country="GR""
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

## 🤖 ML Predictor

Το ML μοντέλο χρησιμοποιεί **Random Forest Classifier** για να προβλέπει:
- **Predicted Risk Level** (low/medium/high/critical)
- **Compromise Probability** (0-100%)
- **Model Confidence** (0-100%)
- **Risk Distribution** ανά επίπεδο

**Features που χρησιμοποιεί:**
- Port risk score
- Service risk score
- Is default port
- Is database service
- Is remote access service
- Is unencrypted

**Παράδειγμα:**
```json
{
  "predicted_risk": "critical",
  "compromise_probability": 59.4,
  "confidence": 99.0,
  "probabilities": {
    "low": 0.0,
    "medium": 1.0,
    "high": 0.0,
    "critical": 99.0
  }
}
```

---

## 🔑 Credential Manager

Διαχειρίζεται πολλαπλά API keys ανά υπηρεσία με:
- **Round-robin rotation**
- **Αυτόματο blacklisting** rate-limited keys
- **Auto-reset** όταν όλα τα keys είναι blacklisted

```
GET /credentials/stats
→ {"shodan": {"total": 2, "blacklisted": 0, "available": 2}, ...}
```

---

## 🌐 Proxy Manager

Διαχειρίζεται proxy pool με:
- **Τυχαία rotation** proxies
- **Αυτόματο blacklisting** αποτυχημένων proxies
- **Fallback** σε direct connection αν δεν υπάρχουν proxies

---

## 🔍 CVE Enrichment

Αυτόματος εμπλουτισμός ευπαθειών με δεδομένα από το **NIST NVD**:
- CVE ID (π.χ. CVE-2018-0181)
- CVSS Score
- Περιγραφή
- Severity level

---

## 🖥️ Frontend

Το dashboard (NEX Security Platform) βρίσκεται στο:
👉 https://github.com/ManosBiliouris/nex-dashboard-hub

**Χαρακτηριστικά Dashboard:**
- Real-time security stats
- Asset discovery & management
- Vulnerability tracking με CVEs
- Scan history
- ML Risk Prediction visualization
- Settings & API key management

---

## 👨‍💻 Ανάπτυξη

**Manos Biliouris**
Πτυχιακή Εργασία — Τμήμα Πληροφορικής
2025-2026

---

## 📄 Άδεια

MIT License
