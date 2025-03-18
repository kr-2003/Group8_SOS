from pyvirtualdisplay import Display
from PIL import ImageGrab

def take_screenshot():
    # Start a virtual display
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    try:
        # Capture the screen
        screenshot = ImageGrab.grab()
        screenshot.save("screenshot.png")
        print("Screenshot saved as screenshot.png")
    finally:
        # Stop the virtual display
        display.stop()

if __name__ == "__main__":
    take_screenshot()
