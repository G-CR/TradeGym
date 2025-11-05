# 📈 量化交易入门项目

一个完整的Python量化交易回测框架，专为初学者设计。包含数据获取、策略开发、回测引擎、性能分析和可视化等完整功能。

## 🎯 项目特点

- ✅ **易于上手**：清晰的代码结构，详细的注释
- ✅ **功能完整**：从数据获取到结果分析的完整流程
- ✅ **支持A股**：使用AkShare获取A股实时数据
- ✅ **多种策略**：内置5个经典量化策略
- ✅ **可扩展**：轻松创建自定义策略
- ✅ **专业分析**：提供详细的性能指标和可视化

## 📁 项目结构

```
.
├── README.md                      # 项目说明文档
├── requirements.txt               # 依赖包列表
├── data_fetcher.py               # 数据获取模块
├── backtest_engine.py            # 回测引擎核心
├── strategies.py                 # 策略模块（5个内置策略）
├── performance_analyzer.py       # 性能分析模块
├── visualizer.py                 # 可视化模块
├── example_single_strategy.py    # 示例1：单策略回测
├── example_compare_strategies.py # 示例2：多策略对比
├── example_custom_strategy.py    # 示例3：自定义策略
└── outputs/                      # 输出目录（图表等）
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

**注意**：如果你在安装 `ta-lib` 时遇到问题，可以暂时注释掉 requirements.txt 中的这一行，其他功能不受影响。

### 2. 运行你的第一个回测

```bash
python example_single_strategy.py
```

这将运行一个双均线策略的完整回测，并生成详细的分析报告和可视化图表。

### 3. 对比多个策略

```bash
python example_compare_strategies.py
```

一次性测试所有内置策略，找出表现最好的那个！

### 4. 创建自己的策略

```bash
python example_custom_strategy.py
```

查看如何创建和测试自定义策略的完整示例。

## 📊 内置策略

项目内置了5个经典量化策略：

### 1. **双均线策略** (Double MA)
- 原理：短期均线上穿长期均线买入，下穿卖出
- 适合：趋势明显的市场
- 参数：短期窗口=5，长期窗口=20

### 2. **MACD策略**
- 原理：MACD线和信号线的交叉
- 适合：中长期趋势跟踪
- 参数：快线=12，慢线=26，信号线=9

### 3. **海龟交易策略** (Turtle Trading)
- 原理：唐奇安通道突破系统
- 适合：趋势跟踪
- 参数：入场周期=20，出场周期=10

### 4. **RSI策略**
- 原理：相对强弱指标超买超卖
- 适合：震荡市场
- 参数：周期=14，超卖=30，超买=70

### 5. **布林带策略** (Bollinger Bands)
- 原理：价格触及上下轨时交易
- 适合：均值回归策略
- 参数：周期=20，标准差=2.0

## 💻 使用示例

### 基础用法

```python
from data_fetcher import DataFetcher
from backtest_engine import BacktestEngine
from strategies import DoubleMAStrategy
from performance_analyzer import PerformanceAnalyzer
from visualizer import Visualizer

# 1. 获取数据
fetcher = DataFetcher()
data = fetcher.get_stock_data(
    symbol='000001',      # 平安银行
    start_date='20220101',
    end_date='20241101',
    adjust='qfq'          # 前复权
)

# 2. 创建策略
strategy = DoubleMAStrategy(short_window=5, long_window=20)

# 3. 运行回测
engine = BacktestEngine(initial_cash=100000, commission_rate=0.0003)
engine.set_data(data)
engine.set_strategy(strategy)
results = engine.run()

# 4. 分析结果
analyzer = PerformanceAnalyzer(results)
analyzer.print_summary()
analyzer.print_detailed_analysis()

# 5. 可视化
visualizer = Visualizer(results, engine.data)
visualizer.plot_equity_curve()
visualizer.plot_with_signals()
```

### 创建自定义策略

```python
from strategies import BaseStrategy
import pandas as pd

class MyStrategy(BaseStrategy):
    """我的自定义策略"""
    
    def __init__(self, param1=10, param2=20):
        super().__init__(name="我的策略")
        self.param1 = param1
        self.param2 = param2
        
    def _prepare_indicators(self):
        """计算技术指标"""
        # 在这里计算你需要的所有指标
        self.data['indicator1'] = self.data['close'].rolling(self.param1).mean()
        self.data['indicator2'] = self.data['close'].rolling(self.param2).mean()
        
    def generate_signal(self, data: pd.DataFrame, index: int) -> int:
        """
        生成交易信号
        
        Returns:
            1: 买入信号
            0: 持有
            -1: 卖出信号
        """
        if index < self.param2:
            return 0
            
        current = data.iloc[index]
        
        # 你的交易逻辑
        if current['indicator1'] > current['indicator2']:
            return 1  # 买入
        elif current['indicator1'] < current['indicator2']:
            return -1  # 卖出
        
        return 0  # 持有
