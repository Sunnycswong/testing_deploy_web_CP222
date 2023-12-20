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
os.environ["OPENAI_API_VERSION"] = "2023-09-01-preview"
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
        For this task, you are tasked with crafting a response based on the information provided. Meticulously examine the details specified under ----Client Name---- and the RM Notes before attempting to answer the ----Question---- presented.

        You must depend exclusively on the details outlined in the ----RM Notes---- to accomplish this task. Do not consult external sources or rely on personal knowledge.

        **Important**
        In the event that the ----RM Notes---- do not offer sufficient details to resolve the ----Question----, request for additional information at the end using this format: '[RM Please provide further information on Keywords]'.

        ----Client Name----
        {client_name}

        ----RM Notes----
        {rm_note}

        ----Question----
        {question}

        ----Example----
        {example}

        As you prepare your response, adhere strictly to the instructions below:

        1. Formulate your answer in clear, concise English.
        2. Enhance your response with any insights that can be derived from the RM Notes, where possible.
        3. Ensure that your response is based strictly on the provided information; refrain from creating or assuming details that are not explicitly mentioned.
        4. Do not include any references to the source of your information in your response.
        5. In the event that the ----RM Notes---- do not offer sufficient details to resolve the ----Question----, prompt a request for additional information using the format: '[RM Please provide further information on Keywords]'.
        6. If No information are provided in the RM Notes, request for additional information at the end using this format: '[RM Please provide further information on Keywords]'.
        
        Take a systematic and composed approach to this task.

        Note: The ----Example---- provided is for illustrative purposes only. Do not incorporate its content into your response; instead, use it as a guide for style or format when extracting and presenting information from the RM Notes.
        """
    
    rm_prompt_template = PromptTemplate(template=prompt_template_for_extracting_rm_note, input_variables=["rm_note", "question", "client_name", "example",])

    
    # set up openai environment - Jay
    llm_rm_note = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version=os.environ["OPENAI_API_VERSION"], openai_api_base="https://pwcjay.openai.azure.com/",verbose=True)


    # set up openai environment - Ethan
    """llm_rm_note = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://lwyethan-azure-openai-test-01.openai.azure.com/")"""
    
    #"example": dictionary["Example"],

    output_dict_list = []
    rm_text_list = []  # Variable to store the "[RM ...]" text

    for dictionary in hierarchy_dict_list:
        if dictionary["Section"] == section:
            chain = LLMChain(llm=llm_rm_note, prompt=rm_prompt_template, verbose=True)
            dictionary["Value"] = chain({"rm_note":rm_note_txt, "question": dictionary["Question"], "client_name": client, "example": dictionary["Example"]})['text']
            dictionary["Value"] = dictionary["Value"].replace("Based on the given information, ", "")
            
            # Use regular expressions to find the pattern "[RM ...]"
            match = re.search(r"\[RM [^\]]+\]", dictionary["Value"])
            if match:
                rm_text_variable = match.group(0)  # Store the "[RM ...]" text in the variable
                rm_text_list.append(rm_text_variable)
                #dictionary["Value"] = dictionary["Value"].replace(rm_text_variable, "")  # Remove the "[RM ...]" text from the "Value"
                dictionary["Value"] = ""
            
            if "[N/A]" in dictionary["Value"]:
                dictionary["Value"] = ""
            
            output_dict_list.append(dictionary)

    # Create Json file 
    # output_json_name = "GOGOVAN_hierarchy_rm_note.json"
    # json.dump(output_dict_list, open(output_json_name, "w"), indent=4)

    return output_dict_list, rm_text_list

'''
        ======
        Example: (Keyword: proposal_example)
        {example}
        ======

'''


