"""
AI-powered semantic comparison module for Drawing Comparator.
Uses OpenAI GPT models to provide intelligent, context-aware comparison of technical drawings.
"""

import os
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import openai
from openai import OpenAI

@dataclass
class SemanticComparisonResult:
    """Enhanced comparison result with semantic analysis."""
    similarity_score: float  # 0.0 to 1.0
    confidence: float  # How confident the AI is in its assessment
    semantic_differences: List[str]  # High-level meaningful differences
    technical_analysis: Dict[str, any]  # Detailed technical comparison
    reasoning: str  # AI's explanation of the comparison
    categories: Dict[str, float]  # Similarity scores by category
    timestamp: str
    raw_similarity: float  # Original difflib similarity for comparison

class SemanticComparator:
    """AI-powered semantic comparison for technical drawings."""
    
    def __init__(self, api_key: str = None):
        """Initialize with OpenAI API key."""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Comparison categories for technical drawings
        self.categories = {
            "structural_elements": "Beams, columns, foundations, supports",
            "dimensions": "Measurements, sizes, specifications",
            "materials": "Material types, grades, properties",
            "annotations": "Labels, notes, callouts, legends",
            "symbols": "Standard symbols, notations, markers",
            "layout": "Overall arrangement and spatial relationships",
            "details": "Technical details, connections, joints",
            "calculations": "Load calculations, design values, formulas"
        }
    
    def create_comparison_prompt(self, text1: str, text2: str) -> str:
        """Create a detailed prompt for GPT to compare technical drawings."""
        return f"""
You are an expert structural engineer analyzing two technical drawings. Compare the extracted text from these drawings and provide a comprehensive analysis.

DRAWING 1 TEXT:
{text1[:4000]}  # Limit to avoid token limits

DRAWING 2 TEXT:
{text2[:4000]}  # Limit to avoid token limits

Please provide a detailed comparison in the following JSON format:

{{
    "similarity_score": <float between 0.0 and 1.0>,
    "confidence": <float between 0.0 and 1.0 indicating how confident you are>,
    "reasoning": "<detailed explanation of your analysis>",
    "semantic_differences": [
        "<meaningful difference 1>",
        "<meaningful difference 2>",
        "..."
    ],
    "technical_analysis": {{
        "major_differences": ["<list of significant technical differences>"],
        "minor_differences": ["<list of minor differences>"],
        "common_elements": ["<list of shared elements>"],
        "critical_discrepancies": ["<safety or code-critical differences>"]
    }},
    "categories": {{
        "structural_elements": <similarity score 0.0-1.0>,
        "dimensions": <similarity score 0.0-1.0>,
        "materials": <similarity score 0.0-1.0>,
        "annotations": <similarity score 0.0-1.0>,
        "symbols": <similarity score 0.0-1.0>,
        "layout": <similarity score 0.0-1.0>,
        "details": <similarity score 0.0-1.0>,
        "calculations": <similarity score 0.0-1.0>
    }}
}}

ANALYSIS GUIDELINES:
1. Focus on SEMANTIC meaning, not just text similarity
2. Consider technical context and engineering significance
3. Weigh structural elements and safety-critical items more heavily
4. Account for different ways of expressing the same concept
5. Consider drawing standards and conventions
6. Identify functionally equivalent but differently expressed elements
7. Flag critical discrepancies that could affect safety or compliance

Provide only the JSON response, no additional text.
"""
    
    def create_simple_comparison_prompt(self, text1: str, text2: str) -> str:
        """Create a simpler prompt for basic comparison."""
        return f"""
Compare these two technical drawing texts and rate their similarity from 0% to 100%.

Drawing 1: {text1[:2000]}
Drawing 2: {text2[:2000]}

Consider:
- Structural elements (beams, columns, etc.)
- Dimensions and measurements
- Materials and specifications
- Overall design intent

Respond with only a JSON object:
{{
    "similarity_percentage": <number 0-100>,
    "main_differences": ["<difference 1>", "<difference 2>"],
    "explanation": "<brief explanation>"
}}
"""
    
    def compare_with_gpt(self, text1: str, text2: str, model: str = "gpt-4o") -> SemanticComparisonResult:
        """Use GPT to perform semantic comparison of drawing texts."""
        try:
            # Try detailed analysis first
            prompt = self.create_comparison_prompt(text1, text2)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert structural engineer and technical drawing analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent analysis
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                result_data = json.loads(result_text)
            except json.JSONDecodeError:
                # Fallback to simple comparison if JSON parsing fails
                return self._fallback_simple_comparison(text1, text2, model)
            
            # Calculate raw similarity for comparison
            import difflib
            raw_similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
            
            return SemanticComparisonResult(
                similarity_score=result_data.get("similarity_score", 0.0),
                confidence=result_data.get("confidence", 0.0),
                semantic_differences=result_data.get("semantic_differences", []),
                technical_analysis=result_data.get("technical_analysis", {}),
                reasoning=result_data.get("reasoning", ""),
                categories=result_data.get("categories", {}),
                timestamp=datetime.now().isoformat(),
                raw_similarity=raw_similarity
            )
            
        except Exception as e:
            # Fallback to simple comparison if detailed analysis fails
            print(f"Detailed analysis failed: {e}")
            return self._fallback_simple_comparison(text1, text2, model)
    
    def _fallback_simple_comparison(self, text1: str, text2: str, model: str) -> SemanticComparisonResult:
        """Fallback to simple comparison if detailed analysis fails."""
        try:
            prompt = self.create_simple_comparison_prompt(text1, text2)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a technical drawing analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content
            result_data = json.loads(result_text)
            
            # Calculate raw similarity
            import difflib
            raw_similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
            
            similarity_score = result_data.get("similarity_percentage", 0) / 100.0
            
            return SemanticComparisonResult(
                similarity_score=similarity_score,
                confidence=0.8,  # Moderate confidence for simple analysis
                semantic_differences=result_data.get("main_differences", []),
                technical_analysis={"explanation": result_data.get("explanation", "")},
                reasoning=result_data.get("explanation", "Simple comparison performed"),
                categories={},
                timestamp=datetime.now().isoformat(),
                raw_similarity=raw_similarity
            )
            
        except Exception as e:
            # Final fallback to difflib if all else fails
            import difflib
            raw_similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
            
            return SemanticComparisonResult(
                similarity_score=raw_similarity,
                confidence=0.3,  # Low confidence for fallback
                semantic_differences=["AI comparison failed, using text similarity"],
                technical_analysis={"error": str(e)},
                reasoning="Fallback to basic text comparison due to API error",
                categories={},
                timestamp=datetime.now().isoformat(),
                raw_similarity=raw_similarity
            )
    
    def compare_with_different_models(self, text1: str, text2: str) -> Dict[str, SemanticComparisonResult]:
        """Compare using different GPT models and return results."""
        models = ["gpt-4o", "gpt-3.5-turbo"]
        results = {}
        
        for model in models:
            try:
                results[model] = self.compare_with_gpt(text1, text2, model)
            except Exception as e:
                print(f"Failed to compare with {model}: {e}")
                continue
        
        return results
    
    def get_consensus_result(self, results: Dict[str, SemanticComparisonResult]) -> SemanticComparisonResult:
        """Get consensus result from multiple model comparisons."""
        if not results:
            raise ValueError("No valid results to create consensus from")
        
        if len(results) == 1:
            return list(results.values())[0]
        
        # Calculate weighted average based on confidence
        total_weighted_similarity = 0
        total_weight = 0
        all_differences = []
        all_reasoning = []
        
        for model, result in results.items():
            weight = result.confidence
            total_weighted_similarity += result.similarity_score * weight
            total_weight += weight
            all_differences.extend(result.semantic_differences)
            all_reasoning.append(f"{model}: {result.reasoning}")
        
        consensus_similarity = total_weighted_similarity / total_weight if total_weight > 0 else 0
        
        # Use the result with highest confidence as base
        best_result = max(results.values(), key=lambda r: r.confidence)
        
        return SemanticComparisonResult(
            similarity_score=consensus_similarity,
            confidence=min(1.0, total_weight / len(results)),
            semantic_differences=list(set(all_differences)),  # Remove duplicates
            technical_analysis=best_result.technical_analysis,
            reasoning="Consensus from multiple models: " + "; ".join(all_reasoning),
            categories=best_result.categories,
            timestamp=datetime.now().isoformat(),
            raw_similarity=best_result.raw_similarity
        )

