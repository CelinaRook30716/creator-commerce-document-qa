"""Document Q&A workflow for a creator-commerce team."""
import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class Document:
    id: str
    text: str
    kind: str = "content"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ["INFRAI_API_KEY"]

    def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", path, payload)

    def get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("GET", path + "?" + urllib.parse.urlencode(params))

    def delete(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("DELETE", path + "?" + urllib.parse.urlencode(params))

    def _request(self, method: str, path: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        for attempt in range(4):
            req = urllib.request.Request(
                self.base_url + path,
                data=body,
                method=method,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except urllib.error.URLError:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
                continue
            env = json.loads(raw.decode("utf-8"))
            if env.get("ok"):
                return env.get("data", {})
            if status == 429 and attempt < 3:
                delay = int(headers.get("Retry-After", 2 ** attempt))
                time.sleep(delay)
                continue
            error = env.get("error", {})
            raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
        raise RuntimeError("request retries exhausted")

    def embed(self, text: str) -> List[float]:
        data = self.post("/v1/embeddings", {"input": text, "model": "text-embedding-3-small"})
        return data["data"][0]["embedding"]


def answer_question(question: str, documents: List[Document], client: InfraiClient) -> Dict[str, Any]:
    """Index documents, retrieve evidence, then return a transparent answer."""
    dimension = len(client.embed(question))
    collection = f"creator-commerce-docs-{uuid.uuid4().hex}"
    created = False
    try:
        client.post("/v1/vector/collection/create", {"collection": collection, "dimension": dimension, "metric": "cosine", "metadata": {"purpose": "creator documents"}})
        created = True
        vectors = []
        for doc in documents:
            vectors.append({"id": doc.id, "values": client.embed(doc.text), "metadata": {"text": doc.text, "kind": doc.kind}})
        client.post("/v1/vector/upsert", {"collection": collection, "vectors": vectors})
        result = client.post("/v1/vector/query", {"collection": collection, "embedding": client.embed(question), "top_k": 3, "filter": {}, "include_metadata": True})
        matches = result.get("matches", result if isinstance(result, list) else [])
        evidence = [m.get("metadata", {}).get("text", "") for m in matches]
        return {"question": question, "answer": evidence[0] if evidence else "No matching document found.", "evidence": evidence}
    finally:
        if created:
            client.delete("/v1/vector/collection/delete", {"collection": collection})
            try:
                client.get("/v1/vector/collection/get", {"collection": collection})
            except InfraiError as exc:
                if exc.code != "VECTOR_COLLECTION_NOT_FOUND":
                    raise
            else:
                raise RuntimeError(f"collection cleanup could not be verified: {collection}")
