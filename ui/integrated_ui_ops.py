#! /usr/bin/env python
#
# Wolfinch Auto trading Bot
# Desc: integrated UI impl.
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


from multiprocessing import Process, Pipe

from utils import getLogger

from . import ui_server

log = getLogger ('UI-OPS')
log.setLevel(log.DEBUG)

g_p = None

def ui_mp_init (port):
    global g_p
    
    log.info ("init multi-process ui")
    
    parent_conn, child_conn = Pipe()
    
    g_p = Process(target=ui_server.ui_main, args=(port, child_conn,))
    g_p.start()
    
    return parent_conn
    
def ui_mp_end ():
    
    log.info ("finishing ui")
    
    if g_p == None:
        return
    
    g_p.terminate()
    g_p.join()
    
#EOF
