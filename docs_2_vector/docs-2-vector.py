import os
import glob
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from openai import OpenAI
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="api_key",
    api_version="api_version",
    azure_endpoint="azure_endpoint"
)

# 1. 连接 Milvus
connections.connect("default", host="localhost", port="19530")

# 2. 定义 Collection Schema
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=2000),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=3072),
]
schema = CollectionSchema(fields, description="Markdown docs collection")

if utility.has_collection("docs_collection"):
    utility.drop_collection("docs_collection")

collection = Collection(name="docs_collection", schema=schema)

# 3. 读取 Markdown 文件
def load_markdown_files(folder):
    files = glob.glob(os.path.join(folder, "**", "*.md"), recursive=True)
    docs = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            docs.append(fp.read())
    return docs

# 4. 切分文档（简单按段落）
def split_into_chunks(text, max_len=500):
    chunks, current = [], []
    for line in text.split("\n"):
        if len(" ".join(current)) + len(line) < max_len:
            current.append(line)
        else:
            chunks.append(" ".join(current))
            current = [line]
    if current:
        chunks.append(" ".join(current))
    return chunks

# 5. 生成向量
def embed_texts(texts):
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=texts
    )
    return [d.embedding for d in response.data]

# 6. 插入 Milvus
docs = load_markdown_files("./")
all_chunks = []
for doc in docs:
    all_chunks.extend(split_into_chunks(doc))

embeddings = embed_texts(all_chunks)
collection.insert([all_chunks, embeddings])
collection.flush()

print("✅ Markdown 文档已导入 Milvus")

