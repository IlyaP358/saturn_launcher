from rich.console import Console
from PIL import Image

console = Console()

def get_logo_lines():
    img = Image.open("logo.png").resize((40, 20)).convert("RGBA")
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
