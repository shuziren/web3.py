
from cytoolz import (
    curry,
)


def is_ens_name(value):
    if isinstance(value, bytes):
        value = value.decode('utf-8')
    if not isinstance(value, str):
        return False
    return value.endswith('.eth')


def validate_name_has_address(ens, name):
    addr = ens.address(name)
    if addr:
        return addr
    else:
        raise ValueError("Could not find address for name %r" % name)


@curry
def abi_ens_resolver(ens, abi_type, val):
    if abi_type == 'address' and is_ens_name(val):
        return (abi_type, validate_name_has_address(ens, val))
    else:
        return (abi_type, val)
