import asyncio
import logging
import random

import nekoton as nt

from utils import get_swap_payload, WVENOM_ADDR, get_token_balance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# source account private key (just random acc)
PRIVATE_KEY = '9f2f8f3472fffba608710f5bbbd4d260ee5f771c7a20fe3be73a1ae603801d36'

# destination account address, USDT
TO_TOKEN = nt.Address('0:8a4ed4483500caf2d4bb4b56c84df41009cc3d0ed6a9de05d853e26a30faeced')

# 0.1 venom
TRADE_AMOUNT = nt.Tokens('0.1')

async def main():
    transport = nt.JrpcTransport(endpoint="https://jrpc.venom.foundation")
    await transport.check_connection()

    keypair = nt.KeyPair(secret=bytes.fromhex(PRIVATE_KEY))
    wallet = nt.contracts.EverWallet(transport=transport, keypair=keypair)

    # get account venom balance
    state = await transport.get_account_state(wallet.address)
    venom_balance = state.balance

    call_id = random.randint(0, 2**32)
    tx_data = get_swap_payload(
        call_id,
        WVENOM_ADDR,
        TO_TOKEN,
        int(TRADE_AMOUNT),
        wallet.address,
        int(venom_balance),
        0
    )

    tx = await wallet.send(**tx_data)
    logger.info(f'Account {wallet.address} sent tx: {tx.hash.hex()}')

    trace = transport.trace_transaction(tx)
    await trace.wait()
    await trace.close()
    logger.info(f"Transaction finalized")

    # get token balance
    token_balance = await get_token_balance(wallet.address, TO_TOKEN, transport)
    logger.info(f"Account token balance: {token_balance}")

asyncio.run(main())
