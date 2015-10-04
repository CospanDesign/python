#! /usr/bin/python


def func(): 
  print "In a function"
  f = open("text.txt")
  #print "File Contents:" + f.read()

  lines = f.readlines()

  print "List: " + str(lines)

  if (len(lines) == 0):
    print "no lines"
  elif(len(lines) > 0):
    print "More than 0"

  for line in lines:
    print "Line: " + line

def process_file(input_list, output_list):
  print "Hello"

  


if __name__ == "__main__":
  print "Hello World"
  func()
  find_list = ["word1", "word2"]

  '''
  filenames = sys.argv[1:]

  input_file = filenames[0]
  world_list_file = filename[1]

  print "input files: %s
  '''

  s1 = "hello my name is dave"
  
  if "my" in s1:
    print "Found my"

  before = s1.partition("my")[0]
  after = s1.partition("my")[2]

  insert_string = "your"

  s2 = before + insert_string + after

  print "output: " + s2

