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
