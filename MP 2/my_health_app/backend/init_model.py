import sys
import os

# Add the parent directory to sys.path so we can import model_code
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import model_code

if __name__ == "__main__":
    print("Initializing model training and saving...")
    # The models are trained as soon as model_code is imported.
    # Now we save them.
    models_dir = os.path.join(current_dir, "models")
    model_code.save_models(models_dir=models_dir)
    print("Done! You can now start the backend server.")
