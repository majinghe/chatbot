from fastapi import FastAPI
from pydantic import BaseModel
from pymilvus import connections, Collection
from openai import OpenAI
from openai import AzureOpenAI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],   
    allow_headers=["*"],   
)
# 连接 Milvus
connections.connect("default", host="localhost", port="19530")
collection = Collection("docs_collection")

index_params = {
    "metric_type": "COSINE",  # 或 "L2"
    "index_type": "IVF_FLAT",  # Milvus 支持多种索引类型
    "params": {"nlist": 128}
}

collection.create_index(
    field_name="embedding",
    index_params=index_params
)

collection.load()

client = AzureOpenAI(
    api_key="api_key",
    api_version="api_version",
    azure_endpoint="azure_endpoint"
)

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
def chat(req: ChatRequest):
    query = req.query

    query_embedding = client.embeddings.create(
      model="text-embedding-3-large",
      input=[query]
      ).data[0].embedding

    query_embedding = [float(x) for x in query_embedding]

    # 2. 从 Milvus 检索相似文档
    search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=3,
        output_fields=["content"]
    )

    docs = [hit.entity.get("content") for hit in results[0]]

    # 3. 拼接 RAG Prompt
    prompt = f"你是一个RustFS 专家，请基于以下文档回答：\n\n{docs}\n\n用户问题：{query}"

    # 4. 调用 LLM
    response = client.chat.completions.create(
        model="gpt-5-chat",  
        messages=[{"role": "user", "content": prompt}],
        # max_tokens=16384,
        # temperature=1.0,
        # top_p=1.0,
    )

    answer = response.choices[0].message.content

    return {"answer": answer, "sources": docs}
