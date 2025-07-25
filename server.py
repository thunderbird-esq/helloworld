import sys
import subprocess
import base64
import ipaddress
import queue
import concurrent.futures
from flask import Flask, request, Response, stream_with_context

app = Flask(__name__)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json(silent=True) or {}
    ip_input = (data.get('ip') or '').strip()
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

    def generate():
        q = queue.Queue()

        def run_scan(target_ip):
            process = subprocess.Popen(
                [sys.executable, '-u', 'CamXploit.py'],
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
                q.put(f"{target_ip}: Failed to send input: {e}")
                process.kill()
                q.put(None)
                return

            for line in iter(process.stdout.readline, ''):
                q.put(f"{target_ip}: {line.rstrip()}")
            process.stdout.close()
            process.wait()
            q.put(None)

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(targets), 4)) as executor:
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
                yield f'data: {item}\n\n'

        yield 'event: end\ndata: done\n\n'

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
            'ffmpeg',
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
    app.run(host='0.0.0.0', port=5000, threaded=True)
