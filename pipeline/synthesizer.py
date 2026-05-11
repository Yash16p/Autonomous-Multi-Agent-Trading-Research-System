"""
Pipeline - Signal Synthesizer Module
Combines agent outputs into final trading signals
"""

import logging
from typing import Dict, Any, List
import numpy as np

logger = logging.getLogger(__name__)


class SignalSynthesizer:
    """Synthesizes trading signals from multiple agents"""

    def __init__(self):
        """Initialize signal synthesizer"""
        self.quant_signal = None
        self.sentiment_signal = None
        self.risk_signal = None
        self.final_signal = None

    def synthesize(self, quant_output: Dict[str, Any], 
                  sentiment_output: Dict[str, Any],
                  risk_output: Dict[str, Any],
                  weights: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Synthesize signals from all agents
        
        Args:
            quant_output: Quantitative agent output
            sentiment_output: Sentiment agent output
            risk_output: Risk agent output
            weights: Optional custom weights
            
        Returns:
            Synthesized signal dictionary
        """
        try:
            # Extract signals
            self.quant_signal = quant_output.get('signal', 0.0)
            self.sentiment_signal = sentiment_output.get('signal', 0.0)
            self.risk_signal = risk_output.get('signal', 0.0)
            
            # Default weights (can be overridden by RL)
            if weights is None:
                weights = {
                    'quant': 0.40,
                    'sentiment': 0.35,
                    'risk': 0.25
                }
            
            # Normalize weights
            total_weight = sum(weights.values())
            weights = {k: v / total_weight for k, v in weights.items()}
            
            # Weighted signal
            self.final_signal = (
                self.quant_signal * weights['quant'] +
                self.sentiment_signal * weights['sentiment'] +
                self.risk_signal * weights['risk']
            )
            
            # Clamp to [-1, 1]
            self.final_signal = np.clip(self.final_signal, -1.0, 1.0)
            
            # Calculate confidence
            confidences = [
                quant_output.get('confidence', 0.5),
                sentiment_output.get('confidence', 0.5),
                risk_output.get('confidence', 0.5)
            ]
            confidence = np.mean(confidences)
            
            # Check for conflicts
            conflicts = self._detect_conflicts(
                self.quant_signal,
                self.sentiment_signal,
                self.risk_signal
            )
            
            # Build reasoning
            reasoning = self._build_reasoning(
                self.quant_signal,
                self.sentiment_signal,
                self.risk_signal,
                weights,
                conflicts
            )
            
            return {
                'final_signal': float(self.final_signal),
                'confidence': float(confidence),
                'weights': weights,
                'component_signals': {
                    'quant': float(self.quant_signal),
                    'sentiment': float(self.sentiment_signal),
                    'risk': float(self.risk_signal)
                },
                'conflicts': conflicts,
                'reasoning': reasoning
            }
            
        except Exception as e:
            logger.error(f"Error synthesizing signals: {str(e)}")
            return {
                'final_signal': 0.0,
                'confidence': 0.0,
                'error': str(e)
            }

    def _detect_conflicts(self, quant: float, sentiment: float, risk: float) -> List[str]:
        """
        Detect conflicts between signals
        
        Args:
            quant: Quant signal
            sentiment: Sentiment signal
            risk: Risk signal
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Check quant vs sentiment
        if (quant > 0.3 and sentiment < -0.3) or (quant < -0.3 and sentiment > 0.3):
            conflicts.append("Quant and sentiment signals diverge significantly")
        
        # Check quant vs risk
        if quant > 0.3 and risk < -0.5:
            conflicts.append("Bullish quant signal conflicts with high risk assessment")
        
        # Check sentiment vs risk
        if sentiment > 0.3 and risk < -0.5:
            conflicts.append("Bullish sentiment conflicts with high risk assessment")
        
        return conflicts

    def _build_reasoning(self, quant: float, sentiment: float, risk: float,
                        weights: Dict[str, float], conflicts: List[str]) -> str:
        """
        Build reasoning string
        
        Args:
            quant: Quant signal
            sentiment: Sentiment signal
            risk: Risk signal
            weights: Signal weights
            conflicts: Detected conflicts
            
        Returns:
            Reasoning string
        """
        reasons = []
        
        # Dominant signal
        signals = {
            'quant': (quant, weights['quant']),
            'sentiment': (sentiment, weights['sentiment']),
            'risk': (risk, weights['risk'])
        }
        
        dominant = max(signals.items(), key=lambda x: abs(x[1][0]) * x[1][1])
        
        if dominant[1][0] > 0.3:
            reasons.append(f"Dominant bullish signal from {dominant[0]} ({dominant[1][0]:.2f})")
        elif dominant[1][0] < -0.3:
            reasons.append(f"Dominant bearish signal from {dominant[0]} ({dominant[1][0]:.2f})")
        else:
            reasons.append("Mixed signals with no clear direction")
        
        # Signal alignment
        bullish_count = sum(1 for s in [quant, sentiment, risk] if s > 0.2)
        bearish_count = sum(1 for s in [quant, sentiment, risk] if s < -0.2)
        
        if bullish_count >= 2:
            reasons.append("Multiple bullish signals aligned")
        elif bearish_count >= 2:
            reasons.append("Multiple bearish signals aligned")
        else:
            reasons.append("Signals mixed, no strong consensus")
        
        # Conflicts
        if conflicts:
            reasons.append(f"Warning: {conflicts[0]}")
        
        return "; ".join(reasons[:3])

    def get_signal_direction(self) -> str:
        """
        Get signal direction
        
        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        if self.final_signal is None:
            return 'HOLD'
        
        if self.final_signal > 0.3:
            return 'BUY'
        elif self.final_signal < -0.3:
            return 'SELL'
        else:
            return 'HOLD'

    def get_signal_strength(self) -> str:
        """
        Get signal strength
        
        Returns:
            'STRONG', 'MODERATE', or 'WEAK'
        """
        if self.final_signal is None:
            return 'WEAK'
        
        strength = abs(self.final_signal)
        
        if strength > 0.7:
            return 'STRONG'
        elif strength > 0.4:
            return 'MODERATE'
        else:
            return 'WEAK'
