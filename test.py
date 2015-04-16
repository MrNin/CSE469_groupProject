import struct
import hashlib
import os
import sys

#filename = str(sys.argv[1])

filename = 'TestImage1.img'
info = open(filename, 'rb').read()
mbr = info[:512]
print mbr
