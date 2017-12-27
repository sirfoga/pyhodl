# How to import your transactions

## General overview
APIs are hooks that apps use to interface with other apps. `pyhodl` needs just read access to your exchanges APIs. `pyhodl` does not hold your keys, rather it saves them in your local machine, so be sure to keep it virus-free. `pyhodl` needs a config file to save your data, so just run `pyhodl -updater` once and follow the instructions to setup your workplace.

## Supported exchanges

- [Binance](#binance)
- [Bitfinex](#bitfinex)
- [Coinbase](#coinbase)
- [GDAX](#gdax)

## Binance

0. Log in into your Binance account and navigate to the [Security Settings page](https://binance.com)
0. Click on `API Settings` and create a new key
0. Check only the `Read Info` permission
0. Save your `key` and your `secret` in your config file

## Bitfinex

0. Log in into your Bitfinex account and navigate to [Account -> API](https://www.bitfinex.com/api)
0. Create a new key
0. Select all Read boxes (should be selected by default) and do not select any Write boxes.
0. Label the API Key and generate it.
0. Save your `key` and your `secret` in your config file

## Coinbase

0. Log in into your Coinbase account and navigate to [Settings -> API Access](https://www.coinbase.com/settings/api)
0. Click on `+ New API Key` to create a new key
0. Enable all accounts you would like to check (we recommend to check all)
0. Enable all checkboxes with a read permission
0. Save your `key` and your `secret` in your config file


## GDAX

0. Log in into your GDAX account, hover the navigation icon and click on [API](https://www.gdax.com/settings/api)
0. Enable only View
0. Save your `key`, `secret` and `passphrase` in your config file
