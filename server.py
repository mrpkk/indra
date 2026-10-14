#!/usr/bin/env python3
"""Витрина Индры — одна страница на все сервисы.

Пять сервисов, пять адресов — значит пять ссылок, которые надо по
каждому отдельно упоминать, и ни одна из них не собирает аудиторию в
одном месте. Здесь ровно обратное: один адрес, одна страница, все
сервисы сразу.

Продвигать одну страницу дешевле, чем пять: один пост, одна ссылка,
один домен в истории. Репо с пятью адресами не превращается в поток
посетителей — оно остаётся папкой с кодом.
"""

from __future__ import annotations

import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

CARDS = [
    {
        "name": "ṚTA",
        "path": "https://rta.lat/",
        "tag": "ZK proofs",
        "body": "Prove a balance, stake, account age or transaction count meets "
                "a threshold — the verifier learns only that it does, never the "
                "value. Five Groth16 circuits, zero public signals.",
        "price": "1 USDC per verification",
        "state": "Base mainnet",
    },
    {
        "name": "attest",
        "path": "https://attest.rta.lat/",
        "tag": "Provenance",
        "body": "Four layers: schema, is there anything inside, what conditions "
                "produced it, and was the action permitted. Ed25519-signed, and "
                "the check runs without trusting us.",
        "demo": "https://attest.rta.lat/demo",
        "price": "20 free/day, then 0.005 USDC per call, or 9 USDC "
                 "for 30 days prepaid",
        "state": "Base mainnet",
    },
    {
        "name": "agentpay",
        "path": "https://rta.lat/agentpay/",
        "tag": "Billing",
        "body": "Price a call by what it actually consumed — tokens, CPU, bytes, "
                "writes, external calls — with the breakdown attached. A price "
                "table is a guess made once; this recomputes.",
        "price": "Free preview",
        "state": "Live",
    },
    {
        "name": "drift",
        "path": "https://drift.rta.lat/",
        "tag": "Agent trust",
        "body": "Continuous mandate enforcement for AI agents, as an MCP server. "
                "Checks the mandate at the moment of the action, so permissions "
                "that expire mid-session stop working mid-session.",
        "price": "100 free/day, then 0.005 USDC",
        "state": "Base mainnet",
    },
    {
        "name": "indra-memory",
        "path": "https://rta.lat/memory/",
        "tag": "Long memory",
        "body": "Facts live in SQLite outside the context window; only a "
                "relevance-ranked sample enters the prompt. Context-bound memory "
                "degrades with length — the model cannot see the start of its own "
                "conversation.",
        "price": "Free preview",
        "state": "Live",
    },
    {
        "name": "verity",
        "path": "https://rta.lat/verity/",
        "tag": "Due diligence",
        "body": "Three answers, not two: the site responds, the domain is a "
                "corporate root with the platform buried at a path, or it is "
                "dead. A responding domain is not a usable platform.",
        "price": "Free",
        "state": "Live",
    },
]

