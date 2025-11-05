"""
多策略对比示例
演示如何对比不同策略的表现
"""

from data_fetcher import DataFetcher
from backtest_engine import BacktestEngine
from strategies import DoubleMAStrategy, MACDStrategy, TurtleStrategy, RSIStrategy, BollingerBandsStrategy
from performance_analyzer import compare_strategies
from visualizer import compare_strategies_plot
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


def compare_all_strategies(
    stock_code: str = '000001',
    start_date: str = None,
    end_date: str = None,
    initial_cash: float = 100000
):
    """
    对比所有策略
    
    Args:
        stock_code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        initial_cash: 初始资金
    """
    print("="*80)
    print("量化交易回测系统 - 多策略对比".center(80))
    print("="*80)
    
    # 1. 获取数据
    print("\n[1] 获取历史数据...")
    
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y%m%d')
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')
    
    fetcher = DataFetcher()
    data = fetcher.get_stock_data(
        symbol=stock_code,
        start_date=start_date,
        end_date=end_date,
        adjust='qfq'
    )
    
    print(f"✓ 数据获取完成: {len(data)} 天")
    
    # 2. 定义要测试的策略
    strategies = {
        '双均线策略': DoubleMAStrategy(short_window=5, long_window=20),
        'MACD策略': MACDStrategy(fast_period=12, slow_period=26, signal_period=9),
        '海龟策略': TurtleStrategy(entry_window=20, exit_window=10),
        'RSI策略': RSIStrategy(period=14, oversold=30, overbought=70),
        '布林带策略': BollingerBandsStrategy(period=20, std_dev=2.0)
    }
    
    # 3. 运行所有策略
    print(f"\n[2] 运行 {len(strategies)} 个策略的回测...")
    
    all_results = {}
    
    for strategy_name, strategy in strategies.items():
        print(f"\n  正在测试: {strategy_name}...", end=' ')
        
        engine = BacktestEngine(initial_cash=initial_cash, commission_rate=0.0003)
        engine.set_data(data)
        engine.set_strategy(strategy)
        
        results = engine.run()
        all_results[strategy_name] = results
        
        print(f"✓ 完成 (收益: {results['total_return']:.2%})")
    
    # 4. 对比分析
    print(f"\n[3] 策略对比分析")
    
    compare_strategies(
        results_list=list(all_results.values()),
        strategy_names=list(all_results.keys())
    )
    
    # 5. 可视化对比
    print(f"\n[4] 生成对比图表...")
    
    compare_strategies_plot(all_results)
    
    # 6. 找出最佳策略
    print("\n[5] 最佳策略排名")
    print("-" * 80)
    
    # 按总收益率排序
    sorted_by_return = sorted(all_results.items(), 
                              key=lambda x: x[1]['total_return'], 
                              reverse=True)
    
    print("\n按总收益率排名:")
    for i, (name, results) in enumerate(sorted_by_return, 1):
        print(f"  {i}. {name:15s} - 收益: {results['total_return']:>7.2%}, "
              f"最大回撤: {results['max_drawdown']:>7.2%}, "
              f"夏普: {results['sharpe_ratio']:>5.2f}")
    
    # 按夏普比率排序
    sorted_by_sharpe = sorted(all_results.items(), 
                               key=lambda x: x[1]['sharpe_ratio'], 
                               reverse=True)
    
    print("\n按夏普比率排名:")
    for i, (name, results) in enumerate(sorted_by_sharpe, 1):
        print(f"  {i}. {name:15s} - 夏普: {results['sharpe_ratio']:>5.2f}, "
              f"收益: {results['total_return']:>7.2%}, "
              f"最大回撤: {results['max_drawdown']:>7.2%}")
    
    # 按风险调整收益（收益/最大回撤）排序
    sorted_by_risk_adjusted = sorted(all_results.items(), 
                                     key=lambda x: abs(x[1]['total_return'] / x[1]['max_drawdown']) 
                                                   if x[1]['max_drawdown'] != 0 else 0, 
                                     reverse=True)
    
    print("\n按风险调整收益排名:")
    for i, (name, results) in enumerate(sorted_by_risk_adjusted, 1):
        ratio = abs(results['total_return'] / results['max_drawdown']) if results['max_drawdown'] != 0 else 0
        print(f"  {i}. {name:15s} - 比率: {ratio:>5.2f}, "
              f"收益: {results['total_return']:>7.2%}, "
              f"最大回撤: {results['max_drawdown']:>7.2%}")
    
    print("\n" + "="*80)
    print("对比分析完成！".center(80))
    print("="*80)
    
    return all_results


def main():
    """主函数"""
    print("\n欢迎使用多策略对比系统！\n")
    
    # 对比所有策略在平安银行上的表现
    results = compare_all_strategies(
        stock_code='000001',  # 平安银行
        initial_cash=100000
    )
    
    # 你也可以测试其他股票
    """
    # 测试贵州茅台
    results = compare_all_strategies(
        stock_code='600519',  # 贵州茅台
        initial_cash=100000
    )
    """


if __name__ == "__main__":
    main()