def first_gen_template():
    proposal_proposal_template_text = """
        Carefully consider the following guidelines while working on this task:

        ----Note: Write as comprehensively as necessary to fully address the task. There is no maximum length.----

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".

        - Format any missing information in the specified manner at the end of your response following this format: "[RM Please provide further information on Keywords...]" as a standalone sentence.
        
        ----Client Name----
        {client_name}
    
        ----Example for Reference----
        {example}
    
        ----Input Information----
        {input_info}


        If specific information is missing, follow this format: "[RM Please provide further information on Keywords...]". Do not invent information or state that something is unclear. 
        Make assumptions where necessary, but do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

# Executive Summary
def section_1_template():
    proposal_proposal_template_text = """
        Read through this task carefully and take your time. Ensure all information is factual and verifiable:

        **Please limit the generated content in 200 words**

        1. Craft your content based on the provided ----Client Name---- and ----Input Information----. Exclude any details from the ----Example for Reference----.
        2. Replace any mention of "RM Note", "Component", or client meetings with "It is mentioned that".
        3. Present your answers clearly without justifications or recommendations, and refrain from revealing the source of your input.
        4. Compose your response in English, using concise paragraphs. Split any section over 100 words into smaller paragraphs.
        5. Maintain continuous sentences within the same paragraph without line breaks.
        6. Begin paragraphs directly without using headings.
        7. Present answers in bullet points or tables as needed, without prefacing what each section includes.
        8. Remain neutral and avoid subjective language or phrases indicating personal judgment.
        9. Use only the figures provided in the content and refrain from introducing new numbers or statistics.
        10. Leave out disclaimers and references to information sources in your response.

        For any missing information, append the following sentence at the end of your response: "[RM Please provide further information on Keywords...]", keeping it separate from bullet points or tables.

        ----Input Information----
        {input_info}

        ----Client Name----
        {client_name}

        ----Example for Reference----
        {example}

        ----Executive Summary----
        Create a succinct executive summary paragraph for a credit proposal, focusing on the borrower's name, the requested credit amount, the purpose of the credit, and the proposed credit structure. Include the relationship history and the strategic rationale for the credit request, alongside the details of the proposed credit structure.

        The executive summary should contain:
        1. A clear depiction of the proposed credit structure. Example: XYZ Corporation has successfully negotiated a structured credit facility of $10 million with a 5-year term and a fixed interest rate of 4.5% annually. The repayment schedule is based on a quarterly amortization plan ensuring manageable cash outflows while gradually reducing the principal balance. The loan is secured by the company's commercial real estate assets, providing the lender with a tangible guarantee. Adherence to financial covenants, including a minimum debt-service coverage ratio of 1.25x and a maximum leverage ratio of 3.5x, is required to maintain loan terms and prevent default. In the event of early repayment, XYZ Corporation will incur a prepayment penalty of 2% of the outstanding balance to compensate for the lender's interest income loss. The loan carries a subordinated clause, placing it after other senior debts in case of liquidation. Loan administration fees total $50,000, covering the due diligence and ongoing monitoring costs. Funds from the loan are earmarked strictly for the expansion of the company's manufacturing capacity, as per the agreed end-use terms. The loan agreement is governed by the laws of the State of New York, ensuring a clear legal framework for both parties.
        2. A summary of the credit proposal, emphasizing the borrower's name, requested credit amount, credit purpose, and credit structure details.

        If details are missing, close your response with a request for additional information using the specified format: "[RM Please provide further information on Keywords...]". Avoid any indication of missing information within the output itself.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

