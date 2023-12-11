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
from langchain.chains import SimpleSequentialChain
from langchain.chains import SequentialChain




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
    hierarchy_file_name = "config/hierarchy_v3.json"

    hierarchy_dict_list = load_json(hierarchy_file_name)

    hierarchy_dict_list = hierarchy_dict_list["content"]

    prompt_template_for_extracting_rm_note = """
        For this task, you'll be generating a response based on given information. Please read the client name and the RM Notes, then answer the question provided.

        Do not search any information from internet or based on your understanding. Only based on RM Notes information to perform this task.

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
                            openai_api_version="2023-05-15", openai_api_base="https://pwcjay.openai.azure.com/",verbose=True)


    # set up openai environment - Ethan
    """llm_rm_note = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://lwyethan-azure-openai-test-01.openai.azure.com/")"""
    
    #"example": dictionary["Example"],

    output_dict_list = []
    for dictionary in hierarchy_dict_list:
        if dictionary["Section"] == section:
            chain = LLMChain(llm=llm_rm_note, prompt=rm_prompt_template,verbose=True)
            dictionary["Value"] = chain({"rm_note":rm_note_txt, "question": dictionary["Question"], "client_name": client})['text']
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


        If specific information is missing, follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 
        Make assumptions where necessary, but do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

# Executive Summary
def section_1_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        Do not incude 'In view of the above' in the output.

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.

        **Input Information**
        {input_info}
        
        **Client Name**
        {client_name}

        **Example for Reference**
        {example}

        **Executive Summary**
        Using the given borrower's name, requested credit amount, purpose of the credit, and the proposed credit structure, draft a concise executive summary paragraph for a credit proposal. The summary should reflect the relationship history, the strategic rationale behind the credit request, and the key terms of the proposed credit structure. 

        Ensure the following infomation is included in the input_info:
        1. Proposed credit structure
        2. A concise overview of the credit proposal, highlighting key information such as the borrowers name, request credit amount, purpose of the credit and the proposed credit structure.
        
        If specific information is missing, follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

# Client Request
def section_2_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        As a Relationship Manager at a bank, draft a concise paragraph for a credit proposal for a client. Use factual and professional language, including key details about the client's financial status and the proposed credit terms.
        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        
        **Input Information**
        {input_info}
        
        **Client Name**
        {client_name}

        **Example for Reference**
        {example}


        **Client Request**
        Please provide a concise summary of the Client Request based on the above information. 
        Conclude the Client Request with a statement about the proposed loan facility.
        Ensure the following infomation is included in the input_info:
        (a.	Please describe in detail the desired amount of the credit and type of facility such as a term loan, revolving credit line, or a combination of various credit instruments. 

        b.	Please explain the purpose of the credit facility with the breakdown of the funds allocation and highlights of the specific areas or projects where the credit will be utilized. For example, it could be for working capital , capital expenditure, expansion into new markets, research and development, or debt refinancing.

        c.	Please describe the proposed repayment plan for the credit facility, outlining the repayment term, interest rate and any specific repayment structures or conditions.

        i.	If the client has specific milestones or project timelines, include them to demonstrate the expected usage of funds over time.

        ii.	If the credit facility required collateral or security, detail the assets or guarantees the client is willing to pledge to secure the loan.)

        If specific information is missing, follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

