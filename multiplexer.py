import asyncio
from itertools import cycle

# Map protokol ke satu atau lebih port
PROTOCOL_PORT_MAP = {
    "ssh": [8022],
    "http": [],
    "https": [5000, 5900],
    "tcp": [5555],
}

# Buat round-robin iterator untuk daftar port HTTPS dan TCP
https_port_cycle = cycle(PROTOCOL_PORT_MAP["https"])
tcp_port_cycle = cycle(PROTOCOL_PORT_MAP["tcp"])

async def detect_protocol(reader):
    try:
        data = await reader.read(64)
        if data.startswith(b'SSH-'):
            return "ssh", data
        elif data.startswith(b'GET') or data.startswith(b'POST'):
            return "http", data
        elif data.startswith(b'\x16\x03'):
            return "https", data
        else:
            return "tcp", data
    except Exception:
        return "unknown", b''

async def forward(src, dst):
    try:
        while True:
            data = await src.read(4096)
            if not data:
                break
            dst.write(data)
            await dst.drain()
    except:
        pass
    finally:
        dst.close()

async def handle_tcp(reader, writer):
    peer = writer.get_extra_info("peername")
    if peer:
        ip, port = peer
        print(f"[+] Koneksi dari {ip}:{port}")
    protocol, initial_data = await detect_protocol(reader)
    if protocol in PROTOCOL_PORT_MAP:
        if protocol == "https":
            target_port = next(https_port_cycle)
        elif protocol == "tcp":
            target_port = next(tcp_port_cycle)
        else:
            target_port = PROTOCOL_PORT_MAP[protocol][0]
    else:
        target_port = 2222  # fallback jika protokol tidak dikenali
    print(f"[+] Deteksi protokol: {protocol.upper()} → mengarah ke port {target_port}")
    try:
        target_reader, target_writer = await asyncio.open_connection("127.0.0.1", target_port)
        if initial_data:
            target_writer.write(initial_data)
            await target_writer.drain()
        await asyncio.gather(
            forward(reader, target_writer),
            forward(target_reader, writer)
        )
    except Exception as e:
        print(f"[-] Gagal terhubung ke port {target_port}: {e}")
        writer.close()

async def main():
    listen_port = 9000
    server = await asyncio.start_server(handle_tcp, "0.0.0.0", listen_port)
    print(f"[+] Multiplexer aktif di port {listen_port}")
    async with server:
        await server.serve_forever()

asyncio.run(main())
