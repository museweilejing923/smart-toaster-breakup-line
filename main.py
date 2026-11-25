"""4,096 slices and a double-pressed lever: the toaster's goodbye, checked and printed."""

import string
import sys
import unicodedata
from pathlib import Path

ENTRY = "I need space. I have toasted 4,096 slices for you and you still press the lever twice like you don't trust me. I'm leaving, and I'm taking the settings with me."
MAX_LEN = 280
CLOSERS = ".!?"
OUT_PATH = Path("/output/entry.txt")


class EntryError(Exception):
    """One of the entry rules was broken."""


class EntryChecker:
    """Validates the fixed entry in three passes: shape, wording, topic."""

    def __init__(self, sentence):
        self.sentence = sentence

    def run(self):
        self._shape_pass()
        self._wording_pass()
        self._topic_pass()
        self._fresh_pass()

    def _fresh_pass(self):
        # A breakup line must not open with a digit: "4,096 slices"
        # on its own is a count, not a sentence, so a leading digit
        # means the line starts in the wrong place.
        text = self.sentence
        if text[:1].isdigit():
            raise EntryError("must not start with a digit")

    def _shape_pass(self):
        text = self.sentence
        if len(text) > MAX_LEN:
            raise EntryError("over %d characters" % MAX_LEN)
        if not text.strip():
            raise EntryError("blank entry")
        if any(unicodedata.category(ch) == "Cc" for ch in text):
            raise EntryError("control character found")
        if text.strip() != text or "  " in text or "\n" in text or "\r" in text:
            raise EntryError("ragged edges, double space, or line break")
        if not text or text[-1] not in CLOSERS:
            raise EntryError("must end with . ! or ?")

    def _wording_pass(self):
        text = self.sentence
        letters = [ch for ch in text if ch.isalpha()]
        if text and all(ch in string.punctuation for ch in text):
            raise EntryError("punctuation only")
        if text.isdigit():
            raise EntryError("digits only")
        if not letters:
            raise EntryError("no letters")
        if any(a == b == c for a, b, c in zip(text, text[1:], text[2:])):
            raise EntryError("one character repeated three times in a row")
        if "---" in text:
            raise EntryError("triple hyphen is not a sentence")

    def _topic_pass(self):
        if "lever" not in self.sentence.casefold():
            raise EntryError("must mention the lever")


def emit():
    try:
        EntryChecker(ENTRY).run()
    except EntryError as problem:
        sys.stderr.write("invalid: %s\n" % problem)
        raise SystemExit(1)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(ENTRY + "\n", encoding="utf-8")


if __name__ == "__main__":
    emit()
