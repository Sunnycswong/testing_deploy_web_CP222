
# def bing_web_search(self, query, k):
#     '''
#     This sample makes a call to the Bing Web Search API with a query and returns relevant web search.
#     Documentation: https://docs.microsoft.com/en-us/bing/search-apis/bing-web-search/overview
#     '''

#     # Add your Bing Search V7 subscription key and endpoint to your environment variables.
#     subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
#     endpoint = os.environ['BING_SEARCH_V7_ENDPOINT'] + "/v7.0/search"

#     # Construct a request
#     mkt = 'en-US'
#     params = { 'q': query, 'mkt': mkt }
#     headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

#     # Call the API
#     try:
#         response = requests.get(endpoint, headers=headers, params=params)
#         response.raise_for_status()

#         # print("\nHeaders:\n")
#         # print(response.headers)
#         result_list= []

#         # print("\nJSON Response:\n")
#         # print(response.json())

#         result = response.json()['webPages']['value']

#         for r in result:
#             title = r['name']
#             snippet = r['snippet']
#             link = r['url']
#             result_list.append({"title":title,
#                                 "snippet":snippet,
#                                 "link":link})

#         return result_list
#     except Exception as ex:
#         raise ex

# test
# bing_web_search("GOGOX CEO Hong Kong")

"""
[{'title': 'Co-founder & Cheap Everything Officer (CEO) - GOGOX - LinkedIn', 'snippet': 'Steven Lam Co-Founder & Cheap Everything Officer at GoGoX (We are actively hiring! PM me if you like adventure and challenges!) Hong Kong SAR 2K followers 500+ connections Join now New to...', 'link': 'https://hk.linkedin.com/in/stevenhylam'}, 
 {'title': 'Good to Go: Meet the CEO Behind Hong Kong’s First Billion Dollar ...', 'snippet': 'Steven Lam, Co-CEO, Executive Director and Co-founder of GOGOX Connecting Asia Formerly known as GOGOVan, GOGOX is a tech-driven logistics startup based out of Hong Kong.', 'link': 'https://www.ypo.org/2023/03/meet-steven-lam-ypo-member-and-winner-of-ey-entrepreneur-of-the-year-2022/'},
 {'title': "GoGoX's Steven Lam on the mindset shift that changed his life", 'snippet': '02 August 2023 - 5:00 PM Tech unicorn CEO shares the simple mindset shift that changed his life Steven Lam dropped out of high school in Hong Kong, but then a plane ticket and an idea cooked up in a Chinese restaurant changed his life. Steven Lam has a unique way of looking at the world.', 'link': 'https://www.theceomagazine.com/business/innovation-technology/steven-lam-gogox/'},
 {'title': 'GOGOX', 'snippet': 'LAM was granted accolades including Hong Kong’s Ten Outstanding Young Persons Selection in 2018 (2018十大傑出青年), and 50 Asians to watch of The Straits Timesin 2018 (海峽時報50位受矚目亞洲人). ... Mr. YE has served as the Chief Executive Officer of Golden Pacer, a financial technology platform since April 2021, the Chief ...', 'link': 'https://www.gogoxholdings.com/en/about_board.php'}, 
 {'title': 'Steven Lam | Tatler Asia', 'snippet': 'The Gogox founder has built Asia’s Uber for vans ... He then moved back to Hong Kong and started Boxad, a company selling ads on food takeaway boxes. Inspired by the difficulty the company experienced trying to book vans, he and two friends co-founded Gogovan with a combined HK$20,000 of savings. ... GoGoX CEO Steven Lam on his journey from ...', 'link': 'https://www.tatlerasia.com/people/steven-lam'},
 {'title': 'GoGoX Entrepreneur Steven Lam on His Drive to Succeed - Prestige Online', 'snippet': 'Hong Kong’s first unicorn start-up, with a valuation of more than US$1billion, GoGoX seems like the ultimate entrepreneur’s dream. The on-demand delivery platform revolutionised the traditional logistics industry in Asia back in 2013 with a mobile app that connects individuals and businesses to van drivers for the transportation of goods.. Fast forward to today and GoGoX – the “x ...', 'link': 'https://www.prestigeonline.com/hk/people/driven-to-succeed-how-gogox-entrepreneur-steven-lams-billion-dollar-business-came-to-be/'},
 {'title': 'Watch GogoX CEO: Optimistic About Chinese Market - Bloomberg', 'snippet': 'Steven Lam, co-founder and chief executive officer at GogoX, discusses the company’s debut on the Hong Kong Stock Exchange, China’s tech crackdown and what if they are considering acquisitions.', 'link': 'https://www.bloomberg.com/news/videos/2022-06-24/gogox-ceo-optimistic-about-chinese-market'},
 {'title': 'GOGOX Company Profile - Office Locations, Competitors, Revenue ... - Craft', 'snippet': '$276.5 M Company Summary Overview GOGOX (formerly GOGOVAN) is a company providing an app-based logistics platform for transporting goods. The platform connects individuals and businesses directly to drivers and couriers for their delivery needs. Type Private Status Active Founded 2013 HQ HK | view all locations Website https://www.gogox.com/index/', 'link': 'https://craft.co/gogox'},
 {'title': 'GogoX, Hong Kong’s First Tech Unicorn Startup, Slumps In ... - Forbes', 'snippet': 'GogoX, formerly known as GogoVan, listed on the Hong Kong stock exchange, raising $85 million to grow its user base, raise its brand awareness, develop new services and products, and to fund...', 'link': 'https://www.forbes.com/sites/jaydecheung/2022/06/24/gogox-hong-kongs-first-tech-unicorn-startup-slumps-in-trading-debut/'},
 {'title': 'GogoX to Hold Rare In-Person Hong Kong IPO Press Briefing', 'snippet': 'He Song and Steven Lam, its co-chief executive officers, will be among those attending the occasion. The press conference signals how the financial circle in Hong Kong has revived face-to-face...', 'link': 'https://www.bloomberg.com/news/articles/2022-06-14/gogox-to-hold-rare-in-person-hong-kong-ipo-press-briefing'}]

"""