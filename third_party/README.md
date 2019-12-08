### Third-party dependencies:

**All the python third-party dependencies are in requirement.txt**

Install by `pip install -r requirement.txt`

1. Install sqlite (if not installed already)

####Below are not required or related to deprecated functionality:

2. gdax python implementation.

	* Official gdax python doesn't support websockets. Install danpaquin/gdax-python or joshith/gdax-python manually.
 	* coinbasepro official python library is good and included in requirements.txt
	
3. ~~ta-lib~~ -- not required - using tulip now. which is directly installable with pip
	* http://mrjbq7.github.io/ta-lib
	* https://github.com/joshith/ta-lib
	1.install ta-lib
		mac:
		brew install ta-lib
		linux:
		download : http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
		1. untar
		2. ./configure
		3. make install
	2. pip install TA-Lib
	
