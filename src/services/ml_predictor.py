import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import json
import os

class MLPredictor:
    """
    ML model που προβλέπει την πιθανότητα compromise ενός asset
    βάσει χαρακτηριστικών όπως port, service, risk_score.
    """

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        self._train_with_synthetic_data()

    def _train_with_synthetic_data(self):
        """
        Εκπαιδεύει το μοντέλο με συνθετικά δεδομένα βασισμένα
        σε γνωστά patterns κυβερνοεπιθέσεων.
        """

        # Features: [port_risk, service_risk, is_default_port, is_db, is_remote_access, is_unencrypted]
        # Label: 0=low_risk, 1=medium_risk, 2=high_risk, 3=critical_risk

        training_data = [
            # [port_risk, service_risk, is_default_port, is_db, is_remote, is_unencrypted] -> label
            # Critical cases
            [95, 95, 1, 0, 0, 1, 3],  # Redis unauthenticated
            [95, 90, 1, 1, 0, 1, 3],  # MongoDB exposed
            [95, 90, 1, 0, 0, 1, 3],  # Elasticsearch exposed
            [90, 90, 1, 0, 1, 1, 3],  # RDP exposed
            [95, 95, 1, 0, 0, 1, 3],  # Telnet
            [85, 85, 1, 0, 1, 1, 3],  # VNC exposed
            [85, 85, 1, 1, 0, 1, 3],  # SMB exposed
            # High risk
            [80, 80, 1, 1, 0, 1, 2],  # MySQL exposed
            [80, 75, 1, 1, 0, 1, 2],  # PostgreSQL exposed
            [80, 80, 1, 1, 0, 1, 2],  # MSSQL exposed
            [70, 70, 1, 0, 0, 1, 2],  # FTP exposed
            [40, 35, 1, 0, 1, 1, 2],  # SSH on default port
            # Medium risk
            [30, 20, 1, 0, 0, 1, 1],  # HTTP
            [15, 35, 0, 0, 0, 0, 1],  # Apache Tomcat
            [20, 20, 0, 0, 0, 1, 1],  # HTTP Alt
            [40, 15, 0, 0, 1, 1, 1],  # SSH non-default
            # Low risk
            [10, 10, 1, 0, 0, 0, 0],  # HTTPS
            [5,  10, 1, 0, 0, 0, 0],  # HTTPS default
            [15, 20, 0, 0, 0, 0, 0],  # HTTP Alt encrypted
            [10, 10, 0, 0, 0, 0, 0],  # HTTPS non-default
        ]

        X = np.array([row[:6] for row in training_data])
        y = np.array([row[6] for row in training_data])

        self.model.fit(X, y)
        self.is_trained = True
        print("[MLPredictor] Model trained successfully")

    def _extract_features(self, asset: dict) -> np.ndarray:
        """
        Εξάγει features από ένα asset για πρόβλεψη.
        """
        port = asset.get("port") or 0
        service = (asset.get("service") or "").lower()
        risk_score = asset.get("risk_score") or 0

        # Port risk (0-100)
        port_risk_map = {
            21: 70, 22: 40, 23: 95, 25: 40, 80: 20, 443: 10,
            445: 85, 1433: 80, 1521: 80, 3306: 80, 3389: 90,
            5432: 80, 5900: 85, 6379: 95, 8080: 30, 9200: 95, 27017: 95
        }
        port_risk = port_risk_map.get(port, 15)

        # Service risk (0-100)
        service_risk_map = {
            "telnet": 95, "ftp": 70, "rdp": 90, "remote desktop protocol": 90,
            "vnc": 85, "redis": 95, "mongodb": 90, "elasticsearch": 90,
            "mysql": 75, "postgresql": 75, "mssql": 80, "smb": 85,
            "http": 20, "https": 10, "ssh": 35, "apache httpd": 20,
        }
        service_risk = 15
        for key, val in service_risk_map.items():
            if key in service:
                service_risk = val
                break

        # Binary features
        default_ports = {80, 443, 22, 21, 23, 25, 3306, 5432, 3389, 6379, 27017, 9200}
        db_services = {"mysql", "postgresql", "mongodb", "mssql", "oracle", "redis", "elasticsearch"}
        remote_services = {"rdp", "vnc", "ssh", "telnet", "remote desktop"}
        unencrypted = port not in {443, 8443, 22}

        is_default_port = 1 if port in default_ports else 0
        is_db = 1 if any(db in service for db in db_services) else 0
        is_remote = 1 if any(r in service for r in remote_services) else 0
        is_unencrypted = 1 if unencrypted else 0

        return np.array([[port_risk, service_risk, is_default_port, is_db, is_remote, is_unencrypted]])

    def predict(self, asset: dict) -> dict:
        """
        Προβλέπει το risk level και την πιθανότητα compromise.
        """
        if not self.is_trained:
            return {"error": "Model not trained"}

        features = self._extract_features(asset)
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]

        risk_labels = ["low", "medium", "high", "critical"]
        risk_label = risk_labels[prediction]

        # Compromise probability = weighted sum of high+critical probabilities
        compromise_prob = round(
            (probabilities[2] * 0.4 + probabilities[3] * 0.6) * 100, 1
        )

        return {
            "predicted_risk": risk_label,
            "compromise_probability": compromise_prob,
            "confidence": round(float(max(probabilities)) * 100, 1),
            "probabilities": {
                "low": round(float(probabilities[0]) * 100, 1),
                "medium": round(float(probabilities[1]) * 100, 1),
                "high": round(float(probabilities[2]) * 100, 1),
                "critical": round(float(probabilities[3]) * 100, 1),
            }
        }

    def predict_batch(self, assets: list) -> list:
        """
        Προβλέπει για πολλά assets ταυτόχρονα.
        """
        return [
            {**asset, "ml_prediction": self.predict(asset)}
            for asset in assets
        ]

# Singleton
ml_predictor = MLPredictor()