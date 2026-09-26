import os
import sys
import requests

def post_comment(repo_full_name: str, pr_number: int, comment_body: str, token: str):
    """
    Posts a Markdown comment to a GitHub PR using GitHub REST API v3.
    """
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {"body": comment_body}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        print(f"🎉 Successfully posted audit comment to PR #{pr_number} on {repo_full_name}!")
        print(f"🔗 View comment: {response.json().get('html_url')}")
    else:
        print(f"❌ Failed to post comment ({response.status_code}): {response.text}", file=sys.stderr)
        sys.exit(1)

def main():
    # Gather configuration from environment (standard in CI/CD environments)
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY", "Sam4907/blast-radius")
    pr_num = os.getenv("PR_NUMBER")
    comment_file = sys.argv[1] if len(sys.argv) > 1 else "pr_comment.md"

    if not os.path.exists(comment_file):
        print(f"❌ Comment source file '{comment_file}' not found.")
        sys.exit(1)

    with open(comment_file, "r", encoding="utf-8") as f:
        body = f.read()

    if not token or not pr_num:
        print("⚠️ Missing GITHUB_TOKEN or PR_NUMBER environment variables.")
        print("Running in dry-run preview mode:")
        print("--------------------------------------------------")
        print(body[:300] + "\n... [truncated preview]")
        print("--------------------------------------------------")
        print("To post live: set GITHUB_TOKEN=ghp_xxx and PR_NUMBER=1")
        return

    post_comment(repo, int(pr_num), body, token)

if __name__ == "__main__":
    main()