"""
Trading-Technical-Indicators (tti) python library

File name: test_indicators_common.py
    tti.indicators package, Abstract class for common unit tests applicable for
    all the indicators.
"""

from abc import ABC, abstractmethod

import pandas as pd
import matplotlib.pyplot as plt

from tti.utils.exceptions import NotEnoughInputData, \
    WrongTypeForInputParameter, WrongValueForInputParameter, \
    NotValidInputDataForSimulation


class TestIndicatorsCommon(ABC):

    # Definition of the abstract methods and properties
    @abstractmethod
    def assertRaises(self, *kwargs):
        raise NotImplementedError

    @abstractmethod
    def subTest(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def assertEqual(self, *kwargs):
        raise NotImplementedError

    @abstractmethod
    def assertIn(self, *kwargs):
        raise NotImplementedError

    @property
    @abstractmethod
    def indicator(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def indicator_input_arguments(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def indicator_other_input_arguments(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def indicator_minimum_required_data(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def graph_file_name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def indicator_test_data_file_name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def mandatory_arguments_missing_cases(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def arguments_wrong_type(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def arguments_wrong_value(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def required_input_data_columns(self):
        raise NotImplementedError

    precision = 4

    # Unit Tests

    # Validate indicators input arguments

    def test_mandatory_input_arguments_missing(self):
        for arguments_set in self.mandatory_arguments_missing_cases:
            with self.subTest(arguments_set=arguments_set):
                with self.assertRaises(TypeError):
                    self.indicator(**arguments_set)

    def test_input_arguments_wrong_type(self):
        for arguments_set in self.arguments_wrong_type:
            with self.subTest(arguments_set=arguments_set):
                with self.assertRaises(WrongTypeForInputParameter):
                    self.indicator(**arguments_set)

    def test_input_arguments_wrong_value(self):
        for arguments_set in self.arguments_wrong_value:
            with self.subTest(arguments_set=arguments_set):
                with self.assertRaises(WrongValueForInputParameter):
                    self.indicator(**arguments_set)

    # Validate input argument: input_data

    def test_argument_input_data_wrong_index_type(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=1)

        with self.assertRaises(TypeError):
            self.indicator(df)

    def test_argument_input_data_required_column_missing(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        for missing_column in self.required_input_data_columns:
            with self.subTest(
                    missing_column=missing_column):
                with self.assertRaises(ValueError):
                    self.indicator(pd.DataFrame(
                        df.drop(columns=[missing_column])))

    def test_argument_input_data_values_wrong_type(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        df.iloc[0, :] = 'no-numeric'

        with self.assertRaises(ValueError):
            self.indicator(df)

    def test_argument_input_data_empty(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        with self.assertRaises(ValueError):
            self.indicator(pd.DataFrame(df[df.index >= '2032-01-01']))

    # Validate input argument: fill_missing_values

    def test_argument_fill_missing_values_is_true(self):
        df = pd.read_csv('./data/missing_values_data.csv', parse_dates=True,
                         index_col=0)

        df_expected_result = pd.read_csv(
            './data/missing_values_filled.csv', parse_dates=True, index_col=0
        )[self.required_input_data_columns].round(self.precision)

        df_result = self.indicator(
            df, fill_missing_values=True, **self.indicator_input_arguments
        )._input_data[self.required_input_data_columns]

        pd.testing.assert_frame_equal(df_result, df_expected_result)

    def test_argument_fill_missing_values_is_false(self):
        df = pd.read_csv('./data/missing_values_data.csv', parse_dates=True,
                         index_col=0)

        df_expected_result = pd.read_csv(
            './data/missing_values_data_sorted.csv', parse_dates=True,
            index_col=0)[self.required_input_data_columns].round(
            self.precision)

        df_result = self.indicator(
            df, fill_missing_values=False, **self.indicator_input_arguments
        )._input_data[self.required_input_data_columns]

        pd.testing.assert_frame_equal(df_result, df_expected_result)

    def test_argument_fill_missing_values_is_default_true(self):
        df = pd.read_csv('./data/missing_values_data.csv', parse_dates=True,
                         index_col=0)

        df_expected_result = pd.read_csv(
            './data/missing_values_filled.csv', parse_dates=True, index_col=0
        )[self.required_input_data_columns].round(self.precision)

        df_result = self.indicator(
            df, **self.indicator_input_arguments
        )._input_data[self.required_input_data_columns]

        pd.testing.assert_frame_equal(df_result, df_expected_result)

    # Validate indicator creation

    def test_validate_indicator_input_data_one_row(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        if self.indicator_minimum_required_data > 1:
            with self.assertRaises(NotEnoughInputData):
                self.indicator(df[df.index == '2000-02-01'])
        else:
            self.indicator(df[df.index == '2000-02-01'])

    def test_validate_indicator_less_than_required_input_data(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        if self.indicator_minimum_required_data != 1:
            with self.assertRaises(NotEnoughInputData):
                self.indicator(
                    df.iloc[:self.indicator_minimum_required_data - 1],
                    **self.indicator_input_arguments)
        else:
            pass

    def test_validate_indicator_exactly_required_input_data(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        self.indicator(df.iloc[:self.indicator_minimum_required_data],
            **self.indicator_input_arguments)

    def test_validate_indicator_full_data(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        df_expected_result = pd.read_csv(self.indicator_test_data_file_name,
            parse_dates=True, index_col=0).round(self.precision)

        df_result = self.indicator(
            df, **self.indicator_input_arguments)._ti_data

        pd.testing.assert_frame_equal(df_expected_result, df_result,
                                      check_dtype=False)

    def test_validate_indicator_full_data_default_arguments(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        self.indicator(df)

    def test_validate_indicator_full_data_other_arguments_values(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        for arguments_set in self.indicator_other_input_arguments:
            with self.subTest(arguments_set=arguments_set):
                self.indicator(df, **arguments_set)

    # Validate API

    def test_getTiGraph(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        indicator = self.indicator(df, **self.indicator_input_arguments)

        # Needs manual check of the produced graph
        self.assertEqual(indicator.getTiGraph(), plt)

        indicator.getTiGraph().savefig(self.graph_file_name)
        plt.close('all')

    def test_getTiData(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        df_expected_result = pd.read_csv(self.indicator_test_data_file_name,
            parse_dates=True, index_col=0).round(self.precision)

        pd.testing.assert_frame_equal(
            df_expected_result,
            self.indicator(df, **self.indicator_input_arguments).getTiData(),
            check_dtype=False)

    def test_getTiValue_specific(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        df_expected_result = pd.read_csv(self.indicator_test_data_file_name,
            parse_dates=True, index_col=0).round(self.precision)

        self.assertEqual(list(df_expected_result.loc['2009-10-19', :]),
            self.indicator(df, **self.indicator_input_arguments).
                         getTiValue('2009-10-19'))

    def test_getTiValue_latest(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        df_expected_result = pd.read_csv(self.indicator_test_data_file_name,
            parse_dates=True, index_col=0).round(self.precision)

        self.assertEqual(list(df_expected_result.iloc[-1]), self.indicator(df,
            **self.indicator_input_arguments).getTiValue())

    def test_getTiSignal(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        self.assertIn(self.indicator(
            df, **self.indicator_input_arguments).getTiSignal(),
                      [('buy', -1), ('hold', 0), ('sell', 1)])

    def test_getTiSignal_minimum_required_data(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        self.assertIn(
            self.indicator(df.iloc[:self.indicator_minimum_required_data],
                           **self.indicator_input_arguments).getTiSignal(),
            [('buy', -1), ('hold', 0), ('sell', 1)])

    def test_simulation_close_values_no_dataframe(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
            index_col=0)

        with self.assertRaises(NotValidInputDataForSimulation):
            self.indicator(df[df.index >= '2011-09-12'],
                **self.indicator_input_arguments).runSimulation(
                close_values='NO_DF')

    def test_simulation_close_values_missing_close_column(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        with self.assertRaises(NotValidInputDataForSimulation):
            self.indicator(df[df.index >= '2011-09-12'],
                **self.indicator_input_arguments).runSimulation(
                close_values=df[df.index >= '2011-09-12'].drop(
                    columns=['close']))

    def test_simulation_close_values_not_valid_index_data(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        with self.assertRaises(NotValidInputDataForSimulation):
            self.indicator(df[df.index >= '2011-09-12'],
                **self.indicator_input_arguments).runSimulation(
                close_values=df)

    def test_simulation_max_pieces_per_buy_wrong_type(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        with self.assertRaises(WrongTypeForInputParameter):
            self.indicator(df[df.index >= '2011-09-12'],
                **self.indicator_input_arguments).runSimulation(
                close_values=df[df.index >= '2011-09-12'],
                max_pieces_per_buy='1')

    def test_simulation_max_pieces_per_buy_wrong_value_0(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        with self.assertRaises(WrongValueForInputParameter):
            self.indicator(df[df.index >= '2011-09-12'],
                **self.indicator_input_arguments).runSimulation(
                close_values=df[df.index >= '2011-09-12'],
                max_pieces_per_buy=0)

    def test_simulation_max_pieces_per_buy_wrong_value_negative(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        with self.assertRaises(WrongValueForInputParameter):
            self.indicator(df[df.index >= '2011-09-12'],
                **self.indicator_input_arguments).runSimulation(
                close_values=df[df.index >= '2011-09-12'],
                max_pieces_per_buy=-1)

    def test_simulation_commission_wrong_type(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        with self.assertRaises(WrongTypeForInputParameter):
            self.indicator(df[df.index >= '2011-09-12'],
                **self.indicator_input_arguments).runSimulation(
                close_values=df[df.index >= '2011-09-12'], commission='0.05')

    def test_simulation_commission_wrong_value_negative(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        with self.assertRaises(WrongValueForInputParameter):
            self.indicator(df[df.index >= '2011-09-12'],
                **self.indicator_input_arguments).runSimulation(
                close_values=df[df.index >= '2011-09-12'], commission=-0.05)

    def test_simulation_success(self):
        df = pd.read_csv('./data/sample_data.csv', parse_dates=True,
                         index_col=0)

        indicator = self.indicator(df[df.index >= '2011-09-12'],
            **self.indicator_input_arguments)

        simulation, statistics = indicator.runSimulation(
            close_values=df[df.index >= '2011-09-12'])

        with self.subTest(sub_test_name='simulation DataFrame structure'):

            self.assertListEqual(list(simulation.columns), ['signal',
                'stocks_in_transaction', 'stocks_in_possession', 'balance',
                'total_value'])

        with self.subTest(sub_test_name='simulation DataFrame index'):
            self.assertEqual(simulation.index.equals(
                indicator.getTiData().index), True)

        with self.subTest(sub_test_name='statistics dictionary structure'):
            self.assertListEqual(list(statistics.keys()),
                ['number_of_trading_days', 'number_of_buy_signals',
                'number_of_sell_signals', 'number_of_ignored_sell_signals',
                'balance', 'stocks_in_possession', 'stock_value',
                 'total_value'])

        with self.subTest(sub_test_name='statistics has valid data'):
            self.assertEqual(simulation.isnull().values.any(), False)

        with self.subTest(sub_test_name='statistics values'):
            self.assertEqual(statistics['number_of_trading_days'],
                             len(indicator.getTiData().index))

            self.assertIsInstance(statistics['number_of_buy_signals'], int)
            self.assertIsInstance(statistics['number_of_sell_signals'], int)
            self.assertIsInstance(statistics['number_of_ignored_sell_signals'],
                                  int)
            self.assertIsInstance(statistics['balance'], (int, float))
            self.assertIsInstance(statistics['stocks_in_possession'], int)
            self.assertIsInstance(statistics['stock_value'], (int, float))
            self.assertIsInstance(statistics['total_value'], (int, float))



