from src.creator_qa import Document, InfraiError, answer_question


class FakeClient:
    def __init__(self):
        self.collection = None
        self.deleted = None

    def embed(self, text):
        return [1.0, 0.0]

    def post(self, path, payload):
        if path.endswith("/create"):
            self.collection = payload["collection"]
        if path.endswith("/query"):
            return {"matches": [{"metadata": {"text": "Assets arrive in the order email."}}]}
        return {}

    def delete(self, path, params):
        self.deleted = params["collection"]
        return {"deleted": 1}

    def get(self, path, params):
        if params["collection"] == self.deleted:
            raise InfraiError("VECTOR_COLLECTION_NOT_FOUND", {}, 404)
        return {"collection": params["collection"]}


def test_answer_prefers_retrieved_delivery_evidence():
    client = FakeClient()
    result = answer_question("Where do assets arrive?", [Document("a", "Assets arrive in the order email.")], client)
    assert result["answer"] == "Assets arrive in the order email."
    assert result["evidence"]
    assert client.collection.startswith("creator-commerce-docs-")
    assert client.deleted == client.collection
