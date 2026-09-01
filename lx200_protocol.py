import re
from datetime import datetime


PRODUCT_NAME = "Telescope DSC"
FIRMWARE_VERSION = "0.1"

_RA_PATTERN = re.compile(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$")
_DEC_PATTERN = re.compile(r"^([+-])(\d{1,2})[*:](\d{2})(?::(\d{2}))?$")
_LONGITUDE_PATTERN = re.compile(
    r"^([+-]?)(\d{1,3})[*:](\d{2})(?::(\d{2}))?$"
)


def format_ra(ra_degrees):
    total_seconds = round((ra_degrees % 360.0) * 240.0) % 86400
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}#"


def format_dec(dec_degrees):
    value = max(-90.0, min(90.0, dec_degrees))
    sign = "+" if value >= 0 else "-"
    total_seconds = round(abs(value) * 3600.0)
    degrees, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{sign}{degrees:02d}*{minutes:02d}:{seconds:02d}#"


def format_site_angle(value_degrees, degree_width):
    sign = "+" if value_degrees >= 0 else "-"
    total_minutes = round(abs(value_degrees) * 60.0)
    degrees, minutes = divmod(total_minutes, 60)
    return f"{sign}{degrees:0{degree_width}d}*{minutes:02d}#"


def format_site_longitude(longitude_degrees):
    west_positive = (-longitude_degrees) % 360.0
    total_minutes = round(west_positive * 60.0) % (360 * 60)
    degrees, minutes = divmod(total_minutes, 60)
    return f"{degrees:03d}*{minutes:02d}#"


def parse_ra(value):
    match = _RA_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError("Invalid LX200 right ascension")
    hours, minutes, seconds = (
        int(part) if part is not None else 0 for part in match.groups()
    )
    if hours > 23 or minutes > 59 or seconds > 59:
        raise ValueError("Invalid LX200 right ascension")
    return (hours + minutes / 60.0 + seconds / 3600.0) * 15.0


def parse_dec(value):
    match = _DEC_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError("Invalid LX200 declination")
    sign_text, degrees_text, minutes_text, seconds_text = match.groups()
    degrees = int(degrees_text)
    minutes = int(minutes_text)
    seconds = int(seconds_text or 0)
    if degrees > 90 or minutes > 59 or seconds > 59:
        raise ValueError("Invalid LX200 declination")
    value = degrees + minutes / 60.0 + seconds / 3600.0
    if value > 90.0:
        raise ValueError("Invalid LX200 declination")
    return -value if sign_text == "-" else value


def parse_longitude(value):
    match = _LONGITUDE_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError("Invalid LX200 longitude")
    sign_text, degrees_text, minutes_text, seconds_text = match.groups()
    degrees = int(degrees_text)
    minutes = int(minutes_text)
    seconds = int(seconds_text or 0)
    maximum_degrees = 180 if sign_text else 359
    if degrees > maximum_degrees or minutes > 59 or seconds > 59:
        raise ValueError("Invalid LX200 longitude")
    longitude = degrees + minutes / 60.0 + seconds / 3600.0
    if sign_text and longitude > 180.0:
        raise ValueError("Invalid LX200 longitude")
    return -longitude if sign_text == "-" else longitude


class Lx200Session:
    def __init__(
        self,
        position_reader,
        target_setter,
        observer,
        observer_setter=None,
    ):
        self.position_reader = position_reader
        self.target_setter = target_setter
        self.observer = observer
        self.observer_setter = observer_setter
        self.target_ra = None
        self.target_dec = None

    def execute(self, command):
        if command == "GR":
            ra_degrees, _ = self.position_reader()
            return format_ra(ra_degrees)
        if command == "GD":
            _, dec_degrees = self.position_reader()
            return format_dec(dec_degrees)

        if command.startswith("Sr"):
            try:
                self.target_ra = parse_ra(command[2:])
            except ValueError:
                return "0"
            return "1"
        if command.startswith("Sd"):
            try:
                self.target_dec = parse_dec(command[2:])
            except ValueError:
                return "0"
            return "1"
        if command == "MS":
            if self.target_ra is None or self.target_dec is None:
                return "1"
            self.target_setter(self.target_ra, self.target_dec)
            return "0"

        if command == "GVP":
            return f"{PRODUCT_NAME}#"
        if command == "GVN":
            return f"{FIRMWARE_VERSION}#"
        if command == "GVD":
            return "09/01/26#"
        if command == "GVT":
            return "00:00:00#"
        if command == "GC":
            return datetime.now().strftime("%m/%d/%y#")
        if command == "GL":
            return datetime.now().strftime("%H:%M:%S#")
        if command == "GG":
            utc_offset = datetime.now().astimezone().utcoffset()
            offset_hours = utc_offset.total_seconds() / 3600.0
            return f"{-offset_hours:+05.1f}#"
        if command == "Gt":
            return format_site_angle(self.observer[0], 2)
        if command == "Gg":
            # LX200 uses west-positive longitude, unlike our configuration.
            return format_site_longitude(self.observer[1])
        if command.startswith("St"):
            try:
                latitude = parse_dec(command[2:])
            except ValueError:
                return "0"
            self.update_observer(latitude, self.observer[1])
            return "1"
        if command.startswith("Sg"):
            try:
                west_positive_longitude = parse_longitude(command[2:])
            except ValueError:
                return "0"
            longitude = (-west_positive_longitude + 180.0) % 360.0 - 180.0
            self.update_observer(self.observer[0], longitude)
            return "1"
        if command.startswith(("SG", "SL")):
            # The Raspberry Pi already maintains its own clock and timezone.
            return "1"
        if command.startswith("SC"):
            # LX200 date setters return a flag followed by two status strings.
            return "1Updating planetary data#                              #"
        if command == "GW":
            return "AT2#"
        if command == "D":
            return "#"
        if command in ("Q", "Qn", "Qs", "Qe", "Qw"):
            return ""

        return ""

    def update_observer(self, latitude, longitude):
        self.observer = (latitude, longitude)
        if self.observer_setter is not None:
            self.observer_setter(self.observer)
