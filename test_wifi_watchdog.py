import subprocess
import unittest
from collections import deque
from unittest.mock import call, Mock

from wifi_watchdog import (
    can_reach,
    get_active_connection,
    get_default_gateway,
    parse_default_gateway,
    reconnect,
    record_probe,
)


def result(returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


class WifiWatchdogTest(unittest.TestCase):
    def test_parses_default_gateway(self):
        output = "default via 192.168.68.1 dev wlan0 metric 50\n"
        self.assertEqual(parse_default_gateway(output), "192.168.68.1")

    def test_returns_none_without_default_gateway(self):
        self.assertIsNone(parse_default_gateway("192.168.68.0/22 dev wlan0\n"))

    def test_reads_gateway_only_for_requested_interface(self):
        runner = Mock(return_value=result(stdout="default via 10.0.0.1\n"))
        gateway = get_default_gateway("wlan0", runner)
        self.assertEqual(gateway, "10.0.0.1")
        runner.assert_called_once_with(
            ["ip", "-4", "route", "show", "default", "dev", "wlan0"]
        )

    def test_reads_active_network_manager_connection(self):
        runner = Mock(return_value=result(stdout="Phone hotspot\n"))
        self.assertEqual(
            get_active_connection("wlan0", runner),
            "Phone hotspot",
        )

    def test_ping_is_bound_to_wifi_interface(self):
        runner = Mock(return_value=result())
        self.assertTrue(can_reach("10.0.0.1", "wlan0", 3, 3, runner))
        runner.assert_called_once_with(
            [
                "ping",
                "-n",
                "-I",
                "wlan0",
                "-c",
                "3",
                "-i",
                "0.5",
                "-W",
                "3",
                "10.0.0.1",
            ],
            timeout=6,
        )

    def test_reconnects_the_connection_that_was_active(self):
        runner = Mock(side_effect=[result(), result()])
        self.assertTrue(reconnect("wlan0", "Phone hotspot", runner))
        self.assertEqual(
            runner.call_args_list,
            [
                call(
                    [
                        "nmcli",
                        "--wait",
                        "15",
                        "device",
                        "disconnect",
                        "wlan0",
                    ],
                    timeout=20,
                ),
                call(
                    [
                        "nmcli",
                        "--wait",
                        "45",
                        "connection",
                        "up",
                        "Phone hotspot",
                        "ifname",
                        "wlan0",
                    ],
                    timeout=50,
                ),
            ],
        )

    def test_reconnects_after_three_failures_in_five_probes(self):
        recent_results = deque(maxlen=5)
        for success in (False, True, False, True):
            self.assertFalse(record_probe(success, recent_results, 3))

        self.assertTrue(record_probe(False, recent_results, 3))

    def test_old_failures_leave_the_rolling_window(self):
        recent_results = deque((False, False, True, True, True), maxlen=5)
        self.assertFalse(record_probe(True, recent_results, 3))
        self.assertEqual(list(recent_results), [False, True, True, True, True])


if __name__ == "__main__":
    unittest.main()
