# Flashcard CLI

A command-line flashcard quiz tool that reads from a CSV file, lets you filter by topic, and tracks how many times you've missed each question across sessions.

## Features

- Filter questions by category or quiz on all topics at once
- User-chosen amount of questions per session, shuffled randomly
- 555 questions included in flashcards.csv
- Multiple choice answers (a/b/c/d) with input validation
- Tracks missed answers persistently — the CSV is updated after every session
- Displays your score as a percentage at the end

## Requirements

- Python 3.10+
- No external dependencies

## Setup

The tool reads from a file called `flashcards.csv` in the same directory as the script. The CSV must have the following columns:

| Column | Description |
|--------|-------------|
| `question` | The question text |
| `a` | Answer choice A |
| `b` | Answer choice B |
| `c` | Answer choice C |
| `d` | Answer choice D |
| `answer` | The correct answer (`a`, `b`, `c`, or `d`) |
| `category` | Topic category for filtering |
| `times_missed` | Number of times this question has been answered incorrectly (start at `0`) |

### Example CSV

```
question,a,b,c,d,answer,category,times_missed
What does 'hello'[1] return?,e,h,l,o,a,strings,0,,
What is the output of bool(None)?,True,0,Error,False,d,data_types,0,,
What is the output of 'Python'[1:4]?,Pyt,yth,ytho,Pyth,b,strings,0,,
What exception is raised when a dictionary key doesn't exist?,IndexError,KeyError,ValueError,AttributeError,b,error_handling,0,,
What does 'abc' * 3 produce?,An error,abcabcabc,abc3,['abc',abc,'abc'],b,strings,0
```

## Usage
```bash
cd Python-Flashcards
python main.py
```

You'll be asked how many questions you want to review. Then you'll be shown a list of available categories and prompted to choose one, or you can enter `all` or `missed`. The quiz then runs through random questions based your selections. After the session, the CSV is updated with any incremented miss counts.

## Notes

- Category names are case-sensitive at the prompt
- The `times_missed` column is updated in place after each session, so you can track which cards are giving you trouble over time
- Questions rotate each session — already-seen questions move to the end of the pool

## In Development:

**Input validation and edge-case handling**
Right now some inputs can crash the program or create empty quiz sessions.
I want to tighten up topic selection, question count input, and no-results cases so the app behaves more reliably.

**Retry missed questions**
A useful next step is letting the user review the questions they got wrong at the end of a session.
That would make the tool more practical for studying and build on the times_missed logic already in place.

**Session history / stats tracking**
I’d like to log each quiz session to a separate CSV or JSON file with the date, topic, score, and number of questions.
That would make it possible to view recent performance and track improvement over time.

**Hardest cards report**
Since times_missed is already being tracked, I want to use it to show which cards are missed most often.
A simple report of the most-missed questions would make the app feel more data-driven and useful.

**Spaced repetition algorithm**
Right now times_missed is tracked but not really used for anything.
The natural next step is to weight card selection by that field so cards missed more often appear more frequently.

**Add / edit / delete flashcards**
At the moment, the program can quiz from a CSV, but managing cards still has to be done manually.
Adding command-line options for creating, editing, and deleting flashcards would make it feel more like a complete tool.

**argparse for proper CLI interface**
The current input()-based flow works, but it’s fragile and not how real command-line tools usually behave.
Replacing parts of it with argparse would allow commands like python flashcards.py --topic Python --questions 15 and make the script easier to test and extend.
