"""
Quantitative Agent - Data Fetcher Module
Fetches OHLCV data and historical price information using yfinance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches market data for technical analysis"""

    def __init__(self, ticker: str):
        """
        Initialize data fetcher for a specific ticker
        
        Args:
            ticker: Stock ticker symbol (e.g., 'NVDA')
        """
        self.ticker = ticker.upper()
        self.data = None

    def fetch_historical_data(
        self,
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data
        
        Args:
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max')
            interval: Data interval ('1m', '5m', '15m', '30m', '60m', '1d', '1wk', '1mo')
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            logger.info(f"Fetching {period} of {interval} data for {self.ticker}")
            self.data = yf.download(
                self.ticker,
                period=period,
                interval=interval,
                progress=False
            )
            
            if self.data.empty:
                logger.error(f"No data found for ticker {self.ticker}")
                return pd.DataFrame()
            
            logger.info(f"Successfully fetched {len(self.data)} rows of data")
            return self.data
            
        except Exception as e:
            logger.error(f"Error fetching data for {self.ticker}: {str(e)}")
            return pd.DataFrame()

    def fetch_recent_data(self, days: int = 252) -> pd.DataFrame:
        """
        Fetch recent trading data (default: 1 year of trading days)
        
        Args:
            days: Number of trading days to fetch
            
        Returns:
            DataFrame with recent OHLCV data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        try:
            logger.info(f"Fetching {days} days of data for {self.ticker}")
            self.data = yf.download(
                self.ticker,
                start=start_date,
                end=end_date,
                progress=False
            )
            
            if self.data.empty:
                logger.error(f"No data found for ticker {self.ticker}")
                return pd.DataFrame()
            
            logger.info(f"Successfully fetched {len(self.data)} rows of data")
            return self.data
            
        except Exception as e:
            logger.error(f"Error fetching recent data for {self.ticker}: {str(e)}")
            return pd.DataFrame()

    def get_current_price(self) -> Optional[float]:
        """
        Get current price for the ticker
        
        Returns:
            Current price or None if unavailable
        """
        try:
            ticker_obj = yf.Ticker(self.ticker)
            current_price = ticker_obj.info.get('currentPrice')
            
            if current_price is None:
                # Fallback: use last close price
                if self.data is not None and not self.data.empty:
                    current_price = self.data['Close'].iloc[-1]
            
            return current_price
            
        except Exception as e:
            logger.error(f"Error fetching current price for {self.ticker}: {str(e)}")
            return None

    def get_ticker_info(self) -> Dict[str, Any]:
        """
        Get ticker information (sector, industry, market cap, etc.)
        
        Returns:
            Dictionary with ticker information
        """
        try:
            ticker_obj = yf.Ticker(self.ticker)
            info = ticker_obj.info
            
            return {
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
            }
            
        except Exception as e:
            logger.error(f"Error fetching ticker info for {self.ticker}: {str(e)}")
            return {}

    def ensure_data_loaded(self, period: str = "1y") -> bool:
        """
        Ensure data is loaded, fetch if necessary
        
        Args:
            period: Time period to fetch if data not loaded
            
        Returns:
            True if data is available, False otherwise
        """
        if self.data is None or self.data.empty:
            self.fetch_historical_data(period=period)
        
        return self.data is not None and not self.data.empty
