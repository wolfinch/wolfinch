'''
 Wolfinch Auto trading Bot
 Desc: Generic Logging routines
#  Copyright: (c) 2017-2022 Wolfinch Inc.
#  This file is part of Wolfinch.
# 
#  Wolfinch is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
# 
#  Wolfinch is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with Wolfinch.  If not, see <https://www.gnu.org/licenses/>.
'''

import logging

# 
# class WolfinchLogger (logging):
#     
# class Logger():
#     def __init__(self, name=None):
#         self.getLogger (name)
#             
def getLogger (name):
#     FORMAT = "[%(levelname)s:%(name)s:%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    FORMAT = "[%(asctime)s %(levelname)s:%(name)s - %(funcName)20s(%(lineno)d) ] %(message)s"

#     logging.basicConfig(filename='wolfinch.log', filemode='a', level=logging.DEBUG, format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')   
    logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')     
    log = logging.getLogger(name)
    log.CRITICAL =  logging.CRITICAL
    log.ERROR    =  logging.ERROR
    log.WARNING  =  logging.WARNING
    log.INFO     =  logging.INFO
    log.DEBUG    =  logging.DEBUG
    log.NOTSET   =  logging.NOTSET
    return log

#EOF
