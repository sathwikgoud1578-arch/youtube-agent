import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent
from tools import get_transcript, summarize_video
from dotenv import load_dotenv
import os

load_dotenv()

# ── Setup ──
client = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)

search_agent = create_agent(
    model=client,
    tools=[get_transcript, summarize_video],
    system_prompt=SystemMessage(
        content="""
        You are a YouTube Video Summarizer Assistant.
        When user gives a YouTube URL:
        1. Use summarize_video tool to fetch the transcript
        2. Write a clean paragraph summary of the entire video in 5-6 sentences
        3. Do NOT use bullet points or headers
        4. Write in simple plain English like explaining to a friend
        For follow-up questions, use get_transcript tool with the video URL and answer from it.
        Never rely on internal knowledge, always use tools.
        """
    )
)

# ── Streamlit UI ──
st.set_page_config(page_title="YouTube AI Agent", page_icon="🎙️")
st.title("🎙️ YouTube Video Summarizer")

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "youtube_url" not in st.session_state:
    st.session_state.youtube_url = ""

# Input
youtube_url = st.text_input("Paste YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

if st.button("📋 Summarize Video") and youtube_url:
    st.session_state.youtube_url = youtube_url
    with st.spinner("Summarizing..."):
        res = search_agent.invoke({
            "messages": [
                HumanMessage(content=f"summarize this video: {youtube_url}")
            ]
        })
        last_message = res["messages"][-1].content
        if isinstance(last_message, list):
            summary = " ".join([
                item["text"] for item in last_message
                if isinstance(item, dict) and item.get("type") == "text"
            ])
        else:
            summary = last_message

        st.markdown(summary)
        st.session_state.chat_history.append({"role": "assistant", "content": summary})

st.divider()
st.markdown("### 💬 Ask Follow-up Questions")

# Show chat history
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input
user_input = st.chat_input("Ask anything about the video...")
if user_input:
    st.chat_message("user").write(user_input)
    with st.spinner("Thinking..."):
        res = search_agent.invoke({
            "messages": [
                HumanMessage(content=f"{user_input} (video: {st.session_state.youtube_url})")
            ]
        })
        last_message = res["messages"][-1].content
        if isinstance(last_message, list):
            answer = " ".join([
                item["text"] for item in last_message
                if isinstance(item, dict) and item.get("type") == "text"
            ])
        else:
            answer = last_message

    st.chat_message("assistant").write(answer)
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": answer})