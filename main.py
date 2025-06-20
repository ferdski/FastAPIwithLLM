from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
import requests
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize OpenAI client
client = OpenAI()

import sys
print(sys.executable)

# Define request model
class Query(BaseModel):
    prompt: str
    model: str = "openai"  # Options: "openai", "ollama"

# Define /ask endpoint
@app.post("/ask")
async def ask(query: Query):
    try:
        if query.model == "openai":
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": query.prompt}
                ]
            )
            return {"response": response.choices[0].message.content.strip()}

        elif query.model == "ollama":
            ollama_response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "mistral", "prompt": query.prompt, "stream": False}
            )
            if ollama_response.status_code == 200:
                return {"response": ollama_response.json().get("response", "No response")}
            else:
                return {"error": f"Ollama request failed with status code {ollama_response.status_code}"}

        else:
            return {"error": "Invalid model specified. Use 'openai' or 'ollama'."}

    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    import uvicorn                       # ← be sure to import it
    uvicorn.run(
        "main:app",                      # dotted-path string is safest
        host="0.0.0.0",
        port=8000,
        reload=True                      # same as  --reload  on CLI
    )