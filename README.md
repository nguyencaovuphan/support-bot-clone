## Setup & Local Run

### Prerequisites
- Python 3.10+
- Gemini API Key (Free tier from AI Studio)

### Installation
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the sample environment file and add your credentials:
   ```bash
   cp .env.sample .env
   # Add your GEMINI_API_KEY to the .env file
   ```

### Execution
- **Run Sync Pipeline**: 
  ```bash
  python main.py
  ```

---

## Docker Usage
Run the pipeline in a container:
```bash
# Build
docker build -t optibot-sync .

# Run Sync
docker run --env-file .env -v ${PWD}/data:/app/data optibot-sync
```

---

## Chunking & AI Strategy
- **Chunking Strategy**: Managed automatically by Gemini's high-efficiency File Search grounding engine, which chunks and embeds document resources asynchronously.
- **Metadata Association**: Prepend article Titles and source URLs directly to the top of each Markdown file:
  ```markdown
  # Title: <Title>
  Article URL: <URL>
  ```
  This ensures that whenever the retriever fetches text chunks, the assistant has immediate access to the canonical URL and title for precise, grounded citation mapping.

---

## Automation & Scheduling
An automated sync job is configured using **GitHub Actions** to trigger daily at 00:00 UTC.
- **Run Logs**: Available under the repository's **Actions** tab.
- **Configuration**: Managed in [.github/workflows/sync.yml](.github/workflows/sync.yml).
