import os
import sys
import sqlcoder
import subprocess

USAGE_STRING = """
Usage: sqlcoder <command>

Available commands:
    sqlcoder launch
    sqlcoder serve-webserver
    sqlcoder serve-static
"""

home_dir = os.path.expanduser("~")

def main():
    if len(sys.argv) < 2:
        print(USAGE_STRING)
        sys.exit(1)
    if sys.argv[1] == "launch":
        launch()
    elif sys.argv[1] == "serve-webserver":
        serve_webserver()
    elif sys.argv[1] == "serve-static":
        serve_static()
    else:
        print(USAGE_STRING)
        sys.exit(1)

def serve_webserver():
    from sqlcoder.serve import app
    import uvicorn
    uvicorn.run(app, host="localhost", port=1235)


def serve_static():
    import http.server
    import socketserver
    import webbrowser

    port = 8002
    directory = os.path.join(sqlcoder.__path__[0], "static")

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(
                *args,
                directory=directory,
                **kwargs
            )

    webbrowser.open(f"http://localhost:{port}")
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Static folder is {directory}")
        httpd.extension_maps = {".html": "text/html", "": "text/html"}
        httpd.serve_forever()

def launch():
    print("Starting SQLCoder server...")
    static_process = subprocess.Popen(["sqlcoder", "serve-static"])
    
    print("Serving static server...")
    webserver_process = subprocess.Popen(["sqlcoder", "serve-webserver"])
    print("Press Ctrl+C to exit.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Exiting...")
        static_process.terminate()
        webserver_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()