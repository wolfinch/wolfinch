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

    logging.basicConfig(level=logging.DEBUG)     
    log = logging.getLogger(name)
    log.CRITICAL =  logging.CRITICAL
    log.ERROR    =  logging.ERROR
    log.WARNING  =  logging.WARNING
    log.INFO     =  logging.INFO
    log.DEBUG    =  logging.DEBUG
    log.NOTSET   =  logging.NOTSET
    return log

#EOF
