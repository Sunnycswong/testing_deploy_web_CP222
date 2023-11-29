#%%
## Import Library
import copy
import openai
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswParameters,
    PrioritizedFields,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticSettings,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
)
from azure.storage.blob import BlobServiceClient
from langchain.chains import LLMChain
from langchain.llms import AzureOpenAI 
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chat_models import AzureChatOpenAI
from langchain.memory import CosmosDBChatMessageHistory
import openai
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch

import openai
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import json

from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
#from langchain.retrievers import AzureCognitiveSearchRetriever
from langdetect import detect
from langchain.prompts import PromptTemplate
import re
# Create chain to answer questions
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import ConversationalRetrievalChain

# Import Azure OpenAI
from langchain.llms import AzureOpenAI 
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage

import openai
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswParameters,
    PrioritizedFields,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticSettings,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
)

from azure.storage.blob import BlobServiceClient
from pypdf import PdfReader
from langchain.schema import Document
import openai
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch
#import textwrap
import logging
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import json
from docx import Document as DocxDocument
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import re

# Setting credit
index_name = "credit-proposal"
search_service = "gptdemosearch"
search_api_key = "PcAZcXbX2hJsxMYExc2SnkMFO0D94p7Zw3Qzeu5WjYAzSeDMuR5O"
storage_service = "creditproposal"
storage_api_key = "hJ2qb//J1I1KmVeDHBpwEpnwluoJzm+b6puc5h7k+dnDSFQ0oxuh1qBz+qPB/ZT7gZvGufwRbUrN+ASto6JOCw=="
connect_str = f"DefaultEndpointsProtocol=https;AccountName={storage_service};AccountKey={storage_api_key}"

doc_intell_endpoint = "https://doc-intelligence-test.cognitiveservices.azure.com/"
doc_intell_key = "9fac3bb92b3c4ef292c20df9641c7374"


# set up openai environment - Jay
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_BASE"] = "https://pwcjay.openai.azure.com/"
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["OPENAI_API_KEY"] = "f282a661571f45a0bdfdcd295ac808e7"


# set up openai environment - Ethan
#os.environ["OPENAI_API_TYPE"] = "azure"
#os.environ["OPENAI_API_BASE"] = "https://lwyethan-azure-openai-test-01.openai.azure.com/"
#os.environ["OPENAI_API_VERSION"] = "2023-05-15"
#os.environ["OPENAI_API_KEY"] = "ff96d48045584cb9844fc70e5b802918"


# Setting up ACS -Jay
#os.environ["AZURE_COGNITIVE_SEARCH_SERVICE_NAME"] = search_service
#os.environ["AZURE_COGNITIVE_SEARCH_API_KEY"] = search_api_key
#os.environ["AZURE_INDEX_NAME"] = index_name


# Core LLM call funcition

def cap(match):
    return(match.group().capitalize())

# load json data function
def load_json(json_path):
    with open(json_path, "r" ,encoding="utf-8") as f:
        data = json.load(f)
    return data

'''
    You could follow the below extraction example format to output the answer.
    example (Keyword: example):
    {example}

    3. The example (Keyword: proposal_example) above is just for your reference only to improve your theme, you must not directly copy the content in the examples

'''