# Client Request
def section_2_template():
    proposal_proposal_template_text = """
        Approach this task methodically, maintaining a calm pace. Ensure all information provided is factual and substantiated:

        As a Relationship Manager at a bank, you are tasked with drafting a succinct paragraph for a credit proposal for a client. Your writing should be factual, professional, and incorporate essential details about the client's financial situation and the proposed credit terms.

        - Summarize any missing information at the end of your response with: "[RM Please provide further information on Keywords...]" as a separate sentence, not in bullet point form.

        - Use the given ----Client Name---- and ----Input Information---- as the basis for your content. Treat the ----Example for Reference---- solely as background context.
        - Refer to any internal notes, components, or client meetings indirectly using the phrase "It is mentioned that".
        - Present your responses in clear English, structured into concise paragraphs. Split paragraphs into smaller sections if they exceed 100 words.
        - Ensure sentences flow continuously within each paragraph.
        - Begin directly with the content of the paragraph, omitting headings.
        - Employ bullet points or tables for clarity, without prefacing the content of each section.
        - Keep your language neutral, avoiding subjective phrases or expressions of personal opinions.
        - Use only figures directly mentioned in the provided content, refraining from introducing new data or statistics.
        - Exclude disclaimers or mentions of information sources within your responses.
        - If details are not available in the input information, request additional data using the specified format: "[RM Please provide further information on Keywords...]", avoiding any indication of missing information within the main output.
        - Remove the sentences that telling the "information is missing" or "information have not been provided" or "information have not been not been mentioned"
        
        ----Input Information----
        {input_info}

        ----Client Name----
        {client_name}

        ----Example for Reference----
        {example}

        ----Client Request----
        Deliver a precise summary of the Client Request with the information provided. 

        Remember to incorporate a request for additional information using the specified format if any is missing, without suggesting uncertainties within the main content of the output. With: "[RM Please provide further information on Keywords...]" as a separate sentence.

        Proceed with each task step by step, and remember to breathe deeply as you work.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal


"""
        - A detailed description of the desired credit amount and the type of facility, such as a term loan, revolving credit line, or a mix of credit instruments.
        - An explanation of the purpose of the credit facility, detailing the allocation of funds and highlighting specific areas or projects for credit utilization, such as working capital, capital expenditure, market expansion, research and development, or debt refinancing.
        - A description of the proposed repayment plan, including the loan-to-value (LTV), amortization period, repayment term, interest rate, and any particular repayment structures or conditions.
        - Include any client milestones or project timelines to illustrate expected fund usage over time.
        - Detail collateral or security for the credit facility, specifying assets or guarantees the client is prepared to offer."""

# Shareholders and Group Structure
def section_3_template():
    proposal_proposal_template_text = """
        Approach this task with attention to detail and maintain a steady breathing rhythm. Here are the guidelines to follow, ensuring that all information is factual and verifiable:

        - Present your response in bullet points, limiting each to a maximum of three rows.

        - Derive your content solely from the ----Client Name---- and ----Input Information---- provided. The ----Example for Reference---- should only be used to understand the context and not mentioned in your output.
        - Use indirect phrasing such as "It is mentioned that" to reference any internal notes or discussions.
        - Write your response in English, organizing it into paragraphs. Break down any paragraph that exceeds 100 words into shorter sections.
        - Ensure sentences within the same paragraph are continuous without line breaks.
        - Begin writing your paragraph without any headings.
        - Utilize bullet points or tables to present your answers clearly, avoiding introductory statements for sections.
        - Refrain from using phrases like "Based on the input json" or "it is mentioned" to maintain neutrality.
        - Create responses devoid of subjective language or expressions that convey personal opinions.
        - Include figures and statistics only if they are explicitly provided in the content given.
        - Do not include disclaimers or mention the source of your information within your response.
        - Do not mention 'RM notes' in the content

        ----Input Information----
        {input_info}

        ----Client Name----
        {client_name}

        ----Example for Reference----
        {example}

        ----Shareholders and Group Structure----
        Your summary should based on the information to draft a paragraph.

        Proceed through each part of the task methodically, and ensure to maintain deep, regular breaths as you progress.
        """
    
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

# Back up prompt
"""
        Approach this task with attention to detail and maintain a steady breathing rhythm. Here are the guidelines to follow, ensuring that all information is factual and verifiable:

        If the input information lacks specific details about the company's shareholders, ownership structure, and group companies, succinctly state 'No information on shareholders, ownership structure, and group companies' and request more information using the format: "[RM Please provide further information on Keywords...]" at the end of your response.

        - If the input information does not include specific details about the company's shareholders, ownership structure, and group companies, clearly state: "No information provided about Shareholders and Group Structure."
        - Present your response in bullet points, limiting each to a maximum of three rows.

        - Derive your content solely from the ----Client Name---- and ----Input Information---- provided. The ----Example for Reference---- should only be used to understand the context and not mentioned in your output.
        - Use indirect phrasing such as "It is mentioned that" to reference any internal notes or discussions.
        - Write your response in English, organizing it into paragraphs. Break down any paragraph that exceeds 100 words into shorter sections.
        - Ensure sentences within the same paragraph are continuous without line breaks.
        - Begin writing your paragraph without any headings.
        - Utilize bullet points or tables to present your answers clearly, avoiding introductory statements for sections.
        - Refrain from using phrases like "Based on the input json" or "it is mentioned" to maintain neutrality.
        - Create responses devoid of subjective language or expressions that convey personal opinions.
        - Include figures and statistics only if they are explicitly provided in the content given.
        - Do not include disclaimers or mention the source of your information within your response.
        - Should any specific information be absent in the input information, request it using the prescribed format: "[RM Please provide further information on Keywords...]". Refrain from creating information or indicating ambiguities within the main content.

        ----Input Information----
        {input_info}

        ----Client Name----
        {client_name}

        ----Example for Reference----
        {example}

        ----Shareholders and Group Structure----
        Your summary should include:

        - A listing of the major shareholders with their names, ownership percentages, and relevant background information.
        - If the clients company is part of a group structure, detail the key entities and their interrelations, including parent companies, subsidiaries, and affiliates.
        - Disclose and explicate any significant transactions or relationships between the clients company and related parties.

        Request additional information if necessary using the format: "[RM Please provide further information on Keywords...]" without indicating any lack of clarity in the main output.

        Proceed through each part of the task methodically, and ensure to maintain deep, regular breaths as you progress.
        """




# Project Details
def section_4_template():
    proposal_proposal_template_text = """
        Read through this task one step at a time and remember to take deep breaths. Ensure your work adheres to the following guidelines, which emphasize factual and verifiable information:

        - Present your output concisely in bullet point form, with each bullet not exceeding two rows.

        - Derive your content directly from the provided ----Client Name---- and ----Input Information----. Use the ----Example for Reference---- solely for context.

        - Reference information by stating "It is mentioned that," avoiding direct mentions of "RM Note," "Component," or client meetings.

        - Craft your response in English, structured into clear, concise paragraphs. For longer paragraphs over 100 words, break them into smaller, digestible sections.

        - Maintain a continuous flow within the same paragraph, avoiding line breaks mid-sentence.

        - Initiate your paragraphs directly, without the use of headings.

        - Use bullet points or tables for clarity in presenting your answers, without prefacing what the section will include.

        - Exclude subjective language and phrases that express sentiment or personal judgment, such as 'unfortunately,' from your responses.

        - Incorporate figures and statistics only if they are explicitly included in the provided content. Do not invent data.

        - Leave out disclaimers or mentions of information sources within your response.

        - If certain information is missing from the input, request it clearly at the end of your response using the format: "[RM Please provide further information on Keywords...]." Avoid creating information or suggesting ambiguities.

        - Format requests for additional information as a standalone sentence at the end of your response, not as a bullet point.

        ----Input Information----
        {input_info}

        ----Client Name----
        {client_name}

        ----Example for Reference----
        {example}

        ----Project Details----
        Your summary should include:

        a. A detailed, yet succinct, description of the project's nature, purpose, and objectives.
        b. An outline of the project's scope and scale, including aspects such as physical size, production capacity, target market size, or geographical reach.
        c. A presentation of the project's timeline or schedule, highlighting major phases, activities, and estimated timeframes.
        d. An explanation of the necessary resources for the project's success, such as financial resources, equipment or technology.

        Conclude the Project Details with key information about the proposed loan facility.

        If any specific details are absent, end your response with a request for more information using the prescribed format: "[RM Please provide further information on Keywords...]." Ensure all provided information is clear and do not mention any deficiencies in the output.

        Tackle this task methodically, and keep your breathing steady and calm.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

