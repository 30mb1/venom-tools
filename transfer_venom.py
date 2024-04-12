import nekoton as nt
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# source account private key (just random acc)
PRIVATE_KEY = '85b5ce964d7522e99ee8f4f773c59bbc48e0450d5c359868fbc56cf2c512975a'

# destination account address
DESTINATION = nt.Address('0:0000000000000000000000000000000000000000000000000000000000000001')

# 0.1 venom
VALUE = nt.Tokens('0.1')

async def main():
    transport = nt.JrpcTransport(endpoint="https://jrpc.venom.foundation")
    await transport.check_connection()

    keypair = nt.KeyPair(secret=bytes.fromhex(PRIVATE_KEY))
    wallet = nt.contracts.EverWallet(transport=transport, keypair=keypair)

    tx = await wallet.send(dst=DESTINATION, value=VALUE, bounce=False, payload=nt.Cell())
    logger.info(f'Account {wallet.address} sent tx: {tx.hash.hex()}')
    trace = transport.trace_transaction(tx)
    await trace.wait()
    await trace.close()

    logger.info(f"Transaction finalized")


asyncio.run(main())
