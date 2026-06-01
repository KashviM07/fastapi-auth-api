from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

data={
    "username": "kashvineha",
    "password": "password123"
}


class LoginData(BaseModel):
    username: str
    password: str

@app.post("/login")
def user_login(login_data: LoginData):
    if login_data.username.casefold() == data["username"].casefold() and login_data.password == data["password"]:
        return {"message": "Login successful!"}
    else:
        return {"message": "Invalid username or password."} 