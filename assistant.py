import os
import hashlib
import json
import numpy as np
import requests
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else genai.Client()

class OptiBotAssistant:
    def __init__(self, vector_db_path="vector_db.json"):
        self.vector_db_path = vector_db_path
        self.model_name = "gemini-3.5-flash"
        self.fallback_model_name = "gemini-3.1-flash-lite"
        self.embedding_model_name = "gemini-embedding-2"
        self.db = self.load_db()

    def load_db(self):
        if os.path.exists(self.vector_db_path):
            with open(self.vector_db_path, "r") as f:
                return json.load(f)
        return {"hashes": {}, "chunks": []}

    def save_db(self):
        with open(self.vector_db_path, "w") as f:
            json.dump(self.db, f)

    def get_embedding(self, text):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY không tồn tại trong file .env")

        try:
            response = client.models.embed_content(
                model=self.embedding_model_name,
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
            )
            values = response.embeddings[0].values
            if values:
                return values
        except Exception as sdk_error:
            try:
                headers = {"Content-Type": "application/json"}
                payload = {
                    "content": {
                        "parts": [{"text": text}]
                    }
                }
                url_fallback = f"https://generativelanguage.googleapis.com/v1beta/models/{self.embedding_model_name}:embedContent?key={api_key}"
                fallback_res = requests.post(url_fallback, headers=headers, json=payload, timeout=10)
                if fallback_res.status_code == 200:
                    values = fallback_res.json().get("embedding", {}).get("values")
                    if values:
                        return values
            except Exception:
                pass

            raise RuntimeError(f"Không thể lấy Embedding từ Google API: {sdk_error}")

    def chunk_text(self, text, max_chars=1000, overlap=200):
        chunks = []
        start = 0
        while start < len(text):
            end = start + max_chars
            chunks.append(text[start:end])
            start += (max_chars - overlap)
        return chunks

    def index_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        filename = os.path.basename(file_path)
        
        if self.db["hashes"].get(filename) == file_hash:
            return "skipped"
            
        status = "updated" if filename in self.db["hashes"] else "added"
        self.db["chunks"] = [c for c in self.db["chunks"] if c["source"] != filename]
        
        article_url = "https://support.optisigns.com"
        for line in content.split("\n"):
            if "Article URL:" in line:
                article_url = line.replace("Article URL:", "").strip()
                break
        
        chunks = self.chunk_text(content)
        for chunk in chunks:
            try:
                embedding = self.get_embedding(chunk)
            except Exception as e:
                print(f"⚠️ Bỏ qua chunk lỗi cho {filename}: {e}")
                continue

            self.db["chunks"].append({
                "source": filename,
                "url": article_url, 
                "text": chunk,
                "embedding": embedding
            })
            
        self.db["hashes"][filename] = file_hash
        return status

    def retrieve_context(self, query, top_k=3):
        if not self.db["chunks"]:
            return ""
            
        query_emb = self.get_embedding(query)
        
        scores = []
        for chunk in self.db["chunks"]:
            dot_product = np.dot(query_emb, chunk["embedding"])
            norm_q = np.linalg.norm(query_emb)
            norm_c = np.linalg.norm(chunk["embedding"])
            score = dot_product / (norm_q * norm_c)
            scores.append((score, chunk["text"], chunk.get("url", "https://support.optisigns.com")))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        
        context_blocks = []
        for score, text, url in scores[:top_k]:
            block = f"Article URL: {url}\nContent:\n{text}"
            context_blocks.append(block)
            
        return "\n\n--- Context Section ---\n".join(context_blocks)

    def ask_optibot(self, query):
        context = self.retrieve_context(query)
        
        system_prompt = (
            "You are OptiBot, the customer-support bot for OptiSigns.com.\n"
            "• Tone: helpful, factual, concise.\n"
            "• Only answer using the uploaded docs.\n"
            "• Max 5 bullet points; else link to the doc.\n"
            "• Cite up to 3 \"Article URL:\" lines per reply."
        )
        
        prompt = f"{system_prompt}\n\nContext information:\n{context}\n\nUser Question: {query}"
        
        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            try:
                response = client.models.generate_content(
                    model=self.fallback_model_name,
                    contents=prompt
                )
                return response.text
            except Exception as fallback_error:
                return f"Không thể tạo câu trả lời từ Gemini API. Lỗi chính: {e}. Lỗi dự phòng: {fallback_error}"