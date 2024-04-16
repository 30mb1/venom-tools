import logging
import os
from typing import List

import nekoton as nt
import requests
import asyncio

logger = logging.getLogger()
logger.setLevel(logging.INFO)



# read token_root.abi.json file
def read_abi(file: str) -> str:
    with open(file) as f:
        return f.read()


# get token root abi
def get_token_root_abi() -> str:
    return read_abi('tvm_abi/token_root.abi.json')


# get token wallet abi
def get_token_wallet_abi() -> str:
    return read_abi('tvm_abi/token_wallet.abi.json')


token_abi = nt.ContractAbi(get_token_root_abi())
token_wallet_abi = nt.ContractAbi(get_token_wallet_abi())


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

WVENOM_ADDR = '0:77d36848bb159fa485628bc38dc37eadb74befa514395e09910f601b841f749e'

def get_swap_payload(
    id: int,
    from_currency: nt.Address,
    to_currency: nt.Address,
    amount: int,
    account: nt.Address,
    native_balance: int,
    token_balance: int,
    slippage: float = 0.99
):
    native_info = 'spendonlynative' if str(from_currency) == WVENOM_ADDR else 'receivenative'
    data = {
        "crossPairInput": {
            "amount": str(amount),
            "deep": 2,
            "direction": 'expectedexchange',
            "fromCurrencyAddress": str(from_currency),
            "toCurrencyAddress": str(to_currency),
            "slippage": str(slippage),
            "minTvl": "0",
            "whiteListCurrencies": [str(from_currency), str(to_currency)]
        },
        "id": id,
        "nativeBalance": str(native_balance),
        "nativeInfo": native_info,
        "recipient": str(account),
        "tokenBalance": str(token_balance)
    }
    res = requests.post('https://api.web3.world/v2/pools/cross_swap_payload', json=data).json()
    return {
        'dst': nt.Address(res['walletOfDestination']),
        'payload': nt.Cell.decode(res['payload']),
        'value': nt.Tokens.from_nano(int(res['gas'])),
        'bounce': True
    }

async def get_token_wallet_addr(address: nt.Address, token_address: nt.Address, transport: nt.Transport) -> nt.Address:
    function_abi = token_abi.get_function('walletOf')
    token_state = await transport.get_account_state(token_address)
    res = function_abi.call(token_state, input={'answerId': 0, 'walletOwner': address})
    return res.output['value0']

async def get_token_balance(address: nt.Address, token: nt.Address, transport: nt.Transport) -> int:
    token_wallet_addr = await get_token_wallet_addr(address, token, transport)
    token_wallet_state = await transport.get_account_state(token_wallet_addr)
    if not token_wallet_state:
        return 0
    function_abi = token_wallet_abi.get_function('balance')
    res = function_abi.call(token_wallet_state, input={'answerId': 0})
    return int(res.output['value0'])
