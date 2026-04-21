import csv
import io
import pytest
from unittest.mock import patch, mock_open
from main import filter_rows, ask_question, run_quiz, load_flashcards, save_flashcards


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_row(question="Q", answer="a", category="Python", times_missed=0):
    return {
        "question": question,
        "a": "opt a", "b": "opt b", "c": "opt c", "d": "opt d",
        "answer": answer,
        "category": category,
        "times_missed": str(times_missed),
    }


FIELDNAMES = ["question", "a", "b", "c", "d", "answer", "category", "times_missed"]


# ---------------------------------------------------------------------------
# filter_rows
# ---------------------------------------------------------------------------

class TestFilterRows:

    def test_category_filter_returns_only_matching_rows(self):
        rows = [make_row(category="Python"), make_row(category="Python"), make_row(category="OOP")]
        filtered, excluded = filter_rows(rows, "Python")
        assert all(r["category"] == "Python" for r in filtered)
        assert len(filtered) == 2

    def test_category_filter_excludes_non_matching_rows(self):
        rows = [make_row(category="Python"), make_row(category="OOP")]
        filtered, excluded = filter_rows(rows, "Python")
        assert all(r["category"] == "OOP" for r in excluded)
        assert len(excluded) == 1

    def test_all_returns_every_row_with_no_exclusions(self):
        rows = [make_row(category="Python"), make_row(category="OOP")]
        filtered, excluded = filter_rows(rows, "all")
        assert filtered == rows
        assert excluded == []

    def test_missed_returns_only_rows_with_misses(self):
        rows = [make_row(times_missed=3), make_row(times_missed=0), make_row(times_missed=1)]
        filtered, excluded = filter_rows(rows, "missed")
        assert all(int(r["times_missed"]) > 0 for r in filtered)
        assert len(filtered) == 2

    def test_missed_excludes_rows_with_zero_misses(self):
        rows = [make_row(times_missed=3), make_row(times_missed=0)]
        filtered, excluded = filter_rows(rows, "missed")
        assert all(int(r["times_missed"]) == 0 for r in excluded)

    def test_category_with_no_matches_returns_empty_filtered(self):
        rows = [make_row(category="OOP"), make_row(category="OOP")]
        filtered, excluded = filter_rows(rows, "Python")
        assert filtered == []
        assert len(excluded) == 2

    def test_missed_with_no_missed_rows_returns_empty_filtered(self):
        rows = [make_row(times_missed=0), make_row(times_missed=0)]
        filtered, excluded = filter_rows(rows, "missed")
        assert filtered == []
        assert len(excluded) == 2

    def test_filter_does_not_mutate_original_rows(self):
        rows = [make_row(category="Python"), make_row(category="OOP")]
        original_len = len(rows)
        filter_rows(rows, "Python")
        assert len(rows) == original_len


# ---------------------------------------------------------------------------
# ask_question
# ---------------------------------------------------------------------------

class TestAskQuestion:

    def test_correct_answer_returns_true(self):
        row = make_row(answer="b")
        with patch("builtins.input", return_value="b"), patch("builtins.print"):
            result = ask_question(row)
        assert result is True

    def test_wrong_answer_returns_false(self):
        row = make_row(answer="b")
        with patch("builtins.input", return_value="c"), patch("builtins.print"):
            result = ask_question(row)
        assert result is False

    def test_wrong_answer_increments_times_missed(self):
        row = make_row(answer="b", times_missed=2)
        with patch("builtins.input", return_value="c"), patch("builtins.print"):
            ask_question(row)
        assert row["times_missed"] == 3

    def test_correct_answer_does_not_increment_times_missed(self):
        row = make_row(answer="b", times_missed=1)
        with patch("builtins.input", return_value="b"), patch("builtins.print"):
            ask_question(row)
        assert row["times_missed"] == "1"

    def test_invalid_input_then_correct_returns_true(self):
        row = make_row(answer="a")
        inputs = iter(["z", "a"])
        with patch("builtins.input", side_effect=inputs), patch("builtins.print"):
            result = ask_question(row)
        assert result is True

    def test_invalid_input_then_wrong_returns_false(self):
        row = make_row(answer="a")
        inputs = iter(["!", "d"])
        with patch("builtins.input", side_effect=inputs), patch("builtins.print"):
            result = ask_question(row)
        assert result is False

    def test_invalid_input_does_not_increment_times_missed(self):
        row = make_row(answer="a", times_missed=0)
        # two invalid inputs, then correct
        inputs = iter(["x", "y", "a"])
        with patch("builtins.input", side_effect=inputs), patch("builtins.print"):
            ask_question(row)
        assert row["times_missed"] == "0"

    def test_multiple_invalid_inputs_before_wrong_answer(self):
        row = make_row(answer="a", times_missed=0)
        inputs = iter(["x", "y", "d"])
        with patch("builtins.input", side_effect=inputs), patch("builtins.print"):
            result = ask_question(row)
        assert result is False
        assert row["times_missed"] == 1


