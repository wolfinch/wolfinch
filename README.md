[![|License|](https://img.shields.io/badge/license-GPL%20v3.0-brightgreen.svg)](LICENSE)

********
# Wolfinch

Wolfinch is a trading bot implemented in Python. It supports algorithmic trading for equity market and cryptocurrency exchanges. The modularized implementation is easily extensible to support more exchanges, trading strategies and indicators. A simple UI is available out of the box to view trades and allow basic controls in operation. 

#### Features include : 
* Auto / Manual Trading Modes
* Multiple decision engines
* YAML based rich configuration file support - Tons of nuts and bolts to customize
* Out of the box UI availability
* Pluggable Strategies 
* Pluggable Indicators
* Pluggable Exchanges
* Backtesting support
* Paper trading (Simulation) mode
* Genetic optimizer support for tuning strategies
* Machine Learning mode - supports training and using trained models and ML decision engines
* Positional Stop Stop Loss support, multiple smart stop strategies available
	- Fixed Percent
	- Trailing with fixed percent
	- ATR trailing stop (with variable ATR period support)
	- Strategy provided
* Positional Take profit support
	- Fixed percent
	- Strategy provided
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

**Read More here**:

[Introduction-to-the-friendly-trading-bot](https://medium.com/@joe.cet/wolfinch-introduction-to-the-friendly-trading-bot-fe9281825e59)

[algorithmic-trading-with-robinhood-using-wolfinch](https://medium.com/@joe.cet/algorithmic-trading-with-robinhood-using-wolfinch-b268b7aca43f)

[algorithmic-trading-with-binance-using-wolfinch](https://medium.com/@joe.cet/algorithmic-trading-with-binance-using-wolfinch-fe5353885451)


### Supported Exchanges
* Coinbase Pro
* Binance
* Binance US
* Robinhood
* gdax [deprecated]

### Disclaimer:

This project is for educational purpose only. Strategies are experimental. Use them at your own risk. 

#### Further Enhancements: 

Not based on priority.

1. more indicators
2. more strategies 
3. improve Decision/Model
5. more exchanges
7. integrate news source, sentiment analysis input for decision 
10. **Any feature requests**

#### NOTE:
Read third-party [Readme](third_party/README.md) for dependencies

### Donate:
You can donate to appreciate the countless hours spent on the development.

* **BTC** : `35bYjx9Geo6gLM41nqRnZA5KpciJEfJokD`
* **ETH** : `0x2598eA883719a679deEf821736fa39DF0DD9F86C`
* **LTC** : `MRfdbKHUrSxv2zKztdVyodKwSzpQNgofr8`

[![](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=JCTW62GFL4QGW&currency_code=USD&source=url)



### License

GNU General Public License v3.0 or later

See [LICENSE](LICENSE) to see the full text.


   
