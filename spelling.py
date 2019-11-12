import os
import time
import random
import sys
import pyttsx3
import threading


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

def Sayer(astr):
    print("Loading speech module...")
    speaker = pyttsx3.init()
    print("Speech module loaded!")
    speaker.say(astr)
    speaker.runAndWait()

def joeSay(astr):
    t = threading.Thread(target=Sayer, args=[astr])
    t.start()

def read_file(filename):
   global data
   lines = open(filename).readlines()

   for line in lines:

      if line is "END":
         break

      parts = line.split(',')

      # word to spell is only valid column
      if len(parts) < 1:
          continue

      parts[0] = parts[0].strip()

      try:
          data.append(parts[0])

      except ValueError:
          pass

def score():
   if right+wrong == 0:
       return
   else:
       print("Score: %s / %s (%.2f %%)" % (right, right+wrong, 100*right*1.0/(right+wrong)))

def print_list(alist, astr):
    if len(alist) == 0:
        return

    print("-----------------------------------------------")
    print("%s:" % astr)
    print("-----------------------------------------------")
    for item in alist:
        print(" * %s" % item)
    print("")

def quit():
    print("")
    print_list(help_list, "%sYou asked for help with these%s" % (YELLOW, NC))
    print_list(wrong_list, "%sYou got these wrong%s" % (RED, NC))
    print("")
    score()
    print("")
    tdiff = time.time() - start_time
    if questions_answered > 0:
       tpq = "%.1f" % (tdiff / questions_answered)
    else:
       tpq = "N/A"
    print("Elapsed time: %.0f sec (%s sec / question)" % (tdiff, tpq))
    print("Bye!")
    sys.exit(0)

def main():
   global right
   global wrong
   global start_time
   global questions_answered
   global states

   if len(sys.argv) > 1 and sys.argv[1] == "-h":
       print("Usage: python game.py [INITIALS]")
       print("   INITIALS: a space-separated list of states to study, e.g., IL IN MS")
       print("     if no initials are given, then all 50 states will be studied.")
       sys.exit(0)

   filename = 'states.dat'
   if len(sys.argv) > 1:
       filename = sys.argv[1]

   print(" * Loading filename %s" % filename)
   read_file(filename)

   print(" ** Answer each question.  Use '?' if you give up, q to quit **")

   questions_to_ask = []
   for i in range(len(data)):
       questions_to_ask.append(i)

   random.shuffle(questions_to_ask)

   print(questions_to_ask)

   start_time = time.time()

   while len(questions_to_ask) > 0:
      score()

      print(" %s questions to go" % (len(questions_to_ask)))

      x = questions_to_ask.pop(0)
      
      answer = data[x]

      joeSay("Spell the word %s" % (answer))

      while True:    
          print("Elapsed time: %.0f sec" % (time.time() - start_time))

          # Python < 3
          #resp = raw_input(astr)

          resp = input("> ")
          if resp == answer:
              print("%s* * * * Correct * * * *%s" % (GREEN, NC))
              #joeSay("You got it right!")
              right = right + 1
              break
          elif resp == "h":
              print(" . : repeat the word to spell")
              print(" ? : I give up, give me the answer")
              print(" q : quit")
          elif resp == ".":
              joeSay("Spell the word %s" % (answer))
          elif resp == "?":
              print("%sAnswer: '%s'%s" % (YELLOW, answer, NC))
              help_list.append("%s : %s" % (resp, answer))
          elif resp == "q":
              quit()
          else:
              wrong = wrong + 1
              wrong_list.append("%s : '%s' (You said %s'%s'%s)" % (resp, answer, YELLOW, resp, NC))
              #joeSay("No that's not quite right, Try again")
              print("%s! ! ! ! NOPE ! ! ! !%s" % (RED, NC))

      questions_answered = questions_answered + 1
      time.sleep(0.25)

   quit()

if __name__ == "__main__":
    main()

