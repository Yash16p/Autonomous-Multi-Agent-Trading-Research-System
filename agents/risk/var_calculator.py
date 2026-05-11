"""
Risk Agent - VaR Calculator Module
Computes risk metrics: VaR, CVaR, Max Drawdown, Sharpe Ratio, Beta
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class VaRCalculator:
    """Computes Value at Risk and other risk metrics"""

    def __init__(self, returns: pd.Series, risk_free_rate: float = 0.04):
        """
        Initialize VaR calculator
        
        Args:
            returns: Series of returns (daily, weekly, monthly, etc.)
            risk_free_rate: Annual risk-free rate (default 4%)
        """
        self.returns = returns
        self.risk_free_rate = risk_free_rate
        self.metrics = {}

    def compute_var(self, confidence: float = 0.95, method: str = 'historical') -> float:
        """
        Compute Value at Risk
        
        Args:
            confidence: Confidence level (0.95 = 95%)
            method: 'historical' or 'parametric'
            
        Returns:
            VaR as percentage loss
        """
        try:
            if method == 'historical':
                var = np.percentile(self.returns, (1 - confidence) * 100)
            else:  # parametric
                mean = self.returns.mean()
                std = self.returns.std()
                z_score = np.abs(np.percentile(np.random.standard_normal(10000), (1 - confidence) * 100))
                var = mean - z_score * std
            
            self.metrics['var_95'] = float(var * 100)  # Convert to percentage
            return float(var)
            
        except Exception as e:
            logger.error(f"Error computing VaR: {str(e)}")
            return 0.0

    def compute_cvar(self, confidence: float = 0.95) -> float:
        """
        Compute Conditional Value at Risk (Expected Shortfall)
        
        Args:
            confidence: Confidence level (0.95 = 95%)
            
        Returns:
            CVaR as percentage loss
        """
        try:
            var = np.percentile(self.returns, (1 - confidence) * 100)
            cvar = self.returns[self.returns <= var].mean()
            
            self.metrics['cvar_95'] = float(cvar * 100)  # Convert to percentage
            return float(cvar)
            
        except Exception as e:
            logger.error(f"Error computing CVaR: {str(e)}")
            return 0.0

    def compute_max_drawdown(self, prices: pd.Series) -> float:
        """
        Compute maximum drawdown
        
        Args:
            prices: Series of prices
            
        Returns:
            Maximum drawdown as percentage
        """
        try:
            cumulative_returns = (1 + self.returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_dd = drawdown.min()
            
            self.metrics['max_drawdown'] = float(max_dd * 100)
            return float(max_dd)
            
        except Exception as e:
            logger.error(f"Error computing max drawdown: {str(e)}")
            return 0.0

    def compute_sharpe_ratio(self, periods_per_year: int = 252) -> float:
        """
        Compute Sharpe Ratio
        
        Args:
            periods_per_year: Number of periods per year (252 for daily)
            
        Returns:
            Sharpe ratio
        """
        try:
            excess_return = self.returns.mean() - (self.risk_free_rate / periods_per_year)
            volatility = self.returns.std()
            
            if volatility == 0:
                sharpe = 0.0
            else:
                sharpe = (excess_return / volatility) * np.sqrt(periods_per_year)
            
            self.metrics['sharpe_ratio'] = float(sharpe)
            return float(sharpe)
            
        except Exception as e:
            logger.error(f"Error computing Sharpe ratio: {str(e)}")
            return 0.0

    def compute_sortino_ratio(self, target_return: float = 0.0, periods_per_year: int = 252) -> float:
        """
        Compute Sortino Ratio (penalizes downside volatility only)
        
        Args:
            target_return: Target return threshold
            periods_per_year: Number of periods per year
            
        Returns:
            Sortino ratio
        """
        try:
            excess_return = self.returns.mean() - (self.risk_free_rate / periods_per_year)
            
            # Downside deviation
            downside_returns = self.returns[self.returns < target_return]
            downside_std = downside_returns.std()
            
            if downside_std == 0:
                sortino = 0.0
            else:
                sortino = (excess_return / downside_std) * np.sqrt(periods_per_year)
            
            self.metrics['sortino_ratio'] = float(sortino)
            return float(sortino)
            
        except Exception as e:
            logger.error(f"Error computing Sortino ratio: {str(e)}")
            return 0.0

    def compute_beta(self, market_returns: pd.Series) -> float:
        """
        Compute Beta (market correlation)
        
        Args:
            market_returns: Series of market returns (e.g., S&P 500)
            
        Returns:
            Beta coefficient
        """
        try:
            # Align series
            aligned = pd.DataFrame({
                'stock': self.returns,
                'market': market_returns
            }).dropna()
            
            if len(aligned) < 2:
                return 1.0
            
            covariance = aligned['stock'].cov(aligned['market'])
            market_variance = aligned['market'].var()
            
            if market_variance == 0:
                beta = 1.0
            else:
                beta = covariance / market_variance
            
            self.metrics['beta'] = float(beta)
            return float(beta)
            
        except Exception as e:
            logger.error(f"Error computing beta: {str(e)}")
            return 1.0

    def compute_volatility(self, annualized: bool = True, periods_per_year: int = 252) -> float:
        """
        Compute volatility
        
        Args:
            annualized: Whether to annualize the volatility
            periods_per_year: Number of periods per year
            
        Returns:
            Volatility as percentage
        """
        try:
            vol = self.returns.std()
            
            if annualized:
                vol = vol * np.sqrt(periods_per_year)
            
            self.metrics['volatility'] = float(vol * 100)
            return float(vol)
            
        except Exception as e:
            logger.error(f"Error computing volatility: {str(e)}")
            return 0.0

    def compute_all_metrics(self, market_returns: Optional[pd.Series] = None,
                           prices: Optional[pd.Series] = None) -> Dict[str, float]:
        """
        Compute all risk metrics
        
        Args:
            market_returns: Market returns for beta calculation
            prices: Price series for drawdown calculation
            
        Returns:
            Dictionary with all metrics
        """
        self.compute_var()
        self.compute_cvar()
        self.compute_sharpe_ratio()
        self.compute_sortino_ratio()
        self.compute_volatility()
        
        if market_returns is not None:
            self.compute_beta(market_returns)
        
        if prices is not None:
            self.compute_max_drawdown(prices)
        
        return self.metrics

    def get_metrics(self) -> Dict[str, float]:
        """
        Get computed metrics
        
        Returns:
            Dictionary with metrics
        """
        return self.metrics

    def assess_risk_level(self) -> Tuple[str, float]:
        """
        Assess overall risk level based on metrics
        
        Returns:
            Tuple of (risk_level, risk_score [0-1])
        """
        try:
            risk_score = 0.0
            
            # VaR assessment (higher loss = higher risk)
            var = abs(self.metrics.get('var_95', 0)) / 100
            risk_score += min(var / 0.05, 1.0) * 0.3  # 30% weight
            
            # Volatility assessment
            vol = self.metrics.get('volatility', 0) / 100
            risk_score += min(vol / 0.30, 1.0) * 0.3  # 30% weight
            
            # Sharpe ratio assessment (lower = higher risk)
            sharpe = self.metrics.get('sharpe_ratio', 0)
            sharpe_risk = max(0, 1 - sharpe / 1.0)
            risk_score += sharpe_risk * 0.2  # 20% weight
            
            # Max drawdown assessment
            max_dd = abs(self.metrics.get('max_drawdown', 0)) / 100
            risk_score += min(max_dd / 0.20, 1.0) * 0.2  # 20% weight
            
            # Determine risk level
            if risk_score > 0.7:
                risk_level = 'high'
            elif risk_score > 0.4:
                risk_level = 'moderate'
            else:
                risk_level = 'low'
            
            return risk_level, float(risk_score)
            
        except Exception as e:
            logger.error(f"Error assessing risk level: {str(e)}")
            return 'unknown', 0.5
