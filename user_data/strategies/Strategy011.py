
# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
import numpy # noqa

class Strategy011(IStrategy):
    """
    Strategy 011
    author@: Jason Too
    Added stricter thresholds for trigger using S007 - 11/3/2021
    How to use it?
    > python3 ./freqtrade/main.py -s Strategy002
    """
    
    # # Minimal ROI designed for the strategy.
    # # This attribute will be overridden if the config file contains "minimal_roi"
    # minimal_roi = {
    #     "60":  0.015,
    #     "30":  0.03,
    #     "20":  0.06,
    #     "0":  0.176
    # }

    # # Optimal stoploss designed for the strategy
    # # This attribute will be overridden if the config file contains "stoploss"
    # stoploss = -0.10
    
     # ROI table:
    minimal_roi = {
        "0": 0.17631,
        "14": 0.03154,
        "63": 0.01506,
        "150": -0.05,
    }

    # Stoploss:
    stoploss = -0.2

    # Optimal timeframe for the strategy
    timeframe = '5m'

    # trailing stoploss
    trailing_stop = False
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02

    # run "populate_indicators" only for new candle
    process_only_new_candles = False

    # Experimental settings (configuration will overide these if set)
    use_sell_signal = True
    sell_profit_only = True
    ignore_roi_if_buy_signal = False

    # Optional order type mapping
    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        """
        # Stochastic Fast
        stoch_fast = ta.STOCHF(dataframe)
        dataframe['fastd'] = stoch_fast['fastd']

        # Stochastic Slow
        stoch = ta.STOCH(dataframe)
        dataframe['slowd'] = stoch['slowd']
        dataframe['slowk'] = stoch['slowk']

        # Bollinger Bands
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_upperband'] = bollinger['upper']

        # Dragonfly Doji: values [0, 100]
        dataframe['CDLDRAGONFLYDOJI'] = ta.CDLDRAGONFLYDOJI(dataframe)
        # Evening Doji Star: values [0, 100]
        dataframe['CDLEVENINGDOJISTAR'] = ta.CDLEVENINGDOJISTAR(dataframe)
        # Evening Star: values [0, 100]
        dataframe['CDLEVENINGSTAR'] = ta.CDLEVENINGSTAR(dataframe)

        # ADX
        dataframe['adx'] = ta.ADX(dataframe)

        # MFI
        dataframe['mfi'] = ta.MFI(dataframe)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                # (dataframe['CDLDRAGONFLYDOJI'] == 100) |
                (
                    (dataframe['fastd'] < 38) &
                    (dataframe['slowk'] < 22) &
                    (dataframe['close'] < 0.98*dataframe['bb_lowerband'])
                )
            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe['CDLEVENINGSTAR'] == 100) |
                (dataframe['CDLEVENINGDOJISTAR'] == 100) |
                (
                    (dataframe['adx'] < 52) & 
                    # (dataframe['mfi'] > 99) & 
                    (dataframe['rsi'] > 71) &
                    (dataframe['close'] > 1.02*dataframe['bb_upperband'])
                )
            ),
            'sell'] = 1
        return dataframe
