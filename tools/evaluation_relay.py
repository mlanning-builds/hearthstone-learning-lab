"""Owner-started authenticated LAN queue. Carries evaluation snapshots, never optimizer state."""
import argparse, hashlib, hmac, json, os, re, threading, time, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
QUEUE=ROOT/'runs/remote_evaluation'
ID=re.compile(r'^[a-f0-9]{64}$')

def atomic(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix('.partial')
 temp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');temp.replace(path)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--start',action='store_true');parser.add_argument('--port',type=int,default=8766);parser.add_argument('--queue',type=Path,default=QUEUE);parser.add_argument('--bind',default='0.0.0.0');args=parser.parse_args()
 global_queue=args.queue
 # Explicit test queues can be isolated from the owner's production outbox.
 queue=global_queue
 if not args.start:print('Prepared only. Owner must start the relay.');return
 config=json.loads((queue/'connection.json').read_text());lock=threading.Lock()
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def send(self,status,value):
   raw=json.dumps(value).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  def authorized(self):return hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+config['token'])
  def do_GET(self):
   if not self.authorized():self.send(403,{'error':'authorization'});return
   if self.path=='/health':self.send(200,{'protocol':'frozen-evaluation-v1'});return
   if self.path=='/next':
    with lock:
     for folder in sorted((queue/'jobs').glob('*'),key=lambda p:p.stat().st_mtime_ns):
      if not ID.fullmatch(folder.name) or not (folder/'job.json').exists() or (folder/'result.json').exists() or (folder/'superseded.json').exists():continue
      meta=json.loads((folder/'job.json').read_text())
      predecessor=meta.get('predecessor')
      if predecessor and not (queue/'jobs'/predecessor/'result.json').exists():continue
      lease=folder/'lease.json'
      if lease.exists():
       previous=json.loads(lease.read_text())
       if time.time()-previous['time']<1800 and previous.get('worker')!=self.headers.get('X-Worker-ID',''):continue
      atomic(lease,{'time':time.time(),'worker':self.headers.get('X-Worker-ID','')});self.send(200,meta);return
    self.send(200,None);return
   parts=self.path.strip('/').split('/')
   if len(parts)==2 and parts[0]=='payload' and ID.fullmatch(parts[1]):
    path=queue/'jobs'/parts[1]/'payload.pt'
    if not path.exists():self.send(404,{'error':'missing job'});return
    self.send_response(200);self.send_header('Content-Length',str(path.stat().st_size));self.end_headers()
    with path.open('rb') as stream:
     import shutil;shutil.copyfileobj(stream,self.wfile)
    return
   if len(parts)==2 and parts[0]=='result' and ID.fullmatch(parts[1]):
    path=queue/'jobs'/parts[1]/'result.json';self.send(200,json.loads(path.read_text()) if path.exists() else None);return
   self.send(404,{'error':'unknown endpoint'})
  def do_POST(self):
   if not self.authorized():self.send(403,{'error':'authorization'});return
   parts=self.path.strip('/').split('/')
   if len(parts)!=2 or not ID.fullmatch(parts[1]):self.send(404,{});return
   folder=queue/'jobs'/parts[1]
   if not (folder/'job.json').exists():self.send(404,{});return
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<=32*1024*1024:self.send(413,{});return
   value=json.loads(self.rfile.read(length))
   with lock:
    if parts[0]=='heartbeat':atomic(folder/'lease.json',{'time':time.time(),'worker':self.headers.get('X-Worker-ID','')});self.send(200,{'ok':True});return
    if parts[0]=='result':
     from tools.remote_evaluation_worker import validate_result
     meta=json.loads((folder/'job.json').read_text())
     try:validate_result(meta,value)
     except (ValueError,KeyError,TypeError) as error:self.send(400,{'error':str(error)});return
     if not (folder/'result.json').exists():atomic(folder/'result.json',value)
     if meta.get('golden_cases_sha256'):
      atomic(queue/'verified-worker.json',dict(compatibility=meta['report_metadata']['compatibility'],job_id=parts[1],verified_at=time.time()))
     self.send(200,{'ok':True});return
   self.send(404,{})
 server=ThreadingHTTPServer((args.bind,args.port),Handler)
 print('Evaluation relay ready on port '+str(args.port),flush=True)
 try:server.serve_forever()
 finally:server.server_close()

if __name__=='__main__':main()
