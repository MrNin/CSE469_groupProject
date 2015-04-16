import struct
import hashlib
import os
import sys

#filename = str(sys.argv[1])

filename = 'TestImage1.img'
name = ''
mD5 = hashlib.md5(open(filename, 'rb').read()).hexdigest()
         
sHA = hashlib.sha1(open(filename, 'rb').read()).hexdigest()

print(mD5)

print (sHA)

index = filename.find('.img', 0)

if index != 0:
    name = filename[0:index]
    print(name)

mD5file = 'MD5-' + name + '.txt'

sHAfile = 'SHA-' + name + '.txt'

print(mD5file)

print(sHAfile)

fo = open(mD5file, 'w').write(mD5)

open(sHAfile, 'w').write(sHA)
