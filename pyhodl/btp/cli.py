#!/usr/bin/env python
# coding: utf-8


# download some coins data from binance
#   summary of stats (e.g variance, mean, mean return ...)
#   develop strategy
#   backtest
# deploy
# profit

from binance.client import Client
from sklearn import svm

from btp.ai import train_model, score_model
from btp.data import get_data
from btp.wallet import do_strategy, summary_orders


def main():
    # data we want to work on
    ticker = 'TRXBNB'
    start_ticker = '2020-01-01'
    end_ticker = '2020-01-26'
    ticker_interval = Client.KLINE_INTERVAL_1MINUTE
    data = get_data(ticker, ticker_interval, start_ticker, end_ticker)

    # train model
    n = 24 * 60  # available time frame
    m = 6 * 60  # next time frame
    n_train_samples = 10000
    n_test_samples = 100
    model = train_model(data, n, m, n_train_samples, svm.SVC(C=1000.0).fit)
    s = score_model(data, n, m, n_test_samples, model)
    print('SCORE: {:.3f}'.format(s))  # scoring

    # deploy
    buys, sells = do_strategy(n, m, data, model)

    # summary
    summary_orders(buys, sells, data)
    # plot_orders(buys, sells, data)


if __name__ == '__main__':
    main()
