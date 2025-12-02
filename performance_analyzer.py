"""
性能分析模块
计算和展示回测结果的各项指标
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime


class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self, results: Dict):
        """
        初始化性能分析器
        
        Args:
            results: 回测结果字典
        """
        self.results = results
        self.equity_curve = results.get('equity_curve', pd.Series())
        self.trades = results.get('trades', [])
        
    def print_summary(self):
        """打印回测摘要"""
        print("\n" + "="*60)
        print("回测结果摘要".center(60))
        print("="*60)
        
        # 收益指标
        print("\n【收益指标】")
        print(f"总收益率:        {self.results['total_return']:.2%}")
        print(f"年化收益率:      {self.results['annual_return']:.2%}")
        print(f"最终资产:        ¥{self.results['final_value']:,.2f}")
        
        # 风险指标
        print("\n【风险指标】")
        print(f"最大回撤:        {self.results['max_drawdown']:.2%}")
        print(f"夏普比率:        {self.results['sharpe_ratio']:.2f}")
        
        # 交易指标
        print("\n【交易指标】")
        print(f"总交易次数:      {self.results['total_trades']}")
        
        # 详细交易统计
        if self.trades:
            buy_trades = [t for t in self.trades if t.action == 'buy']
            sell_trades = [t for t in self.trades if t.action == 'sell']
            
            print(f"买入次数:        {len(buy_trades)}")
            print(f"卖出次数:        {len(sell_trades)}")
            
            if buy_trades:
                avg_buy_price = sum(t.price for t in buy_trades) / len(buy_trades)
                print(f"平均买入价:      ¥{avg_buy_price:.2f}")
            
            if sell_trades:
                avg_sell_price = sum(t.price for t in sell_trades) / len(sell_trades)
                print(f"平均卖出价:      ¥{avg_sell_price:.2f}")
            
            # 计算总手续费
            total_commission = sum(t.commission for t in self.trades)
            print(f"总手续费:        ¥{total_commission:,.2f}")
        
        print("\n" + "="*60)
        
    def get_monthly_returns(self) -> pd.DataFrame:
        """计算月度收益率"""
        if self.equity_curve.empty:
            return pd.DataFrame()
        
        df = pd.DataFrame({'value': self.equity_curve})
        df['return'] = df['value'].pct_change()
        
        # 按月分组
        monthly = df['return'].resample('M').apply(lambda x: (1 + x).prod() - 1)
        
        return monthly
    
    def get_yearly_returns(self) -> pd.DataFrame:
        """计算年度收益率"""
        if self.equity_curve.empty:
            return pd.DataFrame()
        
        df = pd.DataFrame({'value': self.equity_curve})
        df['return'] = df['value'].pct_change()
        
        # 按年分组
        yearly = df['return'].resample('Y').apply(lambda x: (1 + x).prod() - 1)
        
        return yearly
    
    def calculate_drawdown_details(self) -> pd.DataFrame:
        """计算详细的回撤信息"""
        if self.equity_curve.empty:
            return pd.DataFrame()
        
        df = pd.DataFrame({'value': self.equity_curve})
        df['cummax'] = df['value'].cummax()
        df['drawdown'] = (df['value'] - df['cummax']) / df['cummax']
        
        return df
    
    def get_trade_analysis(self) -> Dict:
        """分析交易记录"""
        if not self.trades:
            return {}
        
        # 配对买卖交易
        buy_trades = []
        sell_trades = []
        
        for trade in self.trades:
            if trade.action == 'buy':
                buy_trades.append(trade)
            else:
                sell_trades.append(trade)
        
        # 计算每笔交易的盈亏
        trade_returns = []
        for i in range(min(len(buy_trades), len(sell_trades))):
            buy = buy_trades[i]
            sell = sell_trades[i]
            
            profit = (sell.price - buy.price) * buy.quantity - buy.commission - sell.commission
            profit_rate = profit / (buy.price * buy.quantity)
            
            trade_returns.append({
                'buy_date': buy.date,
                'sell_date': sell.date,
                'buy_price': buy.price,
                'sell_price': sell.price,
                'quantity': buy.quantity,
                'profit': profit,
                'profit_rate': profit_rate,
                'holding_days': (sell.date - buy.date).days
            })
        
        if not trade_returns:
            return {}
        
        df = pd.DataFrame(trade_returns)
        
        winning_trades = df[df['profit'] > 0]
        losing_trades = df[df['profit'] < 0]
        
        analysis = {
            'total_trades': len(df),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(df) if len(df) > 0 else 0,
            'avg_profit': df['profit'].mean(),
            'avg_profit_rate': df['profit_rate'].mean(),
            'avg_holding_days': df['holding_days'].mean(),
            'max_profit': df['profit'].max(),
            'max_loss': df['profit'].min(),
            'profit_factor': abs(winning_trades['profit'].sum() / losing_trades['profit'].sum()) if len(losing_trades) > 0 and losing_trades['profit'].sum() != 0 else 0
        }
        
        return analysis
    
    def calculate_risk_metrics(self) -> Dict:
        """计算风险指标"""
        if self.equity_curve.empty:
            return {}
        
        returns = self.equity_curve.pct_change().dropna()
        
        # 下行风险
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252)
        
        # 索提诺比率（假设无风险利率3%）
        sortino_ratio = (returns.mean() * 252 - 0.03) / downside_std if downside_std > 0 else 0
        
        # 卡玛比率
        max_dd = self.results.get('max_drawdown', 0)
        calmar_ratio = self.results.get('annual_return', 0) / abs(max_dd) if max_dd != 0 else 0
        
        # VaR (Value at Risk) 95%
        var_95 = returns.quantile(0.05)
        
        # CVaR (Conditional VaR)
        cvar_95 = returns[returns <= var_95].mean()
        
        return {
            'downside_std': downside_std,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'volatility': returns.std() * np.sqrt(252)
        }
    
    def print_detailed_analysis(self):
        """打印详细分析"""
        print("\n" + "="*60)
        print("详细性能分析".center(60))
        print("="*60)
        
        # 交易分析
        trade_analysis = self.get_trade_analysis()
        if trade_analysis:
            print("\n【交易分析】")
            print(f"总交易次数:      {trade_analysis['total_trades']}")
            print(f"盈利次数:        {trade_analysis['winning_trades']}")
            print(f"亏损次数:        {trade_analysis['losing_trades']}")
            print(f"胜率:            {trade_analysis['win_rate']:.2%}")
            print(f"平均盈亏:        ¥{trade_analysis['avg_profit']:,.2f}")
            print(f"平均盈亏率:      {trade_analysis['avg_profit_rate']:.2%}")
            print(f"平均持仓天数:    {trade_analysis['avg_holding_days']:.1f}")
            print(f"最大单笔盈利:    ¥{trade_analysis['max_profit']:,.2f}")
            print(f"最大单笔亏损:    ¥{trade_analysis['max_loss']:,.2f}")
            if trade_analysis['profit_factor'] > 0:
                print(f"盈亏比:          {trade_analysis['profit_factor']:.2f}")
        
        # 风险指标
        risk_metrics = self.calculate_risk_metrics()
        if risk_metrics:
            print("\n【风险指标】")
            print(f"年化波动率:      {risk_metrics['volatility']:.2%}")
            print(f"下行波动率:      {risk_metrics['downside_std']:.2%}")
            print(f"索提诺比率:      {risk_metrics['sortino_ratio']:.2f}")
            print(f"卡玛比率:        {risk_metrics['calmar_ratio']:.2f}")
            print(f"VaR(95%):        {risk_metrics['var_95']:.2%}")
            print(f"CVaR(95%):       {risk_metrics['cvar_95']:.2%}")
        
        # 年度收益
        yearly_returns = self.get_yearly_returns()
        if not yearly_returns.empty:
            print("\n【年度收益率】")
            for date, ret in yearly_returns.items():
                print(f"{date.year}年:          {ret:.2%}")
        
        print("\n" + "="*60)

    def calculate_metrics(self) -> Dict:
        """
        计算并返回一组常用的关键绩效指标
        
        Returns:
            Dict: 包含总收益率、夏普比率、最大回撤、胜率等指标
        """
        metrics = {
            '总收益率': self.results.get('total_return', 0.0),
            '年化收益率': self.results.get('annual_return', 0.0),
            '最大回撤': self.results.get('max_drawdown', 0.0),
            '夏普比率': self.results.get('sharpe_ratio', 0.0),
        }

        trade_analysis = self.get_trade_analysis()
        if trade_analysis:
            metrics['胜率'] = trade_analysis.get('win_rate', 0.0)
        else:
            metrics['胜率'] = 0.0

        return metrics


def compare_strategies(results_list: List[Dict], strategy_names: List[str]):
    """
    比较多个策略的性能
    
    Args:
        results_list: 多个策略的回测结果列表
        strategy_names: 策略名称列表
    """
    if len(results_list) != len(strategy_names):
        raise ValueError("结果数量和策略名称数量不匹配")
    
    print("\n" + "="*80)
    print("策略对比分析".center(80))
    print("="*80)
    
    # 创建对比表格
    comparison_data = []
    for results, name in zip(results_list, strategy_names):
        comparison_data.append({
            '策略': name,
            '总收益率': f"{results['total_return']:.2%}",
            '年化收益': f"{results['annual_return']:.2%}",
            '最大回撤': f"{results['max_drawdown']:.2%}",
            '夏普比率': f"{results['sharpe_ratio']:.2f}",
            '交易次数': results['total_trades']
        })
    
    df = pd.DataFrame(comparison_data)
    print("\n" + df.to_string(index=False))
    print("\n" + "="*80)


if __name__ == "__main__":
    print("性能分析模块已加载")

