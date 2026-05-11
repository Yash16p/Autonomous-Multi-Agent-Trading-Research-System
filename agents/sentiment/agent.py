"""
Sentiment Agent
Analyzes market sentiment from news and social sources
"""

from typing import Dict, Any, Optional, List
import logging
import json

from .news_fetcher import NewsFetcher
from .nlp_scorer import NLPScorer

logger = logging.getLogger(__name__)


class SentimentAgent:
    """
    Sentiment Analysis Agent
    
    Responsibilities:
    - Fetch recent news via NewsAPI
    - Process text using LLM (Claude) for nuanced sentiment understanding
    - Compute sentiment score, confidence, key themes, recency weight
    - Output: Sentiment signal + themes
    """

    def __init__(self, ticker: str):
        """
        Initialize Sentiment Agent
        
        Args:
            ticker: Stock ticker symbol (e.g., 'NVDA')
        """
        self.ticker = ticker.upper()
        self.news_fetcher = NewsFetcher()
        self.nlp_scorer = NLPScorer()
        self.output = None

    def analyze(self, days: int = 7) -> Dict[str, Any]:
        """
        Perform sentiment analysis
        
        Args:
            days: Number of days to look back for news
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            logger.info(f"Starting sentiment analysis for {self.ticker}")
            
            # Step 1: Fetch news
            logger.info("Fetching news articles...")
            articles = self.news_fetcher.fetch_news(self.ticker, days=days)
            
            if not articles:
                logger.warning(f"No news found for {self.ticker}")
                return self._error_output("No news articles found")
            
            # Step 2: Analyze sentiment
            logger.info("Analyzing sentiment...")
            sentiment_analysis = self.nlp_scorer.analyze_articles(articles)
            
            # Step 3: Extract themes
            logger.info("Extracting themes...")
            themes = self.news_fetcher.extract_themes(articles)
            
            # Step 4: Calculate recency score
            logger.info("Calculating recency score...")
            recency_score = self.news_fetcher.calculate_recency_score(articles)
            
            # Step 5: Generate signal
            logger.info("Generating sentiment signal...")
            signal = self._generate_signal(sentiment_analysis, recency_score)
            
            # Step 6: Build output
            self.output = self._build_output(
                signal,
                sentiment_analysis,
                themes,
                recency_score,
                articles
            )
            
            logger.info(f"Sentiment analysis complete. Signal: {signal:.2f}")
            return self.output
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return self._error_output(str(e))

    def _generate_signal(self, sentiment_analysis: Dict[str, Any], 
                        recency_score: float) -> float:
        """
        Generate trading signal from sentiment
        
        Args:
            sentiment_analysis: Sentiment analysis results
            recency_score: Recency score [0, 1]
            
        Returns:
            Trading signal [-1, 1]
        """
        try:
            # Base signal from sentiment score
            base_signal = sentiment_analysis.get('overall_score', 0.0)
            
            # Adjust for recency (more recent = higher weight)
            recency_weight = 0.5 + (recency_score * 0.5)  # [0.5, 1.0]
            
            # Adjust for confidence
            confidence = sentiment_analysis.get('overall_confidence', 0.5)
            confidence_weight = 0.5 + (confidence * 0.5)  # [0.5, 1.0]
            
            # Combine
            signal = base_signal * recency_weight * confidence_weight
            
            return float(signal)
            
        except Exception as e:
            logger.error(f"Error generating signal: {str(e)}")
            return 0.0

    def _build_output(self, signal: float, sentiment_analysis: Dict[str, Any],
                     themes: Dict[str, float], recency_score: float,
                     articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build structured output
        
        Args:
            signal: Trading signal
            sentiment_analysis: Sentiment analysis results
            themes: Extracted themes
            recency_score: Recency score
            articles: News articles
            
        Returns:
            Structured output dictionary
        """
        # Convert themes to list format with weights
        theme_list = [
            {'theme': theme, 'weight': weight}
            for theme, weight in sorted(themes.items(), key=lambda x: x[1], reverse=True)
            if weight > 0.05  # Only include themes with >5% weight
        ]
        
        # Build reasoning
        reasoning = self._build_reasoning(sentiment_analysis, theme_list, articles)
        
        return {
            'agent': 'sentiment',
            'ticker': self.ticker,
            'signal': float(signal),
            'sentiment': sentiment_analysis.get('overall_sentiment', 'neutral'),
            'confidence': float(sentiment_analysis.get('overall_confidence', 0.0)),
            'themes': theme_list,
            'recency_score': float(recency_score),
            'article_count': len(articles),
            'bullish_articles': sentiment_analysis.get('bullish_count', 0),
            'bearish_articles': sentiment_analysis.get('bearish_count', 0),
            'neutral_articles': sentiment_analysis.get('neutral_count', 0),
            'reasoning': reasoning,
        }

    def _build_reasoning(self, sentiment_analysis: Dict[str, Any],
                        theme_list: List[Dict[str, Any]],
                        articles: List[Dict[str, Any]]) -> str:
        """
        Build reasoning string
        
        Args:
            sentiment_analysis: Sentiment analysis results
            theme_list: List of themes
            articles: News articles
            
        Returns:
            Reasoning string
        """
        reasons = []
        
        # Overall sentiment
        sentiment = sentiment_analysis.get('overall_sentiment', 'neutral')
        score = sentiment_analysis.get('overall_score', 0.0)
        reasons.append(f"Overall sentiment is {sentiment} (score: {score:.2f})")
        
        # Article breakdown
        bullish = sentiment_analysis.get('bullish_count', 0)
        bearish = sentiment_analysis.get('bearish_count', 0)
        total = len(articles)
        
        if bullish > bearish:
            reasons.append(f"More bullish articles ({bullish}/{total}) than bearish ({bearish}/{total})")
        elif bearish > bullish:
            reasons.append(f"More bearish articles ({bearish}/{total}) than bullish ({bullish}/{total})")
        
        # Top themes
        if theme_list:
            top_themes = [t['theme'] for t in theme_list[:2]]
            reasons.append(f"Key themes: {', '.join(top_themes)}")
        
        return "; ".join(reasons[:3])  # Limit to 3 key points

    def _error_output(self, error_msg: str) -> Dict[str, Any]:
        """
        Build error output
        
        Args:
            error_msg: Error message
            
        Returns:
            Error output dictionary
        """
        return {
            'agent': 'sentiment',
            'ticker': self.ticker,
            'signal': 0.0,
            'sentiment': 'neutral',
            'confidence': 0.0,
            'themes': [],
            'recency_score': 0.0,
            'article_count': 0,
            'bullish_articles': 0,
            'bearish_articles': 0,
            'neutral_articles': 0,
            'reasoning': f"Error: {error_msg}",
            'error': error_msg
        }

    def get_output(self) -> Optional[Dict[str, Any]]:
        """
        Get the last analysis output
        
        Returns:
            Output dictionary or None if no analysis performed
        """
        return self.output

    def get_signal(self) -> float:
        """
        Get the current sentiment signal
        
        Returns:
            Signal value [-1, 1] or 0 if no analysis performed
        """
        if self.output:
            return self.output.get('signal', 0.0)
        return 0.0

    def to_json(self) -> str:
        """
        Convert output to JSON string
        
        Returns:
            JSON string representation
        """
        if self.output:
            return json.dumps(self.output, indent=2)
        return json.dumps(self._error_output("No analysis performed"), indent=2)
