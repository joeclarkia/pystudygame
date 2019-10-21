import os
import time
import random
import sys

data = []

right = 0
wrong = 0

BLUE="\033[95m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
CYAN="\033[36m"
NC="\033[0m"

help_list = []
wrong_list = []

start_time = None
questions_answered = 0

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
       print "Score: %s / %s (%.2f %%)" % (right, right+wrong, 100*right*1.0/(right+wrong))

def print_list(alist, astr):
    if len(alist) == 0:
        return

    print("-----------------------------------------------")
    print("%s:" % astr)
    print("-----------------------------------------------")
    for item in alist:
        print " * %s" % item
    print ""

def quit():
    print ""
    print_list(help_list, "%sYou asked for help with these%s" % (YELLOW, NC))
    print_list(wrong_list, "%sYou got these wrong%s" % (RED, NC))
    print ""
    score()
    print ""
    tdiff = time.time() - start_time
    if questions_answered > 0:
       tpq = "%.1f" % (tdiff / questions_answered)
    else:
       tpq = "N/A"
    print "Elapsed time: %.0f sec (%s sec / question)" % (tdiff, tpq)
    print "Bye!"
    sys.exit(0)

def main():
   global right
   global wrong
   global start_time
   global questions_answered

   read_file()

   print " ** Answer each question.  Use '?' if you give up, q to quit **"

   questions_to_ask = []
   for i in range(len(data)*2):
       questions_to_ask.append(i)

   random.shuffle(questions_to_ask)

   print questions_to_ask

   start_time = time.time()

   while len(questions_to_ask) > 0:
      score()

      print " %s questions to go" % (len(questions_to_ask))

      x = questions_to_ask.pop(0)
      q = int(x/2)
      
      if x%2 == 0:
          astr = "%s%s is the capital of ______ > %s" % (BLUE, data[q][0], NC)
          answer = data[q][1]
      else:
          astr = "%sWhat is the capital of %s > %s" % (BLUE, data[q][1], NC)
          answer = data[q][0]

      while True:    
          print "Elapsed time: %.0f sec" % (time.time() - start_time)
          resp = raw_input(astr)
          if resp == answer:
              print "%s* * * * Correct * * * *%s" % (GREEN, NC)
              right = right + 1
              break
          elif resp == "?":
              print "%sAnswer: %s%s" % (YELLOW, answer, NC)
              help_list.append("%s : %s" % (astr, answer))
          elif resp == "q":
              quit()
          else:
              wrong = wrong + 1
              wrong_list.append("%s : %s" % (astr, answer))
              print "%s! ! ! ! NOPE ! ! ! !%s" % (RED, NC)

      questions_answered = questions_answered + 1
      time.sleep(0.25)

   quit()

if __name__ == "__main__":
    main()



