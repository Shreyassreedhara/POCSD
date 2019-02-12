# Client/Server file system

The aim of this project is to build a client/server file system, which stores its data into a remote server instead of a local computers. The FUSE filesystem is designed such that the storage of the file system data takes place in the memory of server.

## Design of the project

There are two kinds of servers here - metaserver and dataserver. Metaserver is used to store the metadata of the files/directories and dataserver is used to store the data of the files. The client will act as the FUSE handler as well as an XMLRPC client in the remote file system which connects to both metaserver and dataserver.

The metaserver will hold the keys which are the path of the files or the directories and the values of the keys are the corresponding metadata of the file or directory. In the data server the key would be the path of the file and the value would be the data of the file. To send/receive and store the data into the server requires it to be serialized/marshalled. Python library 'pickle' is used for serializing the data. 

The configuration of the server endpoints at the client is by the means of the command line arguments passed. The implementation also supports a hierarchial namespace and splitting of the file data into blocks.

## Steps to run the program

```
python metaserver.py --port 2222
python dataserver.py --port 3333
python remoteFS.py fusemount 2222 3333
```

## Author information

Shreyas Gaadikere Sreedhara, Email - shreyasgaadikere@ufl.edu