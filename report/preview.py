"""Loopback-only preview of explicitly public files; no directory/DB access."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
PUBLIC_PATHS = {
    "/index.html", "/metodika.html", "/assets/vysledky.css",
    "/assets/vysledky.js", "/FB Banner.png",
    "/assets/fonts/sofia-sans-latin.woff2",
    "/assets/fonts/sofia-sans-latin-ext.woff2",
    "/assets/fonts/Sofia-Sans-LICENSE.txt",
}


class PublicHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = unquote(urlsplit(self.path).path)
        if path == "/":
            self.path = "/index.html"
            path = "/index.html"
        if path not in PUBLIC_PATHS:
            self.send_error(404, "Only public report files are available")
            return None
        return super().send_head()

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    handler = partial(PublicHandler, directory=str(ROOT))
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
        print(f"Public report preview: http://127.0.0.1:{args.port}/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()