#This funcition is to prepare the rm note in desired format for web, call by app.py
def web_extract_RM(section, rm_note_txt, client):
    hierarchy_file_name = "config/hierarchy_v2.json"

    hierarchy_dict_list = load_json(hierarchy_file_name)

    hierarchy_dict_list = hierarchy_dict_list["content"]

    prompt_template_for_extracting_rm_note = """
        For this task, you'll be generating a response based on given information. Please read the client name and the RM's notes, then answer the question provided.

        **Client Name**
        {client_name}

        **RM Notes**
        {rm_note}

        **Question**
        {question}

        While crafting your response, please observe these guidelines:

        1. Provide your answer in English.
        2. Expand on the information provided by the RM where possible.
        3. Do not invent or exaggerate information. Stick to what's provided.
        4. If no relevant information is available, respond with "[N/A]".
        5. Do not include notes about the source of your information in your answer.

        Remember, approach this task calmly and methodically.
        """
    
    rm_prompt_template = PromptTemplate(template=prompt_template_for_extracting_rm_note, input_variables=["rm_note", "question", "client_name"])# "example",])

    
    # set up openai environment - Jay
    llm_rm_note = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://pwcjay.openai.azure.com/")


    # set up openai environment - Ethan
    """llm_rm_note = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://lwyethan-azure-openai-test-01.openai.azure.com/")"""
    
    #"example": dictionary["Example"],

    output_dict_list = []
    for dictionary in hierarchy_dict_list:
        if dictionary["Section"] == section:
            chain = LLMChain(llm=llm_rm_note, prompt=rm_prompt_template)
            dictionary["Value"] = chain({"rm_note":rm_note_txt, "question": dictionary["Question"], "client_name": client })['text']
            dictionary["Value"] = dictionary["Value"].replace("Based on the given information, ", "")
            if "[N/A]" in dictionary["Value"]:
                dictionary["Value"] = ""
            output_dict_list.append(dictionary)

    # Create Json file 
    # output_json_name = "GOGOVAN_hierarchy_rm_note.json"
    # json.dump(output_dict_list, open(output_json_name, "w"), indent=4)

    return output_dict_list

'''
        ======
        Example: (Keyword: proposal_example)
        {example}
        ======

'''


def first_gen_template():
    proposal_proposal_template_text = """
        Carefully consider the following guidelines while working on this task:

        **Note: Write as comprehensively as necessary to fully address the task. There is no maximum length.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".

        **Client Name**
        {client_name}

        **Example for Reference**
        {example}

        **Input Information**
        {input_info}

        If specific information is missing, follow this format: "[RM please help provide further information on (Keyword: further_info)]". Do not invent information or state that something is unclear. 

        Take this task one step at a time and remember to breathe.
        """
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal


def regen_template():
    proposal_proposal_template_text = """
        To complete this task, carefully consider the previous paragraph and the RM's instructions. Your task is to edit and summarize the previous paragraph according to the instructions provided.

        **Note: Write as comprehensively as necessary to fully address the task. There is no maximum length.**

        **Previous Paragraph**
        {previous_paragraph}

        **RM Instructions**
        {rm_instruction}

        When crafting your response, adhere to the following guidelines:

        1. Frame your information as "It is mentioned that", avoiding words like "RM Note", "Component", or any references to meetings with the client.
        2. Do not reference the source of your input or justify your answers.
        3. Provide your answer in English, breaking it into multiple paragraphs if it exceeds 100 words.
        4. Avoid line breaks within sentences in the same paragraph and starting your paragraph with a title.
        5. Point-form or table format can be used to present your answer, but avoid introducing what the section includes.
        6. Do not include notes that the paragraphs are based on aggregated content.

        If specific information is missing, use the following format: "[RM please provide further information on (Keyword: further_info)]". Do not invent information or state that something is unclear. 

        Take this task one step at a time and remember to breathe.
        """
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["previous_paragraph", "rm_instruction"])


    return prompt_template_proposal


