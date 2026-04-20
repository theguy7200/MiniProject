# Aura Health - Disease & Risk Prediction

A full-stack machine learning web application that predicts potential diseases and health risk levels based on patient symptoms, vitals, and lab tests.

## 🚀 Features
- **FastAPI Backend:** High-performance, asynchronous REST API.
- **Pre-trained ML Models:** Avoids long startup times by loading serialized `.pkl` models generated via Joblib.
- **Premium Glassmorphism UI:** A sleek, dynamic frontend using modern web design principles.
- **Single-Service Deployment:** The FastAPI backend serves the frontend static files, making it incredibly easy to deploy on free platforms like Render.

---

## 🛠️ Local Setup & Running

### 1. Prerequisites
- Python 3.9+
- Your original dataset file (`professional_dataset_16k.csv`) placed in the root directory (`my_health_app/`).

### 2. Install Dependencies
Open a terminal in the `my_health_app/backend` folder and run:
```bash
cd backend
pip install -r requirements.txt
```

### 3. Generate the ML Models (Run Once)
Since your model needs to be trained on the dataset, we must run the setup script to generate the saved model files.

From the `my_health_app/backend` directory, run:
```bash
python init_model.py
```
*This will execute the model training pipeline and save the `.pkl` files into the `backend/models/` directory.*

### 4. Start the Application
Once the models are generated, you can start the web server:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
- **Web UI:** Open your browser and go to [http://localhost:8000/](http://localhost:8000/)
- **API Docs:** Go to [http://localhost:8000/docs](http://localhost:8000/docs) to test the backend API directly.

---

## 🌍 Deployment (Render)

Deploying this app is completely free and easy using **Render.com**.

1. **Push to GitHub**:
   - Initialize a git repository in the `my_health_app/` folder.
   - Commit and push the code (including the `.pkl` files inside `backend/models/`) to a public or private GitHub repo.
   - *Note: If your `.pkl` files are too large for standard Git, you may need to use Git LFS.*

2. **Create a Web Service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/) and click **New+** > **Web Service**.
   - Connect your GitHub repository.

3. **Configure the Service**:
   - **Name**: `aura-health-app` (or whatever you prefer)
   - **Root Directory**: `backend` (Important! Set this to `backend` since that's where `app.py` is).
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

4. **Deploy**:
   - Click **Create Web Service**.
   - Wait a few minutes for the build to finish. Render will provide you with a public URL (e.g., `https://aura-health-app.onrender.com`).
