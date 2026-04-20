import csv
import random

# Number of questions to ask per session
num_questions = 10


def main():
    # Load all flashcards from CSV into memory and randomize order
    with open("flashcards.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        random.shuffle(rows)

        # Build a unique set of categories and prompt the user to choose one
        topics = {row["category"] for row in rows}
        print("Choose a topic:")

        for topic in topics:
            print("• " + topic)
        print("• all\n")
        choice = input("").strip()

        # Filter rows by chosen topic, or use all rows if "all" was selected.
        # excluded_rows are set aside so they can be written back to the CSV unchanged.
        excluded_rows = []
        filtered_rows = rows

        if choice != "all":
            excluded_rows = [row for row in rows if row["category"] != choice]
            filtered_rows = [row for row in rows if row["category"] == choice]

        # Split filtered rows into the active session and the remaining questions
        session_questions = filtered_rows[:num_questions]
        remainder = filtered_rows[num_questions:]

        correct = 0

        # Present each question and validate the user's input in a loop
        for row in session_questions:
            print(f"""{row['question']}
    (a): {row['a']}
    (b): {row['b']}
    (c): {row['c']}
    (d): {row['d']}""")

            while True:
                answer = input("What is your answer? ").strip().lower()
                if answer not in ["a", "b", "c", "d"]:
                    print("Invalid Input")
                elif answer == row["answer"]:
                    print("Correct!")
                    correct += 1
                    print("------------------------------------")
                    break
                else:
                    print(f"Wrong! The correct answer was {row['answer']}.")
                    # Increment miss counter so difficult cards can be tracked over time
                    row["times_missed"] = int(row["times_missed"]) + 1
                    print("------------------------------------")
                    break

        print(f"Score: {round((correct / len(session_questions) * 100))}%")

        # Write updated rows back to CSV, preserving the original column structure.
        # Session questions are written first (with updated times_missed), followed
        # by unseen questions and any excluded categories.
        fieldnames = reader.fieldnames
        with open("flashcards.csv", "w", newline="") as csvfile:
            rows = session_questions + remainder
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()
            writer.writerows(rows + excluded_rows)


if __name__ == "__main__":
    main()


"""
In Development:

Spaced repetition algorithm (highest value)
Right now times_missed is tracked but not really used for anything. 
The natural evolution is to weight card selection by that field — cards missed more often appear more frequently. 
Even a simple implementation (sort by times_missed descending, bias the shuffle toward the top) demonstrates you understand data-driven logic. 
A real spaced repetition system like SM-2 would be even more impressive and is well-documented, 
but even a homegrown weighted shuffle shows intentionality.

Session history / stats tracking
A separate stats.csv or JSON file that logs each session — date, topic, score, number of questions — 
lets you add a --history flag that shows performance trends over time. 
"Your Python score has improved from 60% to 85% over 6 sessions" is the kind of output that makes the tool feel alive rather than stateless.

Card management commands
Right now cards can only be added by manually editing the CSV. 
A simple --add mode that walks the user through entering a new question, answers, and category via prompts would make it self-contained. 
A --list flag to show all categories and card counts is also low effort but shows CLI design thinking.

argparse for proper CLI interface
The input()-based topic selection works but is fragile and not how real tools behave. 
Replacing it with argparse — so you can do python flashcards.py --topic Python --questions 15 — is a small change with a big signal. It's also more testable.

Weak card review mode
A --review flag that pulls only cards above a times_missed threshold (say, missed 3+ times) and drills just those. 
Combines the existing data with purposeful filtering — feels like a feature a real user would want.

Pytest coverage
Your Markov project has tests and a GitHub Actions workflow, which is already a strong signal. 
Bringing the same treatment here — testing the shuffle logic, the CSV read/write, the scoring calculation — makes the portfolio consistent and shows the tests weren't a one-off.
"""
