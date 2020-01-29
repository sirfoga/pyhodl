#!/usr/bin/env python
# coding: utf-8

import json
import pathlib

from binance import helpers

DATA_FOLDER = pathlib.Path('/home/stefano/.local/bin/jh/_notebooks/binance-data')
FILE_FORMATTER = 'Binance_{}_{}_{}-{}.json'
SYMBOLS = [
    'BTCUSDT',
    'ETHUSDT',
    'ETHBTC',
    'LTCUSDT',
    'LTCBNB',
    'LTCBTC',
    'LTCETH',
    'EOSUSDT',
    'EOSBNB',
    'EOSBTC',
    'EOSETH',
    'BNBUSDT',
    'BNBBTC',
    'BNBETH',
    'TRXUSDT',
    'TRXBTC',
    'TRXBNB',
    'TRXETH',
    'IOTAUSDT',
    'IOTABTC',
    'IOTAETH',
    'IOTABNB',
    'VETUSDT',
    'VETBTC',
    'VETBNB',
    'VETETH',
    'BATUSDT',
    'BATBNB',
    'BATETH',
    'BATBTC',
    'QTUMUSDT',
    'QTUMETH',
    'QTUMBNB',
    'QTUMBTC',
    'OMGUSDT',
    'OMGBTC',
    'OMGETH',
    'OMGBNB',
    'LSKBNB',
    'LSKETH',
    'LSKBTC',
    'ENJUSDT',
    'ENJBTC',
    'ENJETH',
    'ENJBNB',
    'XVGBTC',
    'XVGETH',
    'STEEMBTC',
    'STEEMBNB',
    'STEEMETH',
    'GNTBTC',
    'GNTETH'
]


def get_klines(symbol, interval, start, end, folder=DATA_FOLDER):
    in_f = FILE_FORMATTER.format(
        symbol,
        interval,
        helpers.date_to_milliseconds(start),
        helpers.date_to_milliseconds(end)
    )
    in_f = DATA_FOLDER / in_f
    with open(in_f) as json_file:
        klines = json.load(json_file)
        return klines


def get_data(ticker, ticker_interval, start_ticker, end_ticker):
    # load dataset
    data = get_klines(ticker, ticker_interval, start_ticker, end_ticker)

    # parse
    data = pd.DataFrame(data, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
                                       'Quote asset volume',
                                       'Number of trades', 'Taker buy base asset volume',
                                       'Taker buy quote asset volume',
                                       'Ignore'])
    for column in data.columns:
        data[column] = data[column].astype(np.float64)
    data['Open time'] = pd.to_datetime(data['Open time'], unit='ms')