#  Industry / Section Analysis
def section_5_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:
        If specific information is missing, follow this format: "[RM Please provide further information on Keywords...]". Do not invent information or state that something is unclear. 
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
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please provide further information on Keywords...]". Do not invent information or state that something is unclear. 
        
        - Format any missing information in the specified manner at the end of your response following this format: "[RM Please provide further information on Keywords...]" as a standalone sentence, do not include this in bullet point form.

        ----Input Information----
        {input_info}

        ----Client Name----
        {client_name}

        ----Example for Reference----
        {example}

        ----Industry / Section Analysis----
        Please provide a concise summary of the Industry / Section Analysis based on the above information.
        Your summary should encompass the following:

        - A detailed overview of the client's industry or sector, including the industry's size, growth rate, and major trends.
        - An analysis of the competitive landscape, identifying major competitors, their market shares, and key strengths and weaknesses, along with the client's unique selling propositions or competitive advantages.
        - An outlook on the industrys future prospects.

        Should there be gaps in the provided information, signal the need for additional details using the designated format: "[RM Please provide further information on Keywords...]." Refrain from hypothesizing or noting any ambiguities in the output.

        Approach each segment of the task methodically, and ensure you keep a steady breathing rhythm.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# Management
def section_6_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe. Stick strictly to factual and verifiable information.:

        ----Do not include any content from ----Example for Reference---- in your output - it's for reference only----

        1. Base your content solely on the 'Input Information' and the 'Client Name'. Do not include any content from ----Example for Reference---- in your output - it's for reference only.
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
        12. If specific information is missing or not provided in the input information, return text at the end in this format: "[RM Please provide further information on Keywords...]". Do not invent information or state that something is unclear. 

        - Format any missing information in the specified manner at the end of your response following this format: "[RM Please provide further information on Keywords...]" as a standalone sentence, do not include this in bullet point form.

        ----Input Information----
        {input_info}

        ----Client Name----
        {client_name}

        Note: The ----Example for Reference---- is intended solely for context and should not be incorporated into your assessment.
        ----Example for Reference----
        {example}

        ----Management----
        Please provide a concise summary of the Management based on the 'Input Information'. Conclude with a statement about the proposed loan facility.

        If specific information is missing, follow this format: "[RM Please provide further information on Keywords...]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.

        Note: The ----Example for Reference---- is intended solely for context and should not be incorporated into your assessment.
    """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

# Financial Information of the Borrower
def section_7_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        ----Note: Write concise in bullet point form, no more than two rows in each bullet points.----

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
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please provide further information on Keywords...]". Do not invent information or state that something is unclear. 
        13. You must not illustrate the definitions of the financial term, including: balance sheets, Financial Statements, Revenue Sources and Cost Structure, Financial Performance and Future Prospects
        
        ----Reminder:---- Your response must include information about the equity to debt ratio, Net income, and Return on Equity (ROE) of the borrower. If this information is not provided, make sure to ask the RM for it using the format: "[RM Please provide further information on Keywords...]". 

        - Format any missing information in the specified manner at the end of your response following this format: "[RM Please provide further information on Keywords...]" as a standalone sentence, do not include this in bullet point form.

        ----Input Information----
        {input_info}

        ----Client Name----
        {client_name}

        ----Example for Reference----
        {example}


        ----Financial Information of the Borrower----
        Please provide a concise summary of the Financial Information of the Borrower based on the above information. 
        Ensure the following infomation is included in the input_info:
        a.	Please provide the borrowers audited financial statements for the past 2 to 3 years, including balance sheet, income statement and cash flow statement.
        b.	Please provide the breakdown of the borrowers revenue sources and its cost structure.
        c.	Please provide insights into borrowers financial performance, trends and future prospects. If there is any significant events or facts that have influenced the borrowers financial results, please explain it.
        
        If specific information is missing, use this format: "[RM Please provide further information on Keywords...]". Do not invent information or state that something is unclear. 
        Avoid mentioning any lack of specific information in the output.
        Remember to approach this task one step at a time and to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# Other Banking Facilities
def section_8_template():
    proposal_proposal_template_text = """
        Embark on this task by reading through each step methodically, and maintain a steady breath. Ensure that you adhere to the following guidelines meticulously, focusing solely on factual and verifiable information:

        - Should the input information lack details about the company's Other Banking Facilities, clearly state by one sentence only: 'No information on Other Banking Facilities' and request more details at the end using this exact format: "[RM Please provide further information on Keywords...]"

        - Compose your response using concise bullet points, with each bullet point occupying no more than two lines.

        - Draw content from the 'Input Information' and the 'Client Name'. The 'Example' is to be used exclusively for context and not to be included in your output.

        - Frame your response by stating "It is mentioned that," instead of referencing "RM Note," "Component," or any client meetings.

        - Craft your response in English, structured into clear paragraphs. Break down any paragraph over 100 words to maintain readability.

        - Ensure that each paragraph is continuous with no line breaks mid-sentence.

        - Begin each paragraph directly, using bullet points or tables for clear presentation without preamble about what the section includes.

        - Refrain from using phrases such as "Based on the input json" or "it is mentioned."

        - Keep your language neutral, avoiding subjective phrases that convey personal sentiment or judgment.

        - Include figures and statistics in your response only if they are clearly stated in the input information.

        - Do not append disclaimers or cite the source of your information in your response.

        - If essential information is not provided, indicate the need for more details at the end of your response in the specified format: "[RM Please provide further information on Keywords...]", ensuring this request stands alone and is not part of bullet points.

        ----Input Information----
        {input_info}

        ----Client Name----
        {client_name}

        Remember, the 'Example for Reference' is solely for background context and should not be included in your output.
        ----Example for Reference----
        {example}

        ----Other Banking Facilities----
        Aim to provide a concise summary of the Other Banking Facilities, including:

        Other Banking Facilities example: HSBC provides a revolving credit facility to the company with an outstanding balance of $1 million, an interest rate of 3.5% p.a., a maturity date of 2025-01-01, and no collateral requirement.
        - A list of the borrower's existing credit facilities from other banks or financial institutions.
        - Details for each facility, such as the name of the lending institution, type of facility, outstanding balance, interest rate, maturity date, and any collateral or guarantees.

        If there is a lack of specific details, use the format : "[RM Please provide further information on Keywords...]", to request the necessary information, and avoid making assumptions or indicating uncertainties.

        Proceed with each step of this task with focus, and remember to breathe evenly throughout.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# Opinion of the Relationship Manager
