"""
Quantitative Agent - Signal Generator Module
Converts technical indicators into trading signals
"""

import numpy as np
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class SignalGenerator:
    """Generates trading signals from technical indicators"""

    def __init__(self, indicators: Dict[str, Dict[str, float]]):
        """
        Initialize with computed indicators
        
        Args:
            indicators: Dictionary of technical indicators
        """
        self.indicators = indicators
        self.signal = 0.0
        self.confidence = 0.0
        self.reasoning = []

    def generate_signal(self) -> Tuple[float, float, str]:
        """
        Generate trading signal from indicators
        
        Returns:
            Tuple of (signal [-1, 1], confidence [0, 1], reasoning)
        """
        try:
            signal_components = []
            weights = []
            
            # Momentum signals (40% weight)
            momentum_signal, momentum_conf = self._analyze_momentum()
            signal_components.append(momentum_signal)
            weights.append(0.40)
            
            # Volatility signals (20% weight)
            volatility_signal, volatility_conf = self._analyze_volatility()
            signal_components.append(volatility_signal)
            weights.append(0.20)
            
            # Trend signals (30% weight)
            trend_signal, trend_conf = self._analyze_trend()
            signal_components.append(trend_signal)
            weights.append(0.30)
            
            # Volume signals (10% weight)
            volume_signal, volume_conf = self._analyze_volume()
            signal_components.append(volume_signal)
            weights.append(0.10)
            
            # Weighted signal
            self.signal = np.average(signal_components, weights=weights)
            self.signal = np.clip(self.signal, -1.0, 1.0)
            
            # Confidence: average of component confidences
            confidences = [momentum_conf, volatility_conf, trend_conf, volume_conf]
            self.confidence = np.mean(confidences)
            
            # Build reasoning
            self._build_reasoning(momentum_signal, volatility_signal, trend_signal, volume_signal)
            
            return self.signal, self.confidence, self._get_reasoning()
            
        except Exception as e:
            logger.error(f"Error generating signal: {str(e)}")
            return 0.0, 0.0, f"Error: {str(e)}"

    def _analyze_momentum(self) -> Tuple[float, float]:
        """
        Analyze momentum indicators
        
        Returns:
            Tuple of (signal [-1, 1], confidence [0, 1])
        """
        try:
            momentum = self.indicators.get('momentum', {})
            
            if not momentum:
                return 0.0, 0.0
            
            signal = 0.0
            confidence_scores = []
            
            # RSI analysis (0-30 oversold, 70-100 overbought)
            rsi = momentum.get('rsi', 50)
            if rsi < 30:
                signal += 0.5  # Oversold = bullish
                confidence_scores.append(0.8)
                self.reasoning.append(f"RSI {rsi:.1f} indicates oversold conditions (bullish)")
            elif rsi > 70:
                signal -= 0.5  # Overbought = bearish
                confidence_scores.append(0.8)
                self.reasoning.append(f"RSI {rsi:.1f} indicates overbought conditions (bearish)")
            else:
                confidence_scores.append(0.4)
            
            # MACD analysis
            macd_hist = momentum.get('macd_histogram', 0)
            if macd_hist > 0:
                signal += 0.3  # Positive histogram = bullish
                confidence_scores.append(0.7)
                self.reasoning.append(f"MACD histogram positive ({macd_hist:.4f}) indicates bullish momentum")
            elif macd_hist < 0:
                signal -= 0.3  # Negative histogram = bearish
                confidence_scores.append(0.7)
                self.reasoning.append(f"MACD histogram negative ({macd_hist:.4f}) indicates bearish momentum")
            else:
                confidence_scores.append(0.3)
            
            # ROC analysis
            roc = momentum.get('roc', 0)
            if roc > 2:
                signal += 0.2  # Strong positive ROC = bullish
                confidence_scores.append(0.6)
                self.reasoning.append(f"Rate of Change {roc:.2f}% shows strong upward momentum")
            elif roc < -2:
                signal -= 0.2  # Strong negative ROC = bearish
                confidence_scores.append(0.6)
                self.reasoning.append(f"Rate of Change {roc:.2f}% shows strong downward momentum")
            else:
                confidence_scores.append(0.3)
            
            signal = np.clip(signal, -1.0, 1.0)
            confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            return signal, confidence
            
        except Exception as e:
            logger.error(f"Error analyzing momentum: {str(e)}")
            return 0.0, 0.0

    def _analyze_volatility(self) -> Tuple[float, float]:
        """
        Analyze volatility indicators
        
        Returns:
            Tuple of (signal [-1, 1], confidence [0, 1])
        """
        try:
            volatility = self.indicators.get('volatility', {})
            
            if not volatility:
                return 0.0, 0.0
            
            signal = 0.0
            confidence_scores = []
            
            # Bollinger Bands analysis
            bb_pos = volatility.get('bollinger_position', 0.5)
            if bb_pos > 0.8:
                signal += 0.3  # Near upper band = potential reversal (bearish)
                confidence_scores.append(0.6)
                self.reasoning.append(f"Price near upper Bollinger Band ({bb_pos:.2f}) suggests potential pullback")
            elif bb_pos < 0.2:
                signal -= 0.3  # Near lower band = potential reversal (bullish)
                confidence_scores.append(0.6)
                self.reasoning.append(f"Price near lower Bollinger Band ({bb_pos:.2f}) suggests potential bounce")
            else:
                confidence_scores.append(0.3)
            
            # ATR analysis (high volatility)
            atr = volatility.get('atr', 0)
            if atr > 0:
                # High ATR = high volatility (neutral, but affects risk)
                confidence_scores.append(0.5)
                self.reasoning.append(f"ATR {atr:.2f} indicates {'high' if atr > 2 else 'normal'} volatility")
            
            signal = np.clip(signal, -1.0, 1.0)
            confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            return signal, confidence
            
        except Exception as e:
            logger.error(f"Error analyzing volatility: {str(e)}")
            return 0.0, 0.0

    def _analyze_trend(self) -> Tuple[float, float]:
        """
        Analyze trend indicators
        
        Returns:
            Tuple of (signal [-1, 1], confidence [0, 1])
        """
        try:
            trend = self.indicators.get('trend', {})
            
            if not trend:
                return 0.0, 0.0
            
            signal = 0.0
            confidence_scores = []
            
            current_price = trend.get('sma_20', 0)  # Placeholder
            
            # Price vs SMA analysis
            price_vs_sma20 = trend.get('price_vs_sma20', 0)
            price_vs_sma50 = trend.get('price_vs_sma50', 0)
            price_vs_sma200 = trend.get('price_vs_sma200', 0)
            
            # Count how many MAs are bullish
            bullish_count = 0
            if price_vs_sma20 > 0:
                bullish_count += 1
            if price_vs_sma50 > 0:
                bullish_count += 1
            if price_vs_sma200 > 0:
                bullish_count += 1
            
            if bullish_count == 3:
                signal += 0.8  # All MAs bullish = strong uptrend
                confidence_scores.append(0.9)
                self.reasoning.append("Price above all major moving averages (SMA 20/50/200) - strong uptrend")
            elif bullish_count == 2:
                signal += 0.4  # Most MAs bullish = moderate uptrend
                confidence_scores.append(0.7)
                self.reasoning.append("Price above most moving averages - moderate uptrend")
            elif bullish_count == 1:
                signal += 0.1  # Some MAs bullish = weak uptrend
                confidence_scores.append(0.5)
                self.reasoning.append("Price above some moving averages - weak uptrend")
            else:
                signal -= 0.5  # All MAs bearish = downtrend
                confidence_scores.append(0.8)
                self.reasoning.append("Price below all major moving averages - downtrend")
            
            # EMA analysis (faster trend)
            ema_12 = trend.get('ema_12', 0)
            ema_26 = trend.get('ema_26', 0)
            if ema_12 > ema_26:
                signal += 0.2  # EMA 12 > EMA 26 = bullish
                confidence_scores.append(0.6)
                self.reasoning.append("EMA 12 above EMA 26 - bullish short-term trend")
            else:
                signal -= 0.2  # EMA 12 < EMA 26 = bearish
                confidence_scores.append(0.6)
                self.reasoning.append("EMA 12 below EMA 26 - bearish short-term trend")
            
            signal = np.clip(signal, -1.0, 1.0)
            confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            return signal, confidence
            
        except Exception as e:
            logger.error(f"Error analyzing trend: {str(e)}")
            return 0.0, 0.0

    def _analyze_volume(self) -> Tuple[float, float]:
        """
        Analyze volume indicators
        
        Returns:
            Tuple of (signal [-1, 1], confidence [0, 1])
        """
        try:
            volume = self.indicators.get('volume', {})
            
            if not volume:
                return 0.0, 0.0
            
            signal = 0.0
            confidence_scores = []
            
            # Volume ratio analysis
            volume_ratio = volume.get('volume_ratio', 1.0)
            if volume_ratio > 1.5:
                signal += 0.3  # High volume = confirmation
                confidence_scores.append(0.7)
                self.reasoning.append(f"Volume ratio {volume_ratio:.2f} indicates strong volume confirmation")
            elif volume_ratio < 0.5:
                signal -= 0.2  # Low volume = weak signal
                confidence_scores.append(0.5)
                self.reasoning.append(f"Volume ratio {volume_ratio:.2f} indicates weak volume")
            else:
                confidence_scores.append(0.4)
            
            # OBV trend
            obv = volume.get('obv', 0)
            obv_ema = volume.get('obv_ema', 0)
            if obv > obv_ema:
                signal += 0.2  # OBV above EMA = bullish
                confidence_scores.append(0.6)
                self.reasoning.append("OBV above its EMA - bullish volume trend")
            else:
                signal -= 0.1  # OBV below EMA = bearish
                confidence_scores.append(0.5)
                self.reasoning.append("OBV below its EMA - bearish volume trend")
            
            signal = np.clip(signal, -1.0, 1.0)
            confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            return signal, confidence
            
        except Exception as e:
            logger.error(f"Error analyzing volume: {str(e)}")
            return 0.0, 0.0

    def _build_reasoning(self, momentum_sig: float, volatility_sig: float, 
                        trend_sig: float, volume_sig: float):
        """Build reasoning summary"""
        self.reasoning = []
        
        # Add component analysis
        self._analyze_momentum()
        self._analyze_volatility()
        self._analyze_trend()
        self._analyze_volume()

    def _get_reasoning(self) -> str:
        """Get formatted reasoning string"""
        if not self.reasoning:
            return "Insufficient data for analysis"
        
        return "; ".join(self.reasoning[:5])  # Limit to 5 key points

    def get_signal_dict(self) -> Dict[str, Any]:
        """
        Get signal as dictionary
        
        Returns:
            Dictionary with signal, confidence, and reasoning
        """
        return {
            'signal': self.signal,
            'confidence': self.confidence,
            'reasoning': self._get_reasoning()
        }
