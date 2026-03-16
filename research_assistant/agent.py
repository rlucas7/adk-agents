import wikipedia
import arxiv

from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.agents.llm_agent import LlmAgent


def wikipedia_tool(query: str) -> str:
    """
    Searches Wikipedia for a given query and returns a summary of the top results.

    Args:
        query (str): The search term to loop up on Wikipedia.
    """
    try:
        summary = wikipedia.summary(query)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"The query '{query}' is ambiguous. Be more specific."
    except wikipedia.exceptions.PageError:
        return f"Sorry, I could not find a wikipedia page for '{query}'."
    except Exception as e:
        return f"An unexpected error occurred while search Wikipedia: {e}"


wiki_agent_instructions = """you are a specialized agent and your task is
to accept a research query and use the `wikipedia_tool` to find relevant
information.
"""


wikipedia_agent = LlmAgent(
    name='wikipedia_researcher',
    model='gemini-2.5-flash',
    description='An expert at finding and summarixing information from Wikipedia',
    instruction=wiki_agent_instructions,
    tools=[wikipedia_tool]
)


def arxiv_tool(query: str) -> str:
    """
    Searches the arXiv repository for academic papers matching a query.

    Args:
        query (str): The topic to search for academic papers on.
    """
    try:
       # arxiv api client
       client = arxiv.Client()

       search = arxiv.Search(query=query, max_results=2, sort_by=arxiv.SortCriterion.Relevance)

       results = []
       for result in client.results(search):
            results.append(f"Title: {result.title}\nSummary: {result.summary}\nURL: {result.entry_id}")

       if not results:
           return f"No academic papers found on arXiv for the query '{query}'."

       return "\n---\n".join(results)
    except Exception as e:
        return f"An unexpected error occurred while searching arXiv: {e}"


arxiv_tool_instructions = """
You are a specialized agent whose job it is to search arXiv for papers on a
given topic. Use `arxiv_tool` to find the papers.
"""


arxiv_agent = LlmAgent(
    name='arXiv_agent',
    model='gemini-2.5-flash',
    description='An expert at finding and summarizing academic papers from ArXiv.',
    instruction=arxiv_tool_instructions,
    tools=[arxiv_tool],
)


google_search_instruction = """
Your only task is to accept a research topic, use the `GoogleSearchTool` to find
relevant information about the topic and return a concise summary of the search
results.
"""

google_search_agent = LlmAgent(
    name='google_search',
    model='gemini-2.5-flash',
    description='An expert at searching the web to find relevant, up-to-date information on a topic using the `GoogleSearchTool` to find the information.',
    instruction=google_search_instruction,
    tools=[GoogleSearchTool(bypass_multi_tools_limit=True)],
)


def report_writer_tool(content: str, filename: str) -> str:
    """
    Writes the given content to a local file. Appends if the file already exists.

    Args:
        content (str): The text content to write to the file.
        filename (str): The name of the file to save the content in (e.g. 'report.txt').
    """
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(content + "\n")
        return f"Successfully appended content to {filename}."
    except Exception as e:
        return f"An error occurred while writing to file: {e}"

report_writer_instruction = """
You are a specialized agent whose job is to use the `report_writer_tool`
to write given text content to a specified file.
"""


writer_agent = LlmAgent(
    model='gemini-2.5-flash-lite',
    name='report_writer',
    description='A research assistnat that gathers information from Wikipedia, arXiv, and Google Search to create a summary report on a given topic.',
    instruction=report_writer_instruction,
    tools=[
        report_writer_tool
    ],
)

### controller agent

controller_instruction = """
You are a research assistant who orchestrates a team of specialist agents
to produce a high-quality research report.

Your primary role is to delegate tasks, synthesize the results, and ensure
the final report is well-structured.

Your specialist team consists of:
- `wikipedia_researcher`: Use this agent to get general background information
     and a high-level overview.
- `arxiv_researcher`: Use this agent to find relevant academic papers and
     their summaries.
- `web_searcher`: Use this agent to find up-to-date information and supplementary
     context from the web.

  Your workflow must be as follows:
  1.  First, call all three specialist research agents:
     (`wikipedia_researcher`, `arxiv_researcher`, and `web_searcher`)
     to gather a comprehensive set of information on the topic.
  2.  Once all information has been gathered, you must personally synthesize
      the content from all three sources into a single, coherent summary.
  3.  Finally, call the `report_writer` tool to save the complete, synthesized
      report into a text file. The filename should be based on the research
      topic (e.g., black_holes_report.txt).
"""


root_agent = LlmAgent(
    name='controller',
    model='gemini-2.5-flash',
    description='The main controller for a multi-agent research team.',
    instruction=controller_instruction,
    tools=[
        AgentTool(wikipedia_agent),
        AgentTool(arxiv_agent),
        AgentTool(google_search_agent),
        AgentTool(writer_agent),
    ],
)
