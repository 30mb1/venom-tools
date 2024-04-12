import argparse
import os
import nekoton as nt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


parser = argparse.ArgumentParser()
parser.add_argument("-n", "--number", type=int, default=10, help="Number of keys to generate")
parser.add_argument("-f", "--file", type=str, default='keys.txt', help="Filename with account keys")
args = parser.parse_args()

os.makedirs('archive_keys', exist_ok=True)
# get names of all files in 'archive' dir
files = os.listdir('archive_keys')
# all files in 'archive' dir have xxx.N format
# get highest N through all files
numbers = [int(f.split('.')[2]) for f in files if f.split('.')[0] == 'keys']
highest = max(numbers) if numbers else 0

filename = args.file
# if keys.txt file exists in current dir, move it to archive
if os.path.exists(filename):
    os.rename(filename, f'archive_keys/{filename}.{highest+1}')
# log
logger.info(f"Archived keys.txt to archive_keys/{filename}.{highest+1}")

# get number of keys to generate from parser and dump to text file
# in format 'key,address' for every line
with open(filename, 'w') as f:
    for i in range(args.number):
        keypair = nt.KeyPair.generate()
        addr = nt.contracts.EverWallet.compute_address(keypair.public_key)
        # convert bytes to hex string
        f.write(f"{keypair.secret_key.hex()},{keypair.public_key.encode('hex')},{addr}\n")
        logger.info(f"Key {i+1} generated, public key: {keypair.public_key.encode('hex')}")
logger.info(f"Generated {args.number} keys and dumped to keys.txt")
