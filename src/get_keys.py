from langchain.utilities import BingSearchAPIWrapper
import os

class GetAzureKeys(object):
    
    def __init__(self):
        # set up openai environment - Jay
        # os.environ["OPENAI_API_TYPE"] = "azure"
        # os.environ["OPENAI_API_BASE"] = "https://pwcjay.openai.azure.com/"
        # os.environ["OPENAI_API_VERSION"] = "2023-05-15"
        # os.environ["OPENAI_API_KEY"] = "f282a661571f45a0bdfdcd295ac808e7"

        # #set up openai environment - Cyrus
        os.environ["OPENAI_API_TYPE"] = "azure"
        os.environ["OPENAI_API_BASE"] = "https://pwc-cyrus-azure-openai.openai.azure.com/"
        os.environ["OPENAI_API_KEY"] = "e1948635e8024556a6a55e37afcce932"
        os.environ["DEPLOYMENT_NAME"] = "gpt-35-turbo-16k"

        # bing search key - Cyrus
        os.environ['BING_SUBSCRIPTION_KEY'] = "037a557cd0e84694bf8be874fe34e981"
        os.environ["BING_SEARCH_URL"] = "https://api.bing.microsoft.com/v7.0/search"