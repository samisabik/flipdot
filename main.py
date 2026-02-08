import time
import random

import numpy as np
from PIL import Image, ImageFont, ImageDraw
from serial import Serial
from evdev import InputDevice, categorize, ecodes


# ── Config ──────────────────────────────────────────────────────────

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 4800
SIGN_ADDRESS = 2

DISP_W = 84
DISP_H = 7

FONT_PATH = "nes-arcade-font-2-1-monospaced.ttf"
FONT_SIZE = 7

SCROLL_STEP = 1          # pixels per scroll step (2+ = faster, choppier)
INPUT_DEVICE = "/dev/input/event0"
INPUT_KEY = "KEY_B"

# Serial TX time for one frame + margin for the display controller
FRAME_INTERVAL = (176 * 10 / BAUD_RATE) + 0.03


# ── Serial / Hanover protocol ──────────────────────────────────────

ser = Serial(SERIAL_PORT, baudrate=BAUD_RATE)

# FTDI adapters default to 16ms latency, which causes frame jitter
try:
    with open("/sys/bus/usb-serial/devices/ttyUSB0/latency_timer", "w") as f:
        f.write("1")
except OSError:
    pass


def _image_to_bytes(image):
    """Encode a numpy frame into Hanover column-major packed bytes."""
    rows, cols = image.shape
    data_rows = (rows + 7) & ~7
    if data_rows != rows:
        padded = np.zeros((data_rows, cols), dtype=np.uint8)
        padded[:rows, :] = image
    else:
        padded = image.astype(np.uint8)
    packed = np.packbits(padded[::-1], axis=0)
    return packed[::-1].flatten(order="F").tobytes()


def _build_packet(image_bytes):
    """Build a Hanover write_image serial packet."""
    resolution = len(image_bytes) & 0xFF
    hex_payload = format(resolution, "02X") + image_bytes.hex().upper()
    body = "1{:1X}".format(SIGN_ADDRESS).encode() + hex_payload.encode() + b"\x03"
    total = sum(body) & 0xFF
    checksum = ((total ^ 0xFF) + 1) & 0xFF
    return b"\x02" + body + format(checksum, "02X").encode()


def _frame_to_packet(frame):
    return _build_packet(_image_to_bytes(frame))


def _send_packets(packets):
    """Send pre-built packets with fixed-interval timing."""
    for packet in packets:
        t0 = time.monotonic()
        ser.write(packet)
        ser.flush()
        remaining = FRAME_INTERVAL - (time.monotonic() - t0)
        if remaining > 0:
            time.sleep(remaining)


def send_frame(frame):
    ser.write(_frame_to_packet(frame))
    ser.flush()


# ── Text rendering ─────────────────────────────────────────────────

font = ImageFont.truetype(FONT_PATH, FONT_SIZE)


def text_to_pixels(text):
    left, _, right, bottom = font.getbbox(text)
    w, h = right - left, bottom * 2
    image = Image.new("L", (w, h), 1)
    ImageDraw.Draw(image).text((0, 0), text, font=font)
    arr = np.asarray(image)
    arr = np.where(arr, 0, 1)
    return arr[(arr != 0).any(axis=1)]


def text_to_frame(text):
    """Render text into a display-sized frame, or None if it needs scrolling."""
    arr = text_to_pixels(text)
    if arr.shape[1] <= DISP_W:
        return np.pad(arr, ((0, 0), (0, DISP_W - arr.shape[1]))).astype(np.uint8)
    return None


# ── Animations ─────────────────────────────────────────────────────

def roll_transition(old_frame, new_frame):
    """New text rolls in from the top, old text exits at the bottom."""
    packets = []
    for shift in range(1, DISP_H + 1):
        frame = np.zeros((DISP_H, DISP_W), dtype=np.uint8)
        frame[:shift, :] = new_frame[:shift, :]
        rest = DISP_H - shift
        if rest > 0:
            frame[shift:, :] = old_frame[:rest, :]
        packets.append(_frame_to_packet(frame))
    _send_packets(packets)


def scroll_text(arr):
    """Horizontally scroll text that's wider than the display."""
    padded = np.pad(arr, ((0, 0), (DISP_W, DISP_W)))
    packets = [
        _frame_to_packet(padded[:, i:i + DISP_W])
        for i in range(0, arr.shape[1] + DISP_W, SCROLL_STEP)
    ]
    _send_packets(packets)


# ── Display logic ──────────────────────────────────────────────────

current_frame = np.zeros((DISP_H, DISP_W), dtype=np.uint8)


def display(text, animate=False):
    global current_frame

    new_frame = text_to_frame(text)

    if new_frame is not None:
        if animate:
            roll_transition(current_frame, new_frame)
        else:
            send_frame(new_frame)
        current_frame = new_frame
    else:
        if animate:
            roll_transition(current_frame, np.zeros_like(current_frame))
        scroll_text(text_to_pixels(text))
        current_frame[:] = 0


# ── Word list ──────────────────────────────────────────────────────

