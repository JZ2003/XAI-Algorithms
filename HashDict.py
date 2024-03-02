class HashDict:
    def __init__(self, *args, **kwargs):
        self._data = dict()
        for key, value in dict(*args, **kwargs).items():
            self._setitem(key, value, initializing=True)
        self._hash = None

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._setitem(key, value, initializing=False)


    def _setitem(self, key, value, initializing=False):
        if not initializing:
            self._check_mutability()
        if isinstance(value, set):
            value = frozenset(value)  # Enforce immutability of set values
        self._data[key] = value
        if not initializing:
            self._invalidate_hash()

    def __delitem__(self, key):
        self._check_mutability()
        del self._data[key]
        self._invalidate_hash()

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def _invalidate_hash(self):
        self._hash = None

    def _check_mutability(self):
        if self._hash is not None:
            raise TypeError("Cannot mutate a hashed HashableDict")

    def __hash__(self):
        if self._hash is None:
            # Use frozenset to ensure hashability of values
            self._hash = hash(frozenset((k, v) for k, v in self._data.items()))
        return self._hash

    def __eq__(self, other):
        if isinstance(other, HashDict):
            return self._data == other._data
        return False

    def __repr__(self):
        dicStr = []
        for key,val in self._data.items():
            if isinstance(val,frozenset):
                valStr = f"({','.join(map(str, sorted(val)))})"
            else:
                valStr = str(val)
            dicStr.append(str(key)+valStr)
        dicStr = ', '.join(dicStr)
        return f"HD:({dicStr})"



    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()
    

class Term(HashDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        dicStr = []
        if len((self._data)) == 0:
            return "True"
        for key,val in self._data.items():
            if isinstance(val,frozenset):
                valStr = f"({','.join(map(str, sorted(val)))})"
            else:
                valStr = str(val)
            dicStr.append(str(key)+valStr)
        dicStr = '*'.join(dicStr)
        return dicStr
    
    def latex_view(self) -> str:
        if len((self._data)) == 0:
            return "\\text{True}"
        res = ""
        for key,val in self._data.items():
            if isinstance(val,frozenset):
                val = [s if len(s) == 1 else "[" + s + "]" for s in map(str, sorted(val)) ]
                stateStr = ''.join(val)
                res += f"{key}_" + f"{{" + f"{stateStr}" + f"}}"
            else:
                raise ValueError("No Latex View!")
        return res

class Clause(HashDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __repr__(self):
        dicStr = []
        if len((self._data)) == 0:
            return "False"
        for key,val in self._data.items():
            if isinstance(val,frozenset):
                valStr = f"({','.join(map(str, sorted(val)))})"
            else:
                valStr = str(val)
            dicStr.append(str(key)+valStr)
        dicStr = '+'.join(dicStr)
        return dicStr

    def latex_view(self) -> str:
        if len((self._data)) == 0:
            return "\\text{False}"
        res = ""
        for i,(key,val) in enumerate(self._data.items()):
            if isinstance(val,frozenset):
                val = [s if len(s) == 1 else "[" + s + "]" for s in map(str, sorted(val)) ]
                stateStr = ''.join(val)
                res += f"{key}_" + f"{{" + f"{stateStr}" + f"}}" if i == 0 else f"+{key}_" + f"{{" + f"{stateStr}" + f"}}"
            else:
                raise ValueError("No Latex View!")
        return res