from __future__ import with_statement
import yaml

# Load  external config file
def readConf (fileName):
    try:
        with open(fileName) as fp:
            confDict = yaml.load(fp, Loader=yaml.FullLoader)
#             print (confDict)
            return confDict
    except : # parent of IOError, OSError *and* WindowsError where available
        print ('Oops!! Conf Read Error for '+fileName)
