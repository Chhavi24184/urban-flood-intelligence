import sys
from pathlib import Path
import uvicorn

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root))
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
