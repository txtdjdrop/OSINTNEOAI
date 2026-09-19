#!/usr/bin/env python3
"""TDD Tests for OSINT Neo AI Features"""
import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))


class TestOSINTNewspaper:
    """Tests for the self-populating newspaper"""
    
    def setup(self):
        from newspaper import OSINTNewspaper
        self.newspaper = OSINTNewspaper()
        
    def test_newspaper_initializes_empty(self):
        """Newspaper starts with empty articles"""
        assert self.newspaper.articles == []
        assert self.newspaper.ledger == []
        
    def test_generate_title_from_filename(self):
        """Title generated from filename"""
        from pathlib import Path
        filepath = Path("test_article.md")
        content = "# Test Article"
        title = self.newspaper._generate_title(filepath, content)
        assert title == "Test Article"
        
    def test_generate_title_truncates_long_names(self):
        """Long filenames are truncated"""
        from pathlib import Path
        filepath = Path("a" * 100 + ".md")
        title = self.newspaper._generate_title(filepath, "")
        assert len(title) <= 60
        assert title.endswith("...")
        
    def test_generate_summary_from_content(self):
        """Summary extracted from content"""
        content = "Line one\nLine two\nLine three"
        summary = self.newspaper._generate_summary(content)
        assert "Line one" in summary
        assert "Line two" in summary
        
    def test_extract_hyperlinks(self):
        """Hyperlinks extracted from content"""
        content = "Visit https://example.com and http://test.org"
        links = self.newspaper._extract_hyperlinks(content)
        assert "https://example.com" in links
        assert "http://test.org" in links
        
    def test_extract_tags(self):
        """Tags extracted from content"""
        content = "This is about Huntington Beach and HBNC"
        tags = self.newspaper._extract_tags(content)
        assert "Huntington Beach" in tags
        assert "HBNC" in tags
        
    def test_generate_newspaper_returns_dict(self):
        """Newspaper generation returns valid dict"""
        result = self.newspaper.generate_newspaper()
        assert "generated_at" in result
        assert "total_articles" in result
        assert "articles" in result
        assert "stats" in result


class TestLegalSection:
    """Tests for the legal section"""
    
    def setup(self):
        from legal import LegalSection
        self.legal = LegalSection()
        
    def test_legal_initializes_empty(self):
        """Legal section starts empty"""
        assert self.legal.documents == []
        assert self.legal.cases == {}
        
    def test_classify_document_permit(self):
        """Permits classified correctly"""
        result = self.legal._classify_document("building_permit.json", ["permit"])
        assert result == "PERMIT"
        
    def test_classify_document_contract(self):
        """Contracts classified correctly"""
        result = self.legal._classify_document("service_contract.md", ["contract"])
        assert result == "CONTRACT"
        
    def test_classify_document_complaint(self):
        """Complaints classified correctly"""
        result = self.legal._classify_document("code_complaint.txt", ["complaint"])
        assert result == "COMPLAINT"
        
    def test_extract_legal_links(self):
        """Legal hyperlinks extracted"""
        content = "See https://legistar.com/city and https://huntingtonbeachca.gov/permits"
        links = self.legal._extract_legal_links(content)
        assert len(links) == 2
        
    def test_extract_references_file_number(self):
        """File numbers extracted"""
        content = "File #: 20-1799 approved by council"
        refs = self.legal._extract_references(content)
        assert "20-1799" in refs
        
    def test_extract_references_apn(self):
        """APN numbers extracted"""
        content = "Property APN: 167-472-08"
        refs = self.legal._extract_references(content)
        assert "167-472-08" in refs
        
    def test_generate_legal_index(self):
        """Legal index generation works"""
        result = self.legal.generate_legal_index()
        assert "generated_at" in result
        assert "total_documents" in result
        assert "categories" in result
        assert "documents" in result


