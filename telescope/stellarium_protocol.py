import struct
import time


POSITION_MESSAGE = 0
POSITION_MESSAGE_LENGTH = 24
GOTO_MESSAGE_LENGTH = 20
FULL_CIRCLE = 1 << 32
QUARTER_CIRCLE = 1 << 30


def encode_ra(ra_degrees):
    return round((ra_degrees % 360.0) / 360.0 * FULL_CIRCLE) % FULL_CIRCLE


def encode_dec(dec_degrees):
    dec_degrees = max(-90.0, min(90.0, dec_degrees))
    return round(dec_degrees / 90.0 * QUARTER_CIRCLE)


def decode_ra(encoded_ra):
    return encoded_ra / FULL_CIRCLE * 360.0


def decode_dec(encoded_dec):
    return encoded_dec / QUARTER_CIRCLE * 90.0


def current_position_message(ra_degrees, dec_degrees, timestamp_us=None):
    if timestamp_us is None:
        timestamp_us = time.time_ns() // 1_000

    return struct.pack(
        "<HHQIii",
        POSITION_MESSAGE_LENGTH,
        POSITION_MESSAGE,
        timestamp_us,
        encode_ra(ra_degrees),
        encode_dec(dec_degrees),
        0,
    )


def decode_goto_message(message):
    if len(message) != GOTO_MESSAGE_LENGTH:
        return None

    length, message_type, _, encoded_ra, encoded_dec = struct.unpack(
        "<HHQIi", message
    )
    if length != GOTO_MESSAGE_LENGTH or message_type != POSITION_MESSAGE:
        return None

    return decode_ra(encoded_ra), decode_dec(encoded_dec)
