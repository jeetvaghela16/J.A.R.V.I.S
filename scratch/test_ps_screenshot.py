import subprocess
import os

def take_screenshot_ps(filepath):
    try:
        # Construct powershell command
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
        # Execute
        result = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
        if result.returncode == 0 and os.path.exists(filepath):
            print(f"Screenshot saved successfully at: {filepath}")
            return True
        else:
            print(f"PowerShell failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Test save to local scratch
take_screenshot_ps("scratch/test_screenshot.png")
