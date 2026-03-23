import json


def rebuild_index(hash_table, filename="data.log"):
    with open(filename, "r", encoding="utf-8") as f:
        while True:
            position = f.tell()
            line = f.readline()

            if not line:
                break

            record = json.loads(line.strip())
            key = record["key"]

            hash_table.put(key, position)