import time
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from ai_shield import BharatAIShield

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Initialize AI Shield
ai_engine = BharatAIShield()

# Simulated system state
state = {
    "quarantine_mode": False,
    "quarantine_until": 0.0,
    "request_times": [],
    "recent_command_history": [],
    "banned_ips": set(),
    "file_mod_count": 0,
    "last_file_mod_reset": time.time(),
    "cpu_load": 12,
    "ram_load": 34,
    "logs": [
        {"timestamp": time.strftime("%H:%M:%S"), "source": "KERNEL", "message": "BharatOS-Shield Kernel loaded successfully.", "type": "info"},
        {"timestamp": time.strftime("%H:%M:%S"), "source": "AI-SHIELD", "message": "Bharat AI-Shield Anomaly Engine initialized. Zero-Trust mode active.", "type": "success"}
    ],
    "vault": {
        "credentials.txt": "root:admin_sovereign_key_india_2026",
        "national_defense_outline.txt": "CONFIDENTIAL: Sovereign airspace monitoring parameters v4.2. Active defense channels enabled.",
        "rupay_routing.conf": "RuPay payment gateway settlement endpoint: https://in.rupay.gateway.internal:9081",
        "cert_in_feed.txt": "ADVISORY: Zero-day alert for Apache Struts. Indian servers advised to apply patches immediately."
    }
}

# Keep a backup of the vault files for self-healing demonstrations
VAULT_BACKUP = dict(state["vault"])

def add_log(source, message, log_type="info"):
    timestamp = time.strftime("%H:%M:%S")
    state["logs"].insert(0, {
        "timestamp": timestamp,
        "source": source,
        "message": message,
        "type": log_type
    })

@app.route('/')
def index():
    return render_template('desktop.html')

@app.route('/api/system_status', methods=['GET'])
def get_system_status():
    now = time.time()
    
    # Check if quarantine has expired
    if state["quarantine_mode"] and now > state["quarantine_until"]:
        state["quarantine_mode"] = False
        add_log("KERNEL", "Security lockdown lifted. Host state restored to normal.", "success")
        
    # Simulate CPU/RAM fluctuation
    import random
    if state["quarantine_mode"]:
        # High CPU load during quarantine/threat handling
        state["cpu_load"] = random.randint(85, 98)
        state["ram_load"] = random.randint(70, 78)
    else:
        state["cpu_load"] = random.randint(10, 22)
        state["ram_load"] = random.randint(30, 36)

    # Dynamic status
    recent_reqs = [t for t in state["request_times"] if now - t <= 5.0]
    eval_res = ai_engine.evaluate_behavior(
        command="", 
        cmd_history=state["recent_command_history"], 
        request_times=state["request_times"],
        file_mod_count=state["file_mod_count"]
    )
    
    return jsonify({
        "quarantine_mode": state["quarantine_mode"],
        "quarantine_time_left": max(0, int(state["quarantine_until"] - now)),
        "cpu_load": state["cpu_load"],
        "ram_load": state["ram_load"],
        "logs": state["logs"][:25],  # Return recent 25 logs
        "threat_index": eval_res["anomaly_score"],
        "threat_classification": eval_res["classification"],
        "file_count": len(state["vault"]),
        "vault_files": list(state["vault"].keys()),
        "banned_ips": list(state["banned_ips"])
    })

