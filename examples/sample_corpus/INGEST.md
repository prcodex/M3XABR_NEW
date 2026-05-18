# Ingesting the sample corpus

The 8 stub documents in `documents.json` aren't representative of
production data — they let you smoke-test the pipeline end-to-end.

## Minimal ingestion script

```python
import json
from datetime import datetime
from pathlib import Path

import lancedb
import pyarrow as pa
from m3xabr_core.backends.embeddings import VoyageEmbeddings

# Load the stub corpus
with open("examples/sample_corpus/documents.json") as f:
    docs = json.load(f)

# Embed each doc
embedder = VoyageEmbeddings()
for doc in docs:
    doc["content_vector"] = embedder.embed(doc["text"])
    doc["has_vector"] = 1.0
    doc["published_at"] = datetime.fromisoformat(doc["published_at"].replace("Z", "+00:00"))

# Create the LanceDB table
db = lancedb.connect("./lancedb_data")

schema = pa.schema([
    pa.field("id", pa.string()),
    pa.field("text", pa.string()),
    pa.field("source", pa.string()),
    pa.field("published_at", pa.timestamp("us", tz="UTC")),
    pa.field("domain", pa.string()),
    pa.field("content_vector", pa.list_(pa.float32(), 2048)),
    pa.field("has_vector", pa.float32()),
])

table = db.create_table("unified_feed", schema=schema, mode="overwrite")
table.add(docs)
print(f"Indexed {len(docs)} documents")
```

## Running

```bash
export VOYAGE_API_KEY=pa-...
python -c "exec(open('examples/sample_corpus/INGEST.md').read().split('```python')[1].split('```')[0])"
```

Or copy the script into `ingest.py` and run `python ingest.py`.

## After ingestion

```bash
export ANTHROPIC_API_KEY=sk-ant-...
m3xabr query "O Itaú revisou Selic?" --lancedb ./lancedb_data --debug
```
