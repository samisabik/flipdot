import select

import numpy as np
from serial import Serial
from evdev import InputDevice, categorize, ecodes

import patterns


SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 4800
SIGN_ADDRESS = 2

DISP_W = 84
DISP_H = 7

INPUT_DEVICE = "/dev/input/event0"
INPUT_KEY = "KEY_B"


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


def send_frame(frame):
    ser.write(_build_packet(_image_to_bytes(frame)))
    ser.flush()


if __name__ == "__main__":
    dev = InputDevice(INPUT_DEVICE)
    print(f"Listening on: {dev.name}")

    send_frame(patterns.random_frame())

    while True:
        select.select([dev.fd], [], [])
        for event in dev.read():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keycode == INPUT_KEY and key_event.keystate == key_event.key_down:
                    frame = patterns.random_frame()
                    print("Pedal pressed")
                    send_frame(frame)
