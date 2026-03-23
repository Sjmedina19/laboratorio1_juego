import json
import os


class RecordStore:
    def __init__(self, filename="data.log"):
        self.filename = filename

        if not os.path.exists(self.filename):
            with open(self.filename, "w", encoding="utf-8") as f:
                pass

    def append_record(self, record_type, key, data):
        record = {
            "type": record_type,
            "key": key,
            "data": data
        }

        with open(self.filename, "a", encoding="utf-8") as f:
            offset = f.tell()
            json_line = json.dumps(record, ensure_ascii=False)
            f.write(json_line + "\n")

        return offset

    def read_record_at(self, offset):
        with open(self.filename, "r", encoding="utf-8") as f:
            f.seek(offset)
            line = f.readline().strip()

            if not line:
                return None

            return json.loads(line)