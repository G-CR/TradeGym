"""
策略管理器使用示例
演示如何使用 StrategyManager 来选择和使用不同的策略
"""

from data_fetcher import DataFetcher
from backtest_engine import BacktestEngine
from performance_analyzer import PerformanceAnalyzer
from visualizer import Visualizer
from strategy_manager import StrategyManager


def main():
    print("="*70)
    print("📊 策略管理器使用示例")
    print("="*70 + "\n")
    
    # 1. 创建策略管理器
    manager = StrategyManager()
    
    # 2. 查看所有可用策略
    print("步骤 1: 查看所有可用策略\n")
    available_strategies = manager.list_strategies(detailed=True)
    
    # 3. 获取数据
    print("="*70)
    print("步骤 2: 获取股票数据")
    print("="*70 + "\n")
    
    fetcher = DataFetcher()
    data = fetcher.get_stock_data(
        symbol='000001',      # 平安银行
        start_date='20230101',
        end_date='20241101',
        adjust='qfq'
    )
    print(f"✓ 成功获取数据，共 {len(data)} 条记录\n")
    
    # 4. 使用策略管理器创建策略并回测
    print("="*70)
    print("步骤 3: 使用策略管理器创建和测试策略")
    print("="*70 + "\n")
    
    # 示例1: 使用默认参数创建双均线策略
    print("【示例 1】使用默认参数创建双均线策略")
    print("-" * 70)
    strategy1 = manager.get_strategy('double_ma')
    print(f"✓ 创建策略: {strategy1.name}")
    
    # 运行回测
    engine = BacktestEngine(initial_cash=100000, commission_rate=0.0003)
    engine.set_data(data)
    engine.set_strategy(strategy1)
    results1 = engine.run()
    
    # 分析结果
    analyzer1 = PerformanceAnalyzer(results1)
    print("\n回测结果:")
    analyzer1.print_summary()
    print()
    
    # 示例2: 使用自定义参数创建MACD策略
    print("\n" + "="*70)
    print("【示例 2】使用自定义参数创建MACD策略")
    print("-" * 70)
    strategy2 = manager.get_strategy('macd', fast_period=10, slow_period=20, signal_period=5)
    print(f"✓ 创建策略: {strategy2.name}")
    print(f"  参数: fast_period=10, slow_period=20, signal_period=5")
    
    engine.set_strategy(strategy2)
    results2 = engine.run()
    
    analyzer2 = PerformanceAnalyzer(results2)
    print("\n回测结果:")
    analyzer2.print_summary()
    print()
    
    # 示例3: 获取策略信息
    print("\n" + "="*70)
    print("【示例 3】获取策略详细信息")
    print("-" * 70)
    rsi_info = manager.get_strategy_info('rsi')
    print(f"策略名称: {rsi_info['name']}")
    print(f"描述: {rsi_info['description']}")
    print(f"适合场景: {rsi_info['适合场景']}")
    print(f"默认参数: {rsi_info['default_params']}")
    print()
    
    # 示例4: 批量测试所有策略
    print("\n" + "="*70)
    print("【示例 4】批量测试所有策略（使用默认参数）")
    print("="*70 + "\n")
    
    all_strategies = manager.get_all_strategies()
    results_summary = []
    
    for strategy_name, strategy in all_strategies.items():
        print(f"正在测试: {strategy.name}...", end=" ")
        
        engine.set_strategy(strategy)
        results = engine.run()
        analyzer = PerformanceAnalyzer(results)
        
        # 收集关键指标
        metrics = analyzer.calculate_metrics()
        results_summary.append({
            'strategy_name': strategy.name,
            'total_return': metrics['总收益率'],
            'sharpe_ratio': metrics['夏普比率'],
            'max_drawdown': metrics['最大回撤'],
            'win_rate': metrics['胜率']
        })
        
        print("✓")
    
    # 显示对比结果
    print("\n" + "="*70)
    print("策略对比结果")
    print("="*70)
    print(f"{'策略名称':<15} {'总收益率':<12} {'夏普比率':<12} {'最大回撤':<12} {'胜率':<10}")
    print("-" * 70)
    
    for result in sorted(results_summary, key=lambda x: x['total_return'], reverse=True):
        print(f"{result['strategy_name']:<15} "
              f"{result['total_return']:>10.2%}  "
              f"{result['sharpe_ratio']:>10.2f}  "
              f"{result['max_drawdown']:>10.2%}  "
              f"{result['win_rate']:>10.2%}")
    
    print("\n" + "="*70)
    print("✅ 所有示例完成！")
    print("="*70)
    
    # 提示：如何使用可视化
    print("\n💡 提示:")
    print("   你可以使用 Visualizer 来可视化任何策略的回测结果:")
    print("   visualizer = Visualizer(results, data)")
    print("   visualizer.plot_equity_curve()")
    print("   visualizer.plot_with_signals()")


if __name__ == "__main__":
    main()
