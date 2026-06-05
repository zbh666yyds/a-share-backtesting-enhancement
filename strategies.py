# strategies.py

from backtesting import Strategy
from backtesting.lib import crossover


def SMA(values, n):
    """
    简单移动平均线
    """
    return values.rolling(n).mean()


class SmaCrossStrategy(Strategy):
    """
    双均线交叉策略：
    - 短期均线上穿长期均线：买入
    - 长期均线上穿短期均线：卖出
    """
    short_window = 10
    long_window = 20

    def init(self):
        close = self.data.Close.s
        self.sma_short = self.I(SMA, close, self.short_window)
        self.sma_long = self.I(SMA, close, self.long_window)

    def next(self):
        if crossover(self.sma_short, self.sma_long):
            self.buy()

        elif crossover(self.sma_long, self.sma_short):
            self.position.close()