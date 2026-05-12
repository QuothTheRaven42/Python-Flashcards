import csv
import random

REQUIRED_FIELDS = {"question", "a", "b", "c", "d", "answer", "category", "times_missed"}


def parse_times_missed(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def load_flashcards():
    # Read the CSV into memory so the file can be closed immediately after.
    # fieldnames is captured here while the reader is still attached to the file.
    with open("flashcards.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        rows = list(reader)
        if fieldnames is None:
            raise ValueError("CSV file has no header row")
        missing = REQUIRED_FIELDS - set(fieldnames)
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise ValueError(f"CSV file is missing required headers: {missing_list}")
    return rows, fieldnames


def filter_rows(rows, choice):
    # Default to using all rows with no exclusions
    excluded_rows = []
    filtered_rows = rows

    if choice != "all" and choice != "missed":
        # Separate rows by category; excluded rows are preserved so they can
        # be written back to the CSV unchanged at the end of the session.
        excluded_rows = [row for row in rows if row["category"] != choice]
        filtered_rows = [row for row in rows if row["category"] == choice]
    elif choice == "missed":
        # Only surface cards the user has previously answered wrong
        excluded_rows = [row for row in rows if parse_times_missed(row.get("times_missed")) == 0]
        filtered_rows = [row for row in rows if parse_times_missed(row.get("times_missed")) > 0]

    return filtered_rows, excluded_rows


def run_quiz(session_questions):
    # Iterate over the session questions and tally correct answers
    correct = 0
    for row in session_questions:
        if ask_question(row):
            correct += 1
    return correct


def ask_question(row):
    # Display the question and its four answer choices
    print(
        f"{row['question']}\n"
        f"    (a): {row['a']}\n"
        f"    (b): {row['b']}\n"
        f"    (c): {row['c']}\n"
        f"    (d): {row['d']}"
    )

    # Keep prompting until the user enters a valid choice
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
            # Track misses so difficult cards surface more often in "missed" mode
            row["times_missed"] = parse_times_missed(row.get("times_missed")) + 1
            print("------------------------------------")
            return False


def save_flashcards(fieldnames, session_questions, remainder, excluded_rows):
    # Write all rows back to the CSV in a consistent order:
    # session questions first (with updated times_missed), then unseen questions,
    # then any categories that were excluded from this session.
    with open("flashcards.csv", "w", newline="") as csv_file:
        rows = session_questions + remainder
        writer = csv.DictWriter(csv_file, fieldnames)
        writer.writeheader()
        writer.writerows(rows + excluded_rows)


def main():
    rows, fieldnames = load_flashcards()
    print(f"{len(rows)} flashcards loaded!\n")

    # Shuffle so questions appear in a different order each session
    random.shuffle(rows)

    # Build a unique set of categories from the loaded data and prompt the user
    topics = {row["category"] for row in rows}
    print("Choose a topic:")
    for topic in topics:
        print("- " + topic)
    print("- all\n- missed")

    valid_choices = topics | {"all", "missed"}
    while True:
        choice = input("").strip()
        if choice in valid_choices:
            break
        print("Topic not found. Please choose one from the list.")

    # Validate that the user enters a positive integer for the question count
    while True:
        try:
            num_questions = int(input("How many questions would you like to review? "))
            if num_questions <= 0:
                print("Please enter a positive number.")
                continue
            break
        except ValueError:
            print("Please enter a valid integer.")

    # Slice the filtered rows into the active session and whatever remains unseen
    filtered_rows, excluded_rows = filter_rows(rows, choice)
    session_questions = filtered_rows[:num_questions]
    remainder = filtered_rows[num_questions:]

    if not session_questions:
        print("No questions available for that topic/filter.")
        save_flashcards(fieldnames, session_questions, remainder, excluded_rows)
        return

    correct = run_quiz(session_questions)
    print(f"Score: {round((correct / len(session_questions) * 100))}%")

    save_flashcards(fieldnames, session_questions, remainder, excluded_rows)


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError:
        print("Could not find flashcards.csv. Make sure the file exists in this folder.")
    except ValueError as error:
        print(f"CSV data error: {error}")
