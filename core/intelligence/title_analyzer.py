"""
Title Formula Analyzer

Uses LLM (Claude/GPT) to analyze successful article titles
and extract recurring patterns and formulas.
"""

import os
from typing import List, Dict
import json
from anthropic import Anthropic
from openai import OpenAI

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.persistence.database import Database


class TitleAnalyzer:
    """LLM-powered title pattern extraction"""

    def __init__(self, use_claude: bool = True):
        self.db = Database()
        self.use_claude = use_claude

        if use_claude:
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = "claude-sonnet-4-5-20250929"
        else:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4o"

    def analyze_titles(self, niche: str = None, limit: int = 500) -> Dict:
        """
        Analyze article titles using LLM to extract formulas

        Args:
            niche: Specific niche or all
            limit: Max titles to analyze

        Returns:
            Dictionary with formulas and insights
        """
        # Get DNA profiles with titles
        profiles = self.db.get_all_dna_profiles(niche=niche)

        if not profiles:
            print("[Title Analyzer] No articles found")
            return {"error": "No data"}

        # Extract titles
        titles = [p['title'] for p in profiles if p.get('title')][:limit]

        print(f"[Title Analyzer] Analyzing {len(titles)} titles using {self.model}...")

        # Create prompt
        prompt = self._create_analysis_prompt(titles)

        # Get LLM analysis
        if self.use_claude:
            analysis = self._analyze_with_claude(prompt)
        else:
            analysis = self._analyze_with_openai(prompt)

        # Parse and structure results
        result = {
            "niche": niche or "all",
            "sample_size": len(titles),
            "analysis": analysis,
            "model_used": self.model
        }

        # Save results
        self.db.save_title_formulas([result])

        print(f"[Title Analyzer] Complete! Extracted formulas saved.")

        return result

    def _create_analysis_prompt(self, titles: List[str]) -> str:
        """Create prompt for LLM analysis"""
        titles_text = "\n".join([f"{i+1}. {title}" for i, title in enumerate(titles[:200])])

        prompt = f"""Analyze these {len(titles)} article titles from high-performing Google Discover articles.

TITLES:
{titles_text}

Your task: Identify recurring patterns, formulas, and structures that make these titles successful.

Please provide:

1. **Title Formulas** (5-10 patterns)
   - Pattern name
   - Formula structure (e.g., "[Number] + [Adjective] + [Topic]")
   - Example from the list
   - Estimated usage frequency

2. **Key Characteristics**
   - Optimal length (character count)
   - Use of numbers (percentage)
   - Use of questions
   - Use of superlatives (best, most, etc.)
   - Power words commonly used

3. **Topic Themes**
   - Most common subject areas
   - Content angles (discovery, controversy, how-to, etc.)

4. **Dos and Don'ts**
   - What makes titles click-worthy
   - What to avoid

Return your analysis as structured JSON with these sections.
"""

        return prompt

    def _analyze_with_claude(self, prompt: str) -> Dict:
        """Analyze using Claude"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            content = response.content[0].text

            # Try to parse as JSON
            try:
                return json.loads(content)
            except:
                # Return as text if not JSON
                return {"analysis_text": content}

        except Exception as e:
            print(f"[Title Analyzer] Claude error: {e}")
            return {"error": str(e)}

    def _analyze_with_openai(self, prompt: str) -> Dict:
        """Analyze using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.3
            )

            content = response.choices[0].message.content

            # Try to parse as JSON
            try:
                return json.loads(content)
            except:
                return {"analysis_text": content}

        except Exception as e:
            print(f"[Title Analyzer] OpenAI error: {e}")
            return {"error": str(e)}


def main():
    """Test title analyzer"""
    analyzer = TitleAnalyzer(use_claude=True)
    result = analyzer.analyze_titles(limit=100)

    print(f"\n{'='*60}")
    print("TITLE ANALYSIS RESULT")
    print(f"{'='*60}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
