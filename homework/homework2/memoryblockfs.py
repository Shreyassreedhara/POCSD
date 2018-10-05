#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import logging

from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

n = 8

if not hasattr(__builtins__, 'bytes'):
    bytes = str

class Memory(LoggingMixIn, Operations):
    'Example memory filesystem. Supports only one level of files.'

    def __init__(self):
        self.files = {}
        self.data = defaultdict(list)
        self.fd = 0
        now = time()
        self.files['/'] = dict(st_mode=(S_IFDIR | 0o755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)

    def chmod(self, path, mode):
        self.files[path]['st_mode'] &= 0o770000
        self.files[path]['st_mode'] |= mode
        return 0

    def chown(self, path, uid, gid):
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid

    def create(self, path, mode):
        self.files[path] = dict(st_mode=(S_IFREG | mode), st_nlink=1,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time())

        self.fd += 1
        return self.fd

    def getattr(self, path, fh=None):
        if path not in self.files:
            raise FuseOSError(ENOENT)

        return self.files[path]

    def getxattr(self, path, name, position=0):
        attrs = self.files[path].get('attrs', {})

        try:
            return attrs[name]
        except KeyError:
            return ''       										# Should return ENOATTR

    def listxattr(self, path):
        attrs = self.files[path].get('attrs', {})
        return attrs.keys()

    def mkdir(self, path, mode):
        self.files[path] = dict(st_mode=(S_IFDIR | mode), st_nlink=2,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time())

        self.files['/']['st_nlink'] += 1

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
	s = ''												# initializing an empty string
	i = len(self.data[path])									# store length of self.data[path] in i to check condition later in the while loop
	m = 0												# initialize m to 0 to use in while loop later
	while (i != 0):											# while loop to make the list into a string
		popword = self.data[path].pop(m)							# take out the first string of self.data[path] and store it in popword
		self.data[path].append(popword)								# add that string back to self.data[path] at the last
		s = s + popword										# concatinate the string s and popword
		i = i-1											# decrementing i 
		print ('popword: ' + popword)			
	print (s)
	offset = len(s)											# set offset till where the data was read
	return s 

    def readdir(self, path, fh):
        return ['.', '..'] + [x[1:] for x in self.files if x != '/']

    def readlink(self, path):
        return self.data[path]

    def removexattr(self, path, name):
        attrs = self.files[path].get('attrs', {})

        try:
            del attrs[name]
        except KeyError:
            pass        										# Should return ENOATTR

    def rename(self, old, new):
        self.files[new] = self.files.pop(old)

    def rmdir(self, path):
        self.files.pop(path)
        self.files['/']['st_nlink'] -= 1

    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
	final = []											# create an empty list 
	var = 0
	for i in range(0,len(source),n):								# for loop to convert source into a list
		divdata = source[var:var+n]
		var = var + n
		final.append(divdata)									# appending divdata to final
	source = final											# copy final into source							
        self.files[target] = dict(st_mode=(S_IFLNK | 0o777), st_nlink=1,
                                  st_size=len(source))
	
        self.data[target] = source

    def truncate(self, path, length, fh=None):
	s = ''												# initializing an empty string
	i = len(self.data[path])									# store length of self.data[path] in i to check condition later in the while loop
	m = 0												# initialize m to 0 to use in while loop later
	while (i != 0):											# while loop to make the list into a string
		popword = self.data[path].pop(m)							# take out the first string of self.data[path] and store it in popword
		s = s + popword										# concatinate the string s and popword
		i = i-1	
	s = s [:length]
	final = []
	var = 0
	for i in range(0,len(s),n):									# for loop to convert string into list
		divdata = s[var:var+n]
		var = var + n
		final.append(divdata)
	self.data[path] = final
        #self.data[path] = self.data[path][:length]
	
        self.files[path]['st_size'] = length

    def unlink(self, path):
        self.files.pop(path)

    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime

    def write(self, path, data, offset, fh):
	if (len(self.data[path]) == 0):
		final = []
		var = 0
		for i in range(0,len(data),n):
			divdata = data[var:var+n]
			var = var + n
			final.append(divdata)
		offset = offset + len(data)
		print (final) 
		self.data[path] = final  
		print ('splitdata' + str(self.data[path]))     
		
	else:
		var1 = 0										# declaring a constant
		final2 = []										# initializing an empty list.
		strsize = len(self.data[path]) - 1							# calculating the length of the list already present and subtract one from it. This will later be 														used for the poping the last element of the list in self.data[path]
		print ('length' + str(strsize))
		print ('first element--------------------> ' +str(self.data[path][0]))
		#print self.data[path]
		laststr = self.data[path].pop(strsize)							# we are poping out the last element of self.data[path] and storing it.
		new_word = laststr + data								# we are concatinating the last element of self.data[path] and the incoming data.
		for i in range(0,len(new_word),n):							# we are running a for loop for the length of new_word and dividing the new_word into strings of 8 														bytes. 
			divdata = new_word[var1:var1+n]
			var1 = var1 + n									# moving the pointer ahead, so that the next 8 bytes will be taken from the divdata.
			final2.append(divdata)								# appending the 8 bytes of data in divdata with the list final2. 
		self.data[path].extend(final2)								# adding the lists self.data[path] and final2. 
		offset = offset + len(data)								# changing the offset.
		print (str(self.data[path]))
        	print (self.files[path]['st_size'])
	self.files[path]['st_size'] = (len(self.data[path])-1) * n + len(self.data[path][-1])		# the st_size will be the length of the charcters in the self.data[path]
        return len(data)

		


if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(Memory(), argv[1], foreground=True, debug=True)
