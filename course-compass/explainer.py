"""
Generate natural language explanations for study paths.

Now enriched with official prerequisites from prerequisites_official.jsonl
so that the explanation can mention the *full* prereq picture, not just
the minimal path in the graph.
"""

from typing import List, Dict, Any, Optional
import json
import networkx as nx

from config import get_langchain_llm, OFFICIAL_PREREQS_FILE

# Cache for official prerequisites loaded from JSONL
_official_prereqs: Optional[Dict[str, Dict[str, Any]]] = None


def _load_official_prereqs() -> Dict[str, Dict[str, Any]]:
    global _official_prereqs
    if _official_prereqs is not None:
        return _official_prereqs

    mapping: Dict[str, Dict[str, Any]] = {}

    try:
        with open(OFFICIAL_PREREQS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                code = obj.get("course_code")
                if code:
                    mapping[code] = obj
    except FileNotFoundError:
        print(f"WARNING: OFFICIAL_PREREQS_FILE not found: {OFFICIAL_PREREQS_FILE}")
    except Exception as e:
        print("WARNING: failed to load official prereqs:", repr(e))

    _official_prereqs = mapping
    return mapping


def _get_official_info(course_code: str) -> Dict[str, Any]:
    mapping = _load_official_prereqs()
    return mapping.get(course_code, {})


def _build_path_description(path: List[str], graph: nx.DiGraph) -> str:
    lines = []
    for i, course_code in enumerate(path, 1):
        node = graph.nodes[course_code]
        title = node.get("title", course_code)
        ects = node.get("ects", 0)
        lines.append(f"{i}. {course_code} - {title} ({ects} ECTS)")
    return "\n".join(lines)


def _fallback_explanation(path: List[str], graph: nx.DiGraph) -> str:
    if not path:
        return "No study path could be generated."

    total_ects = 0
    titles = []

    for code in path:
        node = graph.nodes[code]
        titles.append(node.get("title", code))
        total_ects += node.get("ects", 0)

    start = titles[0]
    end = titles[-1]

    sentences = []
    sentences.append(
        f"This study path takes you from foundational courses such as '{start}' "
        f"up to the target course '{end}'."
    )

    if len(path) > 2:
        sentences.append(
            "The intermediate courses gradually introduce the necessary mathematical and "
            "machine learning concepts, so that each step builds on the previous one."
        )

    sentences.append(
        f"In total, the path consists of {len(path)} courses and approximately {total_ects} ECTS."
    )
    sentences.append(
        "This is one possible path. The official course description may list several "
        "alternative prerequisite courses or combinations, so you should always check "
        "the DTU course base for the full set of acceptable prerequisites."
    )

    return " ".join(sentences)


def explain_study_path(path: List[str], graph: nx.DiGraph) -> str:
    """
    Explain a full study path from first course to target course.

    - Uses CampusAI via LangChain for a medium-length explanation.
    - Includes official prerequisite information (codes + text) if available.
    - Falls back to a deterministic explanation if anything fails.
    """
    if not path:
        return "No study path could be generated."

    path_text = _build_path_description(path, graph)
    target_code = path[-1]
    target_node = graph.nodes[target_code]
    target_title = target_node.get("title", target_code)
    target_str = f"{target_code} - {target_title}"

    # Look up official prereqs for the target course
    official = _get_official_info(target_code)
    official_codes = official.get("prereq_course_codes", [])
    official_text = official.get("prereq_text", "")

    codes_str = ", ".join(official_codes) if official_codes else "None listed"
    official_block = (
        f"Official prerequisites (course codes): {codes_str}\n"
        f"Official prerequisites (free text): {official_text or 'N/A'}\n"
    )

    prompt = (
        "You are advising a DTU student on how to reach a target course.\n\n"
        f"Target course:\n{target_str}\n\n"
        "Planned study path (in order):\n"
        f"{path_text}\n\n"
        "Below is the official prerequisite information from the course database.\n"
        "Use this to be precise about what is formally required or recommended.\n\n"
        f"{official_block}\n"
        "Write a clear, medium-length explanation (3–6 sentences) that:\n"
        "1) Summarizes the progression from fundamentals to the target course,\n"
        "2) Explains why this sequence makes sense academically,\n"
        "3) Mentions roughly how many courses and ECTS are in the suggested path,\n"
        "4) Clarifies that the official prerequisites may include multiple alternative "
        "courses (OR conditions), and that the student should ensure they satisfy one "
        "course from each such group (math, probability/statistics, programming, etc.).\n\n"
        "Keep the tone helpful and not too verbose."
    )

    llm = get_langchain_llm(temperature=0.4)

    try:
        response = llm.invoke(prompt)
        content = getattr(response, "content", None)
        if isinstance(content, str) and content.strip():
            return content.strip()
        return _fallback_explanation(path, graph)
    except Exception as e:
        print("LLM explanation failed in explain_study_path:", repr(e))
        return _fallback_explanation(path, graph)
