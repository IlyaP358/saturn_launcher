from rich.console import Console
from PIL import Image
import sys
import os

console = Console()

def get_logo_lines():
    # Get the correct path for logo.png (works for both bundled and unbundled)
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    logo_path = os.path.join(base_path, "logo.png")
    img = Image.open(logo_path).resize((40, 20)).convert("RGBA")
    lines = []
    for y in range(img.height):
        line = ""
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))
            if a == 0:
                line += " "
            else:
                line += f"[rgb({r},{g},{b})]█[/rgb({r},{g},{b})]"
        lines.append(line)
    return lines

# For standalone execution
if __name__ == "__main__":
    logo_lines = get_logo_lines()
    for line in logo_lines:
        console.print(line)