# Utility functions
def format_semantic_result(result: SemanticComparisonResult) -> str:
    """Format semantic comparison result for display."""
    output = []
    output.append(f"🤖 AI Semantic Similarity: {result.similarity_score:.1%}")
    output.append(f"📊 Raw Text Similarity: {result.raw_similarity:.1%}")
    output.append(f"🎯 AI Confidence: {result.confidence:.1%}")
    output.append(f"\n💭 AI Reasoning:\n{result.reasoning}")
    
    if result.semantic_differences:
        output.append(f"\n🔍 Key Differences:")
        for diff in result.semantic_differences[:5]:  # Show top 5
            output.append(f"  • {diff}")
    
    if result.categories:
        output.append(f"\n📋 Category Analysis:")
        for category, score in result.categories.items():
            output.append(f"  {category.replace('_', ' ').title()}: {score:.1%}")
    
    return "\n".join(output)

if __name__ == "__main__":
    # Example usage
    comparator = SemanticComparator()
    
    # Test with sample texts
    text1 = "Steel beam W14x30, span 20ft, dead load 50 psf, live load 40 psf"
    text2 = "W14x30 steel beam, 20 foot span, DL=50psf, LL=40psf"
    
    result = comparator.compare_with_gpt(text1, text2)
    print(format_semantic_result(result))
