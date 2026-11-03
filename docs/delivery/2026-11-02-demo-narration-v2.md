Spoken word count: 716. Estimated length at 150 words per minute: 4 minutes 46 seconds.

<!-- NARRATION START -->
<!-- scene: hook -->
A customs broker has a new product to file. Somewhere among about nineteen thousand eight hundred tariff lines is the exact ten digit code. A wrong code means the wrong duty. I built this to help the broker find a code worth reviewing before filing.

<!-- scene: overview -->
The user enters a product description. My system searches earlier customs rulings and the tariff schedule, then a small model uses that evidence to choose a code. The user sees the answer and the schedule lines found by search. A person reviews the choice. Saving time is the goal, not a measured result.

<!-- scene: architecture -->
I built search over twenty seven thousand eight hundred forty one real customs rulings and the schedule, using both keywords and meaning. The rulings come from United States Customs and Border Protection. Search returns twenty candidate lines. I kept the agency's own descriptions, removed answers, and used only government code labels. I fine tuned a four billion parameter model with small trainable adapters. It runs on one graphics processor.

<!-- scene: demo_prepared -->
I enter a men's jacket from a real test ruling issued after all training data. It is ninety five percent polyester, five percent elastane, knitted, brushed inside, with a zip front and banded cuffs. I turn on the base comparison and click classify. Both models get the same search evidence. The fine tuned answer appears first, in about two seconds, at the top left. Below it are the twenty tariff lines search found, with the chosen line in bold. The base model's card still says it is running, using that same set of evidence. While we wait, those construction details matter: this jacket is knitted, with no coated fabric described. The base takes about thirty seconds. Here are the results: the tuned model gets the knitted men's jacket line in about two seconds. The base picks a coated fabric garment line, which is wrong here.

<!-- scene: demo_grader -->
I enter a second example I picked from the test set, not a random one, also issued after all training data. This is an empty lipstick container made of injection molded plastic. Its turning mechanism raises and lowers lipstick and protects it during transport, storage, and use. Both models get the same search evidence. While we wait, watch whether each answer fits the material. Below the answer cards are the twenty tariff search results. Look for the chosen line among them, then compare it with the product description while the base model is still running. My tuned model is right about sixty percent overall. Here, it picks the plastic packing and carrying line in under two seconds. After about thirty seconds, the base picks a glass perfume or toilet container line, despite the plastic description.

<!-- scene: results -->
On five hundred fresh rulings, I scored exact ten digit matches. These rulings span August twenty twenty five through October twenty twenty six. Search alone scored thirty eight percent. The base, Qwen three four billion, scored forty two percent. Fine tuning raised that to fifty nine point eight percent. Claude Opus five point five was more accurate at seventy one point six percent. On an H one hundred, my model took about zero point nine seconds per request versus nine point nine for Opus. In bulk, classification cost was about one hundred fiftieth of Opus, excluding idle capacity and hosting.

<!-- scene: challenges -->
The hardest part was making the test honest. My first version always included the right code among eight choices. I rebuilt it with fresh rulings fetched individually, removed sentences that revealed answers, and froze the test rules before scoring any tuned model. Search now misses the code in twenty percent of cases. On those, Opus gets thirty percent right from memory; my model gets one percent. Memory drills raised recall without search from zero to forty six percent on development data, but barely helped with search. That follow up was not scored on the final test; the reported checkpoint stayed the same. Training on four hundred eighty eight verified explanations did not help either. Those experiments showed where the limits are.

<!-- scene: outro -->
I published the model and dataset on Hugging Face, alongside a live demo and results report. Fine tuning took my small model from forty two to about sixty percent. On the faster test hardware, it is about eleven times faster than Opus, but roughly twelve points less accurate.
<!-- NARRATION END -->
