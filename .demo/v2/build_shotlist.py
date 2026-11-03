"""Build .demo/v2/shotlist.yaml from the template and Codex's narration, copying each scene's block verbatim.

  python3 .demo/v2/build_shotlist.py

Scene ids in the template carry `narration: "{{scene_id}}"`; each is replaced by the block under
`<!-- scene: scene_id -->` in docs/delivery/2026-11-02-demo-narration-v2.md. The grader prompt lives in
.demo/v2/grader_prompt.json ({"product": ..., "description": ...}); until Innocent supplies one, a placeholder is used.
"""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[2]
text = (root / "docs/delivery/2026-11-02-demo-narration-v2.md").read_text()
body = text.split("<!-- NARRATION START -->")[1].split("<!-- NARRATION END -->")[0]
parts = re.split(r"<!-- scene: (\w+) -->", body)
blocks = {parts[i]: " ".join(parts[i + 1].split()) for i in range(1, len(parts), 2)}
tpl = (Path(__file__).parent / "shotlist.template.yaml").read_text()
gp = Path(__file__).parent / "grader_prompt.json"
grader = json.loads(gp.read_text()) if gp.exists() else {"product": "PLACEHOLDER product",
                                                          "description": "PLACEHOLDER description from the grader."}
for k, v in blocks.items():
    tpl = tpl.replace("{{" + k + "}}", v.replace('"', '\\"'))
tpl = tpl.replace("{{grader_product}}", grader["product"].replace('"', '\\"'))
tpl = tpl.replace("{{grader_description}}", grader["description"].replace('"', '\\"'))
tpl = tpl.replace("{{grader_description_js}}", "'" + grader["description"].replace("\\", "").replace("'", "\\\\'") + "'")
missing = re.findall(r"\{\{(\w+)\}\}", tpl)
assert not missing, f"no narration for {missing}"
(Path(__file__).parent / "shotlist.yaml").write_text(tpl)
print("wrote shotlist.yaml;", sum(len(v.split()) for v in blocks.values()), "words;",
      "grader prompt:", "SUPPLIED" if gp.exists() else "placeholder")
