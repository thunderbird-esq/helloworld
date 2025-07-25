import os
import sys
import subprocess
import base64
import ipaddress
import queue
import concurrent.futures
import json
import re
from flask import Flask, request, Response, stream_with_context
from dotenv import load_dotenv

load_dotenv()

CAMXPLOIT_PATH = os.getenv("CAMXPLOIT_PATH", "CamXploit.py")
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
HOST = os.getenv("FLASK_HOST", "0.0.0.0")
PORT = int(os.getenv("FLASK_PORT", "5000"))

app = Flask(__name__)

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        ip_input = (data.get('ip') or '').strip()
    else:
        ip_input = (request.args.get('ip') or '').strip()
    if not ip_input:
        return {"error": "ip required"}, 400

    try:
        if '/' in ip_input:
            network = ipaddress.ip_network(ip_input, strict=False)
            targets = [str(h) for h in network.hosts()] or [str(network.network_address)]
        else:
            ipaddress.ip_address(ip_input)
            targets = [ip_input]
    except ValueError:
        return {"error": "invalid ip"}, 400

    def parse_line(line):
        line = line.strip()
        try:
            url_match = re.search(r'(https?|rtsp|rtmp)://\S+', line)
            if url_match:
                event = {"type": "finding", "url": url_match.group(0), "message": line}
                port_match = re.search(r'port\s*(\d+)', line, re.I)
                if port_match:
                    event["port"] = int(port_match.group(1))
            else:
                port_match = re.search(r'port\s*(\d+)', line, re.I)
                if port_match:
                    event = {"type": "finding", "port": int(port_match.group(1)), "message": line}
                else:
                    event = {"type": "status", "message": line}
            if "scan completed" in line.lower():
                event.setdefault("type", "status")
                event["complete"] = True
        except Exception as e:
            event = {"type": "error", "message": f"parse error: {e}", "raw": line}
        return event

    def generate():
        q = queue.Queue()

        def run_scan(target_ip):
            process = subprocess.Popen(
                [sys.executable, '-u', CAMXPLOIT_PATH],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            try:
                process.stdin.write(target_ip + '\n')
                process.stdin.flush()
            except Exception as e:
                q.put({"ip": target_ip, "type": "error", "message": f"send failed: {e}"})
                process.kill()
                q.put(None)
                return

            for line in iter(process.stdout.readline, ''):
                event = parse_line(line)
                event["ip"] = target_ip
                q.put(event)

            process.stdout.close()
            process.wait()
            q.put({"ip": target_ip, "type": "complete"})
            q.put(None)

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(targets), MAX_WORKERS)) as executor:
            for ip_addr in targets:
                executor.submit(run_scan, ip_addr)

            finished = 0
            while finished < len(targets):
                try:
                    item = q.get(timeout=0.1)
                except queue.Empty:
                    continue
                if item is None:
                    finished += 1
                    continue
                yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"

        yield "data: {\"type\": \"end\"}\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    }
    return Response(stream_with_context(generate()), mimetype='text/event-stream', headers=headers)


@app.route('/stream/<stream_url_b64>')
def stream(stream_url_b64):
    """Transcode a stream URL to HLS using FFmpeg and stream the playlist."""
    # Decode the base64-encoded URL
    try:
        padding = '=' * (-len(stream_url_b64) % 4)
        stream_url = base64.urlsafe_b64decode(stream_url_b64 + padding).decode('utf-8')
    except Exception:
        return {"error": "invalid stream url"}, 400

    def generate_hls():
        cmd = [
            FFMPEG_PATH,
            '-i', stream_url,
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-f', 'hls',
            'pipe:1'
        ]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)
        try:
            for chunk in iter(lambda: process.stdout.read(8192), b''):
                if not chunk:
                    break
                yield chunk
        finally:
            process.stdout.close()
            process.kill()

    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    }
    return Response(stream_with_context(generate_hls()), mimetype='application/vnd.apple.mpegurl', headers=headers)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, threaded=True)
