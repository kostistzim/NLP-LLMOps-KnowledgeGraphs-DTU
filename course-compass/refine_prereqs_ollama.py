import json
import argparse
from typing import Dict, List

from langchain_community.chat_models import ChatOllama


def load_courses(path: str) -> Dict[str, Dict]:
    courses: Dict[str, Dict] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            code = obj.get("course_code")
            if code:
                courses[code] = obj
    return courses


def refine_for_course(
    course: Dict,
    candidates: List[str],
    llm: ChatOllama,
    max_out: int = 7,
) -> List[str]:
    title = course.get("title", "")
    objectives = course.get("learning_objectives") or []

    prompt = (
        "You are helping define prerequisite knowledge for a university course.\n\n"
        "A prerequisite is a skill or concept the student should already know "
        "BEFORE taking the course, not something learned during the course.\n\n"
        f"Course title: {title}\n\n"
        "Learning objectives (what students learn during the course):\n"
        + "\n".join(f"- {obj}" for obj in objectives)
        + "\n\nCandidate concepts (may mix prerequisites and learning outcomes):\n"
        + "\n".join(f"- {c}" for c in candidates)
        + "\n\nFrom the candidate list, pick only those concepts that are true prerequisites, "
          "i.e., things the student is expected to know or have experience with BEFORE the course starts.\n"
          "Return your answer as a pure JSON list of strings, with no explanation and no extra text.\n"
          f"Include at most {max_out} items."
    )

    resp = llm.invoke(prompt)
    text = getattr(resp, "content", str(resp)).strip()

    data = json.loads(text)
    result: List[str] = [str(x).strip() for x in data if str(x).strip()]
    return result[:max_out]


def main(
    courses_path: str,
    input_cache: str,
    output_cache: str,
    model_name: str,
    max_out: int,
    limit: int,
) -> None:
    courses_by_code = load_courses(courses_path)
    llm = ChatOllama(model=model_name, temperature=0.0)

    with open(input_cache, "r", encoding="utf-8") as fin, \
         open(output_cache, "w", encoding="utf-8") as fout:

        for idx, line in enumerate(fin, 1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            code = obj.get("course_code")
            title = obj.get("title", "")
            candidates = obj.get("prerequisites") or []

            course = courses_by_code.get(
                code,
                {"course_code": code, "title": title, "learning_objectives": []},
            )

            if limit is not None and idx > limit:
                # For testing limit, just copy remaining lines unchanged
                obj["prerequisites"] = candidates
                fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
                continue

            print(f"[{idx}] Refining {code} ({title}) with {len(candidates)} candidates")

            if not candidates:
                refined: List[str] = []
            else:
                refined = refine_for_course(course, candidates, llm, max_out=max_out)

            obj["prerequisites"] = refined
            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--courses", "-c", default="dtu_courses.jsonl")
    parser.add_argument("--input", "-i", default="prerequisites_cache_nlp_clean.jsonl")
    parser.add_argument("--output", "-o", default="prerequisites_cache_llm_refined.jsonl")
    parser.add_argument("--model", "-m", default="mistral:7b-instruct-q4_0")
    parser.add_argument("--max_out", "-k", type=int, default=7)
    parser.add_argument("--limit", "-l", type=int, default=None, help="number of cache lines to process, for testing")
    args = parser.parse_args()

    main(
        courses_path=args.courses,
        input_cache=args.input,
        output_cache=args.output,
        model_name=args.model,
        max_out=args.max_out,
        limit=args.limit,
    )
