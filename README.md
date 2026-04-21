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

**Spaced repetition algorithm (highest value)**
Right now times_missed is tracked but not really used for anything. 
The natural evolution is to weight card selection by that field — cards missed more often appear more frequently. 
Even a simple implementation (sort by times_missed descending, bias the shuffle toward the top) demonstrates you understand data-driven logic. 

**argparse for proper CLI interface**
The input()-based topic selection works but is fragile and not how real tools behave. 
Replacing it with argparse — so you can do python flashcards.py --topic Python --questions 15 — is a small change with a big signal. It's also more testable.
