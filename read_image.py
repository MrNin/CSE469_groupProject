import argparse
import hashlib
import sys
import os
import struct

from os import path


def findType(char):
   typeList = {'1': 'DOS 12-bit FAT',
               '4': 'DOS 16-bit FAT for partitions smaller than 32 MB',
               '5': 'Extended partition',
               '6': 'DOS 16-bit FAT for partitions larger than 32 MB',
               '7': 'NTFS',
               '8': 'AIX bootable partition',
               '9': 'AIX data partition',
               'b': 'DOS 32-bit FAT',
               'c': 'DOS 32-bit FAT for interrupt 13 support',
               '17': 'Hidden NTFS partition (XP and earlier)',
               '1b': 'Hidden FAT32 partition',
               '1e': 'Hidden VFAT partition',
               '3c': 'Partition Magic recovery partition',
               '66': 'Novell partitions',
               '67': 'Novell partitions',
               '68': 'Novell partitions',
               '69': 'Novell partitions',
               '81': 'Linux',
               '82': 'Linux swap partition (can also be associated with Solaris partitions)',
               '83': 'Linux native file system (Ext2, Ext3, Reiser, xiafs)',
               '86': 'FAT16 volume/stripe set (Windows NT)',
               '87': 'High Performace File System (HPFS) fault-tolerant mirrored partition or NTFS volume/stripe set',
               'a5': 'FreeBSD and BSD/386',
               'a6': 'OpenBSD',
               'a9': 'NetBSD',
               'c7': 'Typical of a corrupted NTFS volume/stripe set',
               'eb': 'BeOS'}
   
   return typeList[char]
   

def isValid(char):
   if char == '4' or char == '6':
      return 16
   elif char == 'b' or char == 'c':
      return 32
   else:
      return -1

def calcChecksums(filename):
   inputFile = open(filename, 'rb').read()
   
   #calculate the two checksums
   mD5 = hashlib.md5(inputFile).hexdigest()
   sHA1 = hashlib.sha1(inputFile).hexdigest()

   #print the two values
   output = "MD5:\t" + mD5 + "\n\nSHA1:\t" + sHA1
   print '\nChecksums:\n=======================================\n' + output 
    
   #write checksums to files
   name = filename
   index = -2
   while index != -1:
      index = name.find('\\',0)
      if index != -1:
         place = index + 1
         name = name[place:]

   while index != -1:
      index = name.find('/',0)
      if index != -1:
         place = index + 1
         name = name[place:]
         
   index = name.find('.img', 0)
   
   if index != -1:
        name = name[0:index]
   else:
      name = name

   mD5file = 'MD5-' + name + '.txt'
   sHAfile = 'SHA-' + name + '.txt'

   open(mD5file, 'w').write(mD5)
   open(sHAfile, 'w').write(sHA1)


def calcMBR(filename):
   #open image file and locate relevant data
   image = open(filename, 'rb').read()
   mbr = image[:512]

   #parse mbr to determine partition info
   record = mbr[446:510]
   partitionStruct = struct.Struct("<BBHBBHII")
   partition0 = partitionStruct.unpack(record[:16])
   partition1 = partitionStruct.unpack(record[16:32])
   partition2 = partitionStruct.unpack(record[32:48])
   partition3 = partitionStruct.unpack(record[48:64])
   partitionList = [partition0, partition1, partition2, partition3]

   #print partition info found from the MBR

   print ('=======================================')
   
   for partition in partitionList:
      print '(0{0:x}) {1}, {2}, {3}'.format(
      (partition[3]),
      findType('{:x}'.format(partition[3])),
      str(partition[6]).zfill(10),
      str(partition[7]).zfill(10))

   

   return partitionList

def calcVBR(filename, partitionList):
   image = open(filename, 'rb').read()

   #cycle through each partition finding its information
   for index, partition in enumerate(partitionList):
      #values needed to be found
      partitionType = '{:x}'.format(partition[3])
      bytesPerSector = 0
      sectorsPerCluster = 0
      reservedAreaSize = 0
      numFats = 0
      rootDirSectors = 0
      maxNumFilesDir = 0
      sectorsPerFat = 0
      cluster2 = 0

      #A list of important partition info
      partitionInfo = [bytesPerSector, sectorsPerCluster, reservedAreaSize, numFats,
                         rootDirSectors, maxNumFilesDir, sectorsPerFat, cluster2]
        
      #extract vbr if FAT16/32 partition
      if isValid(partitionType) == 32 or isValid(partitionType) == 16:
         start = partition[6] * 512
         end = start + 512

         #parsing the partition's vbr
         vbr = image[start:end]
         partitionStruct = struct.Struct("<HBHBHHBHHHIII")
         vbrStruct = partitionStruct.unpack(vbr[11:40])

         partitionInfo[0] = vbrStruct[0]
         partitionInfo[1] = vbrStruct[1]
         partitionInfo[2] = vbrStruct[2]
         partitionInfo[3] = vbrStruct[3]
         if isValid(partitionType) == 16:
               partitionInfo[4] = vbrStruct[4] * 32 / partitionInfo[0]
               partitionInfo[6] = vbrStruct[7]
               partitionInfo[7] = partitionInfo[2] + (partitionInfo[6] * partitionInfo[3]) + partitionInfo[4]
         partitionInfo[5] = vbrStruct[4]
         if isValid(partitionType) == 32:
               partitionInfo[6] = vbrStruct[12]
               partitionInfo[7] = partitionInfo[2] + (partitionInfo[6] * partitionInfo[3])

         #update cluster2
         partitionInfo[7] += partition[6]
            
         #print the information
         print('=======================================')
         print("Partition {0}({1})").format(index, findType(partitionType))
         print("Reserved area: Start sector: {0} Ending sector: {1} Size: {2} sectors").format(0,(partitionInfo[2] - 1),partitionInfo[2])
         print("Sectors per cluster: {0} sectors").format(partitionInfo[1])
         print("FAT area: Starting sector: {0} Ending sector: {1}").format(partitionInfo[2],
                                                                           (partitionInfo[2] - 1 + (partitionInfo[3] * partitionInfo[6])))
         print("# of FATs: {0}").format(partitionInfo[3])
         print("The size of each FAT: {0} sectors").format(partitionInfo[6])
         print("The first sector of cluster 2: {0} sectors").format(partitionInfo[7])

      
   

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Extract and read MBR and VBR for a given image file.')
    parser.add_argument('input', help='Path to a RAW image file.')

    #take in the name of the designated file and begin to read it
    args = parser.parse_args()
    filename = args.input
    filePath = path.relpath(filename)

    #checking if valid input
    if filename is None:
        parser.print_help()
        sys.exit(1)
    if not os.path.isfile(filename):
        print 'File does not exist.'
        sys.exit(1)

    
   #begin operations on given image file
    calcChecksums(filePath)
    partitionList = calcMBR(filePath)
    calcVBR(filePath, partitionList)
    
