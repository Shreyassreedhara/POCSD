#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import logging

from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

# Data will be stored in the filesystem in blocks of following size
block_size = 8

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
	
    # split the parent path and child path
	parentpath,childpath = self.splitdata(path)
    # add the child path to parent file's metadata					
	self.files[parentpath]['files'].append(childpath)				
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
            return ''       								

    def listxattr(self, path):
        attrs = self.files[path].get('attrs', {})
        return attrs.keys()

    def mkdir(self, path, mode):
        self.files[path] = dict(st_mode=(S_IFDIR | mode), st_nlink=2,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time(),files=[])
        # split the path into child path and parent path
	    parentpath,childpath = self.splitdata(path)
        # increment the st_nlink of the parent path by 1				
	    self.files[parentpath]['st_nlink'] += 1
        # add the child path to the files of the parent path					
	    self.files[parentpath]['files'].append(childpath)		

    def splitdata(self,path):
        # storing the child path
	    childpath = path[path.rfind('/')+1:]
        # storing the parent path					 
	    parentpath = path[:path.rfind('/')]						
	    if parentpath == '':
            # default value for parent path
		    parentpath = '/'
        # returning parent path and child path									
	    return parentpath,childpath								
	
    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        # put the data of the file in 'data' variable
	    data = self.data[path]
        # put the metadata of the file in 'path' variable										
	    path = self.files[path]
        # join the required length of the size from the file starting from the offset									
	    dd = ''.join(d[offset//block_size : (offset + size -1)//block_size])		
	    dd = dd[offset % block_size: offset % block_size + size]					
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
        # split old address into old parentpath and old childpath
        oparentpath,ochildpath = self.splitdata(old)
        # split new address into new parentpath and new childpath							 
        nparentpath,nchildpath = self.splitdata(new)
        # check if the object to be moved is a file or a folder							
        if self.files[old]['st_mode'] & 0770000 == S_IFDIR:						
            self.mkdir(new,509)
            for f in self.files[old]['files']:
                self.files[new]['st_nlink'] = self.files[old]['st_nlink']
                self.files[new]['files'] = self.files[old]['files']
                self.rename(old+'/'+self.files[old]['files'][0],new+'/'+self.files[old]['files'][0])
            self.rmdir(old)	
        else:
            # call create function to create a new file in the new path
            self.create(new,33188)
            # copy size from the old parent path to the new parent path										
            self.files[nparentpath]['st_size'] = self.files[oparentpath]['st_size']
            # copy the metadata of the old child path into the new child path			
            self.data[nchildpath]= self.data[ochildpath]
            # remove old child path from the old parent path						
            self.files[oparentpath]['files'].remove(ochildpath)					

    def rmdir(self, path):
        # split the path into parent path and new path
        parentpath,childpath = self.splitdata(path)
        # remove the files related to the childpath from the parent path							
	    self.files[parentpath]['files'].remove(childpath)
        # decrement the st_nlink by 1						
        self.files[parentpath]['st_nlink'] -= 1								
	

    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        self.files[target] = dict(st_mode=(S_IFLINK | 0o777), st_nlink=1, st_size=len(source))
        # find the last occurence of '/' in the path and add 1 to it to do slicing
        d1 = target[target.rfind('/')+1:]
        # copying the data from the source to target, 8 bits at a time													 
        self.data[target] = [source[i:i+block_size] for i in range(0, len(source), block_size)]				

    def truncate(self, path, length, fh=None):
        d1 = path[path.rfind('/')+1:]
        d = self.data
        d[d1] = [(d[d1][i] if i < len(d[d1]) else '').ljust(bsize, '\x00') for i in range(length//bsize)] \
                + [(d[d1][length/bsize][:length % bsize] if length//bsize < len(d[d1]) else '').ljust(length % bsize, '\x00')]
        p = self.files[path]
        p['st_size'] = length

    def unlink(self, path):
        # seperate parentpath and childpath
        parentpath,childpath=self.splitdata(path)
        # remove childpath from parentpath's metadata					
        self.files[parentpath]['files'].remove[childpath]			

    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime

    def write(self, path, data, offset, fh):
        # checking if we are writing for the first time
        if (len(self.data[path]) == 0):									
            final = []													
            var = 0
            # start a for loop for the length of the new_word for dividing into strings of 8 bytes														
            for i in range(0,len(data),block_size):
                # put the 8 bytes of data into divdata								
                divdata = data[var:var+block_size]
                # increment variable by the block_size								
                var = var + block_size
                # add the divided data to the list that was declared earlier											
                final.append(divdata)									
            offset = offset + len(data)
            print (final)
            # copy the list final into self.data[path] 
            self.data[path] = final 									 
            print ('splitdata' + str(self.data[path]))     
            
        else:
            var1 = 0													
            final2 = []
            # strsize will later be used for the poping the last element of the list in self.data[path]													
            strsize = len(self.data[path]) - 1							 														
            print ('length' + str(strsize))
            print ('first element--------------------> ' +str(self.data[path][0]))
            # poping out the last element of self.data[path] and storing it
            laststr = self.data[path].pop(strsize)
            # concatinating the last element of self.data[path] and the incoming data						
            new_word = laststr + data
            # running a for loop for the length of new_word and dividing the new_word into strings of 8 bytes									
            for i in range(0,len(new_word),block_size):							 														 
                divdata = new_word[var1:var1+block_size]
                # moving the pointer ahead, so that the next 8 bytes will be taken from the divdata
                var1 = var1 + block_size
                # appending the 8 bytes of data in divdata with the list final2											
                final2.append(divdata)
            # adding the lists self.data[path] and final2									 
            self.data[path].extend(final2)
            # update the offset								 
            offset = offset + len(data)									
            print (str(self.data[path]))
                print (self.files[path]['st_size'])
        # the st_size will be the length of the charcters in the self.data[path]
        self.files[path]['st_size'] = (len(self.data[path])-1) * block_size + len(self.data[path][-1])		
        return len(data)

		
if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(Memory(), argv[1], foreground=True, debug=True)