# Shareholders and Group Structure
def section_3_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        Be aware if The input information does not provide specific details about the company's shareholders, ownership structure, and group companies, then generate as short as you can, output 'No information on shareholders, ownership structure, and group companies', also return text at the end by this exact format: "[RM Please provide further information on Keywords...]".

        Do not incude 'In view of the above, ' in the output.

        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 

        **Input Information**
        {input_info}
        
        **Client Name**
        {client_name}

        **Example for Reference**
        {example}
        
        **Shareholders and Group Structure**

        If specific information is missing, follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 
        Take this task one step at a time and remember to breathe.
        Do not incude 'In view of the above, ' in the output.
        """
    
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

# Project Details
def section_4_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        You must not contain (In view of the above) in the output

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 
        
        **Input Information**
        {input_info}
        
        **Client Name**
        {client_name}

        **Example for Reference**
        {example}

        **Project Details**
        Please provide a concise summary of the Project Details based on the above information. 
        Conclude the Project Details with a statement about the proposed loan facility.
        
        If specific information is missing, follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

#  Industry / Section Analysis
def section_5_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:
        If specific information is missing, follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 

        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph with a heading. 
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 
        
        **Input Information**
        {input_info}
        
        **Client Name**
        {client_name}

        **Example for Reference**
        {example}


        **Industry / Section Analysis**
        Please provide a concise summary of the Industry / Section Analysis based on the above information. 
        
        If specific information is missing, follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        You must not incude heading **Input Paragraph**.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# Management
def section_6_template():
    proposal_proposal_template_text = """
    Read this task step by step at a time and take a long breathe. Stick strictly to factual and verifiable information.:

    **Note: Write concise in bullet point form, no more than two rows in each bullet point.**

    1. Base your content solely on the 'Input Information' and the 'Client Name'. Do not include any content from 'Example' in your output - it's for reference only.
    2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
    3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
    4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
    5. Don't include line breaks within sentences in the same paragraph.
    6. Start your paragraph directly without a heading.
    7. You can use point form or tables to present your answer, but avoid any introduction of what the section includes.
    8. Avoid phrases like "Based on the input json" or "it is mentioned".
    9. Generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
    10. Do not invent any numbers or statistics. Use figures only if they are explicitly mentioned in the provided content.
    11. Do not add disclaimers or state the source of your information in your response.
    12. If specific information is missing or not provided in the input information, return text at the end in this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 

    **Input Information**
    {input_info}

    **Client Name**
    {client_name}

    **Example for Reference**
    {example}

    **Management**
    Please provide a concise summary of the Management based on the 'Input Information'. Conclude with a statement about the proposed loan facility.

    If specific information is missing, follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 
    Do not mention any lack of specific information in the output.
    Take this task one step at a time and remember to breathe.
    """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

# Financial Information of the Borrower
def section_7_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 
        
        **Reminder:** Your response must include information about the equity to debt ratio, Net income, and Return on Equity (ROE) of the borrower. If this information is not provided, make sure to ask the RM for it using the format: "[RM Please provide further information on Keywords... ]". 

        **Input Information**
        {input_info}

        **Client Name**
        {client_name}

        **Example for Reference**
        {example}


        **Financial Information of the Borrower**
        Please provide a concise summary of the Financial Information of the Borrower based on the above information. 
        Ensure the following infomation is included in the input_info:
        a.	Please provide the borrower’s audited financial statements for the past 2 to 3 years, including balance sheet, income statement and cash flow statement.
        b.	Please provide the breakdown of the borrower’s revenue sources and its cost structure.
        c.	Please provide insights into borrower’s financial performance, trends and future prospects. If there is any significant events or facts that have influenced the borrower’s financial results, please explain it.
        
        If specific information is missing, use this format: "[RM Please provide further information on Keywords...]". Do not invent information or state that something is unclear. 
        Avoid mentioning any lack of specific information in the output.
        Remember to approach this task one step at a time and to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# Other Banking Facilities
def section_8_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Read and Carefully consider all the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        Be aware if The input information does not provide specific details about the company's Other Banking Facilities.
        Then generate as short as you can, output 'No information on Other Banking Facilities'.
        If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please provide further information on Keywords... ]".
        
        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 


        **Input Information**
        {input_info}

        **Client Name**
        {client_name}

        Do not include any information from Example for Reference in your output - it's for reference only.
        **Example for Reference**
        {example}


        **Other Banking Facilities**
        Please provide a concise summary of the Other Banking Facilities based on the above information. 
        Ensure the following infomation is included in the input_info:
        a.	Please provide a list of the borrower’s existing credit facilities from other banks or financial institutions, including details such as the name of the lending institution, type of facility, outstanding balance, interest rate, maturity date and any collateral or guarantees associated with each facility.
        
        If specific information is missing, follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 
        Take this task one step at a time and remember to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# Opinion of the Relationship Manager
def section_9_template():
    proposal_proposal_template_text = """
        Based on the provided relationship history, creditworthiness, repayment capacity, risk assessment, and the strength of the banking relationship with {client_name}, create a balanced credit assessment paragraph. The assessment should outline strengths and weaknesses, adhering to the details included in the input information. If certain aspects are not detailed in the input, consolidate the missing elements and prompt for further information using the format "[RM Please provide further information on Keywords...]" at the end of the output.

        **Instructions:**
        1. Use the input information provided under **Input Information**.
        2. Reference the client as {client_name}.
        3. Do not extract information from the **Example for Reference** section.
        4. Avoid phrases like "Based on the input json" and subjective language or sentiments.
        5. Present information clearly in English, with sub-headers for strengths and weaknesses where applicable.
        6. Ensure responses are factual, free of invented numbers or statistics unless specified in the content.
        7. Refrain from mentioning the source of the information, justification, or personal recommendations.

        **Input Information**
        {input_info}

        **Client Name**
        {client_name}

        **Example for Reference**
        {example}
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# Summary of Recommendation
def section_10_template():
    proposal_proposal_template_text = """
        Take this task step by step, and remember to breathe.
        Please follow these guidelines strictly, focusing on factual and verifiable information:

        **Summary of Recommendation**
        Read the 'Input Information' and use the 'Example for Reference' to guide your thinking. Then, based on your understanding, output one of the exact following lines: 
        1. 'In view of the above, we recommend the proposed loan facility for management approval.' 
        2. 'In view of the above, we do not recommend the proposed loan facility for management approval.' 

        **Input Information**
        {input_info}

        **Client Name**
        {client_name}

        **Example for Reference** 
        {example}

        If specific information is missing, follow this format: "[RM Please provide further information on Keywords...]". Do not invent information or state that something is unclear. 
        Take this task one step at a time and remember to breathe.

        Your output must be one of the exact following lines, with "In view of the above, ": 
        - In view of the above, we recommend the proposed loan facility for management approval.
        - In view of the above, we do not recommend the proposed loan facility for management approval.

        """
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# template for regeneration
def regen_template():
    proposal_proposal_template_text = """
        To complete this task, carefully consider the previous paragraph and the RM's instructions. Your task is to edit and summarize the previous paragraph according to the RM instructions provided.

        **Previous Paragraph**
        {previous_paragraph}

        **RM Instructions**
        {rm_instruction}

        When crafting your response, adhere to the following guidelines:

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.

        If specific information is missing, use the following format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.

        Take this task one step at a time and remember to breathe.
        """
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["previous_paragraph", "rm_instruction"])


    return prompt_template_proposal

