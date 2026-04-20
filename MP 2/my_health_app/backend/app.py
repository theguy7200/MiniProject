from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
import os
import uvicorn
from model_wrapper import HealthModelWrapper

app = FastAPI(title="Health Disease & Risk Prediction API")

# Initialize and load model
current_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(current_dir, "models")
model_wrapper = HealthModelWrapper(models_dir=models_dir)

@app.on_event("startup")
async def startup_event():
    print("[INFO] Starting application, loading models...")
    success = model_wrapper.load_models()
    if not success:
        print("[WARNING] Models could not be loaded at startup. Did you run init_model.py?")

class PredictionRequest(BaseModel):
    symptoms: Dict[str, int] = Field(default_factory=dict, description="Dictionary of symptoms (1 for presence, 0 for absence)")
    vitals: Dict[str, Any] = Field(default_factory=dict, description="Dictionary of vitals e.g., Heart_Rate")
    labs: Optional[Dict[str, float]] = Field(default_factory=dict, description="Dictionary of lab tests e.g., ALT_UL")

@app.post("/api/predict")
async def predict_health(request: PredictionRequest):
    if not model_wrapper.is_loaded:
        # Try loading again just in case models were generated while server was running
        if not model_wrapper.load_models():
            raise HTTPException(status_code=500, detail="Models are not trained/loaded. Please run init_model.py.")
    
    try:
        # Ensure vitals has required minimums, wrapper handles default fallbacks but good to pass what we got
        prediction = model_wrapper.predict(
            symptoms=request.symptoms,
            vitals=request.vitals,
            labs=request.labs or {}
        )
        return {"status": "success", "data": prediction}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(current_dir), "frontend")

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            with open(index_file, "r") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>Frontend not found</h1>", status_code=404)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

# Trigger reload
