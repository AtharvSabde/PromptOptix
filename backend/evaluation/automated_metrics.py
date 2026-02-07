"""
PromptOptimizer Pro - Automated Evaluation Metrics
Implements BLEU, ROUGE, METEOR, and optionally BERT Score for quality assessment
Based on Nagpure et al. (2025) Survey - Evaluation Methods
"""

from typing import Dict, List, Any, Optional, Tuple
import re

from ..utils import get_logger
from ..config import Config

logger = get_logger(__name__)

# Try to import NLP libraries
try:
    import nltk
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.tokenize import word_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logger.warning("NLTK not available - BLEU and METEOR metrics disabled")

try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False
    logger.warning("rouge-score not available - ROUGE metrics disabled")


class AutomatedMetrics:
    """
    Calculate NLP metrics for prompt/output evaluation

    Implements standard evaluation metrics from NLP literature:
    - BLEU: Bilingual Evaluation Understudy (n-gram precision)
    - ROUGE: Recall-Oriented Understudy for Gisting Evaluation
    - METEOR: Metric for Evaluation of Translation with Explicit ORdering
    - BERT Score: Contextual embedding similarity (optional)

    These metrics compare generated outputs against reference texts
    to measure quality improvements from prompt optimization.
    """

    def __init__(self):
        """Initialize the metrics calculator"""
        self._setup_nltk()
        self._setup_rouge()
        logger.info(
            "AutomatedMetrics initialized",
            extra={
                "nltk_available": NLTK_AVAILABLE,
                "rouge_available": ROUGE_AVAILABLE,
                "bert_score_enabled": Config.ENABLE_BERTSCORE
            }
        )

    def _setup_nltk(self):
        """Download required NLTK data"""
        if not NLTK_AVAILABLE:
            return

        try:
            # Download required resources
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
        except Exception as e:
            logger.warning(f"NLTK data download failed: {e}")

    def _setup_rouge(self):
        """Initialize ROUGE scorer"""
        if ROUGE_AVAILABLE:
            self.rouge_scorer = rouge_scorer.RougeScorer(
                ['rouge1', 'rouge2', 'rougeL'],
                use_stemmer=True
            )
        else:
            self.rouge_scorer = None

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for metric calculation

        Args:
            text: Text to tokenize

        Returns:
            List of lowercase tokens
        """
        if NLTK_AVAILABLE:
            try:
                return word_tokenize(text.lower())
            except Exception:
                pass
        # Fallback to simple tokenization
        return re.findall(r'\b\w+\b', text.lower())

    def calculate_bleu(
        self,
        reference: str,
        candidate: str,
        weights: Tuple[float, ...] = (0.25, 0.25, 0.25, 0.25)
    ) -> float:
        """
        Calculate BLEU score between reference and candidate

        BLEU (Bilingual Evaluation Understudy) measures n-gram precision
        between a candidate text and reference text(s).

        Args:
            reference: Reference text (ground truth)
            candidate: Candidate text to evaluate
            weights: Weights for 1-4 gram precision (default: uniform)

        Returns:
            BLEU score between 0 and 1
        """
        if not NLTK_AVAILABLE:
            logger.warning("NLTK not available, returning 0 for BLEU")
            return 0.0

        try:
            reference_tokens = self._tokenize(reference)
            candidate_tokens = self._tokenize(candidate)

            if not reference_tokens or not candidate_tokens:
                return 0.0

            # Use smoothing to handle short texts
            smoothie = SmoothingFunction().method1

            score = sentence_bleu(
                [reference_tokens],
                candidate_tokens,
                weights=weights,
                smoothing_function=smoothie
            )

            return round(score, 4)

        except Exception as e:
            logger.warning(f"BLEU calculation failed: {e}")
            return 0.0

    def calculate_rouge(
        self,
        reference: str,
        candidate: str
    ) -> Dict[str, float]:
        """
        Calculate ROUGE scores between reference and candidate

        ROUGE (Recall-Oriented Understudy for Gisting Evaluation) measures
        overlap between generated and reference text, focusing on recall.

        Variants:
        - ROUGE-1: Unigram overlap
        - ROUGE-2: Bigram overlap
        - ROUGE-L: Longest Common Subsequence

        Args:
            reference: Reference text
            candidate: Candidate text

        Returns:
            Dict with rouge1, rouge2, rougeL F1 scores
        """
        if not ROUGE_AVAILABLE or self.rouge_scorer is None:
            logger.warning("ROUGE not available, returning zeros")
            return {
                'rouge1': 0.0,
                'rouge2': 0.0,
                'rougeL': 0.0
            }

        try:
            scores = self.rouge_scorer.score(reference, candidate)
            return {
                'rouge1': round(scores['rouge1'].fmeasure, 4),
                'rouge2': round(scores['rouge2'].fmeasure, 4),
                'rougeL': round(scores['rougeL'].fmeasure, 4)
            }
        except Exception as e:
            logger.warning(f"ROUGE calculation failed: {e}")
            return {
                'rouge1': 0.0,
                'rouge2': 0.0,
                'rougeL': 0.0
            }

    def calculate_meteor(
        self,
        reference: str,
        candidate: str
    ) -> float:
        """
        Calculate METEOR score between reference and candidate

        METEOR (Metric for Evaluation of Translation with Explicit ORdering)
        considers synonyms and stemming in addition to exact matches.

        Args:
            reference: Reference text
            candidate: Candidate text

        Returns:
            METEOR score between 0 and 1
        """
        if not NLTK_AVAILABLE:
            logger.warning("NLTK not available, returning 0 for METEOR")
            return 0.0

        try:
            from nltk.translate.meteor_score import meteor_score

            reference_tokens = self._tokenize(reference)
            candidate_tokens = self._tokenize(candidate)

            if not reference_tokens or not candidate_tokens:
                return 0.0

            score = meteor_score([reference_tokens], candidate_tokens)
            return round(score, 4)

        except Exception as e:
            logger.warning(f"METEOR calculation failed: {e}")
            return 0.0

    def calculate_bert_score(
        self,
        reference: str,
        candidate: str
    ) -> Optional[Dict[str, float]]:
        """
        Calculate BERT Score between reference and candidate

        BERT Score uses contextual embeddings to measure semantic
        similarity between texts. More accurate than n-gram metrics
        but computationally expensive.

        Args:
            reference: Reference text
            candidate: Candidate text

        Returns:
            Dict with precision, recall, f1 scores, or None if disabled/unavailable
        """
        if not Config.ENABLE_BERTSCORE:
            return None

        try:
            from bert_score import score

            P, R, F1 = score(
                [candidate],
                [reference],
                lang="en",
                verbose=False
            )

            return {
                'precision': round(P.item(), 4),
                'recall': round(R.item(), 4),
                'f1': round(F1.item(), 4)
            }

        except ImportError:
            logger.warning("bert-score package not installed")
            return None
        except Exception as e:
            logger.warning(f"BERT Score calculation failed: {e}")
            return None

    def calculate_all_metrics(
        self,
        reference: str,
        candidate: str,
        include_bert: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate all available metrics

        Args:
            reference: Reference text (ground truth or original output)
            candidate: Candidate text (optimized output)
            include_bert: Whether to include BERT Score (slower)

        Returns:
            Dict containing all metric scores
        """
        metrics = {
            'bleu': self.calculate_bleu(reference, candidate),
            'rouge': self.calculate_rouge(reference, candidate),
            'meteor': self.calculate_meteor(reference, candidate),
        }

        # Add BERT Score if requested and enabled
        if include_bert or Config.ENABLE_BERTSCORE:
            bert_score = self.calculate_bert_score(reference, candidate)
            if bert_score:
                metrics['bert_score'] = bert_score

        # Calculate composite score (weighted average)
        composite_weights = {
            'bleu': 0.2,
            'rouge1': 0.2,
            'rougeL': 0.2,
            'meteor': 0.4
        }

        composite_score = (
            metrics['bleu'] * composite_weights['bleu'] +
            metrics['rouge']['rouge1'] * composite_weights['rouge1'] +
            metrics['rouge']['rougeL'] * composite_weights['rougeL'] +
            metrics['meteor'] * composite_weights['meteor']
        )

        metrics['composite_score'] = round(composite_score, 4)

        return metrics

    def calculate_prompt_similarity(
        self,
        original_prompt: str,
        optimized_prompt: str
    ) -> Dict[str, Any]:
        """
        Calculate similarity between original and optimized prompts

        This helps assess how much the optimization changed the prompt.
        High similarity = minimal changes, low similarity = major restructuring.

        Args:
            original_prompt: Original prompt text
            optimized_prompt: Optimized prompt text

        Returns:
            Dict with similarity metrics
        """
        metrics = self.calculate_all_metrics(original_prompt, optimized_prompt)

        # Calculate length change
        original_len = len(original_prompt.split())
        optimized_len = len(optimized_prompt.split())
        length_ratio = optimized_len / max(original_len, 1)

        # Interpret similarity
        similarity = metrics['composite_score']
        if similarity > 0.8:
            change_level = "minimal"
        elif similarity > 0.5:
            change_level = "moderate"
        else:
            change_level = "substantial"

        return {
            'similarity_metrics': metrics,
            'original_word_count': original_len,
            'optimized_word_count': optimized_len,
            'length_ratio': round(length_ratio, 2),
            'change_level': change_level
        }

    def compare_outputs(
        self,
        original_output: str,
        optimized_output: str,
        reference_output: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare original vs optimized outputs

        If a reference output is provided, both are compared against it.
        Otherwise, optimized is compared against original.

        Args:
            original_output: Output from original prompt
            optimized_output: Output from optimized prompt
            reference_output: Optional gold standard reference

        Returns:
            Comparison metrics showing improvement
        """
        if reference_output:
            # Compare both against reference
            original_metrics = self.calculate_all_metrics(reference_output, original_output)
            optimized_metrics = self.calculate_all_metrics(reference_output, optimized_output)

            improvement = {
                'bleu': round(optimized_metrics['bleu'] - original_metrics['bleu'], 4),
                'rouge1': round(
                    optimized_metrics['rouge']['rouge1'] - original_metrics['rouge']['rouge1'], 4
                ),
                'rougeL': round(
                    optimized_metrics['rouge']['rougeL'] - original_metrics['rouge']['rougeL'], 4
                ),
                'meteor': round(optimized_metrics['meteor'] - original_metrics['meteor'], 4),
                'composite': round(
                    optimized_metrics['composite_score'] - original_metrics['composite_score'], 4
                )
            }

            return {
                'original_scores': original_metrics,
                'optimized_scores': optimized_metrics,
                'improvement': improvement,
                'comparison_type': 'reference_based'
            }
        else:
            # Compare optimized against original
            similarity_metrics = self.calculate_all_metrics(original_output, optimized_output)

            return {
                'similarity_metrics': similarity_metrics,
                'comparison_type': 'original_vs_optimized',
                'interpretation': self._interpret_similarity(similarity_metrics['composite_score'])
            }

    def _interpret_similarity(self, score: float) -> str:
        """Interpret similarity score"""
        if score > 0.9:
            return "Very similar outputs - minimal change in response"
        elif score > 0.7:
            return "Similar outputs - moderate changes in response"
        elif score > 0.5:
            return "Moderately different outputs - noticeable changes"
        else:
            return "Significantly different outputs - substantial changes"


# Singleton instance
_metrics_instance = None


def get_automated_metrics() -> AutomatedMetrics:
    """Get or create singleton AutomatedMetrics instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = AutomatedMetrics()
    return _metrics_instance


# Export
__all__ = [
    "AutomatedMetrics",
    "get_automated_metrics"
]
