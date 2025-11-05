"""
快速入门脚本
最简单的使用示例，适合第一次运行
"""

print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           📈 量化交易入门项目 - 快速开始                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

欢迎！这是一个为初学者设计的量化交易回测框架。

让我们开始你的第一次回测吧！
""")

import warnings
warnings.filterwarnings('ignore')

print("正在导入模块...\n")

try:
    from data_fetcher import DataFetcher
    from backtest_engine import BacktestEngine
    from strategies import DoubleMAStrategy
    from performance_analyzer import PerformanceAnalyzer
    from visualizer import Visualizer
    from datetime import datetime, timedelta
    
    print("✓ 模块导入成功！\n")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("\n请先安装依赖：")
    print("  pip install -r requirements.txt")
    exit(1)

# 开始回测
print("="*70)
print("第一次量化回测体验".center(70))
print("="*70)

try:
    # 步骤1: 获取数据
    print("\n[步骤 1/5] 📊 获取股票数据...")
    print("  股票: 000001 (平安银行)")
    print("  时间范围: 最近1年")
    
    fetcher = DataFetcher()
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    
    data = fetcher.get_stock_data(
        symbol='000001',
        start_date=start_date,
        end_date=end_date,
        adjust='qfq'
    )
    
    print(f"  ✓ 获取到 {len(data)} 天的数据")
    
    # 步骤2: 选择策略
    print("\n[步骤 2/5] 🎯 选择交易策略...")
    print("  策略: 双均线策略")
    print("  说明: 短期均线(5日)上穿长期均线(20日)时买入")
    print("       短期均线下穿长期均线时卖出")
    
    strategy = DoubleMAStrategy(short_window=5, long_window=20)
    print(f"  ✓ 策略已加载")
    
    # 步骤3: 初始化回测引擎
    print("\n[步骤 3/5] ⚙️  初始化回测引擎...")
    print("  初始资金: ¥100,000")
    print("  手续费率: 0.03%")
    
    engine = BacktestEngine(initial_cash=100000, commission_rate=0.0003)
    engine.set_data(data)
    engine.set_strategy(strategy)
    
    print("  ✓ 回测引擎已就绪")
    
    # 步骤4: 运行回测
    print("\n[步骤 4/5] 🚀 运行回测...")
    print("  正在模拟交易...")
    
    results = engine.run()
    
    print("  ✓ 回测完成！")
    
    # 步骤5: 查看结果
    print("\n[步骤 5/5] 📊 分析结果...")
    
    analyzer = PerformanceAnalyzer(results)
    analyzer.print_summary()
    
    # 可视化
    print("\n正在生成图表...")
    visualizer = Visualizer(results, engine.data)
    
    print("\n【图表1】资金曲线")
    visualizer.plot_equity_curve()
    
    print("\n【图表2】交易信号")
    visualizer.plot_with_signals()
    
    print("\n" + "="*70)
    print("🎉 恭喜！你已经完成了第一次量化回测！".center(70))
    print("="*70)
    
    print("""
下一步你可以：

1️⃣  尝试其他策略
   运行: python example_single_strategy.py

2️⃣  对比多个策略的表现
   运行: python example_compare_strategies.py

3️⃣  创建自己的策略
   运行: python example_custom_strategy.py

4️⃣  阅读 README.md 了解更多

💡 提示：
   - 回测好不代表实盘一定赚钱
   - 注意风险控制，不要用输不起的钱
   - 持续学习，保持谨慎

祝你在量化交易的学习之路上收获满满！ 📈
    """)

except Exception as e:
    print(f"\n❌ 出错了: {str(e)}")
    print("\n可能的原因:")
    print("  1. 网络连接问题（无法获取数据）")
    print("  2. 依赖包没有正确安装")
    print("  3. 数据源暂时不可用")
    print("\n建议:")
    print("  - 检查网络连接")
    print("  - 重新运行 pip install -r requirements.txt")
    print("  - 查看完整错误信息")

