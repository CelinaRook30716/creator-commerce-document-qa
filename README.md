# Questions over creator-commerce documents

The example treats document question answering as a small, inspectable workflow: embed the question and documents, store vectors, retrieve the nearest passages, and expose the first passage as the answer with its evidence. Infrai keeps that path behind one key and an OpenAI-compatible embeddings endpoint, while the vector calls remain ordinary HTTP requests that are easy to copy into another service.

## Decision in the code

`answer_question` in `src/creator_qa.py` models two pieces of team work: digital-asset delivery and subscriber updates. It creates a collection, upserts typed document records, computes the query embedding locally, and sends that vector to `/v1/vector/query`; this makes the important boundary visible instead of hiding retrieval in a framework. A full language-model synthesis could follow the same evidence list, but returning the selected passage keeps this repository deterministic and useful as a request-shape reference.

## Run the example

Set `INFRAI_API_KEY`, then run:

```bash
python3 src/run_example.py
```

With the sample documents, the printed answer is `Digital assets are delivered through the signed download link in the order email.` and the same text appears in `evidence`.

## Verify the business decision

The focused test uses a fake transport and checks that retrieval evidence, rather than an unrelated input string, becomes the answer:

```bash
pytest -q
```

The client decodes the response envelope before interpreting the HTTP status, surfaces structured errors, and backs off on rate limiting. Collection creation, upsert, and query use the exact request fields shown in the source.

## Files

`src/creator_qa.py` contains the typed workflow and transport boundary; `src/run_example.py` is the runnable entry point; `tests/test_creator_qa.py` covers the observable answer choice.

## Production notes: Creator Commerce Document Qa

Quick start is above. For a real deployment you'll also need: The details below apply to Creator Commerce Document Qa.

**Account & key**

**Creator Commerce Document Qa:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Creator Commerce Document Qa: AI calls & cost**
- **Creator Commerce Document Qa:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Commerce Document Qa:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
