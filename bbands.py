# !pip install basana[charts]
# !pip install talipp

from talipp.indicators import BB

import basana as bs


# Strategy based on Bollinger Bands: https://www.investopedia.com/articles/trading/07/bollinger.asp
class Strategy(bs.TradingSignalSource):
    def __init__(self, dispatcher: bs.EventDispatcher, period: int, std_dev_multiplier: float):
        super().__init__(dispatcher)
        self.bb = BB(period, std_dev_multiplier)
        self._values = (None, None)

    async def on_bar_event(self, bar_event: bs.BarEvent):
        # Feed the technical indicator.
        value = float(bar_event.bar.close)
        self.bb.add_input_value(value)

        # Keep a small window of values to check if there is a crossover.
        self._values = (self._values[-1], value)

        # Is the indicator ready ?
        if len(self.bb) < 2:
            return

        # Price moved below lower band ?
        if self._values[-2] >= self.bb[-2].lb and self._values[-1] < self.bb[-1].lb:
            self.push(bs.TradingSignal(bar_event.when, bs.OrderOperation.BUY, bar_event.bar.pair))
        # Price moved above upper band ?
        elif self._values[-2] <= self.bb[-2].ub and self._values[-1] > self.bb[-1].ub:
            self.push(bs.TradingSignal(bar_event.when, bs.OrderOperation.SELL, bar_event.bar.pair))