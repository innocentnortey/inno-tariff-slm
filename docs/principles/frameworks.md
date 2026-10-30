# Frameworks and Tools in the Pre-Work Lectures

What the three lectures recommend, what they merely demo, and how firmly. "Recommended" means a lecturer said to use it; "Demoed" means it appeared in teaching code without a recommendation.

---

## Agent frameworks and SDKs

| Tool | Status | What was said | Source |
|---|---|---|---|
| **LangChain** | **Recommended starting point** | *"LangChain is what we often have in the teaching material and it's a good place to get started. I think in a lot of situations it's a little low level compared to some of the other tools… but it's got a good ecosystem and integration with LangSmith for observability."* Also: *"for engineering purposes, it's often a good idea to use a framework"* and *"if you're doing this for real, you might want to use LangChain. And you'll see LangChain plenty in future lectures."* | Aaron V2 [32:16–32:40]; V1 [21:28–21:36], [39:40–39:48] |
| **LangGraph** | **Recommended for multi-agent** | *"LangGraph has some multi-agent tutorials. If you are thinking multi-agent, I would definitely nudge towards LangGraph because you're probably going to want the flexibility that LangGraph gives you."* | Aaron V2 [39:48–39:56] |
| **LangChain.js** (`@langchain/core` `tool()`, `bindTools`, `invoke`) | Demoed | Rewrote a raw OpenAI SDK tool call; LangChain *"handles a lot of the plumbing"* — tool wrapper with schema, auto-parsed arguments. *"Since AI is writing most code these days… it really doesn't matter which one you're using either way."* | Jacob V3 [46:04–48:12], [50:12–50:28], [53:08–53:40] |
| **Raw OpenAI SDK** | Demoed as the teaching baseline | Built the tool loop by hand first *"so we can actually see the scaffolding."* | Jacob V3 [13:56–14:12], [32:04] |
| **Plain Python (standard library)** | Demoed as the teaching baseline | *"mostly depending on standard library… intentional… to actually teach the topics as opposed to just using a framework that solves everything."* | Aaron V1 [39:32–39:48] |
| **Claude / Cursor harness SDKs** | Mentioned with caveats | *"you can use their SDK and you can build on top of their harness for certain tasks. They have more stuff locked in. They're a little bit less customizable… if the problem you're solving is a good fit for a preconfigured tool like that, then that might help you move faster."* | Aaron V2 [32:40–33:12] |
| **AutoGen** | Named only | *"Everything else — LangChain, LangGraph, AutoGen, all of it — it's scaffolding around that loop."* | Jacob V3 [14:04] |
| **MCP servers** | Mentioned | Pre-built tools that connect a model to systems such as Confluence and GitHub; used at the instructor's employer to gather context. | Jacob V3 [7:04–7:44], [9:28–9:44] |

⚠️ **One misstatement to ignore.** Jacob said *"LangGraph is for observability"* at V3 [46:12] and immediately corrected himself to LangChain. LangGraph is an orchestration framework; LangSmith is the observability product.

## Observability

| Tool | Status | What was said | Source |
|---|---|---|---|
| **LangSmith** | **Recommended, demoed live** | Instrumented the RAG demo and showed the trace with retrieved documents; the setup instructions say *"you should definitely put a LangChain key for tracing."* Suggested for debugging tool failures in production. | Aaron V2 [40:44–40:52], [53:08–53:48]; Jacob V3 [43:32–44:12] |
| **Langfuse** | **Recommended alongside LangSmith** | *"there's ones specialized for LLMs — LangSmith and Langfuse — that… are LLM-aware, so they know about your tokens and your model and your token spend."* | Aaron V1 [36:56–37:04] |

## Retrieval stack

| Tool | Status | Notes | Source |
|---|---|---|---|
| **MongoDB Atlas Vector Search** | Demoed | The RAG cookbook repo's vector store (cosine similarity, bring-your-own embeddings). | Aaron V2 [40:36–45:48] |
| **pgvector** | Mentioned | *"pgvector adds a vector store capability to Postgres."* | Aaron V2 [20:23–20:31] |
| **Neo4j** | Demoed (graph RAG level) | Brought up with Docker Compose. | Aaron V2 [55:00–55:08] |
| **BM25** | Demoed (hybrid level) | Keyword matching fused with vector results. | Aaron V2 [16:48–17:04], [54:36–55:00] |
| **OpenAI `text-embedding-3-small`** | Demoed | 1,536 dimensions. | Aaron V2 [47:00–47:16] |
| **LangChain `PyPDFLoader`** | Demoed | *"saves us probably hundreds of lines of painful code."* | Aaron V2 [46:36–47:00] |
| **LangChain `RecursiveCharacterTextSplitter`** | Recommended baseline chunker | *"usually a good one to pick."* | Aaron V2 [42:04–42:20], [57:32–58:00] |
| **ReAct paper; Anthropic tool-use docs; LangGraph multi-agent tutorials** | Recommended reading | *"Anthropic has excellent tool-use docs."* | Aaron V2 [39:31–39:56] |

## Supporting tools

| Tool | Status | Notes | Source |
|---|---|---|---|
| **Zod** | Demoed | Tool input schemas in LangChain.js. | Jacob V3 [47:24–47:32] |
| **Postgres in Docker Compose** | Demoed | Local database behind the tool-calling demo. | Jacob V3 [58:04–58:28] |
| **Faker (Python)** | Recommended for synthetic data | Random draws that seed LLM-written records. | Aaron V1 [57:04–57:12] |
| **Google Colab** | Demoed | Lecture notebooks — *"not production code."* | Aaron V1 [37:44–38:16] |
| **Vercel / Render** | Suggested | Where to deploy the take-home tool-calling web app. | Jacob V3 [1:04:08] |