```

## 📈 性能指标说明

回测系统会计算以下性能指标：

### 收益指标
- **总收益率**：整个回测期间的总收益
- **年化收益率**：按年计算的平均收益率
- **最终资产**：回测结束时的总资产

### 风险指标
- **最大回撤**：从最高点到最低点的最大跌幅
- **夏普比率**：风险调整后的收益指标（>1为好，>2为优秀）
- **索提诺比率**：只考虑下行风险的夏普比率
- **卡玛比率**：收益率与最大回撤的比值
- **波动率**：收益的标准差

### 交易指标
- **总交易次数**：买入+卖出的总次数
- **胜率**：盈利交易占比
- **平均盈亏**：每笔交易的平均盈亏
- **盈亏比**：盈利交易总额/亏损交易总额
- **平均持仓天数**：平均每笔交易的持有时间

## 📚 学习路径建议

### 第一周：熟悉框架
1. 运行 `example_single_strategy.py`，理解回测流程
2. 阅读 `strategies.py`，学习策略是如何实现的
3. 尝试修改策略参数，观察结果变化

### 第二周：对比分析
1. 运行 `example_compare_strategies.py`，对比不同策略
2. 分析为什么有些策略表现好，有些不好
3. 思考：在什么市场环境下用什么策略

### 第三周：创建策略
1. 学习 `example_custom_strategy.py` 中的示例
2. 实现一个简单的自己的策略
3. 回测并优化你的策略

### 第四周：深入优化
1. 学习参数优化技巧
2. 理解过拟合的风险
3. 学习风险管理和仓位控制

## ⚠️ 重要提醒

### 1. 过拟合风险
- ❌ 不要过度优化参数以适应历史数据
- ✅ 使用样本外数据验证策略
- ✅ 保持策略简单，避免过于复杂

### 2. 交易成本
- ✅ 回测时已包含手续费和印花税
- ⚠️ 实盘交易还可能有滑点
- ⚠️ 高频交易会产生更多成本

### 3. 风险控制
- ✅ 永远设置止损
- ✅ 控制单次交易的仓位
- ✅ 分散投资，不要all-in
- ✅ 根据自己的风险承受能力调整策略

### 4. 心态管理
- 回测好 ≠ 实盘一定赚钱
- 市场在不断变化，策略需要持续迭代
- 保持学习，保持谨慎
- **最重要：不要用你输不起的钱！**

## 🔧 常见问题

### Q: 如何更换股票？
A: 在调用 `get_stock_data()` 时，修改 `symbol` 参数即可。常见股票代码：
- 000001: 平安银行
- 600519: 贵州茅台
- 000858: 五粮液
- 600036: 招商银行

### Q: 如何调整回测时间范围？
A: 修改 `start_date` 和 `end_date` 参数，格式为 'YYYYMMDD'。

### Q: 手续费率如何设置？
A: 在创建 `BacktestEngine` 时设置 `commission_rate`，默认为万3（0.0003）。

### Q: 为什么我的策略表现很差？
A: 可能的原因：
- 策略不适合当前市场环境
- 参数没有优化
- 股票本身在回测期间表现不佳
- 正常现象！不是所有策略都会赚钱

### Q: 如何避免未来函数？
A: 在 `generate_signal` 中只使用 `index` 之前的数据，不要使用之后的数据。

### Q: 安装 ta-lib 失败怎么办？
A: ta-lib 不是必需的，你可以：
1. 在 requirements.txt 中注释掉 `ta-lib`
2. 使用 `pandas-ta` 替代（已包含在依赖中）
3. 手动安装：macOS 可以用 `brew install ta-lib`

## 🎓 推荐学习资源

### 书籍
- 《Python金融大数据分析》
- 《量化投资：以Python为工具》
- 《打开量化投资的黑箱》
- 《海龟交易法则》

### 在线资源
- [聚宽](https://www.joinquant.com/) - 在线量化平台
- [米筐](https://www.ricequant.com/) - 量化交易平台
- [AkShare文档](https://akshare.akfamily.xyz/) - 数据接口文档

### 社区
- 知乎量化交易话题
- GitHub上的开源量化项目
- 各大量化平台的社区论坛

## 📝 下一步计划

学完这个项目后，你可以：

1. **添加更多策略**
   - 均值回归策略
   - 多因子模型
   - 机器学习策略

2. **改进回测引擎**
   - 支持多股票组合
   - 动态仓位管理
   - 更复杂的订单类型

3. **参数优化**
   - 网格搜索
   - 遗传算法
   - 贝叶斯优化

4. **实盘交易**
   - 连接券商API
   - 实盘监控
   - 自动化交易

5. **机器学习**
   - 特征工程
   - 预测模型
   - 强化学习

## 🤝 贡献

欢迎提出建议和改进！这是一个学习项目，适合：
- 量化交易初学者
- Python学习者
- 对金融市场感兴趣的程序员

## ⚖️ 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。

- ❌ 历史表现不代表未来收益
- ❌ 回测结果可能存在偏差
- ❌ 实盘交易存在风险，请谨慎决策

投资有风险，入市需谨慎！

## 📧 联系方式

如有问题或建议，欢迎交流讨论！

---

**祝你在量化交易的学习之路上收获满满！** 📈💰

记住：**学习的目的是理解市场，而不是快速致富。保持好奇心，保持谨慎，持续学习！**