def review_prompt_template():
    proposal_proposal_template_text = """
        To complete this task. Your task is to review and edit the Input paragraph according to the instructions provided.
        Please do not add additional content to the Paragraph.

        **Input Paragraph**
        {first_gen_paragraph}

        Double check the Input Paragraph does not contains any content from 'example', if the Input Paragraph contains any content from 'example', remove them.
        **Example**
        {example}

        - Do not state that information is missing, not mentioned, or not provided. If specific information such as the proposed loan facility isn't available in the input, do not mention its absence or request it.
        - If specific information isn't provided, request it in this format: '[RM Please provide further information on Keywords...]'. Do not state that information is missing or not mentioned.
        - Avoid subjective language or personal judgments. 
        - Do not invent numbers or statistics unless explicitly provided.
        - Do not mention 'RM Note', 'Component', or any meetings with the client. Use 'It is mentioned that...' instead.
        - Do not justify your answers or provide your own suggestions. Stick to the information provided.
        - Use English and divide your content into short paragraphs. Do not exceed 100 words per paragraph.
        - Do not introduce your sections, start directly.
        - Avoid subjective language or personal judgments. 
        - if the first_gen_paragraph contains "In view of the above", do not edit and remove that sentence.

        Your response should not highlight missing or unspecified information. Instead, request additional information using the provided format when necessary. Do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["first_gen_paragraph", "example"])

    return prompt_template_proposal

def regenerate_review_prompt_template():
    proposal_proposal_template_text = """
        To complete this task. Your task is to review and edit the Input paragraph according to the instructions provided.
        Please do not add additional content to the Paragraph.

        **Input Paragraph**
        {re_gen_paragraph}

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please provide further information on Keywords... ]". Do not invent information or state that something is unclear. 

        
        If specific information is missing, follow this format: "[RM Please provide further information on Keywords...]". Do not invent information or state that something is unclear. 
        Make assumptions where necessary, but do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["re_gen_paragraph"])

    return prompt_template_proposal

