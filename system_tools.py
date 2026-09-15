import os
import subprocess
import webbrowser
import urllib.parse
import time
from datetime import datetime

# Initialize optional libraries
try:
    import psutil
except ImportError:
    psutil = None

try:
    import pyautogui
except ImportError:
    pyautogui = None


def open_app(app_name: str) -> str:
    """
    Launches a local application on Windows.
    Supports system applications, custom URI schemes, and searches Windows Start Menu / Desktop shortcuts.
    """
    app_name = app_name.lower().strip()
    
    app_mappings = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "paint": "mspaint.exe",
        "mspaint": "mspaint.exe",
        "whatsapp": "whatsapp://",
        "spotify": "spotify://",
        "discord": "discord://",
        "chrome": "chrome.exe",
        "browser": "chrome.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe",
        "task manager": "taskmgr.exe",
        "taskmgr": "taskmgr.exe",
        "settings": "ms-settings:",
        "control panel": "control.exe",
    }
    
    # Handle "browser" open request specially via webbrowser if chrome is missing
    if app_name in ["browser", "web browser"]:
        try:
            webbrowser.open("https://www.google.com")
            return "Successfully opened default web browser."
        except Exception as e:
            return f"Failed to open browser. Error: {str(e)}"
            
    # Step 1: Check hardcoded mappings first
    if app_name in app_mappings:
        cmd = app_mappings[app_name]
        try:
            os.startfile(cmd)
            import time
            time.sleep(1.5)
            subprocess.run(["powershell", "-Command", f"$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('{app_name}')"], capture_output=True)
            return f"Successfully opened {app_name}."
        except Exception:
            pass # Fallback to shortcut search if startfile fails
            
    # Step 2: Search Windows Start Menu & Desktop for shortcuts (.lnk) or executables (.exe)
    try:
        username = os.getlogin()
    except Exception:
        username = os.environ.get("USERNAME", "default")
        
    search_dirs = [
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join("C:\\Users", username, "Desktop"),
        "C:\\Users\\Public\\Desktop"
    ]
    
    for base_dir in search_dirs:
        if not os.path.exists(base_dir):
            continue
            
        # Walk recursively to find matching shortcuts
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".lnk") or file.endswith(".exe"):
                    file_name_lower = file.lower()
                    name_without_ext = os.path.splitext(file_name_lower)[0]
                    
                    # Fuzzy match: does user request match the shortcut name? (e.g. "whatsapp" in "whatsapp.lnk")
                    if app_name in name_without_ext or name_without_ext in app_name:
                        shortcut_path = os.path.join(root, file)
                        try:
                            os.startfile(shortcut_path)
                            import time
                            time.sleep(1.5)
                            subprocess.run(["powershell", "-Command", f"$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('{app_name}')"], capture_output=True)
                            return f"Successfully located and opened {app_name} via shortcut: {file}."
                        except Exception:
                            pass
                            
    # Step 3: Direct shell run fallback
    try:
        os.startfile(app_name)
        import time
        time.sleep(1.5)
        subprocess.run(["powershell", "-Command", f"$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('{app_name}')"], capture_output=True)
        return f"Attempted to open '{app_name}' directly."
    except Exception as e:
        try:
            subprocess.Popen(app_name, shell=True)
            import time
            time.sleep(1.5)
            subprocess.run(["powershell", "-Command", f"$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('{app_name}')"], capture_output=True)
            return f"Attempted to run '{app_name}' via shell."
        except Exception as e2:
            return f"Could not find or launch application '{app_name}' on your laptop. Error: {str(e2)}"


def open_website(site_name: str, search_query: str = "") -> str:
    """
    Opens a website and optionally searches for a query.
    """
    site_name = site_name.lower().strip()
    
    site_mappings = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "github": "https://www.github.com",
        "stackoverflow": "https://www.stackoverflow.com",
        "wikipedia": "https://www.wikipedia.org",
        "gmail": "https://mail.google.com",
        "whatsapp web": "https://web.whatsapp.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://www.twitter.com",
        "linkedin": "https://www.linkedin.com",
    }
    
    url = site_mappings.get(site_name, site_name)
    if not url.startswith("http://") and not url.startswith("https://"):
        if "." in url:
            url = "https://" + url
        else:
            url = f"https://www.google.com/search?q={url}"
            
    if search_query:
        encoded_query = urllib.parse.quote(search_query)
        if "google" in url or "google.com" in url:
            url = f"https://www.google.com/search?q={encoded_query}"
        elif "youtube" in url or "youtube.com" in url:
            url = f"https://www.youtube.com/results?search_query={encoded_query}"
        elif "github" in url or "github.com" in url:
            url = f"https://github.com/search?q={encoded_query}"
        else:
            url = f"https://www.google.com/search?q={encoded_query}"
            
    try:
        webbrowser.open(url)
        return f"Successfully opened {site_name} with URL: {url}."
    except Exception as e:
        return f"Failed to open website. Error: {str(e)}"


def get_system_stats() -> dict:
    """
    Retrieves dynamic hardware metrics like CPU, Memory, battery level, Disk space and top resource-consuming applications.
    """
    stats = {
        "cpu_usage": 0.0,
        "ram_usage": 0.0,
        "battery_percent": "N/A",
        "battery_charging": False,
        "disk_free_gb": 0.0,
        "disk_total_gb": 0.0,
        "top_cpu_process": "None",
        "top_mem_process": "None"
    }
    
    if psutil:
        try:
            stats["cpu_usage"] = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            stats["ram_usage"] = ram.percent
            
            battery = psutil.sensors_battery()
            if battery:
                stats["battery_percent"] = battery.percent
                stats["battery_charging"] = battery.power_plugged
                
            disk = psutil.disk_usage('/')
            stats["disk_free_gb"] = round(disk.free / (1024 ** 3), 1)
            stats["disk_total_gb"] = round(disk.total / (1024 ** 3), 1)
            
            # Find resource intensive applications
            processes = []
            for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except Exception:
                    pass
            if processes:
                # Sort for Memory
                processes.sort(key=lambda x: x.get('memory_percent') or 0.0, reverse=True)
                if processes[0]:
                    stats["top_mem_process"] = f"{processes[0]['name']} ({round(processes[0]['memory_percent'], 1)}% RAM)"
                # Sort for CPU
                processes.sort(key=lambda x: x.get('cpu_percent') or 0.0, reverse=True)
                if processes[0]:
                    stats["top_cpu_process"] = f"{processes[0]['name']} ({round(processes[0]['cpu_percent'], 1)}% CPU)"
        except Exception as e:
            print(f"Error reading system stats: {e}")
            
    return stats


def volume_control(action: str, value: int = None) -> str:
    """
    Controls system volume via PowerShell shell commands.
    Actions: 'set' (requires value 0-100), 'mute', 'unmute', 'up', 'down'
    """
    action = action.lower().strip()
    
    # PowerShell command templates using ComObject Wscript.Shell SendKeys
    # 174: Volume Down, 175: Volume Up, 173: Mute/Unmute toggle
    
    if action == "mute" or action == "unmute":
        ps_script = "$wsh = New-Object -ComObject Wscript.Shell; $wsh.SendKeys([char]173)"
        subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
        return "Toggled system mute state."
        
    elif action == "up":
        ps_script = "$wsh = New-Object -ComObject Wscript.Shell; $wsh.SendKeys([char]175)"
        subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
        return "Increased system volume."
        
    elif action == "down":
        ps_script = "$wsh = New-Object -ComObject Wscript.Shell; $wsh.SendKeys([char]174)"
        subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
        return "Decreased system volume."
        
    elif action == "set" and value is not None:
        target_level = max(0, min(100, int(value)))
        steps_up = target_level // 2
        
        # Lower volume completely, then raise it to the desired level.
        # This is a highly robust method on Windows that doesn't need external C++ modules.
        ps_script = f"""
        $wsh = New-Object -ComObject Wscript.Shell;
        for ($i = 0; $i -lt 50; $i++) {{ $wsh.SendKeys([char]174) }};
        for ($i = 0; $i -lt {steps_up}; $i++) {{ $wsh.SendKeys([char]175) }};
        """
        subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
        return f"System volume set to {target_level}%."
        
    return "Invalid volume action requested."


def take_screenshot() -> str:
    """
    Takes a screen capture, saves it, and displays it.
    """
    try:
        sc_dir = os.path.join(os.path.expanduser("~"), "Pictures", "JarvisScreenshots")
        if not os.path.exists(sc_dir):
            os.makedirs(sc_dir)
            
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(sc_dir, filename)
        
        # Try pyautogui screenshot first
        pyautogui_success = False
        if pyautogui:
            try:
                pyautogui.screenshot(filepath)
                pyautogui_success = True
            except Exception:
                pass
                
        # Fall back to native PowerShell GDI+ screen capture (100% robust on Windows, no external package dependencies)
        if not pyautogui_success:
            import subprocess
            ps_cmd = (
                "Add-Type -AssemblyName System.Windows.Forms; "
                "Add-Type -AssemblyName System.Drawing; "
                "$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; "
                "$bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height; "
                "$graphics = [System.Drawing.Graphics]::FromImage($bitmap); "
                "$graphics.CopyFromScreen($screen.X, $screen.Y, 0, 0, $bitmap.Size); "
                f'$bitmap.Save("{filepath}", [System.Drawing.Imaging.ImageFormat]::Png); '
                "$graphics.Dispose(); "
                "$bitmap.Dispose();"
            )
            result = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
            if result.returncode != 0 or not os.path.exists(filepath):
                raise Exception(f"PowerShell capture failed: {result.stderr}")
        
        # Display the file
        try:
            os.startfile(filepath)
        except Exception:
            pass
            
        return f"Screenshot successfully saved and opened at: {filepath}"
    except Exception as e:
        return f"Failed to take screenshot. Error: {str(e)}"


