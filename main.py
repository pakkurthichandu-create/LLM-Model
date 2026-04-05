# 📦 1. Install Dependencies (NOW INCLUDING ZSTD)
print("📦 1. Installing zstd and Ollama...")
!apt-get update -qq > /dev/null
!apt-get install -y -qq zstd > /dev/null
!curl -fsSL https://ollama.com/install.sh | sh

import shutil
if shutil.which("ollama"):
    print("✅ Ollama installed successfully!")
else:
    print("❌ Ollama installation failed. Please check internet settings.")

!pip install -q fastapi uvicorn httpx python-dotenv tqdm
!npm install -g localtunnel > /dev/null

import subprocess, time, os, threading

# 🚀 2. Start Ollama Server
print("\n🚀 2. Starting Ollama Server...")
def run_ollama():
    subprocess.run(["/usr/local/bin/ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

threading.Thread(target=run_ollama, daemon=True).start()
time.sleep(15) 

# 📥 3. Pull DeepSeek-R1 (8B)
print("\n📥 3. Pulling DeepSeek-R1 8B (approx 5GB)...")
!ollama pull deepseek-r1:8b

# 🔥 4. Create main.py (Now with LIVE THINKING SUPPORT)
print("\n🔥 4. Creating FastAPI Service...")
with open("main.py", "w") as f:
    f.write(r'''
import json, os, httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/v1/chat")
async def chat(request: Request):
    data = await request.json()
    async def event_generator():
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", "http://localhost:11434/api/chat", json={
                "model": data.get("model", "deepseek-r1:8b"),
                "messages": data.get("messages", []),
                "stream": True,
                "think": True # <--- ENABLE THINKING TRACE
            }) as response:
                async for line in response.aiter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "message" in chunk:
                            msg = chunk["message"]
                            # Capture 'thinking' or 'content'
                            thinking = msg.get("thinking", "")
                            content = msg.get("content", "")
                            
                            # Standardized payload for the frontend
                            payload = {"thinking": thinking, "content": content}
                            yield f"data: {json.dumps(payload)}\n\n"
                            
                        if chunk.get("done"):
                            yield "data: [DONE]\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/", response_class=HTMLResponse)
async def gui():
    return """
    <html>
        <head><title>Kaggle DeepSeek Chat</title>
        <style>
            body { font-family: sans-serif; max-width: 750px; margin: 40px auto; background: #eef2f7; }
            #chat { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); min-height: 450px; overflow-y: auto; }
            .msg { margin-bottom: 20px; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px; }
            .thinking { color: #666; font-style: italic; background: #f9f9f9; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #ccc; font-size: 0.9em; }
            #input-area { display: flex; margin-top: 25px; gap: 10px; }
            textarea { flex: 1; padding: 15px; border: 1px solid #ddd; border-radius: 10px; font-family: inherit; font-size: 16px; }
            button { padding: 0 30px; background: #20beff; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: bold; }
        </style></head>
        <body>
            <h2 style="text-align: center;">🚢 Kaggle DeepSeek-R1 (8B) Live</h2>
            <div id="chat"></div>
            <div id="input-area"><textarea id="prompt" rows="2" placeholder="Ask anything..."></textarea><button onclick="send()">Send</button></div>
            <script>
                async function send() {
                    const prompt = document.getElementById('prompt').value;
                    if(!prompt) return;
                    document.getElementById('prompt').value = '';
                    const chat = document.getElementById('chat');
                    chat.innerHTML += '<div class="msg"><b>You:</b> ' + prompt + '</div>';
                    
                    const responseDiv = document.createElement('div');
                    responseDiv.className = 'msg';
                    responseDiv.innerHTML = '<b>DeepSeek:</b><div class="thinking" style="display:none"></div><span class="content"></span>';
                    chat.appendChild(responseDiv);
                    
                    const thinkDiv = responseDiv.querySelector('.thinking');
                    const contentSpan = responseDiv.querySelector('.content');
                    
                    const resp = await fetch('/v1/chat', {
                        method: 'POST',
                        body: JSON.stringify({ messages: [{role: 'user', content: prompt}] })
                    });
                    const reader = resp.body.getReader();
                    const decoder = new TextDecoder();
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        const text = decoder.decode(value);
                        text.split('\\n').forEach(line => {
                            if (line.startsWith('data: ')) {
                                const dataText = line.slice(6);
                                if (dataText !== '[DONE]') {
                                    try { 
                                        const json = JSON.parse(dataText);
                                        if(json.thinking) {
                                            thinkDiv.style.display = 'block';
                                            thinkDiv.innerText += json.thinking;
                                        }
                                        if(json.content) {
                                            contentSpan.innerText += json.content;
                                        }
                                    } catch(e) {}
                                }
                            }
                        });
                    }
                }
            </script>
        </body></html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')

# 🚀 5. Start FastAPI server
print("\n🚀 5. Starting FastAPI Server (Port 8000)...")
threading.Thread(target=lambda: os.system("python3 main.py"), daemon=True).start()
time.sleep(5)

# 🔑 6. Output IP for Tunnel Password
print("\n" + "="*40)
print("🔑 COPY THIS IP (TUNNEL PASSWORD):")
!curl -s ipv4.icanhazip.com
print("="*40)

# 🌍 7. Start Public Tunnel
print("\n🌍 STARTING PUBLIC URL...")
!lt --port 8000
