import os
import time
import random

data = []

right = 0
wrong = 0

def read_file():
   global data
   lines = open('states.dat').readlines()

   for line in lines:

      if line is "END":
         break

      parts = line.split(',')

      if len(parts) != 2:
          continue

      parts[1] = parts[1].strip()

   
      data.append(parts)

def score():
   if right+wrong == 0:
       return
   else:
       print "Score: %s / %s (%s %%)" % (right, right+wrong, right*1.0/(right+wrong))

def main():
   global right
   global wrong

   read_file()

   print " ** Answer each question.  Use '?' if you give up, q to quit **"

   while True:
      score()

      x = random.randint(0, len(data)-1)
      state_cap = random.randint(0,1)

      if state_cap == 0:
          astr = "%s is the capital of ______ > " % (data[x][0])
          answer = data[x][1]
      else:
          astr = "What is the capital of %s > " % (data[x][1])
          answer = data[x][0]

      while True:    
          resp = raw_input(astr)
          if resp == answer:
              print "Yay!"
              right = right + 1
              break
          elif resp == "?":
              print "Answer: %s" % (answer)
          elif resp == "q":
              print "Bye!"
              os.exit(0)
          else:
              wrong = wrong + 1
              print "Sorry, try again"

      time.sleep(0.5)

if __name__ == "__main__":
    main()



