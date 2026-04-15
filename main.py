import csv
import random

num_questions = 10


def reading_csv():
    with open("flashcards.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        random.shuffle(rows)

        topics = {row["category"] for row in rows}
        print("Choose a topic (match case):")

        for topic in topics:
            print("• " + topic)
        print("• all\n")
        choice = input("").strip()

        excluded_rows = []
        filtered_rows = rows

        if choice != "all":
            excluded_rows = [row for row in rows if row["category"] != choice]
            filtered_rows = [row for row in rows if row["category"] == choice]

        session_questions = filtered_rows[:num_questions]
        remainder = filtered_rows[num_questions:]

        correct = 0

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
                    row["times_missed"] = int(row["times_missed"]) + 1
                    print("------------------------------------")
                    break

        print(f"Score: {round((correct / len(session_questions) * 100))}%")

        fieldnames = reader.fieldnames
        with open("flashcards.csv", "w", newline="") as csvfile:
            rows = session_questions + remainder
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()
            writer.writerows(rows + excluded_rows)


reading_csv()
