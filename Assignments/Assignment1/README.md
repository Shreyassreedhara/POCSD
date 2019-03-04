# Flat in memory filesystem with data stored as blocks

This assignment deals with the changing the design of a flat in memory filesystem to store the data in blocks. There are a lot of advantages of keeping storing data as blocks, they are improved input and output operations, better error detection and correction, redundancy and replication for fault tolerance.

## Design 

The [memory.py file](https://github.com/fusepy/fusepy/blob/master/examples/memory.py) is the starting point of this assignment. This file has the flat filesystem implementation of a UNIX like file system. The task is to store all the file data in blocks of equal size but the upper filesystem layers should not feel any difference about this happening in the background. 

The methods that we have to alter to achieve this task are read, write and truncate. The file memoryblockFS.py has the changed methods for read, write and truncate and it achieves splitting the file data into blocks of 8 byte size. 

## Author information

Shreyas Gaadikere Sreedhara, Email - shreyasgaadikere@ufl.edu