"""Independent Queens solver and verified board importer."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARDS = ROOT / "data" / "queens_boards.json"


def solve(rows):
    n = len(rows)
    if not 5 <= n <= 12:
        raise ValueError("Unsupported board size")
    if any(len(row) != n for row in rows):
        raise ValueError("Board must be square")

    regions = set("".join(rows))
    if len(regions) != n:
        raise ValueError("Expected one region per row")

    solutions = []
    used_cols = set()
    used_regions = set()
    chosen = []

    def search(r):
        if len(solutions) >= 2:
            return
        if r == n:
            solutions.append(chosen.copy())
            return

        for c in range(n):
            region = rows[r][c]
            if c in used_cols or region in used_regions:
                continue
            if chosen and abs(c - chosen[-1] + 1) <= 1:
                continue

            used_cols.add(c)
            used_regions.add(region)
            chosen.append(c + 1)

            search(r + 1)

            chosen.pop()
            used_regions.remove(region)
            used_cols.remove(c)

    search(0)
    return solutions


def enrich_queens(day, daily):
    if not BOARDS.exists():
        return False

    boards = json.loads(BOARDS.read_text())
    board = boards.get(str(day))
    if not board:
        return False

    solutions = solve(board["regions"])
    if len(solutions) != 1:
        raise ValueError(
            f"Queens {day}: expected one unique solution, "
            f"found {len(solutions)} (maximum checked: 2)"
        )

    cols = solutions[0]
    number = f'#{board["number"]}'
    existing = daily.setdefault("games", {}).get("queens", {})

    if existing.get("number") not in (None, number):
        raise ValueError("Queens puzzle-number mismatch")

    old_answer = existing.get("answer") or {}
    if existing.get("status") == "verified":
        if old_answer.get("cols") and old_answer["cols"] != cols:
            raise ValueError("Independent solver disagrees with published answer")

    palette = board["palette"]
    full_regions = [
        [palette[symbol] for symbol in row]
        for row in board["regions"]
    ]

    daily["games"]["queens"] = {
        **existing,
        "status": "verified",
        "number": number,
        "hint": existing.get("hint", []),
        "source": board["source"],
        "answer": {
            **old_answer,
            "type": "queens",
            "cols": cols,
            "regions": full_regions
        }
    }

    print(f"Queens {number}: unique solution {cols}; full regions loaded")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="2026-11-02")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    file = ROOT / "data" / f"{args.date}.json"
    daily = json.loads(file.read_text())

    if enrich_queens(args.date, daily):
        if args.apply:
            file.write_text(
                json.dumps(daily, indent=2, ensure_ascii=False) + "\n"
            )
            print("Updated", file)
        else:
            print("Validation only; use --apply to save.")
