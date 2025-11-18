class NeighborsGraph:
    def __init__(self):
        self._data = {}

    def _key(self, a, b):
        # Efficient canonical key: always sorted by numeric id
        return (a, b) if a <= b else (b, a)

    def __setitem__(self, pair, value):
        a, b = pair
        self._data[self._key(a, b)] = value

    def __getitem__(self, pair):
        a, b = pair
        return self._data[self._key(a, b)]

    def __contains__(self, pair):
        a, b = pair
        return self._key(a, b) in self._data

    def get(self, a, b, default=None):
        return self._data.get(self._key(a, b), default)

    def remove(self, a, b):
        del self._data[self._key(a, b)]

    def items(self):
        return self._data.items()

    def __repr__(self):
        return f"{self.__class__.__name__}({self._data})"

    def search(self, obj_or_id):
        """
        Returns all ((id1, id2), value) pairs where obj.id or id is present.
        Accepts either an object or an integer id.
        """
        target_id = obj_or_id.id if hasattr(obj_or_id, "id") else obj_or_id

        results = []
        for key, value in self._data.items():
            if target_id in key:    # key is a 2-tuple like (idA, idB)
                results.append((key, value))

        return results