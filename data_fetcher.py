"""
数据获取模块
支持从多个数据源获取股票数据
"""

import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
from typing import Optional
import warnings
warnings.filterwarnings('ignore')


class DataFetcher:
    """数据获取类"""
    
    def __init__(self):
        self.data_source = "akshare"
    
    def get_stock_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str,
        adjust: str = "qfq"
    ) -> pd.DataFrame:
        """
        获取股票历史数据
        
        Args:
            symbol: 股票代码，如 '000001'（平安银行）
            start_date: 开始日期，格式 'YYYYMMDD'
            end_date: 结束日期，格式 'YYYYMMDD'
            adjust: 复权类型，'qfq'前复权, 'hfq'后复权, ''不复权
            
        Returns:
            包含OHLCV数据的DataFrame
        """
        try:
            print(f"正在获取 {symbol} 从 {start_date} 到 {end_date} 的数据...")
            
            # 使用akshare获取A股数据
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            if df is None or len(df) == 0:
                raise ValueError(f"无法获取股票 {symbol} 的数据")
            
            # 标准化列名
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'pct_change',
                '涨跌额': 'change',
                '换手率': 'turnover'
            })
            
            # 设置日期为索引
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 确保数据类型正确
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            print(f"成功获取 {len(df)} 条数据")
            return df
            
        except Exception as e:
            print(f"获取数据失败: {str(e)}")
            raise
    
    def get_stock_list(self, market: str = "all") -> pd.DataFrame:
        """
        获取股票列表
        
        Args:
            market: 市场类型，'sh'上证, 'sz'深证, 'all'全部
            
        Returns:
            股票列表DataFrame
        """
        try:
            # 获取A股实时行情数据
            df = ak.stock_zh_a_spot_em()
            
            if market == "sh":
                df = df[df['代码'].str.startswith(('60', '68'))]
            elif market == "sz":
                df = df[df['代码'].str.startswith(('00', '30'))]
            
            return df
            
        except Exception as e:
            print(f"获取股票列表失败: {str(e)}")
            raise
    
    def get_index_data(
        self, 
        symbol: str = "sh000001",  # 上证指数
        start_date: str = None,
        end_date: str = None
    ) -> pd.DataFrame:
        """
        获取指数数据
        
        Args:
            symbol: 指数代码
                - sh000001: 上证指数
                - sz399001: 深证成指
                - sz399006: 创业板指
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            指数数据DataFrame
        """
        try:
            # 提取指数代码
            if symbol.startswith('sh'):
                index_code = symbol[2:]
            elif symbol.startswith('sz'):
                index_code = symbol[2:]
            else:
                index_code = symbol
            
            df = ak.stock_zh_index_daily(symbol=index_code)
            
            # 标准化列名
            df = df.rename(columns={
                'date': 'date',
                'open': 'open',
                'close': 'close',
                'high': 'high',
                'low': 'low',
                'volume': 'volume'
            })
            
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 日期过滤
            if start_date:
                df = df[df.index >= start_date]
            if end_date:
                df = df[df.index <= end_date]
            
            return df
            
        except Exception as e:
            print(f"获取指数数据失败: {str(e)}")
            raise


def demo():
    """演示如何使用DataFetcher"""
    fetcher = DataFetcher()
    
    # 获取平安银行最近一年的数据
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    
    # 获取股票数据
    df = fetcher.get_stock_data(
        symbol='000001',  # 平安银行
        start_date=start_date,
        end_date=end_date,
        adjust='qfq'  # 前复权
    )
    
    print("\n数据预览:")
    print(df.head())
    print(f"\n数据形状: {df.shape}")
    print(f"日期范围: {df.index[0]} 到 {df.index[-1]}")


if __name__ == "__main__":
    demo()

