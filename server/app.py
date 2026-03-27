from fastapi import FastAPI
from server.environment import Environment

app = FastAPI()
env = Environment()

@app.get("/")
def home():
    return {"message": "Server is running"}

@app.get("/reset")
def reset():
    return env.reset()

@app.post("/step")
def step(action: str):
    return env.step(action)