@app.route('/api/terminal', methods=['POST'])
def handle_terminal():
    now = time.time()
    client_ip = request.remote_addr or "127.0.0.1"
    
    # Check quarantine
    if state["quarantine_mode"] and now < state["quarantine_until"]:
        time_left = int(state["quarantine_until"] - now)
        return jsonify({
            "output": f"SYSTEM QUARANTINE: Terminal access disabled by AI-Shield. Try again in {time_left} seconds.",
            "status": "error",
            "eval": {"anomaly_score": 100, "classification": "Malicious (Quarantined)", "reasons": ["System is locked under quarantine."]}
        })
        
    # Check if client IP is banned
    if client_ip in state["banned_ips"]:
        return jsonify({
            "output": f"ACCESS DENIED: IP address '{client_ip}' is blacklisted by Sentinel-Shield Firewall.",
            "status": "error",
            "eval": {"anomaly_score": 100, "classification": "Banned IP", "reasons": ["Host IP blacklisted."]}
        })

    data = request.json or {}
    cmd = data.get("command", "").strip()
    
    if not cmd:
        return jsonify({"output": ""})

    # Track requests for DDoS timing check
    state["request_times"].append(now)
    state["recent_command_history"].append(cmd)
    # Keep request list trim
    state["request_times"] = [t for t in state["request_times"] if now - t <= 10.0]
    
    # Reset file modifications every 5 seconds
    if now - state["last_file_mod_reset"] > 5.0:
        state["file_mod_count"] = 0
        state["last_file_mod_reset"] = now

    # Evaluate action through local AI Anomaly Engine
    eval_res = ai_engine.evaluate_behavior(
        command=cmd,
        cmd_history=state["recent_command_history"],
        request_times=state["request_times"],
        file_mod_count=state["file_mod_count"]
    )

    # Process AI outcome
    if eval_res["quarantine"]:
        state["quarantine_mode"] = True
        state["quarantine_until"] = now + 20.0  # 20 seconds lock
        state["banned_ips"].add(client_ip)
        add_log("AI-SHIELD", f"HIGH THREAT INTRUSION DETECTED: {eval_res['classification']}.", "danger")
        add_log("AI-SHIELD", f"Initiated lockdown. Quarantine duration: 20 seconds. Banned host IP: {client_ip}", "danger")
        for reason in eval_res["reasons"]:
            add_log("AI-SHIELD", f"Rule fired: {reason}", "warning")
            
        return jsonify({
            "output": f"\n[!!!] EMERGENCY SECURITY SHUTDOWN INITIATED [!!!]\n"
                      f"Threat Detected: {eval_res['classification']}\n"
                      f"Reason: {eval_res['reasons'][0] if eval_res['reasons'] else 'Suspicious behavior pattern.'}\n"
                      f"Your IP ({client_ip}) has been blocked.\n"
                      f"Terminal connection terminated.",
            "status": "quarantine",
            "eval": eval_res
        })
        
    if eval_res["anomaly_score"] >= 50:
        add_log("AI-SHIELD", f"Suspicious activity warning: {cmd} (Score: {eval_res['anomaly_score']}%)", "warning")

    # Command Execution logic
    args = cmd.split()
    base_cmd = args[0].lower()
    output = ""
    
    try:
        if base_cmd == "help":
            output = ("Available BharatOS sovereign commands:\n"
                      "  help              - Display this helper catalog\n"
                      "  sysinfo           - Display sovereign OS specification and branding\n"
                      "  files             - List documents stored in the secure vault\n"
                      "  cat <filename>    - View the decrypted content of a vault document\n"
                      "  encrypt <file>    - Encrypt a document with sovereign multi-layer cipher\n"
                      "  decrypt <file>    - Decrypt a previously cipher-locked document\n"
                      "  trace             - Trace local secure communication nodes\n"
                      "  clear             - Clear terminal outputs")
                      
        elif base_cmd == "sysinfo":
            output = ("==============================================\n"
                      "          BHARATOS-SHIELD (Sovereign OS)      \n"
                      "          Sovereign Security Shield Prototype \n"
                      "==============================================\n"
                      "Kernel Architecture : IndOS x86_64 SafeKernel\n"
                      "Sovereign Cryptology: Bharat-Shield AES-256 Engine\n"
                      "Local AI Module     : Real-time Behavior Anomaly 1.0\n"
                      "Host Status         : Safe (Zero-Trust Active)\n"
                      "System Language     : Hindi / English (Multi-localized)\n"
                      "Development Agency  : Sovereign Defense Lab (B.Tech Project)\n"
                      "==============================================")
                      
        elif base_cmd == "files":
            output = "Secure Sovereign Vault Directory:\n"
            for filename, content in state["vault"].items():
                size = len(content)
                output += f"  -rw-r--r--   {size} Bytes   {filename}\n"
                
        elif base_cmd == "cat":
            if len(args) < 2:
                output = "Error: Please specify the filename to read. e.g. cat credentials.txt"
            else:
                filename = args[1]
                if filename in state["vault"]:
                    val = state["vault"][filename]
                    if val.startswith("[CIPHER-LOCKED]"):
                        output = f"ERROR: File '{filename}' is locked with Bharat-Cipher. Decrypt it to view contents."
                    else:
                        output = f"Reading file: {filename}\n-----------------------------------\n{val}"
                else:
                    output = f"Error: File '{filename}' not found in vault."
                    
        elif base_cmd == "encrypt":
            if len(args) < 2:
                output = "Error: Specify file to encrypt. e.g. encrypt credentials.txt"
            else:
                filename = args[1]
                if filename in state["vault"]:
                    content = state["vault"][filename]
                    if content.startswith("[CIPHER-LOCKED]"):
                        output = f"File '{filename}' is already encrypted."
                    else:
                        # Simple mock Vigenere cipher representation
                        state["vault"][filename] = f"[CIPHER-LOCKED] {content[::-1]}"
                        add_log("SECURE-VAULT", f"Encrypted file '{filename}' using Bharat-Shield Cipher.", "success")
                        output = f"Success: File '{filename}' ciphered. Contents secured under localized encryption."
                else:
                    output = f"Error: File '{filename}' not found."
                    
        elif base_cmd == "decrypt":
            if len(args) < 2:
                output = "Error: Specify file to decrypt. e.g. decrypt credentials.txt"
            else:
                filename = args[1]
                if filename in state["vault"]:
                    content = state["vault"][filename]
                    if not content.startswith("[CIPHER-LOCKED]"):
                        output = f"File '{filename}' is already in plaintext."
                    else:
                        cipher_data = content.replace("[CIPHER-LOCKED] ", "")
                        state["vault"][filename] = cipher_data[::-1]  # Reverse back
                        add_log("SECURE-VAULT", f"Decrypted file '{filename}' successfully.", "success")
                        output = f"Success: Decrypted file '{filename}'. Contents restored to plain text."
                else:
                    output = f"Error: File '{filename}' not found."
                    
        elif base_cmd == "trace":
            output = ("Tracing sovereign secure nodes...\n"
                      " [1] ind-gw.delhi.nic.in (10.0.1.1)    - RTT: 1.4ms (SECURED)\n"
                      " [2] sovereign-core.hub.gov.in (10.2.1.25) - RTT: 2.1ms (SECURED)\n"
                      " [3] bharatos-vault.local (192.168.99.5) - RTT: 0.2ms (ENCRYPTED)\n"
                      "Trace successfully verified. No MITM (Man-in-the-Middle) threats detected.")
        else:
            output = f"Error: Command '{base_cmd}' not recognized as a sovereign system call. Type 'help' for options."
            
    except Exception as e:
        output = f"Execution Error: {str(e)}"
        
    return jsonify({
        "output": output,
        "status": "success",
        "eval": eval_res
    })

