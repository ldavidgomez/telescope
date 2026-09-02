import argparse
import logging
import os
import select
import socket


LOGGER = logging.getLogger(__name__)


def bridge(serial_device, host, port):
    serial_fd = os.open(serial_device, os.O_RDWR | os.O_NOCTTY)
    tcp_socket = socket.create_connection((host, port), timeout=5.0)
    tcp_socket.settimeout(None)
    LOGGER.info("Bluetooth serial connection bridged to %s:%d.", host, port)

    try:
        while True:
            readable, _, _ = select.select([serial_fd, tcp_socket], [], [])
            if serial_fd in readable:
                data = os.read(serial_fd, 1024)
                if not data:
                    break
                tcp_socket.sendall(data)
            if tcp_socket in readable:
                data = tcp_socket.recv(1024)
                if not data:
                    break
                os.write(serial_fd, data)
    finally:
        tcp_socket.close()
        os.close(serial_fd)
        LOGGER.info("Bluetooth serial connection closed.")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Bridge a Bluetooth RFCOMM device to the LX200 TCP server."
    )
    parser.add_argument("device", help="Connected RFCOMM character device.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=10002)
    return parser.parse_args()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args = parse_arguments()
    try:
        bridge(args.device, args.host, args.port)
    except OSError as error:
        LOGGER.error("Bluetooth bridge failed: %s", error)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
