# Tool Design — GP-8 to GP-13

Tools are how an agent touches the world. Both lecturers treat tool design as the highest-leverage code you write.

---

## GP-8 — Tools are atomic, idempotent, well documented and structured

**Statement.** One tool does one thing; it is safe to retry; its name and docstring explain it; its inputs, outputs and errors are structured; and its results are verified deterministically where possible.

**Source.** Aaron, V1 [21:36–23:04]: *"we want these tools to often be atomic… if a tool can do multiple things, that makes it a bad tool. That makes it ambiguous to decide when to use it or not… You want an idempotent tool… safe to retry if there's a failure. Well documented… structured errors… and verify the results if possible, ideally deterministically."* V1 [35:28–35:44]: treat them *"as if they were a good tool for you. A good Unix CLI sort of tool… Does one thing, does it well, clear what it does."*

**In practice.** `get_active_medications(patient_id)` and `get_allergies(patient_id)`, not `get_patient_everything(patient_id, what)`. Reads are naturally idempotent; any write needs an idempotency key. Errors return a typed object (`{"error": "fhir_timeout", "retryable": true}`), never a stack trace.

---

## GP-9 — Tool descriptions do the routing

**Statement.** The model picks tools by zero-shot matching the user's message against your description strings. A vague description causes wrong calls, missed calls and invented arguments.

**Source.** Jacob, V3 [24:24–26:08]: *"The descriptions of your tools are what are doing the work… the model is doing zero-shot intent classification against the description strings that you wrote… 'get current weather for a city' is a much stronger signal than just 'weather'. Sloppy descriptions are going to lead to wrong tool calls, missed calls or hallucinated arguments. Write the description like you're writing a docstring for a junior engineer who has no other context."* Aaron, V1 [21:52–22:16]: *"If the code is literate, then often the LLM will be able to understand."*

**In practice.** Descriptions say *when* to use the tool and *when not to*: *"Return the patient's currently active medication list from the chart. Use for questions about what the patient is taking now. Does not include discontinued medications — use get_medication_history for those."* Tool-selection cases belong in the eval set (GP-20).

---

## GP-10 — Schema-constrained tool calls are the structure guarantee

**Statement.** A tool schema constrains the model's output to valid arguments. It is the main way to get reliable structured output — far better than asking for JSON in prose.

**Source.** Aaron, V1 [42:12–43:24]: *"this gives deterministic guarantees… that the language model, if it chooses to execute the tool, will do so with a tool call request that adheres to this structure… internally it's restricting the token output space of the model… In the pre-tool-calling days… you could ask an LLM, hey, give me some JSON… and it might be a little inconsistent… You don't do that with tool calling."*

**In practice.** Define every tool input and output as a Pydantic (or Zod) model and generate the schema from it. For pure extraction (GP-5), use the provider's structured-output mode or a "record result" tool rather than parsing free text.

---

## GP-11 — The model advises; your code executes

**Statement.** The model only *requests* a tool call. Your code decides whether to run it, runs it, and owns authentication, secrets, retries and side effects. That gap is where checks, refusals and human approval go.

**Source.** Aaron, V1 [43:40–44:52]: *"the model is not executing the tool. The model is just an API call to a probability model. You are writing the code that does what comes next… it might actually do some checks… this SQL query that it wants to execute would have too high of a cost. We shouldn't execute this… or you could even have human in the loop."* Jacob, V3 [29:12–29:28]: *"The LLM never runs your code, ever. It tells you what to run and you run it. The model is always the advisor, never the executor. This matters for security, correctness, and where your auth and error handling live."* V3 [12:04–12:20]: *"your tool's job is to actually touch your systems… handle authentication secrets, how many times you might retry… and then return a clean result. Those responsibilities never cross."*

**In practice.** Between the model's request and execution, enforce in code: the `patient_id` argument matches the conversation's pinned patient; the caller's role may use this tool; the arguments are in range. A mismatch returns a structured refusal to the model, not data.

---

## GP-12 — Handle every response branch

**Statement.** A model response can contain no tool call, one, or several (possibly in parallel). Each tool result must be returned with its call ID. Raw-SDK arguments arrive as a JSON string.

**Source.** Jacob, V3 [25:04–25:36]: three outcomes — a matching call, *"multiple tool calls… or it's going to call more than one in parallel"*, or *"no tool call and your code does have to handle that branch. If you assume there's always going to be a tool call, you are going to crash."* V3 [16:48–17:36]: every call has a name, arguments and an ID; *"when you send the tool results back, you have to include that same ID and if you don't, the model doesn't know which of its requests got answered."* V3 [17:44–18:00]: arguments come back *"as a string, not an object. So we have to parse it."* V3 [29:28–29:44]: *"Real agents commonly take four, five, six turns."*

**In practice.** The loop handles: final answer, N tool calls executed and returned by ID, unknown tool name, malformed arguments (validation error back to the model), and a tool that raises. Each branch has a test.

---

## GP-13 — Limit the choices

**Statement.** Every extra option makes the model's decision harder. About three is easy, five to ten depends on how distinct they are, thirty is too many — split into sub-agents or pre-filter the tool set.

**Source.** Aaron, V1 [14:32–14:48]: *"you might not want to just kitchen-sink your system… that actually makes the decision of what to do next harder. You might want to limit its choices as much as you can."* V2 [30:56–31:44]: *"Three options, that's a pretty easy decision. Five options up to 10, it depends… if you have like 30 different ways… it might not [do well]… you might need to have sub-agents."* Jacob, V3 [1:13:36–1:14:24]: with a hundred tools, *"have like a classifier… classify what potential tools could be used and then pull those tools in."*

**In practice.** Scope tool sets by role and by use case — a nurse's registry is smaller than a physician's, and a "pre-visit brief" flow needs only the tools that brief uses.
