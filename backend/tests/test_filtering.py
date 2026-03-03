"""
AgriScheme Backend — Eligibility filtering-specific tests.

Run after starting the server and seeding the DB.

Usage:
    python test_filtering.py
"""
import requests
import json

URL = "http://127.0.0.1:5000/api/getEligibleSchemes"
HEADERS = {"Content-Type": "application/json"}


def print_schemes(case_name, data):
    print(f"\n{'─' * 50}")
    print(f"  {case_name}")
    print(f"{'─' * 50}")
    schemes = data.get("schemes", [])
    if not schemes:
        print("  No schemes found.")
        return
    print(f"  Found {data.get('total', len(schemes))} schemes (showing {len(schemes)}):")
    for i, s in enumerate(schemes, 1):
        print(f"  {i}. {s.get('scheme_name')}")
        print(f"     Type: {s.get('type')} | Benefit: {s.get('benefit')}")
        docs = s.get("documents_required", [])
        if docs:
            print(f"     Docs: {', '.join(docs[:3])}{'...' if len(docs) > 3 else ''}")
        print(f"     Link: {s.get('official_link', 'N/A')}")


def test_case(name, state, crop, land_size, season=None):
    payload = {
        "state": state,
        "crop": crop,
        "land_size": land_size,
    }
    if season:
        payload["season"] = season

    try:
        response = requests.post(URL, json=payload, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            print_schemes(name, response.json())
        else:
            print(f"\n❌ {name} — HTTP {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"\n❌ {name} — Connection error: {e}")


print("=" * 60)
print("AgriScheme — Eligibility Filtering Tests")
print("=" * 60)

# 1. Standard: Tamil Nadu, Rice, Small Farmer, Kharif
# Should get: ALL central schemes + TN Rice scheme + Small Farmer scheme
test_case("1. TN Rice Small Farmer (1.0ha, Kharif)", "Tamil Nadu", "Rice", 1.0, "Kharif")

# 2. Large Farmer: Tamil Nadu, Rice, Large Farmer
# Should get: ALL central schemes + TN Rice scheme, but NOT Small Farmer scheme
test_case("2. TN Rice Large Farmer (5.0ha)", "Tamil Nadu", "Rice", 5.0)

# 3. Punjab, Wheat, Rabi
# Should get: central schemes + Punjab Wheat scheme
test_case("3. Punjab Wheat (3ha, Rabi)", "Punjab", "Wheat", 3.0, "Rabi")

# 4. Kerala, Coconut
# Should get: central schemes + Kerala Coconut scheme
test_case("4. Kerala Coconut (1ha)", "Kerala", "Coconut", 1.0)

# 5. Maharashtra, Sugarcane
# Should get: central schemes + Jalyukt Shivar (no crop filter on it)
test_case("5. Maharashtra Sugarcane (2ha)", "Maharashtra", "Sugarcane", 2.0)

# 6. Andhra Pradesh, All crops
# Should get: central schemes + YSR Rythu Bharosa
test_case("6. Andhra Pradesh Rice (3ha)", "Andhra Pradesh", "Rice", 3.0)

# 7. Telangana
# Should get: central schemes + Rythu Bandhu
test_case("7. Telangana Rice (2ha)", "Telangana", "Rice", 2.0)

# 8. Non-existent state (should get zero)
test_case("8. Unknown State (should be empty)", "Atlantis", "Rice", 1.0)

print(f"\n{'=' * 60}")
print("Done. Review results above.")
print("=" * 60)
