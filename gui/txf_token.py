#!/usr/bin/env python3
"""TXF Token - Taxpayer OSINT Ledger System"""
import os
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path

DATA_DIR = Path.home() / "OsintNeoAi" / "data"
LEDGER_DIR = DATA_DIR / "ledger"

class TXFToken:
    """Taxpayer-funded OSINT ledger token system"""
    
    def __init__(self):
        self.ledger = []
        self.token_name = "TXF"
        self.token_symbol = "TXF"
        self.total_supply = 0
        self.balances = {}
        self.transactions = []
        
    def create_genesis_block(self):
        """Create the genesis block for the TXF ledger"""
        genesis = {
            "index": 0,
            "timestamp": datetime.now().isoformat(),
            "transactions": [],
            "previous_hash": "0" * 64,
            "hash": self._hash_block({
                "index": 0,
                "timestamp": datetime.now().isoformat(),
                "data": "Genesis Block - TXF Token OSINT Ledger",
                "previous_hash": "0" * 64,
            }),
            "data": "TXF Token Genesis - Taxpayer OSINT Ledger Initialized",
        }
        self.ledger.append(genesis)
        return genesis
        
    def mint_tokens(self, account, amount, reason):
        """Mint new TXF tokens for taxpayer-funded OSINT work"""
        tx = {
            "type": "MINT",
            "from": "GENESIS",
            "to": account,
            "amount": amount,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "tx_hash": self._hash_tx(account, amount, reason),
        }
        
        self.transactions.append(tx)
        self.balances[account] = self.balances.get(account, 0) + amount
        self.total_supply += amount
        
        block = self._create_block([tx])
        self.ledger.append(block)
        
        return tx
        
    def transfer(self, from_account, to_account, amount, memo=""):
        """Transfer TXF tokens between accounts"""
        if self.balances.get(from_account, 0) < amount:
            return {"error": "Insufficient balance"}
            
        tx = {
            "type": "TRANSFER",
            "from": from_account,
            "to": to_account,
            "amount": amount,
            "memo": memo,
            "timestamp": datetime.now().isoformat(),
            "tx_hash": self._hash_tx(from_account, to_account, amount),
        }
        
        self.transactions.append(tx)
        self.balances[from_account] -= amount
        self.balances[to_account] = self.balances.get(to_account, 0) + amount
        
        block = self._create_block([tx])
        self.ledger.append(block)
        
        return tx
        
    def log_osint_query(self, query_type, target, operator, cost=0):
        """Log an OSINT query to the ledger"""
        tx = {
            "type": "OSINT_QUERY",
            "query_type": query_type,
            "target": target,
            "operator": operator,
            "cost": cost,
            "timestamp": datetime.now().isoformat(),
            "tx_hash": self._hash_tx(query_type, target, operator),
        }
        
        self.transactions.append(tx)
        block = self._create_block([tx])
        self.ledger.append(block)
        
        return tx
        
    def log_data_access(self, data_source, record_count, accessor):
        """Log data access to the ledger"""
        tx = {
            "type": "DATA_ACCESS",
            "data_source": data_source,
            "record_count": record_count,
            "accessor": accessor,
            "timestamp": datetime.now().isoformat(),
            "tx_hash": self._hash_tx(data_source, record_count, accessor),
        }
        
        self.transactions.append(tx)
        block = self._create_block([tx])
        self.ledger.append(block)
        
        return tx
        
    def log_taxpayer_fund(self, amount, source, purpose):
        """Log taxpayer fund allocation"""
        tx = {
            "type": "TAXPAYER_FUND",
            "amount": amount,
            "source": source,
            "purpose": purpose,
            "timestamp": datetime.now().isoformat(),
            "tx_hash": self._hash_tx(amount, source, purpose),
        }
        
        self.transactions.append(tx)
        self.balances["TAXPAYER_FUND"] = self.balances.get("TAXPAYER_FUND", 0) + amount
        self.total_supply += amount
        
        block = self._create_block([tx])
        self.ledger.append(block)
        
        return tx
        
    def get_balance(self, account):
        """Get balance of an account"""
        return self.balances.get(account, 0)
        
    def get_transaction_history(self, account=None, tx_type=None):
        """Get transaction history"""
        txs = self.transactions
        if account:
            txs = [t for t in txs if t.get("from") == account or t.get("to") == account]
        if tx_type:
            txs = [t for t in txs if t.get("type") == tx_type]
        return txs
        
    def get_ledger_stats(self):
        """Get ledger statistics"""
        return {
            "total_blocks": len(self.ledger),
            "total_transactions": len(self.transactions),
            "total_supply": self.total_supply,
            "balances": self.balances,
            "token_name": self.token_name,
            "token_symbol": self.token_symbol,
        }
        
    def export_ledger(self):
        """Export full ledger"""
        return {
            "token": {
                "name": self.token_name,
                "symbol": self.token_symbol,
                "total_supply": self.total_supply,
            },
            "blocks": self.ledger,
            "transactions": self.transactions,
            "balances": self.balances,
            "stats": self.get_ledger_stats(),
        }
        
    def export_html(self):
        """Export ledger as HTML"""
        stats = self.get_ledger_stats()
        
        html = '<!DOCTYPE html>\n'
        html += '<html>\n<head>\n'
        html += '<title>TXF Token - Taxpayer OSINT Ledger</title>\n'
        html += '<style>\n'
        html += '* { margin:0; padding:0; box-sizing:border-box; }\n'
        html += "body { font-family:'Courier New',monospace; background:#0a0a0a; color:#00ff41; }\n"
        html += '.header { background:#111; padding:30px; border-bottom:2px solid #00ff41; }\n'
        html += '.header h1 { font-size:36px; }\n'
        html += '.header p { color:#888; margin-top:5px; }\n'
        html += '.container { max-width:1200px; margin:0 auto; padding:20px; }\n'
        html += ".stats { display:grid; grid-template-columns:repeat(4,1fr); gap:15px; margin:20px 0; }\n"
        html += '.stat-box { background:#111; border:1px solid #333; padding:15px; text-align:center; }\n'
        html += '.stat-box .number { font-size:28px; font-weight:bold; color:#00ff41; }\n'
        html += '.stat-box .label { font-size:11px; color:#888; margin-top:5px; }\n'
        html += '.ledger { background:#111; border:1px solid #333; padding:20px; margin-top:20px; }\n'
        html += '.ledger h2 { color:#00ff41; margin-bottom:15px; }\n'
        html += '.block { border:1px solid #333; margin:10px 0; padding:15px; }\n'
        html += '.block-header { color:#00ff41; font-weight:bold; margin-bottom:10px; }\n'
        html += '.tx { border-bottom:1px solid #222; padding:8px 0; font-size:12px; }\n'
        html += '.tx-type { color:#00ff41; font-weight:bold; }\n'
        html += '.tx-hash { color:#666; }\n'
        html += '.balances { background:#111; border:1px solid #333; padding:20px; margin-top:20px; }\n'
        html += '.balances h2 { color:#00ff41; margin-bottom:15px; }\n'
        html += '.balance-item { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #222; }\n'
        html += '.balance-address { color:#888; }\n'
        html += '.balance-amount { color:#00ff41; font-weight:bold; }\n'
        html += '</style>\n</head>\n<body>\n'
        
        html += '<div class="header">\n'
        html += '<h1>&#127981; TXF TOKEN</h1>\n'
        html += '<p>Taxpayer OSINT Ledger | ' + stats['token_symbol'] + ' | Block #' + str(stats['total_blocks']) + '</p>\n'
        html += '</div>\n'
        
        html += '<div class="container">\n'
        html += '<div class="stats">\n'
        html += '<div class="stat-box">\n<div class="number">' + str(stats['total_blocks']) + '</div>\n<div class="label">Total Blocks</div>\n</div>\n'
        html += '<div class="stat-box">\n<div class="number">' + str(stats['total_transactions']) + '</div>\n<div class="label">Transactions</div>\n</div>\n'
        html += '<div class="stat-box">\n<div class="number">' + str(stats['total_supply']) + '</div>\n<div class="label">Total Supply</div>\n</div>\n'
        html += '<div class="stat-box">\n<div class="number">' + str(len(stats['balances'])) + '</div>\n<div class="label">Accounts</div>\n</div>\n'
        html += '</div>\n'
        
        html += '<div class="balances">\n<h2>Account Balances</h2>\n'
        for addr, bal in sorted(stats['balances'].items(), key=lambda x: -x[1]):
            html += '<div class="balance-item">\n'
            html += '<div class="balance-address">' + addr + '</div>\n'
            html += '<div class="balance-amount">' + str(bal) + ' ' + stats['token_symbol'] + '</div>\n'
            html += '</div>\n'
        html += '</div>\n'
        
        html += '<div class="ledger">\n<h2>Ledger Blocks</h2>\n'
        for block in reversed(self.ledger[-20:]):
            html += '<div class="block">\n'
            html += '<div class="block-header">Block #' + str(block['index']) + ' | ' + block['timestamp'][:19] + '</div>\n'
            html += '<div class="tx-hash">Hash: ' + block['hash'][:32] + '...</div>\n'
            for tx in block.get('transactions', []):
                html += '<div class="tx">\n'
                html += '<span class="tx-type">[' + tx.get('type', 'GENESIS') + ']</span> '
                html += json.dumps({k:v for k,v in tx.items() if k != 'tx_hash'}, default=str)[:100]
                html += '</div>\n'
            html += '</div>\n'
        html += '</div>\n'
        
        html += '</div>\n</body>\n</html>'
        return html
        
    def _create_block(self, transactions):
        """Create a new block"""
        previous_block = self.ledger[-1] if self.ledger else None
        previous_hash = previous_block["hash"] if previous_block else "0" * 64
        
        block = {
            "index": len(self.ledger),
            "timestamp": datetime.now().isoformat(),
            "transactions": transactions,
            "previous_hash": previous_hash,
        }
        block["hash"] = self._hash_block(block)
        
        return block
        
    def _hash_block(self, block):
        """Hash a block"""
        block_string = json.dumps(block, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()
        
    def _hash_tx(self, *args):
        """Hash a transaction"""
        tx_string = json.dumps([str(a) for a in args], sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()[:16]


def load_or_init_ledger():
    """Load existing ledger or initialize new one"""
    ledger_path = LEDGER_DIR / "txf_ledger.json"
    if ledger_path.exists():
        with open(ledger_path) as f:
            return json.load(f)
    return init_ledger()


def init_ledger():
    """Initialize the TXF ledger"""
    txf = TXFToken()
    txf.create_genesis_block()
    
    txf.log_taxpayer_fund(300, "Google Cloud Trial", "Free trial credits for OSINT platform")
    txf.mint_tokens("OSINT_OPERATOR", 100, "Initial operator tokens")
    txf.log_osint_query("EMAIL_RECON", "test@example.com", "system")
    txf.log_data_access("HB_Parcels", 50000, "system")
    
    os.makedirs(LEDGER_DIR, exist_ok=True)
    
    ledger_data = txf.export_ledger()
    with open(LEDGER_DIR / "txf_ledger.json", "w") as f:
        json.dump(ledger_data, f, indent=2)
        
    html = txf.export_html()
    with open(LEDGER_DIR / "txf_ledger.html", "w") as f:
        f.write(html)
        
    return ledger_data


if __name__ == "__main__":
    data = init_ledger()
    print(f"TXF Ledger initialized")
    print(f"Blocks: {data['stats']['total_blocks']}")
    print(f"Transactions: {data['stats']['total_transactions']}")
    print(f"Supply: {data['stats']['total_supply']}")
