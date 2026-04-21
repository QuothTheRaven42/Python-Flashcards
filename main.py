import csv
import random


def load_flashcards():
    # Load all flashcards from CSV into memory and randomize order
    with open("flashcards.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        rows = list(reader)
        if fieldnames is None:
            raise ValueError("CSV file has no header row")
    return rows, fieldnames


def filter_rows(rows, choice):
    # Filter rows by chosen topic, or use all rows if "all" was selected.
    # excluded_rows are set aside so they can be written back to the CSV unchanged.
    excluded_rows = []
    filtered_rows = rows

    if choice != "all" and choice != "missed":
        excluded_rows = [row for row in rows if row["category"] != choice]
        filtered_rows = [row for row in rows if row["category"] == choice]
    elif choice == "missed":
        excluded_rows = [row for row in rows if int(row["times_missed"]) == 0]
        filtered_rows = [row for row in rows if int(row["times_missed"]) > 0]

    return filtered_rows, excluded_rows


def run_quiz(session_questions):
    # the for loop over all questions — it owns the tally and the final score print.
    correct = 0
    for row in session_questions:
        if ask_question(row):
            correct += 1
    return correct


def ask_question(row):
    # everything currently inside that for loop —
    # the question display, the while True input validation, the correct/wrong feedback,
    # and the times_missed increment. One row in, one boolean out.
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
            print("------------------------------------")
            return True
        else:
            print(f"Wrong! The correct answer was {row['answer']}.")
            # Increment miss counter so difficult cards can be tracked over time
            row["times_missed"] = int(row["times_missed"]) + 1
            print("------------------------------------")
            return False


def save_flashcards(fieldnames, session_questions, remainder, excluded_rows):
    # Session questions are written first, 'times_missed' updated
    with open("flashcards.csv", "w", newline="") as csv_file:
        rows = session_questions + remainder
        writer = csv.DictWriter(csv_file, fieldnames)
        writer.writeheader()
        writer.writerows(rows + excluded_rows)


def main():
    rows, fieldnames = load_flashcards()
    print(f"{len(rows)} flashcards loaded!\n")
    random.shuffle(rows)

    # Build a unique set of categories and prompt the user to choose one
    topics = {row["category"] for row in rows}
    print("Choose a topic:")
    for topic in topics:
        print("• " + topic)
    print("• all\n• missed")
    choice = input("").strip()

    filtered_rows, excluded_rows = filter_rows(rows, choice)
    # Number of questions to ask per session
    num_questions = int(input("How many questions would you like to review? "))
    # Split filtered rows into the active session and the remaining questions
    session_questions = filtered_rows[:num_questions]
    remainder = filtered_rows[num_questions:]

    correct = run_quiz(session_questions)
    print(f"Score: {round((correct / len(session_questions) * 100))}%")

    save_flashcards(fieldnames, session_questions, remainder, excluded_rows)


if __name__ == "__main__":
    main()

"""
Spaced repetition algorithm (highest value)
Right now times_missed is tracked but not really used for anything. 
The natural evolution is to weight card selection by that field — cards missed more often appear more frequently. 
Even a simple implementation (sort by times_missed descending, bias the shuffle toward the top) demonstrates you understand data-driven logic. 
A real spaced repetition system like SM-2 would be even more impressive and is well-documented.

Session history / stats tracking
A separate stats.csv or JSON file that logs each session — date, topic, score, number of questions — 
lets you add a --history flag that shows performance trends over time. 

argparse for proper CLI interface
The input()-based topic selection works but is fragile and not how real tools behave. 
Replacing it with argparse — so you can do python flashcards.py --topic Python --questions 15 — is a small change with a big signal. It's also more testable.

Pytest coverage
Testing the shuffle logic, the CSV read/write, the scoring calculation — makes the portfolio consistent and shows the tests weren't a one-off.
"""
