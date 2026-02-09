#!/usr/bin/env python3
"""
Discover DNA Extractor
======================
Extracts 25 data points from each article captured by the Chrome extension.
Outputs to CSV for analysis.

Usage:
    python scripts/extract_discover_dna.py
    python scripts/extract_discover_dna.py --limit 10  # Process only 10 articles
"""

import asyncio
import csv
import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: Playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

# Output paths
OUTPUT_DIR = Path("data/dna_analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class DiscoverDNAExtractor:
    """Extract comprehensive DNA from Discover articles"""

    def __init__(self):
        self.results = []
        self.errors = []

    def analyze_title(self, title: str) -> Dict:
        """Analyze title for patterns"""
        if not title:
            return {
                'title_length': 0,
                'title_word_count': 0,
                'title_has_number': False,
                'title_has_question': False,
                'title_has_superlative': False,
                'title_pattern': 'unknown'
            }

        superlatives = ['best', 'worst', 'most', 'least', 'greatest', 'biggest',
                       'smallest', 'fastest', 'top', 'ultimate', 'essential', 'amazing']

        title_lower = title.lower()
        has_number = bool(re.search(r'\d+', title))
        has_question = '?' in title
        has_superlative = any(word in title_lower for word in superlatives)

        # Determine pattern
        if re.match(r'^\d+', title):
            pattern = "number_first"
        elif has_question or any(w in title_lower for w in ['how to', 'how do', 'why ', 'what ', 'when ', 'where ']):
            pattern = "question"
        elif any(w in title_lower for w in ['breaking', 'just in', 'exclusive']):
            pattern = "breaking_news"
        elif any(w in title_lower for w in ['new ', 'announces', 'launches', 'reveals', 'unveiled']):
            pattern = "announcement"
        elif has_superlative:
            pattern = "superlative"
        elif any(w in title_lower for w in ['review', 'hands-on', 'first look']):
            pattern = "review"
        else:
            pattern = "statement"

        return {
            'title_length': len(title),
            'title_word_count': len(title.split()),
            'title_has_number': has_number,
            'title_has_question': has_question,
            'title_has_superlative': has_superlative,
            'title_pattern': pattern
        }

    async def extract_page_data(self, page, url: str) -> Dict:
        """Extract all data points from a page"""

        data = {
            'url': url,
            'domain': urlparse(url).netloc,
            'extracted_at': datetime.now().isoformat()
        }

        try:
            # Get page title
            page_title = await page.title()
            data['page_title'] = page_title
            data.update(self.analyze_title(page_title))

            # Word count
            data['word_count'] = await page.evaluate("""
                () => {
                    const article = document.querySelector('article') || document.body;
                    return article.innerText.split(/\\s+/).filter(w => w.length > 0).length;
                }
            """)

            # Image analysis
            image_data = await page.evaluate("""
                () => {
                    const images = Array.from(document.querySelectorAll('img'));
                    const contentImages = images.filter(img => {
                        const w = img.naturalWidth || img.width;
                        const h = img.naturalHeight || img.height;
                        return w > 150 && h > 100;
                    });

                    const first = contentImages[0];
                    return {
                        count: contentImages.length,
                        first_width: first ? (first.naturalWidth || first.width) : null,
                        first_height: first ? (first.naturalHeight || first.height) : null,
                        first_src: first ? first.src : null,
                        webp_count: images.filter(img => (img.src || '').includes('.webp')).length
                    };
                }
            """)

            data['image_count'] = image_data['count']
            data['uses_webp'] = image_data['webp_count'] > 0

            # Calculate aspect ratio
            if image_data['first_width'] and image_data['first_height'] and image_data['first_height'] > 0:
                ratio = image_data['first_width'] / image_data['first_height']
                if abs(ratio - 16/9) < 0.15:
                    data['first_image_ratio'] = "16:9"
                elif abs(ratio - 4/3) < 0.15:
                    data['first_image_ratio'] = "4:3"
                elif abs(ratio - 1) < 0.15:
                    data['first_image_ratio'] = "1:1"
                elif abs(ratio - 2.35) < 0.15:
                    data['first_image_ratio'] = "21:9"
                else:
                    data['first_image_ratio'] = f"{ratio:.2f}:1"
            else:
                data['first_image_ratio'] = None

            # Image format
            if image_data['first_src']:
                src = image_data['first_src'].lower()
                if '.webp' in src or 'format=webp' in src:
                    data['first_image_format'] = 'webp'
                elif '.jpg' in src or '.jpeg' in src:
                    data['first_image_format'] = 'jpg'
                elif '.png' in src:
                    data['first_image_format'] = 'png'
                elif '.gif' in src:
                    data['first_image_format'] = 'gif'
                elif '.avif' in src:
                    data['first_image_format'] = 'avif'
                else:
                    data['first_image_format'] = 'unknown'
            else:
                data['first_image_format'] = None

            # Video count
            data['video_count'] = await page.evaluate("""
                document.querySelectorAll('video, iframe[src*="youtube"], iframe[src*="vimeo"], iframe[src*="dailymotion"]').length
            """)

            # Schema.org types
            schema_types = await page.evaluate("""
                () => {
                    const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                    const types = [];
                    scripts.forEach(s => {
                        try {
                            const data = JSON.parse(s.textContent);
                            const addType = (obj) => {
                                if (obj['@type']) {
                                    if (Array.isArray(obj['@type'])) types.push(...obj['@type']);
                                    else types.push(obj['@type']);
                                }
                                if (obj['@graph']) obj['@graph'].forEach(addType);
                            };
                            addType(data);
                        } catch(e) {}
                    });
                    return [...new Set(types)];
                }
            """)
            data['schema_types'] = ','.join(schema_types) if schema_types else ''
            data['has_article_schema'] = any('Article' in t for t in schema_types)
            data['has_newsarticle_schema'] = 'NewsArticle' in schema_types

            # Meta tags
            data['meta_description_length'] = await page.evaluate("""
                (document.querySelector('meta[name="description"]')?.content || '').length
            """)

            meta_keywords = await page.evaluate("""
                document.querySelector('meta[name="keywords"]')?.content || ''
            """)
            data['meta_keywords_count'] = len([k for k in meta_keywords.split(',') if k.strip()]) if meta_keywords else 0

            # HTML structure
            data['h1_count'] = await page.evaluate("document.querySelectorAll('h1').length")
            data['h2_count'] = await page.evaluate("document.querySelectorAll('h2').length")
            data['h3_count'] = await page.evaluate("document.querySelectorAll('h3').length")
            data['total_headings'] = data['h1_count'] + data['h2_count'] + data['h3_count']

            # Links
            link_data = await page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    const internal = links.filter(a => a.hostname === window.location.hostname).length;
                    const external = links.filter(a => a.hostname !== window.location.hostname && a.href.startsWith('http')).length;
                    return { internal, external };
                }
            """)
            data['internal_links'] = link_data['internal']
            data['external_links'] = link_data['external']

            # Mobile optimization
            data['mobile_optimized'] = await page.evaluate("""
                () => {
                    const vp = document.querySelector('meta[name="viewport"]');
                    return vp && vp.content.includes('width=device-width');
                }
            """)

            # Author
            author = await page.evaluate("""
                document.querySelector('meta[name="author"]')?.content ||
                document.querySelector('[rel="author"]')?.textContent ||
                document.querySelector('.author-name, .author, .byline')?.textContent ||
                ''
            """)
            data['author'] = author.strip()[:100] if author else ''

            # Category
            category = await page.evaluate("""
                document.querySelector('meta[property="article:section"]')?.content ||
                document.querySelector('.category, .section-name, nav.breadcrumb a')?.textContent ||
                ''
            """)
            data['category'] = category.strip()[:50] if category else ''

            # Published date
            pub_date = await page.evaluate("""
                document.querySelector('meta[property="article:published_time"]')?.content ||
                document.querySelector('time[datetime]')?.getAttribute('datetime') ||
                ''
            """)
            data['published_date'] = pub_date

            # Ads detection
            data['has_ads'] = await page.evaluate("""
                document.querySelectorAll('[class*="ad-"], [id*="google_ads"], .advertisement, ins.adsbygoogle').length > 0
            """)

            # Reading time estimate (assuming 200 words per minute)
            data['reading_time_mins'] = round(data['word_count'] / 200, 1)

            # Social sharing buttons
            data['has_social_share'] = await page.evaluate("""
                document.querySelectorAll('[class*="share"], [class*="social"], .addtoany, .shareaholic').length > 0
            """)

            # Comments section
            data['has_comments'] = await page.evaluate("""
                document.querySelectorAll('#comments, .comments, [id*="disqus"], .comment-section').length > 0
            """)

            data['extraction_status'] = 'success'

        except Exception as e:
            data['extraction_status'] = 'error'
            data['error_message'] = str(e)[:200]

        return data

    async def process_url(self, browser, url: str, title: str, position: int, total: int) -> Dict:
        """Process a single URL"""
        print(f"  [{position}/{total}] Processing: {url[:60]}...")

        try:
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
                viewport={'width': 375, 'height': 812}
            )
            page = await context.new_page()

            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)  # Wait for JS to load

            data = await self.extract_page_data(page, url)
            data['original_title'] = title
            data['discover_position'] = position

            print(f"       {data['word_count']} words, {data['image_count']} imgs, schema: {data.get('has_article_schema', False)}")
            return data

        except Exception as e:
            print(f"       Error: {str(e)[:50]}")
            return {
                'url': url,
                'domain': urlparse(url).netloc,
                'original_title': title,
                'discover_position': position,
                'extraction_status': 'error',
                'error_message': str(e)[:200]
            }
        finally:
            try:
                await context.close()
            except Exception:
                pass

    async def run(self, limit: int = None):
        """Run DNA extraction on all captured URLs"""

        # Load captured sites
        sites_path = Path("data/competitors/discovered_sites.json")
        if not sites_path.exists():
            print("Error: No captured sites found. Run the Chrome extension first.")
            return

        with open(sites_path) as f:
            sites = json.load(f)

        if not sites:
            print("Error: No sites in discovered_sites.json")
            return

        if limit:
            sites = sites[:limit]

        print(f"\n{'='*60}")
        print("DISCOVER DNA EXTRACTOR")
        print(f"{'='*60}")
        print(f"Sites to process: {len(sites)}")
        print(f"Output: {OUTPUT_DIR}/discover_dna.csv")
        print(f"{'='*60}\n")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            for i, site in enumerate(sites, 1):
                url = site.get('url', '')
                title = site.get('metadata', {}).get('sample_title', '')

                if not url:
                    continue

                data = await self.process_url(browser, url, title, i, len(sites))
                self.results.append(data)

                # Small delay between requests
                await asyncio.sleep(1)

            await browser.close()

        # Save results
        self.save_csv()
        self.print_summary()

    def save_csv(self):
        """Save results to CSV"""
        if not self.results:
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        csv_path = OUTPUT_DIR / f"discover_dna_{timestamp}.csv"

        # Get all unique keys
        all_keys = set()
        for r in self.results:
            all_keys.update(r.keys())

        # Define column order
        ordered_cols = [
            'discover_position', 'domain', 'url', 'original_title', 'page_title',
            'title_length', 'title_word_count', 'title_has_number', 'title_has_question',
            'title_has_superlative', 'title_pattern',
            'word_count', 'reading_time_mins', 'image_count', 'video_count',
            'first_image_ratio', 'first_image_format', 'uses_webp',
            'schema_types', 'has_article_schema', 'has_newsarticle_schema',
            'meta_description_length', 'meta_keywords_count',
            'h1_count', 'h2_count', 'h3_count', 'total_headings',
            'internal_links', 'external_links',
            'mobile_optimized', 'has_ads', 'has_social_share', 'has_comments',
            'author', 'category', 'published_date',
            'extraction_status', 'extracted_at'
        ]

        # Add any missing keys
        for key in sorted(all_keys):
            if key not in ordered_cols and key != 'error_message':
                ordered_cols.append(key)

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=ordered_cols, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.results)

        print(f"\nSaved to: {csv_path}")

        # Also save latest version
        latest_path = OUTPUT_DIR / "discover_dna_latest.csv"
        with open(latest_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=ordered_cols, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.results)

    def print_summary(self):
        """Print extraction summary and insights"""
        successful = [r for r in self.results if r.get('extraction_status') == 'success']

        if not successful:
            print("\nNo successful extractions.")
            return

        print(f"\n{'='*60}")
        print("DNA EXTRACTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total processed: {len(self.results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(self.results) - len(successful)}")

        # Averages
        avg_words = sum(r.get('word_count', 0) for r in successful) / len(successful)
        avg_images = sum(r.get('image_count', 0) for r in successful) / len(successful)
        avg_h2 = sum(r.get('h2_count', 0) for r in successful) / len(successful)

        print("\n--- CONTENT AVERAGES ---")
        print(f"Avg word count: {avg_words:.0f}")
        print(f"Avg images: {avg_images:.1f}")
        print(f"Avg H2 headings: {avg_h2:.1f}")

        # Title patterns
        patterns = {}
        for r in successful:
            p = r.get('title_pattern', 'unknown')
            patterns[p] = patterns.get(p, 0) + 1

        print("\n--- TITLE PATTERNS ---")
        for p, count in sorted(patterns.items(), key=lambda x: -x[1]):
            pct = count / len(successful) * 100
            print(f"{p}: {count} ({pct:.0f}%)")

        # Schema usage
        article_schema = sum(1 for r in successful if r.get('has_article_schema'))
        news_schema = sum(1 for r in successful if r.get('has_newsarticle_schema'))

        print("\n--- SCHEMA MARKUP ---")
        print(f"Has Article schema: {article_schema}/{len(successful)} ({article_schema/len(successful)*100:.0f}%)")
        print(f"Has NewsArticle schema: {news_schema}/{len(successful)} ({news_schema/len(successful)*100:.0f}%)")

        # Mobile optimization
        mobile = sum(1 for r in successful if r.get('mobile_optimized'))
        print("\n--- TECHNICAL ---")
        print(f"Mobile optimized: {mobile}/{len(successful)} ({mobile/len(successful)*100:.0f}%)")

        webp = sum(1 for r in successful if r.get('uses_webp'))
        print(f"Uses WebP images: {webp}/{len(successful)} ({webp/len(successful)*100:.0f}%)")

        print(f"\n{'='*60}")
        print("SECRET SAUCE INSIGHTS")
        print(f"{'='*60}")
        print("""
Based on DNA extraction from Google Discover articles:

1. CONTENT LENGTH: Target {:.0f} words (avg from successful Discover articles)
2. IMAGES: Use {:.0f}+ high-quality images per article
3. HEADINGS: Structure with {:.0f}+ H2 subheadings
4. SCHEMA: {:.0f}% use Article/NewsArticle schema - THIS IS CRITICAL
5. MOBILE: {:.0f}% are mobile-optimized - REQUIRED for Discover
6. TITLE PATTERN: Most common = "{}"
        """.format(
            avg_words,
            avg_images,
            avg_h2,
            (article_schema / len(successful) * 100) if successful else 0,
            (mobile / len(successful) * 100) if successful else 0,
            max(patterns.keys(), key=lambda k: patterns[k]) if patterns else "N/A"
        ))


async def main():
    parser = argparse.ArgumentParser(description='Extract DNA from Discover articles')
    parser.add_argument('--limit', type=int, help='Limit number of articles to process')
    args = parser.parse_args()

    extractor = DiscoverDNAExtractor()
    await extractor.run(limit=args.limit)


if __name__ == "__main__":
    asyncio.run(main())
