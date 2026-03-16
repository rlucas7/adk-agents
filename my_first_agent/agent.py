import asyncio
import os

from google.adk.agents.llm_agent import Agent
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.planners import BuiltInPlanner, PlanReActPlanner
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search, AgentTool
from google.genai import types


def greeting_tool() -> str:
    """returns a warm, friendly greeting."""
    return "Hello from your specialized greeting tool! Welcome."

search_agent = Agent(
    model='gemini-2.5-flash',
    name='SearchAgent',
    instruction="""
    You're a specialist in Google Search
    """,
    tools=[google_search],
)


root_instructions = """
You are a friendly agent. When the user greets you, you MUST use the greeting_tool to respond.
For all other dialogue make a good faith effort to answer questions and provide perspective.
In all cases maintain epistemic humility in your replies to the human.
Use the search_agent tool if you need more information to respond to the human.
"""


root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A friendly agent that provides a special greeting.',
    instruction=root_instructions,
    #NOTE: the agent can either be a code agent or a tool caller but not both
    #code_executor=BuiltInCodeExecutor(),
    #bypass_multi_tools_limit=True,
    tools=[greeting_tool, AgentTool(agent=search_agent)], # NOTE also using `google_search` callable here is not allowed
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=250,
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            )
        ]
    ),
    # NOTE: if instead we use PlanReActPlanner() we get Plan -> Action -> Reason
    # this is helpful for agents that do ot have a built in thinking feature
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_budget=1024,
        )
    ),
)
async def main() -> None:
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY environment variable is not set")

    # Create an in-memory runner for this agent
    runner = InMemoryRunner(
        agent=root_agent,
        app_name="chat_app",
    )

    # Create a session (kept in memory only for this run)
    session = await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="local-user",
    )

    print("ADK Chat Agent is ready.")
    print("Type your message, or 'exit' / 'quit' to stop.\n")

    # Simple chat loop
    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting chat.")
            break

        if user_text.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not user_text:
            continue

        # Build the user message as a Content object
        new_message = types.Content(
            role="user",
            parts=[types.Part(text=user_text)],
        )

        # Collect the model's textual reply
        reply_chunks: list[str] = []

        # Run the agent through the runner for this turn
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=new_message,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    text = getattr(part, "text", None)
                    if text:
                        reply_chunks.append(text)

        # Print the last assembled reply (if any)
        if reply_chunks:
            # Join all text parts for this turn
            reply_text = "".join(reply_chunks)
            print(f"Agent: {reply_text}\n")
        else:
            print("Agent: (no response content received)\n")


if __name__ == "__main__":
    asyncio.run(main())
