from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langserve import add_routes
import uvicorn
import os
from langchain_community.llms import Ollama
from dotenv import load_dotenv

load_dotenv()

AZURE_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

app = FastAPI(
    title="Langchain Server",
    version="1.0",
    description="A simple API Server"
)

# 👇 Define stable schema for inputs
class PromptRequest(BaseModel):
    topic: str

model = AzureChatOpenAI(
    deployment_name=AZURE_DEPLOYMENT,
    openai_api_key=AZURE_KEY,
    azure_endpoint=AZURE_ENDPOINT,
    openai_api_version="2025-01-01-preview"
)

llm = Ollama(model="gemma")

prompt1 = ChatPromptTemplate.from_template(
    "Write me an essay about {topic} with 100 words"
)

prompt2 = ChatPromptTemplate.from_template(
    "Write me a poem about {topic} with 100 words"
)

# 👇 Explicit schemas (avoids broken dynamic model)
add_routes(
    app,
    model.with_types(input_type=PromptRequest),
    path="/openai"
)

add_routes(
    app,
    (prompt1 | model).with_types(input_type=PromptRequest),
    path="/essay"
)

add_routes(
    app,
    (prompt2 | llm).with_types(input_type=PromptRequest),
    path="/poem"
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
