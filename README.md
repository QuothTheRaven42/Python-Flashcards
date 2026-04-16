# Flashcard CLI

A command-line flashcard quiz tool that reads from a CSV file, lets you filter by topic, and tracks how many times you've missed each question across sessions.

## Features

- Filter questions by category or quiz on all topics at once
- 10 questions per session, shuffled randomly
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
"What is the output of (lambda x, y: x + y)(3, 4)?",34,Error,12,7,d,functions,0
```

## Usage
```bash
cd python-flashcards
python main.py
```

You'll be shown a list of available categories and prompted to choose one or enter `all`. The quiz then runs through 10 random questions from your selection. After the session, the CSV is updated with any incremented miss counts.

## Notes

- Category names are case-sensitive at the prompt
- The `times_missed` column is updated in place after each session, so you can track which cards are giving you trouble over time
- Questions rotate each session — already-seen questions move to the end of the pool
