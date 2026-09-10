import os
import re
import urllib.request
import json
import base64

GITHUB_USERNAME = "MAhsaanUllah"
README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")
API_URL = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?sort=pushed&per_page=30"

START_MARKER = "<!-- RECENT_PROJECTS:START -->"
END_MARKER = "<!-- RECENT_PROJECTS:END -->"

TOPIC_MAP = {
    "langgraph": "LangGraph",
    "fastapi": "FastAPI",
    "react": "React",
    "qdrant": "Qdrant",
    "supabase": "Supabase",
    "docker": "Docker",
    "pytorch": "PyTorch",
    "scikit-learn": "Scikit-Learn",
    "nlp": "NLP",
    "saas": "SaaS",
    "multi-tenant": "Multi-Tenant",
    "rag": "RAG",
    "opencv": "OpenCV",
    "typescript": "TypeScript",
    "python": "Python",
    "clerk": "Clerk",
    "streamlit": "Streamlit",
    "win32": "Win32",
    "human-in-the-loop": "HITL",
    "ai-agents": "AI Agents",
    "deepseek": "DeepSeek",
    "devsecops": "DevSecOps",
    "whatsapp-bot": "WhatsApp Bot",
    "desktop-automation": "Desktop Automation",
    "glassmorphism": "Glassmorphism",
    "hybrid-search": "Hybrid Search",
    "llm": "LLM",
}

SPECIAL_NAMES = {
    "agent_friday": "Agent Friday",
    "waraq-ai": "Waraq AI",
    "screenos": "ScreenOS",
    "tarkabot-saas-showcase": "TarkaBot SaaS",
    "deepfakeshield-showcase": "DeepFakeShield",
    "exportshield-saas-showcase": "ExportShield Pro",
    "fraud-detection-ml": "Fraud Detection ML",
    "medivision-ai-disease-predictor": "MediVision AI",
    "aurascout-ai": "AuraScout AI",
    "project-aura-forensic-hub": "Project Aura",
    "edumentor-live": "EduMentor Live",
    "sentinelfix-ai": "SentinelFix AI",
}

def get_headers():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"User-Agent": "GitHub-Profile-Updater"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def fetch_json(url):
    req = urllib.request.Request(url, headers=get_headers())
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def truncate_text(text, max_len=115):
    text = text.strip()
    # clean multiple spaces / newlines
    text = re.sub(r"\s+", " ", text)
    if len(text) <= max_len:
        return text
    # cut at last space before max_len
    truncated = text[:max_len]
    last_space = truncated.rfind(" ")
    if last_space > 50:
        truncated = truncated[:last_space]
    return truncated + "..."

def get_repo_readme_summary(repo_name):
    try:
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/readme"
        data = fetch_json(url)
        content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("<") or line.startswith("![") or line.startswith("[!["):
                continue
            if len(line) > 20:
                clean = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", line)
                clean = re.sub(r"[*_`#]", "", clean)
                return truncate_text(clean, 115)
    except Exception:
        pass
    return "Active development and engineering build"

def choose_emoji(name, topics):
    all_text = (name + " " + " ".join(topics)).lower()
    if any(k in all_text for k in ["agent", "langgraph", "friday", "bot"]):
        return "🤖"
    if any(k in all_text for k in ["rag", "doc", "waraq", "pdf", "retrieval"]):
        return "📄"
    if any(k in all_text for k in ["shield", "fraud", "security", "detect"]):
        return "🛡️"
    if any(k in all_text for k in ["tarka", "food", "restaurant"]):
        return "🍽️"
    if any(k in all_text for k in ["screen", "vision", "cv", "eye"]):
        return "👁️"
    return "⚡"

def format_tech_core(repo):
    topics = repo.get("topics", [])
    formatted_topics = []
    for t in topics:
        key = t.lower()
        if key in TOPIC_MAP:
            formatted_topics.append(TOPIC_MAP[key])
        elif len(t) <= 14 and not t.isdigit():
            formatted_topics.append(t.replace("-", " ").title())
        if len(formatted_topics) >= 3:
            break

    lang = repo.get("language")
    if not formatted_topics:
        if lang:
            return lang
        return "Python"

    if lang and lang not in formatted_topics and len(formatted_topics) < 3:
        formatted_topics.insert(0, lang)

    return " · ".join(formatted_topics[:3])

def get_clean_name(raw_name):
    low = raw_name.lower()
    if low in SPECIAL_NAMES:
        return SPECIAL_NAMES[low]
    # Clean fallback
    clean = raw_name.replace("-Showcase", "").replace("_", " ").replace("-", " ").strip()
    return clean.title()

def generate_table(repos):
    rows = []
    rows.append("| Project | Tech Core | Focus & Engineering Highlights | Live / Showcase |")
    rows.append("| :--- | :--- | :--- | :---: |")

    for repo in repos:
        name = repo["name"]
        display_name = get_clean_name(name)
        emoji = choose_emoji(name, repo.get("topics", []))
        html_url = repo["html_url"]
        homepage = repo.get("homepage")

        tech_core = format_tech_core(repo)

        description = repo.get("description")
        if not description or not description.strip():
            description = get_repo_readme_summary(name)
        else:
            description = truncate_text(description, 115)

        if homepage and homepage.startswith("http"):
            link_cell = f"[Live App]({homepage})"
        else:
            link_cell = f"[Showcase]({html_url})"

        project_cell = f"{emoji} **[{display_name}]({html_url})**"
        rows.append(f"| {project_cell} | {tech_core} | {description} | {link_cell} |")

    return "\n".join(rows)

def update_readme():
    print("Fetching repositories...")
    repos = fetch_json(API_URL)

    filtered = []
    for r in repos:
        if r.get("fork", False) or r.get("archived", False):
            continue
        if r["name"].lower() == GITHUB_USERNAME.lower():
            continue
        filtered.append(r)

    top_3 = filtered[:3]
    table_markdown = generate_table(top_3)

    with open(README_PATH, "r", encoding="utf-8") as f:
        readme_content = f.read()

    pattern = re.compile(
        f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        re.DOTALL
    )

    new_section = f"{START_MARKER}\n{table_markdown}\n{END_MARKER}"

    if not pattern.search(readme_content):
        print("Markers not found in README.md!")
        return False

    updated_content = pattern.sub(new_section, readme_content)

    if updated_content == readme_content:
        print("README is already up to date. No changes made.")
        return False

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print("README.md successfully updated with latest projects!")
    return True

if __name__ == "__main__":
    update_readme()
