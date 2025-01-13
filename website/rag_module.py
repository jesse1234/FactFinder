import os
import torch
from dotenv import load_dotenv
from crewai.tools import tool
from duckduckgo_search import DDGS
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from transformers import BertTokenizer, BertModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import ContextualCompressionRetriever, EnsembleRetriever
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up api variables

load_dotenv()

# os.environ['SERPER_API_KEY'] = os.getenv('SERPER_API_KEY')
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

# Initialize LLM
llm = ChatOpenAI(
    model_name='gpt-4o-mini',
    temperature=0.1,
    max_tokens=1000
)

# Web Scraping function
def duckduckgo_search(query, num_results=5):
    """Perform DuckDuckGo search and return top results"""
    with DDGS() as ddgs:
        results = ddgs.text(query, backend='html')
        links = []
        for result in results:
            if len(links) >= num_results:
                break
            links.append({
                'url': result['href'],
                'title': result.get('title', 'No title')
            })
        return links

def scrape_content(link):
    try:
        response = requests.get(link)
        response.encoding = 'utf-8'

        # Check for paywall indicators in meta tag
        if 'paywall' in response.text.lower():
            print(f"Paywall detected for {link}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')

        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        
        if main_content:
            paragraphs = main_content.find_all('p')
        else:
            paragraphs = soup.find_all('p')

        article_text = ' '.join([p.get_text(strip=True) for p in paragraphs])
        return article_text if article_text else None
    except Exception as e:
        print(f"Error scraping {link}: {e}")
        return None

# Search and Embed Tool function

def search_and_embed(query: str):
    """
    Search the web, scrape content and store embeddings
    """
    try:
        results = duckduckgo_search(query, num_results=3)
        if not results:
            return "No results found"

        links = [{'url': res['url'], 'title': res['title']} for res in results]
        
        scraped_articles = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_link = {executor.submit(scrape_content, link['url']): link for link in links}
            for future in as_completed(future_to_link):
                link = future_to_link[future]
                try:
                    content = future.result()
                    if content:
                        scraped_articles.append({
                            'url': link['url'],
                            'title': link['title'],
                            'content': content
                        })
                except Exception as e:
                    print(f"Error scraping {link['url']}: {e}")

        if not scraped_articles:
            return "No content could be scraped from the articles"

        documents = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512, 
            chunk_overlap=200, 
            length_function=len
        )
        
        for article in scraped_articles:
            chunks = text_splitter.split_text(article['content'])
            for chunk in chunks:
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            'title': article['title'],
                            'url': article['url'],
                            'source': 'Web scrape'
                        }
                    )
                )
        if not documents:
            return "No documents could be processed"

        embeddings = OpenAIEmbeddings(model='text-embedding-3-small')
        vector_store = Chroma.from_documents(documents, embedding=embeddings, persist_directory='./chroma_db')
        
        return documents

    except Exception as e:
        print(f"Error in search_and_embed: {str(e)}")
        return f"Error occurred: {str(e)}"
    

# Get News Tool function

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")

class EmbeddingsFilter:
    def __init__(self, embeddings, similarity_threshold=0.75):
        self.embeddings = embeddings
        self.similarity_threshold = similarity_threshold

    def filter(self, documents):
        if not documents:
            return []

        texts = [doc.page_content for doc in documents]
        embeddings = self.embeddings.embed_documents(texts)
        embeddings_tensor = torch.tensor(embeddings)

        similarities = torch.nn.functional.cosine_similarity(
            embeddings_tensor.unsqueeze(1),
            embeddings_tensor.unsqueeze(0),
            dim=2
        )

        max_similarities = similarities.max(dim=1).values
        mask = max_similarities >= self.similarity_threshold
        return mask.tolist()
    
def sliding_window_tokenize(text, window_size, stride):
    words = text.split()
    chunks = []
    for i in range(0, len(words), stride):
        chunk = " ".join(words[i:i + window_size])
        chunks.append(chunk)
    return chunks

