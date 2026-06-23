import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import feedparser
from google import genai
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# 1. Initialize Google GenAI SDK (Gemini 2.5 Flash is ideal for text categorization)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. Hardcore Framework, Tooling, & LLMOps Feeds
FEEDS = [
    "https://www.langchain.com/blog",                         # Agentic patterns & system tracing
    "https://huggingface.co/blog",                     # Tokenizers, transformers libraries, alignment setups
    "https://thegradient.pub",                            # Deep technical evaluations of model behaviors
    "https://developers.openai.com/blog",                         # API additions, schema enforcements, structured outputs
    "https://vllm.ai"                                 # High-throughput serving engine breakthroughs
    "https://www.anthropic.com/engineering",
    "https://cloud.google.com/blog/products/ai-machine-learning",
    "https://developers.googleblog.com/",
    "https://research.google/",
    "https://aws.amazon.com/blogs/machine-learning/",
    "https://cohere.com/blog",
    "https://blogs.nvidia.com/blog/tag/ai-factory/",
    "https://blogs.nvidia.com/blog/tag/inference/",
    "https://stratechery.com/"

]

collected_text = ""
for url in FEEDS:
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            collected_text += f"Title: {entry.title}\nSummary: {entry.get('summary', '')}\nLink: {entry.link}\n\n"
    except Exception as e:
        print(f"Skipping feed {url} due to error: {e}")

# 3. System Instruction + Strict Prompt to enforce an AI Engineer's perspective
prompt = f"""
You are acting as a Principal AI Infrastructure Architect filtering information for an active AI Engineer. 
Analyze the source data below and discard all high-level product releases, fundraising news, marketing catchphrases, and generic corporate updates.

Select the 4 most critical updates and group them into these three strict categories:
1. Frameworks & Agents (LangChain, LlamaIndex, Orchestration)
2. LLMOps, Infra & Serving (vLLM, Quantization, Evaluation, Tracing)
3. Model Architecture & Fine-Tuning (Context windows, Weights extensions, Post-training alignment)
4. AI Market Landscape & Interesting Use Cases

Format your response strictly using clean Markdown headers (###), bullet points, and hyperlinks. Do NOT wrap it in a code block.
For each selected update:
For each selected update:
- Provide a bold title linked directly to its source URL.
- Write a highly technical 2-sentence breakdown detailing the specific mechanism and its engineering implications.

Data:
{collected_text}
"""

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt
)
markdown_summary = response.text

with open("digest.md", "w", encoding="utf-8") as f:
    f.write("## 🛠️ Weekly AI Engineering & Frameworks Briefing\n\n")
    f.write(markdown_summary)

print("Digest successfully generated.")
