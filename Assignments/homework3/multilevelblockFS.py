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
                               st_mtime=now, st_atime=now, st_nlink=2,files=[])

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
                                st_atime=time(),files=[])
	print('----------------------------------mode-------------------------------------')
	print(self.files[path]['st_mode'])
	
	parentpath,childpath = self.splitdata(path)					# split the parent path and child path
	self.files[parentpath]['files'].append(childpath)			# add the child path to parent file's metadata	
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
            return ''       								# Should return ENOATTR

    def listxattr(self, path):
        attrs = self.files[path].get('attrs', {})
        return attrs.keys()

    def mkdir(self, path, mode):
        self.files[path] = dict(st_mode=(S_IFDIR | mode), st_nlink=2,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time(),files=[])
	parentpath,childpath = self.splitdata(path)				# split the path into child path and parent path
	self.files[parentpath]['st_nlink'] += 1					# increment the st_nlink of the parent path by 1
	self.files[parentpath]['files'].append(childpath)		# add the child path to the files of the parent path

    def splitdata(self,path):
	childpath = path[path.rfind('/')+1:]					# storing the child path 
	parentpath = path[:path.rfind('/')]						# storing the parent path
	if parentpath == '':
		parentpath = '/'									# default value for parent path
	return parentpath,childpath								# returning parent path and child path
	
    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):

	d = self.data[path]										# put the data of the file in 'd' variable
	p = self.files[path]									# put the metadata of the file in 'p' variable
	dd = ''.join(d[offset//n : (offset + size -1)//n])		# join the required length of the size from the file starting from the offset
	dd = dd[offset % n: offset % n + size]					
	return dd 

    def readdir(self, path, fh):
        return ['.', '..'] + [x for x in self.files[path]['files']]

    def readlink(self, path):
        return self.data[path]

    def removexattr(self, path, name):
        attrs = self.files[path].get('attrs', {})

        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

    def rename(self, old, new):
	oparentpath,ochildpath = self.splitdata(old)							# split old address into old parentpath and old childpath 
	nparentpath,nchildpath = self.splitdata(new)							# split new address into new parentpath and new childpath
	if self.files[old]['st_mode'] & 0770000 == S_IFDIR:						# check if the object to be moved is a file or a folder
		self.mkdir(new,509)
		for f in self.files[old]['files']:
			self.files[new]['st_nlink'] = self.files[old]['st_nlink']
			self.files[new]['files'] = self.files[old]['files']
			self.rename(old+'/'+self.files[old]['files'][0],new+'/'+self.files[old]['files'][0])
		self.rmdir(old)	
	else:
		self.create(new,33188)									# call create function to create a new file in the new path	
		self.files[nparentpath]['st_size'] = self.files[oparentpath]['st_size']			# copy size from the old parent path to the new parent path
		self.data[nchildpath]= self.data[ochildpath]						# copy the metadata of the old child path into the new child path
		self.files[oparentpath]['files'].remove(ochildpath)					# remove old child path from the old parent path

    def rmdir(self, path):
        parentpath,childpath = self.splitdata(path)							# split the path into parent path and new path
	self.files[parentpath]['files'].remove(childpath)						# remove the files related to the childpath from the parent path
        self.files[parentpath]['st_nlink'] -= 1								# decrement the st_nlink by 1
	

    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
	self.files[target] = dict(st_mode=(S_IFLINK | 0o777), st_nlink=1, st_size=len(source))
	d1 = target[target.rfind('/')+1:]													# find the last occurence of '/' in the path and add 1 to it to do slicing 
	self.data[target] = [source[i:i+n] for i in range(0, len(source), n)]				# copying the data from the source to target, 8 bits at a time

    def truncate(self, path, length, fh=None):
	d1 = path[path.rfind('/')+1:]
    	d = self.data
        d[d1] = [(d[d1][i] if i < len(d[d1]) else '').ljust(bsize, '\x00') for i in range(length//bsize)] \
                + [(d[d1][length/bsize][:length % bsize] if length//bsize < len(d[d1]) else '').ljust(length % bsize, '\x00')]
        p = self.files[path]
        p['st_size'] = lengt
    def unlink(self, path):
	parentpath,childpath=self.splitdata(path)					# seperate parentpath and childpath
	self.files[parentpath]['files'].remove[childpath]			# remove childpath from parentpath's metadata

    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime

    def write(self, path, data, offset, fh):
	if (len(self.data[path]) == 0):									# checking if we are writing for the first time
		final = []													# initializing an empty list
		var = 0														# declaring a constant
		for i in range(0,len(data),n):								# start a for loop for the length of the new_word for dividing into strings of 8 bytes.
			divdata = data[var:var+n]								# put the 8 bytes of data into divdata
			var = var + n											# increment variable by 8
			final.append(divdata)									# add divdata to the list that was declared earlier
		offset = offset + len(data)
		print (final) 
		self.data[path] = final 									# copy the list final into self.data[path] 
		print ('splitdata' + str(self.data[path]))     
		
	else:
		var1 = 0													# declaring a constant
		final2 = []													# initializing an empty list.
		strsize = len(self.data[path]) - 1							# calculating the length of the list already present and subtract one from it. This will later be 														used for the poping the last element of the list in self.data[path]
		print ('length' + str(strsize))
		print ('first element--------------------> ' +str(self.data[path][0]))
		#print self.data[path]
		laststr = self.data[path].pop(strsize)						# we are poping out the last element of self.data[path] and storing it.
		new_word = laststr + data									# we are concatinating the last element of self.data[path] and the incoming data.
		for i in range(0,len(new_word),n):							# we are running a for loop for the length of new_word and dividing the new_word into strings of 8 														bytes. 
			divdata = new_word[var1:var1+n]
			var1 = var1 + n											# moving the pointer ahead, so that the next 8 bytes will be taken from the divdata.
			final2.append(divdata)									# appending the 8 bytes of data in divdata with the list final2. 
		self.data[path].extend(final2)								# adding the lists self.data[path] and final2. 
		offset = offset + len(data)									# changing the offset.
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
