# Context Engineering and RAG — GP-25 to GP-28

All from Aaron's Agentic RAG lecture (video 2).

---

## GP-25 — Fewer, better tokens

**Statement.** Context engineering means giving the model the right context at the right time. A huge context window is not a reason to fill it: extra tokens dilute the ones that matter, besides costing money. The always-on system prompt is prime real estate.

**Source.** V2 [6:56–8:00]: *"context engineering is all about giving it the right context at the right time. And models these days have fantastically huge context windows… so you might be tempted to… give it everything. You can't. Kitchen-sinking it, even if it all fits… still tends to dilute the actual importance. It's better to give it fewer, better tokens than every token you can possibly think of."* V2 [27:44–28:16]: *"sure you can shove two million tokens in your model. Don't, outside of very special situations… RAG is a way to filter noise out of your system."* V2 [24:48–26:00], on prompt vs RAG: always-present system-prompt tokens are *"prime real estate… tokens that you're always paying for"*; a few hundred to low thousands is fine in a prompt; *"a 20-page document, that is a lot to put in a system prompt… I would probably look at RAG strategies."*

**In practice.** The co-pilot fetches the chart sections the question needs, not the whole chart. The system prompt holds role, rules and output contract — not reference material.

---

## GP-26 — Language models solve language; search solves retrieval

**Statement.** RAG fuses two different technologies. The model isn't a search engine; information retrieval is its own discipline, and the retrieval half deserves its own design and evaluation.

**Source.** V2 [9:04–10:24]: *"a regular user… just feel like AI is search 2.0… But it is critically important that we understand that that is not what a language model is… Language models solve language… What solves information retrieval… is search algorithms, and search algorithms have been around longer than large language models… RAG is sort of like fusing the two."*

**In practice.** Evaluate retrieval (did we fetch the right guideline passages?) separately from generation (did the answer use them correctly?).

---

## GP-27 — Climb the RAG ladder, and let evals decide the rung

**Statement.** Naive RAG → metadata-filtered → hybrid (keyword + vector) → multi-hop / query decomposition and rewriting → graph RAG → agentic RAG. Higher rungs are more flexible and more costly, slower and less deterministic. Metadata filtering is a common sweet spot; agentic RAG is the flagship for serious systems.

**Source.** V2 [14:24–15:12]: naive RAG has *"no retry, there's no routing, there's no check on the quality."* V2 [16:00–18:24]: metadata filtering *"lets you take your overall corpus of documents and focus your search"*; hybrid combines vector search *"with more traditional search like keyword matching… BM25"*; multi-hop because *"a single sentence can imply two or three or more implicit actual questions"*; *"you can rewrite the user's query"*; graph RAG maps *"relationships between entities"* (*"I'm not sure how widely used it is"*); agentic RAG exposes these as tools and *"the first step… is essentially solving a classification problem, routing the user's query."* V2 [22:00–23:28], asked why not always agentic: *"it is inevitably going to add a little bit of cost and latency… it adds complexity and overhead to your development… makes your system a little bit less deterministic… I would say metadata-filtered is a common sweet spot."* V2 [54:44–55:00], hybrid fusion: *"run both searches and then you fuse the results together… if something happened towards the front of both results… it's even more relevant."* V2 [55:16–55:32]: *"whether or not that's going to be better than the other approaches honestly depends a little bit on your problem. That's why you have evals."*

**In practice.** Week 2 names hybrid RAG. Start metadata-filtered (guideline source, topic, recency), add BM25 + dense fusion, and move to agentic retrieval only if eval cases on compound questions justify it.

---

## GP-28 — Retrieval defaults worth knowing

**Statement.** Sensible starting points: chunks of roughly 500 tokens; recursive character splitting as the baseline chunker (semantic chunking is better but expensive); cosine similarity; a top-k parameter rather than a similarity threshold for the search itself; one embedding model used consistently; and config names that exactly match what the store created.

**Source.** V2 [26:00–26:24]: *"you chop it up into pieces of say about 500 tokens each… and then each of those pieces is what you actually calculate the embedding on."* V2 [57:16–58:12]: fixed-length splitting cuts *"in the middle of words, in the middle of sentences"*; recursive character splitting *"uses a little recursion trick and a list of special things to look for, punctuation and spacing… usually a good one to pick"*; semantic chunking *"is one of the most expensive ways to chunk, but it can be worth it."* V2 [20:31–21:28]: cosine similarity *"calculates the angle."* V2 [27:04–27:28]: *"return the five documents with the most similar… the parameter you have control over is top-n documents."* V2 [43:00–43:16]: dimensions *"have to match the embedding model… If we switch embedding models… you'd have to re-embed everything… all the big ones are pretty good these days… just select a decent one and stick with it."* V2 [49:24–50:08], live demo bug: the index was named `vector_index` in the store but differently in code — *"these are the sorts of details you got to pay attention to."*

**In practice.** Record the embedding model, dimensions, chunker and chunk size as configuration in one place. A readiness check verifies the index name exists.
