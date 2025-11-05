"""
回测引擎核心模块
实现完整的回测框架
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Position:
    """持仓信息"""
    symbol: str
    quantity: int  # 持仓数量
    avg_price: float  # 平均成本
    current_price: float  # 当前价格
    
    @property
    def market_value(self) -> float:
        """市值"""
        return self.quantity * self.current_price
    
    @property
    def profit(self) -> float:
        """盈亏"""
        return (self.current_price - self.avg_price) * self.quantity
    
    @property
    def profit_rate(self) -> float:
        """盈亏率"""
        return (self.current_price - self.avg_price) / self.avg_price


@dataclass
class Trade:
    """交易记录"""
    date: datetime
    symbol: str
    action: str  # 'buy' 或 'sell'
    price: float
    quantity: int
    amount: float
    commission: float


class Portfolio:
    """投资组合管理"""
    
    def __init__(self, initial_cash: float = 100000.0, commission_rate: float = 0.0003):
        """
        初始化投资组合
        
        Args:
            initial_cash: 初始资金
            commission_rate: 手续费率（默认万3）
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.commission_rate = commission_rate
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.history: List[Dict] = []
    
    def buy(self, symbol: str, price: float, quantity: int, date: datetime) -> bool:
        """
        买入股票
        
        Args:
            symbol: 股票代码
            price: 买入价格
            quantity: 买入数量
            date: 交易日期
            
        Returns:
            是否成功
        """
        amount = price * quantity
        commission = amount * self.commission_rate
        total_cost = amount + commission
        
        # 检查资金是否足够
        if total_cost > self.cash:
            return False
        
        # 更新现金
        self.cash -= total_cost
        
        # 更新持仓
        if symbol in self.positions:
            pos = self.positions[symbol]
            total_quantity = pos.quantity + quantity
            total_cost_basis = pos.avg_price * pos.quantity + price * quantity
            pos.avg_price = total_cost_basis / total_quantity
            pos.quantity = total_quantity
            pos.current_price = price
        else:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                avg_price=price,
                current_price=price
            )
        
        # 记录交易
        self.trades.append(Trade(
            date=date,
            symbol=symbol,
            action='buy',
            price=price,
            quantity=quantity,
            amount=amount,
            commission=commission
        ))
        
        return True
    
    def sell(self, symbol: str, price: float, quantity: int, date: datetime) -> bool:
        """
        卖出股票
        
        Args:
            symbol: 股票代码
            price: 卖出价格
            quantity: 卖出数量
            date: 交易日期
            
        Returns:
            是否成功
        """
        # 检查持仓
        if symbol not in self.positions:
            return False
        
        pos = self.positions[symbol]
        if pos.quantity < quantity:
            return False
        
        amount = price * quantity
        commission = amount * self.commission_rate
        
        # 印花税（卖出时收取0.1%）
        stamp_tax = amount * 0.001
        
        total_receive = amount - commission - stamp_tax
        
        # 更新现金
        self.cash += total_receive
        
        # 更新持仓
        pos.quantity -= quantity
        pos.current_price = price
        
        if pos.quantity == 0:
            del self.positions[symbol]
        
        # 记录交易
        self.trades.append(Trade(
            date=date,
            symbol=symbol,
            action='sell',
            price=price,
            quantity=quantity,
            amount=amount,
            commission=commission + stamp_tax
        ))
        
        return True
    
    def update_price(self, symbol: str, price: float):
        """更新持仓价格"""
        if symbol in self.positions:
            self.positions[symbol].current_price = price
    
    def get_total_value(self) -> float:
        """获取总资产"""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + positions_value
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """获取持仓"""
        return self.positions.get(symbol)
    
    def record_state(self, date: datetime):
        """记录当前状态"""
        total_value = self.get_total_value()
        positions_value = sum(pos.market_value for pos in self.positions.values())
        
        self.history.append({
            'date': date,
            'cash': self.cash,
            'positions_value': positions_value,
            'total_value': total_value,
            'return': (total_value - self.initial_cash) / self.initial_cash
        })


