import requests
import os

USERNAME = "saimedhi"
TOKEN = os.getenv("GH_TOKEN")

headers = {"Authorization": f"token {TOKEN}"}

def get_total_prs():
    url = f"https://api.github.com/search/issues?q=author:{USERNAME}+type:pr+is:merged"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json().get("total_count", 0)

def get_total_lines():
    repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
    repos = requests.get(repos_url, headers=headers).json()
    total_additions, total_deletions = 0, 0

    for repo in repos:
        stats_url = f"https://api.github.com/repos/{USERNAME}/{repo['name']}/stats/contributors"
        stats = requests.get(stats_url, headers=headers).json()
        if isinstance(stats, list):
            for contributor in stats:
                if contributor["author"]["login"] == USERNAME:
                    for week in contributor["weeks"]:
                        total_additions += week["a"]
                        total_deletions += week["d"]

    return total_additions, total_deletions

if __name__ == "__main__":
    prs = get_total_prs()
    additions, deletions = get_total_lines()

    stats_text = (
        f"🚀 **Merged PRs:** {prs}\n"
        f"📊 **Lines Added:** {additions:,}\n"
        f"📉 **Lines Deleted:** {deletions:,}"
    )

    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    start = "<!--START_STATS-->"
    end = "<!--END_STATS-->"
    new_readme = readme.split(start)[0] + start + "\n" + stats_text + "\n" + readme.split(end)[1]

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme)