def process_doc_batch(docs, query, tokenizer, model):
    scores = []
    query_tokens = tokenizer(query, return_tensors="pt", padding=True, truncation=True, max_length=512)

    for doc in docs:
        text_chunks = sliding_window_tokenize(doc.page_content, window_size=1024, stride=512)
        max_score = 0

        for chunk in text_chunks:
            chunk_tokens = tokenizer(chunk, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                query_embeddings = model(**query_tokens).last_hidden_state[:, 0, :]
                chunk_embeddings = model(**chunk_tokens).last_hidden_state[:, 0, :]
                score = torch.nn.functional.cosine_similarity(query_embeddings, chunk_embeddings).item()
                max_score = max(max_score, score)

        scores.append((max_score, doc))

    return scores

def batch_rerank_documents(query, docs, embeddings_filter, tokenizer, model, batch_size=16):
    filtered_docs = embeddings_filter.filter(docs)
    scores = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i in range(0, len(filtered_docs), batch_size):
            batch_docs = docs[i:i + batch_size]
            futures.append(executor.submit(process_doc_batch, batch_docs, query, tokenizer, model))

        for future in as_completed(futures):
            scores.extend(future.result())

    return sorted(scores, key=lambda x: x[0], reverse=True)

def get_news(query: str) -> str:
    """
    Search the vector store for relevant information that addresses the query.
        
    Args:
        query (str): The search query to look up in the vector store
            
    Returns:
        str: Formatted results from the search
    """
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

        vectorstore_retriever = vector_store.as_retriever(
            search_type="mmr", search_kwargs={"k": 3, "fetch_k": 20, "lambda_mult": 0.7}
        )

        keyword_retriever = BM25Retriever.from_documents(
            search_and_embed(query), k=3
        )

        compressor = LLMChainExtractor.from_llm(llm)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=vectorstore_retriever
        )

        # ensemble_retriever = EnsembleRetriever(
        #     retrievers=[
        #         compression_retriever,
        #         vectorstore_retriever,
        #         keyword_retriever
        #     ],
        #     weights=[0.5, 0.3, 0.2]
        # )

        ensemble_retriever = EnsembleRetriever(
            retrievers=[
                vectorstore_retriever,
                keyword_retriever
            ],
            weights=[0.7, 0.3]
        )

        retrieved_docs = ensemble_retriever.invoke(query)

        embeddings_filter = EmbeddingsFilter(
            embeddings=embeddings,
            similarity_threshold=0.75
        )

        reranked_docs = batch_rerank_documents(
            query=query,
            docs=retrieved_docs,
            embeddings_filter=embeddings_filter,
            tokenizer=tokenizer,
            model=model,
            batch_size=16
        )

        results_text = []
        for score, doc in reranked_docs[:5]:
            metadata = doc.metadata
            result = (
                f"Score: {score:.4f}\n"
                f"Title: {metadata.get('title', 'No title')}\n"
                f"URL: {metadata.get('url', 'No URL')}\n"
                f"Content: {doc.page_content}\n"
                "-------------------\n"
            )
            results_text.append(result)

        return "\n".join(results_text)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return f"Error retrieving news: {str(e)}"

search_and_embed_tool = tool(search_and_embed)
get_news_tool = tool(get_news)

# Defining Agents

# Research agent
Research_Agent = Agent(
    role="News Web Researcher",
    goal="Search the internet for relevant news articles pertaining to users' query and create embeddings from that",
    backstory="You are an expert news researcher and excel at finding relevant news articles on the internet and preparing the information for analysis.",
    verbose=True,
    allow_delegation=False,
    tools=[search_and_embed_tool],
    llm=llm
)

# Retriever agent
Retriever_Agent = Agent(
    role="Information Retriever",
    goal="Retrieve relevant information from the vector store using hybrid search and reranking",
    backstory="You are very skilled at querying vector stores to find the most relevant information for a given question. You use advanced techniques like hybrid search and reranking to ensure the best results.",
    verbose=True,
    allow_delegation=False,
    tools=[get_news_tool],
    llm=llm
)

