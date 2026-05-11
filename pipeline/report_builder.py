"""
Pipeline - Report Builder Module
Generates structured trading analysis reports
"""

import logging
from typing import Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ReportBuilder:
    """Builds comprehensive trading analysis reports"""

    def __init__(self, ticker: str):
        """
        Initialize report builder
        
        Args:
            ticker: Stock ticker symbol
        """
        self.ticker = ticker.upper()
        self.report = None

    def build_report(self, quant_output: Dict[str, Any],
                    sentiment_output: Dict[str, Any],
                    risk_output: Dict[str, Any],
                    synthesis_output: Dict[str, Any],
                    rl_output: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Build comprehensive report
        
        Args:
            quant_output: Quantitative analysis output
            sentiment_output: Sentiment analysis output
            risk_output: Risk analysis output
            synthesis_output: Signal synthesis output
            rl_output: Optional RL optimization output
            
        Returns:
            Comprehensive report dictionary
        """
        try:
            logger.info(f"Building report for {self.ticker}")
            
            # Extract key data
            final_signal = synthesis_output.get('final_signal', 0.0)
            confidence = synthesis_output.get('confidence', 0.0)
            
            # Determine recommendation
            recommendation = self._get_recommendation(final_signal, confidence)
            
            # Build report sections
            self.report = {
                'metadata': {
                    'ticker': self.ticker,
                    'timestamp': datetime.now().isoformat(),
                    'report_version': '1.0'
                },
                'executive_summary': self._build_executive_summary(
                    final_signal, confidence, recommendation
                ),
                'quantitative_analysis': self._build_quant_section(quant_output),
                'sentiment_analysis': self._build_sentiment_section(sentiment_output),
                'risk_assessment': self._build_risk_section(risk_output),
                'signal_synthesis': self._build_synthesis_section(synthesis_output),
                'rl_optimization': self._build_rl_section(rl_output) if rl_output else None,
                'final_recommendation': {
                    'direction': recommendation['direction'],
                    'confidence': float(confidence),
                    'strength': recommendation['strength'],
                    'rationale': recommendation['rationale']
                },
                'risk_disclosure': self._build_risk_disclosure(risk_output),
                'action_items': self._build_action_items(
                    quant_output, sentiment_output, risk_output, recommendation
                )
            }
            
            logger.info(f"Report built successfully for {self.ticker}")
            return self.report
            
        except Exception as e:
            logger.error(f"Error building report: {str(e)}")
            return {'error': str(e)}

    def _build_executive_summary(self, signal: float, confidence: float,
                                recommendation: Dict[str, Any]) -> str:
        """Build executive summary"""
        direction = recommendation['direction']
        strength = recommendation['strength']
        
        summary = f"{self.ticker} receives a {strength} {direction} signal with {confidence:.0%} confidence. "
        
        if direction == 'BUY':
            summary += "Technical indicators and sentiment are aligned bullishly. "
        elif direction == 'SELL':
            summary += "Technical indicators and sentiment are aligned bearishly. "
        else:
            summary += "Signals are mixed with no clear directional bias. "
        
        summary += "See detailed analysis below for risk considerations."
        
        return summary

    def _build_quant_section(self, quant_output: Dict[str, Any]) -> Dict[str, Any]:
        """Build quantitative analysis section"""
        return {
            'signal': quant_output.get('signal', 0.0),
            'confidence': quant_output.get('confidence', 0.0),
            'key_indicators': quant_output.get('indicators', {}),
            'reasoning': quant_output.get('reasoning', ''),
            'sentiment': quant_output.get('sentiment', 'neutral')
        }

    def _build_sentiment_section(self, sentiment_output: Dict[str, Any]) -> Dict[str, Any]:
        """Build sentiment analysis section"""
        return {
            'signal': sentiment_output.get('signal', 0.0),
            'confidence': sentiment_output.get('confidence', 0.0),
            'sentiment': sentiment_output.get('sentiment', 'neutral'),
            'article_count': sentiment_output.get('article_count', 0),
            'bullish_articles': sentiment_output.get('bullish_articles', 0),
            'bearish_articles': sentiment_output.get('bearish_articles', 0),
            'key_themes': sentiment_output.get('themes', []),
            'recency_score': sentiment_output.get('recency_score', 0.0),
            'reasoning': sentiment_output.get('reasoning', '')
        }

    def _build_risk_section(self, risk_output: Dict[str, Any]) -> Dict[str, Any]:
        """Build risk assessment section"""
        return {
            'signal': risk_output.get('signal', 0.0),
            'confidence': risk_output.get('confidence', 0.0),
            'overall_risk_level': risk_output.get('overall_risk_level', 'unknown'),
            'risk_metrics': risk_output.get('risk_metrics', {}),
            'macro_risks': risk_output.get('macro_risks', {}),
            'risk_flags': risk_output.get('risk_flags', []),
            'reasoning': risk_output.get('reasoning', '')
        }

    def _build_synthesis_section(self, synthesis_output: Dict[str, Any]) -> Dict[str, Any]:
        """Build signal synthesis section"""
        return {
            'final_signal': synthesis_output.get('final_signal', 0.0),
            'confidence': synthesis_output.get('confidence', 0.0),
            'weights': synthesis_output.get('weights', {}),
            'component_signals': synthesis_output.get('component_signals', {}),
            'conflicts': synthesis_output.get('conflicts', []),
            'reasoning': synthesis_output.get('reasoning', '')
        }

    def _build_rl_section(self, rl_output: Dict[str, Any]) -> Dict[str, Any]:
        """Build RL optimization section"""
        if not rl_output:
            return None
        
        return {
            'optimized_signal': rl_output.get('final_signal', 0.0),
            'weights': rl_output.get('weights', {}),
            'regime': rl_output.get('regime', 'unknown'),
            'policy_confidence': rl_output.get('confidence', 0.0),
            'reasoning': rl_output.get('reasoning', '')
        }

    def _build_risk_disclosure(self, risk_output: Dict[str, Any]) -> Dict[str, Any]:
        """Build risk disclosure section"""
        risk_flags = risk_output.get('risk_flags', [])
        
        disclosures = {
            'key_risks': [],
            'monitoring_items': [],
            'stop_loss_recommendation': None
        }
        
        # Map risk flags to disclosures
        risk_map = {
            'high_var': 'High Value at Risk - significant downside potential',
            'high_volatility': 'High volatility - expect large price swings',
            'poor_risk_adjusted_returns': 'Poor risk-adjusted returns - low Sharpe ratio',
            'high_drawdown': 'High maximum drawdown - significant historical losses',
            'elevated_beta': 'Elevated beta - more volatile than market',
            'inverted_yield_curve': 'Inverted yield curve - recession risk',
            'high_vix': 'High VIX - elevated market stress',
            'wide_credit_spreads': 'Wide credit spreads - elevated default risk'
        }
        
        for flag in risk_flags:
            if flag in risk_map:
                disclosures['key_risks'].append(risk_map[flag])
        
        # Monitoring items
        disclosures['monitoring_items'] = [
            'Watch for earnings announcements',
            'Monitor macro economic data',
            'Track sector rotation trends',
            'Observe volume and volatility changes'
        ]
        
        # Stop loss recommendation
        var = abs(risk_output.get('risk_metrics', {}).get('var_95', 2.0))
        disclosures['stop_loss_recommendation'] = f"Consider {var:.1f}% stop loss"
        
        return disclosures

    def _build_action_items(self, quant_output: Dict[str, Any],
                           sentiment_output: Dict[str, Any],
                           risk_output: Dict[str, Any],
                           recommendation: Dict[str, Any]) -> list:
        """Build action items"""
        items = []
        
        # Based on recommendation
        if recommendation['direction'] == 'BUY':
            items.append('Consider initiating long position')
            items.append('Set profit target at 2x risk')
            items.append('Monitor for breakout confirmation')
        elif recommendation['direction'] == 'SELL':
            items.append('Consider initiating short position or reducing longs')
            items.append('Set profit target at 2x risk')
            items.append('Monitor for breakdown confirmation')
        else:
            items.append('Wait for clearer signal before trading')
            items.append('Monitor key support/resistance levels')
        
        # Risk-based actions
        risk_flags = risk_output.get('risk_flags', [])
        if 'high_volatility' in risk_flags:
            items.append('Use wider stops due to high volatility')
        
        if 'elevated_beta' in risk_flags:
            items.append('Consider hedging with options')
        
        # Sentiment-based actions
        themes = sentiment_output.get('themes', [])
        if themes:
            top_theme = themes[0].get('theme', '')
            if top_theme == 'earnings':
                items.append('Monitor for earnings announcement')
        
        return items[:5]  # Limit to 5 items

    def _get_recommendation(self, signal: float, confidence: float) -> Dict[str, Any]:
        """Get recommendation from signal"""
        if signal > 0.3:
            direction = 'BUY'
        elif signal < -0.3:
            direction = 'SELL'
        else:
            direction = 'HOLD'
        
        strength = 'STRONG' if abs(signal) > 0.7 else 'MODERATE' if abs(signal) > 0.4 else 'WEAK'
        
        rationale = f"{direction} signal with {strength.lower()} conviction"
        
        return {
            'direction': direction,
            'strength': strength,
            'rationale': rationale
        }

    def to_json(self) -> str:
        """Convert report to JSON"""
        if self.report:
            return json.dumps(self.report, indent=2)
        return json.dumps({'error': 'No report generated'}, indent=2)

    def to_markdown(self) -> str:
        """Convert report to Markdown"""
        if not self.report:
            return "# No Report Generated"
        
        md = f"# Trading Analysis Report: {self.ticker}\n\n"
        md += f"**Generated:** {self.report['metadata']['timestamp']}\n\n"
        
        # Executive Summary
        md += "## Executive Summary\n\n"
        md += f"{self.report['executive_summary']}\n\n"
        
        # Final Recommendation
        rec = self.report['final_recommendation']
        md += "## Final Recommendation\n\n"
        md += f"**Direction:** {rec['direction']}\n"
        md += f"**Confidence:** {rec['confidence']:.0%}\n"
        md += f"**Strength:** {rec['strength']}\n"
        md += f"**Rationale:** {rec['rationale']}\n\n"
        
        # Key Metrics
        md += "## Key Metrics\n\n"
        quant = self.report['quantitative_analysis']
        md += f"- Quant Signal: {quant['signal']:.2f}\n"
        md += f"- Sentiment: {self.report['sentiment_analysis']['sentiment']}\n"
        md += f"- Risk Level: {self.report['risk_assessment']['overall_risk_level']}\n\n"
        
        # Risk Disclosure
        md += "## Risk Disclosure\n\n"
        risks = self.report['risk_disclosure']
        for risk in risks['key_risks']:
            md += f"- {risk}\n"
        
        return md
