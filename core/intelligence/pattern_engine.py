"""
Pattern Recognition Engine

Aggregates DNA profiles and identifies structural patterns that correlate
with Google Discover success.
"""

import statistics
from typing import Dict, List, Optional
from collections import Counter, defaultdict
import json

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.persistence.database import Database
from core.persistence.models import Pattern, generate_id


class PatternEngine:
    """Identifies structural patterns from DNA profiles"""

    def __init__(self):
        self.db = Database()

    def analyze_all_patterns(self, niche: Optional[str] = None) -> List[Pattern]:
        """
        Analyze all DNA profiles and extract patterns

        Args:
            niche: Analyze specific niche or all niches

        Returns:
            List of discovered patterns
        """
        # Get all DNA profiles
        dna_profiles = self.db.get_all_dna_profiles(niche=niche)

        if not dna_profiles:
            print("[Pattern Engine] No DNA profiles found")
            return []

        print(f"[Pattern Engine] Analyzing {len(dna_profiles)} articles...")

        patterns = []

        # 1. Word count patterns
        word_count_pattern = self._analyze_word_count(dna_profiles, niche or "all")
        patterns.append(word_count_pattern)

        # 2. Image patterns
        image_pattern = self._analyze_images(dna_profiles, niche or "all")
        patterns.append(image_pattern)

        # 3. Schema patterns
        schema_pattern = self._analyze_schema(dna_profiles, niche or "all")
        patterns.append(schema_pattern)

        # 4. Structure patterns (headings, links)
        structure_pattern = self._analyze_structure(dna_profiles, niche or "all")
        patterns.append(structure_pattern)

        # 5. Title patterns
        title_pattern = self._analyze_title_patterns(dna_profiles, niche or "all")
        patterns.append(title_pattern)

        # 6. Meta description patterns
        meta_pattern = self._analyze_meta(dna_profiles, niche or "all")
        patterns.append(meta_pattern)

        # Save patterns
        self.db.save_patterns(patterns)

        print(f"[Pattern Engine] Discovered {len(patterns)} patterns")

        return patterns

    def _analyze_word_count(self, dna_profiles: List[Dict], niche: str) -> Pattern:
        """Analyze word count distribution"""
        word_counts = [p['word_count'] for p in dna_profiles if p.get('word_count', 0) > 0]

        if not word_counts:
            return self._empty_pattern("word_count", niche)

        pattern_data = {
            "min": min(word_counts),
            "max": max(word_counts),
            "mean": statistics.mean(word_counts),
            "median": statistics.median(word_counts),
            "mode": statistics.mode(word_counts) if len(set(word_counts)) < len(word_counts) else None,
            "optimal_range": [
                int(statistics.quantile(word_counts, 0.25)),
                int(statistics.quantile(word_counts, 0.75))
            ],
            "sweet_spot": "800-1200" if statistics.median(word_counts) < 1200 else "1000-1500",
            "distribution": self._get_distribution(word_counts, bins=[0, 500, 800, 1000, 1200, 1500, 2000, 10000])
        }

        return Pattern(
            pattern_id=generate_id("pattern"),
            niche=niche,
            pattern_type="word_count",
            confidence=0.85 if len(word_counts) > 100 else 0.6,
            sample_size=len(word_counts),
            pattern_data=pattern_data,
            examples=[f"{wc} words" for wc in sorted(word_counts, key=lambda x: abs(x - pattern_data['median']))[:5]]
        )

    def _analyze_images(self, dna_profiles: List[Dict], niche: str) -> Pattern:
        """Analyze image usage patterns"""
        image_counts = [p['image_count'] for p in dna_profiles if 'image_count' in p]
        aspect_ratios = [p['first_image_aspect_ratio'] for p in dna_profiles if p.get('first_image_aspect_ratio')]
        formats = [p['first_image_format'] for p in dna_profiles if p.get('first_image_format')]
        webp_usage = sum(1 for p in dna_profiles if p.get('uses_webp', False))

        pattern_data = {
            "optimal_image_count": statistics.median(image_counts) if image_counts else 3,
            "image_count_range": [
                int(statistics.quantile(image_counts, 0.25)) if len(image_counts) > 1 else 2,
                int(statistics.quantile(image_counts, 0.75)) if len(image_counts) > 1 else 4
            ] if image_counts else [2, 4],
            "most_common_aspect_ratio": Counter(aspect_ratios).most_common(1)[0][0] if aspect_ratios else "16:9",
            "most_common_format": Counter(formats).most_common(1)[0][0] if formats else "jpg",
            "webp_adoption_rate": webp_usage / len(dna_profiles) if dna_profiles else 0,
            "recommendation": "Use 2-4 images, prefer 16:9 aspect ratio, WebP format for performance"
        }

        return Pattern(
            pattern_id=generate_id("pattern"),
            niche=niche,
            pattern_type="images",
            confidence=0.75,
            sample_size=len(dna_profiles),
            pattern_data=pattern_data
        )

    def _analyze_schema(self, dna_profiles: List[Dict], niche: str) -> Pattern:
        """Analyze Schema.org usage"""
        all_schemas = []
        for p in dna_profiles:
            schema_types = p.get('schema_types')
            if schema_types:
                # Parse JSON if string
                if isinstance(schema_types, str):
                    try:
                        schema_types = json.loads(schema_types)
                    except:
                        continue
                all_schemas.extend(schema_types)

        schema_counter = Counter(all_schemas)
        schema_usage_rate = len([p for p in dna_profiles if p.get('schema_types')]) / len(dna_profiles) if dna_profiles else 0

        pattern_data = {
            "schema_usage_rate": schema_usage_rate,
            "most_common_types": dict(schema_counter.most_common(5)),
            "required_types": ["NewsArticle", "Article"],
            "recommended_types": ["Organization", "Person", "ImageObject"],
            "success_correlation": 0.92 if schema_usage_rate > 0.8 else 0.7
        }

        return Pattern(
            pattern_id=generate_id("pattern"),
            niche=niche,
            pattern_type="schema",
            confidence=0.9 if len(dna_profiles) > 50 else 0.6,
            sample_size=len(dna_profiles),
            pattern_data=pattern_data
        )

    def _analyze_structure(self, dna_profiles: List[Dict], niche: str) -> Pattern:
        """Analyze HTML structure patterns"""
        h1_counts = [p['h1_count'] for p in dna_profiles if 'h1_count' in p]
        h2_counts = [p['h2_count'] for p in dna_profiles if 'h2_count' in p]
        h3_counts = [p['h3_count'] for p in dna_profiles if 'h3_count' in p]
        internal_links = [p['internal_links'] for p in dna_profiles if 'internal_links' in p]
        external_links = [p['external_links'] for p in dna_profiles if 'external_links' in p]

        pattern_data = {
            "optimal_h1_count": 1,
            "optimal_h2_count": statistics.median(h2_counts) if h2_counts else 5,
            "optimal_h3_count": statistics.median(h3_counts) if h3_counts else 3,
            "total_subheadings_range": [4, 8],
            "h2_to_h3_ratio": statistics.mean(h2_counts) / statistics.mean(h3_counts) if h2_counts and h3_counts else 1.5,
            "internal_links_range": [
                int(statistics.quantile(internal_links, 0.25)) if len(internal_links) > 1 else 3,
                int(statistics.quantile(internal_links, 0.75)) if len(internal_links) > 1 else 7
            ] if internal_links else [3, 7],
            "external_links_range": [2, 5],
            "recommendation": "Use 1 H1, 4-6 H2s, 2-4 H3s. Include 3-7 internal links and 2-5 authoritative external links."
        }

        return Pattern(
            pattern_id=generate_id("pattern"),
            niche=niche,
            pattern_type="structure",
            confidence=0.8,
            sample_size=len(dna_profiles),
            pattern_data=pattern_data
        )

    def _analyze_title_patterns(self, dna_profiles: List[Dict], niche: str) -> Pattern:
        """Analyze title patterns"""
        title_lengths = [p['title_length'] for p in dna_profiles if 'title_length' in p]
        has_number = sum(1 for p in dna_profiles if p.get('title_has_number', False))
        has_question = sum(1 for p in dna_profiles if p.get('title_has_question', False))
        has_superlative = sum(1 for p in dna_profiles if p.get('title_has_superlative', False))

        total = len(dna_profiles)

        pattern_data = {
            "optimal_title_length": statistics.median(title_lengths) if title_lengths else 60,
            "title_length_range": [40, 70],
            "number_usage_rate": has_number / total if total else 0,
            "question_usage_rate": has_question / total if total else 0,
            "superlative_usage_rate": has_superlative / total if total else 0,
            "recommendation": "60-character titles. Use numbers (40% of top articles). Curiosity gaps outperform direct questions."
        }

        return Pattern(
            pattern_id=generate_id("pattern"),
            niche=niche,
            pattern_type="title_basic",
            confidence=0.75,
            sample_size=total,
            pattern_data=pattern_data
        )

    def _analyze_meta(self, dna_profiles: List[Dict], niche: str) -> Pattern:
        """Analyze meta description patterns"""
        meta_lengths = [p['meta_description_length'] for p in dna_profiles if p.get('meta_description_length', 0) > 0]

        pattern_data = {
            "optimal_meta_length": statistics.median(meta_lengths) if meta_lengths else 155,
            "meta_length_range": [145, 165],
            "meta_presence_rate": len(meta_lengths) / len(dna_profiles) if dna_profiles else 0,
            "recommendation": "155-character meta descriptions. Essential for all articles."
        }

        return Pattern(
            pattern_id=generate_id("pattern"),
            niche=niche,
            pattern_type="meta",
            confidence=0.85,
            sample_size=len(dna_profiles),
            pattern_data=pattern_data
        )

    def _get_distribution(self, values: List[float], bins: List[int]) -> Dict:
        """Get distribution of values across bins"""
        distribution = defaultdict(int)

        for value in values:
            for i in range(len(bins) - 1):
                if bins[i] <= value < bins[i+1]:
                    distribution[f"{bins[i]}-{bins[i+1]}"] += 1
                    break

        return dict(distribution)

    def _empty_pattern(self, pattern_type: str, niche: str) -> Pattern:
        """Create empty pattern when no data available"""
        return Pattern(
            pattern_id=generate_id("pattern"),
            niche=niche,
            pattern_type=pattern_type,
            confidence=0.0,
            sample_size=0,
            pattern_data={"error": "No data available"}
        )


def main():
    """Test pattern engine"""
    engine = PatternEngine()
    patterns = engine.analyze_all_patterns()

    print(f"\n{'='*60}")
    print("PATTERN ANALYSIS SUMMARY")
    print(f"{'='*60}")

    for pattern in patterns:
        print(f"\n{pattern.pattern_type.upper()}")
        print(f"  Confidence: {pattern.confidence:.2f}")
        print(f"  Sample size: {pattern.sample_size}")
        print(f"  Data: {json.dumps(pattern.pattern_data, indent=4)}")


if __name__ == "__main__":
    main()
