"""
Trading-Technical-Indicators (tti) python library

File name: trading_simulation.py
    Trading simulation class implementation defined under the tti.utils
    package.
"""

import pandas as pd
from ..utils.data_validation import validateInputData
from ..utils.exceptions import WrongTypeForInputParameter, \
    NotValidInputDataForSimulation, WrongValueForInputParameter
from ..utils.constants import TRADE_SIGNALS


class TradingSimulation:
    """
    Trading Simulation class implementation. Provides utilities methods for
    the runSimulation method of the tti.indicators package.

    Args:
        input_data_index (pandas.DateTimeIndex): The indicator's input data
            index. Is used for validating that the close values DataFrame
            includes data for the whole simulation period.

        close_values (pandas.DataFrame): The close prices of the stock, for
            the whole simulation period. Index is of type DateTimeIndex
            with same values as the input to the indicator data. It
            contains one column ``close``.

        max_items_per_transaction (int, default=1): The maximum number of
            stocks to be traded on each ``open_long`` or ``open_short``
            transaction.

        max_investment(float, default=None): Maximum investment for all the
            opened positions (``short`` and ``long``). If the sum of all
            the opened positions reached the maximum investment, then it is
            not allowed to open a new position. A new position can be
            opened when some balance becomes available from a position
            close. If set to  None, then there is no upper limit for the opened
            positions.

    Attributes:
         _input_data_index (pandas.DateTimeIndex): The indicator's input data
            index. Is used for validating that the close values DataFrame
            includes data for the whole simulation period.

        _close_values (pandas.DataFrame): The close prices of the stock, for
            the whole simulation period. Index is of type DateTimeIndex
            with same values as the input to the indicator data. It
            contains one column ``close``.

        _max_items_per_transaction (int, default=1): The maximum number of
            stocks to be traded on each ``open_long`` or ``open_short``
            transaction.

        _max_investment(float, default=None): Maximum investment for all the
            opened positions (``short`` and ``long``). If the sum of all
            the opened positions reached the maximum investment, then it is
            not allowed to open a new position. A new position can be
            opened when some balance becomes available from a position
            close. If set to  None, then there is no upper limit for the opened
            positions.

        _portfolio (pandas.DataFrame): Simulation portfolio, keeps a track of
            the entered positions during the simulation. Position: ``long``,
            ``short`` or ``none``. Items: Number of stocks. Unit_Price: Price
            of each item when entered the position. Status: ``open``, ``close``
            or none

        _simulation_data (pandas.DataFrame): Dataframe which holds details and
            about the simulation. The index of the dataframe is the whole
            trading period(DateTimeIndex). Columns are:

            ``signal``: the signal produced at each day of the simulation
            period.

            ``trading_action``: the trading action applied. Possible values are
            ``open_long``, ``close_long``, ``open_short``, ``close_short`` and
            ``none``.

            ``stocks_in_transaction``: the number of stocks involved in a
            trading_action.

            ``balance``: the available balance (earnings - spending).

            ``stock_value``: The value of the stock during the simulation
            period.

            ``total_value``: the available balance considering the open
            positions (if they would be closed in this transaction).

        _statistics (dict): Statistics about the simulation. contains the below
            keys:

            ``number_of_trading_days``: the number of trading days in the
            simulation round.

            ``number_of_buy_signals``: the number of ``buy`` signals produced
            during the simulation period.

            ``number_of_ignored_buy_signals``: the number of ``buy`` signals
            ignored because of the ``max_investment`` limitation.

            ``number_of_sell_signals``: the number of ``sell`` signals produced
            during the simulation period.

            ``number_of_ignored_sell_signals``: the number of ``sell`` signals
            ignored because of the ``max_investment`` limitation.

            ``balance``: the final available balance (earnings - spending).

            ``total_stocks_in_long``: the number of stocks in long position at
            the end of the simulation.

            ``total_stocks_in_short``: the number of stocks in short position
            at the end of the simulation.

            ``stock_value``: The value of the stock at the end of the
            simulation.

            ``total_value``: The balance plus after closing all the open
            positions.

    Raises:
        WrongTypeForInputParameter: Input argument has wrong type.
        WrongValueForInputParameter: Unsupported value for input argument.
        NotValidInputDataForSimulation: Invalid ``close_values`` `passed for
            the simulation.
    """

    def __init__(self, input_data_index, close_values,
                 max_items_per_transaction=1, max_investment=None):

        self._input_data_index = input_data_index
        self._close_values = close_values
        self._max_items_per_transaction = max_items_per_transaction
        self._max_investment = max_investment

        # Validate input arguments
        self._validateSimulationArguments()

        # Simulation portfolio, keeps a track of the entered positions during
        # the simulation. Position: `long`, `short` or `none`. Items: Number of
        # stocks. Unit_Price: Price of each item when entered the position.
        # Status: `open`, `close` or none
        self._portfolio = pd.DataFrame(
            index=self._input_data_index,
            columns=['position', 'items', 'unit_price', 'status'], data=None)

        # Initialize simulation data structure (DataFrame)
        self._simulation_data = pd.DataFrame(
            index=self._input_data_index,
            columns=['signal', 'trading_action', 'stocks_in_transaction',
                     'balance', 'stock_value', 'total_value'],
            data=None)

        # Initialize statistics data structure (dict)
        self._statistics = {
            'number_of_trading_days': 0,
            'number_of_buy_signals': 0,
            'number_of_ignored_buy_signals': 0,
            'number_of_sell_signals': 0,
            'number_of_ignored_sell_signals': 0,
            'balance': 0.0,
            'total_stocks_in_long': 0,
            'total_stocks_in_short': 0,
            'stock_value': 0.0,
            'total_value': 0.0}

    def _validateSimulationArguments(self):
        """
        Validates the input arguments passed in the constructor. input_data and
        ti_data are already validated by the tti.indicators package.

        Raises:
            WrongTypeForInputParameter: Input argument has wrong type.
            WrongValueForInputParameter: Unsupported value for input argument.
            NotValidInputDataForSimulation: Invalid ``close_values`` `passed
                for the simulation.
        """

        # Validate close_values pandas.DataFrame
        try:
            self._close_values = validateInputData(
                input_data=self._close_values, required_columns=['close'],
                indicator_name='TradingSimulation',
                fill_missing_values=True)

        except Exception as e:
            raise NotValidInputDataForSimulation(
                'close_values', str(e).replace('input_data', 'close_values'))

        if not self._close_values.index.equals(self._input_data_index):
            raise NotValidInputDataForSimulation(
                'close_values', 'Index of the `close_values` DataFrame ' +
                                'should be the same as the index of the ' +
                                '`input_data` argument in the indicator\'s ' +
                                'constructor.')

        # Validate _max_items_per_transaction
        if isinstance(self._max_items_per_transaction, int):
            if self._max_items_per_transaction <= 0:
                raise WrongValueForInputParameter(
                    self._max_items_per_transaction,
                    'max_items_per_transaction', '>0')
        else:
            raise WrongTypeForInputParameter(
                type(self._max_items_per_transaction),
                'max_items_per_transaction', 'int')

        # Validate max_investment
        if isinstance(self._max_investment, (int, float)):
            if self._max_investment <= 0:
                raise WrongValueForInputParameter(
                    self._max_investment, 'max_investment', '>0')
        elif self._max_investment is None:
            pass
        else:
            raise WrongTypeForInputParameter(
                type(self._max_investment), 'max_investment',
                'int or float or None')

    def _calculateSimulationStatistics(self):
        """
        Calculate simulation statistics, at the end of the simulation.
        """

        self._statistics = {
            'number_of_trading_days': len(self._simulation_data.index),

            'number_of_buy_signals':
                len(self._simulation_data[
                        self._simulation_data['signal'] == 'buy'].index),

            'number_of_ignored_buy_signals':
                len(self._simulation_data[
                        self._simulation_data['signal'] == 'buy' and
                        self._simulation_data['trading_action'] == 'none'].
                    index),

            'number_of_sell_signals':
                len(self._simulation_data[
                        self._simulation_data['signal'] == 'sell'].index),

            'number_of_ignored_sell_signals':
                len(self._simulation_data[
                        self._simulation_data['signal'] == 'sell' and
                        self._simulation_data['trading_action'] == 'none'].
                    index),

            'balance': self._simulation_data['balance'].iat[-1],

            'total_stocks_in_long':
                self._portfolio[
                    self._portfolio['position'] == 'long' and
                    self._portfolio['close'] == 'open']['items'].sum(),

            'total_stocks_in_short':
                self._portfolio[
                    self._portfolio['position'] == 'short' and
                    self._portfolio['close'] == 'open']['items'].sum(),

            'stock_value': self._simulation_data['stock_value'].iat[-1],

            'total_value': self._simulation_data['total_value'].iat[-1]}

    def _closeOpenPositions(self, price, force_all=False, write=True):
        """
        Closes the opened positions existing in portfolio.

        Args:
            price (float): The price of the stock to be considered in the
                closing transactions.

            force_all (bool, default=False): If True, all the opened positions
                are being closed. If False, only the positions which will bring
                earnings are being closed.

            write (bool, default=True): If True, update the status of the
                positions in the portfolio. If False, then the positions remain
                open.

        Returns:
            float: The value of the transactions executed (earnings -
            spending).
        """

        # Close all the open positions
        if force_all:
            total_long_items = \
                sum(self._portfolio[self._portfolio['status'] == 'open' and
                    self._portfolio['position'] == 'long']['items'])

            total_short_items = \
                sum(self._portfolio[self._portfolio['status'] == 'open' and
                    self._portfolio['position'] == 'short']['items'])

            # Value when closing short and long positions
            value = (total_long_items - total_short_items) * price

            # Register close action
            if write:
                self._portfolio[
                    self._portfolio['status'] == 'open']['status'] = 'close'

        # Close only positions that bring earnings
        else:

            # Use 2*commission, for the expenses when position was opened and
            # for the expenses from the position closing
            total_long_items = \
                sum(self._portfolio[self._portfolio['status'] == 'open' and
                    self._portfolio['position'] == 'long' and
                    self._portfolio['unit_price'] < price]['items'])

            total_short_items = \
                sum(self._portfolio[self._portfolio['status'] == 'open' and
                    self._portfolio['position'] == 'short' and
                    self._portfolio['unit_price'] > price]['items'])

            # Value when closing short and long positions
            value = (total_long_items - total_short_items) * price

            # Register close action
            if write:
                self._portfolio[
                    self._portfolio['status'] == 'open' and
                    self._portfolio['position'] == 'long' and
                    self._portfolio['unit_price'] < price]['status'] = 'close'

                self._portfolio[
                    self._portfolio['status'] == 'open' and
                    self._portfolio['position'] == 'short' and
                    self._portfolio['unit_price'] > price]['status'] = 'close'

        return value

    def _processHoldSignal(self, i_index):
        """
        Process a ``hold`` trading signal.

        Args:
            i_index (int): The integer index of the current simulation round.
                Refers to the index of all the DataFrames used in the
                simulation.
        """

        # Add portfolio row
        self._portfolio.iat[i_index] = ['none', 0, 0.0, 'none']

        # Total balance = balance + value if all positions are closed today
        value = self._closeOpenPositions(price=self._close_values.iat[i_index],
            force_all=True, write=False)

        self._simulation_data.iat[i_index] = [
            'hold', 'none', 0,
            self._simulation_data['balance'].iat[i_index - 1],
            self._close_values.iat[i_index],
            self._simulation_data['balance'].iat[i_index - 1] + value]

    def _processBuySignal(self, i_index):
        """
        Process a ``buy`` trading signal.

        Args:
            i_index (int): The integer index of the current simulation round.
                Refers to the index of all the DataFrames used in the
                simulation.
        """

        # Not enough balance for proceeding with the `buy` signal
        if ((self._max_investment is not None) and
                (self._simulation_data['balance'].iat[i_index] -
                 self._close_values.iat[i_index] +
                 self._max_investment < 0)):

            # Add portfolio row
            self._portfolio.iat[i_index] = ['none', 0, 0.0, 'none']

            # Total balance = balance + value if all positions are closed
            # today
            value = self._closeOpenPositions(
                price=self._close_values.iat[i_index],
                force_all=True, write=False)

            self._simulation_data.iat[i_index] = [
                'buy', 'none', 0,
                self._simulation_data['balance'].iat[i_index - 1],
                self._close_values.iat[i_index],
                self._simulation_data['balance'].iat[i_index - 1] + value]

        # Enough balance, proceed with opening a `long` position
        else:

            # Calculate number of stocks to be used in position
            if self._max_investment is not None:
                quantity = min(
                    self._max_items_per_transaction,
                    int((self._simulation_data['balance'].iat[i_index - 1] -
                         self._max_investment) /
                    self._close_values.iat[i_index]))
            else:
                quantity = self._max_items_per_transaction

            self._portfolio.iat[i_index] = [
                'long', quantity, self._close_values.iat[i_index], 'open']

            self._simulation_data.iat[i_index] = [
                'buy', 'open_long', quantity,
                self._simulation_data['balance'].iat[i_index - 1] - (
                        quantity * self._close_values.iat[i_index]),
                self._close_values.iat[i_index], 'N/A']

            # At the end to include this transaction also
            value = self._closeOpenPositions(
                price=self._close_values.iat[i_index],
                force_all=True, write=False)

            self._simulation_data['total_value'].iat[i_index] = \
                self._simulation_data['balance'].iat[i_index] + value

    def _processSellSignal(self, i_index):
        """
        Process a ``sell`` trading signal.

        Args:
            i_index (int): The integer index of the current simulation round.
                Refers to the index of all the DataFrames used in the
                simulation.
        """

        # Not enough balance for proceeding with the `sell` signal
        if ((self._max_investment is not None) and
                (self._simulation_data['balance'].iat[i_index] -
                 self._close_values.iat[i_index] +
                 self._max_investment < 0)):

            # Add portfolio row
            self._portfolio.iat[i_index] = ['none', 0, 0.0, 'none']

            # Total balance = balance + value if all positions are closed
            # today
            value = self._closeOpenPositions(
                price=self._close_values.iat[i_index],
                force_all=True, write=False)

            self._simulation_data.iat[i_index] = [
                'sell', 'none', 0,
                self._simulation_data['balance'].iat[i_index - 1],
                self._close_values.iat[i_index],
                self._simulation_data['balance'].iat[i_index - 1] + value]

        # Enough balance, proceed with opening a `short` position
        else:

            # Calculate number of stocks to be used in position
            if self._max_investment is not None:
                quantity = min(
                    self._max_items_per_transaction,
                    int((self._simulation_data['balance'].iat[i_index - 1] -
                         self._max_investment) /
                    self._close_values.iat[i_index]))
            else:
                quantity = self._max_items_per_transaction

            self._portfolio.iat[i_index] = [
                'short', quantity, self._close_values.iat[i_index], 'open']

            self._simulation_data.iat[i_index] = [
                'sell', 'open_short', quantity,
                self._simulation_data['balance'].iat[i_index - 1] + (
                        quantity * self._close_values.iat[i_index]),
                self._close_values.iat[i_index], 'N/A']

            # At the end to include this transaction also
            value = self._closeOpenPositions(
                price=self._close_values.iat[i_index],
                force_all=True, write=False)

            self._simulation_data['total_value'].iat[i_index] = \
                self._simulation_data['balance'].iat[i_index] + value

    def runSimulationRound(self, i_index, signal):
        """
        Executes a simulation round based on given signal.

        Args:
            i_index (int): The integer index of the current simulation round.
                Refers to the index of all the DataFrames used in the
                simulation.

            signal ({('hold', 0), ('buy', -1), ('sell', 1)} or None): The
                signal to be considered in this simulation round.
        """

        # Just initializations at the first day
        if i_index == 0:
            self._simulation_data.iat[0] = ['hold', 'none', 0, 0.0, 0.0, 0.0]
            self._portfolio.iat[0] = ['none', 0, 0.0, 'none']
            return None

        if signal == TRADE_SIGNALS['buy']:
            self._processBuySignal(i_index)

        elif signal == TRADE_SIGNALS['sell']:
            self._processSellSignal(i_index)

        else:
            self._processHoldSignal(i_index)

    def closeSimulation(self):
        """
        Closes this simulation and returns simulation data and statistics.

        Returns:
            (pandas.DataFrame, dict): Dataframe which holds details and
            dictionary which holds statistics about the simulation.

            The index of the dataframe is the whole trading period
            (DateTimeIndex).Columns are:

            ``signal``: the signal produced at each day of the simulation
            period.

            ``trading_action``: the trading action applied. Possible values are
            ``open_long``, ``close_long``, ``open_short``, ``close_short`` and
            ``none``.

            ``stocks_in_transaction``: the number of stocks involved in a
            trading_action.

            ``balance``: the available balance (earnings - spending).

            ``stock_value``: The value of the stock during the simulation
            period.

            ``total_value``: the available balance considering the open
            positions (if they should be closed in this transaction).

            The dictionary contains the below keys:

            ``number_of_trading_days``: the number of trading days in the
            simulation round.

            ``number_of_buy_signals``: the number of ``buy`` signals produced
            during the simulation period.

            ``number_of_ignored_buy_signals``: the number of ``buy`` signals
            ignored because of the ``max_investment`` limitation.

            ``number_of_sell_signals``: the number of ``sell`` signals produced
            during the simulation period.

            ``number_of_ignored_sell_signals``: the number of ``sell`` signals
            ignored because of the ``max_investment`` limitation.

            ``balance``: the final available balance (earnings - spending).

            ``total_stocks_in_long``: the number of stocks in long position at
            the end of the simulation.

            ``total_stocks_in_short``: the number of stocks in short position
            at the end of the simulation.

            ``stock_value``: The value of the stock at the end of the
            simulation.

            ``total_value``: The balance plus after closing all the open
            positions.
        """

        self._calculateSimulationStatistics()

        return self._simulation_data, self._statistics