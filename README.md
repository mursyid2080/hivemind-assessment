# mindhive
## Prerequisites:
* Python 3.8.19
* SQLite (built-in with Python)
* NPM (for frontend)

## Setup Instructions:

### 1. Set Up Virtual Environment
* Run: 
```bash
$ python -m venv venv 
```
* Activate the virtual environment: 
  * **Windows**: `venv\Scripts\activate`
  * **Mac/Linux**: `source venv/bin/activate`

### 2. Install Dependencies
* Navigate to the project directory and run: 
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
* **Google Maps API Key**: Generate an API key with Geocoding API enabled.
* **Create a `.env` file** in the backend directory and add the below line. Save the file:
```bash
GOOGLE_MAPS_API_KEY=your_api_key
```
* **Together AI API Key**: Create an account and copy the user key. Run in the console:
```bash
export TOGETHER_API_KEY=your_together_ai_key
```

### 4. Run the Web Scraper
* The repository has a pre-populated database file (`subway_outlets.db`). If you decide to delete it and create a new one, use the scraping script:
```bash
python scrape.py
```
  * This will create and populate `subway_outlets.db` with Subway outlet data.

### 5. Start the Backend API
* Run:
```bash
uvicorn api:app --reload
```
* The API should be accessible at [http://localhost:8000](http://localhost:8000).

### 6. Start the Frontend
* Navigate to the frontend directory from the project base directory:
```bash
cd frontend
npm install
```
* Ignore any vulnerability warnings and start the frontend:
```bash
npm start
```
* The frontend should now be running at [http://localhost:3000](http://localhost:3000).


