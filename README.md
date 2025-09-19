# DIY Chatbot

This is a learning by troubleshooting project. If you can run well on your machine, then you will learn lot about AIGC, such vector database, embedding, docker compose, fastapi, etc.

## Installation milvus and rustfs

Running the command to install milvus and rustfs,

```
docker compose -f docker-compose.yml up -d
```

You will see the available containers,

```
CONTAINER ID   IMAGE                                             COMMAND                  CREATED       STATUS                   PORTS                                                                                      NAMES
fc10dd1dc0e5   milvusdb/milvus:v2.6.0                            "/tini -- milvus run…"   2 hours ago   Up 2 hours (healthy)     0.0.0.0:9091->9091/tcp, :::9091->9091/tcp, 0.0.0.0:19530->19530/tcp, :::19530->19530/tcp   milvus-standalone
40ddc8ed08bb   zilliz/attu:v2.6                                  "docker-entrypoint.s…"   8 hours ago   Up 8 hours               0.0.0.0:8000->3000/tcp, :::8000->3000/tcp                                                  milvus-attu
3d2c8d80a8ce   quay.io/coreos/etcd:v3.5.18                       "etcd -advertise-cli…"   8 hours ago   Up 8 hours (healthy)     2379-2380/tcp                                                                              milvus-etcd
d760f6690ea7   rustfs/rustfs:1.0.0-alpha.58                      "/entrypoint.sh rust…"   8 hours ago   Up 8 hours (unhealthy)   0.0.0.0:9000-9001->9000-9001/tcp, :::9000-9001->9000-9001/tcp                              milvus-rustfs
```

milvus instance will be available on `19530` port, rustfs will be available on `9000` port and attu will be available on `8000` port.

## Embedding docs

Milvus is a vector database, means, it can not store the docs(such markdown file, png images). So, text or images should first be converted into vector representations via an embedding model before being stored in a vector database.

Running the python script `docs-2-vector.py` to finish this job.

```
python3 docs-2-vector.py
```

After the script runs successfully, your docs are inserted into milvus database. Then you can use the data to build a RAG.

## Build RAG

The script `fastapi/main.py` use milvus and llm to build a RAG, and you can use this RAG via api if you run the command,

```
uvicorn main:app --reload --host 0.0.0.0 --port 9999
```

The RAG will be available on `ip:9999/chat`.

## Build Chatbot

The script `web/page.tsx` use the next.js to build a web page, you can input your question and get the answer, namely a very very very simple chatbot console. You can create a next.js project and copy the `web/page.tsx` into the right directory, and then run,

```
pnpm run dev -H 0.0.0.0 -p 3000
```

Finally, your DIY chatbot will be available `ip:3000/chat`, open it in the broswer and enjoy it.

Maybe you will encounter some problems, that ok, that is the right way to learn milvus, rustfs, fastapi, next.js.