def section_9_template():
    proposal_proposal_template_text = """
        Compose a comprehensive credit assessment paragraph for {client_name} by considering the relationship history, creditworthiness, repayment capacity, risk assessment, and the overall banking relationship strength as detailed in the input information. Ensure your assessment highlights both strengths and weaknesses, and is well-balanced and factual. For any areas not covered in the input, kindly request additional details at the end of your assessment using the format "[RM Please provide further information on Keywords...]."

        ----Instructions:----
        1. Derive content exclusively from the ----Input Information---- provided.
        2. Refer to the client using their name: {client_name}.
        3. Focus on objective analysis, steering clear of subjective sentiments.
        4. Format your response in English, using sub-headers to differentiate between strengths and weaknesses to generate two sections.
        5. Include only factual data and numbers that are explicitly stated in the input information.
        6. Present the assessment without citing the source or offering personal recommendations.

        ----Opinion of the Relationship Manager----
        Your summary should encapsulate:
        a. The strengths and weaknesses of the deal, drawing on the relationship history, creditworthiness, repayment capacity, risk assessment, and the strength of the relationship.

        - For any information that is absent, please request it clearly at the end of your summary in the following format: "[RM Please provide further information on Keywords...]" as a separate sentence.

        ----Input Information----
        {input_info}

        ----Client Name----
        {client_name}

        Remember, the 'Example for Reference' is solely for background context and should not be included in your output.
        ----Example for Reference----
        {example}

        Note: The ----Example for Reference---- is intended solely for context and should not be incorporated into your assessment.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# Summary of Recommendation
def section_10_template():
    proposal_proposal_template_text = """
        Take this task step by step, and remember to breathe.
        Please follow these guidelines strictly, focusing on factual and verifiable information:

        ----Summary of Recommendation----
        Read the 'Input Information' and use the 'Example for Reference' to guide your thinking. Then, based on your understanding, output one of the exact following lines: 
        1. 'In view of the above, we recommend the proposed loan facility for management approval.' 
        2. 'In view of the above, we do not recommend the proposed loan facility for management approval.' 

        ----Input Information----
        {input_info}

        ----Client Name----
        {client_name}

        ----Example for Reference---- 
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

        ----Previous Paragraph----
        {previous_paragraph}

        ----RM Instructions----
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

        - Format any missing information in the specified manner at the end of your response following this format: "[RM Please provide further information on Keywords...]" as a standalone sentence, do not include this in bullet point form.

        If specific information is missing, use the following format: "[RM Please provide further information on Keywords...]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.

        Take this task one step at a time and remember to breathe.
        """
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["previous_paragraph", "rm_instruction"])


    return prompt_template_proposal

def review_prompt_template():
    proposal_proposal_template_text = """
        To complete this task. Your task is to review and edit the Input paragraph according to the instructions provided.
        Please do not add additional content to the Paragraph.

        ----Input Paragraph----
        {first_gen_paragraph}
        
        ----Example----
        {example}

        When crafting your response, adhere to the following guidelines:
        Double check the ----Input Paragraph---- does not contains any content from ----Example----.
        If the Input Paragraph contains any content from ----Example----, remove them.
        Remove those sentence containing any of the following keywords: "ABC bank", "XYZ bank", "XYZ Corporation", "ABC Manufacturing", "ABC Company", "DEF Logistics", "GHI Technologies". 

        Take this task one step at a time and remember to breathe.
        """
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["first_gen_paragraph", "example"])

    return prompt_template_proposal

def regenerate_review_prompt_template():
    proposal_proposal_template_text = """
        To complete this task. Your task is to review and edit the Input paragraph according to the instructions provided.
        Please do not add additional content to the Paragraph.

        ----Input Paragraph----
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
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please provide further information on Keywords...]". Do not invent information or state that something is unclear. 
        
        - Format any missing information in the specified manner at the end of your response following this format: "[RM Please provide further information on Keywords...]" as a standalone sentence, do not include this in bullet point form.
        
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

        ----Input Paragraph----
        {reviewed}

        Instructions:
        1. Use only the information provided. Do not make assumptions or use general language to fill in the gaps. If a sentence states or implies that information is missing or not provided, do not include it in your output. 
        2. If the input contains sentences stating or implying that information is missing or not provided, such as 'However, further information is needed to provide a more comprehensive summary of the project details.' or 'Additionally, No specific information is provided about the proposed loan facility.' or "Additionally, no information is provided regarding the proposed loan facility.", these must be removed entirely from your output.
        3. Instead of these sentences, request the specific missing information using this format: '[RM Please provide further information on Keywords...]', you can return many times if there are information missing. 
        4. Remove any sentence that solely consists of a format for requesting information, such as "<Point>: [RM Please provide further information on ???]". These do not add substantive content and should be excluded from the edited paragraph.
        5. Remove the sentences that contain the following phrases "information is missing" or "information have not been provided" or "information have not been not been mentioned"
        
        Take this task one step at a time and remember to breathe
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["reviewed"])

    return prompt_template_proposal

