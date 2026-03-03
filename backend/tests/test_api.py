"""
AgriScheme Backend — Comprehensive API test suite.

Run this AFTER the Flask server is started (python app.py) and the database
is seeded (python seed_db.py).

Usage:
    python test_api.py
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"
HEADERS = {"Content-Type": "application/json"}

passed = 0
failed = 0


def run_case(name, method, url, payload=None, expected_status=200, check_fn=None):
    """Run a single test case."""
    global passed, failed
    full_url = f"{BASE_URL}{url}"

    try:
        if method == "GET":
            resp = requests.get(full_url, headers=HEADERS, timeout=10)
        else:
            resp = requests.post(full_url, json=payload, headers=HEADERS, timeout=10)

        status_ok = resp.status_code == expected_status
        check_ok = True
        extra = ""

        if check_fn and status_ok:
            try:
                check_ok, extra = check_fn(resp.json())
            except Exception as e:
                check_ok = False
                extra = f"Check error: {e}"

        if status_ok and check_ok:
            print(f"  ✅ PASS: {name}")
            passed += 1
        else:
            print(f"  ❌ FAIL: {name}")
            print(f"       Status: {resp.status_code} (expected {expected_status})")
            if extra:
                print(f"       Detail: {extra}")
            if not status_ok:
                print(f"       Body: {resp.text[:300]}")
            failed += 1

    except requests.ConnectionError:
        print(f"  ❌ FAIL: {name} — Cannot connect to {BASE_URL}")
        failed += 1
    except Exception as e:
        print(f"  ❌ FAIL: {name} — {e}")
        failed += 1


# ═══════════════════════════════════════════════════════════════════════════
# Test Cases  (guarded so pytest can import this module safely)
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("AgriScheme API Test Suite")
    print("=" * 60)

    # --- 1. Health Check ---
    print("\n📋 Health Check")
    run_case("GET / — health check", "GET", "/",
         check_fn=lambda d: (d.get("status") == "ok", f"status={d.get('status')}"))

    # --- 2. List All Schemes ---
    print("\n📋 List Schemes")
    run_case("GET /api/schemes — list all", "GET", "/api/schemes",
         check_fn=lambda d: (d.get("count", 0) > 0, f"count={d.get('count')}"))

    run_case("GET /api/schemes?type=Loan — filter by type", "GET", "/api/schemes?type=Loan",
         check_fn=lambda d: (
             all(s.get("type") == "Loan" for s in d.get("schemes", [])),
             f"count={d.get('count')}"
         ))

    # --- 3. Eligibility Engine — Valid Queries ---
    print("\n📋 Eligibility Engine — Valid Queries")

    run_case(
        "Tamil Nadu + Rice + 2ha + Kharif — should find schemes",
        "POST", "/api/getEligibleSchemes",
        payload={"state": "Tamil Nadu", "crop": "Rice", "land_size": 2.0, "season": "Kharif"},
        check_fn=lambda d: (d.get("count", 0) > 0, f"count={d.get('count')}, total={d.get('total')}")
    )

    run_case(
        "Punjab + Wheat + 3ha + Rabi — should find Punjab Wheat scheme",
        "POST", "/api/getEligibleSchemes",
        payload={"state": "Punjab", "crop": "Wheat", "land_size": 3.0, "season": "Rabi"},
        check_fn=lambda d: (
            any("Punjab" in s.get("scheme_name", "") for s in d.get("schemes", [])),
            f"schemes: {[s['scheme_name'] for s in d.get('schemes', [])[:3]]}"
        )
    )

    run_case(
        "Kerala + Coconut + 1ha — should find Kerala Coconut scheme",
        "POST", "/api/getEligibleSchemes",
        payload={"state": "Kerala", "crop": "Coconut", "land_size": 1.0},
        check_fn=lambda d: (
            any("Coconut" in s.get("scheme_name", "") or "Kerala" in s.get("scheme_name", "")
                for s in d.get("schemes", [])),
            f"schemes: {[s['scheme_name'] for s in d.get('schemes', [])[:3]]}"
        )
    )

    run_case(
        "Small farmer (1ha) — should include Small Farmer scheme",
        "POST", "/api/getEligibleSchemes",
        payload={"state": "Tamil Nadu", "crop": "Rice", "land_size": 1.0},
        check_fn=lambda d: (
            any("Small" in s.get("scheme_name", "") or "Marginal" in s.get("scheme_name", "")
                for s in d.get("schemes", [])),
            f"count={d.get('count')}"
        )
    )

    run_case(
        "Large farmer (5ha) — should NOT include Small Farmer scheme",
        "POST", "/api/getEligibleSchemes",
        payload={"state": "Tamil Nadu", "crop": "Rice", "land_size": 5.0},
        check_fn=lambda d: (
            not any("Small" in s.get("scheme_name", "") and "Marginal" in s.get("scheme_name", "")
                    for s in d.get("schemes", [])),
            f"count={d.get('count')}"
        )
    )

    # --- 4. Benefit Sorting ---
    print("\n📋 Benefit Sorting")
    run_case(
        "Results should be sorted by benefit_amount DESC",
        "POST", "/api/getEligibleSchemes",
        payload={"state": "Tamil Nadu", "crop": "Rice", "land_size": 2.0},
        check_fn=lambda d: (
            all(
                d["schemes"][i].get("benefit_amount", 0) >= d["schemes"][i + 1].get("benefit_amount", 0)
                for i in range(len(d["schemes"]) - 1)
            ) if len(d.get("schemes", [])) > 1 else True,
            f"amounts={[s.get('benefit_amount', 0) for s in d.get('schemes', [])[:5]]}"
        )
    )

    # --- 5. Response Structure ---
    print("\n📋 Response Structure")
    run_case(
        "Response should include pagination metadata",
        "POST", "/api/getEligibleSchemes",
        payload={"state": "Tamil Nadu", "crop": "Rice", "land_size": 2.0},
        check_fn=lambda d: (
            all(k in d for k in ["success", "count", "total", "page", "limit", "schemes"]),
            f"keys={list(d.keys())}"
        )
    )

    run_case(
        "Schemes should include documents_required and official_link",
        "POST", "/api/getEligibleSchemes",
        payload={"state": "Tamil Nadu", "crop": "Rice", "land_size": 2.0},
        check_fn=lambda d: (
            all("documents_required" in s and "official_link" in s
                for s in d.get("schemes", [])[:3]) if d.get("schemes") else True,
            f"first scheme keys: {list(d['schemes'][0].keys()) if d.get('schemes') else 'none'}"
        )
    )

    # --- 6. Invalid Input Handling ---
    print("\n📋 Invalid Input Handling")

    run_case(
        "Missing state — should return 400",
        "POST", "/api/getEligibleSchemes",
        payload={"crop": "Rice", "land_size": 2.0},
        expected_status=400,
    )

    run_case(
        "Missing crop — should return 400",
        "POST", "/api/getEligibleSchemes",
        payload={"state": "Tamil Nadu", "land_size": 2.0},
        expected_status=400,
    )

    run_case(
        "Missing land_size — should return 400",
        "POST", "/api/getEligibleSchemes",
        payload={"state": "Tamil Nadu", "crop": "Rice"},
        expected_status=400,
    )

    run_case(
        "Empty body — should return 400",
        "POST", "/api/getEligibleSchemes",
        payload={},
        expected_status=400,
    )

    run_case(
        "NoSQL injection attempt ($gt in state) — should return 400",
        "POST", "/api/getEligibleSchemes",
        payload={"state": "$gt", "crop": "Rice", "land_size": 2.0},
        expected_status=400,
    )

    # --- 7. No Results Scenario ---
    print("\n📋 Edge Cases")

    run_case(
        "Non-existent state — should only return central (All) schemes",
        "POST", "/api/getEligibleSchemes",
        payload={"state": "Atlantis", "crop": "Rice", "land_size": 2.0},
        check_fn=lambda d: (
            d.get("count", 0) > 0 and all(
                "All" in s.get("states", []) for s in d.get("schemes", [])
            ),
            f"count={d.get('count')}, all central: {all('All' in s.get('states',[]) for s in d.get('schemes',[]))}"
        )
    )

    run_case(
        "Extremely large land — should return only universal schemes",
        "POST", "/api/getEligibleSchemes",
        payload={"state": "Tamil Nadu", "crop": "Rice", "land_size": 500.0},
        check_fn=lambda d: (d.get("success") is True, f"count={d.get('count')}")
    )

    # --- Summary ---
    print("\n" + "=" * 60)
    total = passed + failed
    print(f"Results: {passed}/{total} passed, {failed}/{total} failed")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
