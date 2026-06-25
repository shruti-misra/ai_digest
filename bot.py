import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import feedparser
from google import genai
from dotenv import load_dotenv
from datetime import datetime
from email_sender import EmailSender

# Load the .env file
load_dotenv()

# 1. Initialize Google GenAI SDK (Gemini 2.5 Flash is ideal for text categorization)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. Feeds - Mix of RSS where available + site URLs for Gemini to search
RSS_FEEDS = [
    "https://www.langchain.com/blog/rss.xml",
    "https://huggingface.co/blog/feed.xml",
    "https://developers.openai.com/blog/rss.xml",
    "https://www.anthropic.com/engineering/rss.xml",
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://cohere.com/blog/rss.xml",
    "https://bair.berkeley.edu/blog/feed.xml",
    "https://medium.com/feed/airbnb-engineering",
    "https://machinelearning.apple.com/rss.xml",
    "https://www.databricks.com/blog/feed",
    "https://www.deepmind.com/blog/rss.xml",
    "https://openai.com/blog/rss",
    "http://labs.spotify.com/feed/",
    "https://feeds.feedburner.com/martinkl?format=xml",
    
    
]

SITE_URLS = [
    "https://thegradient.pub",
    "https://vllm.ai/blog",
    "https://cloud.google.com/blog/products/ai-machine-learning",
    "https://developers.googleblog.com/",
    "https://research.google/blog/",
    "https://blogs.nvidia.com/blog/tag/inference/",
    "https://stratechery.com/",
    "https://research.netflix.com/archive"
]

collected_text = ""

# Parse actual RSS feeds
for url in RSS_FEEDS:
    try:
        feed = feedparser.parse(url)
        if feed.entries:
            for entry in feed.entries[:5]:
                collected_text += (
                    f"Title: {entry.title}\n"
                    f"Summary: {entry.get('summary', '')[:500]}\n"
                    f"Link: {entry.link}\n"
                    f"Published: {entry.get('published', 'N/A')}\n\n"
                )
        else:
            # Still log the site so Gemini knows to search it
            collected_text += f"[RSS unavailable — search recent posts at: {url}]\n\n"
    except Exception as e:
        collected_text += f"[Error fetching {url}: {e} — search manually]\n\n"

# For non-RSS sites, tell Gemini to search them directly
site_search_instruction = "\n".join(
    f"- Search for the latest technical posts at: {url}" for url in SITE_URLS
)

# 3. Refined Prompt
prompt = f"""
You are a Principal AI Infrastructure Architect filtering a daily briefing for a senior AI Engineer.

## Your Tasks

### Step 1 — Use the RSS data below as your primary source
Extract any articles from the structured feed data. Retain the exact article URL from the `Link:` field.

### Step 2 — Actively search these sites for articles published in the last 7 days
{site_search_instruction}

For each site, retrieve the 1–2 most technically substantive posts. You MUST include the direct article URL (not the homepage).

### Step 3 — Filter ruthlessly
Discard: product launches with no engineering depth, fundraising news, marketing copy, generic "AI is transforming X" narratives, executive interviews.
Keep: implementation details, benchmark results, architecture changes, new APIs with schema-level changes, serving/inference improvements, training recipes.

### Step 4 — Output exactly this format in clean Markdown (no code block wrapper)

---

### 1. Frameworks & Agents
- **[Article Title](direct-article-url)** — `Source` | `Date`
  Technical breakdown: [2 sentences explaining the specific mechanism and its engineering implication.]

### 2. LLMOps, Infra & Serving
- **[Article Title](direct-article-url)** — `Source` | `Date`
  Technical breakdown: [2 sentences.]

### 3. Model Architecture & Fine-Tuning
- **[Article Title](direct-article-url)** — `Source` | `Date`
  Technical breakdown: [2 sentences.]

### 4. AI Market Landscape & Interesting Use Cases
- **[Article Title](direct-article-url)** — `Source` | `Date`
  Technical breakdown: [2 sentences.]

---

Rules:
- Every bullet MUST have a working direct article URL — never link to a homepage.
- 3–5 bullets per category.
- If a category has no qualifying articles this cycle, write: `> No high-signal updates this cycle.`
- Do not hallucinate URLs. If unsure of the exact URL, write the title and note: `[URL unverified]`.

## RSS Feed Data (use exact URLs from Link: fields):
{collected_text}
"""


response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt
)
markdown_summary = response.text

# At the end of bot.py, after response = client.models.generate_content(...)

digest = response.text

timestamp = datetime.now().strftime("%Y-%m-%d")
subject = f"Digest — {timestamp}"

email = EmailSender(subject, digest)
email.send_email()

