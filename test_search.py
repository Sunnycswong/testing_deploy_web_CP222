import os
import requests

from langchain.chat_models import AzureChatOpenAI
from langchain.agents import initialize_agent, AgentType
from src.get_keys import GetAzureKeys
from langchain.utilities import BingSearchAPIWrapper
from langchain.tools import BaseTool

from src.get_keys import GetAzureKeys
from src.general_prompts import *
# from dotenv import load_dotenv, find_dotenv
# _ = load_dotenv(find_dotenv())  # read local .env file

keys = GetAzureKeys()

class CustomBingSearch(BaseTool):
    """Tool for a Bing Search Wrapper"""
    
    name = "@bing"
    description = "useful when the questions includes the term: @bing.\n"

    k: int = 5
    
    def _run(self, query: str) -> str:
        bing = BingSearchAPIWrapper(k=self.k)
        return bing.results(query,num_results=self.k)
            
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("This Tool does not support async")


keys = GetAzureKeys()

def get_bing_search_response(question):
    
    tools = [CustomBingSearch(k=5)]

    # set up openai environment - Jay
    llm_proposal = AzureChatOpenAI(deployment_name="gpt-35-16k",temperature=0,max_tokens=2048)

    agent_executor = initialize_agent(tools=tools,
                                    llm=llm_proposal,
                                    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                    agent_kwargs={'prefix':BING_PROMPT_PREFIX},
                                    callback_manager=None,
                                    handle_parsing_errors=True #By Jay
                                    )

    #As LLMs responses are never the same, we do a for loop in case the answer cannot be parsed according to our prompt instructions
    for i in range(2):
        try:
            response = agent_executor.run(question) 
        except ValueError as e:
            response = str(e)
            if not response.startswith("Could not parse LLM output: `"):
                raise e
            response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")

    return response

# TODO hard code for testing

client_name = "GOGOX Holding Limited"
section_name = "Shareholders and Group Structure"

SECTION_3_QUESTION_1 = f"""
    Who are the major shareholders of {client_name}? Provide with:
    - their names
    - ownership percentages
    - their background information.

    Summarise of your findings. Provide your references.

    """

SECTION_3_QUESTION_2 = f"""
    Is {client_name} is part of a larger group structure? If yes, provide:
    - key entities within the group and explain its relationship between the entities, including parent companies, subsidaries and affiliates.
    - significant transactions or relationships between the {client_name} and related parties.

    Summarise of your findings. Provide your references.

    """

SECTION_5_QUESTION_1 = f"""
    What is the industry or sector of the {client_name}? Provide:
    - size of the industry and sector
    - growth rate of the industry and sector
    - major current trends of the industry and sector
    - future trends of the industry and sector

    Summarise of your findings. Provide your references.

    """

SECTION_5_QUESTION_2 = f"""
    Who are the major competitors of {client_name}? What are their market shares and key strengths and weaknesses.

    """

SECTION_6_QUESTION_1 = f"""
    Who are the CEO and Direector/Board Member of {client_name}? Provide as many as possible with:
    - their names
    - their titles
    - their relevant experience, qualifications, and achievements

    Summarise of your findings. Provide your references.

    """

"""# TODO move to core script
    if section_name == "Shareholders and Group Structure":
        print(get_bing_search_response(SECTION_3_QUESTION_1))
        print(get_bing_search_response(SECTION_3_QUESTION_2))

    elif section_name == "Industry / Section Analysis":
        print(get_bing_search_response(SECTION_5_QUESTION_1))
        print(get_bing_search_response(SECTION_5_QUESTION_2))

    elif section_name == "Management":
        print(get_bing_search_response(SECTION_6_QUESTION_1))"""

    # small test
    # print(get_bing_search_response(SECTION_5_QUESTION_1))
        