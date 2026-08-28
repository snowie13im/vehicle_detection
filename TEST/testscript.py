# 1. Import the library
from inference_sdk import InferenceHTTPClient

# 2. Connect to your local server
client = InferenceHTTPClient(
    api_url="http://localhost:9001", # Local server address
    api_key="Kno6UrEbmrpiEYq3SLBW"
)

# 3. Run your workflow on an image
result = client.run_workflow(
    workspace_name="snowies-workspace",
    workflow_id="bike-vehicle-detection-logger-1779314546977",
    images={
        "image": "C:\\Users\\USER\\Desktop\\Mestrado\\AM2R\\Vehicle-Detection-main\\Vehicle-Detection-main\\Dataset\\images\\train\\652.png" # Path to your image file
    },
    use_cache=True # Speeds up repeated requests
)

# 4. Get your results
print(result)
