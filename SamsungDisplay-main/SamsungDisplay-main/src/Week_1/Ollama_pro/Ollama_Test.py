# Ollama_Test.py
import gradio as gr
import bs4
import ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings


# 문서 로드 및 벡터화
def load_and_retrieve_docs(url: str):
    loader = WebBaseLoader(
        web_paths=(url,),
        bs_kwargs=dict()  # BeautifulSoup 기본 설정
    )
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

    return vectorstore.as_retriever()


# 문서 포맷팅
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# RAG 체인 동작
def rag_chain(url: str, question: str) -> str:
    retriever = load_and_retrieve_docs(url)
    retrieved_docs = retriever.invoke(question)

    context = format_docs(retrieved_docs)
    prompt = f"Question: {question}\n\nContext: {context}"

    response = ollama.chat(
        model='llama3',
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Check the url content and answer the question. Translate the answer in Korean with emoji."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response['message']['content']


# Gradio 인터페이스
iface = gr.Interface(
    fn=rag_chain,
    inputs=["text", "text"],
    outputs="text",
    title="🦙 LLaMA 3 - RAG 기반 질문 응답",
    description="웹페이지 URL과 질문을 입력하면, 해당 내용을 기반으로 LLaMA 3가 한국어 답변을 제공합니다. 🇰🇷✨"
)

if __name__ == "__main__":
    iface.launch()
