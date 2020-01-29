#!/usr/bin/env python
# coding: utf-8

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import minmax_scale

from btp.finance import get_fee


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


def plot_orders(buys, sells, data):
    plt.plot(data['Open time'], data['Open'], linestyle='--', label='price', color='0.5', markersize=1)
    plt.scatter(buys['Open time'], buys['Price'], marker='^', label='buy', color='red')
    plt.scatter(sells['Open time'], sells['Price'], marker='v', label='sell', color='green')

    plt.legend()
    plt.show()


def summary_orders(buys, sells, data):
    buy_amount = 100  # $
    sell_amount = 100  # $
    asset_profit, currency_profit = get_wallet_profit(buy_amount, buys, sell_amount, sells)
    print('WALLET: {} buys and {} sells: {:.3f} ASS, {:.3f} $'.format(len(buys), len(sells), asset_profit,
                                                                      currency_profit))

    asset_final_valuation = asset_profit * data['Open'].tolist()[-1] if asset_profit > 0 else 0
    total_profit = asset_final_valuation + currency_profit
    rel_profit = total_profit / (len(buys) * buy_amount)
    print('END: {:.3f} $ ({:.3f}%)'.format(total_profit, rel_profit))
