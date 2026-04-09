"""Generate app icon for CYC Meter Reader.
Produces meter-icon-1024.png (master) and apple-touch-icon.png (180x180) for iOS."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

SIZE = 1024
OUT_DIR = Path(__file__).parent


def vertical_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size, top)
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def load_font(candidates, size):
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_lightning(draw, cx, cy, scale, color):
    # Stylised lightning bolt polygon, centred on (cx, cy)
    pts = [
        (0.15, -1.00),
        (0.55, -1.00),
        (0.20, -0.15),
        (0.70, -0.15),
        (-0.25, 1.00),
        (0.05, 0.10),
        (-0.45, 0.10),
    ]
    poly = [(cx + x * scale, cy + y * scale) for x, y in pts]
    draw.polygon(poly, fill=color)


def make_icon():
    # Background gradient
    bg = vertical_gradient((SIZE, SIZE), (30, 58, 95), (10, 18, 32))
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    img.paste(bg)

    # Mask with rounded corners (iOS will mask too, but keeps raw PNG nice)
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, SIZE, SIZE), radius=220, fill=255)
    rounded = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    rounded.paste(img, mask=mask)
    img = rounded

    draw = ImageDraw.Draw(img)

    # Lightning bolts in upper corners
    gold = (255, 224, 102, 230)
    draw_lightning(draw, cx=170, cy=280, scale=140, color=gold)
    draw_lightning(draw, cx=SIZE - 170, cy=280, scale=140, color=gold)

    # LCD window
    lcd_rect = (110, 420, SIZE - 110, 720)
    # Inner gradient for LCD by drawing two stacked rounded rects
    lcd_bg = vertical_gradient((lcd_rect[2] - lcd_rect[0], lcd_rect[3] - lcd_rect[1]),
                               (10, 37, 64), (6, 24, 46)).convert("RGBA")
    lcd_mask = Image.new("L", (lcd_rect[2] - lcd_rect[0], lcd_rect[3] - lcd_rect[1]), 0)
    ImageDraw.Draw(lcd_mask).rounded_rectangle(
        (0, 0, lcd_rect[2] - lcd_rect[0], lcd_rect[3] - lcd_rect[1]),
        radius=34, fill=255,
    )
    img.paste(lcd_bg, (lcd_rect[0], lcd_rect[1]), lcd_mask)

    # LCD border
    draw.rounded_rectangle(lcd_rect, radius=34, outline=(79, 195, 247, 255), width=10)

    # Digital readout with glow
    digits = "1234567"
    font_lcd = load_font([
        "C:/Windows/Fonts/consolab.ttf",   # Consolas Bold
        "C:/Windows/Fonts/courbd.ttf",     # Courier New Bold
        "C:/Windows/Fonts/cour.ttf",
        "arial.ttf",
    ], 210)

    # Glow layer: draw digits large, blur, composite
    glow_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer)
    bbox = gdraw.textbbox((0, 0), digits, font=font_lcd)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (SIZE - tw) // 2 - bbox[0]
    ty = lcd_rect[1] + ((lcd_rect[3] - lcd_rect[1]) - th) // 2 - bbox[1]
    gdraw.text((tx, ty), digits, font=font_lcd, fill=(79, 195, 247, 255))
    glow = glow_layer.filter(ImageFilter.GaussianBlur(radius=14))
    img = Image.alpha_composite(img, glow)
    img = Image.alpha_composite(img, glow_layer)

    draw = ImageDraw.Draw(img)

    # kWh label
    font_label = load_font([
        "C:/Windows/Fonts/ariblk.ttf",     # Arial Black
        "C:/Windows/Fonts/arialbd.ttf",    # Arial Bold
        "arial.ttf",
    ], 130)
    label = "kWh"
    lb = draw.textbbox((0, 0), label, font=font_label)
    lw = lb[2] - lb[0]
    lx = (SIZE - lw) // 2 - lb[0]
    draw.text((lx, 770), label, font=font_label, fill=(255, 224, 102, 255))

    # CYC tag above LCD
    font_cyc = load_font([
        "C:/Windows/Fonts/ariblk.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "arial.ttf",
    ], 90)
    cyc = "CYC METER"
    cb = draw.textbbox((0, 0), cyc, font=font_cyc)
    cw = cb[2] - cb[0]
    cx = (SIZE - cw) // 2 - cb[0]
    draw.text((cx, 315), cyc, font=font_cyc, fill=(232, 228, 216, 255))

    return img


def main():
    icon = make_icon()

    master = OUT_DIR / "meter-icon-1024.png"
    icon.save(master, "PNG")
    print(f"wrote {master}")

    for name, size in [
        ("apple-touch-icon.png", 180),
        ("apple-touch-icon-152.png", 152),
        ("apple-touch-icon-120.png", 120),
        ("favicon-192.png", 192),
    ]:
        resized = icon.resize((size, size), Image.LANCZOS)
        out = OUT_DIR / name
        resized.save(out, "PNG")
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
