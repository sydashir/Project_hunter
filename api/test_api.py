#!/usr/bin/env python3
"""
Test script for Discover API

Run this to verify the API is working correctly before using the extension.
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_api():
    """Test all API endpoints"""

    print("Testing Discover API")
    print("="*60)

    # Test 1: Health check
    print("\n1. Testing API availability...")
    try:
        response = requests.get(f"{API_BASE}/api/discover/stats")
        if response.status_code == 200:
            print("   ✓ API is running")
            print(f"   Current stats: {response.json()}")
        else:
            print(f"   ✗ API returned status {response.status_code}")
            return
    except Exception as e:
        print(f"   ✗ Cannot connect to API: {e}")
        print("   Make sure to run: python api/discover_api.py")
        return

    # Test 2: Reset (clean slate)
    print("\n2. Resetting test data...")
    response = requests.post(f"{API_BASE}/api/discover/reset")
    if response.status_code == 200:
        print("   ✓ Reset successful")
    else:
        print(f"   ✗ Reset failed: {response.status_code}")

    # Test 3: Submit test articles
    print("\n3. Submitting test articles...")
    test_articles = [
        {
            "domain": "techcrunch.com",
            "url": "https://techcrunch.com/2024/01/01/test-article",
            "title": "AI Breakthrough in Natural Language Processing",
            "position": 0,
            "timestamp": datetime.now().isoformat()
        },
        {
            "domain": "forbes.com",
            "url": "https://forbes.com/2024/01/01/business-news",
            "title": "Top Business Trends for 2024",
            "position": 1,
            "timestamp": datetime.now().isoformat()
        },
        {
            "domain": "healthline.com",
            "url": "https://healthline.com/nutrition/healthy-diet",
            "title": "10 Tips for Healthy Eating",
            "position": 2,
            "timestamp": datetime.now().isoformat()
        }
    ]

    for article in test_articles:
        response = requests.post(
            f"{API_BASE}/api/discover/article",
            json=article
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Added: {article['domain']} (total: {result['total_discovered']})")
        else:
            print(f"   ✗ Failed to add {article['domain']}: {response.status_code}")

    # Test 4: Verify stats
    print("\n4. Verifying statistics...")
    response = requests.get(f"{API_BASE}/api/discover/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✓ Total domains: {stats['total_domains']}")
        print(f"   ✓ Domains: {', '.join(stats['domains'])}")
    else:
        print(f"   ✗ Failed to get stats: {response.status_code}")

    # Test 5: Submit duplicate (should be filtered)
    print("\n5. Testing duplicate filtering...")
    duplicate = test_articles[0]  # Submit first article again
    response = requests.post(
        f"{API_BASE}/api/discover/article",
        json=duplicate
    )
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'duplicate':
            print(f"   ✓ Duplicate detected and filtered: {duplicate['domain']}")
        else:
            print(f"   ✗ Duplicate not filtered: {result}")
    else:
        print(f"   ✗ Duplicate test failed: {response.status_code}")

    # Test 6: Check database
    print("\n6. Checking database storage...")
    try:
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        from core.persistence.database import Database

        db = Database()
        competitors = db.load_competitors()
        extension_competitors = [
            c for c in competitors
            if c.discovery_source == "chrome_extension"
        ]

        print(f"   ✓ Database loaded: {len(extension_competitors)} extension competitors")

        if extension_competitors:
            print(f"\n   Sample competitor:")
            sample = extension_competitors[0]
            print(f"     Domain: {sample.domain}")
            print(f"     Niche: {sample.niche}")
            print(f"     Position: {sample.metadata.get('discover_position', 'N/A')}")
            print(f"     Source: {sample.discovery_source}")
    except Exception as e:
        print(f"   ✗ Database check failed: {e}")

    print("\n" + "="*60)
    print("API TEST COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Install Chrome extension (see chrome_extension/README.md)")
    print("2. Browse Google Discover for 30-60 minutes")
    print("3. Run: python scripts/run_discovery.py")

if __name__ == "__main__":
    test_api()
