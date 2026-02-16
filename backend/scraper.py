"""
AgriScheme Backend — Web scraper for official Indian government agriculture scheme data.

Sources:
    1. data.gov.in          — India Open Government Data Portal
    2. agricoop.nic.in      — Ministry of Agriculture & Farmers Welfare
    3. pmkisan.gov.in       — PM-KISAN Scheme
    4. pmfby.gov.in         — Pradhan Mantri Fasal Bima Yojana
    5. nabard.org           — NABARD Agricultural Loans & Subsidies

Usage:
    python scraper.py                     # Scrape and save to schemes_scraped.json
    python scraper.py --insert            # Scrape and insert directly into MongoDB
    python scraper.py --output out.json   # Custom output path
"""

import json
import sys
import argparse
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
TIMEOUT = 15  # seconds


# ═══════════════════════════════════════════════════════════════════════════
# Source 1 — data.gov.in  (API-based catalog search)
# ═══════════════════════════════════════════════════════════════════════════
def scrape_data_gov_in():
    """Fetch agriculture-related datasets from data.gov.in catalog API."""
    logger.info("Scraping data.gov.in ...")
    schemes = []

    try:
        url = "https://data.gov.in/search?title=agriculture+scheme&sort=changed"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".views-row, .view-content .views-row")

        for item in items[:10]:
            title_el = item.select_one("h3 a, .views-field-title a, a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link = title_el.get("href", "")
            if link and not link.startswith("http"):
                link = f"https://data.gov.in{link}"

            desc_el = item.select_one(".views-field-body, p, .field-content")
            desc = desc_el.get_text(strip=True) if desc_el else ""

            schemes.append({
                "scheme_name": title,
                "type": "Subsidy",
                "benefit": "See official portal",
                "benefit_amount": 0,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": ["Aadhaar Card", "Land Records"],
                "official_link": link or "https://data.gov.in",
                "description": {"en": desc or title},
                "source": "data.gov.in",
            })

        logger.info("  → Fetched %d entries from data.gov.in", len(schemes))
    except Exception as exc:
        logger.warning("  ✗ data.gov.in scrape failed: %s", exc)

    return schemes


# ═══════════════════════════════════════════════════════════════════════════
# Source 2 — agricoop.nic.in (Ministry of Agriculture)
# ═══════════════════════════════════════════════════════════════════════════
def scrape_agricoop():
    """Scrape scheme listings from Ministry of Agriculture website."""
    logger.info("Scraping agricoop.nic.in ...")
    schemes = []

    try:
        url = "https://agricoop.nic.in/en/Major"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.select("table tr, .view-content .views-row, li a")

        for row in rows[:15]:
            link_el = row.select_one("a") if row.name != "a" else row
            if not link_el:
                continue
            name = link_el.get_text(strip=True)
            if len(name) < 5:
                continue

            href = link_el.get("href", "")
            if href and not href.startswith("http"):
                href = f"https://agricoop.nic.in{href}"

            schemes.append({
                "scheme_name": name,
                "type": "Subsidy",
                "benefit": "Government subsidy",
                "benefit_amount": 0,
                "states": ["All"],
                "crops": ["All"],
                "min_land": 0,
                "max_land": 100,
                "season": "All",
                "documents_required": ["Aadhaar Card", "Land Records", "Bank Account Details"],
                "official_link": href or "https://agricoop.nic.in",
                "description": {"en": f"Government scheme: {name}"},
                "source": "agricoop.nic.in",
            })

        logger.info("  → Fetched %d entries from agricoop.nic.in", len(schemes))
    except Exception as exc:
        logger.warning("  ✗ agricoop.nic.in scrape failed: %s", exc)

    return schemes


# ═══════════════════════════════════════════════════════════════════════════
# Source 3 — pmkisan.gov.in
# ═══════════════════════════════════════════════════════════════════════════
def scrape_pmkisan():
    """Return PM-KISAN scheme details (primarily static + page verification)."""
    logger.info("Scraping pmkisan.gov.in ...")
    schemes = []

    try:
        url = "https://pmkisan.gov.in"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        # Extract dynamic stats if available
        stats_text = ""
        stats_el = soup.select_one(".counter, .stat, .beneficiary-count")
        if stats_el:
            stats_text = f" Beneficiaries: {stats_el.get_text(strip=True)}."

        schemes.append({
            "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            "type": "Income Support",
            "benefit": "₹6,000 per year (₹2,000 × 3 installments)",
            "benefit_amount": 6000,
            "states": ["All"],
            "crops": ["All"],
            "min_land": 0,
            "max_land": 100,
            "season": "All",
            "documents_required": [
                "Aadhaar Card",
                "Land Ownership Records",
                "Bank Account (linked to Aadhaar)",
                "Mobile Number",
            ],
            "official_link": "https://pmkisan.gov.in",
            "description": {
                "en": (
                    "PM-KISAN provides ₹6,000 per year income support to all "
                    "landholding farmer families in three equal installments of "
                    "₹2,000 each directly to their bank accounts via DBT."
                    + stats_text
                ),
            },
            "source": "pmkisan.gov.in",
        })

        logger.info("  → Fetched PM-KISAN data")
    except Exception as exc:
        logger.warning("  ✗ pmkisan.gov.in scrape failed: %s — using fallback data", exc)
        schemes.append({
            "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            "type": "Income Support",
            "benefit": "₹6,000 per year",
            "benefit_amount": 6000,
            "states": ["All"],
            "crops": ["All"],
            "min_land": 0,
            "max_land": 100,
            "season": "All",
            "documents_required": ["Aadhaar Card", "Land Records", "Bank Account"],
            "official_link": "https://pmkisan.gov.in",
            "description": {
                "en": "PM-KISAN provides ₹6,000/year income support to farmer families.",
            },
            "source": "pmkisan.gov.in (fallback)",
        })

    return schemes


# ═══════════════════════════════════════════════════════════════════════════
# Source 4 — pmfby.gov.in (Crop Insurance)
# ═══════════════════════════════════════════════════════════════════════════
def scrape_pmfby():
    """Return PMFBY scheme details."""
    logger.info("Scraping pmfby.gov.in ...")
    schemes = []

    try:
        url = "https://pmfby.gov.in"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Try to find crop-wise premium info
        tables = soup.select("table")
        premium_info = ""
        for table in tables:
            text = table.get_text()
            if "premium" in text.lower() or "kharif" in text.lower():
                rows = table.select("tr")
                for row in rows[:5]:
                    cells = [td.get_text(strip=True) for td in row.select("td, th")]
                    if cells:
                        premium_info += " | ".join(cells) + ". "
                break

        schemes.append({
            "scheme_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "type": "Insurance",
            "benefit": "Comprehensive Crop Insurance Coverage",
            "benefit_amount": 200000,
            "states": ["All"],
            "crops": ["All"],
            "min_land": 0,
            "max_land": 100,
            "season": "All",
            "documents_required": [
                "Aadhaar Card",
                "Land Records / Tenancy Agreement",
                "Bank Account Details",
                "Sowing Certificate",
                "Crop Details Declaration",
            ],
            "official_link": "https://pmfby.gov.in",
            "description": {
                "en": (
                    "PMFBY provides comprehensive crop insurance coverage at very low "
                    "premium rates — 2% for Kharif, 1.5% for Rabi, 5% for commercial/"
                    "horticultural crops. Covers yield losses, prevented sowing, "
                    "post-harvest losses, and localized calamities. "
                    + (premium_info if premium_info else "")
                ),
            },
            "source": "pmfby.gov.in",
        })

        logger.info("  → Fetched PMFBY data")
    except Exception as exc:
        logger.warning("  ✗ pmfby.gov.in scrape failed: %s — using fallback", exc)
        schemes.append({
            "scheme_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "type": "Insurance",
            "benefit": "Comprehensive Crop Insurance",
            "benefit_amount": 200000,
            "states": ["All"],
            "crops": ["All"],
            "min_land": 0,
            "max_land": 100,
            "season": "All",
            "documents_required": ["Aadhaar Card", "Land Records", "Bank Account", "Sowing Certificate"],
            "official_link": "https://pmfby.gov.in",
            "description": {"en": "Comprehensive crop insurance at 2% (Kharif) / 1.5% (Rabi) premium."},
            "source": "pmfby.gov.in (fallback)",
        })

    return schemes


# ═══════════════════════════════════════════════════════════════════════════
# Source 5 — nabard.org (Loans & Subsidies)
# ═══════════════════════════════════════════════════════════════════════════
def scrape_nabard():
    """Scrape NABARD scheme information."""
    logger.info("Scraping nabard.org ...")
    schemes = []

    try:
        url = "https://www.nabard.org/content.aspx?id=2"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.select("a")

        keywords = ["scheme", "fund", "loan", "subsidy", "credit", "rural", "farm", "agri"]
        for link in links:
            text = link.get_text(strip=True)
            href = link.get("href", "")
            if any(kw in text.lower() for kw in keywords) and len(text) > 10:
                if href and not href.startswith("http"):
                    href = f"https://www.nabard.org/{href.lstrip('/')}"

                schemes.append({
                    "scheme_name": text,
                    "type": "Loan",
                    "benefit": "Financial assistance / loan facility",
                    "benefit_amount": 0,
                    "states": ["All"],
                    "crops": ["All"],
                    "min_land": 0,
                    "max_land": 100,
                    "season": "All",
                    "documents_required": [
                        "Aadhaar Card",
                        "Land Records",
                        "Bank Account Details",
                        "Project Report (if applicable)",
                    ],
                    "official_link": href or "https://www.nabard.org",
                    "description": {"en": f"NABARD programme: {text}"},
                    "source": "nabard.org",
                })

        # De-duplicate by scheme name
        seen = set()
        unique = []
        for s in schemes:
            if s["scheme_name"] not in seen:
                seen.add(s["scheme_name"])
                unique.append(s)
        schemes = unique[:10]

        logger.info("  → Fetched %d entries from nabard.org", len(schemes))
    except Exception as exc:
        logger.warning("  ✗ nabard.org scrape failed: %s — using fallback", exc)
        schemes.append({
            "scheme_name": "NABARD Rural Infrastructure Development Fund (RIDF)",
            "type": "Loan",
            "benefit": "Low-interest infrastructure loans",
            "benefit_amount": 500000,
            "states": ["All"],
            "crops": ["All"],
            "min_land": 0,
            "max_land": 100,
            "season": "All",
            "documents_required": ["Aadhaar Card", "Land Records", "Project Proposal"],
            "official_link": "https://www.nabard.org",
            "description": {"en": "RIDF provides low-interest loans for rural infrastructure."},
            "source": "nabard.org (fallback)",
        })

    return schemes


# ═══════════════════════════════════════════════════════════════════════════
# Orchestrator
# ═══════════════════════════════════════════════════════════════════════════
def scrape_all_sources():
    """Run all scrapers and return a combined, deduplicated list."""
    all_schemes = []

    scrapers = [
        scrape_data_gov_in,
        scrape_agricoop,
        scrape_pmkisan,
        scrape_pmfby,
        scrape_nabard,
    ]

    for scraper_fn in scrapers:
        try:
            results = scraper_fn()
            all_schemes.extend(results)
        except Exception as exc:
            logger.error("Scraper %s raised unexpected error: %s", scraper_fn.__name__, exc)

    # Add timestamp
    for s in all_schemes:
        s["scraped_at"] = datetime.utcnow().isoformat()

    logger.info("=" * 60)
    logger.info("Total schemes scraped: %d", len(all_schemes))
    return all_schemes


def save_to_json(schemes, output_path="schemes_scraped.json"):
    """Save scraped schemes to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schemes, f, indent=2, ensure_ascii=False)
    logger.info("Saved to %s", output_path)


def insert_into_db(schemes):
    """Insert scraped schemes into MongoDB (merges with existing data)."""
    from db import get_schemes_collection

    collection = get_schemes_collection()
    inserted = 0
    updated = 0

    for scheme in schemes:
        result = collection.update_one(
            {"scheme_name": scheme["scheme_name"]},
            {"$set": scheme},
            upsert=True,
        )
        if result.upserted_id:
            inserted += 1
        elif result.modified_count > 0:
            updated += 1

    logger.info("DB insert complete: %d new, %d updated", inserted, updated)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape government agriculture scheme data")
    parser.add_argument("--output", default="schemes_scraped.json", help="Output JSON path")
    parser.add_argument("--insert", action="store_true", help="Insert results into MongoDB")
    args = parser.parse_args()

    schemes = scrape_all_sources()

    # Always save to file
    save_to_json(schemes, args.output)

    # Optionally insert into DB
    if args.insert:
        insert_into_db(schemes)

    print(f"\n✅ Done. Total schemes: {len(schemes)}")
