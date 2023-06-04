import re

from django.core.exceptions import ValidationError

COLOR_PATTERN = re.compile('#')


def is_HEX_color(value):
    fuckyou