# One more template for extracting the useless sentence
def review_prompt_template_2():
    proposal_proposal_template_text = """
        To complete this task, you need to review and edit the Input paragraph according to the instructions provided.
        Please do not add additional content to the Paragraph.

        **Input Paragraph**
        {reviewed}

        Instructions:
        1. Use only the information provided. Do not make assumptions or use general language to fill in the gaps. If a sentence states or implies that information is missing or not provided, do not include it in your output. 
        2. If the input contains sentences stating or implying that information is missing or not provided, such as 'However, further information is needed to provide a more comprehensive summary of the project details.' or 'Additionally, No specific information is provided about the proposed loan facility.' or "Additionally, no information is provided regarding the proposed loan facility.", these must be removed entirely from your output.
        3. Instead of these sentences, request the specific missing information using this format: '[RM Please provide further information on Keywords...]', you can return many times if there are information missing. 
        4. Take this task one step at a time and remember to breathe
        5. if the first_gen_paragraph contains "In view of the above", do not edit and remove that sentence.

        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["reviewed"])

    return prompt_template_proposal


# function to perform first generation of the paragraph
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
    # For each section, gen content based on its prompt.
    if section_name == "Executive Summary":
        prompt_template_proposal = section_1_template()
    elif section_name == "Client Request":
        prompt_template_proposal = section_2_template()
    elif section_name == "Shareholders and Group Structure":
        prompt_template_proposal = section_3_template()
    elif section_name == "Project Details":
        prompt_template_proposal = section_4_template()    
    elif section_name == "Industry / Section Analysis":
        prompt_template_proposal = section_5_template()
    elif section_name == "Management":
        prompt_template_proposal = section_6_template()
    elif section_name == "Financial Information of the Borrower":
        prompt_template_proposal = section_7_template()
    elif section_name == "Other Banking Facilities":
        prompt_template_proposal = section_8_template()
    elif section_name == "Opinion of the Relationship Manager":
        prompt_template_proposal = section_9_template()
    elif section_name == "Summary of Recommendation":
        prompt_template_proposal = section_10_template()
    else:
        prompt_template_proposal = first_gen_template()

    # set up openai environment - Jay
    llm_proposal = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://pwcjay.openai.azure.com/",verbose=True)

    # set up openai environment - Ethan
    """llm_proposal = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://lwyethan-azure-openai-test-01.openai.azure.com/")"""
    
    chain = LLMChain(
        llm=llm_proposal,
        prompt=prompt_template_proposal,
        output_key="first_gen_paragraph"
    )

    review_chain = LLMChain(llm=llm_proposal, prompt=review_prompt_template(), output_key="reviewed",verbose=True)

    additional_chain = LLMChain(llm=llm_proposal, prompt=review_prompt_template_2(), output_key="reviewed_2",verbose=True)

    overall_chain = SequentialChain(chains=[chain, review_chain, additional_chain], 
                                    input_variables=["input_info", "client_name", "example"],
                                    # Here we return multiple variables
                                    output_variables=["reviewed_2"],
                                    verbose=True)

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

    drafted_text = overall_chain({"input_info": final_dict["input_info"], "client_name": client, "example": final_dict["Example"]})
    drafted_text = drafted_text["reviewed_2"]
    drafted_text2 = drafted_text.replace("Based on the given information, ", "").replace("It is mentioned that ", "")

    # All capital letters for first letter in sentences
    formatter = re.compile(r'(?<=[\.\?!]\s)(\w+)')
    drafted_text2 = formatter.sub(lambda m: m.group().capitalize(), drafted_text2)

    # Capitalize the first character of the text
    drafted_text2 = drafted_text2[0].capitalize() + drafted_text2[1:]

    rm_fill_values = []
    lines = drafted_text2.split("\n")

    for i, line in enumerate(lines):
        matches = re.findall(r"\[RM (.+?)\]\.?", line)  # Find all [RM ...] followed by optional dot
        for match in matches:
            rm_fill = match + "\n"
            rm_fill_values.append(rm_fill)
        
        # remove all the RM requests and the optional following dots from the line
        line = re.sub(r"\[RM .+?\]\.?", "", line)
        lines[i] = line

    # Rejoin the lines into a single string without RM requests
    drafted_text2 = "\n".join(lines)

    # Remove the specific phrase "Please provide further information on" from each value in rm_fill_values
    # Then strip any leading/trailing whitespace and remove trailing periods
    rm_fill_values = [value.replace("Please provide further information on", "").strip().rstrip('.') for value in rm_fill_values]

    # Combine the RM_fill values into a single string separated by commas and "and" before the last value
    # Ensure that it doesn't end with a period or a comma
    if rm_fill_values:
        # Create a combined text of RM_fill values
        combined_rm_fill_text = ", ".join(rm_fill_values[:-1])
        if len(rm_fill_values) > 1:
            combined_rm_fill_text += ", and " + rm_fill_values[-1]
        else:
            combined_rm_fill_text = rm_fill_values[0]

        # Add the prefix "Please provide further information on" if it's not already present and appropriate
        if not combined_rm_fill_text.lower().startswith("please provide further information on"):
            combined_rm_fill_text = "Please provide further information on " + combined_rm_fill_text

        final_rm_fill_text = combined_rm_fill_text
    else:
        final_rm_fill_text = ""

    # Capitalize the first letter of the final_rm_fill_text only if it is not empty
    if final_rm_fill_text:
        final_rm_fill_text = final_rm_fill_text[0].upper() + final_rm_fill_text[1:]

    output_json = {
        "section": section_name,
        "output": drafted_text2,
        "RM_fill" : final_rm_fill_text,
    }

    #output the result
    return output_json