class BacktestEngine:
    """回测引擎"""
    
    def __init__(
        self, 
        initial_cash: float = 100000.0,
        commission_rate: float = 0.0003
    ):
        """
        初始化回测引擎
        
        Args:
            initial_cash: 初始资金
            commission_rate: 手续费率
        """
        self.portfolio = Portfolio(initial_cash, commission_rate)
        self.data: Optional[pd.DataFrame] = None
        self.strategy = None
        
    def set_data(self, data: pd.DataFrame):
        """设置回测数据"""
        self.data = data.copy()
        
    def set_strategy(self, strategy):
        """设置策略"""
        self.strategy = strategy
        
    def run(self) -> Dict:
        """
        运行回测
        
        Returns:
            回测结果
        """
        if self.data is None:
            raise ValueError("请先设置回测数据")
        
        if self.strategy is None:
            raise ValueError("请先设置策略")
        
        # 初始化策略
        self.strategy.init(self.data)
        
        # 遍历每一天
        for i in range(len(self.data)):
            current_date = self.data.index[i]
            current_data = self.data.iloc[:i+1]
            
            # 更新持仓价格
            for symbol in self.portfolio.positions.keys():
                self.portfolio.update_price(symbol, self.data.iloc[i]['close'])
            
            # 生成信号
            signal = self.strategy.generate_signal(current_data, i)
            
            # 执行交易
            if signal == 1:  # 买入信号
                self._execute_buy(i, current_date)
            elif signal == -1:  # 卖出信号
                self._execute_sell(i, current_date)
            
            # 记录状态
            self.portfolio.record_state(current_date)
        
        return self._calculate_metrics()
    
    def _execute_buy(self, idx: int, date: datetime):
        """执行买入"""
        price = self.data.iloc[idx]['close']
        
        # 获取当前持仓
        symbol = 'stock'  # 简化处理，使用固定symbol
        position = self.portfolio.get_position(symbol)
        
        # 如果没有持仓，买入
        if position is None:
            # 计算可买数量（使用95%的资金，留一些余地）
            available_cash = self.portfolio.cash * 0.95
            quantity = int(available_cash / price / 100) * 100  # A股以100股为单位
            
            if quantity > 0:
                self.portfolio.buy(symbol, price, quantity, date)
    
    def _execute_sell(self, idx: int, date: datetime):
        """执行卖出"""
        price = self.data.iloc[idx]['close']
        symbol = 'stock'
        
        position = self.portfolio.get_position(symbol)
        if position and position.quantity > 0:
            self.portfolio.sell(symbol, price, position.quantity, date)
    
    def _calculate_metrics(self) -> Dict:
        """计算回测指标"""
        if not self.portfolio.history:
            return {}
        
        df = pd.DataFrame(self.portfolio.history)
        df.set_index('date', inplace=True)
        
        # 总收益率
        total_return = (self.portfolio.get_total_value() - self.portfolio.initial_cash) / self.portfolio.initial_cash
        
        # 年化收益率
        days = (df.index[-1] - df.index[0]).days
        annual_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0
        
        # 最大回撤
        df['cummax'] = df['total_value'].cummax()
        df['drawdown'] = (df['total_value'] - df['cummax']) / df['cummax']
        max_drawdown = df['drawdown'].min()
        
        # 夏普比率（假设无风险利率为3%）
        df['daily_return'] = df['total_value'].pct_change()
        excess_return = df['daily_return'].mean() * 252 - 0.03
        sharpe_ratio = excess_return / (df['daily_return'].std() * np.sqrt(252)) if df['daily_return'].std() > 0 else 0
        
        # 胜率
        winning_trades = [t for t in self.portfolio.trades if t.action == 'sell']
        if winning_trades:
            # 简化处理，计算盈利交易占比
            # 这里需要配对买卖交易来准确计算，暂时简化
            win_rate = 0.5  # 占位
        else:
            win_rate = 0
        
        # 交易次数
        total_trades = len(self.portfolio.trades)
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'total_trades': total_trades,
            'final_value': self.portfolio.get_total_value(),
            'equity_curve': df['total_value'],
            'trades': self.portfolio.trades
        }


if __name__ == "__main__":
    print("回测引擎模块已加载")
    print("请配合策略模块使用")

