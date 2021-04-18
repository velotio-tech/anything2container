#!/usr/bin/python
# Import system module
import os
# Import Local Module
from cent6 import  Cent6OS
from cent7 import Cent7OS
from osinterface import OSinterface

def get_os_object():
    if os.path.exists('/sbin/initctl'):
        print "Generating metadata for cen6"
        return Cent6OS()
    elif os.path.exists('/usr/bin/systemctl'):
        print "Generating metadata for cent7"
        return Cent7OS()
    else:
        return OSinterface()
        
    