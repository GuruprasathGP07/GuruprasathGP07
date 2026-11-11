"""Draws stats.svg from the GitHub GraphQL API. Needs env var GH_TOKEN."""
import os, sys, json, urllib.request

LOGIN = "GuruprasathGP07"
QUERY = """query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{contributionCount date}}}}}}"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        json.dumps({"query": QUERY, "variables": {"l": LOGIN}}).encode(),
        {"Authorization": f"bearer {os.environ['GH_TOKEN']}", "Content-Type": "application/json"},
    )
    data = json.load(urllib.request.urlopen(req))
    if "errors" in data:
        sys.exit(str(data["errors"]))
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


cal = fetch()
weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]]
days = [d["contributionCount"] for w in cal["weeks"] for d in w["contributionDays"]]

total = sum(days)
active = sum(1 for d in days if d)
best = max(weeks) if weeks else 0

longest = run = 0
for d in days:
    run = run + 1 if d else 0
    longest = max(longest, run)
current = 0
for i, d in enumerate(reversed(days)):
    if d:
        current += 1
    elif i == 0:
        continue
    else:
        break

W, H = 560, 60
step = W / max(len(weeks) - 1, 1)
pts = [(i * step, H - (v / best * H if best else 0)) for i, v in enumerate(weeks)]
line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
area = f"0,{H} {line} {W},{H}"
lx, ly = pts[-1]

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="210" viewBox="0 0 600 210"
 font-family="JetBrains Mono,ui-monospace,SFMono-Regular,Menlo,monospace">
<text x="20" y="70" font-size="64" font-weight="700" fill="#e6edf3">{total}</text>
<text x="22" y="95" font-size="13" fill="#8b949e">contributions in the last year</text>
<g text-anchor="end">
<text x="580" y="34" font-size="22" font-weight="700" fill="#e6edf3">{active}</text>
<text x="580" y="50" font-size="11" fill="#8b949e">active days</text>
<text x="580" y="80" font-size="22" font-weight="700" fill="#e6edf3">{best}</text>
<text x="580" y="96" font-size="11" fill="#8b949e">best week</text>
<text x="580" y="126" font-size="11" fill="#8b949e">streak {current}d · longest {longest}d</text>
</g>
<g transform="translate(20,135)">
<polygon points="{area}" fill="#58a6ff" opacity="0.15"/>
<polyline points="{line}" fill="none" stroke="#58a6ff" stroke-width="2" stroke-linejoin="round"
 stroke-dasharray="2000" stroke-dashoffset="2000">
<animate attributeName="stroke-dashoffset" from="2000" to="0" dur="2s" fill="freeze"/></polyline>
<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4" fill="#e6edf3" opacity="0">
<animate attributeName="opacity" from="0" to="1" begin="2s" dur="0.3s" fill="freeze"/></circle>
</g></svg>'''
open("stats.svg", "w", encoding="utf-8").write(svg)
print("stats.svg written:", total, active, best, current, longest)
