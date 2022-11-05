# Why empty dicts are f***ing dangerous when modified (they're a shared reference!)

# solution 
# create new by using "meta if meta else {}"
# then even better use None instead of {} (which seems to be the convention anyways)

from typing import Dict

class DataType:

    def __init__(self, meta: Dict[str, str] = {}) -> None:
        self.meta: Dict[str, str] = meta #if meta else {}

    def getMeta(self, key: str) -> str:
        return self.meta[key] if key in self.meta else ""

    def setMeta(self, key: str, value: str) -> None:
        self.meta[key] = value

    def __str__(self) -> str:
        if not self.meta:
            return f"[T]"
        else:
            uc = ":".join(["%s=%s"%(k, v) for k, v in self.meta.items()])
            return f"[T:{uc}]"


dtype = DataType()
dtype.setMeta("model", "TotalSegmentator")
dtype.setMeta("modality", "seg")
dtype.setMeta("roi", "heart")

dtype2 = DataType()
dtype2.setMeta("model", "TotalSegmentator")
dtype2.setMeta("modality", "seg")
dtype2.setMeta("roi", "lung")

print(dtype)
print(dtype2)