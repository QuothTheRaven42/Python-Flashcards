# Flashcard CLI

A command-line flashcard quiz tool that reads from a CSV file, lets you filter by topic, and tracks how many times you've missed each question across sessions.

## Features

- Filter questions by category or quiz on all topics at once
- 10 questions per session, shuffled randomly
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

You'll be shown a list of available categories and prompted to choose one or enter `all`. The quiz then runs through 10 random questions from your selection. After the session, the CSV is updated with any incremented miss counts.

## Notes

- Category names are case-sensitive at the prompt
- The `times_missed` column is updated in place after each session, so you can track which cards are giving you trouble over time
- Questions rotate each session — already-seen questions move to the end of the pool

## In Development:

**Spaced repetition algorithm (highest value)**
Right now times_missed is tracked but not really used for anything. 
The natural evolution is to weight card selection by that field — cards missed more often appear more frequently. 
Even a simple implementation (sort by times_missed descending, bias the shuffle toward the top) demonstrates you understand data-driven logic. 
A real spaced repetition system like SM-2 would be even more impressive and is well-documented, 
but even a homegrown weighted shuffle shows intentionality.

**Session history / stats tracking**
A separate stats.csv or JSON file that logs each session — date, topic, score, number of questions — 
lets you add a --history flag that shows performance trends over time. 
"Your Python score has improved from 60% to 85% over 6 sessions" is the kind of output that makes the tool feel alive rather than stateless.

**Card management commands**
Right now cards can only be added by manually editing the CSV. 
A simple --add mode that walks the user through entering a new question, answers, and category via prompts would make it self-contained. 
A --list flag to show all categories and card counts is also low effort but shows CLI design thinking.

**argparse for proper CLI interface**
The input()-based topic selection works but is fragile and not how real tools behave. 
Replacing it with argparse — so you can do python flashcards.py --topic Python --questions 15 — is a small change with a big signal. It's also more testable.

**Weak card review mode**
A --review flag that pulls only cards above a times_missed threshold (say, missed 3+ times) and drills just those. 
Combines the existing data with purposeful filtering — feels like a feature a real user would want.

**Pytest coverage**
Your Markov project has tests and a GitHub Actions workflow, which is already a strong signal. 
Bringing the same treatment here — testing the shuffle logic, the CSV read/write, the scoring calculation — makes the portfolio consistent and shows the tests weren't a one-off.
