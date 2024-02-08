import os
import sys
import sqlcoder
import subprocess
from huggingface_hub import snapshot_download, hf_hub_download

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
    home_dir = os.path.expanduser("~")
    defog_path = os.path.join(home_dir, ".defog")
    if not os.popen("lspci | grep -i nvidia").read():
        # not a GPU machine
        filepath = os.path.join(home_dir, ".defog", "sqlcoder-7b-q5_k_m.gguf")
        if not os.path.exists(filepath):
            print(
                "Downloading the SQLCoder-7b-2 GGUF file. This is a ~5GB file and may take a long time to download. But once it's downloaded, it will be saved on your machine and you won't have to download it again."
            )
            hf_hub_download(repo_id="defog/sqlcoder-7b-2", filename="sqlcoder-7b-q5_k_m.gguf", local_dir=defog_path)
    else:
        # check if the huggingface model is already downloaded from hub. If not, download it
        from huggingface_hub import snapshot_download
        print(
            "Downloading the SQLCoder-7b-2 model. This is a ~14GB file and may take a long time to download. But once it's downloaded, it will be saved on your machine and you won't have to download it again."
        )
        _ = snapshot_download("defog/sqlcoder-7b-2")
    
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