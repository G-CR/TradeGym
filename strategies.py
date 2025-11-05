"""
交易策略模块
包含多个经典量化策略
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional


class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str = "BaseStrategy"):
        self.name = name
        self.data: Optional[pd.DataFrame] = None
        
    def init(self, data: pd.DataFrame):
        """
        初始化策略
        
        Args:
            data: 历史数据
        """
        self.data = data.copy()
        self._prepare_indicators()
    
    @abstractmethod
    def _prepare_indicators(self):
        """准备技术指标（子类实现）"""
        pass
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame, index: int) -> int:
        """
        生成交易信号
        
        Args:
            data: 当前可见的历史数据
            index: 当前数据索引
            
        Returns:
            1: 买入信号
            0: 持有/观望
            -1: 卖出信号
        """
        pass


class DoubleMAStrategy(BaseStrategy):
    """双均线策略"""
    
    def __init__(self, short_window: int = 5, long_window: int = 20):
        """
        初始化双均线策略
        
        Args:
            short_window: 短期均线窗口
            long_window: 长期均线窗口
        """
        super().__init__(name="双均线策略")
        self.short_window = short_window
        self.long_window = long_window
        
    def _prepare_indicators(self):
        """计算均线"""
        self.data['ma_short'] = self.data['close'].rolling(window=self.short_window).mean()
        self.data['ma_long'] = self.data['close'].rolling(window=self.long_window).mean()
        
        # 计算前一天的均线（用于判断交叉）
        self.data['ma_short_prev'] = self.data['ma_short'].shift(1)
        self.data['ma_long_prev'] = self.data['ma_long'].shift(1)
    
    def generate_signal(self, data: pd.DataFrame, index: int) -> int:
        """
        生成信号
        策略逻辑：短期均线上穿长期均线买入，下穿卖出
        """
        if index < self.long_window:
            return 0
        
        # 使用self.data而不是传入的data，因为指标是在self.data上计算的
        current = self.data.iloc[index]
        
        # 金叉：短期均线上穿长期均线
        if (current['ma_short'] > current['ma_long'] and 
            current['ma_short_prev'] <= current['ma_long_prev']):
            return 1
        
        # 死叉：短期均线下穿长期均线
        if (current['ma_short'] < current['ma_long'] and 
            current['ma_short_prev'] >= current['ma_long_prev']):
            return -1
        
        return 0


class MACDStrategy(BaseStrategy):
    """MACD策略"""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        """
        初始化MACD策略
        
        Args:
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
        """
        super().__init__(name="MACD策略")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        
    def _prepare_indicators(self):
        """计算MACD指标"""
        # 计算EMA
        exp1 = self.data['close'].ewm(span=self.fast_period, adjust=False).mean()
        exp2 = self.data['close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # MACD线
        self.data['macd'] = exp1 - exp2
        
        # 信号线
        self.data['signal'] = self.data['macd'].ewm(span=self.signal_period, adjust=False).mean()
        
        # MACD柱
        self.data['hist'] = self.data['macd'] - self.data['signal']
        
        # 前一天的值（用于判断交叉）
        self.data['macd_prev'] = self.data['macd'].shift(1)
        self.data['signal_prev'] = self.data['signal'].shift(1)
        self.data['hist_prev'] = self.data['hist'].shift(1)
    
    def generate_signal(self, data: pd.DataFrame, index: int) -> int:
        """
        生成信号
        策略逻辑：
        1. MACD上穿信号线且MACD柱由负转正，买入
        2. MACD下穿信号线，卖出
        """
        if index < self.slow_period + self.signal_period:
            return 0
        
        current = self.data.iloc[index]
        
        # 金叉：MACD上穿信号线
        if (current['macd'] > current['signal'] and 
            current['macd_prev'] <= current['signal_prev'] and
            current['hist'] > 0):
            return 1
        
        # 死叉：MACD下穿信号线
        if (current['macd'] < current['signal'] and 
            current['macd_prev'] >= current['signal_prev']):
            return -1
        
        return 0


class TurtleStrategy(BaseStrategy):
    """海龟交易策略（简化版）"""
    
    def __init__(self, entry_window: int = 20, exit_window: int = 10, atr_period: int = 20):
        """
        初始化海龟交易策略
        
        Args:
            entry_window: 入场突破周期（默认20日）
            exit_window: 出场周期（默认10日）
            atr_period: ATR周期
        """
        super().__init__(name="海龟交易策略")
        self.entry_window = entry_window
        self.exit_window = exit_window
        self.atr_period = atr_period
        
    def _prepare_indicators(self):
        """计算指标"""
        # 唐奇安通道（入场）
        self.data['upper_band'] = self.data['high'].rolling(window=self.entry_window).max()
        self.data['lower_band'] = self.data['low'].rolling(window=self.entry_window).min()
        
        # 出场通道
        self.data['exit_upper'] = self.data['high'].rolling(window=self.exit_window).max()
        self.data['exit_lower'] = self.data['low'].rolling(window=self.exit_window).min()
        
        # ATR（真实波动幅度均值）
        self.data['tr1'] = self.data['high'] - self.data['low']
        self.data['tr2'] = abs(self.data['high'] - self.data['close'].shift(1))
        self.data['tr3'] = abs(self.data['low'] - self.data['close'].shift(1))
        self.data['tr'] = self.data[['tr1', 'tr2', 'tr3']].max(axis=1)
        self.data['atr'] = self.data['tr'].rolling(window=self.atr_period).mean()
        
        # 前一天的通道值
        self.data['upper_band_prev'] = self.data['upper_band'].shift(1)
        self.data['lower_band_prev'] = self.data['lower_band'].shift(1)
        self.data['exit_lower_prev'] = self.data['exit_lower'].shift(1)
        
    def generate_signal(self, data: pd.DataFrame, index: int) -> int:
        """
        生成信号
        策略逻辑：
        1. 价格突破20日最高价，买入
        2. 价格跌破10日最低价，卖出
        """
        if index < self.entry_window:
            return 0
        
        current = self.data.iloc[index]
        prev = self.data.iloc[index - 1] if index > 0 else None
        
        if prev is None:
            return 0
        
        # 突破上轨，买入信号
        if (current['close'] > current['upper_band_prev'] and 
            prev['close'] <= prev['upper_band_prev']):
            return 1
        
        # 跌破出场下轨，卖出信号
        if (current['close'] < current['exit_lower_prev'] and 
            prev['close'] >= prev['exit_lower_prev']):
            return -1
        
        return 0


class RSIStrategy(BaseStrategy):
    """RSI超买超卖策略"""
    
    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        """
        初始化RSI策略
        
        Args:
            period: RSI周期
            oversold: 超卖阈值
            overbought: 超买阈值
        """
        super().__init__(name="RSI策略")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        
    def _prepare_indicators(self):
        """计算RSI"""
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss
        self.data['rsi'] = 100 - (100 / (1 + rs))
        self.data['rsi_prev'] = self.data['rsi'].shift(1)
        
    def generate_signal(self, data: pd.DataFrame, index: int) -> int:
        """
        生成信号
        策略逻辑：
        1. RSI从超卖区向上突破，买入
        2. RSI从超买区向下突破，卖出
        """
        if index < self.period + 1:
            return 0
        
        current = self.data.iloc[index]
        
        # RSI从超卖区向上
        if current['rsi'] > self.oversold and current['rsi_prev'] <= self.oversold:
            return 1
        
        # RSI从超买区向下
        if current['rsi'] < self.overbought and current['rsi_prev'] >= self.overbought:
            return -1
        
        return 0


class BollingerBandsStrategy(BaseStrategy):
    """布林带策略"""
    
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        """
        初始化布林带策略
        
        Args:
            period: 移动平均周期
            std_dev: 标准差倍数
        """
        super().__init__(name="布林带策略")
        self.period = period
        self.std_dev = std_dev
        
    def _prepare_indicators(self):
        """计算布林带"""
        self.data['middle_band'] = self.data['close'].rolling(window=self.period).mean()
        rolling_std = self.data['close'].rolling(window=self.period).std()
        
        self.data['upper_band'] = self.data['middle_band'] + (rolling_std * self.std_dev)
        self.data['lower_band'] = self.data['middle_band'] - (rolling_std * self.std_dev)
        
        # 带宽
        self.data['bb_width'] = (self.data['upper_band'] - self.data['lower_band']) / self.data['middle_band']
        
        # 价格位置
        self.data['bb_position'] = (self.data['close'] - self.data['lower_band']) / (self.data['upper_band'] - self.data['lower_band'])
        
    def generate_signal(self, data: pd.DataFrame, index: int) -> int:
        """
        生成信号
        策略逻辑：
        1. 价格触及下轨，买入
        2. 价格触及上轨，卖出
        """
        if index < self.period:
            return 0
        
        current = self.data.iloc[index]
        prev = self.data.iloc[index - 1] if index > 0 else None
        
        if prev is None:
            return 0
        
        # 价格向上突破下轨
        if current['close'] > current['lower_band'] and prev['close'] <= prev['lower_band']:
            return 1
        
        # 价格触及或突破上轨
        if current['close'] >= current['upper_band']:
            return -1
        
        return 0


if __name__ == "__main__":
    print("策略模块已加载")
    print("\n可用策略:")
    print("1. DoubleMAStrategy - 双均线策略")
    print("2. MACDStrategy - MACD策略")
    print("3. TurtleStrategy - 海龟交易策略")
    print("4. RSIStrategy - RSI超买超卖策略")
    print("5. BollingerBandsStrategy - 布林带策略")

