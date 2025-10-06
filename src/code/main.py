import uvicorn

from server import app


PORT = 8080


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)