HTML = """<!doctype html><html lang=en><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Zero-Knowledge Proof API, Agent Memory &amp; x402 Payments — Indra</title>
<meta name=description content="Zero-knowledge proof API, agent long-term memory,
consumption-based API billing, mandate enforcement and platform due diligence
for AI agents. Groth16, MCP, x402 payments on Base mainnet. Free tiers, no
account, no SDK.">
<meta name=keywords content="zero knowledge proof, zk proof api, groth16, zk-snarks,
agent memory, long term memory ai, x402 payments, base mainnet, usdc api,
mcp server, ai agent infrastructure, api usage based pricing">
<meta property=og:title content="Indra — zero-knowledge proofs, agent memory, x402 payments">
<meta property=og:description content="Six small services for AI agents that have to be trusted. Live on Base mainnet, free tiers, no account.">
<meta property=og:type content=website>
<meta property=og:url content="https://indra.rta.lat">
<link rel=canonical href="https://indra.rta.lat">
<style>
 :root{--bg:#0b0d12;--card:#141821;--ink:#e8ecf4;--mut:#969eac;--am:#f0a35e;
       --gr:#6ec896;--bd:#1f242e}
 *{box-sizing:border-box}
 body{margin:0;background:var(--bg);color:var(--ink);
      font:16px/1.6 ui-sans-serif,system-ui,-apple-system,sans-serif}
 .wrap{max-width:1060px;margin:0 auto;padding:72px 24px 90px}
 h1{font-size:clamp(32px,5.5vw,52px);line-height:1.08;margin:0 0 14px;
    letter-spacing:-.02em}
 .lede{font-size:19px;color:var(--mut);max-width:62ch;margin:0 0 14px}
 .lede b{color:var(--ink);font-weight:600}
 .meta{font-size:14px;color:var(--mut);margin-bottom:56px}
 .meta a{color:var(--am)}
 .grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(310px,1fr))}
 .card{background:var(--card);border:1px solid var(--bd);border-radius:14px;
       padding:22px 22px 20px;display:flex;flex-direction:column;gap:10px;
       text-decoration:none;color:inherit;transition:border-color .15s,transform .15s}
 .card:hover{border-color:#39414f;transform:translateY(-2px)}
 .row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
 .nm{font-size:20px;font-weight:650;letter-spacing:-.01em}
 .tag{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--am);
      border:1px solid #3a2c1d;border-radius:999px;padding:2px 9px}
 .ok{font-size:11px;letter-spacing:.06em;color:var(--gr);margin-left:auto}
 .bd{color:var(--mut);font-size:14.5px;margin:0}
 .pr{display:flex;justify-content:space-between;gap:12px;border-top:1px solid var(--bd);
     padding-top:11px;margin-top:auto;font-size:13px}
 .pr span:last-child{color:var(--ink);font-variant-numeric:tabular-nums}
 .warn{margin-top:52px;border:1px solid #3a2c1d;border-left:3px solid var(--am);
       border-radius:10px;padding:16px 20px;background:#141821}
 .warn b{color:var(--am)}
 .warn p{margin:6px 0 0;color:var(--mut);font-size:14.5px;max-width:74ch}
 footer{margin-top:44px;color:var(--mut);font-size:13.5px}
 footer a{color:var(--am)}
</style>
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
 {"@type":"SoftwareApplication","name":"ṚTA","applicationCategory":"SecurityApplication",
  "description":"Zero-knowledge proof API: prove a balance, stake, account age or transaction count meets a threshold without revealing the value.",
  "url":"https://rta.lat","offers":{"@type":"Offer","price":"1","priceCurrency":"USDC"},
  "operatingSystem":"Web"},
 {"@type":"SoftwareApplication","name":"attest","applicationCategory":"DeveloperApplication",
  "description":"Artifact provenance and schema verification for AI agents.",
  "url":"https://attest.rta.lat/","offers":{"@type":"AggregateOffer","lowPrice":"0.005","highPrice":"9","priceCurrency":"USDC"}},
 {"@type":"SoftwareApplication","name":"agentpay","applicationCategory":"BusinessApplication",
  "description":"Consumption-based API billing priced from measured tokens, CPU and bytes.",
  "url":"https://rta.lat/agentpay/"},
 {"@type":"SoftwareApplication","name":"drift","applicationCategory":"DeveloperApplication",
  "description":"MCP server for continuous mandate enforcement of AI agents.",
  "url":"https://drift.rta.lat/","offers":{"@type":"Offer","price":"0.005","priceCurrency":"USDC"}},
 {"@type":"SoftwareApplication","name":"indra-memory","applicationCategory":"DeveloperApplication",
  "description":"Long-term memory for AI agents in SQLite outside the context window.",
  "url":"https://rta.lat/memory/"},
 {"@type":"SoftwareApplication","name":"verity","applicationCategory":"UtilitiesApplication",
  "description":"Due diligence check distinguishing live platforms from parked or dead domains.",
  "url":"https://rta.lat/verity/"}
]}
</script>
<div class=wrap>
<h1>Small tools for agents<br>that have to be trusted</h1>
<p class=lede>Six services, each one narrow enough to understand in a minute:
<b>prove a fact</b> without revealing it, <b>check where an artifact came
from</b>, <b>price a call by what it cost</b>, <b>enforce a mandate</b> while it
runs, <b>remember across sessions</b>, and <b>check that a platform is real</b>.</p>
<p class=meta>Python standard library where it can be. No accounts, no SDK,
nothing to install. Payments per call over x402 on Base mainnet.
Source: <a href="https://github.com/mrpkk">github.com/mrpkk</a></p>
<div class=grid>__CARDS__</div>
<div class=warn>
<b>What these are not.</b>
ṚTA's ceremony is single-party, so a proof can be forged by the operator —
that is a real limitation, not a footnote. attest's circuits are unaudited.
agentpay's rate card is a demo and is reported as unverified until a source
and a date are attached. verity's pass means the site responds, never that
the operator is trustworthy.
</div>
<footer>Built and run by one person.
<a href="https://github.com/mrpkk/rta">ṚTA</a> &middot;
<a href="https://github.com/mrpkk/attest">attest</a> &middot;
<a href="https://github.com/mrpkk/drift">drift</a> &middot;
<a href="https://github.com/mrpkk/agentpay">agentpay</a> &middot;
<a href="https://github.com/mrpkk/indra-memory">indra-memory</a> &middot;
<a href="https://github.com/mrpkk/verity">verity</a></footer>
</div>
"""


