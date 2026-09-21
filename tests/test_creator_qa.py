from src.creator_qa import Document, answer_question


class FakeClient:
    def embed(self, text):
        return [1.0, 0.0]

    def post(self, path, payload):
        if path.endswith("/query"):
            return {"matches": [{"metadata": {"text": "Assets arrive in the order email."}}]}
        return {}


def test_answer_prefers_retrieved_delivery_evidence():
    result = answer_question("Where do assets arrive?", [Document("a", "Assets arrive in the order email.")], FakeClient())
    assert result["answer"] == "Assets arrive in the order email."
    assert result["evidence"]