Grader_Agent = Agent(
    role='Answer Grader',
    goal='Filter out erroneous retrievals',
    backstory=(
        "You are a grader assessing the relevance of a retrieved document to a user's question."
        "If the document contains keywords related to the user question, grade it as relevant."
        "This is not a stringent test; the goal is to ensure the answer's relevance to the question."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm
)

Hallucination_Grader = Agent(
    role='Hallucination Grader',
    goal='Filter out hallucination',
    backstory=(
        "You are a hallucination grader that assesses whether an answer is grounded in or supported by facts."
        "Meticulously review the answer and check for alignment with the questions asked."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Analyst agent
Analyst_Agent = Agent(
    role="Fact Analyst",
    goal="Provide a thorough and detailed analysis of the retrieved information to fact-check the user's claim.",
    backstory=(
        "You are an expert fact-checker known for your meticulous and comprehensive analyses."
        "You critically evaluate information from multiple sources, cross-verify facts, and present findings in a clear, structured manner."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Defining Tasks
# Research task
research_task = Task(
    description=(
        "Search the internet for relevant news articles pertaining to a users' query: '{claim}'."
        "Retrieve the urls, article content and title of the articles."
        "Do not use Wikipedia as a reliable source of information. The information must come from reputable organization"
        "Create embeddings from the scraped content of relevant articles."
    ),
    agent=Research_Agent,
    expected_output="List of url, article content, article titles and embeddings of relevant articles"
)

# Retrieval task
retrieval_task = Task(
    description=(
        "Using the vector store created from the web search, retrieve the most relevant "
        "information to address the user's claim: '{claim}'.\n"
        "\n"
        "Provide the following for each retrieved article:\n"
        "- **Title**\n"
        "- **URL**\n"
        "- **Content Chunks**: Present significant excerpts or chunks relevant to the claim.\n"
        "\n"
        "Ensure that the information is organized clearly to aid the analyst in their evaluation."
    ),
    agent=Retriever_Agent,
    context=[research_task],
    expected_output=(
        "A list of relevant articles with their titles, URLs, and content chunks."
    )
)

# grader_task = Task(
#     description=(
#         "Evaluate if the response from the retriever task is relevant to the question: '{claim}'."
#         "Return 'yes' if the retrieved content aligns with the question, or 'no' if it does not."
#         "Provide only 'yes' or 'no' with additional explanations."
#     ),
#     agent=Grader_Agent,
#     context=[retrieval_task],
#     expected_output="Binary response ('yes' or 'no') indicating relevance of the document to the question."
# )

# hallucination_task = Task(
#     description=(
#         "Based on the grader's task response for the question '{claim}', determine whether the answer is factually grounded."
#         "Return 'yes' if the answer is factual and relevant, or 'no' if it contains hallucinations or unsupported information."
#         "Provide only 'yes' or 'no' answers with additional explanations."
#     ),
#     agent=Hallucination_Grader,
#     context=[grader_task],
#     expected_output="Binary response ('yes' or 'no') with explanation indicating factual accuracy of the answer."
# )

# Analyst task
analysis_task = Task(
    description = (
        "As a Fact Analyst, your task is to thoroughly analyze the retrieved information and provide a comprehensive, fact-checked response to the claim: {claim}.\n"
        "\n"
        "Your analysis should include the following:\n"
        "1. **Summary of Findings:** Present a set of bullet points that describe the key details and claims from each relevant article. Reference each article by its title and URL, but do not enumerate them as 'Article 1', 'Article 2', etc. Instead, integrate the article's source or a key identifying detail directly into your explanation. Focus on clearly describing the information and how it relates to the claim.\n"
        "2. **Cross Verification:** Cross-verify the information across different sources, highlighting any agreements of discrepancies among them.\n"
        "3. **Contextual Background:** Include any necessary background information that helps in understanding the claim and its significance.\n"
        "4. **Conclusion:** Based on your analysis, draw a well-reasoned conclusion about the validity of the claim.\n"
        "5. **Verdict:** Clearly state your verdict as one of the following options: True, False, Partly True, Partly False or Not Enough Information.\n"
        "6. **References:** List all the articles you used in your analysis, including their titles and URLs.\n"
        "\n"
        "The response should be structured in the following format:\n"
        "\n"
        "**Summary of Findings:**\n"
        "- [Describe details from a relevant article, referencing the article's title or source within the explanation, and include the URL at the end.]\n"
        "- [Describe details from another relevant article in a similar fashion, ensuring the narrative flows naturally.]\n"
        "- [Continue for all relevant articles.]\n"
        "\n"
        "**Cross-Verification:**\n"
        "- Compare and contrast the information from the articles...\n"
        "\n"
        "**Contextual Background:**\n"
        "- Provide any additional background information...\n"
        "\n"
        "**Verdict:**\n"
        "- Your verdict here...\n"
        "\n"
        "**References**\n"
        "- [Title of article 1] - [URL of article 1]\n"
        "- [Title of article 2] - [URL of article 2]\n"
        "[...]\n"
        "\n"
        "Ensure that your analysis and verdict are strictly supported by the retrieved context. Do not include any information not found in the context. DO NOT begin your answer with 'The first article ...' or 'The article ..., The article titled...'. DO NOT put the title or url of the articles in the **Summary of Findings** section, just give the information found in those articles"
        "\n"
        "Below is an example of a perfect response (for a different claim), provided as a guide. Do not copy it verbatim, but follow its structure, style, and level of detail:\n"
        "\n"
        "Follow the same format, style, and approach as shown in the Example of a Perfect Response below." 
        "Do not copy the example verbatim, but produce a similarly structured and detailed response based only on the new claim and context provided here."
        "\n"
        "**Example of a Perfect Response:**\n"
        "**Summary of Findings:**\n"
        "- Luigi Mangione, a 26-year-old Ivy League graduate from a prominent Maryland real estate family, has been identified as the suspect in the fatal shooting of UnitedHealthcare CEO Brian Thompson. He expressed anger towards health insurance companies and corporate greed in a handwritten document found on him during his arrest. Mangione faces charges in Pennsylvania for possession of an unlicensed firearm, forgery, and providing false identification to police. Manhattan prosecutors are working to extradite him to New York to face a murder charge.\n"
        "- Authorities believe Mangione will be sent to New York to face the murder charge despite his resistance to extradition. His family expressed shock and devastation over his arrest. Law enforcement used various forensic evidence to track down the suspect, who was eventually apprehended with the help of a tip from a McDonald's employee.\n"
        "- Mangione comes from a prominent Maryland real estate family and graduated as valedictorian from the Gilman School in Baltimore. His family expressed shock and devastation over his arrest and asked for prayers for all involved. Authorities are investigating the suspect's actions, including leaving behind inscribed shell casings, for possible motives.\n"
        "- New York Gov. Kathy Hochul is signing a request for a governor's warrant to ensure Mangione is held accountable in New York. Pennsylvania Gov. Josh Shapiro praises the McDonald's customer who alerted police to the suspect. Mangione was arrested in Altoona, Pennsylvania, after a McDonald's customer recognized him and notified an employee. Images of Mangione released by Pennsylvania State Police showed him in the corner of the McDonald's holding what appeared to be hash browns.\n"
        "\n"
        "**Cross-Verification:**\n"
        "- The information regarding Luigi Mangione being the suspect in the killing of UnitedHealthcare CEO Brian Thompson is consistent across all sources.\n"
        "- Details about Mangione's background, his arrest in Pennsylvania, and the efforts to extradite him to New York are corroborated in multiple articles.\n"
        "\n"
        "**Contextual Background:**\n"
        "Luigi Mangione, a 26-year-old with a notable educational background and family history, has been charged as the suspect in the murder of UnitedHealthcare CEO Brian Thompson. His arrest in Pennsylvania and the subsequent legal proceedings to extradite him to New York have garnered significant attention.\n"
        "\n"
        "**Verdict:**\n"
        "Based on the comprehensive analysis of the provided information, it can be concluded that Luigi Mangione is indeed the suspect charged with the murder of the UnitedHealthcare CEO, Brian Thompson.\n"
        "\n"
        "**References:**\n"
        "- [Luigi Mangione has been charged with murder - ABC News](https://abcnews.go.com/US/unitedhealthcare-ceo-shooting-latest-net-closing-suspect-new/story?id=116591169)\n"
        "- [Key details about the man accused of killing UnitedHealthcare's CEO - AP News](https://apnews.com/article/unitedhealthcare-ceo-brian-thompson-shooting-79a9710978fc7adbb23d3fed4ea2f70d)\n"
        "- [What we know about Luigi Mangione, suspect charged - CBS News](https://www.cbsnews.com/news/luigi-mangione-healthcare-ceo-shooting-what-we-know/)\n"
        "- [Suspect in the killing of UnitedHealthcare's CEO struggles, shouts - AP News](https://apnews.com/article/unitedhealthcare-ceo-shooting-suspect-c68d0328f278d85fcf201ae89f634098)\n"
        "\n"
        "IMPORTANT:\n"
        "1. Use ONLY the provided context for information. Do not speculate or add information not found in the context.\n"
        "2. Do not introduce external knowledge.\n"
        "3. If the context doesn't provide enough information, say 'Not Enough Information'.\n"
        "4. Do not enumerate articles as 'Article 1, Article 2' and do not say 'the context provided', 'the articles provided...' or 'The first article from..., The second article from...'.Instead, integrate the information from the articles naturally by referencing each article's title and content directly.\n"
        "5. The final format and style should be similar to the example provided.\n"
        "6. Clearly state your verdict as one of the following options: True, False, Partly True, Partly False or Not Enough Information.\n"
        "7. DO NOT use Wikipedia as a source of credible information."
    ),
    agent=Analyst_Agent,
    context=[retrieval_task],
    expected_output=(
        "A detailed, structured analysis of the claim, including summaries, cross-verification, contextual background, a conclusion, a verdict, and references."
    )
)

fact_check_crew = Crew(
   agents=[Research_Agent, Retriever_Agent, Analyst_Agent],
   tasks=[research_task, retrieval_task, analysis_task],
   verbose=True, 
)