"""
Quantitative Agent
Analyzes technical indicators and generates quantitative trading signals
"""

from typing import Dict, Any, Optional
import logging
import json

from .data_fetcher import DataFetcher
from .indicators import TechnicalIndicators
from .signal_generator import SignalGenerator

logger = logging.getLogger(__name__)


class QuantAgent:
    """
    Quantitative Analysis Agent
    
    Responsibilities:
    - Fetch OHLCV data using yfinance
    - Compute technical indicators (momentum, volatility, trend, volume)
    - Generate numerical feature vectors
    - Output: Preliminary signal (bullish/bearish) + confidence
    """

    def __init__(self, ticker: str):
        """
        Initialize Quant Agent
        
        Args:
            ticker: Stock ticker symbol (e.g., 'NVDA')
        """
        self.ticker = ticker.upper()
        self.data_fetcher = DataFetcher(self.ticker)
        self.indicators = None
        self.signal_generator = None
        self.output = None

    def analyze(self, period: str = "1y") -> Dict[str, Any]:
        """
        Perform quantitative analysis
        
        Args:
            period: Time period for analysis ('1y', '6mo', '3mo', etc.)
            
        Returns:
            Dictionary with analysis results
        """
        try:
            logger.info(f"Starting quantitative analysis for {self.ticker}")
            
            # Step 1: Fetch data
            logger.info("Fetching historical data...")
            data = self.data_fetcher.fetch_historical_data(period=period)
            
            if data.empty:
                logger.error(f"Failed to fetch data for {self.ticker}")
                return self._error_output("Failed to fetch market data")
            
            # Step 2: Compute indicators
            logger.info("Computing technical indicators...")
            self.indicators = TechnicalIndicators(data)
            indicators_dict = self.indicators.compute_all_indicators()
            
            # Step 3: Generate signal
            logger.info("Generating trading signal...")
            self.signal_generator = SignalGenerator(indicators_dict)
            signal, confidence, reasoning = self.signal_generator.generate_signal()
            
            # Step 4: Build output
            self.output = self._build_output(signal, confidence, reasoning, indicators_dict)
            
            logger.info(f"Quantitative analysis complete. Signal: {signal:.2f}, Confidence: {confidence:.2f}")
            return self.output
            
        except Exception as e:
            logger.error(f"Error in quantitative analysis: {str(e)}")
            return self._error_output(str(e))

    def _build_output(self, signal: float, confidence: float, reasoning: str, 
                     indicators: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Build structured output
        
        Args:
            signal: Trading signal [-1, 1]
            confidence: Confidence score [0, 1]
            reasoning: Reasoning string
            indicators: Dictionary of indicators
            
        Returns:
            Structured output dictionary
        """
        # Determine sentiment
        if signal > 0.3:
            sentiment = "bullish"
        elif signal < -0.3:
            sentiment = "bearish"
        else:
            sentiment = "neutral"
        
        # Extract key indicators for output
        key_indicators = {
            'rsi': indicators.get('momentum', {}).get('rsi', 50),
            'macd': indicators.get('momentum', {}).get('macd', 0),
            'macd_histogram': indicators.get('momentum', {}).get('macd_histogram', 0),
            'bollinger_position': indicators.get('volatility', {}).get('bollinger_position', 0.5),
            'atr': indicators.get('volatility', {}).get('atr', 0),
            'sma_20': indicators.get('trend', {}).get('sma_20', 0),
            'sma_50': indicators.get('trend', {}).get('sma_50', 0),
            'sma_200': indicators.get('trend', {}).get('sma_200', 0),
            'volume_ratio': indicators.get('volume', {}).get('volume_ratio', 1.0),
        }
        
        return {
            'agent': 'quant',
            'ticker': self.ticker,
            'signal': float(signal),
            'sentiment': sentiment,
            'confidence': float(confidence),
            'indicators': key_indicators,
            'reasoning': reasoning,
            'all_indicators': indicators
        }

    def _error_output(self, error_msg: str) -> Dict[str, Any]:
        """
        Build error output
        
        Args:
            error_msg: Error message
            
        Returns:
            Error output dictionary
        """
        return {
            'agent': 'quant',
            'ticker': self.ticker,
            'signal': 0.0,
            'sentiment': 'neutral',
            'confidence': 0.0,
            'indicators': {},
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
        Get the current signal value
        
        Returns:
            Signal value [-1, 1] or 0 if no analysis performed
        """
        if self.output:
            return self.output.get('signal', 0.0)
        return 0.0

    def get_confidence(self) -> float:
        """
        Get the current confidence score
        
        Returns:
            Confidence [0, 1] or 0 if no analysis performed
        """
        if self.output:
            return self.output.get('confidence', 0.0)
        return 0.0

    def to_json(self) -> str:
        """
        Convert output to JSON string
        
        Returns:
            JSON string representation
        """
        if self.output:
            # Remove all_indicators from JSON output for brevity
            output_copy = self.output.copy()
            output_copy.pop('all_indicators', None)
            return json.dumps(output_copy, indent=2)
        return json.dumps(self._error_output("No analysis performed"), indent=2)
