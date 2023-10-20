# Importing Libraries
import pandas as pd
import ta
import numpy as np
import matplotlib.pyplot as plt
import random
import itertools
import numpy as np
import progressbar
import yfinance as yf


"""
Read and Clean Data
"""
def data_reader(data_path='rsi_bb_candlestick_stra\data\EURUSD_Data.csv'):
    # Read CSV file into DataFrame df
    df = pd.read_csv(data_path, index_col='time', parse_dates=True)
    df.index.name = 'Date'

    # Making main error
    if 'close' not in df.columns :
        ValueError("We Have Necessary Need For Close Price")

    # Data Quality Test
    df.dropna(thresh=4)

    # Show dataframe
    df.head()

    # Creating summary df
    smry_df = df[['open', 'close', 'high', 'low']]

    # set option
    pd.options.mode.chained_assignment = None

    return smry_df


"""
Make strategy function
"""

def my_stra(smry_df, n_sl, rsi_per, bb_per, stdev, tp_method, ror, overbuy, oversell) :

    # Calculate rsi column with Period 13
    smry_df['rsi'] = ta.momentum.RSIIndicator(smry_df['close'],window=13).rsi()

    # Calculate BollingerBands Indicator With Period 30 And StDev 2
    bb_handler = ta.volatility.BollingerBands(close=smry_df['close'], window=bb_per, window_dev=stdev)
    smry_df['h_band'] = bb_handler.bollinger_hband()
    smry_df['m_band'] = bb_handler.bollinger_mavg()
    smry_df['l_band'] = bb_handler.bollinger_lband()



    # Handling Warnings

    # Making Stop Loss Data
    smry_df['n_high_swing'] = smry_df['high'].rolling(n_sl).max()
    smry_df['n_low_swing'] = smry_df['low'].rolling(n_sl).min()

    # Long Position Signals

    smry_df['flag_long'] = np.nan
    smry_df['signal_long'] = np.nan
    smry_df['long_sl_dis'] = np.nan


    # Buy Conditions When RSI < 25 And Price Toch Lower Band
    smry_df.loc[(smry_df['rsi'] < oversell ) & (smry_df['close'] < smry_df['l_band'] ),'flag_long'] = 1

    smry_df.loc[(smry_df['flag_long'].fillna(method='ffill') == 1 ) & (smry_df['close'] > smry_df['open']) &\
         (smry_df['low'] < smry_df['l_band']) & (smry_df['close'] > smry_df['l_band'])  ,'signal_long'] = 1

    smry_df.loc[(smry_df['signal_long'] == 1 ) ,'long_sl_dis'] = smry_df['close'] - smry_df['n_low_swing']
    smry_df.loc[(smry_df['signal_long'] == 1 ),'long_price'] = smry_df['close']


    # Closing True Buy Position With Middle BB LINE
    if tp_method == 'mbb' :
        smry_df.loc[ (smry_df['high'] >= smry_df['m_band'] ),'signal_long'] = 0

    # Closing True Buy Position With ROR
    elif tp_method == 'ror' :
        smry_df.loc[ ( (smry_df['close'] - smry_df['long_price'].fillna(method='ffill')) >=\
             (smry_df['long_sl_dis'].fillna(method='ffill') * ror) ),'signal_long'] = 0

    else:
        print('Your Methode Is Wrong')

    # Closing False Buy Position With Previous N Candles Swing Stop Loss
    smry_df.loc[(smry_df['close'] < smry_df['n_low_swing'] ) ,'signal_long'] = 0

    # Short Position Signals
    smry_df['flag_short'] = np.nan
    smry_df['signal_short'] = np.nan
    smry_df['short_sl_dis'] = np.nan

    # Sell Conditions When RSI > 75 And Price Toch Higher Band
    smry_df.loc[(smry_df['rsi'] > overbuy ) & (smry_df['close'] > smry_df['h_band'] ),'flag_short'] = -1

    smry_df.loc[(smry_df['flag_short'].fillna(method='ffill') == -1 ) & (smry_df['close'] < smry_df['open']) &\
         (smry_df['high'] > smry_df['h_band']) & (smry_df['close'] < smry_df['h_band'])  ,'signal_short'] = -1

    smry_df.loc[(smry_df['signal_short'] == -1 ) ,'short_sl_dis'] =  smry_df['n_high_swing'] - smry_df['close']

    smry_df.loc[(smry_df['signal_short'] == -1 ),'short_price'] = smry_df['close']

    # Closing True Sell Position With Middle BB LINE
    if tp_method == 'mbb' :
        smry_df.loc[ (smry_df['low'] <= smry_df['m_band'] ),'signal_short'] = 0

    # Closing True Sell Position With ROR
    elif tp_method == 'ror' :
        smry_df.loc[ ( ( smry_df['short_price'].fillna(method='ffill') - smry_df['close'] ) >= (smry_df['short_sl_dis'].fillna(method='ffill') * ror) ),'signal_short'] = 0
    else:
        print('Your Methode Is Wrong')

    # Closing False Sell Position With Previous N Candles Swing Stop Loss
    smry_df.loc[(smry_df['close'] > smry_df['n_high_swing'] ) ,'signal_short'] = 0

    # Set Position 
    smry_df['position'] = ( smry_df['signal_short'].fillna(method='ffill') + smry_df['signal_long'].fillna(method='ffill') )

    # profit of position
    smry_df['pct'] = smry_df['close'].pct_change(1)
    smry_df['return'] = smry_df['pct'] * (smry_df['position'].shift(1))
    smry_df['equity'] = smry_df['return'].cumsum()
    equity_percent = round(smry_df['equity'][-1] * 100, 2)

    return equity_percent


