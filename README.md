Our kids are in 2nd grade and 4th grade, and at that level there are lots of facts to learn -- in diverse subjects such as geography (states and their capitals), spelling, and math.  We as parents spent a lot of time running through lots of facts with the kids flashcard-style, and I thought it would be fun to work on some Python scripts to make this process simpler for us as parents, and maybe more fun for the kids.

I came up with three scripts that we've used to help the kids practice their school topics.  Surprisingly, they've seemed to enjoy it, even though it's just a command-line program (no pretty pictures, sorry).

PS: I call this a "game", because I think of it as a game, but hopefully a fun and memory-building game!

Each game keeps track of the student's progress, and prints out the questions that the student asked for help with or got wrong.

== States & Capitals ==
The states game (states.py) uses the provided states.dat file to ask the student questions of two forms:

* What is the capital of STATE?
* CITY is the capital of ______.

To use the game, provide the 2-letter abbreviations of the states you wish to study (see the example).

Example usage:

    python states.py IA MN FL GA

== Math ==
The math game (math.py) sets up a set of questions to ask to study math families.  The user specifies an operation to study (+, -, x, or /) and the numbers families to study.

Example usage:

    python math.py + 1 2 3 9 10

== Spelling ==

The spelling game (spelling.py) uses a text-to-speech engine to ask the student to spell words from a specified data file.  The format of the data file is lines of the following format:

 word,sentence

The voice will direct the student to spell the word.  The sentence can be spoken upon request to help understand the word and the context better.

Dependency: pyttsx3 (https://pypi.org/project/pyttsx3/)
    To install: python -m pip install pyttsx3

If you run into problems installing pyttsx3 software, feel free to create a GitHub issue and request help -- I will aim to improve this documentation based on the feedback I receive.

