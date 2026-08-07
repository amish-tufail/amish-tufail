"""Pull live numbers from the GitHub API into stats.json.

Run locally with `gh` authenticated, or in Actions with GITHUB_TOKEN.
Everything the README shows numerically comes from here, so the profile
stays true without anyone editing an SVG by hand.
"""
import json, os, subprocess, sys, collections

USER = "amish-tufail"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Languages that are build noise or research output rather than shipped app code.
EXCLUDE = {"Jupyter Notebook", "Makefile", "Dockerfile", "HTML", "CMake", "Shell",
           "Kotlin", "Java", "Ruby", "R"}
PRETTY = {"Gen-AI": "Gen AI", "GenAI-Editor": "Gen AI Editor"}
FEATURED = ["Gen-AI", "Flon", "MailBrief", "Trace", "Zerack", "SwiftSocialKit"]


def gh(path, tries=4):
    """GitHub secondary rate limits bite on bursts of small calls, so back off."""
    import time
    for i in range(tries):
        out = subprocess.run(["gh", "api", path], capture_output=True, text=True)
        if out.returncode == 0:
            try:
                return json.loads(out.stdout)
            except json.JSONDecodeError:
                return None
        time.sleep(1.5 * (i + 1))
    print(f"  ! gave up on {path}: {out.stderr.strip()[:120]}", file=sys.stderr)
    return None


CAL_QUERY = """
{ user(login:"%s") { contributionsCollection {
    totalCommitContributions restrictedContributionsCount
    contributionCalendar { totalContributions
      weeks { firstDay contributionDays { date contributionCount } } } } } }
""" % USER


def contributions():
    """Real contribution calendar plus streaks, computed rather than guessed."""
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={CAL_QUERY}"],
                         capture_output=True, text=True)
    if out.returncode:
        return {}
    cc = json.loads(out.stdout)["data"]["user"]["contributionsCollection"]
    cal = cc["contributionCalendar"]
    weeks = [[d["contributionCount"] for d in w["contributionDays"]] for w in cal["weeks"]]
    week_starts = [w["firstDay"] for w in cal["weeks"]]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]

    # Streaks. Today counts as "not yet broken" if it is still empty.
    counts = [d["contributionCount"] for d in days]
    longest = cur = 0
    for c in counts:
        cur = cur + 1 if c > 0 else 0
        longest = max(longest, cur)
    current = 0
    for c in reversed(counts[:-1] if counts and counts[-1] == 0 else counts):
        if c == 0:
            break
        current += 1

    active = sum(1 for c in counts if c > 0)
    best = max(days, key=lambda d: d["contributionCount"])
    return {
        "contrib_total": cal["totalContributions"],
        "contrib_private": cc["restrictedContributionsCount"],
        "contrib_weeks": weeks,
        "week_starts": week_starts,
        "first_day": days[0]["date"],
        "last_day": days[-1]["date"],
        "streak_current": current,
        "streak_longest": longest,
        "active_days": active,
        "total_days": len(days),
        "best_day": best["date"],
        "best_day_count": best["contributionCount"],
        "peak": max(counts) or 1,
    }


def main():
    user = gh(f"users/{USER}") or {}

    # `gh repo list` honours the current token, so it also sees private repos when
    # one with `repo` scope is available. Falls back to public-only otherwise.
    out = subprocess.run(
        ["gh", "repo", "list", USER, "--limit", "300", "--source",
         "--json", "name,isFork,visibility"],
        capture_output=True, text=True)
    repos = json.loads(out.stdout) if out.returncode == 0 else []
    public_only = all(r["visibility"] == "PUBLIC" for r in repos) if repos else True

    totals = collections.Counter()
    per_repo = {}
    for r in repos:
        if r.get("isFork"):
            continue
        langs = gh(f"repos/{USER}/{r['name']}/languages") or {}
        totals.update(langs)
        if langs.get("Swift"):
            per_repo[r["name"]] = langs["Swift"]

    app = {k: v for k, v in totals.items() if k not in EXCLUDE}
    tot = sum(app.values()) or 1
    swift = app.get("Swift", 0) / tot * 100
    python = (app.get("Python", 0)) / tot * 100
    other = max(100 - swift - python, 0)

    top = [[PRETTY.get(n, n), per_repo.get(n, 0) / 1024]
           for n in FEATURED if per_repo.get(n)]
    top = sorted(top, key=lambda x: -x[1])[:5]

    contrib = contributions()

    data = {
        "repos": user.get("public_repos", 59),
        "total_repos": len([r for r in repos if not r.get("isFork")]),
        "public_only": public_only,
        "years": "3+",
        "mix": [["Swift", round(swift, 1), "a4"],
                ["Python", round(python, 1), "a1"],
                ["Other", round(other, 1), "a3"]],
        "top_repos": [[n, round(kb, 1)] for n, kb in top],
        **contrib,
    }
    with open(os.path.join(ROOT, "stats.json"), "w") as f:
        json.dump(data, f, indent=2)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    sys.exit(main())
