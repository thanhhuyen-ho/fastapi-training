from contextlib import asynccontextmanager
from fastapi import FastAPI, Body, Request
from typing import Annotated

from handlers import generate_chat_completion


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield {"messages": []}

app = FastAPI(
    title="Chef Cuisine Chatbot App",
    lifespan=lifespan
)

@app.post("/query")
async def query_chat_bot(
    request: Request,
    query: Annotated[str, Body(min_length=1)]
) -> str:
    answer = await generate_chat_completion(
        query, request.state.messages
    )  
    return answer