# venom-tools
Set of tools for venom 2024 tokenforge hackaton

# Setup
```bash
pip install -r requirements.txt
```

# Scripts
## Generate keys from seed phrase
```bash
python gen_keys_from_seed.py -n 50 -f keys_filename.txt
```

## Generate random accounts
```bash
python gen_random_accounts.py -n 50 -f keys_filename.txt
```

## Transfer venom native token
```bash
python transfer_venom.py
```

## Trade native venom to token
```bash
python trade_venom_to_token.py
```

## Trade token to native venom
```bash
python trade_token_to_venom.py
```