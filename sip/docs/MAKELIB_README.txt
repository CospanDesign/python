If you need to make a c++ library to use with SIP

$ g++ -c <name>.cpp
$ ar -crs lib<name>.a word.o
$ sudo cp lib<name>.a /usr/lib
