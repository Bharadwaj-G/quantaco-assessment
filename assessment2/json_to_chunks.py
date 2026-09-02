import sys
import time
import ijson
import json
import orjson
from pathlib import Path


def get_chunk_stats(venue):
    """Return (store_count, transaction_count, item_count) for one venue."""
    store_count = len(venue["Stores"])
    transaction_count = 0
    item_count = 0
    for store in venue["Stores"]:
        transaction_count += len(store["Transactions"])
        for transaction in store["Transactions"]:
            item_count += len(transaction["Items"])
    return store_count, transaction_count, item_count


def write_chunk(venue, chunk_path):
    """Serialize one venue to its own JSON file via orjson."""
    with open(chunk_path, "wb") as chunk_file:
        chunk_file.write(orjson.dumps(venue))


def json_to_chunks(json_file):
    """
    Streams the source JSON array one venue at a time (via ijson) and writes
    each venue to its own chunk file, without ever holding the whole file in
    memory. Returns (chunk_count, stats, total_time).
    """
    dir_path = Path("chunks")
    dir_path.mkdir(exist_ok=True)

    stats = []
    chunk_count = 1
    start_time = time.time()

    with open(json_file, "rb") as input_file:
        for item in ijson.items(input_file, "item", use_float=True):
            print(f"Processing item: {item['VenueID']}")

            chunk_path = f"chunks/chunk_{chunk_count}_venue{item['VenueID']}.json"
            write_chunk(item, chunk_path)

            store_count, transaction_count, item_count = get_chunk_stats(item)
            stats.append(
                {
                    "VenueID": item["VenueID"],
                    "VenueName": item["VenueName"],
                    "StoreCount": store_count,
                    "TransactionCount": transaction_count,
                    "ItemCount": item_count,
                }
            )

            chunk_count += 1

    total_time = time.time() - start_time
    print(f"Total time taken: {total_time} seconds")
    return chunk_count, stats, total_time


def main():
    json_file = sys.argv[1]
    chunk_count, stats, total_time = json_to_chunks(json_file)

    final_stats = {
        "total_chunks": chunk_count - 1,
        "stats": stats,
        "processing_time": total_time,
    }

    with open("stats.json", "w") as stats_file:
        json.dump(final_stats, stats_file, indent=2)


if __name__ == "__main__":
    main()
