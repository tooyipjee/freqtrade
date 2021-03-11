# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

# --- Do not remove these libs ---
from functools import reduce
from typing import Any, Callable, Dict, List

import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from skopt.space import Categorical, Dimension, Integer, Real  # noqa

from freqtrade.optimize.hyperopt_interface import IHyperOpt

# --------------------------------
# Add your lib to import here
import talib.abstract as ta  # noqa
import freqtrade.vendor.qtpylib.indicators as qtpylib


class AwesomeHyperopt(IHyperOpt):
    """
    This is a Hyperopt template to get you started.

    More information in the documentation: https://www.freqtrade.io/en/latest/hyperopt/

    You should:
    - Add any lib you need to build your hyperopt.

    You must keep:
    - The prototypes for the methods: populate_indicators, indicator_space, buy_strategy_generator.

    The methods roi_space, generate_roi_table and stoploss_space are not required
    and are provided by default.
    However, you may override them if you need 'roi' and 'stoploss' spaces that
    differ from the defaults offered by Freqtrade.
    Sample implementation of these methods will be copied to `user_data/hyperopts` when
    creating the user-data directory using `freqtrade create-userdir --userdir user_data`,
    or is available online under the following URL:
    https://github.com/freqtrade/freqtrade/blob/develop/freqtrade/templates/sample_hyperopt_advanced.py.
    """

    @staticmethod
    def buy_strategy_generator(params: Dict[str, Any]) -> Callable:
        """
        Define the buy strategy parameters to be used by Hyperopt.
        """
        def populate_buy_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            """
            Buy strategy Hyperopt will build and use.
            """
            conditions = []

            # GUARDS AND TRENDS
            # if params.get('mfi-enabled'):
            #     conditions.append(dataframe['mfi'] < params['mfi-value'])
            # if params.get('fastd-enabled'):
            #     conditions.append(dataframe['fastd'] < params['fastd-value'])
            # if params.get('adx-enabled'):
            #     conditions.append(dataframe['adx'] > params['adx-value'])
            if params.get('rsi-enabled'):
                conditions.append(dataframe['rsi'] < params['rsi-value'])
            if params.get('slowk-enabled'):
                conditions.append(dataframe['slowk'] < params['slowk-value'])
            if params.get('CDLHAMMER-enabled'):
                conditions.append(dataframe['CDLHAMMER'] == 100)
            # if params.get('CDLDRAGONFLYDOJI-enabled'):
            #     conditions.append(dataframe['CDLDRAGONFLYDOJI'] == 100)
            # if params.get('CDLMORNINGSTAR-enabled'):
            #     conditions.append(dataframe['CDLMORNINGSTAR'] == 100)

            # TRIGGERS
            if 'trigger' in params:
                if params['trigger'] == 'bb_lower':
                    conditions.append(dataframe['close'] < dataframe['bb_lowerband'])
                if params['trigger'] == 'wbb_lower':
                    conditions.append(dataframe['close'] < dataframe['wbb_lowerband'])
                if params['trigger'] == 'macd_cross_signal':
                    conditions.append(qtpylib.crossed_above(
                        dataframe['macd'], dataframe['macdsignal']
                    ))
                if params['trigger'] == 'sar_reversal':
                    conditions.append(qtpylib.crossed_above(
                        dataframe['close'], dataframe['sar']
                    ))
                if params['trigger'] == 'ao_signal':
                    conditions.append(qtpylib.crossed_above(
                        dataframe['ao'], params['ao-value']
                    ))


            # Check that the candle had volume
            conditions.append(dataframe['volume'] > 0)

            if conditions:
                dataframe.loc[
                    reduce(lambda x, y: x & y, conditions),
                    'buy'] = 1

            return dataframe

        return populate_buy_trend

    @staticmethod
    def indicator_space() -> List[Dimension]:
        """
        Define your Hyperopt space for searching buy strategy parameters.
        """
        return [
            # Integer(10, 25, name='mfi-value'),
            # Integer(15, 45, name='fastd-value'),
            # Integer(20, 50, name='adx-value'),
            Integer(20, 40, name='rsi-value'),
            Integer(20, 40, name='slowk-value'),
            Integer(-20, 20, name='ao-value'),
            # Categorical([True, False], name='mfi-enabled'),
            # Categorical([True, False], name='fastd-enabled'),
            # Categorical([True, False], name='adx-enabled'),
            Categorical([True, False], name='slowk-enabled'),
            Categorical([True, False], name='rsi-enabled'),
            # Categorical([True, False], name='CDLHAMMER-enabled'),
            # Categorical([True, False], name='CDLDRAGONFLYDOJI-enabled'),
            # Categorical([True, False], name='CDLMORNINGSTAR-enabled'),
            Categorical([
                'bb_lower',
                'macd_cross_signal',
                'sar_reversal',
                'ao_signal',
                'wbb_lower'
                ], name='trigger'),

            
            
        ]

    @staticmethod
    def sell_strategy_generator(params: Dict[str, Any]) -> Callable:
        """
        Define the sell strategy parameters to be used by Hyperopt.
        """
        def populate_sell_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
            """
            Sell strategy Hyperopt will build and use.
            """
            conditions = []

            # GUARDS AND TRENDS
            # if params.get('sell-mfi-enabled'):
            #     conditions.append(dataframe['mfi'] > params['sell-mfi-value'])
            if params.get('sell-fastd-enabled'):
                conditions.append(dataframe['fastd'] > params['sell-fastd-value'])
            # if params.get('sell-adx-enabled'):
            #     conditions.append(dataframe['adx'] < params['sell-adx-value'])
            if params.get('sell-rsi-enabled'):
                conditions.append(dataframe['rsi'] > params['sell-rsi-value'])
            # if params.get('CDLHANGINGMAN-enabled'):
            #     conditions.append(dataframe['CDLHANGINGMAN'] == 100)
            # if params.get('CDLEVENINGDOJISTAR-enabled'):
            #     conditions.append(dataframe['CDLEVENINGDOJISTAR'] == 100)
            # if params.get('CDLEVENINGSTAR-enabled'):
            #     conditions.append(dataframe['CDLEVENINGSTAR'] == 100)
            
            # TRIGGERS
            if 'sell-trigger' in params:
                if params['sell-trigger'] == 'sell-bb_upper':
                    conditions.append(dataframe['close'] > dataframe['bb_upperband'])
                if params['sell-trigger'] == 'sell-wbb_upper':
                    conditions.append(dataframe['close'] > dataframe['wbb_upperband'])
                if params['sell-trigger'] == 'sell-macd_cross_signal':
                    conditions.append(qtpylib.crossed_above(
                        dataframe['macdsignal'], dataframe['macd']
                    ))
                if params['sell-trigger'] == 'sell-sar_reversal':
                    conditions.append(qtpylib.crossed_above(
                        dataframe['sar'], dataframe['close']
                    ))
                if params['sell-trigger'] == 'sell-ao_signal':
                    conditions.append(qtpylib.crossed_below(
                        dataframe['ao'], params['sell-ao-value']
                    ))

            # Check that the candle had volume
            conditions.append(dataframe['volume'] > 0)

            if conditions:
                dataframe.loc[
                    reduce(lambda x, y: x & y, conditions),
                    'sell'] = 1

            return dataframe

        return populate_sell_trend

    @staticmethod
    def sell_indicator_space() -> List[Dimension]:
        """
        Define your Hyperopt space for searching sell strategy parameters.
        """
        return [
            # Integer(75, 100, name='sell-mfi-value'),
            Integer(50, 100, name='sell-fastd-value'),
            # Integer(50, 100, name='sell-adx-value'),
            Integer(60, 100, name='sell-rsi-value'),
            Integer(-20, 20, name='sell-ao-value'),
            # Categorical([True, False], name='sell-mfi-enabled'),
            Categorical([True, False], name='sell-fastd-enabled'),
            # Categorical([True, False], name='sell-adx-enabled'),
            Categorical([True, False], name='sell-rsi-enabled'),
            Categorical(['sell-bb_upper',
                        'sell-wbb_upper',
                        'sell-macd_cross_signal',
                        'sell-sar_reversal',
                        'sell-ao_signal'], name='sell-trigger'),
            # Categorical([True, False], name='CDLHANGINGMAN-enabled'),
            # Categorical([True, False], name='CDLEVENINGDOJISTAR-enabled'),
            # Categorical([True, False], name='CDLEVENINGSTAR-enabled'),
                         
        ]