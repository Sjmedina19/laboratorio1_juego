from persistence.hash_table import HashTable
from storage.record_store import RecordStore
from storage.recovery import rebuild_index


class ProfileRepository:
    def __init__(self):
        self.hash_table = HashTable()
        self.store = RecordStore()
        rebuild_index(self.hash_table)

    def save(self, key, data):
        offset = self.store.append_record("profile", key, data)
        self.hash_table.put(key, offset)

    def get(self, key):
        offset = self.hash_table.get(key)

        if offset is None:
            return None

        record = self.store.read_record_at(offset)

        if record is None:
            return None

        return record["data"]