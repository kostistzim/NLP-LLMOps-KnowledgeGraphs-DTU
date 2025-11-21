import streamlit as st
import requests
import time

st.set_page_config(
    page_title="DTU Course Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .course-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
        color: #000000;
    }
    .answer-box {
        background: #e8f4f8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        color: #000000;
        font-size: 1.1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #145a8c;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'query' not in st.session_state:
    st.session_state.query = ""

# Header
st.markdown('<p class="main-header">🎓 DTU Course Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Ask questions about DTU courses and get AI-powered answers</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    mode = st.selectbox(
        "Retrieval Mode",
        ["dense", "sparse", "hybrid"],
        help="Dense: Semantic search | Sparse: Keyword matching | Hybrid: Both"
    )
    
    top_k = st.slider(
        "Number of courses to retrieve",
        min_value=1,
        max_value=10,
        value=5,
        help="More courses = more context for AI"
    )
    
    if mode == "hybrid":
        alpha = st.slider(
            "Hybrid weight (alpha)",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            help="1.0 = pure dense, 0.0 = pure sparse"
        )
    else:
        alpha = 0.5
    
    st.divider()
    
    st.header("💡 Example Questions")
    st.write("Click to try:")
    
    examples = [
        "How many ECTS is Tue Herlau's course?",
        "Are there courses about MRI?",
        "Which course is Hiba Nassar involved in?",
        "Does Ivana Konvalenka teach with another teacher?"
    ]
    
    for example in examples:
        if st.button(example, key=f"example_{example}", use_container_width=True):
            st.session_state.query = example
            st.rerun()

# Main content
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    # Input
    query = st.text_input(
        "Your question:",
        placeholder="e.g., How many ECTS is Tue Herlau's course?",
        value=st.session_state.query
    )
    
    # Update session state
    if query != st.session_state.query:
        st.session_state.query = query
    
    ask_button = st.button("🔍 Ask Question", use_container_width=True)

    if ask_button and query:
        with st.spinner("🤔 Thinking..."):
            try:
                # Add artificial delay for better UX
                start_time = time.time()
                
                response = requests.get(
                    "http://localhost:8000/v1/ask",
                    params={
                        "query": query,
                        "mode": mode,
                        "top_k": top_k,
                        "alpha": alpha
                    },
                    timeout=30
                )
                
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Display answer
                    st.markdown("### 💬 Answer")
                    st.markdown(f'<div class="answer-box">{data["answer"]}</div>', unsafe_allow_html=True)
                    
                    # Display retrieved courses
                    st.markdown("### 📚 Retrieved Courses")
                    
                    for i, course in enumerate(data['retrieved_courses'], 1):
                        st.markdown(
                            f'<div class="course-card">'
                            f'<strong>{i}. {course["course_code"]}</strong><br>'
                            f'{course["title"]}'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    
                    # Metrics
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Response Time", f"{elapsed:.2f}s")
                    with col_b:
                        st.metric("Courses Retrieved", len(data['retrieved_courses']))
                    with col_c:
                        st.metric("Mode", mode.capitalize())
                    
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The API might be building indices (takes ~30 sec on first start).")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure it's running on http://localhost:8000")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    elif ask_button:
        st.warning("⚠️ Please enter a question first!")

# Footer
st.divider()
col_f1, col_f2, col_f3 = st.columns(3)
with col_f2:
    st.markdown(
        "<p style='text-align: center; color: #666;'>"
        "Powered by FastAPI + Sentence Transformers + DSPy"
        "</p>",
        unsafe_allow_html=True
    )