import json
import re
import argparse
from typing import List, Dict, Any

CODE_RE = re.compile(r"\b\d{5}\b")


def extract_prereq_codes(text) -> List[str]:
    """
    Extract DTU course codes (5-digit numbers) from the
    'Academic prerequisites' free-text field.
    """
    if text is None:
        return []

    # Ensure we always work with a string
    text = str(text)
    if not text.strip():
        return []

    codes = CODE_RE.findall(text)
    seen = set()
    ordered: List[str] = []

    for c in codes:
        if c not in seen:
            seen.add(c)
            ordered.append(c)

    return ordered



def process_file(input_path: str, output_path: str) -> None:
    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:

        for line in fin:
            line = line.strip()
            if not line:
                continue

            obj: Dict[str, Any] = json.loads(line)

            code = obj.get("course_code")
            title = obj.get("title", "")
            fields = obj.get("fields") or {}
            prereq_text = fields.get("Academic prerequisites", "") or ""

            prereq_codes = extract_prereq_codes(prereq_text)

            out = {
                "course_code": code,
                "title": title,
                "prereq_text": prereq_text,
                "prereq_course_codes": prereq_codes,
            }

            fout.write(json.dumps(out, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", default="dtu_courses.jsonl")
    parser.add_argument("--output", "-o", default="prerequisites_official.jsonl")
    args = parser.parse_args()

    process_file(args.input, args.output)