def render() -> str:
    out = []
    for c in CARDS:
        out.append(
            f'<a class=card href="{c["path"]}">'
            f'<div class=row><span class=nm>{c["name"]}</span>'
            f'<span class=tag>{c["tag"]}</span>'
            f'<span class=ok>{c["state"]}</span></div>'
            f'<p class=bd>{c["body"]}</p>'
            f'<div class=pr><span>Price</span><span>{c["price"]}</span></div>'
            f"</a>")
    return HTML.replace("__CARDS__", "".join(out))


def _base_url() -> str:
    """Публичный адрес витрины: в sitemap обязаны быть абсолютные URL."""
    import os
    return os.environ.get("INDRA_BASE_URL",
                          "https://indra.rta.lat").rstrip("/")


def _robots() -> str:
    """Краулеров пускаем: витрина — точка входа для поиска."""
    return ("User-agent: *\n"
            "Allow: /\n"
            f"Sitemap: {_base_url()}/sitemap.xml\n")


def _sitemap() -> str:
    """Карта витрины: главная плюс адреса продуктов.

    Витрина — единственная страница, перечисляющая остальные домены.
    Без неё поисковик видит семь разрозненных сайтов вместо одного
    проекта, и связь между ними не читается.
    """
    base = _base_url()
    urls = f"<url><loc>{base}</loc></url>"
    for card in CARDS:
        urls += f"<url><loc>{card['path']}</loc></url>"
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"{urls}</urlset>")


def _send_raw(handler, body: bytes, content_type: str) -> None:
    """Отдать не-JSON: витрина отдаёт HTML, robots и sitemap — текст."""
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    try:
        handler.wfile.write(body)
    except (BrokenPipeError, ConnectionResetError):
        pass

class Handler(BaseHTTPRequestHandler):
    server_version = "indra-index"

    def do_GET(self) -> None:  # noqa: N802
        raw = self.path.split("?")[0].rstrip("/") or "/"
        if raw == "/robots.txt":
            return _send_raw(self, _robots().encode("utf-8"),
                              "text/plain; charset=utf-8")
        if raw == "/sitemap.xml":
            return _send_raw(self, _sitemap().encode("utf-8"),
                              "application/xml; charset=utf-8")
        raw = render().encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "public, max-age=300")
        self.end_headers()
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, *_a) -> None:
        pass


def serve(host: str = "127.0.0.1", port: int = 8189) -> None:
    print(f"indra: http://{host}:{port}", flush=True)
    srv = ThreadingHTTPServer((host, port), Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8189)
    a = ap.parse_args()
    serve(a.host, a.port)