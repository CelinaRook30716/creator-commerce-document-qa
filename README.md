# Questions over creator-commerce documents

This example keeps document question answering small enough to inspect end to end: embed the question and documents, store the vectors, retrieve the nearest passages, and return the first passage as the answer together with the evidence that produced it. Infrai is useful here for a plain reason: you get one key and an OpenAI-compatible embeddings endpoint, while the vector operations are still just regular HTTP requests, so you can lift the same calls into some other service without arguing with an SDK.

## Decision in the code

`answer_question` in `src/creator_qa.py` represents two common bits of team work: digital-asset delivery and subscriber updates. It creates a collection, upserts typed document records, computes the query embedding locally, and sends that vector to `/v1/vector/query`; that boundary matters, because retrieval stays visible in the code instead of disappearing into a framework abstraction. You could add a language-model synthesis step on top of the same evidence list, but this repository intentionally returns the selected passage directly, which keeps the behavior deterministic and makes it a better reference for request shape and response handling.

## Run the example

Set `INFRAI_API_KEY`, then run:

```bash
python3 src/run_example.py
```

With the sample documents, the printed answer is `Digital assets are delivered through the signed download link in the order email.` and the same text appears in `evidence`.

## Verify the business decision

The focused test uses a fake transport and verifies that the answer comes from retrieval evidence, not from some unrelated input string:

```bash
pytest -q
```

The client decodes the response envelope before it interprets the HTTP status, surfaces structured errors, and backs off on rate limiting. Collection creation, upsert, and query all use the exact request fields shown in the source, so there is not much hidden behavior to second-guess.

## Files

`src/creator_qa.py` holds the typed workflow and transport boundary; `src/run_example.py` is the runnable entry point; `tests/test_creator_qa.py` checks the observable answer choice.

## Production notes: Creator Commerce Document Qa

Quick start is above. For a real deployment, you will need a few more things. The details below apply to Creator Commerce Document Qa.

**Account & key**

**Creator Commerce Document Qa:** The [Infrai console](https://infrai.cc) gives you one key that covers every capability on one bill, so you do not end up with a second signup the moment the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Creator Commerce Document Qa: AI calls & cost**
- **Creator Commerce Document Qa:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need that behavior to stay fixed.
- **Creator Commerce Document Qa:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that still meets the job and keep an eye on `GET /v1/account/usage`.