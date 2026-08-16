import requests
import re
from config import DEFAULT_BACKEND_URL
 
BASE_URL = DEFAULT_BACKEND_URL
 
UPLOAD_URL = f"{BASE_URL}/upload"
REVIEW_URL = f"{BASE_URL}/review"
APPLY_URL = f"{BASE_URL}/apply"
DOWNLOAD_URL = f"{BASE_URL}/download"
 
 
def upload_file(uploaded_file):
    files = {
        "terraform_file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            "application/octet-stream"
        )
    }
 
    response = requests.post(UPLOAD_URL, files=files)
    response.raise_for_status()
 
    return response.json()
 
 
def review_file(review_id):
 
    payload = {
        "review_id": review_id
    }
 
    response = requests.post(REVIEW_URL, json=payload)
    response.raise_for_status()
 
    return response.json()
 
 
def apply_recommendations(review_id, decisions):
 
    payload = {
        "review_id": review_id,
        "accepted_recommendations": [
            d["id"] for d in decisions
            if d["status"]=="accepted"
        ],
        "rejected_recommendations": [
            d["id"] for d in decisions
            if d["status"]=="rejected"
        ],

    }

    print("PAYLOAD")
    print(payload)
 
    response = requests.post(APPLY_URL, json=payload)
    response.raise_for_status()
 
    return response.json()
 
 
def download_review(review_id):
 
    metadata = requests.get(
        f"{DOWNLOAD_URL}/{review_id}").json()
    
    response=requests.get(
        BASE_URL + metadata["download_url"]
    )
 
    response.raise_for_status()
 
    return response.content