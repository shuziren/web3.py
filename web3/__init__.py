from __future__ import absolute_import

import pkg_resources


from web3.main import Web3  # NOQA
from web3.providers.rpc import (  # NOQA
    RPCProvider,
    TestRPCProvider,
)
from web3.providers.ipc import IPCProvider  # NOQA

__version__ = pkg_resources.get_distribution("web3").version

__all__ = [
    "__version__",
    "Web3",
    "RPCProvider",
    "TestRPCProvider",
    "IPCProvider",
]