# Re-generate function
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
        prompt=prompt_template_proposal,
        output_key="re_gen_paragraph"
    )

    review_chain = LLMChain(llm=llm_proposal, prompt=regenerate_review_prompt_template(), output_key="reviewed",verbose=True)

    additional_chain = LLMChain(llm=llm_proposal, prompt=review_prompt_template_2(), output_key="reviewed_2",verbose=True)

    overall_chain = SequentialChain(chains=[chain, review_chain, additional_chain], 
                                    input_variables=["previous_paragraph", "rm_instruction"],
                                    # Here we return multiple variables
                                    output_variables=["reviewed_2"],
                                    verbose=True)


    drafted_text = overall_chain({"previous_paragraph": previous_paragraph, "rm_instruction":rm_instruction})
    drafted_text = drafted_text["reviewed_2"]
    drafted_text2 = drafted_text.replace("Based on the given information, ", "").replace("It is mentioned that ", "")

    #All capital letters for first letter in sentences
    formatter = re.compile(r'(?<=[\.\?!]\s)(\w+)')
    drafted_text2 = formatter.sub(lambda m: m.group().capitalize(), drafted_text2)

    # Capitalize the first character of the text
    drafted_text2 = drafted_text2[0].capitalize() + drafted_text2[1:]

    rm_fill_values = []
    lines = drafted_text2.split("\n")

    for i, line in enumerate(lines):
        matches = re.findall(r"\[RM (.+?)\]\.?", line)  # Find all [RM ...] followed by optional dot
        for match in matches:
            rm_fill = match + "\n"
            rm_fill_values.append(rm_fill)
        
        # remove all the RM requests and the optional following dots from the line
        line = re.sub(r"\[RM .+?\]\.?", "", line)
        lines[i] = line

    # Rejoin the lines into a single string without RM requests
    drafted_text2 = "\n".join(lines)

    # Remove the specific phrase "Please provide further information on" from each value in rm_fill_values
    # Then strip any leading/trailing whitespace and remove trailing periods
    rm_fill_values = [value.replace("Please provide further information on", "").strip().rstrip('.') for value in rm_fill_values]

    # Combine the RM_fill values into a single string separated by commas and "and" before the last value
    # Ensure that it doesn't end with a period or a comma
    if rm_fill_values:
        # Create a combined text of RM_fill values
        combined_rm_fill_text = ", ".join(rm_fill_values[:-1])
        if len(rm_fill_values) > 1:
            combined_rm_fill_text += ", and " + rm_fill_values[-1]
        else:
            combined_rm_fill_text = rm_fill_values[0]

        # Add the prefix "Please provide further information on" if it's not already present and appropriate
        if not combined_rm_fill_text.lower().startswith("please provide further information on"):
            combined_rm_fill_text = "Please provide further information on " + combined_rm_fill_text

        final_rm_fill_text = combined_rm_fill_text
    else:
        final_rm_fill_text = ""

    # Capitalize the first letter of the final_rm_fill_text only if it is not empty
    if final_rm_fill_text:
        final_rm_fill_text = final_rm_fill_text[0].upper() + final_rm_fill_text[1:]

    output_json = {
        "section": section_name,
        "output": drafted_text2,
        "RM_fill" : final_rm_fill_text,
    }

    #output the result
    return output_json


# Wrapper function
def run_first_gen(section, rm_note_txt, client):

    extract_json = web_extract_RM(section ,rm_note_txt, client)
    output_json = first_generate(section, extract_json, client)

    return output_json
