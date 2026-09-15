import re
import time

class BharatAIShield:
    def __init__(self):
        # Suspicious keywords mapping to threat weights
        self.malicious_keywords = {
            r"\b(rm|del|erase)\b": 45,  # Destructive
            r"\b(nmap|hydra|ping|scan|ncat|nc)\b": 35,  # Reconnaissance / Attack tools
            r"\b(sudo|su|chmod|chown|runas)\b": 40,  # Privilege escalation
            r"\b(wget|curl|ftp|scp)\b": 30,  # Data transfer
            r"\b(cat|type)\b\s+.*(passwd|shadow|credentials|secret|flag|key)": 80,  # Sensitive data exfiltration
            r"\b(drop|delete|insert|select)\b.*(from|table|users)": 50,  # Database exploits (SQLi)
            r"(\.\./|\.\.\\)": 60,  # Path traversal attempts
            r"(\bscript\b|<\s*script|javascript:)": 50,  # XSS attempts
            r"\b(exploit|payload|inject|brute|flood)\b": 55,  # Threat testing terms
        }
        
    def calculate_semantic_score(self, command):
        """Analyzes command syntax using pre-defined threat signatures."""
        if not command:
            return 0, []
        
        score = 0
        matched_indicators = []
        lower_command = command.lower().strip()
        
        for pattern, weight in self.malicious_keywords.items():
            if re.search(pattern, lower_command):
                score += weight
                matched_indicators.append(f"Threat signature matched: '{pattern}' (+{weight}%)")
                
        # Cap semantic score at 95%
        return min(score, 95), matched_indicators

    def evaluate_behavior(self, command, cmd_history, request_times, file_mod_count=0):
        """
        Evaluates current behavior:
        - Command semantic analysis
        - Command frequency analysis (detecting rapid automated attacks / DDoS)
        - File modification rate (detecting mass modification / ransomware)
        """
        now = time.time()
        anomaly_score = 0
        reasons = []
        classification = "Benign"
        
        # 1. Semantic Check
        semantic_score, semantic_reasons = self.calculate_semantic_score(command)
        anomaly_score += semantic_score
        reasons.extend(semantic_reasons)
        
        # 2. Timing/Frequency Check (DDoS or Script Bruteforce)
        # Calculate commands executed in the last 5 seconds
        recent_requests = [t for t in request_times if now - t <= 5.0]
        req_count = len(recent_requests)
        
        if req_count >= 5:
            flood_weight = min((req_count - 4) * 20, 80)
            anomaly_score += flood_weight
            reasons.append(f"High-frequency request flood detected: {req_count} requests in 5s (+{flood_weight}%)")
            
        # 3. File Modification Rate Check (Ransomware)
        if file_mod_count >= 3:
            ransomware_weight = min(file_mod_count * 25, 90)
            anomaly_score += ransomware_weight
            reasons.append(f"Rapid mass file modifications detected: {file_mod_count} files/sec (+{ransomware_weight}%)")
            
        # Bound score between 0 and 100
        anomaly_score = min(max(anomaly_score, 0), 100)
        
        # Classify threat
        if anomaly_score >= 85:
            if file_mod_count >= 3:
                classification = "Malicious (Ransomware Execution)"
            elif req_count >= 5:
                classification = "Malicious (DDoS Attempt)"
            else:
                classification = "Malicious (Intrusion Exploit)"
        elif anomaly_score >= 50:
            classification = "Suspicious (Heuristic Alert)"
        else:
            classification = "Benign"
            
        quarantine = (anomaly_score >= 85)
        
        return {
            "anomaly_score": round(anomaly_score, 1),
            "reasons": reasons,
            "classification": classification,
            "quarantine": quarantine
        }
