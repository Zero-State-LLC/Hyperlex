#!/usr/bin/env python3
"""Tests for ruling_queue helpers and apply behavior."""
import argparse
import contextlib
import io
import json
import os
import sqlite3
import tempfile
import unittest

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "v2"))
import ruling_queue as rq

DATE = "2026-10-20"


class QueueStemTests(unittest.TestCase):
    def test_plain_date(self):
        self.assertEqual(rq.queue_stem("2026-10-11"), "2026-10-11")
        self.assertEqual(rq.queue_stem("2026-10-11", ""), "2026-10-11")

    def test_suffix_b(self):
        self.assertEqual(rq.queue_stem("2026-10-11", "b"), "2026-10-11b")

    def test_invalid_suffix(self):
        with self.assertRaises(SystemExit):
            rq.queue_stem("2026-10-11", "b/c")


class PendingStemTests(unittest.TestCase):
    def test_answered_base_does_not_clear_suffixed_queue(self):
        with tempfile.TemporaryDirectory() as root:
            p = rq.paths(root)
            base = {
                "observation_id": "obs:base",
                "term_id": "term:base",
            }
            extra = {
                "observation_id": "obs:extra",
                "term_id": "term:extra",
            }
            with open(os.path.join(p["queue"], "2026-10-11.jsonl"), "w") as f:
                f.write(json.dumps(base) + "\n")
            with open(os.path.join(p["queue"], "2026-10-11b.jsonl"), "w") as f:
                f.write(json.dumps(extra) + "\n")
            # Answering the unsuffixed queue must not drop the b queue from pending.
            open(os.path.join(p["answered"], "2026-10-11.txt"), "w").close()
            pending = rq.pending_ids(p, "2026-10-11")
            self.assertEqual(pending, {"obs:extra"})
            terms = rq.terms_in_date_queues(p, "2026-10-11")
            self.assertEqual(terms, {"term:base", "term:extra"})


def queue_rows(labels=("SLANG_SENSE", "SLANG_SENSE", "OTHER_SENSE"),
               terms=("term:a", "term:a", "term:b")):
    rows = []
    for i, (lab, tid) in enumerate(zip(labels, terms), 1):
        name = tid.split(":", 1)[1]
        rows.append({"queue_id": f"{DATE}:{i:03d}", "rule_version": rq.RULE_VERSION, "queue_date": DATE,
                     "observation_id": f"obs:{i}", "term_id": tid, "term": name, "term_family": name,
                     "split": "train", "model_label": lab, "model_prob": 0.7, "text": "x",
                     "priority_reason": "unruled_term",
                     "answer": {"sense": None, "definition": None, "notes": None}})
    return rows


def make_root(root, **kw):
    p = rq.paths(root)
    with open(os.path.join(p["queue"], DATE + ".jsonl"), "w") as f:
        for r in queue_rows(**kw):
            f.write(json.dumps(r) + "\n")
    return p


def write(dirpath, name, text):
    path = os.path.join(dirpath, name)
    with open(path, "w") as f:
        f.write(text)
    return path


def make_db(path):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE operator_definitions(term_id TEXT, definition TEXT, defined_by TEXT, "
                "defined_at TEXT, source TEXT)")
    con.execute("CREATE TABLE operator_term_status(term_id TEXT PRIMARY KEY, status TEXT, recorded_by TEXT, "
                "recorded_at TEXT, source TEXT)")
    con.commit()
    con.close()
    return path


def ns(root, answers, **kw):
    d = dict(root=root, db=os.path.join(root, "none.sqlite3"), file=None, answers=answers, date=DATE,
             by="Tester", write_sqlite=False, dry_run=False, corrections_only=False,
             no_auto_corrections=False, update_existing=False)
    d.update(kw)
    return argparse.Namespace(**d)


