#  Copyright: (c) 2017-2020 Joshith Rayaroth Koderi
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

import yaml

# Load  external config file
def readConf (fileName):
    try:
        with open(fileName) as fp:
            confDict = yaml.load(fp, Loader=yaml.FullLoader)
#             print (confDict)
            return confDict
    except Exception as e: # parent of IOError, OSError *and* WindowsError where available
        print('Oops!! Conf Read Error for %s e: %s'%(fileName, e))
