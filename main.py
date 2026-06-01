import time
import random
import select

import numpy as np
from PIL import Image, ImageFont, ImageDraw
from serial import Serial
from evdev import InputDevice, categorize, ecodes


SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 4800
SIGN_ADDRESS = 2

DISP_W = 84
DISP_H = 7

FONT_PATH = "nes-arcade-font-2-1-monospaced.ttf"
FONT_SIZE = 7

INPUT_DEVICE = "/dev/input/event0"
INPUT_KEY = "KEY_B"

FRAME_INTERVAL = (176 * 10 / BAUD_RATE) + 0.03


ser = Serial(SERIAL_PORT, baudrate=BAUD_RATE)

try:
    with open("/sys/bus/usb-serial/devices/ttyUSB0/latency_timer", "w") as f:
        f.write("1")
except OSError:
    pass


def _image_to_bytes(image):
    rows, cols = image.shape
    data_rows = (rows + 7) & ~7
    padded = np.zeros((data_rows, cols), dtype=np.uint8)
    padded[:rows] = image
    packed = np.packbits(padded[::-1], axis=0)
    return packed[::-1].flatten(order="F").tobytes()


def _build_packet(image_bytes):
    resolution = len(image_bytes) & 0xFF
    hex_payload = format(resolution, "02X") + image_bytes.hex().upper()
    body = "1{:1X}".format(SIGN_ADDRESS).encode() + hex_payload.encode() + b"\x03"
    total = sum(body) & 0xFF
    checksum = ((total ^ 0xFF) + 1) & 0xFF
    return b"\x02" + body + format(checksum, "02X").encode()


def _frame_to_packet(frame):
    return _build_packet(_image_to_bytes(frame))


def _send_packets(packets):
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


font = ImageFont.truetype(FONT_PATH, FONT_SIZE)


def text_to_pixels(text):
    left, _, right, bottom = font.getbbox(text)
    img = Image.new("L", (right - left, bottom * 2), 1)
    ImageDraw.Draw(img).text((0, 0), text, font=font)
    arr = np.where(np.asarray(img), 0, 1)
    return arr[(arr != 0).any(axis=1)]


def roll_transition(old_frame, new_frame):
    packets = []
    for shift in range(1, DISP_H + 1):
        frame = np.zeros((DISP_H, DISP_W), dtype=np.uint8)
        frame[:shift] = new_frame[:shift]
        if shift < DISP_H:
            frame[shift:] = old_frame[:DISP_H - shift]
        packets.append(_frame_to_packet(frame))
    _send_packets(packets)


current_frame = np.zeros((DISP_H, DISP_W), dtype=np.uint8)


def display(text, animate=False):
    global current_frame
    arr = text_to_pixels(text)
    if arr.shape[1] <= DISP_W:
        new_frame = np.pad(arr, ((0, 0), (0, DISP_W - arr.shape[1]))).astype(np.uint8)
    else:
        new_frame = arr[:, :DISP_W].astype(np.uint8)
    if animate:
        roll_transition(current_frame, new_frame)
    else:
        send_frame(new_frame)
    current_frame = new_frame


with open("words.txt") as f:
    WORDS = [line.strip() for line in f if line.strip()]


IDLE_TEXT = "tits 4 ..."
WORD_DURATION = 5.0


if __name__ == "__main__":
    dev = InputDevice(INPUT_DEVICE)
    print(f"Listening on: {dev.name}")

    display(IDLE_TEXT)
    word_until = None

    while True:
        timeout = None if word_until is None else max(0.0, word_until - time.monotonic())
        r, _, _ = select.select([dev.fd], [], [], timeout)

        if not r:
            display(IDLE_TEXT, animate=True)
            word_until = None
            continue

        for event in dev.read():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keycode == INPUT_KEY and key_event.keystate == key_event.key_down:
                    text = random.choice(WORDS)
                    print(f"Pedal pressed: {text}")
                    display(text, animate=True)
                    word_until = time.monotonic() + WORD_DURATION
