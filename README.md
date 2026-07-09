## Setup & Local Run

### Prerequisites
- **Python**: 3.10+
- **Gemini API Key**: Obtain a free-tier API key from [Google AI Studio](https://aistudio.google.com/).

### Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/nguyencaovuphan/support-bot-clone.git
   cd support-bot-clone
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables**:
   ```bash
   cp .env.sample .env
   ```
   Open the `.env` file and insert your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

### Execution
Run the complete sync pipeline locally. This command automatically triggers the web scraper, calculates differences to perform delta-only updates, indexes new/modified articles into the vector store, and performs a sanity check query:
```bash
python main.py
```

---

## Docker Usage

The entire environment is fully containerized for seamless cloud deployment.

1. **Build the Docker Image**:
   ```bash
   docker build -t optibot-sync .
   ```
2. **Run the Container**:
   Pass your local environment configurations to run the daily synchronization pipeline:
   ```bash
   docker run --env-file .env optibot-sync
   ```

---

## Chunking & Vector Database Strategy

### 1. Ingestion & Grounding Metadata
- Scraped HTML articles are parsed using `BeautifulSoup` to strip navigation/ads and convert raw content to clean Markdown structure.
- To ensure accurate citations, the scraper prepends metadata directly to the top of each Markdown file:
  ```markdown
  --- 
  Title: <Article Title>
  Article URL: <Source URL>
  ---
  ```
  This strategy guarantees that whenever a text segment is retrieved, the chatbot has direct access to its source title and canonical URL.

### 2. Character-Based Sliding Window Chunking
- **Chunk Size**: `1000` characters
- **Overlap**: `200` characters
- This sliding window ensures semantic context is preserved across splits, preventing key instructions (e.g. step-by-step setup guides) from being cut off.

### 3. Vector Database & Semantic Retrieval
- **Embeddings**: Generated using the `gemini-embedding-2` model via Google GenAI SDK (with automated HTTP fallback).
- **Storage**: Indexes are kept in a local lightweight database (`vector_db.json`) storing file hashes, raw text chunks, and embedding coordinates.
- **Retrieval**: Leverages cosine similarity via `numpy` to retrieve the top `3` most relevant contexts based on the user's query vector.

---

## Daily Job & Automation

An automated sync job runs daily using **GitHub Actions** to keep the vector database up to date.
- **Delta Sync Algorithm**: Uses MD5 hashing to check if articles have been modified. It only processes the delta (**added** or **updated** articles) and skips unchanged content, optimizing performance and API quota.
- **Log Outputs**: Writes the status summary to `last_run_artifact.log`.
- **Live Run Logs**:
  🔗 [Railway Logs](https://railway.com/project/d9c20929-2d22-40be-a80d-2407c60f3673/logs?environmentId=a5f54cde-62a4-422e-b818-df629a4b6769)

---

## Chatbot Sanity Check

![OptiBot Sanity Check Screenshot](Screenshot%202026-07-09%20111538.png)
