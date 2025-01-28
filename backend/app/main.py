from fastapi import FastAPI

app = FastAPI(
    title="Pokemon Battle Simulator",
    description="A Pokemon battle simulator API",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Pokemon Battle Simulator API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
