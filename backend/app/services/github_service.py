import requests
import base64
from app.core.config import GITHUB_TOKEN

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".go", ".cpp", ".c", ".cs",
    ".rb", ".php", ".rs", ".swift", ".kt"
}

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", "dist",
    "build", ".next", "venv", ".env", "vendor",
    "coverage", ".pytest_cache", "migrations"
}

MAX_FILE_SIZE_BYTES = 100_000  # skip files larger than 100kb

def parse_repo_url(url: str):
    try:
        url = url.strip().rstrip("/")
        # handle both https://github.com/owner/repo and github.com/owner/repo
        url = url.replace("https://", "").replace("http://", "")
        parts = url.replace("github.com/", "").split("/")
        if len(parts) < 2:
            raise ValueError("Invalid GitHub URL format")
        return parts[0], parts[1]
    except Exception:
        raise ValueError(f"Could not parse GitHub URL: {url}. Expected format: https://github.com/owner/repo")

def check_repo_accessible(owner: str, repo: str):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 404:
        raise ValueError(f"Repository '{owner}/{repo}' not found. Check the URL or make sure it's public.")
    if response.status_code == 403:
        raise ValueError(f"Access denied to '{owner}/{repo}'. Private repos require a token with repo scope.")
    if response.status_code != 200:
        raise ValueError(f"GitHub API error {response.status_code}: {response.text[:200]}")

def fetch_file_tree(owner: str, repo: str):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    # handle truncated trees (very large repos)
    if data.get("truncated"):
        print("  warning: repo tree truncated by GitHub (very large repo) — working with available files")

    tree = data.get("tree", [])
    code_files = []

    for item in tree:
        if item["type"] != "blob":
            continue

        path = item["path"]
        size = item.get("size", 0)

        # skip large files
        if size > MAX_FILE_SIZE_BYTES:
            print(f"  skipping large file: {path} ({size // 1000}kb)")
            continue

        # skip unwanted dirs
        if any(skip in path.split("/") for skip in SKIP_DIRS):
            continue

        # keep only allowed extensions
        ext = "." + path.split(".")[-1] if "." in path else ""
        if ext in ALLOWED_EXTENSIONS:
            code_files.append(path)

    return code_files

def fetch_file_content(owner: str, repo: str, path: str):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 403:
        raise ValueError(f"Rate limited or access denied for {path}")
    if response.status_code == 404:
        raise ValueError(f"File not found: {path}")

    response.raise_for_status()
    data = response.json()

    # handle submodules or symlinks (no content field)
    if "content" not in data:
        raise ValueError(f"No content available for {path}")

    content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
    return content

def fetch_repo(repo_url: str, max_files: int = None):
    owner, repo = parse_repo_url(repo_url)
    print(f"\nFetching repo: {owner}/{repo}")

    # check accessibility before fetching
    check_repo_accessible(owner, repo)

    file_paths = fetch_file_tree(owner, repo)
    print(f"Found {len(file_paths)} code files")

    if max_files:
        file_paths = file_paths[:max_files]
        print(f"Limiting to {max_files} files")

    print(f"Fetching {len(file_paths)} files...\n")

    files = []
    for path in file_paths:
        try:
            content = fetch_file_content(owner, repo, path)
            # skip empty files
            if not content.strip():
                continue
            files.append({"path": path, "content": content})
            print(f"  fetched: {path}")
        except Exception as e:
            print(f"  skipped: {path} ({e})")

    return files