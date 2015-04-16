"""Usage: test.py (-f <path>)

Arguments:
    path  the filepath

Options:
    -f --filepath  path to the file
"""
import struct
import os

if __name__ == '__main__':
   #entry_structure = struct.Struct("i25s3b21s10s")
   entry_structure = struct.Struct("117s")
   with open("TestImage1.img", 'rb') as fin:
       for line in fin:
           test = len(line.strip())
           print entry_structure.unpack(line.strip())
           #entry = entry_structure.unpack(line.strip())

           #pull data
           #index = entry[0]
           #address = entry[1].decode('utf-8').strip()
           #zipcode = int.from_bytes(entry[2:5], 'little')
           #name = entry[5].decode('utf-8')
           #phone = entry[6].decode('utf-8')

           #print data
           #print(('{0:0>10d}: {3}\n' +
                  #(' '*12) + '{1}, {2:d}\n' +
                  #(' '*12) + '{4}\n').format(index, address, zipcode,name, phone))
