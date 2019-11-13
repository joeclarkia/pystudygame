import os
import time
import random
import sys

if "TERM" not in os.environ:
    import colorama
    colorama.init()

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

if len(sys.argv) < 3:
    print("Usage: python game_m.py ACTION NUMBERS")
    print("   ACTION is one of + - x /")
    print("   NUMBERS is a space-separated string of numbers to practice")
    sys.exit(1)

action = sys.argv[1]
numbers = sys.argv[2:]

def gen_data():
    for i in numbers:
        val = int(i)
        for j in range(val+1):
            if action == "+":
                question = "%s + %s" % (j, val-j)
                answer = "%s" % val
                data.append([question, answer])
            elif action == "-":
                question = "%s - %s" % (val, j)
                answer = "%s" % (val - j)
                data.append([question, answer])
            elif action == "x":
                question = "%s * %s" % (val, j)
                answer = "%s" % (val * j)
                data.append([question, answer])
            elif action == "/":
                question = "%s / %s" % (val*j, val)
                answer = "%s" % (val*j / val)
                data.append([question, answer])
            else:
                print("Unknown action '%s'" % action)
                sys.exit(1)

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

   gen_data()

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

      q = questions_to_ask.pop(0)
      
      astr = "%s%s = ____ >%s " % (BLUE, data[q][0], NC)
      answer = data[q][1]

      while True:    
          print("Elapsed time: %.0f sec" % (time.time() - start_time))
          print(astr, end='')
          resp = input()
          if resp == answer:
              print("%s* * * * Correct * * * *%s" % (GREEN, NC))
              right = right + 1
              break
          elif resp == "?":
              print("%sAnswer: %s%s" % (YELLOW, answer, NC))
              help_list.append("%s : %s" % (astr, answer))
          elif resp == "q":
              quit()
          else:
              wrong = wrong + 1
              wrong_list.append("%s : '%s' (You said %s'%s')%s" % (astr, answer, YELLOW, resp, NC))
              print("%s! ! ! ! NOPE ! ! ! !%s" % (RED, NC))

      questions_answered = questions_answered + 1
      time.sleep(0.25)

   quit()

if __name__ == "__main__":
    main()