# to first generate 
def first_generate(section_name, input_json, client):


    """
    A core function to generate the proposal per section

    Parameters:
    -----------
    prompt: str
    Prompt text for instructing the output based on RM prompt

    rm_note: str
    It contains the information from the RM

    example: str
    Input example for GPt to take it as an example

    """
    #.format(content=content, section=section, context=context)
    
    prompt_template_proposal = first_gen_template()

    # set up openai environment - Jay
    llm_proposal = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://pwcjay.openai.azure.com/")

    # set up openai environment - Ethan
    """llm_proposal = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://lwyethan-azure-openai-test-01.openai.azure.com/")"""
    
    chain = LLMChain(
        llm=llm_proposal,
        prompt=prompt_template_proposal
    )

    # Break the input_json by parts
    input_info_str = []
    example_str = []

    for item in input_json:
        sub_section = item['Sub-section']
        value = item['Value']
        example = item['Example']
        input_info_str.append(f"{sub_section} : {value}")
        example_str.append(f"{sub_section} : {example}")

    final_dict = {"input_info": ", ".join(input_info_str), "Example": ", ".join(example_str)}

    drafted_text = chain({"input_info": final_dict["input_info"], "client_name": client, "example": final_dict["Example"]})['text']
    drafted_text2 = drafted_text.replace("Based on the given information, ", "").replace("It is mentioned that ", "")

    # All capital letters for first letter in sentences
    formatter = re.compile(r'(?<=[\.\?!]\s)(\w+)')
    drafted_text2 = formatter.sub(lambda m: m.group().capitalize(), drafted_text2)

    # Capitalize the first character of the text
    drafted_text2 = drafted_text2[0].capitalize() + drafted_text2[1:]

    rm_fill_values = []
    additional_info_values = []
    lines = drafted_text2.split("\n")
    for i, line in enumerate(lines):
        match = re.search(r"\[RM .+?\]", line)
        if match:
            rm_fill = match.group(0)
            # Remove the '[RM ' at the start and ']' at the end, then append
            rm_fill = rm_fill[4:-1]
            rm_fill_values.append(rm_fill)
            lines[i] = line.replace(match.group(0), "")  # remove the RM request from the line

        # Check for "Please provide further information" in the line
        if "Please provide further information" in line:
            # Append the whole line
            additional_info_values.append(line)

    # Rejoin the lines into a single string without RM requests
    drafted_text2 = "\n".join(lines)

    # Join all the strings in the list with a space in between each string
    rm_fill_text = ' '.join(rm_fill_values)
    additional_info_text = ' '.join(additional_info_values)

    # Combine rm_fill_text and additional_info_text into one string
    combined_text = rm_fill_text + ' ' + additional_info_text

    output_json = {
        "section": section_name,
        "output": drafted_text2,
        "RM_fill" : combined_text,
    }

    #output the result
    return output_json

def regen(section_name, previous_paragraph, rm_instruction):
    prompt_template_proposal = regen_template()

    # set up openai environment - Jay
    llm_proposal = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://pwcjay.openai.azure.com/")


    # set up openai environment - Ethan
    """llm_proposal = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://lwyethan-azure-openai-test-01.openai.azure.com/")"""
    
    chain = LLMChain(
        llm=llm_proposal,
        prompt=prompt_template_proposal
    )

    drafted_text = chain({"previous_paragraph": previous_paragraph, "rm_instruction":rm_instruction})['text']
    drafted_text2 = drafted_text.replace("Based on the given information, ", "").replace("It is mentioned that ", "")

    #All capital letters for first letter in sentences
    formatter = re.compile(r'(?<=[\.\?!]\s)(\w+)')
    drafted_text2 = formatter.sub(lambda m: m.group().capitalize(), drafted_text2)

    # Capitalize the first character of the text
    drafted_text2 = drafted_text2[0].capitalize() + drafted_text2[1:]

    rm_fill_values = []
    additional_info_values = []

    lines = drafted_text2.split("\n")
    for i, line in enumerate(lines):
        match = re.search(r"\[RM .+?\]", line)
        if match:
            rm_fill = match.group(0)
            # Remove the '[RM ' at the start and ']' at the end, then append
            rm_fill = rm_fill[4:-1]
            rm_fill_values.append(rm_fill)
            lines[i] = line.replace(match.group(0), "")  # remove the RM request from the line
                    
        # Check for "Please provide further information" in the line
        if "Please provide further information" in line:
            # Append the whole line
            additional_info_values.append(line)

    # Rejoin the lines into a single string without RM requests
    drafted_text2 = "\n".join(lines)

    # Join all the strings in the list with a space in between each string
    rm_fill_text = ' '.join(rm_fill_values)
    additional_info_text = ' '.join(additional_info_values)

    # Combine rm_fill_text and additional_info_text into one string
    combined_text = rm_fill_text + ' ' + additional_info_text

    output_json = {
        "section": section_name,
        "output": drafted_text2,
        "RM_fill" : combined_text,
    }

    #output the result
    return output_json


# Wrapper function
def run_first_gen(section, rm_note_txt, client):

    extract_json = web_extract_RM(section ,rm_note_txt, client)
    output_json = first_generate(section, extract_json, client)

    return output_json



