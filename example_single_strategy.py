"""
单策略回测示例
演示如何运行单个策略的完整回测流程
"""

from data_fetcher import DataFetcher
from backtest_engine import BacktestEngine
from strategies import DoubleMAStrategy, MACDStrategy, TurtleStrategy, RSIStrategy, BollingerBandsStrategy
from performance_analyzer import PerformanceAnalyzer
from visualizer import Visualizer
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


def run_single_strategy_backtest(
    stock_code: str = '000001',  # 平安银行
    strategy_name: str = 'double_ma',  # 策略类型
    start_date: str = None,
    end_date: str = None,
    initial_cash: float = 100000
):
    """
    运行单策略回测
    
    Args:
        stock_code: 股票代码
        strategy_name: 策略名称 ('double_ma', 'macd', 'turtle', 'rsi', 'bollinger')
        start_date: 开始日期
        end_date: 结束日期
        initial_cash: 初始资金
    """
    print("="*70)
    print("量化交易回测系统 - 单策略回测".center(70))
    print("="*70)
    
    # 1. 获取数据
    print("\n[步骤 1/5] 获取历史数据...")
    
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
    
    print(f"✓ 成功获取 {len(data)} 天的数据")
    print(f"  日期范围: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}")
    
    # 2. 选择策略
    print(f"\n[步骤 2/5] 初始化策略: {strategy_name}")
    
    strategies_map = {
        'double_ma': DoubleMAStrategy(short_window=5, long_window=20),
        'macd': MACDStrategy(fast_period=12, slow_period=26, signal_period=9),
        'turtle': TurtleStrategy(entry_window=20, exit_window=10),
        'rsi': RSIStrategy(period=14, oversold=30, overbought=70),
        'bollinger': BollingerBandsStrategy(period=20, std_dev=2.0)
    }
    
    if strategy_name not in strategies_map:
        raise ValueError(f"未知策略: {strategy_name}. 可选: {list(strategies_map.keys())}")
    
    strategy = strategies_map[strategy_name]
    print(f"✓ 策略已加载: {strategy.name}")
    
    # 3. 运行回测
    print(f"\n[步骤 3/5] 运行回测...")
    print(f"  初始资金: ¥{initial_cash:,.2f}")
    
    engine = BacktestEngine(initial_cash=initial_cash, commission_rate=0.0003)
    engine.set_data(data)
    engine.set_strategy(strategy)
    
    results = engine.run()
    
    print(f"✓ 回测完成")
    
    # 4. 性能分析
    print(f"\n[步骤 4/5] 性能分析")
    
    analyzer = PerformanceAnalyzer(results)
    analyzer.print_summary()
    analyzer.print_detailed_analysis()
    
    # 5. 可视化
    print(f"\n[步骤 5/5] 生成可视化图表...")
    
    visualizer = Visualizer(results, engine.data)
    visualizer.plot_all(output_dir='./outputs')
    
    print("\n" + "="*70)
    print("回测完成！".center(70))
    print("="*70)
    
    return results


def main():
    """主函数"""
    print("\n欢迎使用量化交易回测系统！\n")
    
    # 示例：运行双均线策略
    print("示例1: 双均线策略回测")
    print("-" * 70)
    
    results = run_single_strategy_backtest(
        stock_code='000001',      # 平安银行
        strategy_name='double_ma',  # 双均线策略
        initial_cash=100000
    )
    
    # 你可以取消注释下面的代码来测试其他策略
    """
    print("\n\n示例2: MACD策略回测")
    print("-" * 70)
    
    results = run_single_strategy_backtest(
        stock_code='600519',      # 贵州茅台
        strategy_name='macd',
        initial_cash=100000
    )
    """
    
    """
    print("\n\n示例3: 海龟交易策略回测")
    print("-" * 70)
    
    results = run_single_strategy_backtest(
        stock_code='000858',      # 五粮液
        strategy_name='turtle',
        initial_cash=100000
    )
    """


if __name__ == "__main__":
    main()