def run(a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rq.cmd_apply(a)
    return buf.getvalue()


def status_rows(db):
    con = sqlite3.connect(db)
    rows = con.execute("SELECT term_id, status FROM operator_term_status").fetchall()
    con.close()
    return rows


class ParseAnswersTests(unittest.TestCase):
    def test_corrections_autodetect_and_expand(self):
        corr, co = rq.parse_answers(["Corrections only:", "002 O"])
        self.assertTrue(co)
        self.assertEqual(corr, {"002": ("O", None)})
        out = rq.expand_corrections(queue_rows(), corr)
        self.assertEqual([r["answer"]["sense"] for r in out], ["SLANG_SENSE", "OTHER_SENSE", "OTHER_SENSE"])
        self.assertEqual([r["answer_mode"] for r in out],
                         ["corrections_only_retained", "corrections_only_listed", "corrections_only_retained"])
        self.assertEqual(out[0]["answer"]["notes"], rq.RETAINED_NOTE)

    def test_expand_rejects_bad_model_label(self):
        with self.assertRaises(SystemExit):
            rq.expand_corrections(queue_rows(labels=("WEIRD", "SLANG_SENSE", "OTHER_SENSE")), {})

    def test_multipart_inline(self):
        corr, co = rq.parse_answers(["PART 1: 004 O, 013 S, 021 U", "PART 2: 5 R some def, with comma"])
        self.assertFalse(co)
        self.assertEqual(corr["004"], ("O", None))
        self.assertEqual(corr["013"], ("S", None))
        self.assertEqual(corr["021"], ("U", None))
        self.assertEqual(corr["005"], ("R", "some def, with comma"))

    def test_conflict_across_files(self):
        with tempfile.TemporaryDirectory() as d:
            f1 = write(d, "p1.txt", "001 S\n002 O\n")
            f2 = write(d, "p2.txt", "002 O\n001 R\n")
            with self.assertRaises(SystemExit):
                rq.parse_answers([f1, f2])
            f3 = write(d, "p3.txt", "001 S\n")
            corr, _ = rq.parse_answers([f1, f3])
            self.assertEqual(corr["001"], ("S", None))

    def test_prose_lines_skipped(self):
        lines = ["Test", "Validation", "Training", "R = target absent from the excerpt",
                 "notes: tricky batch", "001 S", "999 S", "002 Q"]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            corr, _ = rq.parse_answers(lines, valid={"001", "002"})
        out = buf.getvalue()
        self.assertEqual(corr, {"001": ("S", None)})
        self.assertNotIn("Test", out)
        self.assertNotIn("target absent", out)
        self.assertIn("ignored line: 999 S", out)
        self.assertIn("ignored line: 002 Q", out)


class ApplyTests(unittest.TestCase):
    def test_explicit_leaves_unlisted_unanswered(self):
        with tempfile.TemporaryDirectory() as root:
            p = make_root(root)
            f = write(root, "a.txt", "002 O\n")
            run(ns(root, [f]))
            L = rq.load_landing(p)
            self.assertEqual(len(L), 1)
            self.assertEqual(L[0]["sense"], "OTHER_SENSE")
            self.assertEqual(L[0]["answer_mode"], "explicit")
            self.assertTrue(os.path.exists(os.path.join(p["answered"], DATE + ".txt")))

    def test_corrections_autodetect_apply(self):
        with tempfile.TemporaryDirectory() as root:
            p = make_root(root)
            f = write(root, "a.txt", "Corrections only\n002 O\n")
            out = run(ns(root, [f]))
            L = rq.load_landing(p)
            self.assertEqual(len(L), 3)
            by = {r["queue_id"][-3:]: r for r in L}
            self.assertEqual(by["001"]["sense"], "SLANG_SENSE")
            self.assertEqual(by["001"]["answer_mode"], "corrections_only_retained")
            self.assertEqual(by["002"]["answer_mode"], "corrections_only_listed")
            self.assertIn('"retained": 2', out)

    def test_no_auto_corrections_flag(self):
        with tempfile.TemporaryDirectory() as root:
            p = make_root(root)
            f = write(root, "a.txt", "corrections only\n002 O\n")
            run(ns(root, [f], no_auto_corrections=True))
            L = rq.load_landing(p)
            self.assertEqual(len(L), 1)
            self.assertEqual(L[0]["answer_mode"], "explicit")

    def test_multi_file_combined_answered(self):
        with tempfile.TemporaryDirectory() as root:
            p = make_root(root)
            f1 = write(root, "p1.txt", "PART 1: 001 S, 002 O\n")
            f2 = write(root, "p2.txt", "PART 2: 003 U\n")
            run(ns(root, [f1, f2]))
            self.assertEqual(len(rq.load_landing(p)), 3)
            combined = open(os.path.join(p["answered"], DATE + ".answers.txt")).read()
            self.assertIn("# --- p1.txt", combined)
            self.assertIn("# --- p2.txt", combined)

    def test_update_existing(self):
        with tempfile.TemporaryDirectory() as root:
            p = make_root(root)
            run(ns(root, [write(root, "a.txt", "001 S\n")]))
            b = write(root, "b.txt", "001 O\n")
            # default: skip existing
            run(ns(root, [b]))
            self.assertEqual(rq.load_landing(p)[0]["sense"], "SLANG_SENSE")
            # dry run: no writes
            run(ns(root, [b], update_existing=True, dry_run=True))
            self.assertEqual(rq.load_landing(p)[0]["sense"], "SLANG_SENSE")
            out = run(ns(root, [b], update_existing=True))
            L = rq.load_landing(p)
            self.assertEqual(len(L), 1)
            self.assertEqual(L[0]["sense"], "OTHER_SENSE")
            self.assertEqual(L[0]["revised_from"], "SLANG_SENSE")
            self.assertEqual(L[0]["revision_source"], "b.txt")
            self.assertIn("revised_at", L[0])
            self.assertIn('"updated": 1', out)
            # same sense again: unchanged, no duplicate
            out = run(ns(root, [b], update_existing=True))
            self.assertEqual(len(rq.load_landing(p)), 1)
            self.assertIn('"unchanged": 1', out)

    def test_never_writes_term_status(self):
        with tempfile.TemporaryDirectory() as root:
            make_root(root)
            db = make_db(os.path.join(root, "v.sqlite3"))
            run(ns(root, [write(root, "a.txt", "001 R\n002 R\n")], db=db, write_sqlite=True))
            self.assertEqual(status_rows(db), [])

    def test_auto_reject_flag_removed(self):
        self.assertNotIn("auto_reject_terms", open(rq.__file__).read())

    def test_reject_gets_target_absent(self):
        with tempfile.TemporaryDirectory() as root:
            p = make_root(root)
            run(ns(root, [write(root, "a.txt", "001 R\n002 S\n")]))
            L = {r["queue_id"][-3:]: r for r in rq.load_landing(p)}
            self.assertEqual(L["001"]["row_status"], "TARGET_ABSENT")
            self.assertEqual(L["001"]["sense"], "REJECT")
            self.assertNotIn("row_status", L["002"])
            self.assertFalse(rq.is_gold(L["001"]))
            self.assertTrue(rq.is_gold(L["002"]))
            self.assertFalse(rq.is_gold({"sense": "SLANG_SENSE", "row_status": "TARGET_ABSENT"}))

    def test_retained_rows_carry_ratification(self):
        with tempfile.TemporaryDirectory() as root:
            p = make_root(root)
            run(ns(root, [write(root, "a.txt", "Corrections only. All unlisted rows retain the proposed labels.\n001 O\n")]))
            L = {r["queue_id"][-3:]: r for r in rq.load_landing(p)}
            self.assertNotIn("ratification_ref", L["001"])
            other = [r for k, r in L.items() if k != "001"]
            self.assertTrue(other)
            for r in other:
                self.assertEqual(r["ratification_ref"]["text"], "Corrections only. All unlisted rows retain the proposed labels.")


if __name__ == "__main__":
    unittest.main()
