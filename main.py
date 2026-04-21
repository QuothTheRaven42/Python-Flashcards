import csv
import random


def load_flashcards():
    # Read the CSV into memory so the file can be closed immediately after.
    # fieldnames is captured here while the reader is still attached to the file.
    with open("flashcards.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        rows = list(reader)
        if fieldnames is None:
            raise ValueError("CSV file has no header row")
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
        excluded_rows = [row for row in rows if int(row["times_missed"]) == 0]
        filtered_rows = [row for row in rows if int(row["times_missed"]) > 0]

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
    print(f"""{row['question']}
    (a): {row['a']}
    (b): {row['b']}
    (c): {row['c']}
    (d): {row['d']}""")

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
            row["times_missed"] = int(row["times_missed"]) + 1
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
        print("• " + topic)
    print("• all\n• missed")
    choice = input("").strip()

    filtered_rows, excluded_rows = filter_rows(rows, choice)

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
    session_questions = filtered_rows[:num_questions]
    remainder = filtered_rows[num_questions:]

    correct = run_quiz(session_questions)
    print(f"Score: {round((correct / len(session_questions) * 100))}%")

    save_flashcards(fieldnames, session_questions, remainder, excluded_rows)


if __name__ == "__main__":
    main()

"""
╔════════════════════════════════════════════════════════════════════════════╗
║                      FLASHCARD APP FEATURE ROADMAP                         ║
║                    (Organized from easiest to hardest)                     ║
╚════════════════════════════════════════════════════════════════════════════╝

PHASE 1: BUG FIXES & ROBUSTNESS (Do these first!)
═══════════════════════════════════════════════════

  [ ] FIX: Validate topic choice
      • If user enters invalid topic, print "Topic not found" and re-prompt
      • Don't silently create empty session
      • Suggested: wrap in try/except or while loop

  [ ] FIX: Validate question count input
      • Handle non-integer input (e.g., "ten", blank, negative)
      • Use try/except with ValueError
      • Suggest max available: "Only 8 available. Use that? (y/n)"

  [ ] FIX: Handle empty session gracefully
      • If session_questions is empty, print message and exit
      • Prevents division by zero in score calculation

  [ ] FIX: Preserve original CSV row order
      • Don't shuffle the original rows list
      • Only shuffle a copy for the session
      • Save back in original order (easier debugging later)

  [ ] FIX: Validate CSV headers on load
      • Check that required fields exist: question, a, b, c, d, answer, category, times_missed
      • Print clear error if any missing
      • Makes debugging broken CSVs much easier

  [ ] FIX: Handle missing flashcards.csv file
      • Catch FileNotFoundError and print helpful message
      • Don't crash with traceback

═══════════════════════════════════════════════════════════════════════════

PHASE 2: QUALITY OF LIFE (Small, high-value improvements)
═══════════════════════════════════════════════════════════

  [ ] Auto-cap question count if user asks for more than available
      • Example: user asks for 20, only 8 exist → silently use 8
      • Add: num_questions = min(num_questions, len(filtered_rows))

  [ ] Sort topics alphabetically before printing
      • Change: topics = {row["category"] for row in rows}
      • To:     topics = sorted({row["category"] for row in rows})
      • Looks more professional

  [ ] Convert times_missed to int on load
      • In load_flashcards(), after reading CSV:
        for row in rows:
            row["times_missed"] = int(row["times_missed"])
      • Makes rest of code cleaner

  [ ] Show detailed results at end of session
      • Instead of just percentage, show:
        • Correct: 7, Wrong: 3, Score: 70%
        • Or: "You got 7 out of 10 correct"

  [ ] Add a "quit early" option during quiz
      • In ask_question(), allow input like "q" to quit
      • Calculate score only on answered questions
      • Teaches: breaking from loops, signaling between functions

═══════════════════════════════════════════════════════════════════════════

PHASE 3: USEFUL FEATURES (Build real value)
═════════════════════════════════════════════

  [ ] Retry missed questions at end of session
      • After quiz, ask: "Retry the questions you missed? (y/n)"
      • Run missed_questions through ask_question() again
      • Show final score
      • Improves learning and is genuinely useful

  [ ] Show "hardest cards" report
      • After session (or as separate mode):
      • Sort all cards by times_missed descending
      • Print top 5-10 hardest cards
      • Example: "Python Basics: 8 misses" "Lists vs Tuples: 5 misses"
      • Uses data you already collect!

  [ ] Show category statistics
      • New option: "--stats" or prompt at start
      • Display: "Python: 12 cards (3 missed)" etc.
      • Helps user see where they need work

  [ ] Implement simple weighted card selection
      • Cards missed more often appear more in the session
      • Beginner version: cards with higher times_missed get repeated in pool
      • Example: times_missed=0 adds 1 copy, times_missed=3 adds 4 copies
      • Teaches: data-driven selection, lists vs weighted probability
      • Not a perfect spaced-repetition, but demonstrates the concept

═══════════════════════════════════════════════════════════════════════════

PHASE 4: CREATE & MANAGE CARDS (Expand beyond quiz mode)
══════════════════════════════════════════════════════════

  [ ] Add new flashcard interactively
      • New function: add_flashcard()
      • Prompt for: question, a, b, c, d, correct answer, category
      • Set times_missed = 0
      • Append to CSV
      • Turns tool from study-only to card-creation tool

  [ ] List all cards (optional: by category)
      • Print questions + answer key
      • Useful for reviewing/printing
      • Optional: group by category

  [ ] Delete a flashcard
      • Prompt user for question text (or number)
      • Confirm deletion
      • Rewrite CSV without that row
      • Teaches: filtering, confirmation UX, data deletion

  [ ] Edit an existing flashcard
      • Find card by question text
      • Prompt which field to edit (question, a, b, c, d, answer, category)
      • Rewrite CSV
      • Teaches: finding, updating, validation

═══════════════════════════════════════════════════════════════════════════

PHASE 5: SESSION HISTORY & INSIGHTS (Gamification + learning data)
═════════════════════════════════════════════════════════════════

  [ ] Log each session to session_history.csv
      • New file with columns: date, topic, num_questions, correct, score_percent
      • Append after each quiz
      • Example row: "2024-01-15, Python, 10, 8, 80%"

  [ ] Show recent session history
      • New mode: "--history" or menu option
      • Display last 5-10 sessions
      • Shows: date, topic, score

  [ ] Calculate average score by topic
      • From session_history.csv:
      • "Python avg: 78% (5 sessions)"
      • "Math avg: 65% (3 sessions)"
      • Helps user see which topics need work

  [ ] Show score trends (simple version)
      • Most recent 5 sessions in order
      • Visual: print scores side by side
      • Example: "Recent: 65% → 70% → 75% → 80% → 82%"
      • Teaches: list sorting, data visualization basics

  [ ] Calculate longest streak (during session)
      • Track consecutive correct answers
      • Display: "Current streak: 4" and "Best streak: 7"
      • Shows current streak on each question
      • Gamifies the experience

═══════════════════════════════════════════════════════════════════════════

PHASE 6: COMMAND-LINE INTERFACE (Make it feel like a real tool)
═══════════════════════════════════════════════════════════════

  [ ] Refactor input prompts into helper functions
      • get_topic_choice(topics) → returns valid topic
      • get_num_questions(max_available) → returns valid int
      • Makes main() much cleaner
      • Reduces code duplication

  [ ] Add argparse for CLI arguments
      • Allow: python flashcards.py --topic Python --questions 10
      • Allow: python flashcards.py --stats
      • Allow: python flashcards.py --history
      • Allow: python flashcards.py --add (interactive add mode)
      • Makes tool feel professional
      • More scriptable (can automate)

  [ ] Create a menu system (optional)
      • Instead of immediate quiz, show menu:
        [1] Quiz  [2] Stats  [3] History  [4] Add Card  [5] Quit
      • Each option calls relevant function
      • More user-friendly

═══════════════════════════════════════════════════════════════════════════

PHASE 7: NICE-TO-HAVES (Polish & advanced features)
═════════════════════════════════════════════════════

  [ ] Implement true spaced repetition (SM-2 algorithm)
      • Research SM-2 (simple, well-documented)
      • Add: last_reviewed, repetitions, ease_factor to CSV
      • Weight card selection by days since last review
      • More sophisticated than Phase 3 weighted selection

  [ ] Add card difficulty rating
      • After each question, ask: "How hard was that? (easy/medium/hard)"
      • Use to weight future selection
      • Complements times_missed data

  [ ] Shuffle choice: randomize or most-missed-first
      • Prompt: "Random order or hardest first? (r/h)"
      • Gives user control over session strategy

  [ ] Export sessions to JSON
      • Instead of/in addition to CSV history
      • Better for parsing, timestamps, structure

  [ ] Backup CSV before overwriting
      • Create flashcards.csv.bak before saving
      • Safety feature (beginner-friendly way to learn backups)

  [ ] Add a "practice mode" vs "test mode"
      • Practice: show answer immediately, no score
      • Test: hide answer, track score
      • Different workflows

═══════════════════════════════════════════════════════════════════════════

RECOMMENDED EXECUTION ORDER:

Week 1-2:  Phases 1 & 2 (make it robust and clean)
Week 3-4:  Phase 3 (add useful features)
Week 5:    Phase 4 (card management)
Week 6+:   Phases 5 & 6 (history, CLI, polish)
Later:     Phase 7 (advanced features)

═══════════════════════════════════════════════════════════════════════════

NOTES:

• Each item should be a commit (git add, git commit)
  → Teaches version control
  → Let's you roll back if something breaks
  
• Test manually after each feature
  → Try edge cases (empty input, wrong data, etc.)
  
• When stuck, break into smaller steps
  → "Add feature X" can become "print the thing" → "get input" → "save it"
  
• Phases build on each other
  → Phase 3 uses Phase 1/2 foundations
  → Don't skip Phase 1, it prevents bugs later

═══════════════════════════════════════════════════════════════════════════
"""
