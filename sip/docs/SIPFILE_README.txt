
Inside a SIP file we attach to a header file of the language

Here is an example of interfacing with a C++ file

// Define the SIP wrapper to the word library

%Module word

class Word {

%TypeHeaderCode
#include <word.h>
%End

public:
  Word (const char * w);
  char *reverse() const;

};


## Notes:

Declare the name of the python module that is generated
  %Module <name>

Add verbatum code into the wrapper

  %TypeHeaderCode
    <Whatever is here will be added into the code SIP generates>
  %End








# Instructions for Creating a SIP binding

Create the Header File

<c filename>.h

Create the SIP file

<sip filename>.sip

Create the sip output

sip -c . <sip filename>.sip


