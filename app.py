import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import system_tools

# Initialize Flask App
app = Flask(__name__, template_folder='templates')
CORS(app, origins=["http://127.0.0.1:5000", "http://localhost:5000"])

# Load environment variables for configuration
load_dotenv()

def get_api_key():
    return os.getenv("GEMINI_API_KEY")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    api_key = get_api_key()
    return jsonify({
        "status": "healthy",
        "has_api_key": bool(api_key)
    })

@app.route('/api/save_key', methods=['POST'])
def save_key():
    try:
        data = request.json or {}
        api_key = data.get('api_key', '').strip()
        if not api_key:
            return jsonify({"status": "error", "message": "API key cannot be empty."}), 400
        
        # Write to .env file
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        
        # Reload environment
        load_dotenv(override=True)
        return jsonify({"status": "success", "message": "API Key saved successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to save key: {str(e)}"}), 500


@app.route('/api/settings/autostart', methods=['GET'])
def get_autostart():
    try:
        import os
        startup_dir = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
        shortcut_path = os.path.join(startup_dir, "Jarvis2.lnk")
        return jsonify({"status": "success", "enabled": os.path.exists(shortcut_path)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/settings/autostart', methods=['POST'])
def set_autostart():
    try:
        data = request.json or {}
        enabled = bool(data.get("enabled", False))
        
        import os
        import subprocess
        
        startup_dir = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
        shortcut_path = os.path.join(startup_dir, "Jarvis2.lnk")
        
        if enabled:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            target_path = os.path.join(current_dir, "start_jarvis.bat")
            
            ps_cmd = (
                f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{shortcut_path}'); "
                f"$s.TargetPath = '{target_path}'; "
                f"$s.WorkingDirectory = '{current_dir}'; "
                f"$s.Save()"
            )
            subprocess.run(["powershell", "-Command", ps_cmd], shell=True, capture_output=True)
            return jsonify({"status": "success", "message": "Startup shortcut enabled."})
        else:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            return jsonify({"status": "success", "message": "Startup shortcut disabled."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/clipboard/poll', methods=['GET'])
def poll_clipboard():
    text = system_tools.get_clipboard_text()
    return jsonify({"status": "success", "text": text})


@app.route('/api/type_text', methods=['POST'])
def api_type_text():
    try:
        data = request.json or {}
        text = data.get("text", "")
        if not text:
            return jsonify({"status": "error", "message": "Text is required."}), 400
        res = system_tools.type_text(text)
        return jsonify({"status": "success", "result": res})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/emails/drafts', methods=['GET'])
def get_email_drafts():
    try:
        emails = get_emails_list()
        if not emails:
            return jsonify({"status": "success", "drafts": []})
            
        api_key = get_api_key()
        if not api_key:
            drafts = []
            for em in emails[:3]:
                drafts.append({
                    "id": em["id"],
                    "from": em["from"],
                    "subject": em["subject"],
                    "summary": f"Unread email from {em['from']}.",
                    "draft": f"Dear sender, thank you for your email regarding '{em['subject']}'. I will get back to you shortly. Best, Tony."
                })
            return jsonify({"status": "success", "drafts": drafts})
            
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        drafts = []
        for em in emails[:3]:
            prompt = (
                f"Generate a brief summary (under 15 words) and a professional email reply draft for this email:\n"
                f"From: {em['from']}\n"
                f"Subject: {em['subject']}\n\n"
                f"Reply as Tony Stark (refer to yourself as JARVIS's pilot or Tony Stark). Keep the reply extremely professional, friendly, and concise (under 40 words).\n"
                f"Output format MUST be JSON with fields: 'summary' and 'draft'."
            )
            try:
                response = model.generate_content(
                    prompt, 
                    generation_config={"response_mime_type": "application/json"}
                )
                import json
                res_json = json.loads(response.text.strip())
                summary = res_json.get("summary", "Brief update request.")
                draft = res_json.get("draft", "I will look into it, Sir.")
            except Exception:
                summary = f"Discussion about {em['subject']}"
                draft = f"Hi, I received your message regarding '{em['subject']}' and will review it soon. Regards, Tony."
                
            drafts.append({
                "id": em["id"],
                "from": em["from"],
                "subject": em["subject"],
                "summary": summary,
                "draft": draft
            })
            
        return jsonify({"status": "success", "drafts": drafts})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/system_stats', methods=['GET'])
def get_system_stats():
    stats = system_tools.get_system_stats()
    return jsonify(stats)

@app.route('/api/weather', methods=['GET'])
def get_weather():
    try:
        city = request.args.get("city", "").strip()
        data = system_tools.get_weather_data(city if city else None)
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/iot', methods=['GET'])
def get_iot_status():
    try:
        devices = system_tools.get_iot_devices()
        return jsonify(devices)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/iot/control', methods=['POST'])
def control_iot():
    try:
        data = request.json or {}
        device_id = data.get("device_id")
        action = data.get("action")
        value = data.get("value")
        
        if not device_id or not action:
            return jsonify({"status": "error", "message": "device_id and action are required."}), 400
            
        devices = system_tools.control_iot_device(device_id, action, value)
        return jsonify({"status": "success", "devices": devices})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Define schemas for Gemini API tool declaration (mock functions for schema generation)
def control_iot_device(device_id: str, action: str, value: str = None):
    """
    Control smart home IoT devices. device_id can be 'bedroom_light', 'study_lamp', 'living_ac', or 'smart_plug'. action can be 'ON' or 'OFF'. value is optional to specify dim/brightness level (e.g. '70%') or thermostat temperature (e.g. '22°C').
    """
    pass

def set_wifi_state(state: str):
    """
    Toggle the system Wi-Fi adapter ON or OFF. state must be 'ON' or 'OFF'.
    """
    pass

def set_bluetooth_state(state: str):
    """
    Toggle the system Bluetooth radio ON or OFF. state must be 'ON' or 'OFF'.
    """
    pass

def set_airplane_mode_state(state: str):
    """
    Toggle the system Airplane Mode state. state must be 'ON' or 'OFF'. Toggling Airplane Mode on turns off all wireless communications.
    """
    pass

def set_energy_saver_state(state: str):
    """
    Toggle the system Energy Saver (Battery Saver) mode. state must be 'ON' or 'OFF'.
    """
    pass

def set_nightlight_state(state: str):
    """
    Toggle the system Night Light (Blue Light Reduction) settings. state must be 'ON' or 'OFF'.
    """
    pass

def set_active_window_state(action: str):
    """
    Minimize or maximize the currently active window. action must be 'minimize' or 'maximize'.
    """
    pass

def set_screen_brightness(level: int):
    """
    Set the screen brightness level. level must be an integer between 0 and 100.
    """
    pass

def set_keyboard_backlight(state: str):
    """
    Toggle the laptop keyboard backlight ON or OFF. state must be 'ON' or 'OFF'.
    """
    pass

def switch_window_tab(target: str):
    """
    Switch active window (Alt+Tab) or switch active browser tab (Ctrl+Tab). target must be 'window' or 'tab'.
    """
    pass

def type_text(text: str):
    """
    Type text Unicode character-by-character into the active foreground application window.
    """
    pass

def control_media(action: str):
    """
    Control system media keys. action can be 'play', 'pause', 'next', 'prev', 'stop', 'mute', 'volume_up', or 'volume_down'.
    """
    pass

def research_topic(query: str):
    """
    Perform web search (using DuckDuckGo) and return a summarized verbal report on the query.
    """
    pass

def plan_my_day():
    """
    Generate an organized daily task timeline and schedule based on calendar events.
    """
    pass

def open_app(app_name: str):
    """
    Launch any local application installed on the computer. app_name can be any application name (e.g., chrome, notepad, word, excel, powerpoint, whatsapp, spotify, discord, vlc, vs code, steam, etc.).
    """
    pass

def close_app(app_name: str):
    """
    Close or terminate any local application running on the computer. app_name can be any application name (e.g., chrome, notepad, word, excel, powerpoint, whatsapp, spotify, discord, vlc, vs code, steam, etc.).
    """
    pass

def send_message_to_app(app_name: str, message: str, contact: str = ""):
    """
    Send a message, type text, or run a command in a given application. app_name is the application name (e.g. whatsapp, notepad, discord, word, cmd, powershell, etc.). message is the text content to send or type. contact is the contact name or phone number to send the message to (e.g. 'John' or '+919876543210', only supported for whatsapp currently).
    """
    pass

def open_website(site_name: str, search_query: str = ""):
    """
    Open a website in the default browser. site_name can be google, youtube, github, stackoverflow, wikipedia, gmail, etc. search_query is optional to search within that website.
    """
    pass

def volume_control(action: str, value: int = None):
    """
    Control system volume. action can be 'set' (with value 0-100), 'mute', 'unmute', 'up', 'down'.
    """
    pass

def take_screenshot():
    """
    Take a screenshot of the user's screen.
    """
    pass

def write_note(content: str):
    """
    Save a quick text note or reminder for the user.
    """
    pass

def execute_shell_command(command: str):
    """
    Execute a PowerShell command on the system. Use this only when the user explicitly asks to run a command or terminal task.
    """
    pass

def go_offline():
    """
    Shut down the Jarvis assistant and turn off the server (go offline). Use this when the user says 'go offline', 'exit', 'shutdown', or 'bye'.
    """
    pass

def close_browser_tab(browser_name: str = ""):
    """
    Close the active tab in any web browser (e.g. chrome, edge, firefox, or general browser). browser_name is optional to specify which browser to close the tab of.
    """
    pass

def system_power_control(action: str):
    """
    Control system power. action can be 'shutdown', 'restart', 'sleep', or 'signout'.
    """
    pass

def get_active_window_context():
    """
    Get active application title and process name currently in focus on the computer. Useful to provide contextual assistance, suggestions, or keyboard shortcuts.
    """
    pass

def add_calendar_event(title: str, start_time: str, end_time: str = "", description: str = ""):
    """
    Add a new event or appointment to the calendar. start_time and end_time should be YYYY-MM-DD HH:MM. description is optional details.
    """
    pass

def list_calendar_events(query_date: str = ""):
    """
    List calendar events and appointments. query_date is optional YYYY-MM-DD to filter by date.
    """
    pass

def modify_calendar_event(event_id: str, action: str, new_value: str = ""):
    """
    Modify or delete an existing calendar event. event_id is the unique event ID or title. action can be 'delete', 'update_title', 'update_time', or 'update_desc'. new_value is the updated content.
    """
    pass

def check_emails():
    """
    Check for new unread emails in the user's inbox. Prioritizes them by urgency.
    """
    pass

def read_email_content(email_id: str):
    """
    Retrieve and read aloud the text content/body of a specific email by email_id.
    """
    pass

def send_email(to_email: str, subject: str, body: str):
    """
    Compose, draft, and send a new email reply or direct email.
    """
    pass

def organize_directory(directory_path: str):
    """
    Automatically group and organize files in a directory (e.g., downloads, documents, desktop, or any path) into folders by type (Documents, Images, Audio, Videos, Code, Archives).
    """
    pass

def search_files(search_query: str, root_path: str = ""):
    """
    Recursively search for files matching search_query inside a directory. root_path is optional (defaults to Documents).
    """
    pass

def manage_file_operation(action: str, source_path: str, target_path: str = ""):
    """
    Execute file operations on local storage. action can be 'create_folder', 'create_file', 'move', 'delete', or 'rename'. source_path is the file/folder path. target_path is the destination (only needed for move or rename).
    """
    pass

def run_disk_cleanup(clean_temp: bool = True, clean_cache: bool = True):
    """
    Execute system disk cleanup routine to free space by clearing temporary files and caches.
    """
    pass

def check_system_updates():
    """
    Scan the operating system and installed apps for outstanding software updates.
    """
    pass

def manage_workflow(action: str, name: str, steps: list = None):
    """
    Create, list, or delete custom multi-step task automation workflows. action can be 'create', 'delete', or 'list'. name is the workflow name. steps is a list of commands (e.g. ["open notepad", "volume set 40"]).
    """
    pass

def run_workflow(name: str):
    """
    Execute a saved custom workflow (macro) of multi-step commands sequentially.
    """
    pass


def has_internet():
    import socket
    try:
        socket.setdefaulttimeout(2.5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except socket.error:
        return False


def query_openrouter(api_key, prompt, history, system_stats):
    import json
    
    # Define tool calling schema for OpenRouter / OpenAI
    tools_schema = [
        {
            "type": "function",
            "function": {
                "name": "control_iot_device",
                "description": "Control smart home IoT devices like lights, lamps, thermostats, and plugs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The unique ID or name of the device (e.g., bedroom_light, study_lamp, living_ac, smart_plug)."
                        },
                        "action": {
                            "type": "string",
                            "enum": ["ON", "OFF"],
                            "description": "Action to perform: turn ON or OFF."
                        },
                        "value": {
                            "type": "string",
                            "description": "Optional value, like brightness level ('70%') or temperature ('22°C')."
                        }
                    },
                    "required": ["device_id", "action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "open_app",
                "description": "Launch any local application installed on the computer. app_name can be any application name, such as chrome, notepad, word, excel, powerpoint, whatsapp, spotify, discord, vlc, vscode, steam, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string"}
                    },
                    "required": ["app_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "open_website",
                "description": "Open a website in the default browser. site_name can be google, youtube, github, stackoverflow, wikipedia, gmail, etc. search_query is optional to search within that website.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "site_name": {"type": "string"},
                        "search_query": {"type": "string"}
                    },
                    "required": ["site_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "volume_control",
                "description": "Control system volume. action can be 'set' (with value 0-100), 'mute', 'unmute', 'up', 'down'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "value": {"type": "integer"}
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "take_screenshot",
                "description": "Take a screenshot of the user's screen.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_note",
                "description": "Save a quick text note or reminder for the user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"}
                    },
                    "required": ["content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "execute_shell_command",
                "description": "Execute a PowerShell command on the system. Use this only when the user explicitly asks to run a command or terminal task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"}
                    },
                    "required": ["command"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "go_offline",
                "description": "Shut down the Jarvis assistant and turn off the server (go offline). Use this when the user says 'go offline', 'exit', 'shutdown', or 'bye'.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "close_app",
                "description": "Close or terminate any local application running on the computer. app_name can be any application name, such as chrome, notepad, word, excel, powerpoint, whatsapp, spotify, discord, vlc, vscode, steam, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string"}
                    },
                    "required": ["app_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "send_message_to_app",
                "description": "Send a message, type text, or run a command in a given application. app_name is the application name (e.g. whatsapp, notepad, discord, word, cmd, powershell, etc.). message is the text content to send or type. contact is an optional contact name or phone number to send the message to (only supported for whatsapp currently).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string"},
                        "message": {"type": "string"},
                        "contact": {"type": "string"}
                    },
                    "required": ["app_name", "message"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "close_browser_tab",
                "description": "Close the active tab in any web browser (e.g. chrome, edge, firefox, or general browser). browser_name is optional to specify which browser to close the tab of.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "browser_name": {"type": "string"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "system_power_control",
                "description": "Control system power. action can be 'shutdown', 'restart', 'sleep', or 'signout'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"}
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_active_window_context",
                "description": "Get active application title and process name currently in focus on the computer. Useful to provide contextual assistance, suggestions, or keyboard shortcuts.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_calendar_event",
                "description": "Add a new event or appointment to the calendar. start_time and end_time should be YYYY-MM-DD HH:MM. description is optional details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "start_time": {"type": "string"},
                        "end_time": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["title", "start_time"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_calendar_events",
                "description": "List calendar events and appointments. query_date is optional YYYY-MM-DD to filter by date.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_date": {"type": "string"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "modify_calendar_event",
                "description": "Modify or delete an existing calendar event. event_id is the unique event ID or title. action can be 'delete', 'update_title', 'update_time', or 'update_desc'. new_value is the updated content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_id": {"type": "string"},
                        "action": {"type": "string"},
                        "new_value": {"type": "string"}
                    },
                    "required": ["event_id", "action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_emails",
                "description": "Check for new unread emails in the user's inbox. Prioritizes them by urgency.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_email_content",
                "description": "Retrieve and read aloud the text content/body of a specific email by email_id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_id": {"type": "string"}
                    },
                    "required": ["email_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "send_email",
                "description": "Compose, draft, and send a new email reply or direct email.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to_email": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"}
                    },
                    "required": ["to_email", "subject", "body"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "organize_directory",
                "description": "Automatically group and organize files in a directory (downloads, documents, desktop, or any path) into folders by type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory_path": {"type": "string"}
                    },
                    "required": ["directory_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_files",
                "description": "Recursively search for files matching search_query inside a directory. root_path is optional.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_query": {"type": "string"},
                        "root_path": {"type": "string"}
                    },
                    "required": ["search_query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_file_operation",
                "description": "Execute file operations on local storage. action can be 'create_folder', 'create_file', 'move', 'delete', or 'rename'. source_path is the file/folder path. target_path is the destination (only needed for move or rename).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "source_path": {"type": "string"},
                        "target_path": {"type": "string"}
                    },
                    "required": ["action", "source_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_disk_cleanup",
                "description": "Execute system disk cleanup routine to free space by clearing temporary files and caches.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "clean_temp": {"type": "boolean"},
                        "clean_cache": {"type": "boolean"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_system_updates",
                "description": "Scan the operating system and installed apps for outstanding software updates.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_workflow",
                "description": "Create, list, or delete custom multi-step task automation workflows. action can be 'create', 'delete', or 'list'. name is the workflow name. steps is a list of commands.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "name": {"type": "string"},
                        "steps": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["action", "name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_workflow",
                "description": "Execute a saved custom workflow (macro) of multi-step commands sequentially.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    },
                    "required": ["name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "set_wifi_state",
                "description": "Toggle the system Wi-Fi adapter ON or OFF.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "string",
                            "enum": ["ON", "OFF"],
                            "description": "The state to set the Wi-Fi adapter to."
                        }
                    },
                    "required": ["state"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "set_bluetooth_state",
                "description": "Toggle the system Bluetooth radio ON or OFF.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "string",
                            "enum": ["ON", "OFF"],
                            "description": "The state to set the Bluetooth radio to."
                        }
                    },
                    "required": ["state"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "set_airplane_mode_state",
                "description": "Toggle the system Airplane Mode state. state must be 'ON' or 'OFF'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "string",
                            "enum": ["ON", "OFF"],
                            "description": "The state to set Airplane Mode to."
                        }
                    },
                    "required": ["state"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "set_energy_saver_state",
                "description": "Toggle the system Energy Saver (Battery Saver) mode. state must be 'ON' or 'OFF'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "string",
                            "enum": ["ON", "OFF"],
                            "description": "The state to set Energy Saver to."
                        }
                    },
                    "required": ["state"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "set_nightlight_state",
                "description": "Toggle the system Night Light (Blue Light Reduction) settings. state must be 'ON' or 'OFF'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "string",
                            "enum": ["ON", "OFF"],
                            "description": "The state to set Night Light to."
                        }
                    },
                    "required": ["state"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "set_active_window_state",
                "description": "Minimize or maximize the currently active foreground window.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["minimize", "maximize"],
                            "description": "The window action: minimize or maximize."
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "set_screen_brightness",
                "description": "Set the monitor screen brightness level.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "level": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "The brightness level percentage (0 to 100)."
                        }
                    },
                    "required": ["level"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "set_keyboard_backlight",
                "description": "Toggle the laptop keyboard backlight ON or OFF.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "string",
                            "enum": ["ON", "OFF"],
                            "description": "The keyboard backlight state."
                        }
                    },
                    "required": ["state"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "switch_window_tab",
                "description": "Switch the active window (Alt+Tab) or the active browser tab (Ctrl+Tab).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "enum": ["window", "tab"],
                            "description": "Whether to switch active window or switch active tab."
                        }
                    },
                    "required": ["target"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "type_text",
                "description": "Type text Unicode character-by-character into the active foreground application window.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The exact text message or sentence to type."
                        }
                    },
                    "required": ["text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "control_media",
                "description": "Control system media keys like play, pause, stop, mute, next track, or volume adjustment.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["play", "pause", "next", "prev", "stop", "mute", "volume_up", "volume_down"],
                            "description": "The media command to execute."
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "research_topic",
                "description": "Perform a search query using DuckDuckGo and return a summarized AI report.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query topic to research."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "plan_my_day",
                "description": "Compile calendar events and emails into a timeline tasks schedule.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://127.0.0.1:5000",
        "X-Title": "Jarvis 2.0"
    }
    
    messages = []
    messages.append({
        "role": "system",
        "content": (
            "You are JARVIS, a highly advanced personal desktop assistant for the user's laptop, reminiscent of Iron Man's JARVIS. "
            "Be helpful, professional, slightly witty, and refer to the user as 'Sir'. "
            "When the user asks you to perform an action, you MUST call the appropriate tool. "
            "When the user wants you to exit, go offline, shutdown, or says goodbye, call the 'go_offline' tool. "
            "Your response should be what you will say verbally *before* the action takes place. For example, if you call open_app(app_name='whatsapp'), you should say: 'Right away, Sir. Opening WhatsApp now.' "
            "Do not explain that you are calling a function; talk as if you are doing it yourself. "
            "You have access to real-time system stats (CPU, RAM, Battery, Disk) passed in your prompt. If the user asks about system performance or stats, use that info to answer them directly and do not run any tools. "
            "Keep your responses extremely concise, direct, and conversational (ideally under 15 words) to ensure maximum verbal speed."
        )
    })
    
    for msg in history:
        role = "user" if msg.get("role") == "user" else "assistant"
        messages.append({
            "role": role,
            "content": msg.get("text", "")
        })
        
    stats_context = ""
    if system_stats:
        stats_context = (
            f"\n[System Status: CPU {system_stats.get('cpu_usage')}% | "
            f"RAM {system_stats.get('ram_usage')}% | "
            f"Battery {system_stats.get('battery_percent')}% (Charging: {system_stats.get('battery_charging')}) | "
            f"Free Disk {system_stats.get('disk_free_gb')}GB / {system_stats.get('disk_total_gb')}GB]"
        )
    messages.append({
        "role": "user",
        "content": f"{prompt}{stats_context}"
    })
    
    payload = {
        "model": "google/gemini-2.5-flash",
        "messages": messages,
        "tools": tools_schema,
        "tool_choice": "auto",
        "max_tokens": 150
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=15
    )
    
    if response.status_code != 200:
        return jsonify({
            "status": "error",
            "message": f"OpenRouter API Error {response.status_code}: {response.text}"
        }), response.status_code
        
    res_data = response.json()
    if "error" in res_data:
        return jsonify({
            "status": "error",
            "message": f"OpenRouter Error: {res_data['error'].get('message', 'Unknown API error')}"
        }), 500
        
    choice = res_data["choices"][0]
    message = choice["message"]
    text_response = message.get("content", "")
    tool_call = None
    
    if "tool_calls" in message and message["tool_calls"]:
        openai_tool_call = message["tool_calls"][0]
        func_name = openai_tool_call["function"]["name"]
        try:
            func_args = json.loads(openai_tool_call["function"]["arguments"])
        except Exception:
            func_args = {}
            
        tool_call = {
            "name": func_name,
            "args": func_args
        }
        
    if not text_response and tool_call:
        action_name = tool_call["name"].replace("_", " ")
        text_response = f"Certainly, Sir. Working on {action_name} now."
        
    if not text_response:
        text_response = "I am not sure how to respond to that, Sir."
        
    return jsonify({
        "status": "success",
        "text_response": text_response.strip(),
        "tool_call": tool_call
    })


