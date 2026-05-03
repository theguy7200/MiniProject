import sys
import json
import traceback
import os
from model_wrapper import HealthModelWrapper

def main():
    try:
        # Read all from stdin
        input_data = sys.stdin.read()
        if not input_data:
            print(json.dumps({"error": "No input provided"}))
            sys.exit(1)
            
        data = json.loads(input_data)
        
        symptoms = data.get("symptoms", {})
        vitals = data.get("vitals", {})
        labs = data.get("labs", {})
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(current_dir, "models")
        
        wrapper = HealthModelWrapper(models_dir=models_dir)
        if not wrapper.load_models():
             print(json.dumps({"error": "Models could not be loaded. Did you run init_model.py?"}))
             sys.exit(1)
             
        prediction = wrapper.predict(symptoms=symptoms, vitals=vitals, labs=labs)
        print(json.dumps({"status": "success", "data": prediction}))
        
    except Exception as e:
        print(json.dumps({"status": "error", "error": str(e), "trace": traceback.format_exc()}))
        sys.exit(1)

if __name__ == "__main__":
    main()
