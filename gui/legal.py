#!/usr/bin/env python3
"""Legal Section - Growing database of legal documents with hyperlinks"""
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

DATA_DIR = Path.home() / "OsintNeoAi" / "data"
LEGAL_DIR = DATA_DIR / "legal"

class LegalSection:
    def __init__(self):
        self.documents = []
        self.cases = {}
        self.hyperlinks = {}
        
    def scan_legal_data(self):
        """Scan all OSINT data for legal documents"""
        legal_keywords = [
            "permit", "contract", "agreement", "ordinance", "resolution",
            "complaint", "lawsuit", "violation", "enforcement", "fine",
            "FOIA", "public records", "disclosure", "subpoena", "warrant",
            "deed", "easement", "zoning", "variance", "appeal",
        ]
        
        for root, dirs, files in os.walk(DATA_DIR):
            for f in files:
                if f.endswith(('.json', '.md', '.txt')):
                    filepath = Path(root) / f
                    self._process_legal_file(filepath, legal_keywords)
                    
    def _process_legal_file(self, filepath, keywords):
        """Process a file for legal content"""
        try:
            content = filepath.read_text(errors='ignore')
            content_lower = content.lower()
            
            found_keywords = [kw for kw in keywords if kw.lower() in content_lower]
            
            if found_keywords:
                doc = {
                    "id": hashlib.md5(str(filepath).encode()).hexdigest()[:12],
                    "file": filepath.name,
                    "path": str(filepath.relative_to(DATA_DIR)),
                    "type": self._classify_document(filepath.name, found_keywords),
                    "keywords": found_keywords,
                    "hyperlinks": self._extract_legal_links(content),
                    "references": self._extract_references(content),
                    "timestamp": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                }
                self.documents.append(doc)
                
                for kw in found_keywords:
                    if kw not in self.cases:
                        self.cases[kw] = []
                    self.cases[kw].append(doc["id"])
        except Exception:
            pass
            
    def _classify_document(self, filename, keywords):
        """Classify document type"""
        filename_lower = filename.lower()
        if "permit" in filename_lower:
            return "PERMIT"
        elif "contract" in filename_lower or "agreement" in filename_lower:
            return "CONTRACT"
        elif "complaint" in filename_lower:
            return "COMPLAINT"
        elif "ordinance" in filename_lower or "resolution" in filename_lower:
            return "ORDINANCE"
        elif "deed" in filename_lower or "easement" in filename_lower:
            return "DEED/EASEMENT"
        elif "foia" in filename_lower or "public" in filename_lower:
            return "PUBLIC RECORDS"
        else:
            return "LEGAL DOCUMENT"
            
    def _extract_legal_links(self, content):
        """Extract legal hyperlinks"""
        import re
        legal_domains = [
            "legistar.com", "huntingtonbeachca.gov", "ocgov.com",
            "courtlistener.com", "casetext.com", "law.justia.com",
            "leginfo.legislature.ca.gov", "aecdev.sccgov.org",
        ]
        urls = re.findall(r'https?://[^\s\)\"]+', content)
        return [u for u in urls if any(d in u for d in legal_domains)]
        
    def _extract_references(self, content):
        """Extract legal references"""
        import re
        refs = []
        patterns = [
            r'File\s*#?\s*:?\s*(\d{2}-\d{4})',
            r'Case\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'APN\s*:?\s*(\d{3}-\d{3}-\d{2,4})',
            r'Ordinance\s*#?\s*:?\s*(\d+)',
            r'Resolution\s*#?\s*:?\s*(\d+)',
        ]
        for p in patterns:
            refs.extend(re.findall(p, content))
        return list(set(refs))
        
    def generate_legal_index(self):
        """Generate legal index"""
        self.scan_legal_data()
        
        return {
            "generated_at": datetime.now().isoformat(),
            "total_documents": len(self.documents),
            "categories": self.cases,
            "documents": self.documents,
            "hyperlink_index": self._build_hyperlink_index(),
        }
        
    def _build_hyperlink_index(self):
        """Build index of all hyperlinks"""
        index = {}
        for doc in self.documents:
            for link in doc["hyperlinks"]:
                if link not in index:
                    index[link] = []
                index[link].append(doc["id"])
        return index
        
    def export_legal_html(self, index):
        """Export legal section as HTML"""
        html = """<!DOCTYPE html>
<html>
<head>
<title>OSINT Neo AI - Legal Section</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',sans-serif; background:#fafaf8; color:#1a1a1a; }
.header { background:#1a1a1a; color:#fff; padding:30px; }
.header h1 { font-size:36px; }
.header p { color:#888; margin-top:5px; }
.container { max-width:1200px; margin:0 auto; padding:20px; }
.stats { display:grid; grid-template-columns:repeat(4,1fr); gap:15px; margin:20px 0; }
.stat-box { background:#fff; border:1px solid #ddd; padding:15px; text-align:center; }
.stat-box .number { font-size:32px; font-weight:bold; color:#1a1a1a; }
.stat-box .label { font-size:12px; color:#888; margin-top:5px; }
.category { background:#fff; border:1px solid #ddd; margin:10px 0; }
.category-header { background:#f0f0f0; padding:10px 15px; cursor:pointer; display:flex; justify-content:space-between; }
.category-header:hover { background:#e8e8e8; }
.category-content { padding:15px; display:none; }
.category-content.active { display:block; }
.doc-card { background:#f8f8f8; border:1px solid #eee; padding:10px; margin:5px 0; }
.doc-card h4 { font-size:14px; margin-bottom:5px; }
.doc-card .meta { font-size:11px; color:#888; }
.doc-card .links { margin-top:5px; }
.doc-card .links a { color:#0066cc; font-size:11px; margin-right:8px; text-decoration:none; }
.hyperlink-section { background:#fff; border:1px solid #ddd; padding:20px; margin-top:20px; }
.hyperlink-section h2 { margin-bottom:15px; }
.link-item { padding:5px 0; border-bottom:1px solid #eee; font-size:12px; }
.link-item a { color:#0066cc; text-decoration:none; }
</style>
</head>
<body>
<div class="header">
<h1>LEGAL SECTION</h1>
<p>Growing database of legal documents, permits, and public records | """ + str(index['total_documents']) + """ documents indexed</p>
</div>
<div class="container">
<div class="stats">
<div class="stat-box">
<div class="number">""" + str(index['total_documents']) + """</div>
<div class="label">Total Documents</div>
</div>
<div class="stat-box">
<div class="number">""" + str(len(index['categories'])) + """</div>
<div class="label">Categories</div>
</div>
<div class="stat-box">
<div class="number">""" + str(len(index['hyperlink_index'])) + """</div>
<div class="label">Unique Hyperlinks</div>
</div>
<div class="stat-box">
<div class="number">""" + str(sum(len(v) for v in index['categories'].values())) + """</div>
<div class="label">Cross-References</div>
</div>
</div>
"""
        for cat, doc_ids in sorted(index['categories'].items()):
            html += f"""
<div class="category">
<div class="category-header" onclick="this.nextElementSibling.classList.toggle('active')">
<span>{cat.upper()} ({len(doc_ids)} documents)</span>
<span>&#9660;</span>
</div>
<div class="category-content">
"""
            for doc in index['documents']:
                if doc['id'] in doc_ids:
                    html += f"""
<div class="doc-card">
<h4>{doc['file']}</h4>
<div class="meta">{doc['type']} | {doc['timestamp'][:10]} | {doc['path']}</div>
<div class="links">
{''.join(f'<a href="{l}" target="_blank">Link</a>' for l in doc['hyperlinks'][:3])}
</div>
</div>
"""
            html += '</div></div>'
            
        html += """
<div class="hyperlink-section">
<h2>Hyperlink Index</h2>
"""
        for link, doc_ids in list(index['hyperlink_index'].items())[:20]:
            html += f'<div class="link-item"><a href="{link}" target="_blank">{link[:80]}</a> ({len(doc_ids)} refs)</div>'
            
        html += """
</div>
</div>
</body>
</html>"""
        return html


def generate():
    """Generate and save legal index"""
    legal = LegalSection()
    index = legal.generate_legal_index()
    
    os.makedirs(LEGAL_DIR, exist_ok=True)
    
    with open(LEGAL_DIR / "legal_index.json", "w") as f:
        json.dump(index, f, indent=2)
        
    html = legal.export_legal_html(index)
    with open(LEGAL_DIR / "legal_index.html", "w") as f:
        f.write(html)
        
    return index


if __name__ == "__main__":
    index = generate()
    print(f"Generated {index['total_documents']} legal documents")
    print(f"Categories: {list(index['categories'].keys())}")
    print(f"Hyperlinks: {len(index['hyperlink_index'])}")
