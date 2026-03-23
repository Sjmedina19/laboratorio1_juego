from persistence.hash_entry import HashEntry


class HashTable:
    def __init__(self, initial_capacity=8, load_factor_threshold=0.7):
        self.capacity = initial_capacity
        self.size = 0
        self.load_factor_threshold = load_factor_threshold
        self.collision_count = 0

        self.buckets = []
        for _ in range(self.capacity):
            self.buckets.append([])

    def _hash(self, key):
        hash_value = 0
        prime = 31

        for char in key:
            hash_value = hash_value * prime + ord(char)

        return hash_value % self.capacity

    def load_factor(self):
        return self.size / self.capacity

    def put(self, key, value_reference):
        index = self._hash(key)
        bucket = self.buckets[index]

        for entry in bucket:
            if entry.key == key:
                entry.value_reference = value_reference
                return

        if len(bucket) > 0:
            self.collision_count += 1

        bucket.append(HashEntry(key, value_reference))
        self.size += 1

        if self.load_factor() > self.load_factor_threshold:
            self._rehash()

    def get(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]

        for entry in bucket:
            if entry.key == key:
                return entry.value_reference

        return None

    def delete(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]

        for i in range(len(bucket)):
            if bucket[i].key == key:
                del bucket[i]
                self.size -= 1
                return True

        return False

    def _rehash(self):
        old_buckets = self.buckets
        old_capacity = self.capacity

        self.capacity = self.capacity * 2
        self.size = 0
        self.collision_count = 0

        self.buckets = []
        for _ in range(self.capacity):
            self.buckets.append([])

        for bucket in old_buckets:
            for entry in bucket:
                self.put(entry.key, entry.value_reference)

        print(f"Rehash ejecutado: capacidad {old_capacity} -> {self.capacity}")

    def print_table(self):
        print("\n=== TABLA HASH ===")
        for i in range(self.capacity):
            print(f"Bucket {i}: {self.buckets[i]}")
        print(f"Elementos: {self.size}")
        print(f"Capacidad: {self.capacity}")
        print(f"Factor de carga: {self.load_factor():.2f}")
        print(f"Colisiones: {self.collision_count}")
        print("==================\n")