Third-party dependencies in requirements.txt
install by 'pip install -r requirements.txt'

1. gdax python implementation.
	Official gdax python doesn't support websockets. Install danpaquin/gdax-python or joshith/gdax-python manually.
1.1 coinbasepro official python library is good and included in requirements.txt
	
2. ta-lib
	http://mrjbq7.github.io/ta-lib
	https://github.com/joshith/ta-lib
	1. install ta-lib
		mac:
		brew install ta-lib
		linux:
		download : http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
		1. untar
		2. ./configure
		3. make install
	
	2. pip install TA-Lib
	
3. Install sqlite
