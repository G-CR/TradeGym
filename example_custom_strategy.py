"""
自定义策略示例
演示如何创建自己的交易策略
"""

from strategies import BaseStrategy
from data_fetcher import DataFetcher
from backtest_engine import BacktestEngine
from performance_analyzer import PerformanceAnalyzer
from visualizer import Visualizer
from datetime import datetime, timedelta
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


class MyCustomStrategy(BaseStrategy):
    """
    自定义策略示例：均线+RSI组合策略
    
    买入条件：
    1. 短期均线上穿长期均线（金叉）
    2. RSI < 50（不在超买区）
    
    卖出条件：
    1. 短期均线下穿长期均线（死叉）
    或
    2. RSI > 70（超买）
    """
    
    def __init__(self, short_window: int = 10, long_window: int = 30, rsi_period: int = 14):
        """
        初始化策略
        
        Args:
            short_window: 短期均线周期
            long_window: 长期均线周期
            rsi_period: RSI周期
        """
        super().__init__(name="均线+RSI组合策略")
        self.short_window = short_window
        self.long_window = long_window
        self.rsi_period = rsi_period
        
    def _prepare_indicators(self):
        """计算技术指标"""
        # 计算均线
        self.data['ma_short'] = self.data['close'].rolling(window=self.short_window).mean()
        self.data['ma_long'] = self.data['close'].rolling(window=self.long_window).mean()
        
        # 前一天的均线
        self.data['ma_short_prev'] = self.data['ma_short'].shift(1)
        self.data['ma_long_prev'] = self.data['ma_long'].shift(1)
        
        # 计算RSI
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        
        rs = gain / loss
        self.data['rsi'] = 100 - (100 / (1 + rs))
        
        # 计算成交量均线（可选，用于确认）
        self.data['volume_ma'] = self.data['volume'].rolling(window=20).mean()
        
    def generate_signal(self, data: pd.DataFrame, index: int) -> int:
        """
        生成交易信号
        
        Returns:
            1: 买入
            0: 持有
            -1: 卖出
        """
        if index < self.long_window:
            return 0
        
        current = self.data.iloc[index]
        
        # 买入条件
        if (current['ma_short'] > current['ma_long'] and  # 金叉
            current['ma_short_prev'] <= current['ma_long_prev'] and
            current['rsi'] < 50):  # RSI不在超买区
            return 1
        
        # 卖出条件
        if ((current['ma_short'] < current['ma_long'] and  # 死叉
             current['ma_short_prev'] >= current['ma_long_prev']) or
            current['rsi'] > 70):  # 超买
            return -1
        
        return 0


class VolumeBreakoutStrategy(BaseStrategy):
    """
    成交量突破策略
    
    当价格创新高且成交量放大时买入
    当价格跌破支撑位时卖出
    """
    
    def __init__(self, lookback_period: int = 20, volume_multiplier: float = 1.5):
        super().__init__(name="成交量突破策略")
        self.lookback_period = lookback_period
        self.volume_multiplier = volume_multiplier
        
    def _prepare_indicators(self):
        # 计算最高价
        self.data['highest'] = self.data['high'].rolling(window=self.lookback_period).max()
        self.data['lowest'] = self.data['low'].rolling(window=self.lookback_period).min()
        
        # 成交量均线
        self.data['volume_ma'] = self.data['volume'].rolling(window=self.lookback_period).mean()
        
        # 前一天的值
        self.data['highest_prev'] = self.data['highest'].shift(1)
        
    def generate_signal(self, data: pd.DataFrame, index: int) -> int:
        if index < self.lookback_period:
            return 0
        
        current = self.data.iloc[index]
        
        # 买入：突破新高 + 成交量放大
        if (current['close'] > current['highest_prev'] and
            current['volume'] > current['volume_ma'] * self.volume_multiplier):
            return 1
        
        # 卖出：跌破最低价的10%
        if current['close'] < current['lowest'] * 1.1:
            return -1
        
        return 0


def test_custom_strategy():
    """测试自定义策略"""
    print("="*70)
    print("自定义策略回测示例".center(70))
    print("="*70)
    
    # 获取数据
    print("\n[1] 获取数据...")
    
    fetcher = DataFetcher()
    start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y%m%d')
    end_date = datetime.now().strftime('%Y%m%d')
    
    data = fetcher.get_stock_data(
        symbol='000001',
        start_date=start_date,
        end_date=end_date,
        adjust='qfq'
    )
    
    print(f"✓ 数据获取完成")
    
    # 测试策略1：均线+RSI组合
    print("\n[2] 测试策略1: 均线+RSI组合策略")
    print("-" * 70)
    
    strategy1 = MyCustomStrategy(short_window=10, long_window=30, rsi_period=14)
    
    engine1 = BacktestEngine(initial_cash=100000, commission_rate=0.0003)
    engine1.set_data(data)
    engine1.set_strategy(strategy1)
    
    results1 = engine1.run()
    
    analyzer1 = PerformanceAnalyzer(results1)
    analyzer1.print_summary()
    
    visualizer1 = Visualizer(results1, engine1.data)
    visualizer1.plot_equity_curve()
    visualizer1.plot_with_signals()
    
    # 测试策略2：成交量突破
    print("\n[3] 测试策略2: 成交量突破策略")
    print("-" * 70)
    
    strategy2 = VolumeBreakoutStrategy(lookback_period=20, volume_multiplier=1.5)
    
    engine2 = BacktestEngine(initial_cash=100000, commission_rate=0.0003)
    engine2.set_data(data)
    engine2.set_strategy(strategy2)
    
    results2 = engine2.run()
    
    analyzer2 = PerformanceAnalyzer(results2)
    analyzer2.print_summary()
    
    print("\n" + "="*70)
    print("自定义策略测试完成！".center(70))
    print("="*70)
    
    print("\n💡 提示：")
    print("  你可以参考这两个例子创建自己的策略")
    print("  只需要继承 BaseStrategy 类，实现以下两个方法：")
    print("    1. _prepare_indicators() - 计算技术指标")
    print("    2. generate_signal() - 生成交易信号")


def main():
    """主函数"""
    print("\n欢迎使用自定义策略示例！\n")
    print("这个示例将演示如何创建和测试你自己的交易策略\n")
    
    test_custom_strategy()
    
    print("\n\n" + "="*70)
    print("创建自己策略的步骤".center(70))
    print("="*70)
    print("""
1. 继承 BaseStrategy 类
2. 在 __init__ 中定义策略参数
3. 在 _prepare_indicators 中计算技术指标
4. 在 generate_signal 中实现交易逻辑
   - 返回 1 表示买入信号
   - 返回 -1 表示卖出信号  
   - 返回 0 表示持有/观望

常用的技术指标：
  - 移动平均线 (MA)
  - RSI (相对强弱指标)
  - MACD
  - 布林带
  - KDJ
  - 成交量指标
  - ATR (真实波动幅度)

你可以组合多个指标来设计更复杂的策略！
    """)


if __name__ == "__main__":
    main()

