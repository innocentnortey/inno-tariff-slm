"""Inject curated.json into template.html and sanity-check it.

Usage: python3 -I build.py curated.json template.html ../slm-domain-explorer.html
"""
import json
import sys

REQUIRED = ["id", "rank", "name", "industry", "verdict", "task", "why_hard", "business", "ft_vs_rag",
            "behavior_spec", "example_input", "example_output", "example_note", "agentic_demo", "eval",
            "risks", "feasibility", "scores", "score_notes", "datasets", "total"]


def main(curated_path, template_path, out_path):
    data = json.load(open(curated_path, encoding="utf-8"))
    keys = [r["key"] for r in data["rubric"]]
    problems = []
    for i in data["ideas"]:
        for k in REQUIRED:
            if i.get(k) in (None, "", []):
                problems.append(f"{i.get('id')}: missing {k}")
        for k in keys:
            if not 1 <= i["scores"].get(k, 0) <= 5:
                problems.append(f"{i['id']}: score {k} out of range")
            if not i["score_notes"].get(k):
                problems.append(f"{i['id']}: no reason for {k}")
        if i["total"] != sum(i["scores"][k] for k in keys):
            problems.append(f"{i['id']}: total mismatch")
        if i["rank"] <= 3 and "experiment" not in i:
            problems.append(f"{i['id']}: top-3 without experiment")
        for d in i["datasets"]:
            if not d.get("url", "").startswith("http"):
                problems.append(f"{i['id']}: dataset without url: {d.get('name')}")
        text = json.dumps(i).lower()
        for banned in ("cvss", "att&ck", "decompil"):
            if banned in text:
                problems.append(f"{i['id']}: mentions removed cyber topic '{banned}'")
    ranks = sorted(i["rank"] for i in data["ideas"])
    if ranks != list(range(1, len(ranks) + 1)):
        problems.append(f"ranks not contiguous: {ranks}")
    html = open(template_path, encoding="utf-8").read()
    assert "/*__DATA__*/" in html
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    open(out_path, "w", encoding="utf-8").write(html.replace("/*__DATA__*/", payload))
    print(f"ideas={len(data['ideas'])} rejected={len(data['rejected'])}")
    print("problems:" if problems else "no problems")
    for p in problems:
        print("  -", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
