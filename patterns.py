import random

import numpy as np

DISP_W = 84
DISP_H = 7

R, C = np.indices((DISP_H, DISP_W))


def blank():
    return np.zeros((DISP_H, DISP_W), dtype=np.uint8)


def vertical_stripes():
    w = random.choice([1, 2, 3])
    return ((C // w) % 2 == 0).astype(np.uint8)


def horizontal_stripes():
    w = random.choice([1, 2])
    return ((R // w) % 2 == 0).astype(np.uint8)


def diagonal_stripes():
    w = random.choice([2, 3, 4])
    d = random.choice([1, -1])
    return (((C + d * R) // w) % 2 == 0).astype(np.uint8)


def checkerboard():
    s = random.choice([1, 2])
    return (((C // s) + (R // s)) % 2 == 0).astype(np.uint8)


def diamonds():
    per = random.choice([7, 9, 11])
    rad = random.choice([3, 4])
    cc = (C % per) - per // 2
    rr = R - DISP_H // 2
    return (np.abs(cc) + np.abs(rr) <= rad).astype(np.uint8)


def triangles():
    per = random.choice([6, 8, 10, 12])
    ramp = (C % per) * DISP_H // per
    return (R >= DISP_H - 1 - ramp).astype(np.uint8)


def zigzag():
    per = random.choice([6, 8, 10, 12])
    thick = random.choice([1, 2])
    cols = np.arange(DISP_W)
    tri = np.abs((cols % per) - per / 2) / (per / 2)
    y = np.round(tri * (DISP_H - 1)).astype(int)
    canvas = blank()
    for t in range(thick):
        canvas[np.clip(y + t, 0, DISP_H - 1), cols] = 1
    return canvas


def sine():
    freq = random.uniform(0.15, 0.6)
    phase = random.uniform(0, 6.283)
    fill = random.random() < 0.5
    cols = np.arange(DISP_W)
    y = np.round((DISP_H - 1) / 2 * (1 + np.sin(cols * freq + phase))).astype(int)
    canvas = blank()
    if fill:
        for c in cols:
            canvas[y[c]:, c] = 1
    else:
        canvas[y, cols] = 1
    return canvas


def border():
    canvas = blank()
    canvas[0, :] = canvas[-1, :] = 1
    canvas[:, 0] = canvas[:, -1] = 1
    return canvas


def grid():
    rs = random.choice([2, 3])
    cs = random.choice([3, 4, 6])
    return (((R % rs) == 0) | ((C % cs) == 0)).astype(np.uint8)


def dots():
    rs = random.choice([2, 3])
    cs = random.choice([2, 3, 4])
    return (((R % rs) == 0) & ((C % cs) == 0)).astype(np.uint8)


def noise():
    density = random.uniform(0.2, 0.5)
    return (np.random.random((DISP_H, DISP_W)) < density).astype(np.uint8)


def brick():
    per = 8
    canvas = blank()
    canvas[0::3, :] = 1
    for band, r0 in enumerate(range(0, DISP_H, 3)):
        off = (band % 2) * (per // 2)
        cols = np.where((np.arange(DISP_W) + off) % per == 0)[0]
        canvas[r0:r0 + 3, cols] = 1
    return canvas


def bullseye():
    per = random.choice([7, 9, 11])
    cc = (C % per) - per // 2
    rr = R - DISP_H // 2
    return ((np.abs(cc) + np.abs(rr)) % 2 == 0).astype(np.uint8)


def diamond_lattice():
    per = random.choice([7, 9, 11])
    rad = per // 2
    cc = (C % per) - rad
    rr = R - DISP_H // 2
    return (np.abs(cc) + np.abs(rr) == rad).astype(np.uint8)


def nested_boxes():
    rings = np.minimum(np.minimum(R, DISP_H - 1 - R), np.minimum(C, DISP_W - 1 - C))
    off = random.choice([0, 1])
    return ((rings + off) % 2 == 0).astype(np.uint8)


def ripples():
    cx = random.uniform(0, DISP_W)
    cy = random.uniform(0, DISP_H)
    freq = random.uniform(0.6, 1.4)
    d = np.sqrt((C - cx) ** 2 + (R - cy) ** 2)
    return (np.sin(d * freq) > 0).astype(np.uint8)


def rays():
    cx = random.uniform(0, DISP_W)
    cy = (DISP_H - 1) / 2
    n = random.choice([6, 8, 12, 16])
    ang = np.arctan2(R - cy, C - cx)
    return ((ang / np.pi * n).astype(int) % 2 == 0).astype(np.uint8)


def spiral():
    cx, cy = DISP_W / 2, (DISP_H - 1) / 2
    tight = random.choice([1.0, 1.5, 2.0])
    d = np.sqrt((C - cx) ** 2 + (R - cy) ** 2)
    ang = np.arctan2(R - cy, C - cx)
    return ((d - ang / np.pi * tight).astype(int) % 2 == 0).astype(np.uint8)


def equalizer():
    bw = random.choice([2, 3])
    canvas = blank()
    x = 0
    while x < DISP_W:
        h = random.randint(1, DISP_H)
        canvas[DISP_H - h:, x:x + bw] = 1
        x += bw + 1
    return canvas


def pyramids():
    per = random.choice([8, 10, 12])
    cc = np.abs((C % per) - per / 2)
    ramp = np.round((1 - cc / (per / 2)) * (DISP_H - 1)).astype(int)
    return (R >= DISP_H - 1 - ramp).astype(np.uint8)


HOUNDS = np.array([
    [1, 1, 0, 0],
    [1, 1, 0, 1],
    [0, 0, 1, 1],
    [1, 0, 1, 1],
], dtype=np.uint8)


def houndstooth():
    return np.tile(HOUNDS, (2, 22))[:DISP_H, :DISP_W]


def basket_weave():
    block = ((R // 2) + (C // 2)) % 2
    horiz = (R % 2 == 0)
    vert = (C % 2 == 0)
    return np.where(block == 0, horiz, vert).astype(np.uint8)


def cross_hatch():
    w = random.choice([3, 4, 5])
    a = ((C + R) % w == 0)
    b = ((C - R) % w == 0)
    return (a | b).astype(np.uint8)


def plasma():
    f1 = random.uniform(0.2, 0.5)
    f2 = random.uniform(0.2, 0.5)
    p = random.uniform(0, 6.283)
    v = np.sin(C * f1) + np.sin(R * f2 + p) + np.sin((C + R) * f1 * 0.5)
    thr = random.uniform(-0.5, 0.5)
    return (v > thr).astype(np.uint8)


def moire():
    w1 = random.choice([2, 3])
    w2 = w1 + 1
    a = ((C + R) // w1) % 2
    b = ((C - R) // w2) % 2
    return (a ^ b).astype(np.uint8)


def interference():
    f1 = random.uniform(0.2, 0.5)
    f2 = random.uniform(0.2, 0.5)
    p = random.uniform(0, 6.283)
    v = np.sin(C * f1) + np.sin(C * f2 + p)
    return (v > 0).astype(np.uint8)


def confetti():
    density = random.uniform(0.05, 0.15)
    return (np.random.random((DISP_H, DISP_W)) < density).astype(np.uint8)


def mosaic():
    bs = random.choice([2, 3, 4])
    small = np.random.random((DISP_H // bs + 1, DISP_W // bs + 1)) < 0.5
    big = np.repeat(np.repeat(small, bs, axis=0), bs, axis=1)
    return big[:DISP_H, :DISP_W].astype(np.uint8)


BAYER = np.array([
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5],
]) / 16.0


def gradient():
    tiled = np.tile(BAYER, (2, 22))[:DISP_H, :DISP_W]
    ramp = C / (DISP_W - 1)
    if random.random() < 0.5:
        ramp = 1 - ramp
    return (ramp > tiled).astype(np.uint8)


def random_bars():
    canvas = blank()
    x = 0
    on = random.random() < 0.5
    while x < DISP_W:
        w = random.choice([1, 2, 3, 4])
        if on:
            canvas[:, x:x + w] = 1
        on = not on
        x += w
    return canvas


def random_rows():
    canvas = blank()
    y = 0
    on = random.random() < 0.5
    while y < DISP_H:
        h = random.choice([1, 2])
        if on:
            canvas[y:y + h, :] = 1
        on = not on
        y += h
    return canvas


HEART = [
    ".##.##.",
    "#######",
    "#######",
    ".#####.",
    "..###..",
    "...#...",
]

DIAMOND = [
    "...#...",
    "..###..",
    ".#####.",
    "#######",
    ".#####.",
    "..###..",
    "...#...",
]

CHEVRON = [
    "#...",
    ".#..",
    "..#.",
    "...#",
    "..#.",
    ".#..",
    "#...",
]

PLAY = [
    "#......",
    "##.....",
    "###....",
    "####...",
    "###....",
    "##.....",
    "#......",
]

CROSS = [
    "#.....#",
    ".#...#.",
    "..#.#..",
    "...#...",
    "..#.#..",
    ".#...#.",
    "#.....#",
]

CIRCLE = [
    ".#####.",
    "#.....#",
    "#.....#",
    "#.....#",
    "#.....#",
    "#.....#",
    ".#####.",
]

SMILEY = [
    ".#####.",
    "#.....#",
    "#.#.#.#",
    "#.....#",
    "#.###.#",
    "#.....#",
    ".#####.",
]

STAR = [
    "...#...",
    "...#...",
    "#######",
    ".#####.",
    "..###..",
    ".##.##.",
    "#.....#",
]

ARROW_UP = [
    "...#...",
    "..###..",
    ".#####.",
    "#######",
    "...#...",
    "...#...",
    "...#...",
]

FLOWER = [
    "..#.#..",
    ".#####.",
    "#######",
    ".#####.",
    "..###..",
    "...#...",
    "...#...",
]

NOTE = [
    "..####.",
    "..#..#.",
    "..#....",
    "..#....",
    ".##....",
    "###....",
    ".#.....",
]

SKULL = [
    ".#####.",
    "#######",
    "#.#.#.#",
    "#######",
    ".#####.",
    ".#.#.#.",
    ".#.#.#.",
]

DROP = [
    "...#...",
    "...#...",
    "..###..",
    ".#####.",
    "#######",
    "#######",
    ".#####.",
]

WINK = [
    ".#####.",
    "#.....#",
    "#.#.##.",
    "#.....#",
    "#.###.#",
    "#.....#",
    ".#####.",
]


PLUS = [
    "..#..",
    "..#..",
    "#####",
    "..#..",
    "..#..",
]

EX = [
    "#...#",
    ".#.#.",
    "..#..",
    ".#.#.",
    "#...#",
]

GHOST = [
    ".#####.",
    "#######",
    "##.#.##",
    "#######",
    "#######",
    "#######",
    "#.#.#.#",
]

ALIEN = [
    "#.#.#.#",
    ".#####.",
    "#######",
    "#.###.#",
    "#######",
    ".#.#.#.",
    "#.....#",
]

SPACE_INVADER = [
    "..#.#..",
    ".#####.",
    "##.#.##",
    "#######",
    "#.###.#",
    "#.....#",
    ".#...#.",
]

ARROW_RIGHT = [
    "...#...",
    "...##..",
    "#######",
    "#######",
    "#######",
    "...##..",
    "...#...",
]

ARROW_LEFT = [
    "...#...",
    "..##...",
    "#######",
    "#######",
    "#######",
    "..##...",
    "...#...",
]

HOURGLASS = [
    "#######",
    ".#####.",
    "..###..",
    "...#...",
    "..###..",
    ".#####.",
    "#######",
]

KEY = [
    ".###...",
    "#...#..",
    "#...#..",
    ".###...",
    "..#....",
    "..###..",
    "..#.#..",
]

ANCHOR = [
    "...#...",
    "..#.#..",
    "...#...",
    ".#####.",
    "...#...",
    "#..#..#",
    ".#####.",
]

LIGHTNING = [
    "...##..",
    "..##...",
    ".##....",
    "######.",
    "...##..",
    "..##...",
    ".##....",
]

YINYANG = [
    ".#####.",
    "###..##",
    "###...#",
    "##.#..#",
    "#...###",
    "#..####",
    ".#####.",
]

COFFEE = [
    "#.#.#..",
    ".#.#...",
    "#######",
    "#####.#",
    "#####.#",
    "#####..",
    ".#####.",
]

CAT = [
    "#.....#",
    "##...##",
    "#######",
    "#.#.#.#",
    "#######",
    "#.###.#",
    "#######",
]


def _parse(glyph):
    return np.array([[1 if ch == "#" else 0 for ch in row] for row in glyph], dtype=np.uint8)


def _tiler(name, glyph):
    g = _parse(glyph)
    gh, gw = g.shape
    top = (DISP_H - gh) // 2

    def fn():
        gap = random.choice([1, 2, 3])
        step = gw + gap
        n = max((DISP_W + gap) // step, 1)
        used = n * gw + (n - 1) * gap
        x = (DISP_W - used) // 2
        canvas = blank()
        for _ in range(n):
            canvas[top:top + gh, x:x + gw] = g
            x += step
        return canvas

    fn.__name__ = name
    return fn


hearts = _tiler("hearts", HEART)
gem_row = _tiler("gem_row", DIAMOND)
chevrons = _tiler("chevrons", CHEVRON)
arrows = _tiler("arrows", PLAY)
crosses = _tiler("crosses", CROSS)
circles = _tiler("circles", CIRCLE)
smileys = _tiler("smileys", SMILEY)
winks = _tiler("winks", WINK)
stars = _tiler("stars", STAR)
flowers = _tiler("flowers", FLOWER)
notes = _tiler("notes", NOTE)
skulls = _tiler("skulls", SKULL)
drops = _tiler("drops", DROP)
up_arrows = _tiler("up_arrows", ARROW_UP)
right_arrows = _tiler("right_arrows", ARROW_RIGHT)
left_arrows = _tiler("left_arrows", ARROW_LEFT)
pluses = _tiler("pluses", PLUS)
exes = _tiler("exes", EX)
ghosts = _tiler("ghosts", GHOST)
aliens = _tiler("aliens", ALIEN)
invaders = _tiler("invaders", SPACE_INVADER)
hourglasses = _tiler("hourglasses", HOURGLASS)
keys = _tiler("keys", KEY)
anchors = _tiler("anchors", ANCHOR)
bolts = _tiler("bolts", LIGHTNING)
yinyangs = _tiler("yinyangs", YINYANG)
coffees = _tiler("coffees", COFFEE)
cats = _tiler("cats", CAT)


PATTERNS = [
    vertical_stripes,
    horizontal_stripes,
    diagonal_stripes,
    checkerboard,
    diamonds,
    triangles,
    zigzag,
    sine,
    border,
    grid,
    dots,
    noise,
    brick,
    hearts,
    gem_row,
    chevrons,
    arrows,
    crosses,
    circles,
    smileys,
]

_last = -1


def random_frame():
    global _last
    i = random.randrange(len(PATTERNS))
    while len(PATTERNS) > 1 and i == _last:
        i = random.randrange(len(PATTERNS))
    _last = i
    return PATTERNS[i]()


if __name__ == "__main__":
    for fn in PATTERNS:
        print(fn.__name__ if hasattr(fn, "__name__") else fn)
        for row in fn():
            print("".join("█" if v else "·" for v in row))
        print()
