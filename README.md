## Introduction ##
Our kids are in 2nd grade and 4th grade, and at that level there are lots of facts to learn -- in diverse subjects such as geography (states and their capitals), spelling, and math.  We as parents spent a lot of time running through lots of facts with the kids flashcard-style, and I thought it would be fun to work on some Python scripts to make this process simpler for us as parents, and maybe more fun for the kids.

I came up with three scripts that we've used to help the kids practice their school topics.  Surprisingly, they've seemed to enjoy it, even though it's just a command-line program (no pretty pictures, sorry).

I call this a "game", because I think of it as a game, but hopefully a fun and memory-building game!

Each game keeps track of the student's progress, and prints out the questions that the student asked for help with or got wrong.

## Prerequisites ##
### Python ###

pystudygame, if you didn't guess by the name, is a set of Python scripts.  You will need to install Python on your computer to use this game.  For Ubuntu Linux, python is probably already installed.  On Windows, download the Python installer from the following site:

 https://www.python.org/downloads/windows/

I recommend using the most recent version (3.8).

**When you get to the Python main install screen, MAKE SURE you select the option to add Python to the PATH environment variable.  You *WILL* have issues later in these instructions if you don't select this option.**

Once you have installed Python, do this to test it:
* Start Menu
* Type "Cmd"
* At the command prompt, type "python"
You should see a couple of lines of text followed by ">>>".
* Type "quit()" to exit.
* If you DON'T see the ">>>", there are a few possible causes:
   * If you see "command not found" or similar, Python was probably not added to the PATH environment variable. Run the installer again and say Modify and look for the option to add Python to system environment variables.
   * If you see an error about a DLL not being found, you might need to install the Visual C++ redistributable from here: https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads

###  pip ###
Ensure that the tool "pip" is installed with this command:

    py -3 -m ensurepip

### pyttsx3 (for text-to-speech spelling) ###
Install with this command:

    python -m pip install pyttsx3

It should end with a message about pyttsx3 being successfully installed.

### colorama (for colorized output) ###
Install with this command:

    python -m pip install colorama

It should end with a message about colorama being successfully installed.

## Installing the Scripts ##
When you have the prerequisites satisfied:
* click the "Clone or Download" link on this page.
* click "Download ZIP"
* Save the file to your computer
* Go to the folder on your computer where the zip file was downloaded.
* Unzip the file pystudygame-master.zip.

## Running the Scripts ##
Open a Command Prompt:
* Start Menu
* Type "cmd"
* Open the Command Prompt
* Once in the Command Prompt, navigate to the directory of the unzipped pystudygame.
* Run the game! Use the examples below as a guideline of what to type.

### States & Capitals ###
The states game (states.py) uses the provided states.dat file to ask the student questions of two forms:

* What is the capital of STATE?
* CITY is the capital of ______.

To use the game, provide the 2-letter abbreviations of the states you wish to study (see the example).

Example usage:

    python states.py IA MN FL GA

### Math ###
The math game (math.py) sets up a set of questions to ask to study math families.  The user specifies an operation to study (+, -, x, or /) and the numbers families to study.

Example usage:

    python math.py + 1 2 3 9 10

### Spelling ###

The spelling game (spelling.py) uses a text-to-speech engine to ask the student to spell words from a specified data file.  The format of the data file is lines of the following format:

 word,sentence

The voice will direct the student to spell the word.  The sentence can be spoken upon request to help understand the word and the context better.

Example usage:

    python spelling.py spelling-11.dat
