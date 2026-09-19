#!/usr/bin/env python3
"""Self-populating OSINT Newspaper Generator"""
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

DATA_DIR = Path.home() / "OsintNeoAi" / "data"
CASES_DIR = DATA_DIR / "cases"
LEDGER_DIR = DATA_DIR / "ledger"

class OSINTNewspaper:
    def __init__(self):
        self.articles = []
        self.ledger = []
        
    def scan_data_sources(self):
        """Scan all OSINT data sources for new articles"""
        sources = {
            "huntington_beach": DATA_DIR / "huntington_beach",
            "cases": CASES_DIR,
            "ledger": LEDGER_DIR,
            "grants": DATA_DIR / "grants",
        }
        
        for name, path in sources.items():
            if path.exists():
                for f in path.glob("**/*.json"):
                    self._process_file(f, name)
                for f in path.glob("**/*.md"):
                    self._process_file(f, name)
                    
    def _process_file(self, filepath, source):
        """Process a data file into a newspaper article"""
        try:
            stat = filepath.stat()
            content = filepath.read_text(errors='ignore')[:5000]
            
            article = {
                "id": hashlib.md5(str(filepath).encode()).hexdigest()[:12],
                "source": source,
                "file": filepath.name,
                "title": self._generate_title(filepath, content),
                "summary": self._generate_summary(content),
                "timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size": stat.st_size,
                "hyperlinks": self._extract_hyperlinks(content),
                "tags": self._extract_tags(content),
            }
            self.articles.append(article)
        except Exception as e:
            pass
            
    def _generate_title(self, filepath, content):
        """Generate article title from filename and content"""
        name = filepath.stem.replace("_", " ").replace("-", " ").title()
        if len(name) > 60:
            name = name[:57] + "..."
        return name
        
    def _generate_summary(self, content):
        """Generate summary from content"""
        lines = content.split("\n")
        summary_lines = [l.strip() for l in lines[:10] if l.strip() and not l.startswith("#")]
        summary = " ".join(summary_lines)[:300]
        if len(content) > 300:
            summary += "..."
        return summary
        
    def _extract_hyperlinks(self, content):
        """Extract hyperlinks from content"""
        import re
        urls = re.findall(r'https?://[^\s\)\"]+', content)
        return list(set(urls))[:20]
        
    def _extract_tags(self, content):
        """Extract tags from content"""
        tags = []
        tag_keywords = [
            "HBNC", "Huntington Beach", "navigation center", "homeless",
            "SCE", "Edison", "underground", "utility", "transformer",
            "StormTech", "concrete", "vault", "permit", "construction",
            "TTS Engineering", "RPM Team", "EEC Environmental",
            "Mercy House", "Jamboree Housing", "property", "parcel",
            "OSINT", "breach", "email", "phone", "address",
        ]
        content_lower = content.lower()
        for kw in tag_keywords:
            if kw.lower() in content_lower:
                tags.append(kw)
        return tags[:10]
        
    def generate_newspaper(self):
        """Generate the self-populating newspaper"""
        self.scan_data_sources()
        
        newspaper = {
            "generated_at": datetime.now().isoformat(),
            "total_articles": len(self.articles),
            "sources": list(set(a["source"] for a in self.articles)),
            "articles": sorted(self.articles, key=lambda x: x["timestamp"], reverse=True),
            "stats": {
                "total_hyperlinks": sum(len(a["hyperlinks"]) for a in self.articles),
                "total_tags": len(set(t for a in self.articles for t in a["tags"])),
                "sources_breakdown": {},
            }
        }
        
        for a in self.articles:
            src = a["source"]
            newspaper["stats"]["sources_breakdown"][src] = \
                newspaper["stats"]["sources_breakdown"].get(src, 0) + 1
                
        return newspaper
        
    def export_html(self, newspaper):
        """Export newspaper as HTML"""
        html = """<!DOCTYPE html>
<html>
<head>
<title>OSINT Neo AI - Intelligence Newspaper</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Georgia',serif; background:#fafaf8; color:#1a1a1a; }
.masthead { background:#1a1a1a; color:#fff; text-align:center; padding:30px; }
.masthead h1 { font-size:48px; font-family:'Playfair Display',serif; letter-spacing:4px; }
.masthead .dateline { color:#888; margin-top:10px; font-style:italic; }
.stats-bar { background:#f0f0f0; padding:10px 30px; display:flex; gap:30px; border-bottom:2px solid #1a1a1a; }
.stats-bar .stat { font-size:12px; color:#666; }
.stats-bar .stat b { color:#1a1a1a; }
.container { max-width:1200px; margin:0 auto; padding:20px; }
.article { background:#fff; border:1px solid #ddd; padding:20px; margin:15px 0; }
.article h2 { font-family:'Playfair Display',serif; font-size:24px; margin-bottom:10px; }
.article .meta { color:#888; font-size:12px; margin-bottom:10px; }
.article .summary { line-height:1.6; margin-bottom:10px; }
.article .tags { display:flex; flex-wrap:wrap; gap:5px; }
.article .tag { background:#e8e8e8; padding:2px 8px; font-size:11px; border-radius:3px; }
.article .links { margin-top:10px; }
.article .links a { color:#0066cc; font-size:12px; margin-right:10px; text-decoration:none; }
.article .links a:hover { text-decoration:underline; }
.ledger-section { background:#1a1a1a; color:#00ff41; padding:30px; margin-top:30px; font-family:monospace; }
.ledger-section h2 { color:#00ff41; margin-bottom:15px; }
.ledger-entry { border-bottom:1px solid #333; padding:8px 0; font-size:12px; }
</style>
</head>
<body>
<div class="masthead">
<h1>OSINT NEO AI</h1>
<div class="dateline">Intelligence Newspaper | Generated: """ + newspaper["generated_at"] + """</div>
</div>
<div class="stats-bar">
<div class="stat"><b>""" + str(newspaper["total_articles"]) + """</b> Articles</div>
<div class="stat"><b>""" + str(newspaper["stats"]["total_hyperlinks"]) + """</b> Hyperlinks</div>
<div class="stat"><b>""" + str(newspaper["stats"]["total_tags"]) + """</b> Tags</div>
<div class="stat"><b>""" + str(len(newspaper["sources"])) + """</b> Sources</div>
</div>
<div class="container">
"""
        for article in newspaper["articles"][:50]:
            html += f"""
<div class="article">
<h2>{article['title']}</h2>
<div class="meta">Source: {article['source']} | {article['timestamp'][:10]} | {article['file']}</div>
<div class="summary">{article['summary']}</div>
<div class="tags">
{''.join(f'<span class="tag">{t}</span>' for t in article['tags'])}
</div>
"""
            if article['hyperlinks']:
                html += '<div class="links">Links: '
                for url in article['hyperlinks'][:5]:
                    html += f'<a href="{url}" target="_blank">{url[:50]}...</a> '
                html += '</div>'
            html += '</div>'
            
        html += """
</div>
<div class="ledger-section">
<h2>TAXPAYER OSINT LEDGER</h2>
<p>Every query, every scan, every dollar tracked on-chain.</p>
<div id="ledger-entries"></div>
</div>
</body>
</html>"""
        return html


def generate():
    """Generate and save the newspaper"""
    newspaper = OSINTNewspaper()
    data = newspaper.generate_newspaper()
    
    os.makedirs(LEDGER_DIR, exist_ok=True)
    
    with open(LEDGER_DIR / "newspaper.json", "w") as f:
        json.dump(data, f, indent=2)
        
    html = newspaper.export_html(data)
    with open(LEDGER_DIR / "newspaper.html", "w") as f:
        f.write(html)
        
    return data


if __name__ == "__main__":
    data = generate()
    print(f"Generated {data['total_articles']} articles")
    print(f"Sources: {data['sources']}")
    print(f"Hyperlinks: {data['stats']['total_hyperlinks']}")
    print(f"Saved to: {LEDGER_DIR}")
