import os
from typing import List

import nekoton as nt

import os
from typing import List
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# get list of accounts from keys file
def get_accounts(file: str, transport: nt.Transport) -> List[nt.contracts.EverWallet]:
    # check if file exists
    if not os.path.exists(file):
        logger.error(f"File {file} with keys not found")
        exit(1)

    try:
        with open(file) as f:
            keys = f.readlines()
            keys = [key.strip().split(',') for key in keys]
            (keys, public_keys, addresses) = list(zip(*keys))
    except Exception as e:
        logger.error(f"Error while reading keys file: {e}")
        exit(1)

    logger.info(f"Read {len(keys)} accounts from file {file}")
    keypairs = [nt.KeyPair(bytes.fromhex(key)) for key in keys]

    return [nt.contracts.EverWallet(transport=transport, keypair=keypair) for keypair in keypairs]
