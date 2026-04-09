import sys
import io

# Force stdout to utf-8 in case of weird characters in errors
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from huggingface_hub import HfApi

token = "YOUR_HUGGINGFACE_TOKEN"
api = HfApi(token=token)

try:
    user_info = api.whoami()
    namespace = user_info['name']
    repo_name = "waste-detection-app"
    repo_id = f"{namespace}/{repo_name}"
    
    print(f"Deploying to Space: {repo_id}")
    
    # Create the space if it doesn't already exist.
    # We use "static" to bypass a bug in some SDK versions; the README.yaml we upload will convert it to "streamlit"
    api.create_repo(repo_id=repo_id, repo_type="space", space_sdk="static", exist_ok=True)
    
    # Upload the folder
    print("Uploading files... This may take a few minutes as the YOLO model is being uploaded.")
    api.upload_folder(
        folder_path="used",
        repo_id=repo_id,
        repo_type="space"
    )
    print(f"\n✅ Deployed successfully! You can view your app at: https://huggingface.co/spaces/{repo_id}")
except Exception as e:
    print(f"An error occurred during deployment: {e}")
