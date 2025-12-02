"""
策略管理器模块
提供统一的策略选择和实例化接口
"""

from typing import Dict, Type, Optional, List, Any
from strategies import (
    BaseStrategy,
    DoubleMAStrategy,
    MACDStrategy,
    TurtleStrategy,
    RSIStrategy,
    BollingerBandsStrategy
)


class StrategyManager:
    """策略管理器 - 统一管理所有交易策略"""
    
    # 策略注册表：映射策略名称到策略类
    _STRATEGY_REGISTRY: Dict[str, Type[BaseStrategy]] = {
        'double_ma': DoubleMAStrategy,
        'macd': MACDStrategy,
        'turtle': TurtleStrategy,
        'rsi': RSIStrategy,
        'bollinger': BollingerBandsStrategy,
    }
    
    # 策略信息：包含描述和默认参数
    _STRATEGY_INFO: Dict[str, Dict[str, Any]] = {
        'double_ma': {
            'name': '双均线策略',
            'description': '短期均线上穿长期均线买入，下穿卖出',
            '适合场景': '趋势明显的市场',
            'default_params': {
                'short_window': 5,
                'long_window': 20
            }
        },
        'macd': {
            'name': 'MACD策略',
            'description': 'MACD线和信号线的交叉',
            '适合场景': '中长期趋势跟踪',
            'default_params': {
                'fast_period': 12,
                'slow_period': 26,
                'signal_period': 9
            }
        },
        'turtle': {
            'name': '海龟交易策略',
            'description': '唐奇安通道突破系统',
            '适合场景': '趋势跟踪',
            'default_params': {
                'entry_window': 20,
                'exit_window': 10,
                'atr_period': 20
            }
        },
        'rsi': {
            'name': 'RSI策略',
            'description': '相对强弱指标超买超卖',
            '适合场景': '震荡市场',
            'default_params': {
                'period': 14,
                'oversold': 30,
                'overbought': 70
            }
        },
        'bollinger': {
            'name': '布林带策略',
            'description': '价格触及上下轨时交易',
            '适合场景': '均值回归策略',
            'default_params': {
                'period': 20,
                'std_dev': 2.0
            }
        }
    }
    
    def __init__(self):
        """初始化策略管理器"""
        pass
    
    def get_strategy(self, strategy_name: str, **kwargs) -> BaseStrategy:
        """
        获取策略实例
        
        Args:
            strategy_name: 策略名称，可选值：
                - 'double_ma': 双均线策略
                - 'macd': MACD策略
                - 'turtle': 海龟交易策略
                - 'rsi': RSI策略
                - 'bollinger': 布林带策略
            **kwargs: 策略参数，如果不提供则使用默认参数
            
        Returns:
            策略实例
            
        Raises:
            ValueError: 如果策略名称不存在
            
        Examples:
            >>> manager = StrategyManager()
            >>> # 使用默认参数
            >>> strategy = manager.get_strategy('double_ma')
            >>> # 自定义参数
            >>> strategy = manager.get_strategy('double_ma', short_window=10, long_window=30)
        """
        strategy_name = strategy_name.lower()
        
        if strategy_name not in self._STRATEGY_REGISTRY:
            available = ', '.join(self._STRATEGY_REGISTRY.keys())
            raise ValueError(
                f"未知的策略名称: '{strategy_name}'\n"
                f"可用的策略: {available}"
            )
        
        strategy_class = self._STRATEGY_REGISTRY[strategy_name]
        
        # 如果没有提供参数，使用默认参数
        if not kwargs:
            kwargs = self._STRATEGY_INFO[strategy_name]['default_params'].copy()
        
        return strategy_class(**kwargs)
    
    def list_strategies(self, detailed: bool = False) -> List[str]:
        """
        列出所有可用的策略
        
        Args:
            detailed: 是否显示详细信息
            
        Returns:
            策略名称列表（如果detailed=False）或详细信息
        """
        if not detailed:
            return list(self._STRATEGY_REGISTRY.keys())
        
        print("\n" + "="*60)
        print("📊 可用策略列表")
        print("="*60 + "\n")
        
        for i, (key, info) in enumerate(self._STRATEGY_INFO.items(), 1):
            print(f"{i}. 【{info['name']}】 ('{key}')")
            print(f"   描述: {info['description']}")
            print(f"   适合场景: {info['适合场景']}")
            print(f"   默认参数: {info['default_params']}")
            print()
        
        return list(self._STRATEGY_REGISTRY.keys())
    
    def get_strategy_info(self, strategy_name: str) -> Dict[str, Any]:
        """
        获取策略的详细信息
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            策略信息字典
            
        Raises:
            ValueError: 如果策略名称不存在
        """
        strategy_name = strategy_name.lower()
        
        if strategy_name not in self._STRATEGY_INFO:
            available = ', '.join(self._STRATEGY_INFO.keys())
            raise ValueError(
                f"未知的策略名称: '{strategy_name}'\n"
                f"可用的策略: {available}"
            )
        
        return self._STRATEGY_INFO[strategy_name].copy()
    
    def get_all_strategies(self, **common_params) -> Dict[str, BaseStrategy]:
        """
        获取所有策略的实例（使用默认参数）
        
        Args:
            **common_params: 所有策略共享的参数（如果适用）
            
        Returns:
            策略名称到策略实例的字典
            
        Examples:
            >>> manager = StrategyManager()
            >>> all_strategies = manager.get_all_strategies()
            >>> for name, strategy in all_strategies.items():
            ...     print(f"策略: {strategy.name}")
        """
        strategies = {}
        for strategy_name in self._STRATEGY_REGISTRY.keys():
            try:
                strategies[strategy_name] = self.get_strategy(strategy_name, **common_params)
            except TypeError:
                # 如果common_params不适用于某个策略，使用默认参数
                strategies[strategy_name] = self.get_strategy(strategy_name)
        
        return strategies
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[BaseStrategy], 
                         info: Optional[Dict[str, Any]] = None):
        """
        注册自定义策略（高级功能）
        
        Args:
            name: 策略名称
            strategy_class: 策略类
            info: 策略信息（可选）
        """
        cls._STRATEGY_REGISTRY[name.lower()] = strategy_class
        
        if info:
            cls._STRATEGY_INFO[name.lower()] = info
        else:
            cls._STRATEGY_INFO[name.lower()] = {
                'name': name,
                'description': '自定义策略',
                '适合场景': '未指定',
                'default_params': {}
            }


if __name__ == "__main__":
    # 测试代码
    manager = StrategyManager()
    
    print("测试策略管理器\n")
    
    # 列出所有策略
    manager.list_strategies(detailed=True)
    
    # 创建策略实例
    print("="*60)
    print("创建策略实例测试")
    print("="*60 + "\n")
    
    # 使用默认参数
    strategy1 = manager.get_strategy('double_ma')
    print(f"✓ 创建策略: {strategy1.name}")
    
    # 使用自定义参数
    strategy2 = manager.get_strategy('macd', fast_period=10, slow_period=20, signal_period=5)
    print(f"✓ 创建策略: {strategy2.name}")
    
    # 获取策略信息
    print("\n" + "="*60)
    print("获取策略信息测试")
    print("="*60 + "\n")
    info = manager.get_strategy_info('rsi')
    print(f"策略名称: {info['name']}")
    print(f"描述: {info['description']}")
    print(f"默认参数: {info['default_params']}")
    
    print("\n✅ 所有测试通过！")
