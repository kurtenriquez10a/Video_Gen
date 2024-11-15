import time
import jwt
import requests

# API Keys
ACCESS_KEY = "dd750c90da9b46d5bc59b91fa957715b"
SECRET_KEY = "f4fac419352b4117b9956306e027acbe"

# Base API URL
BASE_URL = "https://api.klingai.com"

# Generate API Token
def encode_jwt_token(ak, sk):
    """
    Generate JWT token using Access Key and Secret Key.
    """
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 3600,  # Token valid for 1 hour
        "nbf": int(time.time()) - 5      # Token starts being valid 5 seconds before now
    }
    token = jwt.encode(payload, sk, algorithm="HS256", headers=headers)
    return token

# Create Text-to-Video Task
def create_video_task(api_token, prompt, model="kling-v1", duration="5", aspect_ratio="16:9", mode="std"):
    """
    Create a Text-to-Video generation task.
    """
    url = f"{BASE_URL}/v1/videos/text2video"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "mode": mode
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        task_id = data.get("data", {}).get("task_id")
        print(f"Task Created! Task ID: {task_id}")
        return task_id
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Query Text-to-Video Task Status
def query_video_task_status(api_token, task_id):
    """
    Query the status of a Text-to-Video task and extract the video URL.
    """
    url = f"{BASE_URL}/v1/videos/text2video/{task_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("Full Response:", data)  # Debug: Print the full response

        status = data.get("data", {}).get("task_status")
        service_code = data.get("code", 0)  # Default to 0 if "code" is not present
        print(f"Task Status: {status}")
        print(f"Service Code: {service_code}")

        # Extract video URL
        video_data = data.get("data", {}).get("task_result", {}).get("videos", [])
        if video_data:
            video_url = video_data[0].get("url")  # Extract the URL of the first video
            print(f"Video URL: {video_url}")
            return video_url
        else:
            print("No videos found in the task result.")
            return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None





# Wait for Task Completion
def wait_for_task_completion(api_token, task_id):
    """
    Wait for the task to complete by repeatedly querying the task status.
    Exit the loop if the task succeeds or fails.
    """
    while True:
        # Query the task status
        url = f"{BASE_URL}/v1/videos/text2video/{task_id}"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            status = data.get("data", {}).get("task_status")
            print(f"Task Status: {status}")

            if status == "succeed":
                # Extract and print the video URL
                video_data = data.get("data", {}).get("task_result", {}).get("videos", [])
                if video_data:
                    video_url = video_data[0].get("url")
                    print(f"Video URL: {video_url}")
                print("Video generation completed successfully!")
                break
            elif status == "failed":
                print("Video generation failed.")
                break
            else:
                print(f"Task {task_id} still processing... Waiting for 30 seconds.")
                time.sleep(30)
        else:
            print(f"Error querying task status: {response.status_code} - {response.text}")
            break


# Main Execution
if __name__ == "__main__":
    # Generate API Token
    api_token = encode_jwt_token(ACCESS_KEY, SECRET_KEY)
    print(f"Generated API Token: {api_token}")

    # Ask user for input
    action = input("Do you want to query an existing task or create a new one? (query/create): ").strip().lower()

    if action == "query":
        # Query an existing task
        existing_task_id = input("Enter the task ID to query: ").strip()
        if existing_task_id:
            print(f"Querying status for task ID: {existing_task_id}")
            wait_for_task_completion(api_token, existing_task_id)
        else:
            print("No task ID provided. Exiting.")
    elif action == "create":
        # Create a new task
        prompt = input("Enter the prompt for video generation: ").strip()
        if prompt:
            print(f"Creating a new task with prompt: {prompt}")
            task_id = create_video_task(api_token, prompt)
            if task_id:
                wait_for_task_completion(api_token, task_id)
        else:
            print("No prompt provided. Exiting.")
    else:
        print("Invalid action. Please type 'query' or 'create'. Exiting.")