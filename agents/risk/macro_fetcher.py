"""
Risk Agent - Macro Fetcher Module
Fetches macroeconomic indicators from FRED API
"""

import os
from typing import Dict, Any, Optional
import logging
import requests

logger = logging.getLogger(__name__)


class MacroFetcher:
    """Fetches macroeconomic indicators"""

    # FRED API series IDs
    FRED_SERIES = {
        'vix': 'VIXCLS',                    # VIX Index
        'yield_10y': 'DGS10',               # 10-Year Treasury Yield
        'yield_2y': 'DGS2',                 # 2-Year Treasury Yield
        'unemployment': 'UNRATE',           # Unemployment Rate
        'credit_spreads': 'BAMLH0A0HYM2',  # High Yield OAS
        'fed_funds': 'FEDFUNDS',            # Federal Funds Rate
        'inflation': 'CPIAUCSL',            # CPI
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize macro fetcher
        
        Args:
            api_key: FRED API key (defaults to FRED_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('FRED_API_KEY')
        self.base_url = 'https://api.stlouisfed.org/fred/series/observations'
        self.data = {}

    def fetch_vix(self) -> Optional[float]:
        """
        Fetch current VIX level
        
        Returns:
            VIX value or None if unavailable
        """
        try:
            value = self._fetch_series(self.FRED_SERIES['vix'])
            if value is not None:
                self.data['vix'] = value
            return value
        except Exception as e:
            logger.error(f"Error fetching VIX: {str(e)}")
            return None

    def fetch_yield_curve(self) -> Optional[Dict[str, float]]:
        """
        Fetch yield curve (2Y and 10Y yields)
        
        Returns:
            Dictionary with 2Y and 10Y yields, or None if unavailable
        """
        try:
            yield_2y = self._fetch_series(self.FRED_SERIES['yield_2y'])
            yield_10y = self._fetch_series(self.FRED_SERIES['yield_10y'])
            
            if yield_2y is not None and yield_10y is not None:
                curve = {
                    'yield_2y': yield_2y,
                    'yield_10y': yield_10y,
                    'spread': yield_10y - yield_2y,
                    'status': 'inverted' if yield_10y < yield_2y else 'normal'
                }
                self.data['yield_curve'] = curve
                return curve
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching yield curve: {str(e)}")
            return None

    def fetch_unemployment(self) -> Optional[float]:
        """
        Fetch unemployment rate
        
        Returns:
            Unemployment rate or None if unavailable
        """
        try:
            value = self._fetch_series(self.FRED_SERIES['unemployment'])
            if value is not None:
                self.data['unemployment'] = value
            return value
        except Exception as e:
            logger.error(f"Error fetching unemployment: {str(e)}")
            return None

    def fetch_credit_spreads(self) -> Optional[float]:
        """
        Fetch high yield credit spreads (OAS)
        
        Returns:
            Credit spread value or None if unavailable
        """
        try:
            value = self._fetch_series(self.FRED_SERIES['credit_spreads'])
            if value is not None:
                self.data['credit_spreads'] = value
            return value
        except Exception as e:
            logger.error(f"Error fetching credit spreads: {str(e)}")
            return None

    def fetch_fed_funds_rate(self) -> Optional[float]:
        """
        Fetch Federal Funds Rate
        
        Returns:
            Fed funds rate or None if unavailable
        """
        try:
            value = self._fetch_series(self.FRED_SERIES['fed_funds'])
            if value is not None:
                self.data['fed_funds'] = value
            return value
        except Exception as e:
            logger.error(f"Error fetching Fed funds rate: {str(e)}")
            return None

    def fetch_all_macro_indicators(self) -> Dict[str, Any]:
        """
        Fetch all macro indicators
        
        Returns:
            Dictionary with all macro indicators
        """
        logger.info("Fetching macroeconomic indicators...")
        
        self.fetch_vix()
        self.fetch_yield_curve()
        self.fetch_unemployment()
        self.fetch_credit_spreads()
        self.fetch_fed_funds_rate()
        
        return self.data

    def _fetch_series(self, series_id: str) -> Optional[float]:
        """
        Fetch a single FRED series
        
        Args:
            series_id: FRED series ID
            
        Returns:
            Latest value or None if unavailable
        """
        if not self.api_key:
            logger.warning("FRED_API_KEY not set, cannot fetch macro data")
            return None
        
        try:
            params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json',
                'limit': 1,
                'sort_order': 'desc'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            observations = data.get('observations', [])
            
            if observations:
                latest = observations[0]
                value = latest.get('value')
                if value and value != '.':
                    return float(value)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching FRED series {series_id}: {str(e)}")
            return None

    def get_macro_data(self) -> Dict[str, Any]:
        """
        Get cached macro data
        
        Returns:
            Dictionary with macro indicators
        """
        return self.data

    def assess_macro_risks(self) -> Dict[str, Any]:
        """
        Assess macroeconomic risks
        
        Returns:
            Dictionary with risk assessment
        """
        risks = {
            'yield_curve_risk': 'normal',
            'vix_risk': 'normal',
            'credit_risk': 'normal',
            'employment_risk': 'normal',
            'overall_risk_level': 'low'
        }
        
        try:
            # Yield curve risk
            yield_curve = self.data.get('yield_curve', {})
            if yield_curve.get('status') == 'inverted':
                risks['yield_curve_risk'] = 'high'
                logger.warning("Inverted yield curve detected - recession risk")
            
            # VIX risk
            vix = self.data.get('vix', 20)
            if vix > 30:
                risks['vix_risk'] = 'high'
                logger.warning(f"High VIX level: {vix}")
            elif vix > 20:
                risks['vix_risk'] = 'moderate'
            
            # Credit spreads risk
            spreads = self.data.get('credit_spreads', 300)
            if spreads > 600:
                risks['credit_risk'] = 'high'
                logger.warning(f"Wide credit spreads: {spreads} bps")
            elif spreads > 400:
                risks['credit_risk'] = 'moderate'
            
            # Employment risk
            unemployment = self.data.get('unemployment', 4.0)
            if unemployment > 6.0:
                risks['employment_risk'] = 'high'
                logger.warning(f"High unemployment: {unemployment}%")
            elif unemployment > 5.0:
                risks['employment_risk'] = 'moderate'
            
            # Overall risk level
            risk_count = sum(1 for v in risks.values() if v == 'high')
            if risk_count >= 2:
                risks['overall_risk_level'] = 'high'
            elif risk_count >= 1:
                risks['overall_risk_level'] = 'moderate'
            
            return risks
            
        except Exception as e:
            logger.error(f"Error assessing macro risks: {str(e)}")
            return risks
