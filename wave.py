from serial import Serial
import numpy as np
import math

DISP_H = 7
DISP_W = 84
SIGN_ADDRESS = 2
BAUD_RATE = 4800

ser = Serial("/dev/ttyUSB0", baudrate=BAUD_RATE)


def _image_to_bytes(image):
    rows, cols = image.shape
    data_rows = ((rows + 7) & ~7)
    if data_rows != rows:
        padded = np.zeros((data_rows, cols), dtype=np.uint8)
        padded[:rows, :] = image
    else:
        padded = image.astype(np.uint8)
    packed = np.packbits(padded[::-1], axis=0)
    return packed[::-1].flatten(order="F").tobytes()


def _build_packet(address, image_bytes):
    resolution = len(image_bytes) & 0xFF
    hex_payload = format(resolution, "02X") + image_bytes.hex().upper()
    body = "1{:1X}".format(address).encode() + hex_payload.encode() + b"\x03"
    total = sum(body) & 0xFF
    checksum = ((total ^ 0xFF) + 1) & 0xFF
    return b"\x02" + body + format(checksum, "02X").encode()


def send_frame(image):
    ser.write(_build_packet(SIGN_ADDRESS, _image_to_bytes(image)))
    ser.flush()


def make_wave_frames(num_frames=200, wavelength=28.0, speed=0.15):
    """Pre-compute frames of a thick sine wave with trail effect."""
    frames = []
    mid = (DISP_H - 1) / 2.0
    amplitude = mid * 0.9

    for t in range(num_frames):
        frame = np.zeros((DISP_H, DISP_W), dtype=np.uint8)
        for x in range(DISP_W):
            y = mid + amplitude * math.sin(2 * math.pi * (x / wavelength - t * speed))
            # Thick wave: light up the main pixel and its neighbors
            for dy in range(-1, 2):
                row = int(round(y)) + dy
                if 0 <= row < DISP_H:
                    frame[row, x] = 1
        frames.append(frame)

    return frames


# Deduplicate consecutive identical frames — skip sends that wouldn't change anything
def dedupe_packets(packets):
    deduped = [packets[0]]
    for p in packets[1:]:
        if p != deduped[-1]:
            deduped.append(p)
    return deduped


print("Pre-computing wave frames...")
raw_frames = make_wave_frames()
packets = dedupe_packets(
    [_build_packet(SIGN_ADDRESS, _image_to_bytes(f)) for f in raw_frames]
)
print(f"{len(raw_frames)} frames -> {len(packets)} unique packets")

print("Playing wave animation (Ctrl+C to stop)")
try:
    while True:
        for packet in packets:
            ser.write(packet)
            ser.flush()
except KeyboardInterrupt:
    send_frame(np.zeros((DISP_H, DISP_W), dtype=np.uint8))
    print("\nDone.")