WORDS = [
    "Acanthite", "Actinolite", "Adamite", "Aegirine", "Agate",
    "Albite", "Almandine", "Amazonite", "Amber", "Amethyst",
    "Ametrine", "Analcime", "Anatase", "Andalusite", "Andesine",
    "Andradite", "Anglesite", "Anhydrite", "Ankerite", "Anorthite",
    "Antlerite", "Apatite", "Aragonite", "Augite", "Autunite",
    "Aventurine", "Axinite", "Azurite",
    "Barite", "Benitoite", "Beryl", "Biotite", "Bismuth",
    "Bloodstone", "Boleite", "Bornite", "Bronzite", "Brookite",
    "Brucite",
    "Calcite", "Carnelian", "Carnotite", "Celestine", "Cerussite",
    "Chabazite", "Chalcedony", "Chalcocite", "Charoite", "Chlorite",
    "Chromite", "Chrysocola", "Cinnabar", "Citrine", "Cobaltite",
    "Colemanite", "Columbite", "Copper", "Coral", "Cordierite",
    "Corundum", "Covellite", "Crocoite", "Cryolite", "Cuprite",
    "Danburite", "Datolite", "Demantoid", "Diamond", "Diaspore",
    "Diopside", "Dioptase", "Dolomite",
    "Ekanite", "Elbaite", "Emerald", "Enargite", "Enstatite",
    "Epidote", "Epsomite", "Erythrite", "Euclase", "Eudialyte",
    "Euxenite",
    "Fayalite", "Feldspar", "Ferberite", "Fluorite", "Forsterite",
    "Fuchsite",
    "Gadolinite", "Gahnite", "Galena", "Garnet", "Gaspeite",
    "Gehlenite", "Gibbsite", "Glauberite", "Goethite", "Gold",
    "Goshenite", "Graphite", "Grossular", "Gypsum",
    "Hackmanite", "Halite", "Hauyne", "Heliodor", "Hematite",
    "Herderite", "Hessonite", "Hibonite", "Hiddenite", "Hornblende",
    "Howlite", "Hubnerite", "Humite",
    "Idocrase", "Ilmenite", "Inesite", "Iolite",
    "Jade", "Jadeite", "Jasper", "Jet",
    "Kaolinite", "Kernite", "Kieserite", "Kinoite", "Kunzite",
    "Kyanite",
    "Larimar", "Laumontite", "Lawsonite", "Lazulite", "Lazurite",
    "Legrandite", "Lepidolite", "Leucite", "Linarite", "Lizardite",
    "Magnesite", "Magnetite", "Malachite", "Manganite", "Marcasite",
    "Meionite", "Mesolite", "Microcline", "Microlite", "Millerite",
    "Mimetite", "Moldavite", "Monazite", "Moonstone", "Mordenite",
    "Morganite", "Muscovite",
    "Natrolite", "Nepheline", "Nephrite", "Niccolite", "Nuummite",
    "Obsidian", "Oligoclase", "Olivine", "Onyx", "Opal", "Orpiment",
    "Orthoclase",
    "Painite", "Pargasite", "Pectolite", "Periclase", "Peridot",
    "Perovskite", "Petalite", "Phenakite", "Phlogopite", "Pietersite",
    "Platinum", "Plancheite", "Pollucite", "Powellite", "Prehnite",
    "Proustite", "Purpurite", "Pyrite", "Pyrolusite", "Pyrope",
    "Pyrrhotite",
    "Quartz",
    "Raspite", "Realgar", "Rhodizite", "Rhodolite", "Rhodonite",
    "Rosasite", "Rubellite", "Ruby", "Rutile",
    "Samarskite", "Sanidine", "Sapphire", "Sardonyx", "Scapolite",
    "Scheelite", "Schorl", "Scolecite", "Scorodite", "Selenite",
    "Serandite", "Serpentine", "Siderite", "Silver",
    "Sinhalite", "Sodalite", "Sphalerite", "Sphene",
    "Spinel", "Spodumene", "Stannite", "Staurolite", "Stibnite",
    "Stilbite", "Strengite", "Sugilite", "Sulfur", "Sunstone",
    "Taaffeite", "Talc", "Tantalite", "Tanzanite", "Tektite",
    "Tennantite", "Tephroite", "Thomsonite", "Titanite", "Topaz",
    "Torbernite", "Tourmaline", "Tremolite", "Triphylite", "Triplite",
    "Troilite", "Tsavorite", "Tugtupite", "Turquoise",
    "Ulexite", "Uraninite", "Uvarovite", "Uvite",
    "Vanadinite", "Variscite", "Vivianite",
    "Wardite", "Wavellite", "Willemite", "Witherite", "Wolframite",
    "Wulfenite", "Wurtzite",
    "Xenotime",
    "Zektzerite", "Zeolite", "Zincite", "Zircon", "Zoisite",
]


# ── Main ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    dev = InputDevice(INPUT_DEVICE)
    print(f"Listening on: {dev.name}")

    display(random.choice(WORDS))

    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            key_event = categorize(event)
            if key_event.keycode == INPUT_KEY and key_event.keystate == key_event.key_down:
                text = random.choice(WORDS)
                print(f"Pedal pressed: {text}")
                display(text, animate=True)
