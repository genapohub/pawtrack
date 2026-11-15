"""进程内 Redis/Mongo 替身，仅供本地 Mock 与 TestClient 使用，不连真实服务。"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Optional


class MemoryRedis:
    def __init__(self):
        self._kv: dict[str, str] = {}
        self._geo: dict[str, dict[str, tuple[float, float]]] = defaultdict(dict)
        self._streams: dict[str, list] = defaultdict(list)

    async def ping(self):
        return True

    async def get(self, key: str):
        return self._kv.get(key)

    async def set(self, key: str, value: str):
        self._kv[key] = value
        return True

    async def xadd(self, name: str, fields: dict, maxlen: int = 0, approximate: bool = False):
        self._streams[name].append(dict(fields))
        if maxlen and len(self._streams[name]) > maxlen:
            self._streams[name] = self._streams[name][-maxlen:]
        return "0-1"

    async def geoadd(self, key: str, values):
        # values: (lng, lat, member)
        lng, lat, member = values
        self._geo[key][str(member)] = (float(lng), float(lat))
        return 1

    async def geopos(self, key: str, member: str):
        pos = self._geo.get(key, {}).get(str(member))
        if not pos:
            return [None]
        lng, lat = pos
        return [(lng, lat)]

    async def publish(self, channel: str, message: str):
        return 0

    async def georadius(self, *args, **kwargs):
        return []


class _FakeCursor:
    def __init__(self, items: list[dict]):
        self._items = items

    def sort(self, key, direction=1):
        reverse = direction == -1
        self._items = sorted(self._items, key=lambda x: x.get(key) or 0, reverse=reverse)
        return self

    def limit(self, n: int):
        self._items = self._items[:n]
        return self

    async def to_list(self, length: int = 500):
        return list(self._items[:length])


class MemoryLocations:
    def __init__(self):
        self._docs: list[dict] = []

    async def insert_one(self, doc: dict):
        self._docs.append(dict(doc))
        return None

    def _match(self, query: dict, doc: dict) -> bool:
        for k, v in query.items():
            if k == "ts" and isinstance(v, dict):
                ts = doc.get("ts") or 0
                if "$gte" in v and ts < v["$gte"]:
                    return False
                if "$lte" in v and ts > v["$lte"]:
                    return False
            elif doc.get(k) != v:
                return False
        return True

    async def count_documents(self, query: dict) -> int:
        return sum(1 for d in self._docs if self._match(query, d))

    def find(self, query: dict, projection: Optional[dict] = None):
        items = []
        for d in self._docs:
            if not self._match(query, d):
                continue
            if projection:
                keep = {k: d.get(k) for k, inc in projection.items() if inc and k != "_id"}
                items.append(keep)
            else:
                items.append({k: v for k, v in d.items() if k != "_id"})
        return _FakeCursor(items)