def write_note(content: str) -> str:
    """
    Appends a quick note to jarvis_notes.txt.
    """
    try:
        notes_path = os.path.join(os.path.expanduser("~"), "Documents", "jarvis_notes.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(notes_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {content}\n")
            
        return f"Note successfully logged in: {notes_path}"
    except Exception as e:
        return f"Failed to save note. Error: {str(e)}"


def execute_shell_command(command: str) -> str:
    """
    Runs a shell command inside PowerShell. Returns console output or error.
    """
    try:
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, timeout=15)
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        response = []
        if output:
            response.append(output)
        if error:
            response.append(f"Error output:\n{error}")
            
        return "\n".join(response) if response else "Command executed successfully with no console output."
    except subprocess.TimeoutExpired:
        return "Command execution timed out after 15 seconds."
    except Exception as e:
        return f"Failed to execute command. Error: {str(e)}"


def close_app(app_name: str) -> str:
    """
    Closes a running application by terminating its process.
    """
    if not psutil:
        return "Cannot close applications because psutil is not installed."
        
    app_name = app_name.lower().strip()
    
    # Mappings for common processes
    process_mappings = {
        "notepad": ["notepad.exe"],
        "calculator": ["calculator.exe", "calc.exe", "calculatorapp.exe"],
        "calc": ["calc.exe"],
        "paint": ["mspaint.exe"],
        "whatsapp": ["whatsapp.exe"],
        "spotify": ["spotify.exe"],
        "discord": ["discord.exe"],
        "chrome": ["chrome.exe"],
        "browser": ["chrome.exe", "msedge.exe", "firefox.exe"],
        "explorer": ["explorer.exe"],
        "cmd": ["cmd.exe"],
        "powershell": ["powershell.exe"],
        "word": ["winword.exe"],
        "excel": ["excel.exe"],
        "powerpoint": ["powerpnt.exe"],
    }
    
    target_names = process_mappings.get(app_name, [app_name])
    extended_targets = []
    for t in target_names:
        extended_targets.append(t)
        if not t.endswith(".exe"):
            extended_targets.append(t + ".exe")
            
    closed_count = 0
    errors = []
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            match = False
            for target in extended_targets:
                target_lower = target.lower()
                if proc_name == target_lower or proc_name.startswith(target_lower) or target_lower in proc_name:
                    match = True
                    break
                    
            if match:
                proc.terminate()
                closed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            errors.append(str(e))
            
    if closed_count > 0:
        return f"Successfully closed {closed_count} instance(s) of '{app_name}'."
        
    # Fuzzy match fallback: search all processes where process name contains the requested app_name
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            if app_name in proc_name:
                proc.terminate()
                closed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    if closed_count > 0:
        return f"Successfully closed {closed_count} process(es) matching '{app_name}'."
        
    return f"No running application found matching '{app_name}'."


def activate_whatsapp_window(retries: int = 20, delay: float = 0.5) -> bool:
    """
    Tries to activate the WhatsApp window up to `retries` times, waiting `delay` seconds between each attempt.
    Returns True if successfully activated, False otherwise.
    """
    import subprocess
    import time
    
    cmd = "$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('WhatsApp')"
    for i in range(retries):
        result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
        if "True" in result.stdout:
            time.sleep(1.0)  # Let the window settle
            return True
        time.sleep(delay)
    return False


def launch_and_focus_whatsapp() -> bool:
    """
    Launches WhatsApp Desktop and forces it to the foreground.
    """
    import time
    
    # Try launching via URI scheme first
    opened = False
    try:
        os.startfile("whatsapp://")
        opened = True
    except Exception:
        pass
        
    if not opened:
        # Fallback: Search Start Menu / Desktop shortcuts just like open_app does
        try:
            username = os.getlogin()
        except Exception:
            username = os.environ.get("USERNAME", "default")
            
        search_dirs = [
            os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
            os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), "Microsoft", "Windows", "Start Menu", "Programs"),
            os.path.join("C:\\Users", username, "Desktop"),
            "C:\\Users\\Public\\Desktop"
        ]
        
        for base_dir in search_dirs:
            if opened:
                break
            if not os.path.exists(base_dir):
                continue
                
            for root, dirs, files in os.walk(base_dir):
                if opened:
                    break
                for file in files:
                    if file.endswith(".lnk") or file.endswith(".exe"):
                        if "whatsapp" in file.lower():
                            shortcut_path = os.path.join(root, file)
                            try:
                                os.startfile(shortcut_path)
                                opened = True
                                break
                            except Exception:
                                pass
                                
    # Wait for WhatsApp to become active (up to 10 seconds timeout)
    activated = activate_whatsapp_window(retries=20, delay=0.5)
    return activated


def send_message_to_app(app_name: str, message: str, contact: str = "") -> str:
    """
    Sends a text message or types text into a given application.
    Supports whatsapp, notepad, discord, word, terminals, etc.
    """
    app_name = app_name.lower().strip()
    message = message.strip()
    contact = contact.strip()
    
    if not message:
        return "Message content is empty."
        
    # 1. WhatsApp Integration
    if "whatsapp" in app_name:
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        
        if contact:
            # Check if contact is a phone number
            cleaned_contact = contact.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            is_phone = False
            phone_num = ""
            
            if cleaned_contact.startswith("+") and cleaned_contact[1:].isdigit():
                is_phone = True
                phone_num = cleaned_contact
            elif cleaned_contact.isdigit():
                is_phone = True
                phone_num = cleaned_contact
                if len(phone_num) == 10:
                    phone_num = "+91" + phone_num
                    
            if is_phone:
                url = f"whatsapp://send?phone={phone_num}&text={encoded_message}"
                try:
                    os.startfile(url)
                    
                    # Wait for WhatsApp to open and become active
                    activated = activate_whatsapp_window(retries=20, delay=0.5)
                    
                    if pyautogui:
                        # First enter: dismisses the start chat prompt or focuses
                        pyautogui.press("enter")
                        time.sleep(1.5)
                        
                        # Force focus again
                        activate_whatsapp_window(retries=5, delay=0.3)
                        
                        # Second enter: sends the pre-filled text message
                        pyautogui.press("enter")
                        time.sleep(0.5)
                        pyautogui.hotkey('ctrl', 'enter')
                    return f"Opened WhatsApp chat with phone number '{phone_num}' and sent message: '{message}'"
                except Exception:
                    try:
                        webbrowser.open(f"https://web.whatsapp.com/send?phone={phone_num}&text={encoded_message}")
                        return f"Opened WhatsApp Web chat with phone number '{phone_num}' to send message: '{message}'"
                    except Exception as e:
                        return f"Failed to open WhatsApp for phone number '{phone_num}'. Error: {str(e)}"
            else:
                # Automate sending to a contact name via pyautogui search
                try:
                    activated = launch_and_focus_whatsapp()
                    if not activated:
                        # Try one more time to activate if it was already running
                        activate_whatsapp_window(retries=5, delay=0.5)
                        
                    if not pyautogui:
                        return f"Opened WhatsApp. Please select contact '{contact}' manually to send: '{message}'"
                    
                    # Press Ctrl+F to search
                    pyautogui.hotkey('ctrl', 'f')
                    time.sleep(0.5)
                    # Clear search bar
                    pyautogui.hotkey('ctrl', 'a')
                    pyautogui.press('backspace')
                    time.sleep(0.5)
                    
                    # Type the contact name
                    pyautogui.write(contact)
                    time.sleep(1.5)  # Wait for search results to load
                    
                    # Press Down arrow to navigate from search bar to the first result
                    pyautogui.press('down')
                    time.sleep(0.5)
                    
                    # Press Enter to open the chat
                    pyautogui.press('enter')
                    time.sleep(1.5)  # Wait for chat window to load
                    
                    # Type the message and send it
                    pyautogui.write(message)
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    time.sleep(0.5)
                    pyautogui.hotkey('ctrl', 'enter')
                    
                    return f"Opened WhatsApp, searched for contact '{contact}', and sent message: '{message}'"
                except Exception as e:
                    return f"Failed to automate WhatsApp for contact '{contact}'. Error: {str(e)}"
        else:
            # Standard share window without contact
            try:
                activated = launch_and_focus_whatsapp()
                if not activated:
                    activate_whatsapp_window(retries=5, delay=0.5)
                
                url = f"whatsapp://send?text={encoded_message}"
                os.startfile(url)
                return f"Opened WhatsApp to send message: '{message}'"
            except Exception:
                try:
                    webbrowser.open(f"https://web.whatsapp.com/send?text={encoded_message}")
                    return f"Opened WhatsApp Web to send message: '{message}'"
                except Exception as e:
                    return f"Failed to open WhatsApp. Error: {str(e)}"
                
    # 2. Notepad Integration
    if "notepad" in app_name:
        if not pyautogui:
            return "PyAutoGUI is not installed; cannot type into Notepad."
        try:
            subprocess.Popen("notepad.exe")
            time.sleep(1.0)
            
            # Force focus on Notepad
            subprocess.run(["powershell", "-Command", "$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('Notepad')"], capture_output=True)
            time.sleep(0.5)
            
            pyautogui.write(message, interval=0.01)
            pyautogui.press("enter")
            return f"Successfully opened Notepad and typed message: '{message}'"
        except Exception as e:
            return f"Failed to type message into Notepad. Error: {str(e)}"
            
    # 3. Word Integration
    if "word" in app_name or "winword" in app_name:
        if not pyautogui:
            return "PyAutoGUI is not installed; cannot type into MS Word."
        try:
            open_app("word")
            time.sleep(2.5) # Wait for Word to initialize
            
            # Force focus on Word
            subprocess.run(["powershell", "-Command", "$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('Word')"], capture_output=True)
            time.sleep(0.5)
            
            pyautogui.write(message, interval=0.01)
            return f"Attempted to open MS Word and type message: '{message}'"
        except Exception as e:
            return f"Failed to send message to MS Word. Error: {str(e)}"

    # 4. Command Prompt / Terminal Integration
    if app_name in ["cmd", "command prompt", "terminal", "powershell"]:
        if not pyautogui:
            return "PyAutoGUI is not installed; cannot type into terminal."
        try:
            if "powershell" in app_name:
                subprocess.Popen("powershell.exe")
            else:
                subprocess.Popen("cmd.exe")
            time.sleep(1.0)
            
            # Force focus on Terminal
            title = "PowerShell" if "powershell" in app_name else "Command Prompt"
            subprocess.run(["powershell", "-Command", f"$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('{title}')"], capture_output=True)
            time.sleep(0.5)
            
            pyautogui.write(message, interval=0.01)
            pyautogui.press("enter")
            return f"Opened terminal and executed command: '{message}'"
        except Exception as e:
            return f"Failed to execute command in terminal. Error: {str(e)}"
            
    # 5. Clipboard Fallback + App Launch (useful for Discord, Spotify, etc.)
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(message)
        root.update()
        root.destroy()
        
        # Try to open target app so user can paste
        launch_result = open_app(app_name)
        
        # Try to focus after launching
        subprocess.run(["powershell", "-Command", f"$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('{app_name}')"], capture_output=True)
        
        return f"Copied message '{message}' to clipboard and launched '{app_name}'. Press Ctrl+V to paste. Details: {launch_result}"
    except Exception as e:
        return f"Could not send message to '{app_name}'. Clipboard copy failed: {str(e)}"


