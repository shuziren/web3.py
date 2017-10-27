
import codecs
import functools

from eth_abi.abi import (
    process_type,
)

from eth_utils import (
    to_checksum_address,
)

from web3.utils.encoding import (
    hexstr_if_str,
    text_if_str,
    to_bytes,
    to_hex,
)


def implicitly_identity(to_wrap):
    @functools.wraps(to_wrap)
    def wrapper(abi_type, data):
        modified = to_wrap(abi_type, data)
        if modified is None:
            return abi_type, data
        else:
            return modified
    return wrapper


@implicitly_identity
def addresses_checksummed(abi_type, data):
    if abi_type == 'address':
        return abi_type, to_checksum_address(data)


@implicitly_identity
def decode_abi_strings(abi_type, data):
    if abi_type == 'string':
        return abi_type, codecs.decode(data, 'utf8', 'backslashreplace')


@implicitly_identity
def abi_bytes_to_hex(abi_type, data):
    base, sub, arrlist = process_type(abi_type)
    if base == 'bytes' and not arrlist:
        bytes_data = hexstr_if_str(to_bytes, data)
        if not sub:
            return abi_type, to_hex(bytes_data)
        else:
            num_bytes = int(sub)
            if len(bytes_data) <= num_bytes:
                padded = bytes_data.ljust(num_bytes, b'\0')
                return abi_type, to_hex(padded)
            else:
                raise ValueError(
                    "This value was expected to be at most %d bytes, but instead was %d: %r" % (
                        (num_bytes, len(bytes_data), data)
                    )
                )


@implicitly_identity
def abi_int_to_hex(abi_type, data):
    base, _sub, arrlist = process_type(abi_type)
    if base == 'uint' and not arrlist:
        return abi_type, hexstr_if_str(to_hex, data)


@implicitly_identity
def abi_string_to_hex(abi_type, data):
    if abi_type == 'string':
        return abi_type, text_if_str(to_hex, data)


@implicitly_identity
def hexstrs_to_bytes(abi_type, data):
    base, sub, arrlist = process_type(abi_type)
    if base in {'string', 'bytes'}:
        return abi_type, hexstr_if_str(to_bytes, data)


BASE_RETURN_NORMALIZERS = [
    addresses_checksummed,
    decode_abi_strings,
]