# ---------------------------------------------------------------------------
# run_quiz
# ---------------------------------------------------------------------------

class TestRunQuiz:

    def test_all_correct_returns_full_count(self):
        questions = [make_row() for _ in range(4)]
        with patch("main.ask_question", return_value=True):
            assert run_quiz(questions) == 4

    def test_all_wrong_returns_zero(self):
        questions = [make_row() for _ in range(4)]
        with patch("main.ask_question", return_value=False):
            assert run_quiz(questions) == 0

    def test_mixed_results_tallied_correctly(self):
        questions = [make_row() for _ in range(5)]
        answers = [True, False, True, True, False]
        with patch("main.ask_question", side_effect=answers):
            assert run_quiz(questions) == 3

    def test_single_question_correct(self):
        questions = [make_row()]
        with patch("main.ask_question", return_value=True):
            assert run_quiz(questions) == 1

    def test_single_question_wrong(self):
        questions = [make_row()]
        with patch("main.ask_question", return_value=False):
            assert run_quiz(questions) == 0


# ---------------------------------------------------------------------------
# load_flashcards
# ---------------------------------------------------------------------------

class TestLoadFlashcards:

    def test_loads_rows_and_fieldnames(self, tmp_path):
        csv_file = tmp_path / "flashcards.csv"
        csv_file.write_text(
            "question,a,b,c,d,answer,category,times_missed\n"
            "What is 2+2?,3,4,5,6,b,Math,0\n"
        )
        with patch("main.open", mock_open(read_data=csv_file.read_text())):
            # Use real file for simplicity
            pass
        # Test using actual tmp file via monkeypatching open
        import main
        original = main.open if hasattr(main, "open") else open
        with patch("builtins.open", lambda *a, **kw: csv_file.open(*a[1:], **kw) if a[0] == "flashcards.csv" else original(*a, **kw)):
            rows, fieldnames = load_flashcards()
        assert len(rows) == 1
        assert rows[0]["question"] == "What is 2+2?"
        assert "category" in fieldnames

    def test_raises_on_missing_file(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                load_flashcards()


# ---------------------------------------------------------------------------
# save_flashcards
# ---------------------------------------------------------------------------

class TestSaveFlashcards:

    def _read_csv_output(self, tmp_path):
        with open(tmp_path / "flashcards.csv", newline="") as f:
            return list(csv.DictReader(f))

    def test_all_rows_written(self, tmp_path):
        session = [make_row(question="Q1", times_missed=1)]
        remainder = [make_row(question="Q2")]
        excluded = [make_row(question="Q3")]
        out_file = tmp_path / "flashcards.csv"

        with patch("builtins.open", lambda *a, **kw: out_file.open("w", newline=kw.get("newline", ""))):
            save_flashcards(FIELDNAMES, session, remainder, excluded)

        rows = self._read_csv_output(tmp_path)
        questions = [r["question"] for r in rows]
        assert "Q1" in questions
        assert "Q2" in questions
        assert "Q3" in questions

    def test_session_written_before_remainder(self, tmp_path):
        session = [make_row(question="Session")]
        remainder = [make_row(question="Remainder")]
        out_file = tmp_path / "flashcards.csv"

        with patch("builtins.open", lambda *a, **kw: out_file.open("w", newline=kw.get("newline", ""))):
            save_flashcards(FIELDNAMES, session, remainder, [])

        rows = self._read_csv_output(tmp_path)
        assert rows[0]["question"] == "Session"
        assert rows[1]["question"] == "Remainder"

    def test_updated_times_missed_persisted(self, tmp_path):
        session = [make_row(question="Q1", times_missed=5)]
        out_file = tmp_path / "flashcards.csv"

        with patch("builtins.open", lambda *a, **kw: out_file.open("w", newline=kw.get("newline", ""))):
            save_flashcards(FIELDNAMES, session, [], [])

        rows = self._read_csv_output(tmp_path)
        assert rows[0]["times_missed"] == "5"

    def test_fieldnames_preserved_in_header(self, tmp_path):
        out_file = tmp_path / "flashcards.csv"
        with patch("builtins.open", lambda *a, **kw: out_file.open("w", newline=kw.get("newline", ""))):
            save_flashcards(FIELDNAMES, [], [], [])

        with open(out_file, newline="") as f:
            reader = csv.DictReader(f)
            assert list(reader.fieldnames) == FIELDNAMES