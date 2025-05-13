# agents/crew_setup.py

import os
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()

def build_marketing_crew() -> Crew:
    """
    Constructs a sequential Crew of three agents:
      1. Researcher    - analyzes scraped data
      2. ScriptWriter  - drafts a video prompt
      3. GapDetector   - identifies gaps and awaits human input
    """
    gemini_llm = LLM(
        model="gemini/gemini-2.0-flash",
        api_key=os.getenv("GOOGLE_API_KEY")
    )

    researcher = Agent(
        role="Researcher",
        goal="Analyze scraped data",
        backstory="An AI agent specialized in data analysis.",
        verbose=True,
        llm=gemini_llm
    )
    script_writer = Agent(
        role="ScriptWriter",
        goal="Draft video prompt",
        backstory="An AI agent skilled in script writing.",
        verbose=True,
        llm=gemini_llm
    )
    gap_detector = Agent(
        role="GapDetector",
        goal="Identify content gaps",
        backstory="An AI agent that identifies missing information.",
        verbose=True,
        human_input=True,  # expects human feedback
        llm=gemini_llm
    )

    task1 = Task(
        name="AnalyzeData",
        description="Analyze the scraped data and extract key insights.",
        expected_output="A summary of key insights from the data.",
        agent=researcher
    )
    task2 = Task(
        name="DraftScript",
        description="Draft a video script based on the insights.",
        expected_output="A video script prompt.",
        agent=script_writer
    )
    task3 = Task(
        name="IdentifyGaps",
        description="Review the script and identify any content gaps.",
        expected_output="List of questions for human input to fill gaps.",
        agent=gap_detector
    )

    crew = Crew(
        agents=[researcher, script_writer, gap_detector],
        tasks=[task1, task2, task3],
        process=Process.sequential,
        verbose=True
    )

    return crew
