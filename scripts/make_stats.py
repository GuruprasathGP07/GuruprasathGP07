from PIL import Image, ImageOps, ImageFilter, ImageChops, ImageDraw
from html import escape

COLS, ADV, LH, FS = 100, 6, 12, 10          # 0.6em advance at 10px font
RAMP = " .:-=+*#%@"
SRC = "me.jpg"
CROP = (200, 110, 920, 910)                 # head + shoulders
FILL = "#c9d1d9"                             # light grey
STEP = 0.04                                  # seconds between rows in the draw-in animation
GAMMA = 0.8                                  # lower = brighter shadows (hair)
CUT = 28                                     # values below this become empty (clean background)

img = Image.open(SRC).convert("L").crop(CROP)
orig = img.copy()
W0, H0 = img.size

# darken the shirt gradually below the collar so the face stays the focus
grad = Image.linear_gradient("L").resize((W0, H0))                 # black (top) -> white (bottom)
shade = grad.point(lambda g: 255 if g < 150 else int(255 - (g - 150) * 0.55))
img = ImageChops.multiply(img, shade)
img = ImageOps.autocontrast(img, cutoff=0.5)
img = img.point(lambda v: int(255 * (v / 255) ** GAMMA))

# local contrast so eyes / nose / mouth / beard / hair texture stand out
blur = img.filter(ImageFilter.GaussianBlur(14))
detail = ImageChops.subtract(img, blur, scale=1, offset=128)
detail = detail.point(lambda v: max(0, min(255, int(128 + (v - 128) * 2.6))))
img = Image.blend(img, detail, 0.45)
img = ImageOps.autocontrast(img, cutoff=1)
img = img.point(lambda v: 0 if v < CUT else v)
img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120))

# remove the black backdrop: keep only the head/hair region and the body
keep = Image.new("L", (W0, H0), 0)
kd = ImageDraw.Draw(keep)
kd.ellipse((150, 15, 565, 560), fill=255)                          # head + hair
kd.polygon([(0, H0), (20, 620), (230, 520), (500, 520), (700, 620), (W0, H0)], fill=255)  # shoulders
bg = orig.point(lambda v: 255 if v < 26 else 0)                    # near-black pixels
drop = ImageChops.multiply(bg, ImageChops.invert(keep))
img = ImageChops.subtract(img, drop)

w, h = img.size
rows = int(COLS * h / w * (ADV / LH))
img = img.resize((COLS, rows), Image.LANCZOS)
px = img.load()
n = len(RAMP) - 1
grid = ["".join(RAMP[px[x, y] * n // 255] for x in range(COLS)) for y in range(rows)]

lines = []
for y, row in enumerate(grid):
    t = f"{0.3 + y*STEP:.2f}"
    lines.append(
        f'<text x="0" y="{(y+1)*LH}" textLength="{COLS*ADV}" lengthAdjust="spacing" '
        f'xml:space="preserve" opacity="0" fill="#ffffff">{escape(row)}'
        f'<animate attributeName="opacity" from="0" to="1" begin="{t}s" dur="0.12s" fill="freeze"/>'
        f'<animate attributeName="fill" from="#ffffff" to="{FILL}" begin="{t}s" dur="0.6s" fill="freeze"/>'
        f'</text>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{COLS*ADV}" height="{rows*LH}" '
       f'viewBox="0 0 {COLS*ADV} {rows*LH}"><g font-family="JetBrains Mono,ui-monospace,monospace" '
       f'font-size="{FS}">{"".join(lines)}</g></svg>')
open("ascii.svg", "w", encoding="utf-8").write(svg)
open("preview.txt", "w").write("\n".join(grid))
print(COLS*ADV, "x", rows*LH)
