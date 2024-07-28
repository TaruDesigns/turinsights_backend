# Helper debug file to avoid having to do remote debug in the container, for quick tests

from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    # Debug whole app
    import uvicorn

    from app.main import app

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