@app.route('/api/query', methods=['POST'])
def query_jarvis():
    data = request.json or {}
    prompt = data.get("prompt", "").strip()
    history = data.get("history", [])
    system_stats = data.get("system_stats", {})
    
    if not prompt:
        return jsonify({"status": "error", "message": "Prompt is required."}), 400

    # COMPONENT 11: Real-time internet connectivity check for Offline Command Fallback routing
    if not has_internet():
        offline_res = system_tools.offline_command_router(prompt)
        # Convert simple tools results format
        tool_call = None
        if "tool_call" in offline_res:
            tool_call = offline_res["tool_call"]
        elif "offline" in offline_res.get("text_response", "").lower() and "unparsed" not in offline_res.get("result", ""):
            # Check what tool was run internally
            tool_name = "unknown"
            if "opening" in offline_res["text_response"].lower():
                tool_name = "open_app"
            elif "closing" in offline_res["text_response"].lower():
                tool_name = "close_app"
            elif "browsing" in offline_res["text_response"].lower():
                tool_name = "open_website"
            elif "volume" in offline_res["text_response"].lower():
                tool_name = "volume_control"
            elif "screenshot" in offline_res["text_response"].lower():
                tool_name = "take_screenshot"
            elif "note" in offline_res["text_response"].lower():
                tool_name = "write_note"
            elif "shutdown" in offline_res["text_response"].lower() or "restart" in offline_res["text_response"].lower():
                tool_name = "system_power_control"
                
            tool_call = {
                "name": tool_name,
                "args": {"offline_run": True, "result": offline_res["result"]}
            }
            
        return jsonify({
            "status": "success",
            "is_offline": True,
            "text_response": "[LOCAL OFFLINE ENGINE]: " + offline_res["text_response"],
            "tool_call": tool_call
        })

    api_key = get_api_key()
    if not api_key:
        return jsonify({
            "status": "error",
            "message": "API Key is not configured. Please go to settings and add your API Key."
        }), 400
        
    try:
        if api_key.startswith("sk-or-"):
            return query_openrouter(api_key, prompt, history, system_stats)
            
        genai.configure(api_key=api_key)
        
        # Register ALL tools for native Gemini
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=[
                control_iot_device, open_app, close_app, send_message_to_app, open_website, volume_control, 
                take_screenshot, write_note, execute_shell_command, go_offline, close_browser_tab,
                system_power_control, get_active_window_context, add_calendar_event, 
                list_calendar_events, modify_calendar_event, check_emails, read_email_content, 
                send_email, organize_directory, search_files, manage_file_operation, 
                run_disk_cleanup, check_system_updates, manage_workflow, run_workflow,
                set_wifi_state, set_bluetooth_state, set_airplane_mode_state, set_energy_saver_state, set_nightlight_state,
                set_active_window_state, set_screen_brightness, set_keyboard_backlight,
                switch_window_tab, type_text, control_media, research_topic, plan_my_day
            ],
            system_instruction=(
                "You are JARVIS, a highly advanced personal desktop assistant for the user's laptop, reminiscent of Iron Man's JARVIS. "
                "Be helpful, professional, slightly witty, and refer to the user as 'Sir'. "
                "When the user asks you to perform an action, you MUST select and call the appropriate tool. "
                "When the user wants you to exit, go offline, shutdown, or says goodbye, call the 'go_offline' tool. "
                "Your response should be what you will say verbally *before* the action takes place. For example, if you call open_app(app_name='whatsapp'), you should say: 'Right away, Sir. Opening WhatsApp now.' "
                "Do not explain that you are calling a function; talk as if you are doing it yourself. "
                "You have access to real-time system stats (CPU, RAM, Battery, Disk) passed in your prompt. If the user asks about system performance or stats, use that info to answer them directly and do not run any tools. "
                "Keep your responses extremely concise, direct, and conversational (ideally under 15 words) to ensure maximum verbal speed."
            )
        )
        
        contents = []
        for msg in history:
            role = "user" if msg.get("role") == "user" else "model"
            msg_text = msg.get("text", "")
            contents.append({
                "role": role,
                "parts": [msg_text]
            })
            
        stats_context = ""
        if system_stats:
            stats_context = (
                f"\n[System Status: CPU {system_stats.get('cpu_usage')}% | "
                f"RAM {system_stats.get('ram_usage')}% | "
                f"Battery {system_stats.get('battery_percent')}% (Charging: {system_stats.get('battery_charging')}) | "
                f"Free Disk {system_stats.get('disk_free_gb')}GB / {system_stats.get('disk_total_gb')}GB]"
            )
            
        prompt_with_stats = f"{prompt}{stats_context}"
        contents.append({
            "role": "user",
            "parts": [prompt_with_stats]
        })
        
        response = model.generate_content(contents, request_options={"retry": None})
        
        text_response = ""
        tool_call = None
        
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.text:
                    text_response += part.text
                elif part.function_call:
                    tool_call = {
                        "name": part.function_call.name,
                        "args": dict(part.function_call.args)
                    }
                    
        if not text_response and tool_call:
            action_name = tool_call["name"].replace("_", " ")
            text_response = f"Certainly, Sir. Working on {action_name} now."
            
        if not text_response:
            text_response = "I am not sure how to respond to that, Sir."
            
        return jsonify({
            "status": "success",
            "text_response": text_response.strip(),
            "tool_call": tool_call
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Fallback offline parsing if AI fails due to network/API error
        try:
            offline_res = system_tools.offline_command_router(prompt)
            return jsonify({
                "status": "success",
                "is_offline": True,
                "text_response": "[API ERROR FALLBACK]: " + offline_res["text_response"],
                "tool_call": None
            })
        except Exception:
            return jsonify({"status": "error", "message": f"Core API Error: {str(e)}"}), 500


@app.route('/api/execute_tool', methods=['POST'])
def execute_tool():
    try:
        data = request.json or {}
        name = data.get("name", "")
        args = data.get("args", {})
        
        # Write to debug log file
        try:
            from datetime import datetime
            log_path = os.path.join(os.path.dirname(__file__), "jarvis_debug.log")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] /api/execute_tool name='{name}' args='{args}'\n")
        except Exception:
            pass
            
        if not name:
            return jsonify({"status": "error", "message": "Tool name is required."}), 400
            
        # If tool was already executed offline, return the offline result
        if args.get("offline_run") and args.get("result"):
            return jsonify({
                "status": "success",
                "result": args.get("result")
            })

        result = ""
        
        if name == "control_iot_device":
            result = str(system_tools.control_iot_device(args.get("device_id", ""), args.get("action", ""), args.get("value")))
        elif name == "set_wifi_state":
            result = system_tools.set_wifi_state(args.get("state", ""))
        elif name == "set_bluetooth_state":
            result = system_tools.set_bluetooth_state(args.get("state", ""))
        elif name == "set_airplane_mode_state":
            result = system_tools.set_airplane_mode_state(args.get("state", ""))
        elif name == "set_energy_saver_state":
            result = system_tools.set_energy_saver_state(args.get("state", ""))
        elif name == "set_nightlight_state":
            result = system_tools.set_nightlight_state(args.get("state", ""))
        elif name == "set_active_window_state":
            result = system_tools.set_active_window_state(args.get("action", ""))
        elif name == "set_screen_brightness":
            result = system_tools.set_screen_brightness(args.get("level", 50))
        elif name == "set_keyboard_backlight":
            result = system_tools.set_keyboard_backlight(args.get("state", ""))
        elif name == "switch_window_tab":
            result = system_tools.switch_window_tab(args.get("target", "window"))
        elif name == "type_text":
            result = system_tools.type_text(args.get("text", ""))
        elif name == "control_media":
            result = system_tools.control_media(args.get("action", ""))
        elif name == "research_topic":
            result = system_tools.research_topic(args.get("query", ""))
        elif name == "plan_my_day":
            result = system_tools.plan_my_day()
        elif name == "open_app":
            result = system_tools.open_app(args.get("app_name", ""))
        elif name == "close_app":
            result = system_tools.close_app(args.get("app_name", ""))
        elif name == "send_message_to_app":
            result = system_tools.send_message_to_app(args.get("app_name", ""), args.get("message", ""), args.get("contact", ""))
        elif name == "close_browser_tab":
            result = system_tools.close_browser_tab(args.get("browser_name", ""))
        elif name == "open_website":
            result = system_tools.open_website(args.get("site_name", ""), args.get("search_query", ""))
        elif name == "volume_control":
            result = system_tools.volume_control(args.get("action", ""), args.get("value"))
        elif name == "take_screenshot":
            result = system_tools.take_screenshot()
        elif name == "write_note":
            result = system_tools.write_note(args.get("content", ""))
        elif name == "execute_shell_command":
            result = system_tools.execute_shell_command(args.get("command", ""))
        elif name == "system_power_control":
            result = system_tools.system_power_control(args.get("action", ""))
        elif name == "get_active_window_context":
            result = str(system_tools.get_active_window_context())
        elif name == "add_calendar_event":
            result = system_tools.add_calendar_event(
                args.get("title", ""), args.get("start_time", ""), args.get("end_time", ""), args.get("description", "")
            )
        elif name == "list_calendar_events":
            result = system_tools.list_calendar_events(args.get("query_date", ""))
        elif name == "modify_calendar_event":
            result = system_tools.modify_calendar_event(
                args.get("event_id", ""), args.get("action", ""), args.get("new_value", "")
            )
        elif name == "check_emails":
            result = system_tools.check_emails()
        elif name == "read_email_content":
            result = system_tools.read_email_content(args.get("email_id", ""))
        elif name == "send_email":
            result = system_tools.send_email(
                args.get("to_email", ""), args.get("subject", ""), args.get("body", "")
            )
        elif name == "organize_directory":
            result = system_tools.organize_directory(args.get("directory_path", ""))
        elif name == "search_files":
            result = system_tools.search_files(args.get("search_query", ""), args.get("root_path", ""))
        elif name == "manage_file_operation":
            result = system_tools.manage_file_operation(
                args.get("action", ""), args.get("source_path", ""), args.get("target_path", "")
            )
        elif name == "run_disk_cleanup":
            result = system_tools.run_disk_cleanup(
                args.get("clean_temp", True), args.get("clean_cache", True)
            )
        elif name == "check_system_updates":
            result = system_tools.check_system_updates()
        elif name == "manage_workflow":
            result = system_tools.manage_workflow(
                args.get("action", ""), args.get("name", ""), args.get("steps")
            )
        elif name == "run_workflow":
            result = system_tools.run_workflow(args.get("name", ""))
        elif name == "go_offline":
            import threading
            import time
            import os
            import subprocess
            def shutdown_server():
                time.sleep(3.0)
                try:
                    ppid = os.getppid()
                    subprocess.run(f"taskkill /F /PID {ppid} /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    os._exit(0)
            threading.Thread(target=shutdown_server, daemon=True).start()
            result = "Server shutdown scheduled in 3.0 seconds."
        else:
            return jsonify({"status": "error", "message": f"Unknown tool: {name}"}), 400
            
        return jsonify({
            "status": "success",
            "result": result
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Tool execution failed: {str(e)}"}), 500


# =====================================================================
#                      DIRECT ENDPOINTS FOR PREMIUM UI
# =====================================================================

@app.route('/api/calendar', methods=['GET'])
def get_calendar():
    events = system_tools._load_calendar()
    return jsonify(events)


@app.route('/api/calendar/add', methods=['POST'])
def add_calendar():
    data = request.json or {}
    title = data.get("title", "")
    start_time = data.get("start_time", "")
    end_time = data.get("end_time", "")
    description = data.get("description", "")
    res = system_tools.add_calendar_event(title, start_time, end_time, description)
    return jsonify({"status": "success", "result": res})


@app.route('/api/calendar/delete', methods=['POST'])
def delete_calendar():
    data = request.json or {}
    event_id = data.get("id", "")
    res = system_tools.modify_calendar_event(event_id, "delete")
    return jsonify({"status": "success", "result": res})


def get_emails_list():
    import imaplib
    from email.header import decode_header
    creds = system_tools._get_email_credentials()
    if not creds["email"] or not creds["password"]:
        # Mock inbox for visual wow factor if credentials are blank
        return [
            {"id": "1", "from": "Pepper Potts <pepper@stark.com>", "subject": "Stark Industries Quarterly Report & Arc Reactor status", "priority": "High"},
            {"id": "2", "from": "Nick Fury <fury@shield.gov>", "subject": "S.H.I.E.L.D. Project Avengers Initiative update required", "priority": "High"},
            {"id": "3", "from": "Github Engines <noreply@github.com>", "subject": "Build Successful: Jarvis Core 2.5 local-offline-routing", "priority": "Work"},
            {"id": "4", "from": "Tony Stark <tony@stark.com>", "subject": "Vocal pitch biometrics verification check", "priority": "Work"},
            {"id": "5", "from": "Amazon Systems <orders@amazon.com>", "subject": "Your package of custom electronic circuits was shipped", "priority": "Low"},
        ]
    try:
        mail = imaplib.IMAP4_SSL(creds["imap_server"], creds["imap_port"])
        mail.login(creds["email"], creds["password"])
        mail.select("inbox")
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            mail.logout()
            return []
        mail_ids = messages[0].split()
        unread_emails = []
        for mail_id in reversed(mail_ids[-8:]):
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    import email
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")
                    from_sender, encoding = decode_header(msg["From"])[0]
                    if isinstance(from_sender, bytes):
                        from_sender = from_sender.decode(encoding or "utf-8", errors="ignore")
                    priority = "Normal"
                    from_lower = from_sender.lower()
                    subj_lower = subject.lower()
                    if "urgent" in subj_lower or "action required" in subj_lower or "important" in subj_lower:
                        priority = "High"
                    elif "github" in from_lower or "jira" in from_lower or "google" in from_lower:
                        priority = "Work"
                    elif "newsletter" in subj_lower or "offer" in subj_lower or "promo" in subj_lower:
                        priority = "Low"
                    unread_emails.append({
                        "id": mail_id.decode(),
                        "from": from_sender,
                        "subject": subject,
                        "priority": priority
                    })
        mail.logout()
        return unread_emails
    except Exception:
        # Fallback to mock inbox if login fails
        return [
            {"id": "1", "from": "Pepper Potts <pepper@stark.com>", "subject": "Stark Industries Quarterly Report & Arc Reactor status", "priority": "High"},
            {"id": "2", "from": "Nick Fury <fury@shield.gov>", "subject": "S.H.I.E.L.D. Project Avengers Initiative update required", "priority": "High"},
            {"id": "3", "from": "Github Engines <noreply@github.com>", "subject": "Build Successful: Jarvis Core 2.5 local-offline-routing", "priority": "Work"},
            {"id": "4", "from": "Tony Stark <tony@stark.com>", "subject": "Vocal pitch biometrics verification check", "priority": "Work"},
        ]


@app.route('/api/emails', methods=['GET'])
def get_emails_api():
    emails = get_emails_list()
    return jsonify(emails)


@app.route('/api/email/send', methods=['POST'])
def send_email_api():
    data = request.json or {}
    to_email = data.get("to_email", "")
    subject = data.get("subject", "")
    body = data.get("body", "")
    res = system_tools.send_email(to_email, subject, body)
    return jsonify({"status": "success", "result": res})


@app.route('/api/workflows', methods=['GET'])
def get_workflows_api():
    wfs = system_tools._load_workflows()
    return jsonify(wfs)


@app.route('/api/workflows/create', methods=['POST'])
def create_workflow_api():
    data = request.json or {}
    name = data.get("name", "")
    steps = data.get("steps", [])
    res = system_tools.manage_workflow("create", name, steps)
    return jsonify({"status": "success", "result": res})


@app.route('/api/workflows/delete', methods=['POST'])
def delete_workflow_api():
    data = request.json or {}
    name = data.get("name", "")
    res = system_tools.manage_workflow("delete", name)
    return jsonify({"status": "success", "result": res})


@app.route('/api/workflows/run', methods=['POST'])
def run_workflow_api():
    data = request.json or {}
    name = data.get("name", "")
    res = system_tools.run_workflow(name)
    return jsonify({"status": "success", "result": res})


@app.route('/api/active_window', methods=['GET'])
def active_window_api():
    res = system_tools.get_active_window_context()
    return jsonify(res)


@app.route('/api/maintenance/clean', methods=['POST'])
def clean_maintenance():
    res = system_tools.run_disk_cleanup(True, True)
    return jsonify({"status": "success", "result": res})


@app.route('/api/save_email_settings', methods=['POST'])
def save_email_settings():
    try:
        data = request.json or {}
        email_addr = data.get('email', '').strip()
        password = data.get('password', '').strip()
        imap = data.get('imap', '').strip()
        port_imap = data.get('port_imap', '993').strip()
        smtp = data.get('smtp', '').strip()
        port_smtp = data.get('port_smtp', '587').strip()
        
        # Read current .env
        env_lines = []
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                env_lines = f.readlines()
                
        new_lines = []
        for line in env_lines:
            if not (line.startswith("JARVIS_EMAIL") or line.startswith("JARVIS_IMAP") or line.startswith("JARVIS_SMTP")):
                new_lines.append(line)
                
        new_lines.append(f"JARVIS_EMAIL={email_addr}\n")
        new_lines.append(f"JARVIS_EMAIL_PASSWORD={password}\n")
        new_lines.append(f"JARVIS_IMAP_SERVER={imap}\n")
        new_lines.append(f"JARVIS_IMAP_PORT={port_imap}\n")
        new_lines.append(f"JARVIS_SMTP_SERVER={smtp}\n")
        new_lines.append(f"JARVIS_SMTP_PORT={port_smtp}\n")
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
        load_dotenv(override=True)
        return jsonify({"status": "success", "message": "Email settings saved successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to save email settings: {str(e)}"}), 500


@app.route('/api/flows', methods=['GET'])
def get_flows_api():
    try:
        flows = system_tools.get_visual_flows()
        return jsonify(flows)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/flows/save', methods=['POST'])
def save_flow_api():
    try:
        data = request.json or {}
        name = data.get("name", "")
        nodes = data.get("nodes", [])
        links = data.get("links", [])
        if not name:
            return jsonify({"status": "error", "message": "Flow name is required."}), 400
        res = system_tools.save_visual_flow(name, nodes, links)
        return jsonify({"status": "success", "result": res})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/flows/delete', methods=['POST'])
def delete_flow_api():
    try:
        data = request.json or {}
        name = data.get("name", "")
        if not name:
            return jsonify({"status": "error", "message": "Flow name is required."}), 400
        res = system_tools.delete_visual_flow(name)
        return jsonify({"status": "success", "result": res})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


last_timer_execution = {}

def flow_trigger_monitor():
    import time
    import logging
    
    time.sleep(3)
    logging.info("Visual Flow Trigger Monitor Thread started.")
    
    while True:
        try:
            flows = system_tools.get_visual_flows()
            if not flows:
                time.sleep(4)
                continue
                
            stats = system_tools.get_system_stats()
            cpu_usage = stats.get('cpu_usage', 0)
            ram_usage = stats.get('ram_usage', 0)
            
            # System Health Optimization: Trigger automatic disk clean if RAM exceeds 90%
            if ram_usage > 90:
                logging.warning("RAM usage exceeds 90%. Auto-cleaning temp folders to optimize system health.")
                try:
                    system_tools.run_disk_cleanup(clean_temp=True, clean_cache=True)
                except Exception as ex:
                    logging.error(f"Auto disk cleanup failed: {ex}")
            
            now = time.time()
            
            for flow_name, flow_data in flows.items():
                nodes = flow_data.get("nodes", [])
                links = flow_data.get("links", [])
                
                trigger_nodes = [n for n in nodes if n.get("type") == "trigger"]
                
                for trigger in trigger_nodes:
                    is_triggered = False
                    trigger_id = trigger.get("id")
                    action_type = trigger.get("action")
                    params = trigger.get("params", {})
                    
                    if action_type == "cpu_overload":
                        if cpu_usage > 80:
                            key = f"{flow_name}_{trigger_id}"
                            if now - last_timer_execution.get(key, 0) > 30:
                                is_triggered = True
                                last_timer_execution[key] = now
                    elif action_type == "timer":
                        interval = int(params.get("interval", 10))
                        key = f"{flow_name}_{trigger_id}"
                        last_run = last_timer_execution.get(key, 0)
                        if last_run == 0:
                            last_timer_execution[key] = now
                        elif now - last_run >= interval:
                            is_triggered = True
                            last_timer_execution[key] = now
                            
                    if is_triggered:
                        connected_action_ids = [l.get("to") for l in links if l.get("from") == trigger_id]
                        action_nodes = [n for n in nodes if n.get("id") in connected_action_ids and n.get("type") == "action"]
                        
                        for act in action_nodes:
                            act_type = act.get("action")
                            act_params = act.get("params", {})
                            
                            logging.info(f"Executing Flow Action: {flow_name} -> {act_type} with parameters {act_params}")
                            
                            try:
                                if act_type == "launch_app":
                                    system_tools.open_app(act_params.get("app_name", "notepad"))
                                elif act_type == "set_volume":
                                    system_tools.volume_control("set", int(act_params.get("volume", 50)))
                                elif act_type == "open_site":
                                    system_tools.open_website(act_params.get("url", "google.com"))
                                elif act_type == "iot_control":
                                    system_tools.control_iot_device(
                                        act_params.get("device_id", ""),
                                        act_params.get("action", "ON"),
                                        act_params.get("value")
                                    )
                            except Exception as ex:
                                logging.error(f"Error executing flow action {act_type}: {ex}")
                                
        except Exception as e:
            logging.error(f"Error in flow_trigger_monitor loop: {e}")
            
        time.sleep(4)


def monitor_global_hotkey():
    import ctypes
    import ctypes.wintypes
    import webbrowser
    import time
    import logging
    
    user32 = ctypes.windll.user32
    MOD_CONTROL = 2
    MOD_SHIFT = 4
    VK_J = 74
    
    time.sleep(2)
    
    if user32.RegisterHotKey(None, 1, MOD_CONTROL | MOD_SHIFT, VK_J):
        logging.info("Global Wake Hotkey (Ctrl+Shift+J) registered successfully.")
        try:
            msg = ctypes.wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == 0x0312:  # WM_HOTKEY
                    logging.info("Global Wake Hotkey pressed. Opening browser to wake Jarvis.")
                    webbrowser.open("http://127.0.0.1:5000")
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        except Exception as e:
            logging.error(f"Error in global hotkey event loop: {e}")
        finally:
            user32.UnregisterHotKey(None, 1)
    else:
        logging.warning("Failed to register Global Wake Hotkey (Ctrl+Shift+J). Code might already be bound.")


if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    app.debug = True
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        import threading
        import time
        import webbrowser
        
        def open_browser():
            time.sleep(1.5)
            webbrowser.open("http://127.0.0.1:5000")
            
        threading.Thread(target=open_browser, daemon=True).start()
        threading.Thread(target=flow_trigger_monitor, daemon=True).start()
        threading.Thread(target=monitor_global_hotkey, daemon=True).start()
    
    app.run(host='127.0.0.1', port=5000, debug=True)