class TestTXFToken:
    """Tests for the TXF token ledger system"""
    
    def setup(self):
        from txf_token import TXFToken
        self.txf = TXFToken()
        
    def test_txf_initializes_empty(self):
        """TXF starts empty"""
        assert self.txf.ledger == []
        assert self.txf.total_supply == 0
        assert self.txf.balances == {}
        
    def test_create_genesis_block(self):
        """Genesis block created"""
        genesis = self.txf.create_genesis_block()
        assert genesis["index"] == 0
        assert genesis["previous_hash"] == "0" * 64
        assert len(self.txf.ledger) == 1
        
    def test_mint_tokens(self):
        """Tokens can be minted"""
        self.txf.create_genesis_block()
        tx = self.txf.mint_tokens("user1", 100, "test")
        assert tx["type"] == "MINT"
        assert tx["amount"] == 100
        assert self.txf.get_balance("user1") == 100
        assert self.txf.total_supply == 100
        
    def test_transfer_tokens(self):
        """Tokens can be transferred"""
        self.txf.create_genesis_block()
        self.txf.mint_tokens("user1", 100, "test")
        tx = self.txf.transfer("user1", "user2", 50)
        assert tx["type"] == "TRANSFER"
        assert self.txf.get_balance("user1") == 50
        assert self.txf.get_balance("user2") == 50
        
    def test_transfer_insufficient_balance(self):
        """Transfer fails with insufficient balance"""
        self.txf.create_genesis_block()
        self.txf.mint_tokens("user1", 10, "test")
        tx = self.txf.transfer("user1", "user2", 100)
        assert "error" in tx
        assert self.txf.get_balance("user1") == 10
        
    def test_log_osint_query(self):
        """OSINT queries logged to ledger"""
        self.txf.create_genesis_block()
        tx = self.txf.log_osint_query("EMAIL_RECON", "test@example.com", "operator")
        assert tx["type"] == "OSINT_QUERY"
        assert tx["query_type"] == "EMAIL_RECON"
        assert len(self.txf.transactions) == 1
        
    def test_log_data_access(self):
        """Data access logged to ledger"""
        self.txf.create_genesis_block()
        tx = self.txf.log_data_access("HB_Parcels", 50000, "operator")
        assert tx["type"] == "DATA_ACCESS"
        assert tx["record_count"] == 50000
        
    def test_log_taxpayer_fund(self):
        """Taxpayer funds logged"""
        self.txf.create_genesis_block()
        tx = self.txf.log_taxpayer_fund(300, "Google Cloud", "Trial credits")
        assert tx["type"] == "TAXPAYER_FUND"
        assert self.txf.get_balance("TAXPAYER_FUND") == 300
        assert self.txf.total_supply == 300
        
    def test_get_transaction_history(self):
        """Transaction history works"""
        self.txf.create_genesis_block()
        self.txf.mint_tokens("user1", 100, "test")
        self.txf.log_osint_query("EMAIL", "test@test.com", "op")
        
        all_txs = self.txf.get_transaction_history()
        assert len(all_txs) == 2
        
        user_txs = self.txf.get_transaction_history(account="user1")
        assert len(user_txs) == 1
        
    def test_get_ledger_stats(self):
        """Ledger stats correct"""
        self.txf.create_genesis_block()
        self.txf.mint_tokens("user1", 100, "test")
        
        stats = self.txf.get_ledger_stats()
        assert stats["total_blocks"] == 2
        assert stats["total_transactions"] == 1
        assert stats["total_supply"] == 100
        assert stats["balances"]["user1"] == 100
        
    def test_export_ledger(self):
        """Ledger exports correctly"""
        self.txf.create_genesis_block()
        self.txf.mint_tokens("user1", 100, "test")
        
        data = self.txf.export_ledger()
        assert "token" in data
        assert "blocks" in data
        assert "transactions" in data
        assert "balances" in data
        assert data["token"]["name"] == "TXF"
        
    def test_hash_consistency(self):
        """Hashing is consistent"""
        h1 = self.txf._hash_block({"test": "data"})
        h2 = self.txf._hash_block({"test": "data"})
        assert h1 == h2
        
    def test_hash_unique(self):
        """Different inputs produce different hashes"""
        h1 = self.txf._hash_block({"test": "data1"})
        h2 = self.txf._hash_block({"test": "data2"})
        assert h1 != h2


def run_all_tests():
    """Run all TDD tests"""
    test_classes = [TestOSINTNewspaper, TestLegalSection, TestTXFToken]
    total = 0
    passed = 0
    failed = 0
    errors = []
    
    for cls in test_classes:
        instance = cls()
        test_methods = [m for m in dir(instance) if m.startswith("test_")]
        
        for method_name in test_methods:
            total += 1
            try:
                instance.setup()
                method = getattr(instance, method_name)
                method()
                passed += 1
                print(f"  PASS: {cls.__name__}.{method_name}")
            except AssertionError as e:
                failed += 1
                errors.append((cls.__name__, method_name, str(e)))
                print(f"  FAIL: {cls.__name__}.{method_name}: {e}")
            except Exception as e:
                failed += 1
                errors.append((cls.__name__, method_name, str(e)))
                print(f"  ERROR: {cls.__name__}.{method_name}: {e}")
    
    print(f"\n{'='*50}")
    print(f"RESULTS: {passed}/{total} passed, {failed} failed")
    
    if errors:
        print("\nFAILURES:")
        for cls, method, err in errors:
            print(f"  {cls}.{method}: {err}")
            
    return failed == 0


if __name__ == "__main__":
    print("Running TDD Tests for OSINT Neo AI\n")
    success = run_all_tests()
    sys.exit(0 if success else 1)
