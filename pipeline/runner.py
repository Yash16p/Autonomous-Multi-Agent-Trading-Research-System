"""
Pipeline - Runner Module
Main execution pipeline orchestrating all components
"""

import logging
from typing import Dict, Any, Optional
import pandas as pd

from agents.quant import QuantAgent
from agents.sentiment import SentimentAgent
from agents.risk import RiskAgent
from .synthesizer import SignalSynthesizer
from .report_builder import ReportBuilder

logger = logging.getLogger(__name__)


class PipelineRunner:
    """Main pipeline runner orchestrating all analysis components"""

    def __init__(self, ticker: str):
        """
        Initialize pipeline runner
        
        Args:
            ticker: Stock ticker symbol
        """
        self.ticker = ticker.upper()
        self.quant_agent = QuantAgent(self.ticker)
        self.sentiment_agent = SentimentAgent(self.ticker)
        self.risk_agent = RiskAgent(self.ticker)
        self.synthesizer = SignalSynthesizer()
        self.report_builder = ReportBuilder(self.ticker)
        
        self.results = {}

    def run(self, quant_period: str = '1y', sentiment_days: int = 7,
           rl_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Run complete analysis pipeline
        
        Args:
            quant_period: Period for quantitative analysis
            sentiment_days: Days to look back for sentiment
            rl_weights: Optional RL-optimized weights
            
        Returns:
            Complete analysis results
        """
        try:
            logger.info(f"Starting pipeline for {self.ticker}")
            
            # Step 1: Quantitative Analysis
            logger.info("Step 1: Quantitative Analysis")
            quant_output = self.quant_agent.analyze(period=quant_period)
            self.results['quant'] = quant_output
            
            # Step 2: Sentiment Analysis
            logger.info("Step 2: Sentiment Analysis")
            sentiment_output = self.sentiment_agent.analyze(days=sentiment_days)
            self.results['sentiment'] = sentiment_output
            
            # Step 3: Risk Analysis
            logger.info("Step 3: Risk Analysis")
            # For risk analysis, we need returns data
            # Fetch from quant agent's data
            if hasattr(self.quant_agent.data_fetcher, 'data') and self.quant_agent.data_fetcher.data is not None:
                data = self.quant_agent.data_fetcher.data
                returns = data['Close'].pct_change().dropna()
                risk_output = self.risk_agent.analyze(returns=returns, prices=data['Close'])
            else:
                logger.warning("No price data available for risk analysis")
                risk_output = self.risk_agent._error_output("No price data available")
            
            self.results['risk'] = risk_output
            
            # Step 4: Signal Synthesis
            logger.info("Step 4: Signal Synthesis")
            weights = rl_weights or {
                'quant': 0.40,
                'sentiment': 0.35,
                'risk': 0.25
            }
            synthesis_output = self.synthesizer.synthesize(
                quant_output, sentiment_output, risk_output, weights
            )
            self.results['synthesis'] = synthesis_output
            
            # Step 5: Report Generation
            logger.info("Step 5: Report Generation")
            report = self.report_builder.build_report(
                quant_output, sentiment_output, risk_output, synthesis_output
            )
            self.results['report'] = report
            
            logger.info(f"Pipeline complete for {self.ticker}")
            return self._build_final_output()
            
        except Exception as e:
            logger.error(f"Error running pipeline: {str(e)}")
            return {
                'error': str(e),
                'ticker': self.ticker,
                'status': 'failed'
            }

    def _build_final_output(self) -> Dict[str, Any]:
        """Build final output combining all results"""
        synthesis = self.results.get('synthesis', {})
        report = self.results.get('report', {})
        
        return {
            'ticker': self.ticker,
            'status': 'success',
            'final_signal': synthesis.get('final_signal', 0.0),
            'confidence': synthesis.get('confidence', 0.0),
            'recommendation': report.get('final_recommendation', {}),
            'component_signals': synthesis.get('component_signals', {}),
            'weights': synthesis.get('weights', {}),
            'conflicts': synthesis.get('conflicts', []),
            'quant_analysis': self.results.get('quant', {}),
            'sentiment_analysis': self.results.get('sentiment', {}),
            'risk_analysis': self.results.get('risk', {}),
            'report': report
        }

    def get_results(self) -> Dict[str, Any]:
        """Get all results"""
        return self.results

    def get_signal(self) -> float:
        """Get final signal"""
        return self.results.get('synthesis', {}).get('final_signal', 0.0)

    def get_recommendation(self) -> str:
        """Get recommendation"""
        signal = self.get_signal()
        if signal > 0.3:
            return 'BUY'
        elif signal < -0.3:
            return 'SELL'
        else:
            return 'HOLD'

    def get_report_json(self) -> str:
        """Get report as JSON"""
        return self.report_builder.to_json()

    def get_report_markdown(self) -> str:
        """Get report as Markdown"""
        return self.report_builder.to_markdown()
