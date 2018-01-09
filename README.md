# Pyhodl

> Download, update, analyze and plot your crypto-transactions. Completely off-line and secure (you own your data). Made with love and crypto money.

[![Build Status](https://travis-ci.org/sirfoga/pyhodl.svg?branch=master)](https://travis-ci.org/sirfoga/pyhodl) [![CircleCI](https://circleci.com/gh/sirfoga/pyhodl.png)](https://circleci.com/gh/sirfoga/pyhodl) ![Python version](https://img.shields.io/badge/Python-3.5-blue.svg) 

[![Code Health](https://landscape.io/github/sirfoga/pyhodl/master/landscape.svg?style=flat)](https://landscape.io/github/sirfoga/pyhodl/master) 
[![BCH compliance](https://bettercodehub.com/edge/badge/sirfoga/pyhodl?branch=master)](https://bettercodehub.com/) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/1eff18395a134c9aa2d829fcb1f124bf)](https://www.codacy.com/app/sirfoga/pyhodl?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=sirfoga/pyhodl&amp;utm_campaign=Badge_Grade) [![Code Climate](https://lima.codeclimate.com/github/sirfoga/pyhodl/badges/gpa.svg)](https://codeclimate.com/github/sirfoga/pyhodl) ![pylint Score](https://mperlet.de/pybadge/badges/9.88.svg)

[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/1544/badge)](https://bestpractices.coreinfrastructure.org/projects/1544)

## Table of content

- [Key Features](#key-features)
- [Usage](#usage)
- [Example](#example)
- [Install](#install)
- [Changelog](#changelog)
- [Contribute](#contribute)
- [License](#license)
- [Links](#links)
- [You may also like...](#you-may-also-like)

## Key Features

* continuous (hourly, daily, you-decide-when) updates from your exchanges
* completely off-line
* **you** own your data
* analyze profit and ROI of transactions
* plot charts (buy/sells, prices, market cap ...)
* stats and trends
* cross-OS
* supported exchanges:
    - Binance
    - Bitfinex
    - Coinbase
    - GDAX
    
## Usage

```bash
$ pyhodl [options]
```
To specify your settings, please refer to [this](WRITE_CONFIGS.md).
To import your transactions, please refer to [the guide](IMPORT_DATA.md).

### Supported commands

The following flags are supported:

| Flag | Description | Allowed attributes |
| --- | --- | --- |
| `-h` | show this help message and exit | None |
| `-m` | Choose run mode | `{plotter,stats,download,update}` |
| `-p` | Path to use as input | any OS existent path |
| `-t` | Connect to tor via this password (advanced) | any string |
| `-v` | Increase verbosity | nothing, just add `-v` |


## Example
A simple run with parameters like
```bash
pyhodl -plot "~/.pyhodl/data/BitfinexUpdater.json" -verbose
```
would result in a plot like this one:
![Example bitfinex](extra/buy_sells.jpg)

while if you want to plot your gains against your total spent, just run
```bash
-plot -verbose
```
![Example bitfinex](extra/crypto_fiat_balance.jpg)


### Documentation
If you want to browse the full documentation please go [here](https://sirfoga.github.io/pyhodl/), or clone [the repo](https://github.com/sirfoga/pyhodl) and navigate to the [index file](docs/index.html).


### API example
To show how simple it is, take a look at the code on how to produce the chart of the example:

```python
wallets = exchange.build_wallets().values()  # get wallets
plotter = FiatPlotter(wallets)  # setup plot
plotter.plot_buy_sells("XRP")  # plot buy/sells data
```


## Install
Just run `./install.sh` and test your installation with `pyhodl -h`. Should come out
```bash
usage: -[mode] -h/--help for full usage

optional arguments:
  -h, --help            show this help message and exit
  -m {plotter,stats,download,update}, --mode {plotter,stats,download,update}
                        Run mode
  -p PATH, --path PATH  Path to use as input
  -t TOR, --tor TOR     Connect to tor via this password (advanced)
  -v, --verbose         Increase verbosity
```
To run the tests (please do):
```bash
python3 setup.py test
```

## Changelog
See [CHANGELOG](https://github.com/sirfoga/pyhodl/blob/master/CHANGELOG.md)

## Contribute

[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/sirfoga/pyhodl/issues) [![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://opensource.org/licenses/Apache-2.0)

0. [Open an issue](https://github.com/sirfoga/pyhodl/issues/new)
0. [fork](https://github.com/sirfoga/pyhodl/fork) this repository
0. create your feature branch (`git checkout -b my-new-feature`)
0. commit your changes (`git commit -am 'Added my new feature'`)
0. publish the branch (`git push origin my-new-feature`)
0. [open a PR](https://github.com/sirfoga/pyhodl/compare)

## License

[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bhttps%3A%2F%2Fgithub.com%2Fsirfoga%2Fpyhodl.svg?type=shield)](https://app.fossa.io/projects/git%2Bhttps%3A%2F%2Fgithub.com%2Fsirfoga%2Fpyhodl?ref=badge_shield) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[Apache License](http://www.apache.org/licenses/LICENSE-2.0) Version 2.0, January 2004

## Links

* [Documentation](https://sirfoga.github.io/pyhodl)
* [Issue tracker](https://github.com/sirfoga/pyhodl/issues)
* [Source code](https://github.com/sirfoga/pyhodl)

## You may also like...

- [cryptowatch](https://sirfoga.github.io/cryptowatch/) - Uses cryptowat.ch and tradingview.com APIs to display charts side-by-side
