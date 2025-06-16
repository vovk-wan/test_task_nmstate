import re


def ipv4_validator(value):
    pattern = re.compile(
        r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    )
    return bool(pattern.match(value))


def bridge_name_validator(value):
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_-]{0,14}$", value))


def nullable_validator(value):
    return True


MAPPER_VALIDATORS = {
    "text": nullable_validator,
    "bool": nullable_validator,
    "state_bool": nullable_validator,
    "ipv4address": ipv4_validator,
    "apply_button": nullable_validator,
    "bridge_name": bridge_name_validator,
}


def get_validator(name):
    return MAPPER_VALIDATORS.get(name, nullable_validator)
