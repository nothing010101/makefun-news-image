#!/usr/bin/env python3
"""news-image-01 entry: one image summing up world news of Friday 13 November 2026.

Pure Python 3.13 stdlib (zlib, struct, math, os). No network, deterministic:
two runs write byte-identical output. Writes entry.png to $MAKEFUN_OUTPUT_DIR
or /output. Layout is a newspaper front page: masthead, one lead story
(Nvidia chief executive resigns), four more stories in a 2x2 grid
(Ukraine talks, Microsoft 365 outage, China Pacific drills, Gulf tanker),
plus a source footer. Every story was verified against real reporting
(Reuters/AP via The Raisina Post, Bangladesh Chronicle, Open Chronicle, KLZ).
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)   # warm newsprint
INK = (26, 26, 26)
NAVY = (20, 33, 61)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
LIGHT = (240, 234, 217)   # alternate panel tint
GREEN_NV = (118, 185, 0)  # Nvidia green
GREEN_DK = (84, 138, 0)
RED = (222, 41, 16)
BLUE_UK = (0, 87, 183)    # Ukraine blue
YELLOW_UK = (255, 215, 0) # Ukraine yellow
BLUE_MS = (0, 164, 239)   # Microsoft blue
SEA = (18, 92, 140)
TEAL = (14, 116, 120)
ORANGE = (230, 126, 34)
YELLOW_BOLT = (255, 191, 0)
GREY = (90, 90, 96)
DARKRED = (150, 40, 30)

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x0, x1, y, c):
        if y < 0 or y >= self.h:
            return
        x0, x1 = max(0, x0), min(self.w - 1, x1)
        for x in range(x0, x1 + 1):
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def vline(self, x, y0, y1, c):
        if x < 0 or x >= self.w:
            return
        for y in range(max(0, y0), min(self.h - 1, y1) + 1):
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            self.hline(x, x + w - 1, yy, c)

    def rect(self, x, y, w, h, c, t=1):
        for k in range(t):
            self.hline(x, x + w - 1, y + k, c)
            self.hline(x, x + w - 1, y + h - 1 - k, c)
            self.vline(x + k, y, y + h - 1, c)
            self.vline(x + w - 1 - k, y, y + h - 1, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def filled_ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            v = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * math.sqrt(v)) if v > 0 else 0
            self.hline(cx - dx, cx + dx, cy + dy, c)

    def filled_circle(self, cx, cy, r, c):
        self.filled_ellipse(cx, cy, r, r, c)

    def fill_poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(max(0, int(min(ys))), min(self.h - 1, int(max(ys))) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(xs[i]), int(xs[i + 1]), y, c)

    def star(self, cx, cy, r_out, r_in, c):
        pts = []
        for i in range(10):
            r = r_out if i % 2 == 0 else r_in
            a = math.radians(-90 + i * 36)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        self.fill_poly(pts, c)

    def to_png(self):
        raw = b"".join(b"\x00" + bytes(self.px[y * self.w * 3:(y + 1) * self.w * 3])
                       for y in range(self.h))
        comp = zlib.compress(raw, 9)

        def chunk(typ, data):
            c = struct.pack(">I", len(data)) + typ + data
            return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 chars, '#' = on. All text is set in capitals.
FONT = {
    "A": [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    "C": [" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"],
    "D": ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "F": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    "G": [" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "],
    "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "I": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"],
    "J": ["  ###", "    #", "    #", "    #", "    #", "#   #", " ### "],
    "K": ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "S": [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"],
    "X": ["#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"],
    "Y": ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],
    "0": [" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "],
    "1": ["  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "2": [" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"],
    "3": ["#### ", "    #", "    #", " ### ", "    #", "    #", "#### "],
    "4": ["   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "],
    "5": ["#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "],
    "6": [" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "],
    "7": ["#####", "    #", "   # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "8": [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "],
    "9": [" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "],
    " ": ["     ", "     ", "     ", "     ", "     ", "     ", "     "],
    ".": ["     ", "     ", "     ", "     ", "     ", "     ", "  #  "],
    ",": ["     ", "     ", "     ", "     ", "     ", "  #  ", " #   "],
    ":": ["     ", "  #  ", "     ", "     ", "     ", "  #  ", "     "],
    ";": ["     ", "  #  ", "     ", "     ", "     ", "  #  ", " #   "],
    "'": ["  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "],
    "-": ["     ", "     ", "     ", " ### ", "     ", "     ", "     "],
    "/": ["    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "],
    "!": ["  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "],
    "?": [" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "],
    "(": ["   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "],
    ")": [" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "],
    "%": ["#   #", "#  # ", "   # ", "  #  ", " #   ", "#  # ", "#   #"],
    "+": ["     ", "  #  ", "  #  ", " ### ", "  #  ", "  #  ", "     "],
}

def text_width(s, scale):
    return len(s) * 6 * scale - scale if s else 0

def draw_text(cv, x, y, s, scale, color, align="left"):
    s = s.upper()  # the bitmap font only carries capitals, digits and punctuation
    if align == "center":
        x -= text_width(s, scale) // 2
    elif align == "right":
        x -= text_width(s, scale)
    for ch in s:
        g = FONT.get(ch, FONT[" "])
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row[c] == "#":
                    cv.fill_rect(x + c * scale, y + r * scale, scale, scale, color)
        x += 6 * scale

def wrap_text(s, max_w, scale):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- pictograms
def draw_chip(cv, x, y, w, h):
    """Nvidia chip with pins and a red down arrow."""
    cv.fill_rect(x, y, w, h, GREEN_NV)
    cv.rect(x, y, w, h, GREEN_DK, 3)
    cv.fill_rect(x + 14, y + 14, w - 28, h - 28, GREEN_DK)
    draw_text(cv, x + w // 2, y + h // 2 - 10, "NVDA", 3, WHITE, "center")
    for i in range(5):  # pins top and bottom
        px = x + 16 + i * 26
        cv.fill_rect(px, y - 10, 10, 10, GREEN_DK)
        cv.fill_rect(px, y + h, 10, 10, GREEN_DK)
    for i in range(3):  # pins left and right
        py = y + 16 + i * 30
        cv.fill_rect(x - 10, py, 10, 10, GREEN_DK)
        cv.fill_rect(x + w, py, 10, 10, GREEN_DK)
    ax = x + w + 34  # down arrow
    cv.fill_rect(ax, y + 8, 16, h - 56, RED)
    cv.fill_poly([(ax - 14, y + h - 48), (ax + 30, y + h - 48),
                  (ax + 8, y + h - 2)], RED)

def draw_dove(cv, x, y, w, h):
    """White dove over a blue-yellow flag (Ukraine)."""
    cv.fill_rect(x, y, w, h // 2, BLUE_UK)
    cv.fill_rect(x, y + h // 2, w, h - h // 2, YELLOW_UK)
    bx, by = x + w // 2, y + h // 2  # dove body centre
    cv.fill_poly([(bx - 34, by + 6), (bx - 52, by - 6), (bx - 50, by + 12)], WHITE)  # tail
    cv.filled_ellipse(bx, by, 30, 17, WHITE)      # body
    cv.filled_circle(bx + 28, by - 14, 10, WHITE)  # head
    cv.fill_poly([(bx + 36, by - 16), (bx + 48, by - 12), (bx + 36, by - 9)], GOLD)  # beak
    cv.fill_poly([(bx - 18, by - 6), (bx + 6, by - 16), (bx + 2, by + 8)], WHITE)    # wing
    cv.filled_circle(bx + 31, by - 16, 2, INK)    # eye

def draw_cloud(cv, x, y, w, h):
    """Cloud with lightning bolt and 365 (Microsoft 365 outage)."""
    cv.fill_rect(x, y, w, h, (207, 232, 247))  # sky, so the white cloud reads
    cv.filled_circle(x + 28, y + 52, 20, WHITE)
    cv.filled_circle(x + 56, y + 40, 26, WHITE)
    cv.filled_circle(x + 86, y + 52, 20, WHITE)
    cv.fill_rect(x + 12, y + 52, 92, 26, WHITE)
    cv.fill_poly([(x + 62, y + 48), (x + 44, y + 82), (x + 56, y + 82),
                  (x + 50, y + 104), (x + 78, y + 66), (x + 64, y + 66),
                  (x + 74, y + 48)], YELLOW_BOLT)
    draw_text(cv, x + w // 2, y + h - 14, "365", 2, BLUE_MS, "center")

def draw_ship(cv, x, y, w, h):
    """Warship on waves under a red star (China Pacific drills)."""
    cv.fill_rect(x, y + h - 34, w, 34, SEA)
    cv.hline(x, x + w - 1, y + h - 30, WHITE)
    cv.hline(x + 8, x + w - 9, y + h - 22, WHITE)
    cv.fill_poly([(x + 10, y + 66), (x + 110, y + 66), (x + 98, y + 88),
                  (x + 22, y + 88)], GREY)                    # hull
    cv.fill_rect(x + 52, y + 44, 22, 22, GREY)                # tower
    cv.vline(x + 63, y + 26, y + 44, GREY)                    # mast
    cv.fill_poly([(x + 63, y + 26), (x + 79, y + 31), (x + 63, y + 36)], RED)  # flag
    cv.star(x + 63, y + 14, 12, 5, RED)                       # red star

def draw_tanker(cv, x, y, w, h):
    """Oil tanker, spiky naval mine, warning triangle (Gulf)."""
    cv.fill_rect(x, y + h - 30, w, 30, TEAL)
    cv.hline(x, x + w - 1, y + h - 26, WHITE)
    # spiky mine, top left
    mx, my = x + 22, y + 30
    for k in range(8):
        a = math.radians(k * 45)
        cv.line(int(mx + 12 * math.cos(a)), int(my + 12 * math.sin(a)),
                int(mx + 20 * math.cos(a)), int(my + 20 * math.sin(a)), INK)
    cv.filled_circle(mx, my, 13, INK)
    # tanker, bottom right
    cv.fill_rect(x + 34, y + 76, 80, 16, DARKRED)
    cv.fill_poly([(x + 114, y + 76), (x + 114, y + 92), (x + 98, y + 92)], DARKRED)
    cv.fill_rect(x + 88, y + 58, 20, 18, GREY)   # bridge
    cv.fill_rect(x + 62, y + 66, 10, 10, GREY)   # funnel
    # warning triangle, top right
    tx, ty = x + 96, y + 8
    cv.fill_poly([(tx, ty + 30), (tx + 15, ty), (tx + 30, ty + 30)], YELLOW_BOLT)
    draw_text(cv, tx + 15, ty + 12, "!", 2, INK, "center")

# ---------------------------------------------------------------- layout
def panel(cv, x, y, w, h, accent):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.fill_rect(x, y, w, 8, accent)
    cv.rect(x, y, w, h, INK, 2)

def story_panel(cv, x, y, w, h, accent, pic, headline, summary):
    panel(cv, x, y, w, h, accent)
    pic(cv, x + 16, y + 34, 120, 116)
    hx = x + 150
    lines = wrap_text(headline, w - 166, 3)
    for i, ln in enumerate(lines[:2]):
        draw_text(cv, hx, y + 36 + i * 26, ln, 3, INK)
    slines = wrap_text(summary, w - 32, 3)
    for i, ln in enumerate(slines[:4]):
        draw_text(cv, x + 16, y + 166 + i * 24, ln, 3, INK)

def main():
    cv = Canvas(W, H, PAPER)

    # masthead
    cv.fill_rect(0, 0, W, 104, NAVY)
    draw_text(cv, W // 2, 18, "THE WORLD IN ONE DAY", 5, WHITE, "center")
    draw_text(cv, W // 2, 66, "FRIDAY 13 NOVEMBER 2026", 3, GOLD, "center")
    cv.fill_rect(0, 104, W, 4, GOLD)

    # lead story: Nvidia
    panel(cv, 8, 112, 1008, 268, GREEN_NV)
    draw_chip(cv, 36, 168, 150, 110)
    draw_text(cv, 1008 - 24, 132, "TOP STORY", 2, GOLD, "right")
    draw_text(cv, 308, 132, "NVIDIA CHIEF", 4, INK)
    draw_text(cv, 308, 172, "EXECUTIVE RESIGNS", 4, INK)
    lead = ("Jensen Huang steps down as chief executive and leaves the board. "
            "Chief financial officer Colette Kress becomes interim CEO.")
    for i, ln in enumerate(wrap_text(lead, 676, 3)):
        draw_text(cv, 308, 224 + i * 26, ln, 3, INK)

    # 2x2 grid
    story_panel(cv, 8, 388, 500, 280, BLUE_UK, draw_dove,
                "UKRAINE TALKS OPEN TO EUROPE",
                "Europe joins the next peace talks. Moscow and Kyiv plan "
                "the war's biggest prisoner swap.")
    story_panel(cv, 516, 388, 500, 280, BLUE_MS, draw_cloud,
                "MICROSOFT 365 GOES DOWN",
                "A worldwide Microsoft 365 outage disrupts businesses, "
                "schools and government services.")
    story_panel(cv, 8, 676, 500, 280, RED, draw_ship,
                "CHINA'S BIG PACIFIC DRILLS",
                "Taiwan details huge, unannounced Chinese naval drills "
                "across the Pacific and around Taiwan.")
    story_panel(cv, 516, 676, 500, 280, ORANGE, draw_tanker,
                "TANKER HIT IN THE GULF",
                "A tanker hits a mine in the Strait of Hormuz. Inspectors "
                "cannot trace 440 kg of Iran's uranium.")

    # footer
    cv.fill_rect(0, 964, W, 60, NAVY)
    draw_text(cv, W // 2, 986,
              "SOURCES - REUTERS - AP - IEA - IAEA - ALL EVENTS FRIDAY 13 NOVEMBER 2026",
              2, WHITE, "center")

    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    data = cv.to_png()
    with open(os.path.join(out, "entry.png"), "wb") as f:
        f.write(data)

if __name__ == "__main__":
    main()
