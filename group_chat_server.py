#!/usr/bin/env python3
"""group_chat_server.py — Proper group chat web app. Rob types, Gemini pastes, Hermes auto-responds."""

import http.server, json, os, re, subprocess, time, urllib.parse

PROJECT = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(PROJECT, "group_chat.md")
PORT = 8082

def nzst():
    return time.strftime("%Y-%m-%d %H:%M:%S NZST", time.gmtime(time.time() + 43200))

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>☯ Group Chat</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0d0d0d;color:#e0e0e0;font-family:'Segoe UI',system-ui,sans-serif;display:flex;flex-direction:column;height:100vh}
#header{text-align:center;padding:14px;border-bottom:1px solid #2a2a2a;flex-shrink:0}
#header h1{font-size:1.2em}
#header .rob{color:#4fc3f7} #header .hermes{color:#ce93d8} #header .gemini{color:#81c784}
#chat{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px}
.msg{display:flex;gap:10px;animation:fadeIn .2s}
@keyframes fadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}
.av{width:32px;height:32px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}
.av.rob{background:#1565c0} .av.hermes{background:#6a1b9a} .av.gemini{background:#2e7d32}
.bub{flex:1}
.bub .hdr{display:flex;gap:8px;align-items:baseline;margin-bottom:2px}
.bub .nm{font-weight:700;font-size:.85em}
.nm.rob{color:#4fc3f7} .nm.hermes{color:#ce93d8} .nm.gemini{color:#81c784}
.bub .tm{font-size:.65em;color:#555}
.bub .txt{line-height:1.5;font-size:.9em;white-space:pre-wrap;word-break:break-word}
#inputbar{display:flex;gap:8px;padding:12px 16px;border-top:1px solid #2a2a2a;flex-shrink:0;background:#0d0d0d}
#inputbar input{flex:1;background:#1a1a1a;border:1px solid #333;border-radius:8px;padding:10px 14px;color:#e0e0e0;font-size:.9em;outline:none}
#inputbar input:focus{border-color:#4fc3f7}
#inputbar button{background:#1565c0;border:none;border-radius:8px;padding:10px 18px;color:#fff;font-weight:600;cursor:pointer;font-size:.85em}
#inputbar button:hover{background:#1976d2}
#gemini-panel{display:none;position:fixed;bottom:70px;left:50%;transform:translateX(-50%);width:90%;max-width:600px;background:#1a1a1a;border:1px solid #2e7d32;border-radius:12px;padding:14px;z-index:10}
#gemini-panel textarea{width:100%;height:120px;background:#111;border:1px solid #333;border-radius:8px;padding:10px;color:#e0e0e0;font-size:.85em;resize:vertical;outline:none;margin-bottom:8px}
#gemini-panel textarea:focus{border-color:#81c784}
#gemini-panel .btns{display:flex;gap:8px;justify-content:flex-end}
#gemini-panel button{padding:8px 16px;border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:.8em}
.btn-send{background:#2e7d32;color:#fff} .btn-cancel{background:#333;color:#aaa}
#status{text-align:center;font-size:.7em;color:#444;padding:6px;flex-shrink:0}
#gemini-btn{background:#2e7d32;border:none;border-radius:8px;padding:10px;color:#fff;font-weight:600;cursor:pointer;font-size:.75em;white-space:nowrap}
</style>
</head>
<body>
<div id="header"><h1><span class="rob">Rob</span> &middot; <span class="hermes">Hermes</span> &middot; <span class="gemini">Gemini</span></h1></div>
<div id="chat"><div style="text-align:center;color:#555;padding:40px">loading...</div></div>
<div id="gemini-panel">
  <textarea id="gemini-input" placeholder="Paste Gemini&apos;s message here..."></textarea>
  <div class="btns">
    <button class="btn-cancel" onclick="closeGemini()">Cancel</button>
    <button class="btn-send" onclick="sendGemini()">Send as Gemini</button>
  </div>
</div>
<div id="inputbar">
  <input id="msg-input" placeholder="Type as Rob..." autofocus>
  <button id="gemini-btn" onclick="openGemini()">&#128203; Gemini</button>
  <button onclick="sendRob()">Send</button>
</div>
<div id="status">connecting...</div>
<script>
let sending=false;
function escape(t){const d=document.createElement('div');d.textContent=t;return d.innerHTML}
function render(t){
  t=t.replace(/```(\w*)\n?([\s\S]*?)```/g,(m,l,c)=>'<pre><code>'+escape(c)+'</code></pre>');
  t=t.replace(/`([^`]+)`/g,'<code>$1</code>');
  t=t.replace(/\n/g,'<br>');
  return t
}
async function load(){
  try{
    const r=await fetch('/api/messages?_='+Date.now());
    const data=await r.json();
    const chat=document.getElementById('chat');
    if(data.messages.length===0){
      chat.innerHTML='<div style="text-align:center;color:#555;padding:40px">no messages yet</div>';
      return
    }
    let html='';
    for(const m of data.messages){
      const t=m.speaker.toLowerCase();
      html+='<div class="msg"><div class="av '+t+'">'+(t==='rob'?'R':t==='hermes'?'H':'G')+'</div><div class="bub"><div class="hdr"><span class="nm '+t+'">'+escape(m.speaker)+'</span><span class="tm">'+escape(m.time)+'</span></div><div class="txt">'+render(m.body)+'</div></div></div>'
    }
    chat.innerHTML=html;
    chat.scrollTop=chat.scrollHeight;
    const last=data.messages[data.messages.length-1];
    document.getElementById('status').textContent=data.messages.length+' msgs &middot; last: '+last.speaker+' &middot; '+(data.watcher_running?'watcher live':'watcher dead');
  }catch(e){
    document.getElementById('status').textContent='error: '+e.message
  }
}
async function sendRob(){
  if(sending)return;
  const inp=document.getElementById('msg-input');
  const txt=inp.value.trim();
  if(!txt)return;
  sending=true;
  try{
    await fetch('/api/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({speaker:'Rob',text:txt})});
    inp.value='';
    await load()
  }catch(e){document.getElementById('status').textContent='send error: '+e.message}
  sending=false
}
async function sendGemini(){
  const inp=document.getElementById('gemini-input');
  const txt=inp.value.trim();
  if(!txt)return;
  sending=true;
  try{
    await fetch('/api/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({speaker:'Gemini',text:txt})});
    inp.value='';
    closeGemini();
    await load()
  }catch(e){document.getElementById('status').textContent='send error: '+e.message}
  sending=false
}
function openGemini(){document.getElementById('gemini-panel').style.display='block';document.getElementById('gemini-input').focus()}
function closeGemini(){document.getElementById('gemini-panel').style.display='none';document.getElementById('gemini-input').value=''}
document.getElementById('msg-input').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendRob()}});
setInterval(load,3000);
load()
</script>
</body>
</html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == '/api/messages':
            self._messages()
        elif p.path == '/':
            self._html()
        else:
            self.send_error(404)
    def do_POST(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == '/api/send':
            self._send()
        else:
            self.send_error(404)
    def _html(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML.encode())
    def _messages(self):
        msgs = []
        if os.path.exists(FILE):
            with open(FILE, encoding='utf-8', errors='replace') as f:
                content = f.read()
            sections = re.split(r'\n---+\n', content)
            for sec in sections:
                sec = sec.strip()
                if not sec:
                    continue
                m = re.match(r'^##\s+(\w+)\s*\[([^\]]*)\]', sec)
                if not m:
                    continue
                body = sec[m.end():].strip()
                msgs.append({'speaker': m.group(1), 'time': m.group(2), 'body': body})
        watcher = subprocess.run(['pgrep', '-f', 'group_chat_watcher'], capture_output=True, timeout=3).returncode == 0
        data = json.dumps({'messages': msgs, 'watcher_running': watcher})
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(data.encode())
    def _send(self):
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length)
        data = json.loads(raw)
        speaker = data.get('speaker', 'Rob')
        text = data.get('text', '').strip()
        if not text:
            self.send_error(400)
            return
        ts = nzst()
        sep = '\n\n---\n\n' if os.path.exists(FILE) and os.path.getsize(FILE) > 0 else ''
        with open(FILE, 'a', encoding='utf-8') as f:
            f.write(f"{sep}## {speaker} [{ts}]\n\n{text}")
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'ok': True}).encode())
    def log_message(self, fmt, *args):
        pass

if __name__ == '__main__':
    srv = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"☯ Group Chat on http://127.0.0.1:{PORT}/")
    print(f"   Also: http://172.30.59.109:{PORT}/")
    srv.serve_forever()