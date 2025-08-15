import json
from collections import defaultdict
from pathlib import Path
from typing import Dict


def make_name_char_bigram_table(
    corpus_path: str | Path, out_path: str | Path
) -> Dict[str, Dict[str, float]]:
    """Build a character bigram probability table from a corpus.

    Parameters
    ----------
    corpus_path:
        Path to a text file where each line contains a single shikona name.
    out_path:
        Destination for the generated JSON table. The function returns the
        table as a nested dictionary mapping a character to the probability of
        following characters. Start ("^") and end ("$") sentinels are
        included so the table can be used for name generation.
    """
    counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    path = Path(corpus_path)
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            name = line.strip()
            if not name:
                continue
            chars = ["^", *name, "$"]
            for a, b in zip(chars, chars[1:], strict=False):
                counts[a][b] += 1

    table: Dict[str, Dict[str, float]] = {}
    for prev, nexts in counts.items():
        total = sum(nexts.values())
        table[prev] = {
            nxt: count / total for nxt, count in sorted(nexts.items())
        }

    out = Path(out_path)
    out.write_text(
        json.dumps(table, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    return table
