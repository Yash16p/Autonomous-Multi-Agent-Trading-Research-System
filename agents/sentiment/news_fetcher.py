"""
Sentiment Agent - News Fetcher Module
Fetches recent news and social sentiment
"""

import os
from typing import List, Dict, Any, Optional
import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetches news articles and sentiment data"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize news fetcher
        
        Args:
            api_key: NewsAPI key (defaults to NEWS_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('NEWS_API_KEY')
        self.base_url = 'https://newsapi.org/v2'
        self.articles = []

    def fetch_news(self, ticker: str, days: int = 7, language: str = 'en') -> List[Dict[str, Any]]:
        """
        Fetch recent news articles for a ticker
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days to look back
            language: Language code (default: 'en')
            
        Returns:
            List of news articles
        """
        if not self.api_key:
            logger.warning("NEWS_API_KEY not set, cannot fetch news")
            return []
        
        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            # Search for company name and ticker
            query = f'"{ticker}" OR "{self._get_company_name(ticker)}"'
            
            params = {
                'q': query,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'language': language,
                'sortBy': 'publishedAt',
                'apiKey': self.api_key,
                'pageSize': 50
            }
            
            logger.info(f"Fetching news for {ticker}...")
            response = requests.get(f'{self.base_url}/everything', params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Process articles
            processed_articles = []
            for article in articles:
                processed = {
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'content': article.get('content', ''),
                }
                processed_articles.append(processed)
            
            self.articles = processed_articles
            logger.info(f"Fetched {len(processed_articles)} articles for {ticker}")
            return processed_articles
            
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {str(e)}")
            return []

    def fetch_top_headlines(self, ticker: str, country: str = 'us') -> List[Dict[str, Any]]:
        """
        Fetch top headlines for a ticker
        
        Args:
            ticker: Stock ticker symbol
            country: Country code (default: 'us')
            
        Returns:
            List of headline articles
        """
        if not self.api_key:
            logger.warning("NEWS_API_KEY not set, cannot fetch headlines")
            return []
        
        try:
            params = {
                'q': ticker,
                'country': country,
                'apiKey': self.api_key,
                'pageSize': 20
            }
            
            logger.info(f"Fetching top headlines for {ticker}...")
            response = requests.get(f'{self.base_url}/top-headlines', params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Process articles
            processed_articles = []
            for article in articles:
                processed = {
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'content': article.get('content', ''),
                }
                processed_articles.append(processed)
            
            logger.info(f"Fetched {len(processed_articles)} headlines for {ticker}")
            return processed_articles
            
        except Exception as e:
            logger.error(f"Error fetching headlines for {ticker}: {str(e)}")
            return []

    def get_articles(self) -> List[Dict[str, Any]]:
        """
        Get cached articles
        
        Returns:
            List of articles
        """
        return self.articles

    def _get_company_name(self, ticker: str) -> str:
        """
        Get company name from ticker (simplified mapping)
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Company name
        """
        company_map = {
            'NVDA': 'NVIDIA',
            'TSLA': 'Tesla',
            'AAPL': 'Apple',
            'MSFT': 'Microsoft',
            'GOOGL': 'Google',
            'AMZN': 'Amazon',
            'META': 'Meta',
            'NFLX': 'Netflix',
        }
        return company_map.get(ticker, ticker)

    def extract_themes(self, articles: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract themes from articles (simple keyword matching)
        
        Args:
            articles: List of articles
            
        Returns:
            Dictionary of themes and their weights
        """
        themes = {
            'earnings': 0.0,
            'product_launch': 0.0,
            'regulatory': 0.0,
            'supply_chain': 0.0,
            'competition': 0.0,
            'partnership': 0.0,
            'acquisition': 0.0,
            'layoffs': 0.0,
        }
        
        keywords = {
            'earnings': ['earnings', 'revenue', 'profit', 'beat', 'miss', 'guidance'],
            'product_launch': ['launch', 'product', 'release', 'new', 'announcement'],
            'regulatory': ['regulatory', 'sec', 'fda', 'antitrust', 'lawsuit', 'fine'],
            'supply_chain': ['supply', 'chain', 'shortage', 'logistics', 'delivery'],
            'competition': ['competitor', 'competition', 'rival', 'market share'],
            'partnership': ['partnership', 'collaboration', 'joint venture', 'deal'],
            'acquisition': ['acquisition', 'acquired', 'merger', 'buyout'],
            'layoffs': ['layoff', 'restructuring', 'headcount', 'workforce'],
        }
        
        try:
            for article in articles:
                text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
                
                for theme, keywords_list in keywords.items():
                    for keyword in keywords_list:
                        if keyword in text:
                            themes[theme] += 1.0 / len(articles)
            
            # Normalize
            total = sum(themes.values())
            if total > 0:
                themes = {k: v / total for k, v in themes.items()}
            
            return themes
            
        except Exception as e:
            logger.error(f"Error extracting themes: {str(e)}")
            return themes

    def calculate_recency_score(self, articles: List[Dict[str, Any]]) -> float:
        """
        Calculate recency score (how recent are the articles)
        
        Args:
            articles: List of articles
            
        Returns:
            Recency score [0, 1]
        """
        try:
            if not articles:
                return 0.0
            
            now = datetime.now(datetime.now().astimezone().tzinfo)
            
            recency_scores = []
            for article in articles:
                pub_date_str = article.get('published_at', '')
                
                try:
                    # Parse ISO format date
                    pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                    
                    # Convert to naive datetime for comparison
                    if pub_date.tzinfo is not None:
                        pub_date = pub_date.replace(tzinfo=None)
                    if now.tzinfo is not None:
                        now_naive = now.replace(tzinfo=None)
                    else:
                        now_naive = now
                    
                    hours_old = (now_naive - pub_date).total_seconds() / 3600
                    
                    # Score: 1.0 if < 24 hours, decays to 0 after 7 days
                    if hours_old < 24:
                        score = 1.0
                    elif hours_old < 168:  # 7 days
                        score = 1.0 - (hours_old - 24) / 144
                    else:
                        score = 0.0
                    
                    recency_scores.append(score)
                    
                except Exception as e:
                    logger.debug(f"Error parsing date {pub_date_str}: {str(e)}")
                    recency_scores.append(0.5)
            
            return sum(recency_scores) / len(recency_scores) if recency_scores else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating recency score: {str(e)}")
            return 0.5
