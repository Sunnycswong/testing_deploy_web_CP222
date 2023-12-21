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

import export_doc
import extract_info

DEPLOYMENT_NAME = "gpt-35-16k"
OPENAI_API_TYPE = "azure"
OPENAI_API_BASE = "https://pwcjay.openai.azure.com/"
OPENAI_API_VERSION = "2023-09-01-preview"
OPENAI_API_KEY = "f282a661571f45a0bdfdcd295ac808e7"

client = "GogoX"
section_name = 'Executive Summary'
rm_note_txt = """Client: GogoX
Industry: Logistics and Delivery Services
Date: 20 Nov 2023

1	Company Background:		
	GogoX is a leading logistics and delivery service provider, offering on-demand delivery solutions to individuals and businesses. Established in 2013, the company has rapidly expanded its operations and established a strong presence in the market. GogoX operates a user-friendly mobile application and web platform, connecting customers with a network of professional drivers and delivery partners.		

2	Financial Performance:		
GogoX has demonstrated consistent revenue growth over the past few years, driven by increasing customer adoption and expansion into new markets.			
The company's financial statements reflect a healthy profitability margin, indicating effective cost management and operational efficiency.			

3	Market Position and Competitive Landscape:		
GogoX has successfully positioned itself as a market leader in the logistics and delivery industry, leveraging its strong brand recognition and innovative technology platform.			
The company has built a robust network of drivers and delivery partners, enabling quick and reliable service fulfillment.			
GogoX's competitive advantage lies in its ability to offer cost-effective and flexible solutions tailored to meet the needs of various customer segments, including e-commerce, retail, and individual users.			

4	Growth Strategy and Market Potential:		
GogoX has outlined a comprehensive growth strategy focused on expanding its geographical presence, diversifying its service offerings, and enhancing customer experience.			
The company plans to enter new markets, both domestically and internationally, to capture additional customer segments and increase market share.			
GogoX aims to invest in technology and infrastructure improvements to streamline operations, optimize delivery routes, and enhance overall efficiency.			

5	Risk Assessment:		
The logistics industry is subject to various risks and weaknesses, including intense competition, regulatory changes, and economic downturns. GogoX has implemented risk mitigation measures such as diversification of services and markets, maintaining strong relationships with key partners, and closely monitoring market trends.			
Operational risks, such as driver availability, vehicle maintenance, and service disruptions, are managed through rigorous driver screening, continuous training programs, and proactive maintenance schedules.			
Financial risks are mitigated by maintaining a healthy liquidity position, diversifying funding sources, and prudent financial management practices.			
			
6	Credit Request and Repayment Plan:		
GogoX is requesting a credit facility of $10 million to support its expansion plans			
The proposed repayment plan consists of regular principal and interest payments over a 3 years term, aligning with the company's projected cash flow generation and financial performance.			
			
7	Project Details:		
The Expansion plans include 3 areas:
a) Expanding the business in 3 cities in China (Beijing, Shanghai and Shenzhen)
b) technology investments (AI assistant fo drivers and AI-based matching among drivers and customers)
c) Working capital needs: expanding 300 more permanent staff, including customer service supports in the 3 new cities, technology experts in IT and AI.			
The timeline for this expansion is within the next 36 months. 

8	Shareholders and Group Structure:		
New Horizon Capital (15%), Alibaba Entrepreneurs Fund (23.3%), InnoVision Capital (17.2%) are the shareholders of GogoX
			
Conclusion:			
GogoX has demonstrated a strong market position, consistent financial performance, and a well-defined growth strategy. With its robust operational capabilities, innovative technology platform, and customer-centric approach, the company is well-positioned to capitalize on the growing demand for logistics and delivery services. The proposed credit facility, in line with the company's financial projections, will support GogoX's expansion plans and enable it to maintain its competitive edge in the market.					
"""

#%%
output_dict = extract_info.run_first_gen("Opinion of the Relationship Manager", rm_note_txt, client, deployment_name=DEPLOYMENT_NAME, openai_api_version=OPENAI_API_VERSION, openai_api_base=OPENAI_API_BASE)
print(">>> Generated Output:", output_dict['output'])
print(">>> RM fill:", output_dict['RM_fill'])

#%%
output_dict = extract_info.run_first_gen("Client Request", rm_note_txt, client, deployment_name=DEPLOYMENT_NAME, openai_api_version=OPENAI_API_VERSION, openai_api_base=OPENAI_API_BASE)
print(">>> Generated Output:", output_dict['output'])
print(">>> RM fill:", output_dict['RM_fill'])

#%%
extract_info.run_first_gen("Shareholders and Group Structure", rm_note_txt, client, deployment_name=DEPLOYMENT_NAME, openai_api_version=OPENAI_API_VERSION, openai_api_base=OPENAI_API_BASE) 

#%%
extract_info.run_first_gen("Executive Summary", rm_note_txt, client, deployment_name=DEPLOYMENT_NAME, openai_api_version=OPENAI_API_VERSION, openai_api_base=OPENAI_API_BASE) 

#%%
extract_info.run_first_gen("Management", rm_note_txt, client, deployment_name=DEPLOYMENT_NAME, openai_api_version=OPENAI_API_VERSION, openai_api_base=OPENAI_API_BASE) 

#%%
extract_info.run_first_gen("Financial Information of the Borrower", rm_note_txt, client, deployment_name=DEPLOYMENT_NAME, openai_api_version=OPENAI_API_VERSION, openai_api_base=OPENAI_API_BASE)

#%%
extract_info.run_first_gen("Other Banking Facilities", rm_note_txt, client, deployment_name=DEPLOYMENT_NAME, openai_api_version=OPENAI_API_VERSION, openai_api_base=OPENAI_API_BASE) 

# %%
output_dict = extract_info.run_first_gen("Project Details", rm_note_txt, client, deployment_name=DEPLOYMENT_NAME, openai_api_version=OPENAI_API_VERSION, openai_api_base=OPENAI_API_BASE)
print(">>> Generated Output:", output_dict['output'])
print(">>> RM fill:", output_dict['RM_fill'])

#%%
extract_info.run_first_gen("Summary of Recommendation", rm_note_txt, client, deployment_name=DEPLOYMENT_NAME, openai_api_version=OPENAI_API_VERSION, openai_api_base=OPENAI_API_BASE) 

#%%
extract_info.run_first_gen("Industry / Section Analysis", rm_note_txt, client, deployment_name=DEPLOYMENT_NAME, openai_api_version=OPENAI_API_VERSION, openai_api_base=OPENAI_API_BASE) 
