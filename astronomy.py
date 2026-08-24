import math
from datetime import datetime, timezone


J2000_JULIAN_DATE = 2451545.0
UNIX_EPOCH_JULIAN_DATE = 2440587.5
DAYS_PER_JULIAN_CENTURY = 36525.0


def julian_date(moment=None):
    if moment is None:
        moment = datetime.now(timezone.utc)
    if moment.tzinfo is None:
        raise ValueError("The datetime must include a timezone.")
    return moment.timestamp() / 86400.0 + UNIX_EPOCH_JULIAN_DATE


def precess_j2000_to_date(ra_degrees, dec_degrees, target_julian_date):
    centuries = (
        target_julian_date - J2000_JULIAN_DATE
    ) / DAYS_PER_JULIAN_CENTURY

    zeta = math.radians(
        (
            2306.2181 * centuries
            + 0.30188 * centuries**2
            + 0.017998 * centuries**3
        )
        / 3600.0
    )
    z = math.radians(
        (
            2306.2181 * centuries
            + 1.09468 * centuries**2
            + 0.018203 * centuries**3
        )
        / 3600.0
    )
    theta = math.radians(
        (
            2004.3109 * centuries
            - 0.42665 * centuries**2
            - 0.041833 * centuries**3
        )
        / 3600.0
    )

    ra = math.radians(ra_degrees)
    dec = math.radians(dec_degrees)
    a = math.cos(dec) * math.sin(ra + zeta)
    b = (
        math.cos(theta) * math.cos(dec) * math.cos(ra + zeta)
        - math.sin(theta) * math.sin(dec)
    )
    c = (
        math.sin(theta) * math.cos(dec) * math.cos(ra + zeta)
        + math.cos(theta) * math.sin(dec)
    )

    ra_of_date = math.degrees(math.atan2(a, b) + z) % 360.0
    dec_of_date = math.degrees(math.asin(max(-1.0, min(1.0, c))))
    return ra_of_date, dec_of_date


def precess_date_to_j2000(ra_degrees, dec_degrees, source_julian_date):
    centuries = (
        source_julian_date - J2000_JULIAN_DATE
    ) / DAYS_PER_JULIAN_CENTURY
    zeta = math.radians(
        (
            2306.2181 * centuries
            + 0.30188 * centuries**2
            + 0.017998 * centuries**3
        )
        / 3600.0
    )
    z = math.radians(
        (
            2306.2181 * centuries
            + 1.09468 * centuries**2
            + 0.018203 * centuries**3
        )
        / 3600.0
    )
    theta = math.radians(
        (
            2004.3109 * centuries
            - 0.42665 * centuries**2
            - 0.041833 * centuries**3
        )
        / 3600.0
    )

    ra = math.radians(ra_degrees)
    dec = math.radians(dec_degrees)
    a = math.cos(dec) * math.sin(ra - z)
    b = math.cos(dec) * math.cos(ra - z)
    c = math.sin(dec)

    x = math.cos(theta) * b + math.sin(theta) * c
    y = a
    z_axis = -math.sin(theta) * b + math.cos(theta) * c

    ra_j2000 = math.degrees(math.atan2(y, x) - zeta) % 360.0
    dec_j2000 = math.degrees(
        math.asin(max(-1.0, min(1.0, z_axis)))
    )
    return ra_j2000, dec_j2000


def greenwich_mean_sidereal_time(target_julian_date):
    centuries = (
        target_julian_date - J2000_JULIAN_DATE
    ) / DAYS_PER_JULIAN_CENTURY
    return (
        280.46061837
        + 360.98564736629 * (target_julian_date - J2000_JULIAN_DATE)
        + 0.000387933 * centuries**2
        - centuries**3 / 38710000.0
    ) % 360.0


def j2000_to_horizontal(
    ra_degrees,
    dec_degrees,
    latitude_degrees,
    longitude_degrees,
    moment=None,
):
    target_julian_date = julian_date(moment)
    ra_of_date, dec_of_date = precess_j2000_to_date(
        ra_degrees,
        dec_degrees,
        target_julian_date,
    )

    local_sidereal_time = (
        greenwich_mean_sidereal_time(target_julian_date) + longitude_degrees
    ) % 360.0
    hour_angle = math.radians((local_sidereal_time - ra_of_date) % 360.0)
    dec = math.radians(dec_of_date)
    latitude = math.radians(latitude_degrees)

    altitude = math.asin(
        math.sin(latitude) * math.sin(dec)
        + math.cos(latitude) * math.cos(dec) * math.cos(hour_angle)
    )
    azimuth = math.atan2(
        -math.sin(hour_angle) * math.cos(dec),
        math.sin(dec) * math.cos(latitude)
        - math.cos(dec) * math.sin(latitude) * math.cos(hour_angle),
    )

    return math.degrees(azimuth) % 360.0, math.degrees(altitude)


def horizontal_to_j2000(
    azimuth_degrees,
    altitude_degrees,
    latitude_degrees,
    longitude_degrees,
    moment=None,
):
    target_julian_date = julian_date(moment)
    azimuth = math.radians(azimuth_degrees)
    altitude = math.radians(altitude_degrees)
    latitude = math.radians(latitude_degrees)

    dec = math.asin(
        math.sin(altitude) * math.sin(latitude)
        + math.cos(altitude) * math.cos(latitude) * math.cos(azimuth)
    )
    hour_angle = math.atan2(
        -math.sin(azimuth) * math.cos(altitude),
        math.sin(altitude) * math.cos(latitude)
        - math.cos(altitude) * math.sin(latitude) * math.cos(azimuth),
    )
    local_sidereal_time = (
        greenwich_mean_sidereal_time(target_julian_date) + longitude_degrees
    ) % 360.0
    ra_of_date = (local_sidereal_time - math.degrees(hour_angle)) % 360.0
    dec_of_date = math.degrees(dec)

    return precess_date_to_j2000(
        ra_of_date,
        dec_of_date,
        target_julian_date,
    )
