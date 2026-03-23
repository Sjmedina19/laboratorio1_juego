class HashEntry:
    def __init__(self, key, value_reference):
        self.key = key
        self.value_reference = value_reference

    def __repr__(self):
        return f"HashEntry(key={self.key}, value_reference={self.value_reference})"