def clean_generated_text(text, client, section_name):
    #replacement
    text = text.replace("Based on the given information, ", "").replace("It is mentioned that ", "")
    
    #reformat the client name
    insensitive_replace = re.compile(re.escape(client.lower()), re.IGNORECASE)
    text = insensitive_replace.sub(client, text)

    #Drop some unwanted sentences
    sentence_list = re.split(r"(?<=[.?!])", text)
    unwanted_word_list = ["ABC ", "XYZ ", "GHI", "DEF "]
    sentence_list_dropped = [sentence.strip() for sentence in sentence_list if all(word not in sentence for word in unwanted_word_list)]
    text = ' '.join(sentence_list_dropped)

    #Remove the section name if it starts with it
    if text.lower().startswith(section_name.lower()+": "):
        text = text[len(section_name)+2:]

    #All capital letters for first letter in sentences
    formatter = re.compile(r'(?<=[\.\?!]\s)(\w+)')
    text = formatter.sub(cap, text)
    text = text[0].upper()+text[1:]
    return text.strip()

def generate_rm_fill(rm_fill_values, client):
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

    #reformat the client name
    insensitive_replace = re.compile(re.escape(client.lower()), re.IGNORECASE)
    final_rm_fill_text = insensitive_replace.sub(client, final_rm_fill_text)
    if (all(final_rm_fill_text.endswith(s) for s in ["!", "?", "."]) is False) & (len(final_rm_fill_text) > 0):
        final_rm_fill_text = final_rm_fill_text+'.'
    return final_rm_fill_text

