import requests, time, sys

USERNAME = "saimedhi"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": f"{USERNAME}-readme-stats"
}

def get_json(url, params=None, retries=6, backoff=2.0):
    for i in range(retries):
        r = requests.get(url, headers=HEADERS, params=params or {})
        if r.status_code == 202:  # stats being generated
            time.sleep(backoff)
            continue
        if r.ok:
            return r.json()
        time.sleep(backoff)
    r.raise_for_status()
    return r.json()

def get_public_merged_prs(username):
    # public, tokenless search
    params = {"q": f"author:{username} type:pr is:merged", "per_page": 1}
    data = get_json("https://api.github.com/search/issues", params=params)
    return data.get("total_count", 0)

def get_lines_changed_user_repos(username):
    # Sum additions+deletions from your OWN public repos only
    repos = get_json(f"https://api.github.com/users/{username}/repos?per_page=100")
    adds = dels = 0
    if not isinstance(repos, list):
        return 0, 0
    for repo in repos:
        stats = get_json(f"https://api.github.com/repos/{username}/{repo['name']}/stats/contributors")
        if isinstance(stats, list):
            me = next((c for c in stats if c.get("author", {}).get("login") == username), None)
            if me:
                for w in me.get("weeks", []):
                    adds += w.get("a", 0)
                    dels += w.get("d", 0)
    return adds, dels

if __name__ == "__main__":
    try:
        merged_prs = get_public_merged_prs(USERNAME)
        adds, dels = get_lines_changed_user_repos(USERNAME)
    except Exception as e:
        print(f"Failed to fetch stats: {e}", file=sys.stderr)
        sys.exit(1)

    block = (
        f"🚀 **Merged PRs (public):** {merged_prs}\n"
        f"📊 **Lines Added (own public repos):** {adds:,}\n"
        f"📉 **Lines Deleted (own public repos):** {dels:,}"
    )

    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    start, end = "<!--START_STATS-->", "<!--END_STATS-->"
    if start not in readme or end not in readme:
        print("Markers not found in README.md", file=sys.stderr)
        sys.exit(1)

    new = readme.split(start)[0] + start + "\n" + block + "\n" + readme.split(end)[1]
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new)

    print("README updated.")
