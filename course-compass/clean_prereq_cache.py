import json
import argparse
import re
from typing import List, Dict

# Phrases we consider too generic or clearly outcome/task-related
BAD_SUBSTRINGS = [
    "students project",
    "fellow students project",
    "student project",
    "project work",
    "group project",
    "group work",
    "case study",
    "case studies",
    "assignment",
    "assignments",
    "homework",
    "report writing",
    "presentation",
    "presentations",
]

# Verbs that strongly suggest "what you will do in the course"
VERB_PREFIXES = [
    "implement",
    "design",
    "develop",
    "evaluate",
    "analyze",
    "analyse",
    "apply",
    "use",
    "learn",
    "understand",
    "be able",
    "will be able",
    "perform",
    "run",
    "automate",
    "optimize",
    "build",
    "test",
]

# Words that usually indicate course logistics, not prereqs
NOISE_WORDS = [
    "student",
    "students",
    "project",
    "projects",
    "experiment",
    "experiments",
    "laboratory",
    "lab",
    "supervision",
    "collaboration",
    "feedback",
    "group",
    "team",
]


MIN_LEN = 4      # min characters
MAX_WORDS = 8    # max words in a phrase


def should_drop(concept: str, code: str, title: str) -> bool:
    c = concept.strip()
    if not c:
        return True

    c_norm = c.lower()
    title_norm = title.lower()

    # Drop if it contains the course code
    if code and code.lower() in c_norm:
        return True

    # Drop if it contains the title without leading code
    title_no_code = re.sub(r"^\s*\d+\s*", "", title_norm).strip()
    if title_no_code and title_no_code in c_norm:
        return True

    # Drop very short or very long phrases
    if len(c_norm) < MIN_LEN:
        return True

    words = c_norm.split()
    if len(words) > MAX_WORDS:
        return True

    # Drop phrases starting with "outcome verbs" (implement, design, ...)
    for v in VERB_PREFIXES:
        if c_norm.startswith(v + " ") or c_norm.startswith("to " + v + " "):
            return True

    # Drop if any noise word appears anywhere
    for w in NOISE_WORDS:
        if w in c_norm:
            return True

    # Drop known bad substrings
    for bad in BAD_SUBSTRINGS:
        if bad in c_norm:
            return True

    return False


def clean_prereqs(prereqs: List[str], code: str, title: str, max_concepts: int = 7) -> List[str]:
    seen = set()
    cleaned: List[str] = []

    for p in prereqs:
        if should_drop(p, code, title):
            continue
        key = p.lower().strip()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(p)
        if len(cleaned) >= max_concepts:
            break

    return cleaned


def main(input_path: str, output_path: str, max_concepts: int) -> None:
    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:

        for line in fin:
            line = line.strip()
            if not line:
                continue
            obj: Dict = json.loads(line)

            code = (obj.get("course_code") or "").strip()
            title = (obj.get("title") or "").strip()
            prereqs = obj.get("prerequisites") or []

            cleaned = clean_prereqs(prereqs, code, title, max_concepts=max_concepts)
            obj["prerequisites"] = cleaned

            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", default="prerequisites_cache_nlp.jsonl")
    parser.add_argument("--output", "-o", default="prerequisites_cache_nlp_clean.jsonl")
    parser.add_argument("--max_concepts", "-k", type=int, default=7)
    args = parser.parse_args()

    main(args.input, args.output, args.max_concepts)
