import subprocess

def type_text(text: str):
    try:
        # Escape double quotes and send
        escaped = text.replace('"', '`"')
        ps_cmd = f'[void][System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms"); [System.Windows.Forms.SendKeys]::SendWait("{escaped}")'
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

type_text("Hello from Jarvis!")
