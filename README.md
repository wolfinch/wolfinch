[![|License|](https://img.shields.io/badge/license-GPL%20v3.0-brightgreen.svg)](LICENSE)

********
# Wolfinch Auto Trading Bot

Wolfinch is a trading bot implemented in Python. It is primarily focused on crypto currency trading, however the implementation is generic enough that it can be used for trading any asset. The modularized implementation is easily extensible to support more exchanges, trading strategies and indicators. A simple UI is available out of the box to view trades and allow basic controls in operation. 

#### Features include : 
* Auto / Manual Trading Modes
* Multiple decision engines
* YAML based rich configuration - tons of nuts and bolts to customize
* Out of the box UI availability
* Pluggable Strategies 
* Pluggable Indicators
* Pluggable Exchanges
* Backtesting support
* Paper trading (Simulation) mode
* Genetic optimizer support for tuning strategies
* Machine Learning mode - supports training and using trained models and ML decision engines
* Take profit and stop Stop Loss support ( Plus Smart Stop loss)
* Supports trading multiple exchanges at the same time
* Supports trading multiple trading pairs at the same time
* Supports cross exchange, cross pair trading (Using signals and indicators on one exchange/trading-pair to make trading decision on another exchange/trading-pair)
* Restartability (of live trading, backtesting, genetic optimizer)


## Using Wolfinch

Starting the bot is fairly straight forward. 

A few examples below covers most startup modes:
* Fresh start: 
    `Wolfinch.py --config <config.yml>`
* Restart from previous state: 
    `Wolfinch.py --config <config.yml> --restart`
* Import historic data and exit: 
    `Wolfinch.py --config <config.yml> --import_only`

A lot of sample config files are available in config/ directory. Those should serve as a very good starting point.


### Supported Exchanges
* Coinbase Pro
* Binance
* Binance US
* gdax [deprecated]

### Disclaimer:

Strategies are experimental. Use them at your own risk. 

#### Further Enhancements: 

Not based on priority.

1. add more indicators
2. add more strategies 
3. improve Decision/Model
5. more exchanges, inter exchange strategy, tie with model
7. integrate news source
10. high frequency trading
11. **Any additional feature requests**

#### NOTE:
Read third-party [Readme](third_party/README) for dependencies

### Donate:
You can donate to appreciate the countless hours spent on the development.

* **BTC** : 35bYjx9Geo6gLM41nqRnZA5KpciJEfJokD
* **ETH** : 0x2598eA883719a679deEf821736fa39DF0DD9F86C
* **LTC** : MRfdbKHUrSxv2zKztdVyodKwSzpQNgofr8

### License

GNU General Public License v3.0 or later

See [LICENSE](LICENSE) to see the full text.


   
