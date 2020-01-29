#!/usr/bin/env python
# coding: utf-8


# download some coins data from binance
#   summary of stats (e.g variance, mean, mean return ...)
#   develop strategy
#   backtest
# deploy
# profit

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from binance.client import Client

from sklearn import svm

TICKER = 'TRXBNB'
START_TICKER = '2020-01-01'
END_TICKER = '2020-01-26'
TICKER_INTERVAL = Client.KLINE_INTERVAL_1MINUTE


def get_strategy(data, n, m, reg):
    predictions = []

    for i in range(n, len(data) - m):  # need at least n samples
        available_data = data['Open'][i - n: i]

        prediction = reg.predict([available_data])[0]
        prediction_time = data['Open time'][i + m]
        predictions.append((prediction_time, prediction))

        true_val = data['Open'][i + m]
        rel_error = abs(true_val - prediction) / abs(true_val)
        perc_error = rel_error * 100.0
        print('predicted {}/{} e: {:.3f}%'.format(i, len(data) - m, perc_error))

    return pd.DataFrame(predictions, columns=['Open time', 'Predict'])


def get_wallet_profit(buy_amount, buys, sell_amount, sells):
    """ const amount of buy/sell """

    # todo
    # buys = buys.rename(columns={'Price': 'Buy'})
    # sells = sells.rename(columns={'Price': 'Sell'})
    # orders = pd.merge(buys, sells, on='Open time')

    # buys
    amount_spent = 0
    asset_bought = 0
    for _, buy in buys.iterrows():
        amount = buy_amount / buy['Price']
        asset_bought += amount
        amount_spent += amount * buy['Price'] + get_fee(buy['Price'])

    # sells
    asset_sold = 0
    amount_gained = 0
    for _, sell in sells.iterrows():
        amount = sell_amount / sell['Price']
        asset_sold += amount
        amount_gained += amount * sell['Price'] - get_fee(sell['Price'])

    asset_profit = asset_bought - asset_sold
    currency_profit = amount_gained - amount_spent
    return asset_profit, currency_profit


def do_strategy(n, m, data, model):
    buys = []
    sells = []

    for i in range(n, len(data) - m):  # need at least n samples
        available_data = data['Open'][i - n: i]
        available_data = minmax_scale(available_data)  # scale
        current_val = data['Open'][i]

        prediction = model.predict([available_data])[0]  # predicted difference between now and future
        prediction_time = data['Open time'][i]
        if prediction > 0:
            buys.append((prediction_time, current_val))
        elif prediction < 0:
            sells.append((prediction_time, current_val))

    buys = pd.DataFrame(buys, columns=['Open time', 'Price'])
    sells = pd.DataFrame(sells, columns=['Open time', 'Price'])

    return buys, sells


def plot_strategy(buys, sells, data):
    plt.plot(data['Open time'], data['Open'], linestyle='--', label='price', color='0.5', markersize=1)
    plt.scatter(buys['Open time'], buys['Price'], marker='^', label='buy', color='red')
    plt.scatter(sells['Open time'], sells['Price'], marker='v', label='sell', color='green')

    plt.legend()
    plt.show()


def strategy_summary(buys, sells, data):
    buy_amount = 100  # $
    sell_amount = 100  # $
    asset_profit, currency_profit = get_wallet_profit(buy_amount, buys, sell_amount, sells)
    print('WALLET: {} buys and {} sells: {:.3f} ASS, {:.3f} $'.format(len(buys), len(sells), asset_profit,
                                                                      currency_profit))

    asset_final_valuation = asset_profit * data['Open'].tolist()[-1] if asset_profit > 0 else 0
    total_profit = asset_final_valuation + currency_profit
    rel_profit = total_profit / (len(buys) * buy_amount)
    print('END: {:.3f} $ ({:.3f}%)'.format(total_profit, rel_profit))


def main():
    # load dataset
    data = get_klines(TICKER, TICKER_INTERVAL, START_TICKER, END_TICKER)

    # parse
    data = pd.DataFrame(data, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
                                       'Quote asset volume',
                                       'Number of trades', 'Taker buy base asset volume',
                                       'Taker buy quote asset volume',
                                       'Ignore'])
    for column in data.columns:
        data[column] = data[column].astype(np.float64)
    data['Open time'] = pd.to_datetime(data['Open time'], unit='ms')

    # model data
    n = 24 * 60  # available time frame
    m = 6 * 60  # next time frame
    n_train_samples = 10000
    n_test_samples = 100

    # train model
    model = train_model(data, n, m, n_train_samples, svm.SVC(C=1000.0).fit)
    s = score_model(data, n, m, n_test_samples, model)
    print('SCORE: {:.3f}'.format(s))  # scoring

    # predict
    buys, sells = do_strategy(n, m, data, model)

    # summary
    strategy_summary(buys, sells, data)
    # plot_strategy(n, m, data, model)


if __name__ == '__main__':
    main()
