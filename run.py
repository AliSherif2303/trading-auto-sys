#app/run.py
from app.main import app
from app.db.database_postgres import init_db
import uvicorn


if __name__ == '__main__':
    init_db()
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)