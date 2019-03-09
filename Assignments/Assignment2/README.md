# Multiple level in-memory filesystem with data stored as blocks

This is the continuation of the previous assignment where we had changed the design of the flat in-memory filesystem to store the data in blocks. Here we need to change the design to make the filesystem to support heirarchy, that is multiple levels of files in the filesystem.

## Design of the project

In this assignment, we had to make the directories be able to support directories inside them. A quick brainstorming will tell us that we'll need to maintain a record of the children directories and files in each level of the filesystem to be able to do any actions on them. This is exactly what has been followed here.



## Author information

1. Shreyas Gaadikere Sreedhara, Email - shreyasgaadikere@ufl.edu