"""
Enhanced DNA Extractor

Extracts comprehensive article DNA with 20+ data points:
- Title analysis (length, patterns, keywords)
- Content structure (word count, images, videos)
- Schema.org markup
- Meta tags
- HTML structure (headings, links)
- Performance metrics
"""

import asyncio
import re
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Page
from playwright_stealth import stealth_async
from urllib.parse import urlparse

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.persistence.database import Database
from core.persistence.models import ArticleDNA


class DNAExtractor:
    """Comprehensive DNA extraction using Playwright"""

    def __init__(self):
        self.db = Database()

    async def extract_article_dna(self, article_id: str, url: str, title: str) -> Optional[ArticleDNA]:
        """
        Extract full DNA profile for an article

        Args:
            article_id: Article ID from database
            url: Article URL
            title: Article title

        Returns:
            ArticleDNA object or None if failed
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)

                # Mobile-first context (Google Discover is mobile)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    viewport={'width': 375, 'height': 812}  # iPhone size
                )

                page = await context.new_page()
                await stealth_async(page)

                print(f"  [DNA] Extracting: {url[:60]}")

                # Load page
                await page.goto(url, wait_until="networkidle", timeout=30000)

                # Extract all DNA components
                dna = await self._extract_all_data_points(page, title)

                await browser.close()

                # Store in database
                self.db.insert_dna_profile(article_id, dna)
                self.db.mark_dna_extracted(article_id)

                print(f"  [DNA] ✓ Complete: {dna.word_count} words, {dna.image_count} images")

                return dna

        except Exception as e:
            print(f"  [DNA] ✗ Error extracting DNA: {e}")
            return None

    async def _extract_all_data_points(self, page: Page, title: str) -> ArticleDNA:
        """Extract all DNA data points from page"""

        # 1. Title Analysis
        title_analysis = self._analyze_title(title)

        # 2. Content metrics
        word_count = await page.evaluate("document.body.innerText.split(/\\s+/).length")

        # 3. Image analysis
        image_data = await self._extract_image_data(page)

        # 4. Video count
        video_count = await page.evaluate("document.querySelectorAll('video, iframe[src*=\"youtube\"], iframe[src*=\"vimeo\"]').length")

        # 5. Schema.org data
        schema_types = await self._extract_schema_types(page)

        # 6. Meta tags
        meta_description = await page.evaluate("document.querySelector('meta[name=\"description\"]')?.content || ''")
        meta_description_length = len(meta_description)

        meta_keywords = await page.evaluate("document.querySelector('meta[name=\"keywords\"]')?.content || ''")
        meta_keywords_count = len(meta_keywords.split(',')) if meta_keywords else 0

        # 7. HTML structure
        h1_count = await page.evaluate("document.querySelectorAll('h1').length")
        h2_count = await page.evaluate("document.querySelectorAll('h2').length")
        h3_count = await page.evaluate("document.querySelectorAll('h3').length")
        subheading_total = h1_count + h2_count + h3_count

        # 8. Links
        internal_links = await self._count_internal_links(page)
        external_links = await page.evaluate("""
            Array.from(document.querySelectorAll('a[href]'))
                .filter(a => a.hostname !== window.location.hostname)
                .length
        """)

        # 9. Author and category
        author = await page.evaluate("""
            document.querySelector('meta[name="author"]')?.content ||
            document.querySelector('[rel="author"]')?.textContent ||
            document.querySelector('.author')?.textContent ||
            null
        """)

        category = await page.evaluate("""
            document.querySelector('meta[property="article:section"]')?.content ||
            document.querySelector('.category')?.textContent ||
            null
        """)

        # 10. Tags
        tags = await self._extract_tags(page)

        # 11. Mobile optimization
        mobile_optimized = await self._check_mobile_optimization(page)

        # Create DNA object
        dna = ArticleDNA(
            # Title
            title=title,
            title_length=title_analysis['length'],
            title_has_number=title_analysis['has_number'],
            title_has_question=title_analysis['has_question'],
            title_has_superlative=title_analysis['has_superlative'],
            title_pattern=title_analysis['pattern'],

            # Content
            word_count=word_count,
            image_count=image_data['count'],
            video_count=video_count,
            first_image_aspect_ratio=image_data['first_aspect_ratio'],
            first_image_format=image_data['first_format'],

            # Schema and meta
            schema_types=schema_types,
            meta_description_length=meta_description_length,
            meta_keywords_count=meta_keywords_count,

            # Structure
            h1_count=h1_count,
            h2_count=h2_count,
            h3_count=h3_count,
            subheading_total=subheading_total,
            internal_links=internal_links,
            external_links=external_links,

            # Performance
            mobile_optimized=mobile_optimized,
            uses_webp=image_data['uses_webp'],

            # Metadata
            author=author[:100] if author else None,
            category=category[:50] if category else None,
            tags=tags
        )

        return dna

    def _analyze_title(self, title: str) -> Dict:
        """Analyze title for patterns"""
        analysis = {
            'length': len(title),
            'has_number': bool(re.search(r'\d+', title)),
            'has_question': '?' in title,
            'has_superlative': False,
            'pattern': None
        }

        # Check for superlatives
        superlatives = ['best', 'worst', 'most', 'least', 'greatest', 'biggest', 'smallest', 'fastest', 'slowest']
        analysis['has_superlative'] = any(word in title.lower() for word in superlatives)

        # Identify pattern
        title_lower = title.lower()
        if re.match(r'^\d+', title):
            analysis['pattern'] = "number_first"
        elif any(word in title_lower for word in ['how to', 'how do', 'why', 'what', 'when', 'where']):
            analysis['pattern'] = "question"
        elif any(word in title_lower for word in ['scientists', 'new study', 'research', 'discovery']):
            analysis['pattern'] = "authority"
        elif analysis['has_superlative']:
            analysis['pattern'] = "superlative"
        else:
            analysis['pattern'] = "generic"

        return analysis

    async def _extract_image_data(self, page: Page) -> Dict:
        """Extract image data and analysis"""
        image_data = await page.evaluate("""() => {
            const images = Array.from(document.querySelectorAll('img'));
            const articleImages = images.filter(img => {
                const src = img.src || '';
                // Filter out icons, logos, ads
                return img.width > 200 && img.height > 100 &&
                       !src.includes('logo') && !src.includes('icon');
            });

            const firstImage = articleImages[0];

            return {
                count: articleImages.length,
                first_width: firstImage ? firstImage.naturalWidth : null,
                first_height: firstImage ? firstImage.naturalHeight : null,
                first_src: firstImage ? firstImage.src : null,
                webp_count: articleImages.filter(img => (img.src || '').includes('.webp')).length
            };
        }""")

        # Calculate aspect ratio
        first_aspect_ratio = None
        if image_data['first_width'] and image_data['first_height']:
            ratio = image_data['first_width'] / image_data['first_height']
            # Common ratios
            if abs(ratio - 16/9) < 0.1:
                first_aspect_ratio = "16:9"
            elif abs(ratio - 4/3) < 0.1:
                first_aspect_ratio = "4:3"
            elif abs(ratio - 1) < 0.1:
                first_aspect_ratio = "1:1"
            else:
                first_aspect_ratio = f"{image_data['first_width']}:{image_data['first_height']}"

        # Get image format
        first_format = None
        if image_data['first_src']:
            src = image_data['first_src'].lower()
            if '.webp' in src:
                first_format = 'webp'
            elif '.jpg' in src or '.jpeg' in src:
                first_format = 'jpg'
            elif '.png' in src:
                first_format = 'png'
            elif '.gif' in src:
                first_format = 'gif'

        return {
            'count': image_data['count'],
            'first_aspect_ratio': first_aspect_ratio,
            'first_format': first_format,
            'uses_webp': image_data['webp_count'] > 0
        }

    async def _extract_schema_types(self, page: Page) -> List[str]:
        """Extract Schema.org types"""
        try:
            schema_types = await page.evaluate("""() => {
                const scripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
                const types = [];

                scripts.forEach(script => {
                    try {
                        const data = JSON.parse(script.innerText);
                        if (data['@type']) {
                            if (Array.isArray(data['@type'])) {
                                types.push(...data['@type']);
                            } else {
                                types.push(data['@type']);
                            }
                        }
                    } catch (e) {}
                });

                return [...new Set(types)];
            }""")
            return schema_types or []
        except:
            return []

    async def _count_internal_links(self, page: Page) -> int:
        """Count internal links"""
        try:
            count = await page.evaluate("""
                Array.from(document.querySelectorAll('a[href]'))
                    .filter(a => a.hostname === window.location.hostname &&
                                 a.pathname !== window.location.pathname)
                    .length
            """)
            return count
        except:
            return 0

    async def _extract_tags(self, page: Page) -> List[str]:
        """Extract article tags"""
        try:
            tags = await page.evaluate("""
                const tagElements = Array.from(document.querySelectorAll('[rel="tag"], .tag, .tags a'));
                return tagElements.slice(0, 10).map(el => el.textContent.trim());
            """)
            return [t for t in tags if t] if tags else []
        except:
            return []

    async def _check_mobile_optimization(self, page: Page) -> bool:
        """Check if page is mobile-optimized"""
        try:
            is_responsive = await page.evaluate("""
                const viewport = document.querySelector('meta[name="viewport"]');
                return viewport && viewport.content.includes('width=device-width');
            """)
            return bool(is_responsive)
        except:
            return False


async def main():
    """Test DNA extraction"""
    extractor = DNAExtractor()

    # Test URL
    test_url = "https://www.space.com/"
    test_title = "Test Article"

    dna = await extractor.extract_article_dna("test_123", test_url, test_title)

    if dna:
        print(f"\nDNA Extraction Result:")
        print(f"  Word count: {dna.word_count}")
        print(f"  Images: {dna.image_count}")
        print(f"  Schema types: {dna.schema_types}")
        print(f"  Title pattern: {dna.title_pattern}")


if __name__ == "__main__":
    asyncio.run(main())
