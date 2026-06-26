import os
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from ai.embeddings import get_embedding
from ai.vector_store import vector_store
from ai.llm import gpt_4o

app = FastAPI()

async def stream_answer(query: str, session_id: str, user_id: str):
    # Read API keys lazily
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")

    # Step 1: Embed query
    query_embedding = get_embedding(query, model="text-embedding-3-small")

    # Step 2: Retrieve top-5 chunks from vector store
    top_chunks = vector_store.search(query_embedding, top_k=5)

    # Step 3: Build prompt with retrieved context
    context = "\n\n".join([chunk["text"] for chunk in top_chunks])
    prompt = f"Answer the following question based on the context provided:\n\nContext:\n{context}\n\nQuestion:\n{query}"

    # Step 4: Call gpt-4o with stream=True
    async for token in gpt_4o(prompt, api_key=openai_api_key, stream=True):
        yield f'data: {{"token": "{token}"}}\n'

    # Step 5: After final token, yield citations
    citations = [chunk["source"] for chunk in top_chunks]
    yield f'data: {{"done": true, "citations": {citations}}}\n'

@app.get("/stream")
async def stream(query: str = Query(...), session_id: str = Query(...), user_id: str = Query(...)):
    return StreamingResponse(stream_answer(query, session_id, user_id), media_type="text/event-stream")