
import uvicorn
from infrastructure.repository import init_db

if __name__ == "__main__":
    uvicorn.run("api.http:app", host="127.0.0.1", port=8000)
