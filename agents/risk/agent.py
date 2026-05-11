"""
Risk Management Agent
Assesses portfolio and market risk exposure
"""

from typing import Dict, Any, Optional
import logging
import json
import pandas as pd
import numpy as np

from .macro_fetcher import MacroFetcher
from .var_calculator import VaRCalculator

logger = logging.getLogger(__name__)


class RiskAgent:
    """
    Risk Management Agent
    
    Responsibilities:
    - Compute risk metrics (VaR, CVaR, Max Drawdown, Sharpe Ratio, Beta)
    - Fetch macro indicators (yield curve, VIX, unemployment)
    - Flag systemic risks
    - Output: Risk score (0 = safe, 1 = dangerous)
    """

    def __init__(self, ticker: str):
        """
        Initialize Risk Agent
        
        Args:
            ticker: Stock ticker symbol
        """
        self.ticker = ticker.upper()
        self.macro_fetcher = MacroFetcher()
        self.var_calculator = None
        self.output = None

    def analyze(self, returns: pd.Series, prices: Optional[pd.Series] = None,
               market_returns: Optional[pd.Series] = None) -> Dict[str, Any]:
        """
        Perform risk analysis
        
        Args:
            returns: Series of returns
            prices: Series of prices (optional, for drawdown calculation)
            market_returns: Market returns (optional, for beta calculation)
            
        Returns:
            Dictionary with risk analysis results
        """
        try:
            logger.info(f"Starting risk analysis for {self.ticker}")
            
            # Step 1: Fetch macro indicators
            logger.info("Fetching macroeconomic indicators...")
            macro_data = self.macro_fetcher.fetch_all_macro_indicators()
            macro_risks = self.macro_fetcher.assess_macro_risks()
            
            # Step 2: Compute risk metrics
            logger.info("Computing risk metrics...")
            self.var_calculator = VaRCalculator(returns)
            risk_metrics = self.var_calculator.compute_all_metrics(
                market_returns=market_returns,
                prices=prices
            )
            
            # Step 3: Generate risk signal
            logger.info("Generating risk signal...")
            risk_signal, risk_score = self._generate_risk_signal(risk_metrics, macro_risks)
            
            # Step 4: Build output
            self.output = self._build_output(risk_signal, risk_metrics, macro_data, macro_risks)
            
            logger.info(f"Risk analysis complete. Risk Signal: {risk_signal:.2f}, Risk Score: {risk_score:.2f}")
            return self.output
            
        except Exception as e:
            logger.error(f"Error in risk analysis: {str(e)}")
            return self._error_output(str(e))

    def _generate_risk_signal(self, risk_metrics: Dict[str, float],
                             macro_risks: Dict[str, str]) -> tuple:
        """
        Generate risk signal from metrics
        
        Args:
            risk_metrics: Dictionary of risk metrics
            macro_risks: Dictionary of macro risk assessments
            
        Returns:
            Tuple of (risk_signal [-1, 1], risk_score [0, 1])
        """
        try:
            signal = 0.0
            risk_score = 0.0
            
            # VaR component (higher loss = higher risk = negative signal)
            var = abs(risk_metrics.get('var_95', 0)) / 100
            var_signal = -min(var / 0.05, 1.0)  # Normalize to [-1, 0]
            signal += var_signal * 0.3
            risk_score += min(var / 0.05, 1.0) * 0.3
            
            # Volatility component
            vol = risk_metrics.get('volatility', 0) / 100
            vol_signal = -min(vol / 0.30, 1.0)  # Normalize to [-1, 0]
            signal += vol_signal * 0.2
            risk_score += min(vol / 0.30, 1.0) * 0.2
            
            # Sharpe ratio component (lower = higher risk)
            sharpe = risk_metrics.get('sharpe_ratio', 0)
            sharpe_signal = -max(0, 1 - sharpe / 1.0)  # Normalize to [-1, 0]
            signal += sharpe_signal * 0.2
            risk_score += max(0, 1 - sharpe / 1.0) * 0.2
            
            # Max drawdown component
            max_dd = abs(risk_metrics.get('max_drawdown', 0)) / 100
            dd_signal = -min(max_dd / 0.20, 1.0)  # Normalize to [-1, 0]
            signal += dd_signal * 0.15
            risk_score += min(max_dd / 0.20, 1.0) * 0.15
            
            # Macro risks component
            macro_risk_count = sum(1 for v in macro_risks.values() if v == 'high')
            macro_signal = -(macro_risk_count / 4.0)  # Normalize to [-1, 0]
            signal += macro_signal * 0.15
            risk_score += (macro_risk_count / 4.0) * 0.15
            
            # Clamp signal to [-1, 1]
            signal = np.clip(signal, -1.0, 1.0)
            risk_score = np.clip(risk_score, 0.0, 1.0)
            
            return signal, risk_score
            
        except Exception as e:
            logger.error(f"Error generating risk signal: {str(e)}")
            return 0.0, 0.5

    def _build_output(self, risk_signal: float, risk_metrics: Dict[str, float],
                     macro_data: Dict[str, Any], macro_risks: Dict[str, str]) -> Dict[str, Any]:
        """
        Build structured output
        
        Args:
            risk_signal: Risk signal [-1, 1]
            risk_metrics: Dictionary of risk metrics
            macro_data: Macro indicators
            macro_risks: Macro risk assessment
            
        Returns:
            Structured output dictionary
        """
        # Determine risk flags
        risk_flags = []
        
        if abs(risk_metrics.get('var_95', 0)) > 2.5:
            risk_flags.append('high_var')
        
        if risk_metrics.get('volatility', 0) > 30:
            risk_flags.append('high_volatility')
        
        if risk_metrics.get('sharpe_ratio', 0) < 0.5:
            risk_flags.append('poor_risk_adjusted_returns')
        
        if abs(risk_metrics.get('max_drawdown', 0)) > 15:
            risk_flags.append('high_drawdown')
        
        if risk_metrics.get('beta', 1.0) > 1.3:
            risk_flags.append('elevated_beta')
        
        if macro_risks.get('yield_curve_risk') == 'high':
            risk_flags.append('inverted_yield_curve')
        
        if macro_risks.get('vix_risk') == 'high':
            risk_flags.append('high_vix')
        
        if macro_risks.get('credit_risk') == 'high':
            risk_flags.append('wide_credit_spreads')
        
        # Determine confidence
        confidence = 0.8 if risk_metrics else 0.3
        
        # Build reasoning
        reasoning = self._build_reasoning(risk_metrics, macro_risks, risk_flags)
        
        return {
            'agent': 'risk',
            'ticker': self.ticker,
            'signal': float(risk_signal),
            'confidence': float(confidence),
            'risk_metrics': {
                'var_95': risk_metrics.get('var_95', 0),
                'cvar_95': risk_metrics.get('cvar_95', 0),
                'max_drawdown': risk_metrics.get('max_drawdown', 0),
                'sharpe_ratio': risk_metrics.get('sharpe_ratio', 0),
                'sortino_ratio': risk_metrics.get('sortino_ratio', 0),
                'volatility': risk_metrics.get('volatility', 0),
                'beta': risk_metrics.get('beta', 1.0),
            },
            'macro_risks': {
                'yield_curve': macro_data.get('yield_curve', {}).get('status', 'unknown'),
                'yield_spread': macro_data.get('yield_curve', {}).get('spread', 0),
                'vix_level': macro_data.get('vix', 0),
                'unemployment': macro_data.get('unemployment', 0),
                'credit_spreads': macro_data.get('credit_spreads', 0),
                'fed_funds_rate': macro_data.get('fed_funds', 0),
            },
            'risk_flags': risk_flags,
            'overall_risk_level': macro_risks.get('overall_risk_level', 'unknown'),
            'reasoning': reasoning,
        }

    def _build_reasoning(self, risk_metrics: Dict[str, float],
                        macro_risks: Dict[str, str], risk_flags: list) -> str:
        """
        Build reasoning string
        
        Args:
            risk_metrics: Risk metrics
            macro_risks: Macro risks
            risk_flags: Risk flags
            
        Returns:
            Reasoning string
        """
        reasons = []
        
        # VaR reasoning
        var = abs(risk_metrics.get('var_95', 0))
        if var > 2.5:
            reasons.append(f"High VaR ({var:.2f}%) indicates significant downside risk")
        
        # Sharpe ratio reasoning
        sharpe = risk_metrics.get('sharpe_ratio', 0)
        if sharpe < 0.5:
            reasons.append(f"Low Sharpe ratio ({sharpe:.2f}) suggests poor risk-adjusted returns")
        
        # Macro reasoning
        if macro_risks.get('yield_curve_risk') == 'high':
            reasons.append("Inverted yield curve signals potential recession risk")
        
        if macro_risks.get('vix_risk') == 'high':
            reasons.append("Elevated VIX indicates market stress and uncertainty")
        
        if macro_risks.get('credit_risk') == 'high':
            reasons.append("Wide credit spreads suggest elevated default risk")
        
        if not reasons:
            reasons.append("Risk metrics within normal ranges")
        
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
            'agent': 'risk',
            'ticker': self.ticker,
            'signal': 0.0,
            'confidence': 0.0,
            'risk_metrics': {},
            'macro_risks': {},
            'risk_flags': [],
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
        Get the current risk signal
        
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
