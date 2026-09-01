import unittest

from lx200_protocol import (
    Lx200Session,
    format_dec,
    format_ra,
    format_site_angle,
    format_site_longitude,
    parse_dec,
    parse_longitude,
    parse_ra,
)


class Lx200ProtocolTest(unittest.TestCase):
    def test_formats_coordinates(self):
        self.assertEqual(format_ra(279.23473479), "18:36:56#")
        self.assertEqual(format_ra(360.0), "00:00:00#")
        self.assertEqual(format_dec(38.78368896), "+38*47:01#")
        self.assertEqual(format_dec(-6.1946), "-06*11:41#")

    def test_parses_coordinates(self):
        self.assertAlmostEqual(parse_ra("18:36:56"), 279.2333333, places=5)
        self.assertAlmostEqual(parse_dec("+38*47:01"), 38.7836111, places=5)
        self.assertAlmostEqual(parse_dec("-06:11:41"), -6.1947222, places=5)
        self.assertAlmostEqual(parse_longitude("+006*11:41"), 6.1947222, places=5)
        self.assertAlmostEqual(parse_longitude("357*52"), 357.8666667, places=5)

    def test_formats_site_coordinates(self):
        self.assertEqual(format_site_angle(36.4753, 2), "+36*29#")
        self.assertEqual(format_site_longitude(-6.1946), "006*12#")
        self.assertEqual(format_site_longitude(2.1333333), "357*52#")

    def test_rejects_invalid_coordinates(self):
        for value in ("24:00:00", "12:60:00", "wrong"):
            with self.assertRaises(ValueError):
                parse_ra(value)
        for value in ("+91*00:00", "+90*00:01", "38*47:01"):
            with self.assertRaises(ValueError):
                parse_dec(value)

    def test_reports_position_and_accepts_target(self):
        targets = []
        session = Lx200Session(
            lambda: (279.23473479, 38.78368896),
            lambda ra, dec: targets.append((ra, dec)),
            (36.4753, -6.1946),
        )

        self.assertEqual(session.execute("GR"), "18:36:56#")
        self.assertEqual(session.execute("GD"), "+38*47:01#")
        self.assertEqual(session.execute("Sr04:35:55"), "1")
        self.assertEqual(session.execute("Sd+16*30:33"), "1")
        self.assertEqual(session.execute("MS"), "0")
        self.assertEqual(len(targets), 1)
        self.assertAlmostEqual(targets[0][0], 68.9791667, places=5)
        self.assertAlmostEqual(targets[0][1], 16.5091667, places=5)

    def test_rejects_goto_without_complete_target(self):
        session = Lx200Session(lambda: (0.0, 0.0), lambda *_: None, (0.0, 0.0))
        self.assertEqual(session.execute("Sr99:00:00"), "0")
        self.assertEqual(session.execute("MS"), "1")

    def test_reports_identity_and_location(self):
        session = Lx200Session(lambda: (0.0, 0.0), lambda *_: None, (36.5, -6.2))
        self.assertEqual(session.execute("GVP"), "Telescope DSC#")
        self.assertEqual(session.execute("Gt"), "+36*30#")
        self.assertEqual(session.execute("Gg"), "006*12#")

    def test_reports_mobile_mount_status(self):
        session = Lx200Session(lambda: (0.0, 0.0), lambda *_: None, (0.0, 0.0))
        self.assertRegex(session.execute("GC"), r"^\d{2}/\d{2}/\d{2}#$")
        self.assertRegex(session.execute("GL"), r"^\d{2}:\d{2}:\d{2}#$")
        self.assertRegex(session.execute("GG"), r"^[+-]\d{2}\.\d#$")
        self.assertEqual(session.execute("GW"), "AT2#")
        self.assertEqual(session.execute("D"), "#")

    def test_accepts_mobile_location_sync(self):
        observers = []
        session = Lx200Session(
            lambda: (0.0, 0.0),
            lambda *_: None,
            (36.4753, -6.1946),
            observers.append,
        )

        self.assertEqual(session.execute("SG-02.0"), "1")
        self.assertEqual(session.execute("St+41*22"), "1")
        self.assertEqual(session.execute("Sg357*50"), "1")
        self.assertEqual(session.execute("Gt"), "+41*22#")
        self.assertEqual(session.execute("Gg"), "357*50#")
        self.assertAlmostEqual(observers[-1][0], 41.3666667, places=6)
        self.assertAlmostEqual(observers[-1][1], 2.1666667, places=6)


if __name__ == "__main__":
    unittest.main()
