from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import get_transcript, summarize_video
import os
from dotenv import load_dotenv

load_dotenv()

# Step 1 - Define  Model
client = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    
)

# Step 2 - Create Agent
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

# Step 3 - Invoke
res = search_agent.invoke({
    "messages": [
        HumanMessage(content="summarize this video: https://www.youtube.com/watch?v=your_id")
    ]
})

print(res["messages"][-1].content)