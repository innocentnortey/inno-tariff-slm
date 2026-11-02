Word count, six hundred seventy five. Estimated length, four minutes and thirty seconds at one hundred fifty words per minute.

<!-- NARRATION START -->
<!-- scene: intro -->
It is filing week. A customs broker at a mid size apparel and footwear importer gets new styles with thin descriptions. One missing fact can change the duty on every shipment. I built a specialist to catch that gap before filing.

<!-- scene: overview -->
Every import needs a ten digit code. I want to help this broker avoid a confident wrong answer. The flow I designed starts with a shortlist. My specialist picks with evidence or asks for a missing fact. That becomes a supplier question. A person approves.

<!-- scene: architecture -->
I have not built candidate retrieval yet. Keyword search finds the right code among eight candidates only four percent of the time. Here, I supply the candidates. I tuned Qwen three, one point seven billion, using Q LoRA on Modal. It returns one J S O N answer, pick and quote, or ask. Code checks the format and candidate code, then checks that the quote appears in the description. A licensed broker approves the legal call. Code labels come from real C B P rulings, never a model. I ran three label reviews. Copies with deciding facts removed teach asking. My sealed test uses two hundred twenty one cases from twenty twenty four and twenty twenty five.

<!-- scene: live1 -->
Here is the broker's blouse. Women's short sleeve, one hundred percent cotton knit. Both models pick six one zero six, one zero, zero zero, one zero, citing women's. My tuned model also names the runner up.

<!-- scene: live2 -->
Now I remove women's. The base model still picks the women's line. It cites of cotton, words from the schedule, under the wrong kind of fact.

My tuned model asks who wears it. That is the behavior I want before this broker files.

<!-- scene: case1 -->
I also checked ballet shoes in the sealed test. Two styles, no wearer stated. The base model picks. Claude Opus five point five picks without supporting words. My specialist asks for the wearer.

<!-- scene: case2 -->
Chest waders show the same pattern. The base model calls them house slippers. Opus picks a code. My specialist asks who wears them.

<!-- scene: curve -->
I learned this through data. At first, only six percent of training examples taught asking. When a fact was missing, it asked sixty one percent of the time. Adding six hundred seventy eight ask examples, with the same training settings, raised that to ninety four percent on development data. Rebalancing rare branches and making a second training pass averaged one hundred thirty six of one hundred fifty seven correct, and fifty one of fifty eight robust across two random seeds. Opus scored one hundred thirty five and fifty one.

<!-- scene: weak -->
But I still see failures. On a woman's rain boot covered in leather flocking, my model treats leather as the upper. C B P says other materials. Opus gets it right. The surface rule is missing from my input. Pretraining likely gives Opus that knowledge.

<!-- scene: results -->
On the sealed test, the overall behavior score rose from six point three to eighty point one percent, reproducible with one command. Opus scores eighty four point six. Robustness ties at seventy five percent. My model asks when facts are missing eighty four to eighty nine percent of the time, versus seventy three. On thirteen summaries missing facts without my removing them, it asks eleven times versus six. These model written summaries can omit facts from original rulings. Unneeded questions are one point six percent versus three point three. The latest tuned results are a second look at this test.

<!-- scene: plan -->
My plan was to beat frontier models at classification, but things didn't go as planned. In twenty twenty five, Atlas research found a frontier model right about a quarter of the time searching the full schedule. I handed over eight close candidates. The frontier model reads them well. My specialist comes close, but is not ahead at picking codes. It does refuse to guess more reliably. Next I would build better candidate retrieval for the full search, keeping this decide or ask step.

<!-- scene: outro -->
I built a specialist that asks for missing facts before filing. My model and dataset are public on Hugging Face.
<!-- NARRATION END -->
