from fastapi import FastAPI, Depends
from pydantic import BaseModel
from pymongo import MongoClient
from jose import jwt, JWTError  
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  
from datetime import datetime, timedelta


client = MongoClient("mongodb://localhost:27017/")

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()

db = client["user_database"]
collection = db["users"]

class LoginData(BaseModel):
    username: str
    password: str
    email: str
    date_of_birth: str

@app.post("/register")
def register_user(login_data: LoginData):
    students_data = {
        "username": login_data.username,
        "password": login_data.password,
        "email": login_data.email,
        "date_of_birth": login_data.date_of_birth
    }
    collection.insert_one(students_data)
    return {"message": "User registered successfully!"}

# Changed to OAuth2PasswordRequestForm so Swagger's Authorize button works
@app.post("/login")
def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_login = collection.find_one({
        "username": form_data.username,
        "password": form_data.password
    })

    if user_login:
        data = {
            "sub": form_data.username,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }

        token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

        #  must be "access_token" and "token_type" for Swagger to pick it up
        return {"access_token": token, "token_type": "bearer"}
    else:
        return {"message": "Invalid username or password"}

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return {"error": "Invalid token"}

@app.get("/profile")
def get_profile(payload: dict = Depends(verify_token)):
    user = collection.find_one({"username": payload["sub"]})

    return {
    "message": f"Welcome to your profile {payload['sub']}",
    "email": user["email"],
    "date_of_birth": user["date_of_birth"]
}

@app.put("/update-profile")
def update_profile(login_data:LoginData, payload: dict = Depends(verify_token)):
    collection.update_one(
        {"username": payload['sub']},
        {"$set": {
            "email": login_data.email,
            "date_of_birth": login_data.date_of_birth,
            "password": login_data.password
        }}
    )

       
    return {"message":"Profile update successful!"}