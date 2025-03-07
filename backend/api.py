from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from together import Together
import sqlite3
from pydantic import BaseModel


# Together AI URL for Query
client = Together()
url = "https://api.together.xyz/v1/completions"

DB_NAME = "subway_outlets.db"
app = FastAPI()

# Allow CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Database helper function
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Returns dictionary-like rows
    return conn

# Root endpoint to test 
@app.get("/")
def read_root():
    return {"message": "Welcome to the Subway Outlets API"}

# Get all outlets
@app.get("/outlets")
def get_outlets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM outlets")
    outlets = cursor.fetchall()
    conn.close()
    return [dict(outlet) for outlet in outlets]

# Get outlet by ID
@app.get("/outlets/{id}")
def get_outlet(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM outlets WHERE id = ?", (id,))
    outlet = cursor.fetchone()
    conn.close()
    if outlet:
        return dict(outlet)
    return {"error": "Outlet not found"}

# Request model for AI chat
class QueryRequest(BaseModel):
    message: str

# AI Chatbot Query Endpoint
@app.post("/chat")
async def chat(request: QueryRequest):
    user_message = request.message

    # Fetch all outlets from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, address, operating_hours FROM outlets")
    outlets = cursor.fetchall()
    conn.close()

    # Format the data for prompt
    formatted_data = "\n".join([
        f"{outlet['name']} at {outlet['address']} with operating hours: {outlet['operating_hours'] or 'Unknown'}."
        for outlet in outlets
    ])

    # Generate the prompt
    prompt = f"You are Subway Location Finder. Given the following store data:\n{formatted_data}\n\nAnswer the question: {user_message}"

    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=[{"role": "user", "content": prompt}],
        )
     
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))