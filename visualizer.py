"""
可视化模块
用于绘制回测结果的各种图表
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False


class Visualizer:
    """可视化工具类"""
    
    def __init__(self, results: Dict, data: pd.DataFrame = None):
        """
        初始化可视化工具
        
        Args:
            results: 回测结果
            data: 原始数据
        """
        self.results = results
        self.data = data
        self.equity_curve = results.get('equity_curve', pd.Series())
        self.trades = results.get('trades', [])
        
    def plot_equity_curve(self, figsize=(14, 6), save_path: str = None):
        """
        绘制资金曲线
        
        Args:
            figsize: 图表大小
            save_path: 保存路径
        """
        if self.equity_curve.empty:
            print("没有可用的资金曲线数据")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, height_ratios=[2, 1])
        
        # 资金曲线
        ax1.plot(self.equity_curve.index, self.equity_curve.values, 
                 linewidth=2, color='#2E86AB', label='资金曲线')
        ax1.axhline(y=self.equity_curve.iloc[0], color='gray', 
                    linestyle='--', linewidth=1, alpha=0.5, label='初始资金')
        ax1.set_title('资金曲线', fontsize=14, fontweight='bold')
        ax1.set_ylabel('资金 (¥)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best')
        
        # 格式化Y轴为货币格式
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'¥{x:,.0f}'))
        
        # 回撤曲线
        df = pd.DataFrame({'value': self.equity_curve})
        df['cummax'] = df['value'].cummax()
        df['drawdown'] = (df['value'] - df['cummax']) / df['cummax'] * 100
        
        ax2.fill_between(df.index, df['drawdown'], 0, 
                         color='#A23B72', alpha=0.3, label='回撤')
        ax2.plot(df.index, df['drawdown'], 
                color='#A23B72', linewidth=1.5)
        ax2.set_title('回撤曲线', fontsize=14, fontweight='bold')
        ax2.set_xlabel('日期', fontsize=12)
        ax2.set_ylabel('回撤 (%)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='best')
        
        # 格式化日期
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        
        plt.show()
    
    def plot_with_signals(self, figsize=(14, 8), save_path: str = None):
        """
        绘制价格走势和交易信号
        
        Args:
            figsize: 图表大小
            save_path: 保存路径
        """
        if self.data is None or self.data.empty:
            print("没有价格数据")
            return
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制价格曲线
        ax.plot(self.data.index, self.data['close'], 
                linewidth=2, color='#2E86AB', label='收盘价', alpha=0.8)
        
        # 如果有均线数据，绘制均线
        if 'ma_short' in self.data.columns:
            ax.plot(self.data.index, self.data['ma_short'], 
                    linewidth=1.5, color='#F18F01', label='短期均线', alpha=0.7)
        
        if 'ma_long' in self.data.columns:
            ax.plot(self.data.index, self.data['ma_long'], 
                    linewidth=1.5, color='#C73E1D', label='长期均线', alpha=0.7)
        
        # 绘制布林带
        if 'upper_band' in self.data.columns:
            ax.plot(self.data.index, self.data['upper_band'], 
                    linewidth=1, color='gray', linestyle='--', alpha=0.5, label='上轨')
            ax.plot(self.data.index, self.data['lower_band'], 
                    linewidth=1, color='gray', linestyle='--', alpha=0.5, label='下轨')
            ax.fill_between(self.data.index, self.data['upper_band'], self.data['lower_band'],
                           alpha=0.1, color='gray')
        
        # 标记买卖点
        if self.trades:
            buy_trades = [t for t in self.trades if t.action == 'buy']
            sell_trades = [t for t in self.trades if t.action == 'sell']
            
            if buy_trades:
                buy_dates = [t.date for t in buy_trades]
                buy_prices = [t.price for t in buy_trades]
                ax.scatter(buy_dates, buy_prices, marker='^', 
                          color='red', s=100, zorder=5, label='买入', alpha=0.8)
            
            if sell_trades:
                sell_dates = [t.date for t in sell_trades]
                sell_prices = [t.price for t in sell_trades]
                ax.scatter(sell_dates, sell_prices, marker='v', 
                          color='green', s=100, zorder=5, label='卖出', alpha=0.8)
        
        ax.set_title('价格走势与交易信号', fontsize=14, fontweight='bold')
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('价格 (¥)', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # 格式化日期
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        
        plt.show()
    
    def plot_returns_distribution(self, figsize=(12, 5), save_path: str = None):
        """
        绘制收益率分布
        
        Args:
            figsize: 图表大小
            save_path: 保存路径
        """
        if self.equity_curve.empty:
            print("没有可用数据")
            return
        
        returns = self.equity_curve.pct_change().dropna()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # 收益率直方图
        ax1.hist(returns * 100, bins=50, color='#2E86AB', alpha=0.7, edgecolor='black')
        ax1.axvline(x=0, color='red', linestyle='--', linewidth=2, alpha=0.5)
        ax1.set_title('日收益率分布', fontsize=14, fontweight='bold')
        ax1.set_xlabel('收益率 (%)', fontsize=12)
        ax1.set_ylabel('频数', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # 添加统计信息
        stats_text = f'均值: {returns.mean()*100:.3f}%\n'
        stats_text += f'标准差: {returns.std()*100:.3f}%\n'
        stats_text += f'偏度: {returns.skew():.3f}\n'
        stats_text += f'峰度: {returns.kurtosis():.3f}'
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 累计收益率
        cumulative_returns = (1 + returns).cumprod() - 1
        ax2.plot(cumulative_returns.index, cumulative_returns * 100, 
                linewidth=2, color='#2E86AB')
        ax2.fill_between(cumulative_returns.index, 0, cumulative_returns * 100, 
                         alpha=0.3, color='#2E86AB')
        ax2.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax2.set_title('累计收益率', fontsize=14, fontweight='bold')
        ax2.set_xlabel('日期', fontsize=12)
        ax2.set_ylabel('累计收益率 (%)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # 格式化日期
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        
        plt.show()
    
    def plot_monthly_returns(self, figsize=(14, 6), save_path: str = None):
        """
        绘制月度收益率热力图
        
        Args:
            figsize: 图表大小
            save_path: 保存路径
        """
        if self.equity_curve.empty:
            print("没有可用数据")
            return
        
        df = pd.DataFrame({'value': self.equity_curve})
        df['return'] = df['value'].pct_change()
        
        # 计算月度收益
        monthly_returns = df['return'].resample('M').apply(lambda x: (1 + x).prod() - 1)
        
        if len(monthly_returns) < 2:
            print("数据不足以绘制月度收益")
            return
        
        # 重组数据为年-月矩阵
        monthly_df = pd.DataFrame({
            'year': monthly_returns.index.year,
            'month': monthly_returns.index.month,
            'return': monthly_returns.values
        })
        
        pivot_table = monthly_df.pivot(index='year', columns='month', values='return')
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制热力图
        im = ax.imshow(pivot_table.values * 100, cmap='RdYlGn', aspect='auto', 
                      vmin=-10, vmax=10)
        
        # 设置刻度
        ax.set_xticks(range(12))
        ax.set_xticklabels(['1月', '2月', '3月', '4月', '5月', '6月',
                           '7月', '8月', '9月', '10月', '11月', '12月'])
        ax.set_yticks(range(len(pivot_table.index)))
        ax.set_yticklabels(pivot_table.index.astype(int))
        
        # 添加数值标签
        for i in range(len(pivot_table.index)):
            for j in range(len(pivot_table.columns)):
                value = pivot_table.iloc[i, j]
                if not np.isnan(value):
                    text = ax.text(j, i, f'{value*100:.1f}%',
                                 ha="center", va="center", color="black", fontsize=9)
        
        ax.set_title('月度收益率热力图', fontsize=14, fontweight='bold')
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('收益率 (%)', fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        
        plt.show()
    
    def plot_all(self, output_dir: str = "./outputs"):
        """
        生成所有图表
        
        Args:
            output_dir: 输出目录
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print("正在生成所有图表...")
        
        self.plot_equity_curve(save_path=f"{output_dir}/equity_curve.png")
        self.plot_with_signals(save_path=f"{output_dir}/signals.png")
        self.plot_returns_distribution(save_path=f"{output_dir}/returns_dist.png")
        
        if len(self.equity_curve) > 60:  # 至少2个月数据
            self.plot_monthly_returns(save_path=f"{output_dir}/monthly_returns.png")
        
        print(f"所有图表已保存到: {output_dir}")


def compare_strategies_plot(results_dict: Dict[str, Dict], figsize=(14, 6)):
    """
    比较多个策略的资金曲线
    
    Args:
        results_dict: 策略名称到结果的字典
        figsize: 图表大小
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
    
    for i, (name, results) in enumerate(results_dict.items()):
        equity_curve = results.get('equity_curve', pd.Series())
        if not equity_curve.empty:
            # 归一化到100
            normalized = (equity_curve / equity_curve.iloc[0]) * 100
            ax.plot(normalized.index, normalized.values, 
                   linewidth=2, label=name, color=colors[i % len(colors)])
    
    ax.axhline(y=100, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='基准')
    ax.set_title('策略对比 - 归一化资金曲线', fontsize=14, fontweight='bold')
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('归一化资金 (起始=100)', fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    # 格式化日期
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("可视化模块已加载")

