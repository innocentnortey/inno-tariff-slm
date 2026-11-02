# Label review and build fixes

## Changed
Reviewed the derived labels (dimension, value, decision, ablations): 100 items read in two rounds plus a pattern audit of every item. Rewrote `attributes.py` so evidence must support the gold line over the sibling; fixed fiber, elastomeric, garment, gender, knit-to-shape and ablation patterns; drop 83 conflicting items. Added 21 regression tests. Rebuilt the data and reran baselines.

## Why
Innocent delegated the Step 1 review; derived labels decide what the model is trained and scored on.

## Checked
Round 1: 8 errors in 50; round 2 after fixes: 5 in 50, then fixed; all flagged items re-checked by script; tests pass.

## Remaining
Spec sign-off; judge needs ~20 human labels; review was by Claude, not independent.
