# Multiple level in-memory filesystem with data stored as blocks

This is the continuation of the previous assignment where we had changed the design of the flat in-memory filesystem to store the data in blocks. Here we need to change the design of the filesystem to support heirarchy, that is multiple levels of files in the filesystem.

## FUSE filesystem

Before working on this assignment it is necessary to have a good understanding of the FUSE filesystem. FUSE stands for 'Filesystem in user space'. It is a software interface for Unix like computer operating systems that lets non-previleged users create their own filesystems without editing kernel code. This is achieved by running the filesystem code in user space while FUSE module provides only a "bridge" to the actual kernel interfaces. 

To implement a new file system, a handler program linked to the supplied libfuse library needs to be written. The main purpose of this program is to specify how the file system is to respond to read/write/stat requests. The program is also used to mount the new file system. At the time the file system is mounted, the handler is registered with the kernel. If a user now issues read/write/stat requests for this newly mounted file system, the kernel forwards these IO-requests to the handler and then sends the handler's response back to the user.

![alt text](fuse_filesystem.png)

## Design of the project

In this assignment, we had to make the directories be able to support directories inside them. A quick brainstorming will tell us that we'll need to maintain a record of the children directories and files in each level of the filesystem to be able to do any actions on them. This is exactly what has been followed here.

To proceed with this task, first you must familarize yourself with the working of the data structures used in the flat filesystem, and built in data types in Python - specifically, the python dictionary (dict). 

The file [multilevelblockFS.py](multilevelblockFS.py) is well commented and supports the complex file system operations.

## Author information

1. Shreyas Gaadikere Sreedhara, Email - shreyasgaadikere@ufl.edu