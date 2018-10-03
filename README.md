<div align="center">
<h1>pyhodl | Download, update, analyze and plot your crypto-transactions. Completely off-line and secure (you own your data).</h1>
<em>Made with love and crypto money.</em></br></br>
</div>

<div align="center">
<a href="https://travis-ci.org/sirfoga/pyhodl"><img alt="Build Status" src="https://travis-ci.org/sirfoga/pyhodl.svg?branch=master"></a> <a href="https://circleci.com/gh/sirfoga/pyhodl"><img alt="CircleCI" src="https://circleci.com/gh/sirfoga/pyhodl.png"></a>
</div>

<div align="center">
<a href="https://landscape.io/github/sirfoga/pyhodl/master"><img alt="Code Health" src="https://landscape.io/github/sirfoga/pyhodl/master/landscape.svg?style=flat"></a> <a href="https://bettercodehub.com/"><img alt="BCH compliance" src="https://bettercodehub.com/edge/badge/sirfoga/pyhodl?branch=master"></a> <a href="https://www.codacy.com/app/sirfoga/pyhodl?utm_source=github.com&amp;amp;utm_medium=referral&amp;amp;utm_content=sirfoga/pyhodl&amp;amp;utm_campaign=Badge_Grade"><img alt="Codacy Badge" src="https://api.codacy.com/project/badge/Grade/1eff18395a134c9aa2d829fcb1f124bf"></a> <a href="https://codeclimate.com/github/sirfoga/pyhodl"><img alt="Code Climate" src="https://lima.codeclimate.com/github/sirfoga/pyhodl/badges/gpa.svg"></a>

<img alt="pylint Score" src="https://mperlet.de/pybadge/badges/9.88.svg"> <a href="https://bestpractices.coreinfrastructure.org/projects/1544"><img alt="CII Best Practices" src="https://bestpractices.coreinfrastructure.org/projects/1544/badge"></a> <a href="https://snyk.io/test/github/sirfoga/pyhodl"><img alt="Known Vulnerabilities" src="https://snyk.io/test/github/sirfoga/pyhodl/badge.svg"></a>

<a href="https://app.fossa.io/projects/git%2Bhttps%3A%2F%2Fgithub.com%2Fsirfoga%2Fpyhodl?ref=badge_shield"><img alt="FOSSA Status" src="https://app.fossa.io/api/projects/git%2Bhttps%3A%2F%2Fgithub.com%2Fsirfoga%2Fpyhodl.svg?type=shield"></a> <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg"></a> <a href="https://github.com/sirfoga/pyhodl/issues"><img alt="Contributions welcome" src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat"></a>
</div>


## Table of Contents

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

[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/sirfoga/pyhodl/issues) [![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](http://unlicense.org/)

0. [Open an issue](https://github.com/sirfoga/pyhodl/issues/new)
0. [fork](https://github.com/sirfoga/pyhodl/fork) this repository
0. create your feature branch (`git checkout -b my-new-feature`)
0. commit your changes (`git commit -am 'Added my new feature'`)
0. publish the branch (`git push origin my-new-feature`)
0. [open a PR](https://github.com/sirfoga/pyhodl/compare)


## License

[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bhttps%3A%2F%2Fgithub.com%2Fsirfoga%2Fpyhodl.svg?type=shield)](https://app.fossa.io/projects/git%2Bhttps%3A%2F%2Fgithub.com%2Fsirfoga%2Fpyhodl?ref=badge_shield) [![License](https://img.shields.io/badge/license-Unlicense-blue.svg)](http://unlicense.org/)
[MIT License](https://opensource.org/licenses/MIT)


## Links

* [Documentation](https://sirfoga.github.io/pyhodl)
* [Issue tracker](https://github.com/sirfoga/pyhodl/issues)
* [Source code](https://github.com/sirfoga/pyhodl)

## You may also like...

- [cryptowatch](https://sirfoga.github.io/cryptowatch/) - Uses cryptowat.ch and tradingview.com APIs to display charts side-by-side
