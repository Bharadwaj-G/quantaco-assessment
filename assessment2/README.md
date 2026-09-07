# Large JSON File Chunking

Splits a large, deeply-nested JSON file into smaller, independently-loadable chunks without ever loading the full file into memory.

## The problem

The source file is a single JSON array of Venues, each containing nested
`Stores → Transactions → (Payments, Items → Product)`. The real file provided is **~4GB**, with 40 venues, 240 stores, 877,560 transactions.

## Approach

Stream the top-level array one venue at a time with `ijson` (an incremental JSON
parser), and write each venue's complete subtree to its own chunk file. This keeps peak
memory bounded by the size of a single venue (~45MB - approx chunk size after split), never the whole file.

**Chunking granularity: one venue per chunk.**

**Serialization: `orjson`, not stdlib `json`.**

| Usage | Time (40 venues, ~4GB) |
|---|---|
| Write (`json.dump`, stdlib) | ~230-270s |
| Write (`orjson.dumps`) | ~50-80s |


## Output

- `chunks/chunk_{n}_venue{VenueID}.json` - one self-contained, valid JSON file per
  venue, loadable on its own with a plain `json.load()` (no `ijson`/`orjson` required
  downstream - those are only needed to handle the *original* full-size file).
- `stats.json` - a total stats file with total chunk count, per-venue `VenueID`/`VenueName`/
  `StoreCount`/`TransactionCount`/`ItemCount`, and total processing time. Lets a
  downstream consumer know what each chunk contains without opening it.

## Setup & running

```bash
python -m venv venv
venv/Scripts/activate   # Windows cmd
pip install -r requirements.txt

python json_to_chunks.py "your_path/to/Venue1-5_20240601 - 20240630.json"
```

Output lands in `chunks/` and
`stats.json` in the current directory.
