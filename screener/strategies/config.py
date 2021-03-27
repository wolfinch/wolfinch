#
# Wolfinch Auto trading Bot
# Desc:  Market Screener config
#  Copyright: (c) 2017-2021 Joshith Rayaroth Koderi
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


from .volume_spike import VOL_SPIKE

def Configure ():
    scrnr_list = []
    
    scrnr_list.append(VOL_SPIKE("VOL-SPIKE-MEGACAP", ticker_kind="MEGACAP", vol_multiplier=2))
#     scrnr_list.append(VOL_SPIKE("VOL-SPIKE-MEGACAP1", ticker_kind="MEGACAP", vol_multiplier=2))
    
#     scrnr_list.append(VOL_SPIKE("VOL-SPIKE-ALL", ticker_kind="ALL"))
    scrnr_list.append(VOL_SPIKE("VOL-SPIKE-GT50M", ticker_kind="GT50M", vol_multiplier=3))
    scrnr_list.append(VOL_SPIKE("VOL-SPIKE-LT50M", ticker_kind="LT50M", vol_multiplier=4))
    return scrnr_list

#EOF