"""
validators.py
---------------
The module contains validators for the types that are used in the application and a function for obtaining a validator
by field type.
"""

import re

from typing import Any, Callable


def ipv4_validator(value: str) -> bool:
    """
    IPv4 address checking function.

    Args:
        value: str - string with IPv4 address.

    Returns: bool - True if the address is valid, False otherwise.
    """

    pattern = re.compile(r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    return bool(pattern.match(value))


def bridge_name_validator(value: str) -> bool:
    """
    Function to check LinuxBridge name.

    Args:
        value: str - string with bridge name.

    Returns: bool - True if the name is valid, False otherwise.
    """

    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_-]{0,14}$", value))


def nullable_validator(value: Any) -> True:
    """
    Function stub, always returns true.

    Args:
        value: Any

    Returns: bool - always True
    """

    return True


MAPPER_VALIDATORS = {
    "text": nullable_validator,
    "bool": nullable_validator,
    "state_bool": nullable_validator,
    "ipv4address": ipv4_validator,
    "apply_button": nullable_validator,
    "bridge_name": bridge_name_validator,
}


def get_validator(field_type: str) -> Callable:
    """
    The function to get a validator by value type.

    Args:
        field_type: str - string with value type

    Returns: Callable - validator function
    """

    return MAPPER_VALIDATORS.get(field_type, nullable_validator)
