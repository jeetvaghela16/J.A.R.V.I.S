import ctypes
from ctypes import wintypes

# Win32 GDI screenshot using ctypes
def take_screenshot_ctypes(filename="screenshot.png"):
    try:
        # Load user32 and gdi32
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        # Get screen metrics
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)

        # Get desktop DC
        hdesktop = user32.GetDesktopWindow()
        desktop_dc = user32.GetWindowDC(hdesktop)
        img_dc = gdi32.CreateCompatibleDC(desktop_dc)

        # Create compatible bitmap
        hbitmap = gdi32.CreateCompatibleBitmap(desktop_dc, width, height)
        gdi32.SelectObject(img_dc, hbitmap)

        # Copy screen to bitmap
        gdi32.BitBlt(img_dc, 0, 0, width, height, desktop_dc, 0, 0, 0x00CC0020) # SRCCOPY

        # We need to save the hbitmap to filename.
        # Since Pillow might fail to import, we can write a BMP file directly or use GDI+ to save as PNG!
        # GDI+ is built into Windows and can save to PNG. Let's see if we can do GDI+ or just save as BMP
        # Wait, if Pillow is installed, can we load the bitmap data into Pillow?
        # If Pillow itself is broken, then loading Pillow will fail. But let's check if Pillow can be imported.
        # If Pillow CAN be imported, we can convert bitmap to Image.
        # If Pillow cannot be imported, we can write a BMP file.
        # Let's check if we can import Pillow (PIL)
        try:
            from PIL import Image
            # Get bitmap bits
            bmpinfo = ctypes.c_char_array()
            # To get PIL Image from hbitmap:
            # We can use ImageGrab or use GDI bitmap bytes
            import io
            # We can write a simple BMP header and write the file
        except ImportError:
            pass

        print(f"Metrics: {width}x{height}")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False

take_screenshot_ctypes()
