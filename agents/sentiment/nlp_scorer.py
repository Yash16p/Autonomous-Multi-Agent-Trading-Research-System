"""
Sentiment Agent - NLP Scorer Module
Analyzes sentiment using LLM (Claude)
"""

import os
from typing import Dict, Any, List, Optional
import logging
import json

logger = logging.getLogger(__name__)


class NLPScorer:
    """Analyzes sentiment using LLM"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize NLP scorer
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = None
        
        # Initialize Anthropic client if available
        try:
            from anthropic import Anthropic
            if self.api_key:
                self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            logger.warning("Anthropic library not installed, using fallback sentiment analysis")

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using LLM
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis
        """
        if not text or not text.strip():
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'reasoning': 'Empty text'
            }
        
        if self.client:
            return self._analyze_with_llm(text)
        else:
            return self._analyze_with_fallback(text)

    def _analyze_with_llm(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using Claude LLM
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis dictionary
        """
        try:
            prompt = f"""Analyze the sentiment of the following text about a stock/company. 
            
Text: {text}

Provide your analysis in JSON format with:
- sentiment: "bullish", "bearish", or "neutral"
- score: -1.0 (very bearish) to 1.0 (very bullish)
- confidence: 0.0 to 1.0
- reasoning: brief explanation

Return only valid JSON."""
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            # Parse JSON response
            try:
                result = json.loads(response_text)
                return {
                    'sentiment': result.get('sentiment', 'neutral'),
                    'score': float(result.get('score', 0.0)),
                    'confidence': float(result.get('confidence', 0.5)),
                    'reasoning': result.get('reasoning', '')
                }
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM response, using fallback")
                return self._analyze_with_fallback(text)
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment with LLM: {str(e)}")
            return self._analyze_with_fallback(text)

    def _analyze_with_fallback(self, text: str) -> Dict[str, Any]:
        """
        Fallback sentiment analysis using keyword matching
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis dictionary
        """
        text_lower = text.lower()
        
        # Bullish keywords
        bullish_keywords = [
            'beat', 'strong', 'growth', 'profit', 'revenue', 'surge', 'rally',
            'bullish', 'positive', 'upgrade', 'outperform', 'buy', 'excellent',
            'innovation', 'launch', 'partnership', 'acquisition', 'expansion',
            'record', 'breakthrough', 'success', 'momentum', 'upside'
        ]
        
        # Bearish keywords
        bearish_keywords = [
            'miss', 'weak', 'decline', 'loss', 'downgrade', 'underperform', 'sell',
            'bearish', 'negative', 'risk', 'concern', 'warning', 'challenge',
            'lawsuit', 'fine', 'layoff', 'restructuring', 'shortage', 'delay',
            'downside', 'headwind', 'pressure', 'slump', 'crash'
        ]
        
        bullish_count = sum(1 for keyword in bullish_keywords if keyword in text_lower)
        bearish_count = sum(1 for keyword in bearish_keywords if keyword in text_lower)
        
        total = bullish_count + bearish_count
        
        if total == 0:
            sentiment = 'neutral'
            score = 0.0
            confidence = 0.3
        else:
            net_sentiment = bullish_count - bearish_count
            score = net_sentiment / total
            
            if score > 0.3:
                sentiment = 'bullish'
            elif score < -0.3:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'
            
            confidence = min(abs(score), 1.0)
        
        return {
            'sentiment': sentiment,
            'score': float(score),
            'confidence': float(confidence),
            'reasoning': f"Bullish signals: {bullish_count}, Bearish signals: {bearish_count}"
        }

    def analyze_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze sentiment across multiple articles
        
        Args:
            articles: List of articles
            
        Returns:
            Aggregated sentiment analysis
        """
        if not articles:
            return {
                'overall_sentiment': 'neutral',
                'overall_score': 0.0,
                'overall_confidence': 0.0,
                'article_sentiments': []
            }
        
        article_sentiments = []
        scores = []
        confidences = []
        
        for article in articles:
            # Combine title and description for analysis
            text = f"{article.get('title', '')} {article.get('description', '')}"
            
            sentiment_result = self.analyze_sentiment(text)
            article_sentiments.append({
                'title': article.get('title', ''),
                'sentiment': sentiment_result['sentiment'],
                'score': sentiment_result['score'],
                'confidence': sentiment_result['confidence']
            })
            
            scores.append(sentiment_result['score'])
            confidences.append(sentiment_result['confidence'])
        
        # Calculate aggregate
        overall_score = sum(scores) / len(scores) if scores else 0.0
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        if overall_score > 0.2:
            overall_sentiment = 'bullish'
        elif overall_score < -0.2:
            overall_sentiment = 'bearish'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'overall_sentiment': overall_sentiment,
            'overall_score': float(overall_score),
            'overall_confidence': float(overall_confidence),
            'article_sentiments': article_sentiments,
            'bullish_count': sum(1 for s in article_sentiments if s['sentiment'] == 'bullish'),
            'bearish_count': sum(1 for s in article_sentiments if s['sentiment'] == 'bearish'),
            'neutral_count': sum(1 for s in article_sentiments if s['sentiment'] == 'neutral'),
        }

    def score_text(self, text: str) -> float:
        """
        Get sentiment score for text [-1, 1]
        
        Args:
            text: Text to score
            
        Returns:
            Sentiment score
        """
        result = self.analyze_sentiment(text)
        return result.get('score', 0.0)

    def get_sentiment_label(self, score: float) -> str:
        """
        Get sentiment label from score
        
        Args:
            score: Sentiment score [-1, 1]
            
        Returns:
            Sentiment label
        """
        if score > 0.3:
            return 'bullish'
        elif score < -0.3:
            return 'bearish'
        else:
            return 'neutral'
