from creator_qa import InfraiClient
from creator_qa import Document, answer_question


if __name__ == "__main__":
    docs = [
        Document("delivery", "Digital assets are delivered through the signed download link in the order email.", "digital delivery"),
        Document("updates", "Subscribers receive a weekly update every Friday with the newest release notes.", "subscriber update"),
    ]
    print(answer_question("How are digital assets delivered?", docs, InfraiClient()))
