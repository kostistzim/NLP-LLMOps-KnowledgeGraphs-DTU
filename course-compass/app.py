import re
import requests
import streamlit as st

API_BASE = "http://localhost:8000"


def parse_message_for_courses(message: str):
    """
    Very simple parser:
    - Extract all 5-digit codes.
    - First code = target course.
    - Remaining codes = completed courses.
    If no codes found, return (None, []).
    """
    codes = re.findall(r"\b\d{5}\b", message)
    if not codes:
        return None, []
    target = codes[0]
    completed = codes[1:]
    return target, completed


st.set_page_config(page_title="CourseCompass Chat", layout="centered")
st.title("CourseCompass – Study Path Assistant")

st.write(
    "You can ask things like:\n"
    "- 'I want to take 02460 and I have not completed anything yet.'\n"
    "- 'Target 02460, completed 01003 and 02405.'\n"
    "The app will extract course codes from your message."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content)

user_msg = st.chat_input("Ask about a study path to a DTU course...")
if user_msg:
    # Add user message to history
    st.session_state.messages.append(("user", user_msg))
    with st.chat_message("user"):
        st.markdown(user_msg)

    # Parse message for course codes
    target_course, completed_courses = parse_message_for_courses(user_msg)

    if target_course is None:
        answer = (
            "I could not find any 5-digit DTU course codes in your message.\n\n"
            "Please mention at least one course code, for example: `02460` "
            "or `I want to reach 02460 and I have completed 01003`."
        )
    else:
        try:
            resp = requests.post(
                f"{API_BASE}/v1/generate-path",
                json={
                    "target_course": target_course,
                    "completed_courses": completed_courses,
                },
                timeout=30,
            )
            if resp.status_code != 200:
                answer = f"API error ({resp.status_code}):\n\n```json\n{resp.text}\n```"
            else:
                data = resp.json()
                path = data.get("path", [])
                explanation = data.get("explanation", "")
                total_ects = data.get("total_ects", 0)

                path_lines = []
                for i, c in enumerate(path, 1):
                    path_lines.append(
                        f"{i}. **{c['course_code']}** – {c['title']} ({c['ects']} ECTS)"
                    )

                answer = (
                    f"**Target course:** {data['target_course']}\n\n"
                    f"**Suggested path:**\n" +
                    "\n".join(path_lines) +
                    f"\n\n**Total ECTS in path:** {total_ects}\n\n"
                    f"**Explanation:**\n{explanation}"
                )
        except Exception as e:
            answer = f"Request to the FastAPI backend failed:\n\n`{e!r}`"

    # Add assistant message to history
    st.session_state.messages.append(("assistant", answer))
    with st.chat_message("assistant"):
        st.markdown(answer)
