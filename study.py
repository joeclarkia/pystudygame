import os
import time
import random
import sys
import pyttsx3
import threading

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

def Sayer(astr):
    speaker = pyttsx3.init()
    speaker.say(astr)
    try:
        speaker.runAndWait()
    except RuntimeError as re:
        print("%sError trying to play sound, try command again%s" % (RED, NC))

def joeSay(astr):
    t = threading.Thread(target=Sayer, args=[astr])
    t.start()

def read_file(filename):
   global data
   lines = open(filename).readlines()

   for line in lines:
      parts = line.split(',')

      # word to spell is only valid column
      if len(parts) < 1:
          continue

      parts[0] = parts[0].strip()
      if len(parts) > 1:
          parts[1] = parts[1].strip()

      try:
          data.append(parts)

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

   if len(sys.argv) < 2:
       print("%sMust specify spelling list filename%s" % (RED, NC))
       sys.exit(1)
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

      item = data[x]
      
      answer = item[0]
      sentence = None
      if len(item) > 1:
          sentence = item[1]

      #joeSay("%s" % (sentence))
      print("%s%s%s" % (YELLOW, sentence, NC))

      while True:    
          print("Elapsed time: %.0f sec" % (time.time() - start_time))

          print("(h for help) > %s" % (BLUE), end='')
          resp = input()

          print("%s" % (NC)),

          if resp == answer:
              print("%s* * * * Correct * * * *%s" % (GREEN, NC))
              right = right + 1
              break
          elif resp == "h":
              print(" . : repeat the word to spell")
              print(" s : say the word in a sentence")
              print(" ? : I give up, give me the answer")
              print(" q : quit")
          #elif resp == "s":
          #    if sentence:
          #        joeSay(sentence)
          #    else:
          #        print("%sNo sentence provided%s" % (YELLOW, NC))
          elif resp == ".":
               print("%s%s%s" % (YELLOW, sentence, NC))
               #joeSay("%s" % (sentence))
          elif resp == "?":
              print("%sAnswer: '%s'%s" % (YELLOW, answer, NC))
              help_list.append("%s : %s" % (resp, answer))
          elif resp == "q":
              quit()
          elif resp == "":
              pass
          else:
              wrong = wrong + 1
              wrong_list.append("%s : '%s' (You said %s'%s'%s)" % (resp, answer, YELLOW, resp, NC))
              print("%s! ! ! ! NOPE ! ! ! !%s" % (RED, NC))
              print("%s'%s' is NOT correct%s" % (RED, resp, NC))

      questions_answered = questions_answered + 1
      time.sleep(0.25)

   quit()

if __name__ == "__main__":
    main()

