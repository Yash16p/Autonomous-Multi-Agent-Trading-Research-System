"""
Quantitative Agent - Technical Indicators Module
Computes technical indicators for market analysis
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Computes technical indicators from OHLCV data"""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize with OHLCV data
        
        Args:
            data: DataFrame with columns [Open, High, Low, Close, Volume]
        """
        self.data = data.copy()
        self.indicators = {}

    def compute_momentum_indicators(self) -> Dict[str, float]:
        """
        Compute momentum indicators: RSI, MACD, Rate of Change
        
        Returns:
            Dictionary with momentum indicator values
        """
        try:
            momentum = {}
            
            # RSI (Relative Strength Index) - 14 period default
            rsi = ta.rsi(self.data['Close'], length=14)
            momentum['rsi'] = float(rsi.iloc[-1]) if not rsi.empty else 50.0
            
            # MACD (Moving Average Convergence Divergence)
            macd_result = ta.macd(self.data['Close'], fast=12, slow=26, signal=9)
            if macd_result is not None and not macd_result.empty:
                momentum['macd'] = float(macd_result.iloc[-1, 0]) if len(macd_result.columns) > 0 else 0.0
                momentum['macd_signal'] = float(macd_result.iloc[-1, 1]) if len(macd_result.columns) > 1 else 0.0
                momentum['macd_histogram'] = float(macd_result.iloc[-1, 2]) if len(macd_result.columns) > 2 else 0.0
            else:
                momentum['macd'] = 0.0
                momentum['macd_signal'] = 0.0
                momentum['macd_histogram'] = 0.0
            
            # Rate of Change (ROC) - 12 period
            roc = ta.roc(self.data['Close'], length=12)
            momentum['roc'] = float(roc.iloc[-1]) if not roc.empty else 0.0
            
            self.indicators['momentum'] = momentum
            return momentum
            
        except Exception as e:
            logger.error(f"Error computing momentum indicators: {str(e)}")
            return {}

    def compute_volatility_indicators(self) -> Dict[str, float]:
        """
        Compute volatility indicators: Bollinger Bands, ATR, Standard Deviation
        
        Returns:
            Dictionary with volatility indicator values
        """
        try:
            volatility = {}
            
            # Bollinger Bands (20 period, 2 std dev)
            bb = ta.bbands(self.data['Close'], length=20, std=2)
            if bb is not None and not bb.empty:
                bb_high = float(bb.iloc[-1, 0]) if len(bb.columns) > 0 else 0.0
                bb_mid = float(bb.iloc[-1, 1]) if len(bb.columns) > 1 else 0.0
                bb_low = float(bb.iloc[-1, 2]) if len(bb.columns) > 2 else 0.0
                current_price = float(self.data['Close'].iloc[-1])
                
                # Bollinger position: 0 = at lower band, 1 = at upper band
                if bb_high != bb_low:
                    bb_position = (current_price - bb_low) / (bb_high - bb_low)
                    bb_position = max(0, min(1, bb_position))  # Clamp to [0, 1]
                else:
                    bb_position = 0.5
                
                volatility['bollinger_high'] = bb_high
                volatility['bollinger_mid'] = bb_mid
                volatility['bollinger_low'] = bb_low
                volatility['bollinger_position'] = bb_position
            else:
                volatility['bollinger_high'] = 0.0
                volatility['bollinger_mid'] = 0.0
                volatility['bollinger_low'] = 0.0
                volatility['bollinger_position'] = 0.5
            
            # ATR (Average True Range) - 14 period
            atr = ta.atr(self.data['High'], self.data['Low'], self.data['Close'], length=14)
            volatility['atr'] = float(atr.iloc[-1]) if not atr.empty else 0.0
            
            # Standard Deviation - 20 period
            std_dev = ta.stdev(self.data['Close'], length=20)
            volatility['std_dev'] = float(std_dev.iloc[-1]) if not std_dev.empty else 0.0
            
            self.indicators['volatility'] = volatility
            return volatility
            
        except Exception as e:
            logger.error(f"Error computing volatility indicators: {str(e)}")
            return {}

    def compute_trend_indicators(self) -> Dict[str, float]:
        """
        Compute trend indicators: SMA, EMA, TEMA
        
        Returns:
            Dictionary with trend indicator values
        """
        try:
            trend = {}
            current_price = float(self.data['Close'].iloc[-1])
            
            # Simple Moving Averages
            sma_20 = ta.sma(self.data['Close'], length=20)
            sma_50 = ta.sma(self.data['Close'], length=50)
            sma_200 = ta.sma(self.data['Close'], length=200)
            
            trend['sma_20'] = float(sma_20.iloc[-1]) if not sma_20.empty else current_price
            trend['sma_50'] = float(sma_50.iloc[-1]) if not sma_50.empty else current_price
            trend['sma_200'] = float(sma_200.iloc[-1]) if not sma_200.empty else current_price
            
            # Exponential Moving Averages
            ema_12 = ta.ema(self.data['Close'], length=12)
            ema_26 = ta.ema(self.data['Close'], length=26)
            
            trend['ema_12'] = float(ema_12.iloc[-1]) if not ema_12.empty else current_price
            trend['ema_26'] = float(ema_26.iloc[-1]) if not ema_26.empty else current_price
            
            # Triple Exponential Moving Average (TEMA)
            tema = ta.tema(self.data['Close'], length=10)
            trend['tema'] = float(tema.iloc[-1]) if not tema.empty else current_price
            
            # Price position relative to moving averages
            trend['price_vs_sma20'] = (current_price - trend['sma_20']) / trend['sma_20'] if trend['sma_20'] != 0 else 0
            trend['price_vs_sma50'] = (current_price - trend['sma_50']) / trend['sma_50'] if trend['sma_50'] != 0 else 0
            trend['price_vs_sma200'] = (current_price - trend['sma_200']) / trend['sma_200'] if trend['sma_200'] != 0 else 0
            
            self.indicators['trend'] = trend
            return trend
            
        except Exception as e:
            logger.error(f"Error computing trend indicators: {str(e)}")
            return {}

    def compute_volume_indicators(self) -> Dict[str, float]:
        """
        Compute volume indicators: OBV, Volume-weighted MACD
        
        Returns:
            Dictionary with volume indicator values
        """
        try:
            volume = {}
            
            # On-Balance Volume (OBV)
            obv = ta.obv(self.data['Close'], self.data['Volume'])
            volume['obv'] = float(obv.iloc[-1]) if not obv.empty else 0.0
            
            # OBV EMA for trend
            obv_ema = ta.ema(obv, length=20)
            volume['obv_ema'] = float(obv_ema.iloc[-1]) if not obv_ema.empty else 0.0
            
            # Volume Rate of Change
            volume_roc = ta.roc(self.data['Volume'], length=5)
            volume['volume_roc'] = float(volume_roc.iloc[-1]) if not volume_roc.empty else 0.0
            
            # Average Volume
            avg_volume = self.data['Volume'].rolling(window=20).mean()
            volume['avg_volume'] = float(avg_volume.iloc[-1]) if not avg_volume.empty else 0.0
            
            # Current volume vs average
            current_volume = float(self.data['Volume'].iloc[-1])
            volume['volume_ratio'] = current_volume / volume['avg_volume'] if volume['avg_volume'] > 0 else 1.0
            
            self.indicators['volume'] = volume
            return volume
            
        except Exception as e:
            logger.error(f"Error computing volume indicators: {str(e)}")
            return {}

    def compute_all_indicators(self) -> Dict[str, Dict[str, float]]:
        """
        Compute all technical indicators
        
        Returns:
            Dictionary with all indicator categories
        """
        self.compute_momentum_indicators()
        self.compute_volatility_indicators()
        self.compute_trend_indicators()
        self.compute_volume_indicators()
        
        return self.indicators

    def get_indicators(self) -> Dict[str, Dict[str, float]]:
        """
        Get all computed indicators
        
        Returns:
            Dictionary with all indicators
        """
        if not self.indicators:
            self.compute_all_indicators()
        
        return self.indicators

    def normalize_indicators(self) -> Dict[str, float]:
        """
        Normalize indicators to [-1, 1] range for signal generation
        
        Returns:
            Dictionary with normalized indicator values
        """
        normalized = {}
        
        if not self.indicators:
            self.compute_all_indicators()
        
        try:
            # Normalize RSI (0-100 -> -1 to 1)
            rsi = self.indicators.get('momentum', {}).get('rsi', 50)
            normalized['rsi_norm'] = (rsi - 50) / 50
            
            # Normalize MACD histogram (positive = bullish)
            macd_hist = self.indicators.get('momentum', {}).get('macd_histogram', 0)
            normalized['macd_norm'] = np.sign(macd_hist) * min(abs(macd_hist) / 0.1, 1.0)
            
            # Normalize Bollinger position (0-1 -> -1 to 1)
            bb_pos = self.indicators.get('volatility', {}).get('bollinger_position', 0.5)
            normalized['bollinger_norm'] = (bb_pos - 0.5) * 2
            
            # Normalize price vs SMA (positive = above, negative = below)
            price_vs_sma20 = self.indicators.get('trend', {}).get('price_vs_sma20', 0)
            normalized['trend_norm'] = np.sign(price_vs_sma20) * min(abs(price_vs_sma20) / 0.05, 1.0)
            
            # Normalize volume ratio (>1 = high volume)
            volume_ratio = self.indicators.get('volume', {}).get('volume_ratio', 1.0)
            normalized['volume_norm'] = np.sign(volume_ratio - 1) * min(abs(volume_ratio - 1) / 0.5, 1.0)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing indicators: {str(e)}")
            return {}
