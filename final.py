import binascii
import argparse
import hashlib
import ntpath
import sys
import os
import struct

PARTITION_TYPES = {
    0x01: 'DOS 12-bit FAT',
    0x04: 'DOS 16-bit FAT for partitions smaller than 32 MB',
    0x05: 'Extended partition',
    0x06: 'DOS 16-bit FAT for partitions larger than 32 MB',
    0x07: 'NTFS',
    0x08: 'AIX bootable partition',
    0x09: 'AIX data partition',
    0x0B: 'DOS 32-bit FAT',
    0x0C: 'DOS 32-bit FAT for interrupt 13 support',
    0x17: 'Hidden NTFS partition (XP and earlier)',
    0x1B: 'Hidden FAT32 partition',
    0x1E: 'Hidden VFAT partition',
    0x3C: 'Partition Magic recovery partition',
    0x66: 'Novell partitions',
    0x67: 'Novell partitions',
    0x68: 'Novell partitions',
    0x69: 'Novell partitions',
    0x81: 'Linux',
    0x82: 'Linux swap partition (can also be associated with Solaris partitions)',
    0x83: 'Linux native file system (Ext2, Ext3, Reiser, xiafs)',
    0x86: 'FAT16 volume/stripe set (Windows NT)',
    0x87: 'High Performace File System (HPFS) fault-tolerant mirrored partition or NTFS volume/stripe set',
    0xA5: 'FreeBSD and BSD/386',
    0xA6: 'OpenBSD',
    0xA9: 'NetBSD',
    0xC7: 'Typical of a corrupted NTFS volume/stripe set',
    0xEB: 'BeOS'
}


def to_value(char):
    padded = '\x00\x00\x00' + str(char)
    val = int(struct.unpack('>I', padded)[0])
    return val

def to_type(partition_type):
    return PARTITION_TYPES.get(partition_type)

def _print_mbr(entries):
    print '(0{0:x}) {1}, {2}, {3}'.format(
        to_value(entries[0][4]),
        to_type(to_value(entries[0][4])),
        str(entries[0][8]).zfill(10),
        str(entries[0][9]).zfill(10))
    print '(0{0:x}) {1}, {2}, {3}'.format(
        to_value(entries[1][4]),
        to_type(to_value(entries[1][4])),
        str(entries[1][8]).zfill(10),
        str(entries[1][9]).zfill(10))
    print '(0{0:x}) {1}, {2}, {3}'.format(
        to_value(entries[2][4]),
        to_type(to_value(entries[2][4])),
        str(entries[2][8]).zfill(10),
        str(entries[2][9]).zfill(10))
    print '(0{0:x}) {1}, {2}, {3}'.format(
        to_value(entries[3][4]),
        to_type(to_value(entries[3][4])),
        str(entries[3][8]).zfill(10),
        str(entries[3][9]).zfill(10))
    print '======================================='

def _read_image(image):
    boot_data = image[:440]
    disk_signature = image[440:446]
    entries = image[446:510]
    disk_structure = struct.Struct("<BBBBH")
    testy = disk_structure.unpack(disk_signature)
    
    entry_structure = struct.Struct("<cBBBcBBBIi")
    entry_0 = entry_structure.unpack(entries[:16])
    entry_1 = entry_structure.unpack(entries[16:32])
    entry_2 = entry_structure.unpack(entries[32:48])
    entry_3 = entry_structure.unpack(entries[48:64])
    entry_list = [entry_0, entry_1, entry_2, entry_3]
    _print_mbr(entry_list)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Extract and read MBR and VBR for given image file.')
    parser.add_argument('-i', '--input', help='Path to a RAW image file.')
    args = parser.parse_args()
    if args.input is None:
        parser.print_help()
        sys.exit(1)
    if not os.path.isfile(args.input):
        print 'File does not exist.'
        sys.exit(1)
        
    filename = args.input
    input_file = open(filename, 'rb').read()
    #filename = 'TestImage1.img'

    name = ''
    mD5 = hashlib.md5(input_file).hexdigest()
    sHA1 = hashlib.sha1(input_file).hexdigest()

    #print the two values
    output = "\nMD5:\t" + mD5 + "\n\nSHA1:\t" + sHA1 + "\n"
    print output + '=======================================\n'
    
    #write them to files
    index = filename.find('.img', 0)

    if index != 0:
        name = filename[0:index]

    mD5file = 'MD5-' + name + '.txt'
    sHAfile = 'SHA-' + name + '.txt'

    open(mD5file, 'w').write(mD5)
    open(sHAfile, 'w').write(sHA1)

    #read the raw image
    info = open(filename, 'rb').read()
    mbr = info[:512]
    _read_image(mbr)


    
