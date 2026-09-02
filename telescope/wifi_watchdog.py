import argparse
from collections import deque
import logging
import subprocess
import time


LOGGER = logging.getLogger(__name__)


def run_command(command, timeout=15):
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def parse_default_gateway(route_output):
    for line in route_output.splitlines():
        fields = line.split()
        if fields and fields[0] == "default" and "via" in fields:
            return fields[fields.index("via") + 1]
    return None


def get_default_gateway(interface, runner=run_command):
    result = runner(
        ["ip", "-4", "route", "show", "default", "dev", interface]
    )
    if result.returncode != 0:
        return None
    return parse_default_gateway(result.stdout)


def get_active_connection(interface, runner=run_command):
    result = runner(
        ["nmcli", "-g", "GENERAL.CONNECTION", "device", "show", interface]
    )
    if result.returncode != 0:
        return None
    connection = result.stdout.strip()
    if not connection or connection == "--":
        return None
    return connection


def can_reach(target, interface, timeout, packets, runner=run_command):
    result = runner(
        [
            "ping",
            "-n",
            "-I",
            interface,
            "-c",
            str(packets),
            "-i",
            "0.5",
            "-W",
            str(timeout),
            target,
        ],
        timeout=timeout + packets,
    )
    return result.returncode == 0


def reconnect(interface, connection, runner=run_command):
    LOGGER.warning(
        "Reconnecting Wi-Fi interface %s using connection %s.",
        interface,
        connection,
    )
    runner(
        ["nmcli", "--wait", "15", "device", "disconnect", interface],
        timeout=20,
    )
    result = runner(
        [
            "nmcli",
            "--wait",
            "45",
            "connection",
            "up",
            connection,
            "ifname",
            interface,
        ],
        timeout=50,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
        LOGGER.error("Wi-Fi reconnection failed: %s", detail)
        return False
    LOGGER.info("Wi-Fi connection %s reactivated.", connection)
    return True


def record_probe(success, recent_results, failure_threshold):
    recent_results.append(success)
    failure_count = sum(not result for result in recent_results)
    return failure_count >= failure_threshold


def watch(interface, interval, timeout, packets, failure_threshold, window_size):
    recent_results = deque(maxlen=window_size)
    unavailable_logged = False
    LOGGER.info(
        "Wi-Fi watchdog started for %s: interval=%ss, failures=%d/%d.",
        interface,
        interval,
        failure_threshold,
        window_size,
    )

    while True:
        connection = get_active_connection(interface)
        gateway = get_default_gateway(interface)

        if connection is None or gateway is None:
            recent_results.clear()
            if not unavailable_logged:
                LOGGER.info(
                    "No active IPv4 Wi-Fi connection; waiting for NetworkManager."
                )
                unavailable_logged = True
            time.sleep(interval)
            continue

        unavailable_logged = False
        success = can_reach(gateway, interface, timeout, packets)
        should_reconnect = record_probe(
            success,
            recent_results,
            failure_threshold,
        )
        failure_count = sum(not result for result in recent_results)

        if success:
            if failure_count:
                LOGGER.info(
                    "Wi-Fi gateway responded; recent failures remain %d/%d.",
                    failure_count,
                    len(recent_results),
                )
        else:
            LOGGER.warning(
                "Wi-Fi gateway %s did not respond; recent failures %d/%d.",
                gateway,
                failure_count,
                len(recent_results),
            )

        if should_reconnect:
            reconnect(interface, connection)
            recent_results.clear()

        time.sleep(interval)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Reconnect a silently stalled NetworkManager Wi-Fi link."
    )
    parser.add_argument("--interface", default="wlan0")
    parser.add_argument("--interval", type=float, default=20.0)
    parser.add_argument("--timeout", type=int, default=3)
    parser.add_argument("--packets", type=int, default=3)
    parser.add_argument("--failures", type=int, default=3)
    parser.add_argument("--window", type=int, default=5)
    args = parser.parse_args()
    if args.interval <= 0:
        parser.error("--interval must be greater than zero")
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")
    if args.packets <= 0:
        parser.error("--packets must be greater than zero")
    if args.failures <= 0:
        parser.error("--failures must be greater than zero")
    if args.window < args.failures:
        parser.error("--window must be greater than or equal to --failures")
    return args


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args = parse_arguments()
    try:
        watch(
            args.interface,
            args.interval,
            args.timeout,
            args.packets,
            args.failures,
            args.window,
        )
    except (OSError, subprocess.SubprocessError) as error:
        LOGGER.error("Wi-Fi watchdog failed: %s", error)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
