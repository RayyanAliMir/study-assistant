import streamlit as st
from summarizer import summarize_text, answer_from_context
from rag import build_knowledge_base, retrieve_relevant_chunks
from database import init_db, log_question, get_all_questions, get_stats

init_db()

st.set_page_config(page_title="Study Assistant", page_icon="📚")
st.title("📚 Study Assistant")

if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

tab1, tab2, tab3 = st.tabs(["Summarize", "Ask Questions", "Analytics"])
with tab3:
    st.write("Your study activity over time.")

    stats = get_stats()
    st.metric("Total questions asked", stats["total_questions"])

    if stats["by_day"]:
        st.subheader("Questions per day")
        chart_data = {row["day"]: row["count"] for row in stats["by_day"]}
        st.bar_chart(chart_data)

    st.subheader("Question history")
    all_questions = get_all_questions()
    for q in all_questions:
        with st.expander(f"{q['question']}  —  {q['timestamp'][:10]}"):
            st.write(q["answer"])

with tab1:
    st.write("Paste your notes below and get an instant summary.")
    notes_for_summary = st.text_area("Your notes", height=200, key="summary_notes")

    if st.button("Summarize"):
        if notes_for_summary.strip() == "":
            st.warning("Please paste some notes first.")
        else:
            with st.spinner("Summarizing..."):
                summary = summarize_text(notes_for_summary)
            st.subheader("Summary")
            st.write(summary)

with tab2:
    st.write("Paste your notes once, then ask as many questions as you want.")
    notes_for_rag = st.text_area("Your notes", height=200, key="rag_notes")

    if st.button("Build Knowledge Base"):
        if notes_for_rag.strip() == "":
            st.warning("Please paste some notes first.")
        else:
            with st.spinner("Reading and understanding your notes..."):
                st.session_state.knowledge_base = build_knowledge_base(notes_for_rag, chunk_size=300)
            st.success(f"Knowledge base built with {len(st.session_state.knowledge_base)} chunks. Ask away!")

    if st.session_state.knowledge_base is not None:
        question = st.text_input("Ask a question about your notes")

        if st.button("Ask"):
            if question.strip() == "":
                st.warning("Please type a question first.")
            else:
                with st.spinner("Thinking..."):
                    relevant_chunks = retrieve_relevant_chunks(question, st.session_state.knowledge_base, top_n=3)
                    answer = answer_from_context(question, relevant_chunks)
                st.session_state.chat_history.append((question, answer))
                log_question(question, answer)

        for q, a in reversed(st.session_state.chat_history):
            st.markdown(f"**Q: {q}**")
            st.write(a)
            st.divider()