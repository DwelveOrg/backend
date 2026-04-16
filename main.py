import uvicorn
from fastapi import FastAPI
from App import auth, groups, tests, dashboard

app = FastAPI(title="LMS Exam Prep API")

# Подключаем роутеры (аналог Blueprint в Flask)
app.include_router(auth.router)
app.include_router(groups.router)
app.include_router(tests.router)
app.include_router(dashboard.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Exam Prep API", "docs": "/docs"}

if __name__ == "__main__":
    # Запуск сервера (аналог app.run во Flask)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)