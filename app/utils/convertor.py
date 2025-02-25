from pathlib import Path

from PIL import Image


def convert_to_png(input_path, output_png_path, size=(200, 200)) -> bool:
    if not Path(input_path).exists():
        return False
    image = Image.open(input_path)

    if image.mode != "RGB":
        image = image.convert("RGB")
    image.thumbnail(size)
    image.save(output_png_path, format='PNG')
    image.close()
    return True


if __name__ == "__main__":
    convert_to_png('Blue.tif', 'why.png', (1080, 1080))
