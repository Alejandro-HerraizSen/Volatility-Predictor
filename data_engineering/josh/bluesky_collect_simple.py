import os
import csv
import re
import sys
from atproto import Client

handle = os.getenv("BSKY_HANDLE")
app_password = os.getenv("BSKY_APP_PASSWORD")

if not handle or not app_password:
    raise ValueError("Missing BSKY_HANDLE or BSKY_APP_PASSWORD environment variable.")

if len(sys.argv) != 4:
    raise ValueError("Usage: python src/collect/bluesky_collect_simple.py <event_id> <ticker> <company_name>")

event_id = sys.argv[1]
ticker = sys.argv[2].upper()
company_name = sys.argv[3]

client = Client()
client.login(handle, app_password)

query = f"{ticker} earnings"
response = client.app.bsky.feed.search_posts({"q": query, "limit": 25})

output_path = f"data/processed/bluesky_{event_id}.csv"
os.makedirs("data/processed", exist_ok=True)

earnings_terms = ["earnings", "revenue", "eps", "guidance", "quarter", "results", "reported", "call", "outlook"]

rows = []
for post in response.posts:
    author = getattr(post.author, "handle", "unknown")
    text = getattr(post.record, "text", "")
    created_at = getattr(post.record, "created_at", "")
    post_uri = getattr(post, "uri", "")

    text_no_urls = re.sub(r"http\S+", "", text)
    text_lower = text_no_urls.lower()

    has_cashtag = f"${ticker.lower()}" in text_lower
    has_plain_ticker = bool(re.search(rf"\b{ticker.lower()}\b", text_lower))
    has_company = company_name.lower() in text_lower
    has_earnings_term = any(term in text_lower for term in earnings_terms)

    match_score = sum([has_cashtag, has_plain_ticker, has_company, has_earnings_term])

    if match_score >= 2:
        relevance_label = "high"
    elif match_score == 1:
        relevance_label = "medium"
    else:
        relevance_label = "low"

    if relevance_label in ["high", "medium"]:
        rows.append({
            "event_id": event_id,
            "ticker": ticker,
            "company_name": company_name,
            "created_at": created_at,
            "author_handle": author,
            "text_raw": text,
            "query_used": query,
            "post_uri": post_uri,
            "has_cashtag": has_cashtag,
            "has_plain_ticker": has_plain_ticker,
            "has_company": has_company,
            "has_earnings_term": has_earnings_term,
            "match_score": match_score,
            "relevance_label": relevance_label
        })

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "event_id",
            "ticker",
            "company_name",
            "created_at",
            "author_handle",
            "text_raw",
            "query_used",
            "post_uri",
            "has_cashtag",
            "has_plain_ticker",
            "has_company",
            "has_earnings_term",
            "match_score",
            "relevance_label"
        ]
    )
    writer.writeheader()
    writer.writerows(rows)

print("Search query:", query)
print("Total posts returned by search:", len(response.posts))
print("Posts saved:", len(rows))
print("Saved file:", output_path)