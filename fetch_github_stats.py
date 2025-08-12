import requests
import os

GITHUB_USERNAME = "saimedhi"
TOKEN = os.getenv("GH_TOKEN")  # GitHub Personal Access Token

headers = {"Authorization": f"token {TOKEN}"}

# Get total PRs
def get_total_prs():
    url = f"https://api.github.com/search/issues?q=author:{GITHUB_USERNAME}+type:pr"
    r = requests.get(url, headers=headers)
    return r.json().get("total_count", 0)

# Get total additions & deletions
def get_total_lines():
    repos_url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100"
    repos = requests.get(repos_url, headers=headers).json()
    total_additions, total_deletions = 0, 0

    for repo in repos:
        stats_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo['name']}/stats/contributors"
        stats = requests.get(stats_url, headers=headers).json()
        if isinstance(stats, list):
            for contributor in stats:
                if contributor["author"]["login"] == GITHUB_USERNAME:
                    for week in contributor["weeks"]:
                        total_additions += week["a"]
                        total_deletions += week["d"]

    return total_additions, total_deletions

if __name__ == "__main__":
    prs = get_total_prs()
    additions, deletions = get_total_lines()
    with open("GITHUB_STATS.md", "w") as f:
        f.write(f"🚀 Total PRs: **{prs}**\n")
        f.write(f"📊 Total Lines Added: **{additions:,}**\n")
        f.write(f"📉 Total Lines Deleted: **{deletions:,}**\n")