"""
a simple strategy optimization function (very slow)
* we can use other best optimization methods like genetic algorithm or particle swarm optimization
"""

def optimize_stra(smry_df):
    # set range of each parameter
    all_n_sl = list(range(1,30,2))
    all_rsi_per = list(range(5,30,2))
    all_bb_per = list(range(10,30,2))
    all_stdev = list(range(1,5,1))
    all_tp_method = ['ror' , 'mbb']
    all_ror = list(np.arange(1,5,0.3))
    all_overbuy = list(range(60,90,5))
    all_oversell = list(range(10,40,5))

    # combining all lists for finding all states
    combined_list = list(itertools.product(all_n_sl , all_rsi_per , all_bb_per , all_stdev , all_tp_method , all_ror , all_overbuy , all_oversell))
    states_len = len(combined_list)
    print('states len is : ' , states_len , 'states')

    # randomizing states for finding best faster
    random.shuffle(combined_list)

    # finding maximum of equaty
    max_equ = -1000000
    max_params = {}

    # make progress bar
    bar = progressbar.ProgressBar(max_value=states_len)

    for idx,states in enumerate(combined_list):

        equ = my_stra(smry_df, states[0] , states[1] , states[2] ,states[3] ,states[4] , states[5] ,states[6] , states[7])
        
        # update bars
        bar.update(idx)

        if equ > max_equ :
            max_equ = equ
            max_params['n_sl'] = states[0]
            max_params['rsi_per'] = states[1]
            max_params['bb_per'] = states[2]
            max_params['stdev'] = states[3]
            max_params['tp_method'] = states[4]
            max_params['ror'] = states[5]
            max_params['all_overbuy'] = states[6]
            max_params['all_oversell'] = states[7]

            print('better equ is founded')
            print('max_equ is : ' , max_equ , 'with params : \n' , max_params)

    print(max_equ , max_params)
    return max_equ , max_params
    

"""
Is it good in new data ?
"""

def new_data_reader(symbol="EURUSD=X", start='2022-05-07', interval='1h'):

    # Read from yf
    df = yf.download(tickers=symbol, start=start, interval=interval)

    # Data quality test
    df.dropna(thresh=4)

    # Creating summary df
    smry_df = pd.DataFrame()
    smry_df[['open','close' , 'high' , 'low']] = df[['Open','Adj Close' , 'High' , 'Low']]

    # set option
    pd.options.mode.chained_assignment = None

    return smry_df

"""
one of the best settings for this strategy is :
"""

def an_example(smry_df):
    end_equity = my_stra(smry_df, n_sl=26, rsi_per=10, bb_per=25, stdev=1,\
                         tp_method='mbb', ror=1, overbuy=70, oversell=20)

    print("The capital growth percentage after this investment is : ", end_equity)


if __name__ == "__main__":
    smry_df = new_data_reader()
    an_example(smry_df)
    # max_equ , max_params = optimize_stra(smry_df)