@app.route('/api/simulate', methods=['POST'])
def simulate_exploit():
    now = time.time()
    data = request.json or {}
    sim_type = data.get("type", "")
    
    if sim_type == "ddos":
        # Simulate rapid requests
        add_log("SIMULATOR", "Simulating external DDoS request flood attack...", "warning")
        
        # Populate mock requests in a split second
        for i in range(7):
            state["request_times"].append(now)
            
        # Re-evaluate
        eval_res = ai_engine.evaluate_behavior(
            command="PING FLOOD",
            cmd_history=state["recent_command_history"],
            request_times=state["request_times"],
            file_mod_count=state["file_mod_count"]
        )
        
        if eval_res["quarantine"]:
            state["quarantine_mode"] = True
            state["quarantine_until"] = now + 20.0
            client_ip = request.remote_addr or "127.0.0.1"
            state["banned_ips"].add(client_ip)
            add_log("AI-SHIELD", "DDoS Flood detected by timing analysis. System lockdown initiated!", "danger")
            add_log("KERNEL", f"Blacklisted attacking node IP: {client_ip}", "danger")
            
        return jsonify({"status": "triggered", "message": "DDoS simulation active."})
        
    elif sim_type == "ransomware":
        add_log("SIMULATOR", "Simulating malicious local ransomware execution...", "warning")
        
        # Ransomware attempts to write to all files instantly
        state["file_mod_count"] = 4
        for filename in list(state["vault"].keys()):
            state["vault"][filename] = "[ENCRYPTED_BY_FOREIGN_MALWARE_SHADOW_LOCK]"
            
        # Evaluate ransomware pattern
        eval_res = ai_engine.evaluate_behavior(
            command="EXFILTRATE_AND_ENCRYPT",
            cmd_history=state["recent_command_history"],
            request_times=state["request_times"],
            file_mod_count=state["file_mod_count"]
        )
        
        if eval_res["quarantine"]:
            add_log("AI-SHIELD", "RANSOMWARE SIGNATURE DETECTED: Bulk file encryption attempt.", "danger")
            add_log("AI-SHIELD", "Killing malicious thread processes (PID 4410, 4412)...", "danger")
            
            # Simulate Self-Healing Restoration
            add_log("KERNEL", "Initiating Secure Vault Self-Healing protocol...", "success")
            time.sleep(1.0)  # Short delay for effect
            state["vault"] = dict(VAULT_BACKUP)
            add_log("KERNEL", "Self-Healing success. Integrity verified. Vault files restored from backup.", "success")
            state["file_mod_count"] = 0
            
        return jsonify({"status": "triggered", "message": "Ransomware simulation neutralized by Self-Healing."})
        
    elif sim_type == "reset":
        state["quarantine_mode"] = False
        state["quarantine_until"] = 0.0
        state["request_times"] = []
        state["recent_command_history"] = []
        state["banned_ips"].clear()
        state["file_mod_count"] = 0
        state["vault"] = dict(VAULT_BACKUP)
        state["logs"] = [
            {"timestamp": time.strftime("%H:%M:%S"), "source": "KERNEL", "message": "System status soft reset completed.", "type": "success"},
            {"timestamp": time.strftime("%H:%M:%S"), "source": "AI-SHIELD", "message": "Threat tables flushed. Normal operations active.", "type": "info"}
        ]
        return jsonify({"status": "reset", "message": "System reset completed."})
        
    return jsonify({"status": "error", "message": "Invalid simulation type."})

if __name__ == '__main__':
    # Running on port 5001 to avoid conflicts with Jarvis 2.0 (which runs on 5000)
    app.run(host='0.0.0.0', port=5001, debug=True)
