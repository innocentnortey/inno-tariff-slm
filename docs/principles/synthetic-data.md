# Synthetic Data — GP-34 to GP-37

From the second half of Aaron's first lecture (V1 [51:24–57:52]). Synthetic data gives you development material and eval cases, and it is *"critical in areas such as say health where getting the real data might not be easy because of privacy and cost"* (V1 [51:48–52:04]). AgentForge requires demo data only.

---

## GP-34 — Use a tool call as a structured data generator

**Statement.** Define a tool whose schema is the record you want (e.g. `make_fake_patient`), prompt the model to call it with guidance on how to vary cases, and have the tool body simply save the arguments.

**Source.** V1 [52:20–53:32]: *"make a tool… the tool is called make fake customer, and then the function signature of the tool is customer name, customer email… and then you prompt the LLM to call the tool and you describe how to make up the cases a bit… every time it calls the tool that's giving you JSON, and the actual body of this function could be as simple as just saving that to a JSON file."*

**In practice.** Generate intake-form payloads with the same Pydantic schema the extractor targets, so generated cases and extraction output are directly comparable.

---

## GP-35 — Perturb real examples

**Statement.** Take a real example and ask the model to rewrite it along a controlled dimension — adding noise, jitter or a persona — to get realistic variation.

**Source.** V1 [53:32–56:24]: *"take existing real data and change it a bit, add a little bit of jitter or noise. And this is a very effective technique to make your data a little bit more realistic… it's a parameterized prompt… we are varying it along this dimension, age, which we're really using as a proxy for the sophistication of the writing… adding noise and variation to real data is one of the best ways to make plausible fake data."*

**In practice.** From one clean synthetic lab report, generate a faxed/degraded variant, one with a unit in a non-standard format, and one missing a reference range.

---

## GP-36 — Break known-good things on purpose

**Statement.** Language models are good at breaking things in specific ways. Take something correct and introduce a targeted defect to make test cases.

**Source.** V1 [56:32–56:56]: *"take something like say code, which is structured, and add bugs to it. That can be a great way if you're making a code debugging system and you need test cases. LLMs can be great at breaking things. So taking something realistic, tweaking it, but tweaking it a very particular way."*

**In practice.** Week 3's adversarial platform in miniature: mutate a clean prompt into injection variants; mutate a clean intake form into one that contradicts the chart's allergy list.

---

## GP-37 — Seed with random draws, let the model elaborate

**Statement.** Generate the specific facts with a classic random library, then have the model write the realistic document around them. Specific inputs force specific, structured outputs.

**Source.** V1 [56:56–57:44]: *"there's a Python library called Faker, which has a bunch of built-ins for making plausible fake stuff. And this is just classic random draws, but you could feed this as input… we're making up all this very specific information and we're giving it structure. And that'll make the LLM actually include that information and be structured as well."*

**In practice.** Draw a patient's age, meds and abnormal values in code (so the expected answer is known), then have the model produce the discharge summary. The drawn values become the eval's ground truth.
