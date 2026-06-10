import uvicorn

from backend.config import HOST, PORT, RELOAD


def main():
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=RELOAD)


if __name__ == "__main__":
    main()
