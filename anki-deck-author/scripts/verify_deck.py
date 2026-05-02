"""verify_deck.py — sanity-check an .apkg before delivering to the user."""
import json
import os
import re
import sqlite3
import sys
import tempfile
import zipfile


def verify(apkg_path: str) -> int:
    if not os.path.exists(apkg_path):
        print(f"ERROR: {apkg_path} does not exist")
        return 1

    print(f"Verifying: {apkg_path}")
    print(f"Size:      {os.path.getsize(apkg_path) / 1024:.1f} KB\n")

    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(apkg_path) as zf:
            zf.extractall(tmp)

        # Locate the SQLite collection
        for fname in ("collection.anki21", "collection.anki2"):
            db_path = os.path.join(tmp, fname)
            if os.path.exists(db_path):
                break
        else:
            print("ERROR: no SQLite collection found in package")
            return 1

        # Media manifest
        media = json.load(open(os.path.join(tmp, "media")))
        media_files = set(media.values())
        print(f"Media manifest: {len(media)} entries\n")

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Models
        models = json.loads(cur.execute("SELECT models FROM col").fetchone()[0])
        print("Models:")
        for mid, m in models.items():
            flds = [f["name"] for f in m["flds"]]
            tmpls = [t["name"] for t in m["tmpls"]]
            kind = "CLOZE" if m.get("type") == 1 else "STANDARD"
            print(f"  {m['name']:50s}  [{kind}]")
            print(f"    fields:    {flds}")
            print(f"    templates: {tmpls}")
        print()

        # Decks
        decks = json.loads(cur.execute("SELECT decks FROM col").fetchone()[0])
        print("Decks:")
        for did, d in decks.items():
            if d["name"] != "Default":
                # Count cards in this deck
                count = cur.execute("SELECT COUNT(*) FROM cards WHERE did = ?", (did,)).fetchone()[0]
                print(f"  {d['name']:50s}  {count} cards")
        print()

        # Counts
        n_notes = cur.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        n_cards = cur.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
        print(f"Total notes: {n_notes}")
        print(f"Total cards: {n_cards}\n")

        # Cards-per-template breakdown
        rows = cur.execute("""
            SELECT n.mid, c.ord, COUNT(*)
            FROM cards c JOIN notes n ON c.nid = n.id
            GROUP BY n.mid, c.ord
            ORDER BY n.mid, c.ord
        """).fetchall()
        print("Cards per model/template:")
        for mid, ord_, count in rows:
            m = models[str(mid)]
            mname = m["name"]
            # Cloze models have one template but produce ord=0,1,2... per deletion
            if m.get("type") == 1:
                tmpl = f"cloze c{ord_ + 1}"
            else:
                tmpl = m["tmpls"][ord_]["name"] if ord_ < len(m["tmpls"]) else f"ord {ord_}"
            print(f"  {mname[:40]:40s}  {tmpl[:25]:25s}  {count}")
        print()

        # Media reference check
        referenced = set()
        for (flds,) in cur.execute("SELECT flds FROM notes"):
            for m in re.finditer(r'src=["\']([^"\']+\.(png|jpg|jpeg|gif|svg|mp3|wav|ogg))["\']', flds, re.I):
                referenced.add(m.group(1))
        missing = referenced - media_files
        print(f"Image references in notes: {len(referenced)}")
        print(f"Missing media files:       {len(missing)}")
        if missing:
            print(f"  Examples: {list(missing)[:5]}")
            print("  FAIL: notes reference media not in package.")
            conn.close()
            return 1
        print()

        # Sample notes per model
        print("Sample notes:")
        for mid in models:
            sample = cur.execute(
                "SELECT flds FROM notes WHERE mid = ? LIMIT 1", (int(mid),)
            ).fetchone()
            if sample:
                first_field = sample[0].split("\x1f")[0]
                print(f"  [{models[mid]['name'][:25]:25s}] {first_field[:90]}")

        conn.close()

    print("\n✓ Verification passed.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_deck.py path/to/deck.apkg")
        sys.exit(2)
    sys.exit(verify(sys.argv[1]))
