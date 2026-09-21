"""Local preview server. A larger queue accommodates parallel browser checks."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class PreviewServer(ThreadingHTTPServer):
    request_queue_size = 128


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1] / 'docs'
    handler = partial(SimpleHTTPRequestHandler, directory=str(root))
    with PreviewServer(('127.0.0.1', 8000), handler) as server:
        print('Preview: http://127.0.0.1:8000', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
