|PyPI version| |Docs badge| |Build Status| |License|

*******
# Wolfinch Auto Trading Bot
*******

Wolfinch is a trading bot implemented in Python. It is primarily focused on crypto currency trading, however the implementation is generic enough that it can be used for any assets. The modularized implementation is easily extensible to support more exchanges, strategies and indicators. A simple UI is available out of the box to view trades and allow basic control on operation. 

Features : 
* Auto / Manual Trading Modes
* Multiple decision engines
* YAML based rich configuration - everything is customizable
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


Supported Exchanges
===================
* Coinbase Pro
* Binance
* Binance US
* gdax [deprecated]

Using Wolfinch
==============

## Further Enhancements: 

Not based on priority.

1. add more indicators
2. add more strategies 
3. improve Decision/Model
5. more exchanges, inter exchange strategy, tie with model
7. integrate news source
10. high frequency trading



NOTE:
# Read third-party readme for dependencies

Read third_party/README

License
=======

GNU General Public License v3.0 or later

See `LICENSE <LICENSE>`_ to see the full text.