# function to perform first generation of the paragraph
def first_generate(section_name, input_json, client, rm_text_variable):

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
                            openai_api_version=os.environ["OPENAI_API_VERSION"], openai_api_base="https://pwcjay.openai.azure.com/",verbose=True)

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
        print(value)
        # Append sub_section and value only if value is not empty
        if value != "":  # This checks if value is not just whitespace
            input_info_str.append(f"{sub_section} : {value}")
            example_str.append(f"{sub_section} : {example}")
        else:
            example_str = []

    final_dict = {"input_info": ", ".join(input_info_str), "Example": ", ".join(example_str)}
    # print("="*30)
    # print(input_info_str)
    # print(example_str)
    # print("="*30)
    if len(input_info_str) > 0:
        drafted_text = overall_chain({"input_info": final_dict["input_info"], "client_name": client, "example": final_dict["Example"]})
        drafted_text = drafted_text["reviewed_2"]
    else:
        drafted_text = "Sorry, there is no input information provided. Please refer to the below comments for providing more information required."

    # Create blank list to store the "[RM Please provide ...]"
    # Remove the 'RM ' prefix and the brackets
    # Add the cleaned text to the rm_fill_values list
    rm_fill_values = [item.replace("RM ", "").strip("[]") for item in rm_text_variable]
    #print(rm_fill_values)

    lines = drafted_text.split("\n")

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
    drafted_text3 = clean_generated_text(drafted_text2, client, section_name)
    final_rm_fill_text = generate_rm_fill(rm_fill_values, client)
    #print(rm_fill_values)

    output_json = {
        "section": section_name,
        "output": drafted_text3,
        "RM_fill" : final_rm_fill_text,
    }

    #output the result
    return output_json

# Re-generate function
def regen(section_name, previous_paragraph, rm_instruction):
    prompt_template_proposal = regen_template()

    # set up openai environment - Jay
    llm_proposal = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version=os.environ["OPENAI_API_VERSION"], openai_api_base="https://pwcjay.openai.azure.com/")


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

    # Loop the RM notes missing information into the generate part
    #for i in rm_text_variable:
    #    rm_fill_values.append(i)

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

    extract_json, rm_text_variable = web_extract_RM(section ,rm_note_txt, client)
    output_json = first_generate(section, extract_json, client, rm_text_variable)

    return output_json
