import sys
import subprocess
import base64
from flask import Flask, request, Response, stream_with_context

app = Flask(__name__)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json(silent=True) or {}
    ip = data.get('ip')
    if not ip:
        return {"error": "ip required"}, 400

    def generate():
        process = subprocess.Popen(
            [sys.executable, '-u', 'CamXploit.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        # send the ip address followed by newline
        try:
            process.stdin.write(ip + '\n')
            process.stdin.flush()
        except Exception as e:
            yield f'data: Failed to send input: {e}\n\n'
            process.kill()
            return
        for line in iter(process.stdout.readline, ''):
            yield f'data: {line.rstrip()}\n\n'
        process.stdout.close()
        process.wait()
        # notify client that the scan is finished
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
