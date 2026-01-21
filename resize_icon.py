from PIL import Image
import os

img = Image.open("logo.png")
img_resized = img.resize((512, 512), Image.Resampling.LANCZOS)
img_resized.save("logo_512.png")
print("Resized logo.png to logo_512.png")

img_cli = Image.open("logo_cli.png")
img_cli_resized = img_cli.resize((512, 512), Image.Resampling.LANCZOS)
img_cli_resized.save("logo_cli_512.png")
print("Resized logo_cli.png to logo_cli_512.png")
