# Concept introduction narration

Total spoken word count: 660.
Estimated length at 150 words per minute: 4 minutes 24 seconds.
Estimated reading level: grades 7–8.

<!-- NARRATION START -->
<!-- scene: intro -->
It's filing week at a mid size apparel and footwear importer. The classification specialist has new styles. Every import needs a ten digit tariff code, and the importer is legally responsible. I'm proposing a human supervised analyst with a small model. No model has been trained yet.

<!-- scene: problem -->
There are nineteen thousand nine hundred forty nine ten digit lines. Small details decide the last four digits. A scarf with at least seventy percent silk gets one point two percent duty, versus three point nine for other silk. G P T five Thinking got a quarter of full codes right on two hundred rulings in Atlas twenty twenty five. A wrong code means wrong duty on every shipment.

<!-- scene: vision -->
My proposed workflow reads documents, extracts product details, and retrieves codes and past U.S. Customs rulings. The specialist would choose or ask, code would calculate duty, and a licensed person would approve. It would never make a binding decision.

<!-- scene: journey_attributes -->
Here, the mock follows a real women's knit shrug from China, ninety four percent polyester and six percent elastane. It shows the extracted details beside eight close codes, all at fourteen point nine percent. The products, codes, and rates are real. The analyst's outputs are hand written.

<!-- scene: journey_decision -->
The closest pair differs only on who wears it. The description says Woman's, so my example chooses the women's line and names that clue and the runner up. That choice is written by hand, not a model result.

<!-- scene: journey_ask -->
But the shoe description leaves out who wears it. The two best lines say for women and for men. Here I want need info, followed by one question to the supplier. Asking for the missing fact instead of guessing is the difference I'm testing.

<!-- scene: journey_review -->
For the shrug, plain code would calculate duty using invented value and quantity. The ruling also notes an extra China duty that a duty service must look up. A reviewer could approve, edit, or escalate, with evidence. A person decides.

<!-- scene: why_slm -->
I'd train one narrow behavior. Given a description and eight candidates, choose one and quote the deciding detail, or say need info and name what's missing. Never cite an unstated fact. Retrieval supplies facts. I suspect past rulings can teach this pattern. Atlas fine tuned a seventy billion parameter model from about two to forty percent at ten digits. Whether one to four billion parameters can do it, with cost, speed, privacy, and consistency benefits, remains a hypothesis.

<!-- scene: data -->
U.S. Customs publishes binding rulings with its own labels. The starting pool has nine thousand five hundred sixty six apparel and footwear rulings. My plan drops obsolete codes, trains through twenty twenty two, and tests on twenty twenty four through twenty twenty five. Deciding details would come from where sibling codes first differ in the schedule. Removing details would create ask cases, without teacher model labels.

<!-- scene: architecture -->
Each part would own one kind of decision. Language models handle language, code handles rules and arithmetic, and a person owns the final call. The specialist must stay within its code list. No model touches duty numbers. Effective dates, origin duties, and old rulings still need work.

<!-- scene: evaluation -->
I'd compare every model on the same eight candidates. My first test spans two frontier families, three prompting styles, and over thirty scenarios each. It hasn't run. The tuned model's proposed bar is a twenty point gain over its base in following the spec on held out rulings, with at least seventy percent recall for missing facts and at most ten percent needless questions. If prompting solves it, I'll narrow the behavior.

<!-- scene: status -->
Only rule baselines have run, with attribute rules at about twenty one percent. Business value is unmeasured. This package does not yet meet the early submission evidence requirements. It sets the direction. Across nine stages, next comes prompting, then data, the first fine tune, and a four point data curve.

<!-- scene: outro -->
My goal is a small specialist that chooses between close tariff codes or asks, with human oversight. Next, I'll run the prompting test.
<!-- NARRATION END -->
