import socket
import threading
import sys

LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 1886  # Local port your client will connect to

TARGET_HOST = 'm2m.sprsun.com'
TARGET_PORT = 1886  # Real server port
functions_names = {
    1: "Read Coils",
    2: "Read Discrete Inputs",
    3: "Read Holding Registers",
    4: "Read Input Registers",
    5: "Write Single Coil",
    6: "Write Single Register",
    8: "Diagnostics",
}
import struct

def parse_modbus_rtu(data):
    if len(data) < 4:
        print("[MODBUS] Frame too short!")
        return

    address = data[0]
    func_code = data[1]
    register = struct.unpack('<H', data[2:4])[0]
    length = struct.unpack('<H', data[4:6])[0]
    payload = data[2:-2]
    crc_received = struct.unpack('<H', data[-2:])[0]

    # Recompute CRC
    crc_calc = calc_crc16(data[:-2])

    print(f"[MODBUS] Address: {address}")
    if func_code in functions_names:
        print(f"[MODBUS] Function: {functions_names[func_code]} ({func_code})")
    else:
       print(f"[MODBUS] Function: 0x{func_code:02X} ({func_code})")
    print(f"[MODBUS] Register: 0x{register:02X} ({register})")
    print(f"[MODBUS] Length:   0x{length:02X} ({length})")
    print(f"[MODBUS] Payload: {payload.hex()}")
    print(f"[MODBUS] CRC Received: 0x{crc_received:04X} | Calculated: 0x{crc_calc:04X}")

    if crc_received == crc_calc:
        print("[MODBUS] ✅ CRC OK")
    else:
        print("[MODBUS] ❌ CRC MISMATCH!")

def calc_crc16(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            lsb = crc & 0x0001
            crc >>= 1
            if lsb:
                crc ^= 0xA001
    return crc & 0xFFFF

def print_hex(direction, data):
    hexstr = data.hex()
    spaced = ' '.join(hexstr[i:i+2] for i in range(0, len(hexstr), 2))
    print(f"[{direction}] {spaced}")

def forward(src, dst, direction, print=False):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            if print:
                parse_modbus_rtu(data)
            print_hex(direction, data)
            if direction == "C→S":
                print(f'Data length=', len(data))
            dst.sendall(data)
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        src.close()
        dst.close()

def handle_client(client_sock):
    print(f"[+] Client connected")

    try:
        # Connect to real server
        server_sock = socket.create_connection((TARGET_HOST, TARGET_PORT))
        print(f"[+] Connected to {TARGET_HOST}:{TARGET_PORT}")

        # Start threads to forward data both ways
        threading.Thread(target=forward, args=(client_sock, server_sock, "C→S"), daemon=True).start()
        threading.Thread(target=forward, args=(server_sock, client_sock, "S→C", True), daemon=True).start()

    except Exception as e:
        print(f"[!] Failed to connect to server: {e}")
        client_sock.close()

def main():
    print(1)
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(2)
    listener.bind((LISTEN_HOST, LISTEN_PORT))
    print(2)
    listener.listen(5)
    print(f"[+] MITM proxy listening on {LISTEN_HOST}:{LISTEN_PORT}")
    print(f"[+] Forwarding to {TARGET_HOST}:{TARGET_PORT}")

    while True:
        client_sock, addr = listener.accept()
        threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()

if __name__ == "__main__":
    if TARGET_HOST == 'target.server.ip.or.hostname':
        print("Edit TARGET_HOST and TARGET_PORT before running!")
        sys.exit(1)
    main()
