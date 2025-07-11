
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from dotenv import load_dotenv
from langchain.agents import Tool
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_experimental.tools import PythonREPLTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper 
import wikipedia   # type: ignore

from playwright.async_api import async_playwright


load_dotenv(override=True)
serper = GoogleSerperAPIWrapper()

async def playwright_tools():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
    return toolkit.get_tools(), browser, playwright


#def push(text: str):
#    """Send a push notification to the user"""
#    requests.post(pushover_url, data = {"token": pushover_token, "user": pushover_user, "message": text})
#    return "success"


def get_file_tools():
    toolkit = FileManagementToolkit(root_dir="sandbox")
    return toolkit.get_tools()

def get_search_tool():

    tool_search =Tool(
        name="search",
        func=serper.run,
        description="Use this tool when you want to get the results of an online web search"
    )
    return tool_search

async def other_tools():
    #push_tool = Tool(name="send_push_notification", func=push, description="Use this tool when you want to send a push notification")
    file_tools = get_file_tools()

    #tool_search =Tool(
    #    name="search",
    #    func=serper.run,
    #    description="Use this tool when you want to get the results of an online web search"
    #)
    tool_search = get_search_tool()

    # ➋ pasa el cliente wikipedia a la wrapper
    wiki_api = WikipediaAPIWrapper(wiki_client=wikipedia)
    wiki_tool = WikipediaQueryRun(api_wrapper=wiki_api)

    python_repl = PythonREPLTool()
    
    return file_tools + [tool_search, python_repl,  wiki_tool]
