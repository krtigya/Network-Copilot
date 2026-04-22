import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Modern LangChain Imports (Bypasses the 'chains' module error)
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

app = FastAPI(title="Network Copilot API")

# Load embeddings and vector store once when the app starts
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.load_local(
    "faiss_index", 
    embeddings, 
    allow_dangerous_deserialization=True
)

# Request Model (Pydantic v2)
class QueryRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat_with_copilot(request: QueryRequest):
    try:
        llm = ChatGroq(temperature=0, model_name="llama3-8b-8192")
        
        # Define the prompt
        prompt = ChatPromptTemplate.from_template("""
        You are an ISP Support Engineer. Use the context to answer.
        Context: {context}
        Question: {question}
        """)

        # Modern LCEL Chain (Highly recommended for hiring projects)
        retriever = vectorstore.as_retriever()
        
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        response = chain.invoke(request.question)
        return {"answer": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)