def close_browser_tab(browser_name: str = "") -> str:
    """
    Closes the active tab in the specified web browser (e.g. chrome, edge, firefox) by focusing it and sending Ctrl+W.
    """
    if not pyautogui:
        return "PyAutoGUI is not installed; cannot close browser tab."
        
    browser_name = browser_name.lower().strip()
    
    # Try to determine which browser to focus
    target_app = "chrome"
    if "edge" in browser_name:
        target_app = "msedge"
    elif "firefox" in browser_name:
        target_app = "firefox"
    elif "chrome" in browser_name:
        target_app = "chrome"
    else:
        # Default: try to look for Chrome first, then Edge, then Firefox
        target_app = "chrome"
        
    # We can activate it using PowerShell
    import subprocess
    import time
    
    # Let's map target_app to Window title substring
    title_map = {
        "chrome": "Google Chrome",
        "msedge": "Microsoft Edge",
        "firefox": "Mozilla Firefox"
    }
    
    title = title_map.get(target_app, "Google Chrome")
    
    # Try to activate the window first
    cmd = f"$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('{title}')"
    res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
    
    # If the default target wasn't found, try the others
    if "False" in res.stdout or not res.stdout.strip():
        # Try other browsers
        for key, t in title_map.items():
            if t != title:
                cmd = f"$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('{t}')"
                res2 = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
                if "True" in res2.stdout:
                    title = t
                    break
                    
    time.sleep(0.5)
    
    # Send Ctrl+W to close tab
    pyautogui.hotkey('ctrl', 'w')
    return f"Successfully closed browser tab in '{title}' by sending Ctrl+W."


# =====================================================================
#                      NEW ADDED JARVIS 2.0 TOOLS
# =====================================================================

import json
import re
import shutil
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.header import decode_header

CALENDAR_FILE = os.path.join(os.path.dirname(__file__), "jarvis_calendar.json")
WORKFLOWS_FILE = os.path.join(os.path.dirname(__file__), "jarvis_workflows.json")


def system_power_control(action: str) -> str:
    """
    Executes system power commands: shutdown, restart, signout, sleep.
    """
    action = action.lower().strip()
    
    # Write to debug log file
    try:
        log_path = os.path.join(os.path.dirname(__file__), "jarvis_debug.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] system_power_control action='{action}'\n")
    except Exception:
        pass

    import threading
    def delay_power_action(cmd_func):
        def run():
            time.sleep(1.0)
            cmd_func()
        threading.Thread(target=run, daemon=True).start()

    if "shutdown" in action:
        def do_shutdown():
            cmd = r"C:\Windows\System32\shutdown.exe /s /t 0" if os.path.exists(r"C:\Windows\System32\shutdown.exe") else "shutdown /s /t 0"
            os.system(cmd)
        delay_power_action(do_shutdown)
        return "Shutting down the laptop now, Sir."
        
    elif "restart" in action:
        def do_restart():
            cmd = r"C:\Windows\System32\shutdown.exe /r /t 0" if os.path.exists(r"C:\Windows\System32\shutdown.exe") else "shutdown /r /t 0"
            os.system(cmd)
        delay_power_action(do_restart)
        return "Restarting the laptop now, Sir."
        
    elif "signout" in action or "logoff" in action or "sign out" in action:
        def do_signout():
            cmd = r"C:\Windows\System32\shutdown.exe /l" if os.path.exists(r"C:\Windows\System32\shutdown.exe") else "shutdown /l"
            os.system(cmd)
        delay_power_action(do_signout)
        return "Signing out from Windows session now, Sir."
        
    elif "sleep" in action:
        def do_sleep():
            # Method 1: ctypes PowrProf direct call (S3 Sleep)
            try:
                import ctypes
                res = ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
                if res != 0:
                    return
            except Exception:
                pass
            # Method 2: PowerShell SetSuspendState (Standard fallback)
            try:
                ps_cmd = "Add-Type -Assembly System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Suspend, $false, $false)"
                subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
            except Exception:
                pass
            # Method 3: Lock Workstation + Turn Off Monitor (Modern Standby S0 Sleep Fallback)
            try:
                import ctypes
                ctypes.windll.user32.LockWorkStation()
                time.sleep(0.5)
                # 0x0112 = WM_SYSCOMMAND, 0xF170 = SC_MONITORPOWER, 2 = Monitor Power Off
                ctypes.windll.user32.SendMessageW(-1, 0x0112, 0xF170, 2)
                return
            except Exception:
                pass
            # Method 4: Rundll32 PowrProf
            try:
                cmd = r"C:\Windows\System32\rundll32.exe powrprof.dll,SetSuspendState 0,1,0" if os.path.exists(r"C:\Windows\System32\rundll32.exe") else "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
                os.system(cmd)
            except Exception:
                pass
        
        delay_power_action(do_sleep)
        return "Putting the laptop to sleep now, Sir."
        
    return f"Invalid power action requested: {action}"


def get_active_window_context() -> dict:
    """
    Finds the active foreground window process name and title on Windows using PowerShell pinvoke.
    """
    ps_script = """
    $code = @'
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    '@
    $type = Add-Type -MemberDefinition $code -Name "Win32Utils" -Namespace "Win32" -PassThru
    $hwnd = $type::GetForegroundWindow()
    $title = New-Object System.Text.StringBuilder 256
    $type::GetWindowText($hwnd, $title, 256)
    $processId = 0
    $type::GetWindowThreadProcessId($hwnd, [ref]$processId)
    if ($processId -gt 0) {
        $process = Get-Process -Id $processId
        $res = @{
            ProcessName = $process.ProcessName
            Title = $title.ToString()
        }
        $res | ConvertTo-Json
    } else {
        '{"ProcessName": "unknown", "Title": "unknown"}'
    }
    """
    try:
        res = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, timeout=5)
        out = res.stdout.strip()
        if out:
            data = json.loads(out)
            return {
                "process_name": data.get("ProcessName", "unknown"),
                "window_title": data.get("Title", "unknown")
            }
    except Exception as e:
        print(f"Error getting active window context: {e}")
    return {"process_name": "unknown", "window_title": "unknown"}


