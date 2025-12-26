"""Multi-stage stock screener for algorithmic trading."""

from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Protocol, Callable
from dataclasses import dataclass

from algotrader.core import get_logger

logger = get_logger(__name__)


@dataclass
class ScreeningCriteria:
    """Criteria for stock screening."""
    
    # Liquidity filters
    min_avg_volume_inr: float = 10_00_00_000  # ₹10 crore daily
    min_price: float = 50.0
    max_price: float = 5000.0
    
    # Market cap filters
    min_market_cap_cr: float = 1000.0  # ₹1000 crore
    
    # Technical filters
    min_days_data: int = 250  # Minimum 1 year data
    price_above_ma200: bool = True  # Trend filter
    min_atr_pct: float = 1.0  # Minimum volatility
    max_atr_pct: float = 8.0  # Maximum volatility
    
    # Strategy filters
    min_sharpe: float = 0.8
    min_win_rate: float = 0.45
    max_drawdown_pct: float = 25.0
    min_trades: int = 5  # Minimum trades for statistical significance
    
    # Portfolio construction
    max_stocks_per_sector: int = 3
    target_portfolio_size: int = 10


class StockScreener:
    """Multi-stage stock screener for algo trading.
    
    Implements a professional 4-stage filtering process:
    1. Universe Definition - Basic filters (liquidity, price, market cap)
    2. Technical Screening - Trend, volatility, momentum
    3. Strategy Fit - Backtest and rank by performance
    4. Portfolio Construction - Diversification and correlation
    
    Args:
        criteria: Screening criteria configuration
    """
    
    def __init__(self, criteria: ScreeningCriteria | None = None):
        self.criteria = criteria or ScreeningCriteria()
        logger.info(f"StockScreener initialized with {self.criteria}")
    
    def stage1_universe_filter(
        self, 
        stocks_data: dict[str, pd.DataFrame],
        metadata: dict[str, dict] | None = None
    ) -> dict[str, pd.DataFrame]:
        """Stage 1: Filter by liquidity, price, and market cap.
        
        Args:
            stocks_data: Dict of {symbol: OHLCV DataFrame}
            metadata: Optional dict of {symbol: {sector, market_cap, etc}}
            
        Returns:
            Filtered dict of stocks passing basic criteria
        """
        logger.info(f"Stage 1: Filtering {len(stocks_data)} stocks by universe criteria...")
        
        passed = {}
        reasons = []
        
        for symbol, df in stocks_data.items():
            # Check minimum data requirement
            if len(df) < self.criteria.min_days_data:
                reasons.append((symbol, f"Insufficient data: {len(df)} < {self.criteria.min_days_data}"))
                continue
            
            # Calculate average daily value traded
            avg_value = (df['close'] * df['volume']).mean()
            if avg_value < self.criteria.min_avg_volume_inr:
                reasons.append((symbol, f"Low liquidity: ₹{avg_value/1e7:.1f}Cr < ₹{self.criteria.min_avg_volume_inr/1e7:.1f}Cr"))
                continue
            
            # Price range check
            current_price = df['close'].iloc[-1]
            if current_price < self.criteria.min_price:
                reasons.append((symbol, f"Price too low: ₹{current_price:.0f}"))
                continue
            if current_price > self.criteria.max_price:
                reasons.append((symbol, f"Price too high: ₹{current_price:.0f}"))
                continue
            
            # Market cap check (if available)
            if metadata and symbol in metadata:
                market_cap = metadata[symbol].get('market_cap_cr', 0)
                if market_cap > 0 and market_cap < self.criteria.min_market_cap_cr:
                    reasons.append((symbol, f"Small cap: ₹{market_cap:.0f}Cr"))
                    continue
            
            passed[symbol] = df
        
        logger.info(f"Stage 1 complete: {len(passed)}/{len(stocks_data)} stocks passed")
        if len(reasons) <= 10:
            for symbol, reason in reasons:
                logger.debug(f"  Rejected {symbol}: {reason}")
        
        return passed
    
    def stage2_technical_filter(
        self,
        stocks_data: dict[str, pd.DataFrame]
    ) -> dict[str, pd.DataFrame]:
        """Stage 2: Filter by technical indicators (trend, volatility).
        
        Args:
            stocks_data: Dict of {symbol: OHLCV DataFrame}
            
        Returns:
            Filtered dict of stocks passing technical criteria
        """
        logger.info(f"Stage 2: Filtering {len(stocks_data)} stocks by technical criteria...")
        
        passed = {}
        
        for symbol, df in stocks_data.items():
            close = df['close']
            
            # Trend filter: Price above 200-day MA
            if self.criteria.price_above_ma200:
                ma200 = close.rolling(200).mean()
                if close.iloc[-1] < ma200.iloc[-1]:
                    logger.debug(f"  Rejected {symbol}: Below 200-day MA")
                    continue
            
            # Volatility filter: ATR as % of price
            high = df['high']
            low = df['low']
            tr = pd.concat([
                high - low,
                (high - close.shift(1)).abs(),
                (low - close.shift(1)).abs()
            ], axis=1).max(axis=1)
            atr = tr.rolling(14).mean()
            atr_pct = (atr / close * 100).iloc[-1]
            
            if atr_pct < self.criteria.min_atr_pct:
                logger.debug(f"  Rejected {symbol}: ATR too low ({atr_pct:.1f}%)")
                continue
            if atr_pct > self.criteria.max_atr_pct:
                logger.debug(f"  Rejected {symbol}: ATR too high ({atr_pct:.1f}%)")
                continue
            
            passed[symbol] = df
        
        logger.info(f"Stage 2 complete: {len(passed)}/{len(stocks_data)} stocks passed")
        return passed
    
    def stage3_strategy_ranking(
        self,
        stocks_data: dict[str, pd.DataFrame],
        backtest_fn: Callable[[pd.DataFrame], dict]
    ) -> list[tuple[str, dict]]:
        """Stage 3: Backtest strategy and rank by performance.
        
        Args:
            stocks_data: Dict of {symbol: OHLCV DataFrame}
            backtest_fn: Function that takes DataFrame and returns metrics dict
            
        Returns:
            List of (symbol, metrics) tuples ranked by Sharpe ratio
        """
        logger.info(f"Stage 3: Backtesting {len(stocks_data)} stocks...")
        
        results = []
        
        for symbol, df in stocks_data.items():
            try:
                metrics = backtest_fn(df)
                
                # Filter by strategy performance
                sharpe = metrics.get('sharpe_ratio', -999)
                win_rate = metrics.get('win_rate', 0)
                max_dd = metrics.get('max_drawdown', 1.0)
                trades = metrics.get('trades', 0)
                
                # Apply filters
                if sharpe < self.criteria.min_sharpe:
                    logger.debug(f"  Rejected {symbol}: Low Sharpe ({sharpe:.2f})")
                    continue
                if win_rate < self.criteria.min_win_rate:
                    logger.debug(f"  Rejected {symbol}: Low win rate ({win_rate:.1%})")
                    continue
                if max_dd > self.criteria.max_drawdown_pct / 100:
                    logger.debug(f"  Rejected {symbol}: High drawdown ({max_dd:.1%})")
                    continue
                if trades < self.criteria.min_trades:
                    logger.debug(f"  Rejected {symbol}: Too few trades ({trades})")
                    continue
                
                results.append((symbol, metrics))
                logger.debug(f"  ✓ {symbol}: Sharpe={sharpe:.2f}, Return={metrics.get('total_return', 0):.1%}")
                
            except Exception as e:
                logger.warning(f"  Error backtesting {symbol}: {e}")
                continue
        
        # Rank by Sharpe ratio
        results.sort(key=lambda x: x[1].get('sharpe_ratio', -999), reverse=True)
        
        logger.info(f"Stage 3 complete: {len(results)} stocks passed strategy filters")
        return results
    
    def stage4_portfolio_construction(
        self,
        ranked_results: list[tuple[str, dict]],
        metadata: dict[str, dict] | None = None
    ) -> list[tuple[str, dict]]:
        """Stage 4: Build diversified portfolio.
        
        Args:
            ranked_results: List of (symbol, metrics) ranked by performance
            metadata: Optional dict of {symbol: {sector, etc}}
            
        Returns:
            Final portfolio list of (symbol, metrics)
        """
        logger.info(f"Stage 4: Building portfolio from {len(ranked_results)} candidates...")
        
        portfolio = []
        sector_counts = {}
        
        for symbol, metrics in ranked_results:
            # Check portfolio size limit
            if len(portfolio) >= self.criteria.target_portfolio_size:
                break
            
            # Check sector diversification (if metadata available)
            if metadata and symbol in metadata:
                sector = metadata[symbol].get('sector', 'Unknown')
                sector_count = sector_counts.get(sector, 0)
                
                if sector_count >= self.criteria.max_stocks_per_sector:
                    logger.debug(f"  Skipped {symbol}: Sector limit reached for {sector}")
                    continue
                
                sector_counts[sector] = sector_count + 1
            
            portfolio.append((symbol, metrics))
            logger.info(f"  Added {symbol}: Sharpe={metrics['sharpe_ratio']:.2f}, Return={metrics['total_return']:.1%}")
        
        logger.info(f"Stage 4 complete: Portfolio of {len(portfolio)} stocks constructed")
        return portfolio
    
    def screen(
        self,
        stocks_data: dict[str, pd.DataFrame],
        backtest_fn: Callable[[pd.DataFrame], dict],
        metadata: dict[str, dict] | None = None
    ) -> list[tuple[str, dict]]:
        """Run complete 4-stage screening process.
        
        Args:
            stocks_data: Dict of {symbol: OHLCV DataFrame}
            backtest_fn: Function to backtest strategy on each stock
            metadata: Optional metadata (sector, market cap, etc)
            
        Returns:
            Final portfolio list of (symbol, metrics) tuples
        """
        logger.info(f"Starting 4-stage screening on {len(stocks_data)} stocks...")
        
        # Stage 1: Universe filter
        stage1_passed = self.stage1_universe_filter(stocks_data, metadata)
        
        # Stage 2: Technical filter
        stage2_passed = self.stage2_technical_filter(stage1_passed)
        
        # Stage 3: Strategy ranking
        ranked = self.stage3_strategy_ranking(stage2_passed, backtest_fn)
        
        # Stage 4: Portfolio construction
        portfolio = self.stage4_portfolio_construction(ranked, metadata)
        
        logger.info(f"Screening complete: {len(portfolio)} stocks selected from {len(stocks_data)}")
        return portfolio
    
    def print_screening_summary(self, portfolio: list[tuple[str, dict]]):
        """Print formatted summary of screening results."""
        print("\n" + "=" * 100)
        print("STOCK SCREENING RESULTS")
        print("=" * 100)
        print(f"{'Rank':<6} {'Symbol':<15} {'Sharpe':<10} {'Return':<12} {'MaxDD':<10} {'Win%':<10} {'Trades':<8}")
        print("-" * 100)
        
        for i, (symbol, metrics) in enumerate(portfolio, 1):
            print(
                f"{i:<6} {symbol:<15} "
                f"{metrics['sharpe_ratio']:<10.2f} "
                f"{metrics['total_return']:<12.2%} "
                f"{metrics['max_drawdown']:<10.2%} "
                f"{metrics['win_rate']:<10.1%} "
                f"{metrics['trades']:<8}"
            )
        
        print("=" * 100)
        
        # Summary stats
        if portfolio:
            avg_sharpe = sum(m['sharpe_ratio'] for _, m in portfolio) / len(portfolio)
            avg_return = sum(m['total_return'] for _, m in portfolio) / len(portfolio)
            print(f"\nPortfolio Statistics:")
            print(f"  Number of stocks: {len(portfolio)}")
            print(f"  Average Sharpe:   {avg_sharpe:.2f}")
            print(f"  Average Return:   {avg_return:.1%}")
