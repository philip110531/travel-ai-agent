from flask import Flask, request, Response, send_from_directory
import requests

app = Flask(__name__, static_folder=".", static_url_path="")

ADK_BASE_URL = "http://127.0.0.1:8001"


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/app.js")
def app_js():
    return send_from_directory(".", "app.js")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)


@app.route("/apps/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def proxy_apps(path):
    target_url = f"{ADK_BASE_URL}/apps/{path}"
    return proxy_request(target_url)


@app.route("/run_sse", methods=["POST", "OPTIONS"])
def proxy_run_sse():
    target_url = f"{ADK_BASE_URL}/run_sse"
    return proxy_request(target_url)


def proxy_request(target_url):
    if request.method == "OPTIONS":
        return Response(status=204)

    headers = {}

    for key, value in request.headers:
        lower_key = key.lower()

        if lower_key in ["host", "content-length", "accept-encoding"]:
            continue

        headers[key] = value

    try:
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            params=request.args,
            timeout=180,
            stream=False,
        )

        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        ]

        response_headers = []

        for key, value in response.headers.items():
            if key.lower() not in excluded_headers:
                response_headers.append((key, value))

        return Response(
            response.content,
            status=response.status_code,
            headers=response_headers,
        )

    except requests.exceptions.RequestException as error:
        return Response(
            f"Proxy 連線 ADK 失敗：{error}",
            status=502,
            content_type="text/plain; charset=utf-8",
        )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5500, debug=True)