def _load_calendar() -> list:
    if os.path.exists(CALENDAR_FILE):
        try:
            with open(CALENDAR_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save_calendar(data: list):
    try:
        with open(CALENDAR_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to save calendar: {e}")


def add_calendar_event(title: str, start_time: str, end_time: str = "", description: str = "") -> str:
    """
    Creates a new event and returns status. start_time and end_time should be ISO formats (e.g. YYYY-MM-DD HH:MM).
    """
    events = _load_calendar()
    event_id = str(int(time.time() * 1000))
    event = {
        "id": event_id,
        "title": title,
        "start_time": start_time,
        "end_time": end_time or start_time,
        "description": description,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    events.append(event)
    _save_calendar(events)
    return f"Successfully added event '{title}' scheduled for {start_time}."


def list_calendar_events(query_date: str = "") -> str:
    """
    Lists upcoming events. If query_date is provided (YYYY-MM-DD), lists events on that day.
    """
    events = _load_calendar()
    if not events:
        return "You have no calendar events, Sir."
    
    events.sort(key=lambda x: x.get("start_time", ""))
    
    matching_events = []
    for ev in events:
        if query_date:
            if query_date in ev.get("start_time", ""):
                matching_events.append(ev)
        else:
            try:
                ev_time_str = ev.get("start_time", "")
                if len(ev_time_str) == 10:
                    ev_time = datetime.strptime(ev_time_str, "%Y-%m-%d")
                else:
                    ev_time = datetime.strptime(ev_time_str[:16], "%Y-%m-%d %H:%M")
                
                if ev_time.date() >= datetime.today().date():
                    matching_events.append(ev)
            except Exception:
                matching_events.append(ev)
                
    if not matching_events:
        return f"No events found for {query_date}, Sir." if query_date else "No upcoming events found, Sir."
        
    res = []
    for i, ev in enumerate(matching_events[:10], 1):
        end_str = f" to {ev['end_time']}" if ev.get("end_time") and ev["end_time"] != ev["start_time"] else ""
        desc_str = f" ({ev['description']})" if ev.get("description") else ""
        res.append(f"{i}. '{ev['title']}' on {ev['start_time']}{end_str}{desc_str} [ID: {ev['id']}]")
        
    return "\n".join(res)


def modify_calendar_event(event_id: str, action: str, new_value: str = "") -> str:
    """
    Modifies or deletes a calendar event. action can be 'delete' or 'update_title', 'update_time', 'update_desc'.
    """
    events = _load_calendar()
    action = action.lower().strip()
    
    found_idx = -1
    for i, ev in enumerate(events):
        if ev.get("id") == event_id or ev.get("title").lower() == event_id.lower():
            found_idx = i
            break
            
    if found_idx == -1:
        return f"Could not find any event matching ID or title '{event_id}'."
        
    event = events[found_idx]
    if action == "delete":
        removed = events.pop(found_idx)
        _save_calendar(events)
        return f"Successfully deleted event '{removed['title']}'."
        
    elif action == "update_title":
        event["title"] = new_value
    elif action == "update_time":
        event["start_time"] = new_value
        event["end_time"] = new_value
    elif action == "update_desc":
        event["description"] = new_value
    else:
        return f"Unknown calendar modification action: {action}"
        
    _save_calendar(events)
    return f"Successfully updated event '{event['title']}'."


def _get_email_credentials():
    return {
        "email": os.getenv("JARVIS_EMAIL", ""),
        "password": os.getenv("JARVIS_EMAIL_PASSWORD", ""),
        "imap_server": os.getenv("JARVIS_IMAP_SERVER", "imap.gmail.com"),
        "imap_port": int(os.getenv("JARVIS_IMAP_PORT", "993")),
        "smtp_server": os.getenv("JARVIS_SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("JARVIS_SMTP_PORT", "587")),
    }


def check_emails() -> str:
    """
    Checks the IMAP server for unread emails and returns prioritized list.
    """
    creds = _get_email_credentials()
    if not creds["email"] or not creds["password"]:
        return "Email integration is not configured, Sir. Please set your credentials in Settings."
        
    try:
        mail = imaplib.IMAP4_SSL(creds["imap_server"], creds["imap_port"])
        mail.login(creds["email"], creds["password"])
        mail.select("inbox")
        
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            return "Failed to search inbox for unseen messages."
            
        mail_ids = messages[0].split()
        if not mail_ids:
            return "You have no unread emails in your inbox, Sir."
            
        unread_emails = []
        for mail_id in reversed(mail_ids[-5:]):
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            if status != "OK":
                continue
                
            for response_part in msg_data:
                if isinstance(response_part, tuple):
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
        
        res = []
        for mail_item in unread_emails:
            res.append(f"[{mail_item['priority']} Priority] From: {mail_item['from']} - Subject: {mail_item['subject']} (ID: {mail_item['id']})")
        return "Here are your latest unread emails, Sir:\n" + "\n".join(res)
    except Exception as e:
        return f"Failed to check emails. Error: {str(e)}"


def read_email_content(email_id: str) -> str:
    """
    Fetches the plain text body of an email by ID to read aloud.
    """
    creds = _get_email_credentials()
    if not creds["email"] or not creds["password"]:
        return "Email integration is not configured, Sir."
        
    try:
        mail = imaplib.IMAP4_SSL(creds["imap_server"], creds["imap_port"])
        mail.login(creds["email"], creds["password"])
        mail.select("inbox")
        
        status, data = mail.fetch(email_id.encode(), "(RFC822)")
        if status != "OK":
            mail.logout()
            return f"Failed to fetch email with ID {email_id}."
            
        import email
        msg = email.message_from_bytes(data[0][1])
        
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8", errors="ignore")
            
        from_sender, encoding = decode_header(msg["From"])[0]
        if isinstance(from_sender, bytes):
            from_sender = from_sender.decode(encoding or "utf-8", errors="ignore")
            
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disp = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disp:
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")
            
        mail.logout()
        
        body_clean = body.strip().replace("\r", "")
        if len(body_clean) > 300:
            body_clean = body_clean[:300] + "... [truncated]"
            
        return f"Email from {from_sender}. Subject: {subject}. Content: {body_clean}"
    except Exception as e:
        return f"Failed to read email content. Error: {str(e)}"


def send_email(to_email: str, subject: str, body: str) -> str:
    """
    Sends an email reply or draft via SMTP.
    """
    creds = _get_email_credentials()
    if not creds["email"] or not creds["password"]:
        return "Email SMTP integration is not configured, Sir."
        
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = creds["email"]
        msg["To"] = to_email
        
        if creds["smtp_port"] == 465:
            server = smtplib.SMTP_SSL(creds["smtp_server"], creds["smtp_port"])
        else:
            server = smtplib.SMTP(creds["smtp_server"], creds["smtp_port"])
            server.starttls()
            
        server.login(creds["email"], creds["password"])
        server.sendmail(creds["email"], [to_email], msg.as_string())
        server.quit()
        return f"Email successfully sent to {to_email} with subject '{subject}'."
    except Exception as e:
        return f"Failed to send email. Error: {str(e)}"


def organize_directory(directory_path: str) -> str:
    """
    Automatically groups files inside directory_path into folders based on file extensions.
    """
    dir_path = directory_path.strip()
    if dir_path.lower() == "desktop":
        dir_path = os.path.join(os.path.expanduser("~"), "Desktop")
    elif dir_path.lower() == "downloads":
        dir_path = os.path.join(os.path.expanduser("~"), "Downloads")
    elif dir_path.lower() == "documents":
        dir_path = os.path.join(os.path.expanduser("~"), "Documents")
        
    if not os.path.exists(dir_path):
        return f"Target directory '{dir_path}' does not exist, Sir."
        
    categories = {
        "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".ppt", ".csv", ".rtf", ".odt"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico", ".webp"],
        "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
        "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
        "Archives": [".zip", ".rar", ".tar", ".gz", ".7z", ".iso"],
        "Code": [".py", ".js", ".html", ".css", ".json", ".cpp", ".c", ".h", ".cs", ".java", ".sh", ".bat", ".ps1"]
    }
    
    moved_counts = {}
    for cat in categories:
        moved_counts[cat] = 0
        
    try:
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        for file in files:
            name, ext = os.path.splitext(file)
            ext = ext.lower()
            
            target_cat = None
            for cat, extensions in categories.items():
                if ext in extensions:
                    target_cat = cat
                    break
                    
            if target_cat:
                cat_dir = os.path.join(dir_path, target_cat)
                if not os.path.exists(cat_dir):
                    os.makedirs(cat_dir)
                    
                src_file = os.path.join(dir_path, file)
                dest_file = os.path.join(cat_dir, file)
                
                counter = 1
                while os.path.exists(dest_file):
                    dest_file = os.path.join(cat_dir, f"{name}_{counter}{ext}")
                    counter += 1
                    
                shutil.move(src_file, dest_file)
                moved_counts[target_cat] += 1
                
        summary = [f"{count} in {cat}" for cat, count in moved_counts.items() if count > 0]
        if not summary:
            return f"Directory '{dir_path}' is already organized, Sir."
        return f"Directory organized successfully. Moved: " + ", ".join(summary)
    except Exception as e:
        return f"Failed to organize directory. Error: {str(e)}"


def search_files(search_query: str, root_path: str = "") -> str:
    """
    Recursively searches files in root_path (defaults to User's Documents) for search_query.
    """
    if not root_path:
        root_path = os.path.join(os.path.expanduser("~"), "Documents")
    elif root_path.lower() == "desktop":
        root_path = os.path.join(os.path.expanduser("~"), "Desktop")
    elif root_path.lower() == "downloads":
        root_path = os.path.join(os.path.expanduser("~"), "Downloads")
        
    if not os.path.exists(root_path):
        return f"Search path '{root_path}' does not exist, Sir."
        
    query = search_query.lower().strip()
    matches = []
    
    try:
        for root, dirs, files in os.walk(root_path):
            if len(matches) >= 15:
                break
            for file in files:
                if query in file.lower():
                    matches.append(os.path.join(root, file))
                    if len(matches) >= 15:
                        break
                        
        if not matches:
            return f"No files found matching '{search_query}' in '{root_path}'."
            
        res = [f"Found {len(matches)} matching files (showing up to 15):"]
        for match in matches:
            res.append(f"- {os.path.basename(match)} at {match}")
        return "\n".join(res)
    except Exception as e:
        return f"File search failed. Error: {str(e)}"


def manage_file_operation(action: str, source_path: str, target_path: str = "") -> str:
    """
    Performs file operations: create_folder, create_file, move, delete, rename.
    """
    action = action.lower().strip()
    
    def resolve_paths(p):
        p_strip = p.strip()
        if p_strip.lower().startswith("documents"):
            return p_strip.replace("documents", os.path.join(os.path.expanduser("~"), "Documents"), 1)
        if p_strip.lower().startswith("desktop"):
            return p_strip.replace("desktop", os.path.join(os.path.expanduser("~"), "Desktop"), 1)
        if p_strip.lower().startswith("downloads"):
            return p_strip.replace("downloads", os.path.join(os.path.expanduser("~"), "Downloads"), 1)
        return p_strip
        
    source = resolve_paths(source_path)
    target = resolve_paths(target_path) if target_path else ""
    
    try:
        if action == "create_folder":
            os.makedirs(source, exist_ok=True)
            return f"Folder successfully created at: {source}"
            
        elif action == "create_file":
            os.makedirs(os.path.dirname(source), exist_ok=True)
            with open(source, "w", encoding="utf-8") as f:
                f.write("")
            return f"File successfully created at: {source}"
            
        elif action == "move":
            if not os.path.exists(source):
                return f"Source '{source}' does not exist."
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.move(source, target)
            return f"Successfully moved '{os.path.basename(source)}' to '{target}'"
            
        elif action == "delete":
            if not os.path.exists(source):
                return f"Path '{source}' does not exist."
            if os.path.isdir(source):
                shutil.rmtree(source)
            else:
                os.remove(source)
            return f"Successfully deleted: {source}"
            
        elif action == "rename":
            if not os.path.exists(source):
                return f"Source '{source}' does not exist."
            os.rename(source, target)
            return f"Successfully renamed '{os.path.basename(source)}' to '{os.path.basename(target)}'"
            
        else:
            return f"Invalid file management action: {action}"
    except Exception as e:
        return f"File operation failed. Error: {str(e)}"


def run_disk_cleanup(clean_temp: bool = True, clean_cache: bool = True) -> str:
    """
    Cleans Windows temporary files and browser cache directories where safe.
    """
    cleaned_dirs = []
    errors = []
    freed_bytes = 0
    
    paths_to_clean = []
    if clean_temp:
        temp_env = os.environ.get("TEMP")
        if temp_env and os.path.exists(temp_env):
            paths_to_clean.append(temp_env)
        win_temp = "C:\\Windows\\Temp"
        if os.path.exists(win_temp):
            paths_to_clean.append(win_temp)
            
    for temp_dir in paths_to_clean:
        try:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    fp = os.path.join(root, file)
                    try:
                        freed_bytes += os.path.getsize(fp)
                        os.remove(fp)
                    except Exception:
                        pass
                for d in dirs:
                    dp = os.path.join(root, d)
                    try:
                        shutil.rmtree(dp)
                    except Exception:
                        pass
            cleaned_dirs.append(temp_dir)
        except Exception as e:
            errors.append(str(e))
            
    freed_mb = round(freed_bytes / (1024 * 1024), 2)
    res = f"Disk cleanup complete, Sir. Freed {freed_mb} MB of space in temporary directories."
    if errors:
        res += " Note: some locked temporary files could not be cleared as they are currently in use."
    return res


def check_system_updates() -> str:
    """
    Checks for available software updates via Windows winget.
    """
    try:
        result = subprocess.run(["winget", "list", "--upgradeable"], capture_output=True, text=True, timeout=15)
        output = result.stdout.strip()
        
        lines = output.split("\n")
        upgrades = []
        for line in lines:
            if "winget" in line or "Name" in line or "ID" in line or "----" in line or not line.strip():
                continue
            parts = [p.strip() for p in line.split("  ") if p.strip()]
            if parts and len(parts) >= 3:
                upgrades.append(f"- {parts[0]} (Current: {parts[1]} -> Latest: {parts[2]})")
                
        if not upgrades:
            return "All software applications are up to date, Sir."
            
        res = ["The following software upgrades are available, Sir:"] + upgrades[:8]
        if len(upgrades) > 8:
            res.append(f"... and {len(upgrades) - 8} more applications can be updated.")
        return "\n".join(res)
    except Exception:
        return "Failed to run winget upgrade check. Please make sure winget is installed and available in the system PATH."


def _load_workflows() -> dict:
    if os.path.exists(WORKFLOWS_FILE):
        try:
            with open(WORKFLOWS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_workflows(data: dict):
    try:
        with open(WORKFLOWS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to save workflows: {e}")


def manage_workflow(action: str, name: str, steps: list = None) -> str:
    """
    Manages user workflows (macros). actions: 'create', 'delete', 'list'.
    """
    action = action.lower().strip()
    workflows = _load_workflows()
    
    if action == "create":
        if not name:
            return "Workflow name cannot be empty."
        if not steps:
            return "Workflow steps list cannot be empty."
        workflows[name] = steps
        _save_workflows(workflows)
        return f"Workflow '{name}' created successfully with {len(steps)} steps."
        
    elif action == "delete":
        if name in workflows:
            workflows.pop(name)
            _save_workflows(workflows)
            return f"Workflow '{name}' has been deleted."
        return f"Workflow '{name}' not found."
        
    elif action == "list":
        if not workflows:
            return "You have no custom workflows configured, Sir."
        res = ["Here are your custom workflows, Sir:"]
        for wf_name, wf_steps in workflows.items():
            res.append(f"- '{wf_name}' ({len(wf_steps)} steps)")
        return "\n".join(res)
        
    return f"Invalid workflow action: {action}"


def run_workflow(name: str) -> str:
    """
    Executes a saved workflow of steps.
    """
    workflows = _load_workflows()
    if name not in workflows:
        return f"Workflow '{name}' not found, Sir."
        
    steps = workflows[name]
    results = []
    
    for step in steps:
        step = step.strip()
        results.append(f"Executing: '{step}'")
        
        step_lower = step.lower()
        if step_lower.startswith("open website "):
            url = step[13:].strip()
            open_website(url)
        elif step_lower.startswith("open app ") or step_lower.startswith("open "):
            app = step_lower.replace("open app ", "").replace("open ", "").strip()
            open_app(app)
        elif step_lower.startswith("close app ") or step_lower.startswith("close "):
            app = step_lower.replace("close app ", "").replace("close ", "").strip()
            close_app(app)
        elif step_lower.startswith("volume "):
            vol_arg = step_lower.replace("volume ", "").strip()
            if vol_arg.isdigit():
                volume_control("set", int(vol_arg))
            else:
                volume_control(vol_arg)
        elif step_lower == "screenshot":
            take_screenshot()
        elif step_lower.startswith("write note "):
            content = step[11:].strip()
            write_note(content)
        elif step_lower.startswith("shell "):
            cmd = step[6:].strip()
            execute_shell_command(cmd)
        else:
            try:
                subprocess.Popen(step, shell=True)
            except Exception as e:
                results.append(f"Failed to execute step: {step}. Error: {str(e)}")
                
        time.sleep(1.0)
        
    return f"Workflow '{name}' completed successfully.\nSteps executed:\n" + "\n".join(results)


def offline_command_router(prompt: str) -> dict:
    """
    A basic regex rule-based engine to execute tools and return verbal voice responses offline.
    """
    prompt_clean = prompt.lower().strip()
    
    m = re.match(r"(?:open|launch)\s+([a-zA-Z0-9\s\.\-_]+)$", prompt_clean)
    if m:
        app_name = m.group(1).strip()
        res = open_app(app_name)
        return {
            "text_response": f"Opening {app_name} offline, Sir.",
            "result": res
        }
        
    m = re.match(r"(?:close|terminate|exit)\s+([a-zA-Z0-9\s\.\-_]+)$", prompt_clean)
    if m:
        app_name = m.group(1).strip()
        res = close_app(app_name)
        return {
            "text_response": f"Closing {app_name} offline, Sir.",
            "result": res
        }
        
    m = re.match(r"(?:open|go to|browse)\s+(?:website\s+)?([a-zA-Z0-9\.\-_/]+)$", prompt_clean)
    if m:
        site = m.group(1).strip()
        res = open_website(site)
        return {
            "text_response": f"Browsing to {site} offline, Sir.",
            "result": res
        }
        
    m = re.match(r"volume\s+(set\s+(\d+)|up|down|mute|unmute)$", prompt_clean)
    if m:
        arg = m.group(1)
        if "set" in arg:
            val = int(m.group(2))
            res = volume_control("set", val)
            return {"text_response": f"Volume adjusted to {val} percent, Sir.", "result": res}
        else:
            res = volume_control(arg)
            return {"text_response": f"Adjusted volume to {arg}, Sir.", "result": res}
            
    if "screenshot" in prompt_clean or "capture screen" in prompt_clean:
        res = take_screenshot()
        return {
            "text_response": "Taking screenshot offline, Sir.",
            "result": res
        }
        
    # Match IoT commands: e.g. "turn on bedroom light", "turn off study lamp", "set bedroom light to 50%"
    m = re.match(r"(?:turn|switch)\s+(on|off)\s+(bedroom\s+light|study\s+lamp|living\s+room\s+ac|smart\s+power\s+outlet|smart\s+plug)", prompt_clean)
    if m:
        action = m.group(1).upper()
        device_raw = m.group(2)
        device_id = "bedroom_light"
        if "study" in device_raw:
            device_id = "study_lamp"
        elif "living" in device_raw or "ac" in device_raw:
            device_id = "living_ac"
        elif "plug" in device_raw or "outlet" in device_raw:
            device_id = "smart_plug"
        
        control_iot_device(device_id, action)
        return {
            "text_response": f"Turning {action} the {device_raw} offline, Sir.",
            "result": f"Device {device_id} set to {action}"
        }

    m = re.match(r"(?:set|dim)\s+(bedroom\s+light|study\s+lamp|living\s+room\s+ac)\s+(?:to\s+)?(\d+)(%|°c|degrees)?", prompt_clean)
    if m:
        device_raw = m.group(1)
        val = m.group(2)
        unit = m.group(3) or ""
        device_id = "bedroom_light"
        if "study" in device_raw:
            device_id = "study_lamp"
            if not unit: unit = "%"
        elif "living" in device_raw or "ac" in device_raw:
            device_id = "living_ac"
            if not unit: unit = "°C"
            elif "degree" in unit: unit = "°C"
        
        control_iot_device(device_id, "ON", f"{val}{unit}")
        return {
            "text_response": f"Setting {device_raw} to {val} {unit} offline, Sir.",
            "result": f"Device {device_id} updated value to {val}{unit}"
        }
        
    # Wi-Fi control offline
    m = re.match(r"(?:turn|switch)\s+(on|off)\s+(?:wifi|wi-fi)$|^(?:wifi|wi-fi)\s+(on|off)$|^(?:enable|disable)\s+(?:wifi|wi-fi)$", prompt_clean)
    if m:
        state_grp = next((g for g in m.groups() if g), "")
        state = "ON" if state_grp.lower() in ["on", "enable"] else "OFF"
        res = set_wifi_state(state)
        return {"text_response": f"Adjusting Wi-Fi adapter state offline, Sir. {res}", "result": res}
        
    # Bluetooth control offline
    m = re.match(r"(?:turn|switch)\s+(on|off)\s+bluetooth$|^bluetooth\s+(on|off)$|^(?:enable|disable)\s+bluetooth$", prompt_clean)
    if m:
        state_grp = next((g for g in m.groups() if g), "")
        state = "ON" if state_grp.lower() in ["on", "enable"] else "OFF"
        res = set_bluetooth_state(state)
        return {"text_response": f"Adjusting Bluetooth radio state offline, Sir. {res}", "result": res}

    # Airplane mode offline
    m = re.match(r"(?:turn|switch)\s+(on|off)\s+(?:airplane|aeroplane)\s+mode$|^(?:airplane|aeroplane)\s+mode\s+(on|off)$|^(?:enable|disable)\s+(?:airplane|aeroplane)\s+mode$", prompt_clean)
    if m:
        state_grp = next((g for g in m.groups() if g), "")
        state = "ON" if state_grp.lower() in ["on", "enable"] else "OFF"
        res = set_airplane_mode_state(state)
        return {"text_response": f"Modifying Airplane mode state offline, Sir. {res}", "result": res}

    # Energy saver offline
    m = re.match(r"(?:turn|switch)\s+(on|off)\s+(?:energy|battery)\s+saver$|^(?:energy|battery)\s+saver\s+(on|off)$|^(?:enable|disable)\s+(?:energy|battery)\s+saver$", prompt_clean)
    if m:
        state_grp = next((g for g in m.groups() if g), "")
        state = "ON" if state_grp.lower() in ["on", "enable"] else "OFF"
        res = set_energy_saver_state(state)
        return {"text_response": f"Adjusting Energy Saver threshold offline, Sir. {res}", "result": res}

    # Night Light offline
    m = re.match(r"(?:turn|switch)\s+(on|off)\s+(?:nightlight|night\s+light)$|^(?:nightlight|night\s+light)\s+(on|off)$|^(?:enable|disable)\s+(?:nightlight|night\s+light)$", prompt_clean)
    if m:
        state_grp = next((g for g in m.groups() if g), "")
        state = "ON" if state_grp.lower() in ["on", "enable"] else "OFF"
        res = set_nightlight_state(state)
        return {"text_response": f"Activating Night Light offline, Sir. {res}", "result": res}

    # Active Window state control offline
    m = re.match(r"(?:minimize|maximize)\s+(?:the\s+)?(?:active\s+)?window$", prompt_clean)
    if m:
        action = "minimize" if "minimize" in prompt_clean else "maximize"
        res = set_active_window_state(action)
        return {"text_response": f"Processing window command offline, Sir. {res}", "result": res}

    # Screen Brightness Control offline
    m = re.match(r"(?:set\s+)?brightness\s+(?:to\s+)?(?:(high|low|medium)|(\d+)(%|percent)?)$", prompt_clean)
    if m:
        named_val = m.group(1)
        num_val = m.group(2)
        
        level = 50
        if named_val:
            if named_val == "high": level = 100
            elif named_val == "low": level = 15
            elif named_val == "medium": level = 50
        elif num_val:
            level = int(num_val)
            
        res = set_screen_brightness(level)
        return {"text_response": f"Setting monitor brightness offline, Sir. {res}", "result": res}

        res = set_keyboard_backlight(state)
        return {"text_response": f"Adjusting keyboard backlit state offline, Sir. {res}", "result": res}

        res = switch_window_tab(target)
        return {"text_response": f"Simulating key commands to switch {target} offline, Sir. {res}", "result": res}

    # Media controls offline
    m = re.match(r"^(?:play|pause|stop|mute|unmute|next|prev|previous)\s+(?:music|song|track|audio|media)$|^(?:play|pause|stop|mute|next|prev)$", prompt_clean)
    if m:
        action = prompt_clean.split()[0]
        res = control_media(action)
        return {"text_response": f"Executing media command offline, Sir. {res}", "result": res}
        
    # Plan my day offline
    if "plan my day" in prompt_clean or "daily schedule" in prompt_clean or "today's events" in prompt_clean:
        res = plan_my_day()
        return {"text_response": f"Generating daily timeline offline, Sir. {res}", "result": res}
        
    # Research offline
    m = re.match(r"^(?:research|search|google|duckduckgo)\s+(?:for\s+)?(.+)$", prompt_clean)
    if m:
        query = m.group(1).strip()
        res = research_topic(query)
        return {"text_response": f"Searching and summarizing offline, Sir. {res}", "result": res}

    m = re.match(r"(?:write|take|save)\s+(?:a\s+)?note\s+(?:saying|content)?\s*(.+)$", prompt_clean)
    if m:
        note = m.group(1).strip()
        res = write_note(note)
        return {
            "text_response": "Note logged successfully offline, Sir.",
            "result": res
        }
        
    if "system status" in prompt_clean or "performance" in prompt_clean or "stats" in prompt_clean:
        stats = get_system_stats()
        text = f"Offline metrics status, Sir. CPU usage is {stats['cpu_usage']}%, memory load is {stats['ram_usage']}%, and battery capacity is {stats['battery_percent']}%."
        return {
            "text_response": text,
            "result": str(stats)
        }
        
    if "shutdown" in prompt_clean:
        return {
            "text_response": "I am preparing to shut down the system, Sir.",
            "tool_call": {
                "name": "system_power_control",
                "args": {"action": "shutdown"}
            }
        }
    if "restart" in prompt_clean:
        return {
            "text_response": "I am preparing to restart the system, Sir.",
            "tool_call": {
                "name": "system_power_control",
                "args": {"action": "restart"}
            }
        }
    if "sleep" in prompt_clean:
        return {
            "text_response": "I am preparing to put the system to sleep, Sir.",
            "tool_call": {
                "name": "system_power_control",
                "args": {"action": "sleep"}
            }
        }
        
    return {
        "text_response": "Offline local mode is active, Sir. However, I am unable to parse that command offline. Please restore connectivity for full assistant logic.",
        "result": "Unparsed offline query."
    }

def get_weather_data(city_name: str = None):
    """
    Fetches the user's location based on manual city query or external IP (ip-api.com)
    and queries Open-Meteo API for real-time weather.
    If offline or an error occurs, falls back to a clean mock object.
    """
    import urllib.request
    import json
    import logging
    import urllib.parse

    lat, lon, city, region = None, None, None, None
    
    if city_name and city_name.strip():
        try:
            safe_city = urllib.parse.quote(city_name.strip())
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={safe_city}&count=1&language=en&format=json"
            req = urllib.request.Request(geo_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=4) as response:
                geo_data = json.loads(response.read().decode('utf-8'))
                
            results = geo_data.get("results", [])
            if results:
                lat = results[0].get("latitude")
                lon = results[0].get("longitude")
                city = results[0].get("name", city_name)
                region = results[0].get("admin1", results[0].get("country", ""))
        except Exception as e:
            logging.warning(f"Failed to geocode custom city '{city_name}': {e}")

    if lat is None or lon is None:
        try:
            # Step 1: Get location from ip-api
            req = urllib.request.Request(
                "http://ip-api.com/json/",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=3) as response:
                loc_data = json.loads(response.read().decode('utf-8'))
            
            if loc_data.get('status') == 'success':
                lat = loc_data.get('lat')
                lon = loc_data.get('lon')
                city = loc_data.get('city', 'Local Area')
                region = loc_data.get('regionName', '')
            else:
                lat, lon, city, region = 40.7128, -74.0060, "New York", "NY"
        except Exception as e:
            logging.warning(f"Failed to get IP-based location: {e}")
            lat, lon, city, region = 40.7128, -74.0060, "Local Area", "Offline"

    try:
        # Step 2: Get weather data from Open-Meteo
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,showers,snowfall,weather_code,cloud_cover,wind_speed_10m"
        req = urllib.request.Request(
            weather_url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            weather_data = json.loads(response.read().decode('utf-8'))
        
        current = weather_data.get('current', {})
        temp = current.get('temperature_2m', 20.0)
        humidity = current.get('relative_humidity_2m', 50)
        feels_like = current.get('apparent_temperature', temp)
        rain = current.get('rain', 0.0)
        snow = current.get('snowfall', 0.0)
        cloud = current.get('cloud_cover', 20)
        wind = current.get('wind_speed_10m', 10.0)
        code = current.get('weather_code', 0)
        
        condition = 'clear'
        if rain > 0.1 or code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            condition = 'rainy'
        elif snow > 0.1 or code in [71, 73, 75, 85, 86]:
            condition = 'snowy'
        elif cloud > 50 or code in [1, 2, 3, 45, 48]:
            condition = 'cloudy'
            
        return {
            "status": "success",
            "city": city,
            "region": region,
            "latitude": lat,
            "longitude": lon,
            "temperature": temp,
            "feels_like": feels_like,
            "humidity": humidity,
            "wind_speed": wind,
            "cloud_cover": cloud,
            "condition": condition,
            "source": "api"
        }
    except Exception as e:
        logging.warning(f"Failed to fetch weather from Open-Meteo: {e}")
        return {
            "status": "success",
            "city": city,
            "region": region,
            "latitude": lat,
            "longitude": lon,
            "temperature": 22.5,
            "feels_like": 23.0,
            "humidity": 45,
            "wind_speed": 12.0,
            "cloud_cover": 15,
            "condition": "clear",
            "source": "mock"
        }

def get_iot_devices():
    """
    Loads smart home device states from jarvis_iot.json.
    Creates default devices if the file does not exist.
    """
    import os
    import json
    import logging
    
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jarvis_iot.json')
    default_devices = [
        {"id": "bedroom_light", "name": "Bedroom Light", "type": "light", "state": "OFF", "value": "100%"},
        {"id": "study_lamp", "name": "Study Lamp", "type": "light", "state": "OFF", "value": "70%"},
        {"id": "living_ac", "name": "Living Room AC", "type": "thermostat", "state": "OFF", "value": "24°C"},
        {"id": "smart_plug", "name": "Smart Power Outlet", "type": "switch", "state": "OFF", "value": "0W"}
    ]
    
    if not os.path.exists(path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(default_devices, f, indent=4)
            return default_devices
        except Exception as e:
            logging.error(f"Failed to create jarvis_iot.json: {e}")
            return default_devices
            
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to read jarvis_iot.json: {e}")
        return default_devices

def control_iot_device(device_id, action, value=None):
    """
    Updates the state of a smart home device.
    """
    import os
    import json
    import logging

    devices = get_iot_devices()
    updated = False
    
    for device in devices:
        if device['id'] == device_id or device['name'].lower() == device_id.lower():
            if action.upper() in ["ON", "OFF"]:
                device['state'] = action.upper()
            if value is not None:
                device['value'] = value
            updated = True
            break
            
    if updated:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jarvis_iot.json')
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(devices, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to write jarvis_iot.json: {e}")
            
    return devices

def get_visual_flows():
    import os
    import json
    import logging
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jarvis_flows.json')
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to read jarvis_flows.json: {e}")
        return {}

def save_visual_flow(flow_name, nodes, links):
    import os
    import json
    import logging
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jarvis_flows.json')
    flows = get_visual_flows()
    flows[flow_name] = {
        "nodes": nodes,
        "links": links
    }
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(flows, f, indent=4)
        return True
    except Exception as e:
        logging.error(f"Failed to write jarvis_flows.json: {e}")
        return False

def delete_visual_flow(flow_name):
    import os
    import json
    import logging
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jarvis_flows.json')
    flows = get_visual_flows()
    if flow_name in flows:
        del flows[flow_name]
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(flows, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"Failed to write jarvis_flows.json: {e}")
            return False
    return False

def set_wifi_state(state: str) -> str:
    """
    Toggles the Wi-Fi adapter state ON or OFF using WinRT Radio API (no admin required).
    """
    import subprocess
    import base64
    cmd_state = "On" if state.upper() == "ON" else "Off"
    ps_cmd = f"""
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {{ 
        $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' 
    }})[0]

    function Await($WinRtTask, $ResultType) {{
        $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
        $netTask = $asTask.Invoke($null, @($WinRtTask))
        $netTask.Wait(-1) | Out-Null
        return $netTask.Result
    }}

    [Windows.Devices.Radios.Radio,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
    [Windows.Devices.Radios.RadioAccessStatus,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null

    $status = Await ([Windows.Devices.Radios.Radio]::RequestAccessAsync()) ([Windows.Devices.Radios.RadioAccessStatus])
    $radios = Await ([Windows.Devices.Radios.Radio]::GetRadiosAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Radios.Radio]])

    $wifi = $radios | Where-Object {{ $_.Kind -eq 'WiFi' }}
    if ($wifi) {{
        [Windows.Devices.Radios.RadioState,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
        Await ($wifi.SetStateAsync('{cmd_state}')) ([Windows.Devices.Radios.RadioAccessStatus]) | Out-Null
        write-output "Wi-Fi has been turned {cmd_state}."
    }} else {{
        write-output "No Wi-Fi radio device was found on this system."
    }}
    """
    encoded_cmd = base64.b64encode(ps_cmd.encode('utf-16le')).decode('utf-8')
    try:
        res = subprocess.run(f"powershell -EncodedCommand {encoded_cmd}", shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            return res.stdout.strip() or f"Wi-Fi set to {cmd_state} successfully."
        return f"Failed to toggle Wi-Fi: {res.stderr}"
    except Exception as e:
        return f"Error setting Wi-Fi state: {str(e)}"

def set_bluetooth_state(state: str) -> str:
    """
    Toggles the Bluetooth radio ON or OFF using WinRT Radio API (no admin required).
    """
    import subprocess
    import base64
    cmd_state = "On" if state.upper() == "ON" else "Off"
    ps_cmd = f"""
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {{ 
        $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' 
    }})[0]

    function Await($WinRtTask, $ResultType) {{
        $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
        $netTask = $asTask.Invoke($null, @($WinRtTask))
        $netTask.Wait(-1) | Out-Null
        return $netTask.Result
    }}

    [Windows.Devices.Radios.Radio,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
    [Windows.Devices.Radios.RadioAccessStatus,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null

    $status = Await ([Windows.Devices.Radios.Radio]::RequestAccessAsync()) ([Windows.Devices.Radios.RadioAccessStatus])
    $radios = Await ([Windows.Devices.Radios.Radio]::GetRadiosAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Radios.Radio]])

    $bluetooth = $radios | Where-Object {{ $_.Kind -eq 'Bluetooth' }}
    if ($bluetooth) {{
        [Windows.Devices.Radios.RadioState,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
        Await ($bluetooth.SetStateAsync('{cmd_state}')) ([Windows.Devices.Radios.RadioAccessStatus]) | Out-Null
        write-output "Bluetooth has been turned {cmd_state}."
    }} else {{
        write-output "No Bluetooth radio device was found on this system."
    }}
    """
    encoded_cmd = base64.b64encode(ps_cmd.encode('utf-16le')).decode('utf-8')
    try:
        res = subprocess.run(f"powershell -EncodedCommand {encoded_cmd}", shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            return res.stdout.strip() or f"Bluetooth set to {cmd_state} successfully."
        return f"Failed to toggle Bluetooth: {res.stderr}"
    except Exception as e:
        return f"Error setting Bluetooth state: {str(e)}"

def set_airplane_mode_state(state: str) -> str:
    """
    Toggles Airplane Mode by enabling/disabling all system radios (Wi-Fi and Bluetooth) using WinRT Radio API.
    """
    import subprocess
    import base64
    cmd_radio_state = "Off" if state.upper() == "ON" else "On"
    ps_cmd = f"""
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {{ 
        $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' 
    }})[0]

    function Await($WinRtTask, $ResultType) {{
        $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
        $netTask = $asTask.Invoke($null, @($WinRtTask))
        $netTask.Wait(-1) | Out-Null
        return $netTask.Result
    }}

    [Windows.Devices.Radios.Radio,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
    [Windows.Devices.Radios.RadioAccessStatus,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null

    $status = Await ([Windows.Devices.Radios.Radio]::RequestAccessAsync()) ([Windows.Devices.Radios.RadioAccessStatus])
    $radios = Await ([Windows.Devices.Radios.Radio]::GetRadiosAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Radios.Radio]])

    $updated = 0
    foreach ($radio in $radios) {{
        [Windows.Devices.Radios.RadioState,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
        Await ($radio.SetStateAsync('{cmd_radio_state}')) ([Windows.Devices.Radios.RadioAccessStatus]) | Out-Null
        $updated++
    }}
    write-output "Airplane mode set to {state.upper()}. Toggled $updated system radios."
    """
    encoded_cmd = base64.b64encode(ps_cmd.encode('utf-16le')).decode('utf-8')
    try:
        res = subprocess.run(f"powershell -EncodedCommand {encoded_cmd}", shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            return res.stdout.strip()
        return f"Failed to toggle Airplane Mode: {res.stderr}"
    except Exception as e:
        return f"Error toggling Airplane Mode: {str(e)}"

def set_energy_saver_state(state: str) -> str:
    """
    Toggles Energy/Battery Saver mode state ON or OFF using powercfg to set activation thresholds.
    """
    import subprocess
    threshold = 100 if state.upper() == "ON" else 0
    try:
        # Update both DC (on battery) and AC (plugged in) values
        subprocess.run(f"powercfg /setdcvalueindex SCHEME_CURRENT SUB_ENERGYSAVER ESBATTTHRESHOLD {threshold}", shell=True, capture_output=True)
        subprocess.run(f"powercfg /setacvalueindex SCHEME_CURRENT SUB_ENERGYSAVER ESBATTTHRESHOLD {threshold}", shell=True, capture_output=True)
        # Apply changes
        res = subprocess.run("powercfg /setactive scheme_current", shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            return f"Energy Saver mode has been turned {state.upper()} successfully."
        return f"Failed to apply Energy Saver settings: {res.stderr}"
    except Exception as e:
        return f"Error setting Energy Saver state: {str(e)}"

def set_nightlight_state(state: str) -> str:
    """
    Launches Windows Settings to the Night Light configurations page.
    """
    import subprocess
    try:
        # Launch settings page directly
        subprocess.Popen("start ms-settings:nightlight", shell=True)
        return f"I have opened the Night Light settings page, Sir, so you can adjust or toggle it to {state.upper()}."
    except Exception as e:
        return f"Error launching Night Light settings: {str(e)}"

def set_active_window_state(action: str) -> str:
    """
    Minimizes or maximizes the currently active window.
    """
    import ctypes
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    if not hwnd:
        return "No active window found to control."
        
    action_clean = action.lower().strip()
    if action_clean == "minimize":
        ctypes.windll.user32.ShowWindow(hwnd, 6)
        return "Active window minimized."
    elif action_clean == "maximize":
        ctypes.windll.user32.ShowWindow(hwnd, 3)
        return "Active window maximized."
    return f"Unknown window control action '{action}'."

def set_screen_brightness(level: int) -> str:
    """
    Sets the screen brightness level from 0 to 100.
    """
    import subprocess
    try:
        level_val = min(100, max(0, int(level)))
        cmd = f'powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level_val})"'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            return f"Screen brightness set to {level_val}%."
        err_msg = res.stderr or ""
        if "not found" in err_msg.lower() or "invalid class" in err_msg.lower() or "cannot find" in err_msg.lower() or "null-valued" in err_msg.lower() or "not supported" in err_msg.lower():
            return "Screen brightness adjustment is only supported on laptops or devices with built-in displays. Desktop monitor controls are not supported via WMI."
        return f"Failed to set brightness: {err_msg.strip()}"
    except Exception as e:
        return f"Error adjusting brightness: {str(e)}"

def set_keyboard_backlight(state: str) -> str:
    """
    Toggles keyboard backlight ON or OFF by querying common WMI vendor namespaces (Asus, Dell, HP, Lenovo).
    """
    import subprocess
    
    state_val = 1 if state.upper() == "ON" else 0
    asus_val = 4 if state.upper() == "ON" else 0
    
    commands = [
        f"powershell -Command \"Get-CimInstance -Namespace root/wmi -ClassName DellKeyboardBacklight | Invoke-CimMethod -MethodName SetState -Arguments @{{State={state_val}}}\"",
        f"powershell -Command \"(Get-CimInstance -Namespace root/wmi -ClassName AsusAtkWmi_Backlight).SetBacklight({asus_val})\"",
        f"powershell -Command \"Get-CimInstance -Namespace root/wmi -ClassName HP_KeyboardBacklight | Invoke-CimMethod -MethodName SetState -Arguments @{{State={state_val}}}\""
    ]
    
    for cmd in commands:
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                return f"Keyboard backlight successfully turned {state.upper()}."
        except Exception:
            pass
            
    return f"Unable to control keyboard backlight: Hardware vendor WMI controls are either not present or require custom proprietary drivers. Tried Dell, Asus, and HP WMI namespaces."


def switch_window_tab(target: str) -> str:
    """
    Switches tabs or active windows. target can be 'tab' (emulates Ctrl+Tab) or 'window' (emulates Alt+Tab).
    """
    import ctypes
    import time
    import logging

    target_clean = target.lower().strip()
    
    # Helper to send key down/up
    def key_event(vk, down=True):
        flags = 0 if down else 2  # KEYEVENTF_KEYUP is 2
        ctypes.windll.user32.keybd_event(vk, 0, flags, 0)
        
    try:
        if target_clean == "window":
            # Emulate Alt + Tab
            key_event(0x12, True)  # VK_MENU (Alt) down
            key_event(0x09, True)  # VK_TAB down
            time.sleep(0.05)
            key_event(0x09, False) # VK_TAB up
            key_event(0x12, False) # VK_MENU up
            return "Active application window switched."
        elif target_clean == "tab":
            # Emulate Ctrl + Tab
            key_event(0x11, True)  # VK_CONTROL (Ctrl) down
            key_event(0x09, True)  # VK_TAB down
            time.sleep(0.05)
            key_event(0x09, False) # VK_TAB up
            key_event(0x11, False) # VK_CONTROL up
            return "Active browser/application tab switched."
        else:
            return f"Unknown target '{target}' for window/tab switching."
    except Exception as e:
        logging.error(f"Error simulating key events: {e}")
        return f"Failed to switch {target_clean}. Error: {str(e)}"


def type_text(text: str) -> str:
    """
    Types text Unicode character-by-character into the active foreground application window.
    """
    import ctypes
    import time
    import logging
    
    user32 = ctypes.windll.user32
    
    # Input structure layouts for Windows API SendInput
    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", ctypes.c_ushort),
            ("wScan", ctypes.c_ushort),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", ctypes.c_void_p)
        ]
        
    class INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("ki", KEYBDINPUT)
        ]
        
    class INPUT(ctypes.Structure):
        _fields_ = [
            ("type", ctypes.c_ulong),
            ("u", INPUT_UNION)
        ]
        
    KEYEVENTF_UNICODE = 0x0004
    KEYEVENTF_KEYUP = 0x0002
    
    try:
        for char in text:
            # Key Down Event
            inp = INPUT()
            inp.type = 1  # INPUT_KEYBOARD = 1
            inp.u.ki.wVk = 0
            inp.u.ki.wScan = ord(char)
            inp.u.ki.dwFlags = KEYEVENTF_UNICODE
            user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
            
            # Key Up Event
            inp_up = INPUT()
            inp_up.type = 1
            inp_up.u.ki.wVk = 0
            inp_up.u.ki.wScan = ord(char)
            inp_up.u.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
            user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(INPUT))
            time.sleep(0.005)
            
        return f"Typed {len(text)} characters into the focused application."
    except Exception as e:
        logging.error(f"Error executing SendInput typing: {e}")
        return f"Failed to type text: {str(e)}"


def control_media(action: str) -> str:
    """
    Controls system media keys: play, pause, next, prev, volume_up, volume_down.
    """
    import ctypes
    import time
    
    action_clean = action.lower().strip()
    
    # Virtual Key codes
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    VK_MEDIA_STOP = 0xB2
    VK_MEDIA_PLAY_PAUSE = 0xB3
    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF
    
    vk = 0
    if action_clean in ["play", "pause", "play_pause"]:
        vk = VK_MEDIA_PLAY_PAUSE
    elif action_clean in ["next", "next_track"]:
        vk = VK_MEDIA_NEXT_TRACK
    elif action_clean in ["prev", "previous", "prev_track"]:
        vk = VK_MEDIA_PREV_TRACK
    elif action_clean in ["stop"]:
        vk = VK_MEDIA_STOP
    elif action_clean == "mute":
        vk = VK_VOLUME_MUTE
    elif action_clean == "volume_up":
        vk = VK_VOLUME_UP
    elif action_clean == "volume_down":
        vk = VK_VOLUME_DOWN
        
    if not vk:
        return f"Unknown media action '{action}'."
        
    try:
        ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(vk, 0, 2, 0) # KEYEVENTF_KEYUP = 2
        return f"Media command '{action_clean}' executed successfully."
    except Exception as e:
        return f"Failed to execute media command: {str(e)}"


def get_clipboard_text() -> str:
    """
    Reads text contents currently stored in the Windows Clipboard using ctypes.
    """
    import ctypes
    import logging
    
    CF_UNICODETEXT = 13
    
    if not ctypes.windll.user32.OpenClipboard(None):
        return ""
        
    try:
        h_clip_mem = ctypes.windll.user32.GetClipboardData(CF_UNICODETEXT)
        if not h_clip_mem:
            return ""
            
        p_clip_mem = ctypes.windll.kernel32.GlobalLock(h_clip_mem)
        if not p_clip_mem:
            return ""
            
        text = ctypes.c_wchar_p(p_clip_mem).value
        ctypes.windll.kernel32.GlobalUnlock(h_clip_mem)
        return text or ""
    except Exception as e:
        logging.error(f"Failed to read clipboard text: {e}")
        return ""
    finally:
        ctypes.windll.user32.CloseClipboard()


def research_topic(query: str) -> str:
    """
    Search DuckDuckGo HTML page and compile top article descriptions, then runs LLM summarizer.
    """
    import urllib.request
    import urllib.parse
    import re
    import logging
    import os
    
    try:
        safe_query = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={safe_query}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        if not snippets:
            snippets = re.findall(r'<div class="result__snippet"[^>]*>(.*?)</div>', html, re.DOTALL)
            
        cleaned_snippets = []
        for snip in snippets[:4]:
            clean = re.sub(r'<[^>]+>', '', snip)
            clean = clean.replace('&amp;', '&').replace('&quot;', '"').replace('&apos;', "'").strip()
            if clean:
                cleaned_snippets.append(clean)
                
        if not cleaned_snippets:
            return f"I performed a search for '{query}', but DuckDuckGo didn't return any readable snippets. Please check your network connection, Sir."
            
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Local search results:\n" + "\n".join([f"- {s}" for s in cleaned_snippets[:3]])
            
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = (
            f"You are JARVIS. Summarize these web search results for the user's query: '{query}' into a single, concise verbal explanation (around 45-60 words). "
            f"Be helpful, professional, and refer to the user as 'Sir'.\n\nSearch Results:\n" + "\n".join(cleaned_snippets)
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Search failed: {e}")
        return f"Apologies, Sir. The web search protocol failed. Error: {str(e)}"


def plan_my_day() -> str:
    """
    Analyzes local calendar events and compiles them into a structured daily plan/timeline.
    """
    import os
    import json
    import logging
    from datetime import datetime
    
    events = []
    cal_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jarvis_calendar.json')
    if os.path.exists(cal_path):
        try:
            with open(cal_path, 'r', encoding='utf-8') as f:
                events = json.load(f)
        except Exception as e:
            logging.error(f"Failed to read calendar in plan_my_day: {e}")
            
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_events = [e for e in events if e.get("start_time", "").startswith(today_str)]
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        if not today_events:
            return "You have a clear schedule today, Sir. No events on your calendar."
        summary = f"Schedule for today, {today_str}:\n"
        for ev in today_events:
            summary += f"- {ev.get('start_time')[11:]}: {ev.get('title')} ({ev.get('description', 'No details')})\n"
        return summary
        
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    events_raw = json.dumps(today_events)
    prompt = (
        f"You are JARVIS. Below is the list of events for today ({today_str}). "
        f"Create a structured daily schedule, including suggestions on when to take breaks or focus on tasks. "
        f"Refer to the user as 'Sir'. Make it highly professional and concise.\n\nEvents:\n{events_raw}"
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Failed to generate timeline. Today's events: {len(today_events)} scheduled."




