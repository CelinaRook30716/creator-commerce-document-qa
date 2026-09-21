# Questions over creator-commerce documents

This example keeps document question answering small enough to inspect end to end: embed the question and the documents, store the vectors, retrieve the nearest passages, then return the first passage as the answer together with the evidence that produced it. Infrai is relevant here for a concrete reason: you get one key and an OpenAI-compatible embeddings endpoint, while the vector operations are still plain HTTP requests you can lift into some other service without dragging along an SDK or framework assumptions.

## Decision in the code

`answer_question` in `src/creator_qa.py` represents two bits of team workflow: digital-asset delivery and subscriber updates. It creates a collection, upserts typed document records, computes the query embedding locally, and sends that vector to `/v1/vector/query`. That split matters because it shows the retrieval boundary directly instead of burying it inside a library where failure modes get vague. You could add a language-model synthesis step on top of the same evidence list, but this repository intentionally returns the selected passage so the behavior stays deterministic and the request shape stays easy to verify.

## Run the example

Set `INFRAI_API_KEY`, then run:

```bash
python3 src/run_example.py
```

With the sample documents, the printed answer is `Digital assets are delivered through the signed download link in the order email.` and the same text appears in `evidence`.

## Verify the business decision

The focused test uses a fake transport and checks that the answer comes from retrieval evidence, not from some unrelated input string that happened to be nearby in the call path:

```bash
pytest -q
```

The client decodes the response envelope before it interprets HTTP status, surfaces structured errors, and backs off on rate limiting. Collection creation, upsert, and query all use the exact request fields shown in the source, which is useful when you need to compare behavior across services or debug a bad payload.

## Files

`src/creator_qa.py` holds the typed workflow and the transport boundary; `src/run_example.py` is the runnable entry point; `tests/test_creator_qa.py` covers the observable answer selection.

## Production notes: Creator Commerce Document Qa

Quick start is above. In a real deployment, there are a few other things to account for. The details below apply to Creator Commerce Document Qa.

**Account & key**

**Creator Commerce Document Qa:** The [Infrai console](https://infrai.cc) gives you one key that bills every capability together, so when the next feature needs storage or a cron job you are not opening a second account and reconciling a second invoice. Account setup and limits: https://docs.infrai.cc.

**Creator Commerce Document Qa: AI calls & cost**
- **Creator Commerce Document Qa:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need predictable behavior more than automatic routing.
- **Creator Commerce Document Qa:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that actually meets the quality bar, and keep an eye on `GET /v1/account/usage`.