---

## Added 2026-09-23 — from the live cohort lectures (E1–E3, O1, L1, G1, G2)

The tools that matter for Week 2. Full per-lecture tables, with every tool named and its timestamp, are in `lecture-notes/`.

### Graphs (LangGraph)

| Construct | What it is for | Source |
|---|---|---|
| `StateGraph` + typed state | *"what you will see more often"*. The state is the graph's spec (GP-73). `MessageGraph` and `set_entry_point` in the G1 demo are the older API. | G1 [42:12–43:56] |
| `add_conditional_edges` + a router function | Branching lives in the edge, not in a node (GP-74). | G1 [46:04–47:16] |
| Prebuilt `ToolNode` | Tool execution isolated in one node, the natural guard point (GP-81). | G1 [45:56–46:12] |
| `recursion_limit` | Set explicitly (25 in the G1 demo, 40 in G2). Hitting it is a failed run (GP-77). | G1 [47:56]; G2 [54:36] |
| `Command(goto=…, update=…)` | A node that both routes and updates state. | G2 [22:28–24:20]; S-AG p.10 |
| `interrupt()` + checkpointer + `thread_id` | The three ingredients of human-in-the-loop. `Command(resume=…)` injects the human's answer. Use a durable checkpointer, not `InMemorySaver`, in production (GP-83). | S-AG p.10, pp.14–15 |
| `Send` | Dynamic parallel fan-out, for reads only (GP-80). | G2 [32:32–33:04]; S-AG p.20 |
| Subgraphs | Orchestrator-workers, hierarchical teams, and explaining a big graph (GP-79, GP-88). | G1 [55:12]; G2 [51:40–52:12] |
| `create_agent` + `HumanInTheLoopMiddleware` | Per-tool `interrupt_on` policy: approve, edit, reject or respond (GP-82). | S-AG p.11 |

### Evals and observability

| Tool | Status | What was said | Source |
|---|---|---|---|
| **LangSmith** annotation queues + datasets | Recommended | Humans review traces before they become labelled data. Also used for scaling labelling to contractors, with a codebook. | O1 [19:08–19:24]; E1 [21:24–21:56] |
| **Langfuse** | Recommended | Open source and **self-hostable**, which is the answer when traces hold sensitive data (GP-60). Datasets per category, labelled experiment runs, automatic prompt versioning. | O1 [15:24–16:44]; E2 [11:48–12:33] |
| **Braintrust** | Named | *"Might be the most opinionated"*, and has the best side-by-side experiment UX. Not worth it for error analysis. | E2 [12:45–13:04]; E3 [56:29–56:46] |
| **Label Studio** | Not recommended | *"always been more work than they're worth"* for error analysis. | E2 [45:36–45:50] |
| **Roll-your-own eval runner** | Byron's practice | Checks are simple static comparisons. Vendor platforms hold the datasets, and your scripts run them. | E2 [29:47–30:54] |
| **Roll-your-own error-analysis page** | Assigned | Trace list with a pass/error toggle, one note per trace and JSON export (GP-44). | E2 [45:50–48:00], [1:04:42–1:04:51] |
| **Correlation ≥ 0.8** (judge vs human) | Calibration target | Below that, the rubric is broken (GP-48). | S-EV p.19 |

### Models, gateways and other frameworks

| Tool | What was said | Source |
|---|---|---|
| **OpenRouter** | Gauntlet's recommended gateway: *"price competitive, gives you a larger model ecosystem and is still compatible with the OpenAI API."* | G1 [36:56–38:24] |
| **LangChain** | Right for real projects: *"You can use LangChain… and you probably should for real projects"*. Also *"not necessarily the one I would even just recommend blindly."* | E1 [32:40–32:56]; O1 [14:44–14:52] |
| **Claude Agent SDK, OpenAI Agents SDK, Google ADK, Microsoft Agent Framework, Deep Agents, Pydantic AI** | Worth looking at *"if you're in those ecosystems."* | O1 [47:32–48:12]; G2 [52:44–53:16]; S-AG p.34 |
| **General-purpose classifier models** (captioned "Jev"; spelling unverified) | One narrow decision with code around it, returned as label + probability (GP-70). Untested by the lecturer on "am I done". | L1 [17:56–20:25] |
| **HyDE, Self-RAG, CRAG, Adaptive RAG** | *"one idea per edge"*. HyDE is *"not a free win — test on your data"* (GP-85, GP-86). | G2 [40:52–47:24]; S-AG pp.25, 28 |
| **Knowledge graphs / GraphRAG / LightRAG** | *"make for visualizations that executives love"*. Start with vectors. | G2 [47:24–48:36] |
| **Open-weights models** | *"I would not reach to them this week."* | O1 [35:28–35:44] |

---

## What this means for our choices

This agrees with the decisions made on 2026-09-13 (see the session notes behind `status.md`):

- **LangGraph** fits Gauntlet's own guidance: LangChain as the teaching default, LangGraph *"if you are thinking multi-agent"* — which weeks 2 and 3 require.
- **Langfuse** is one of the two observability tools Aaron named, and the one Kwabena used for AgentForge.
- **Build the loop by hand once** before leaning on a framework: both lecturers taught the raw version first, and GP-7 expects you to explain what the framework does underneath.
