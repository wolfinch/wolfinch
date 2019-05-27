'''
 OldMonk Auto trading Bot
 Desc: Generic Logging routines
 (c) Joshith
'''

import logging

# 
# class OldMonkLogger (logging):
#     
# class Logger():
#     def __init__(self, name=None):
#         self.getLogger (name)
#             
def getLogger (name):
#     FORMAT = "[%(levelname)s:%(name)s:%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    FORMAT = "[%(levelname)s:%(name)s - %(funcName)20s() ] %(message)s"

#     logging.basicConfig(filename='oldmonk.log', filemode='a', level=logging.DEBUG, format=FORMAT)         
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)     
    log = logging.getLogger(name)
    log.CRITICAL =  logging.CRITICAL
    log.ERROR    =  logging.ERROR
    log.WARNING  =  logging.WARNING
    log.INFO     =  logging.INFO
    log.DEBUG    =  logging.DEBUG
    log.NOTSET   =  logging.NOTSET
    return log

#EOF
