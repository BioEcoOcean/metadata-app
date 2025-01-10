from datetime import datetime
import json
import requests
from flask import jsonify, request

# Function to handle the action based on the form submission
def process_submission_action(issue_number, action, schema_entry, GITHUB_TOKEN, GITHUB_API_URL, REPO_OWNER, GITHUB_REPO):
    if action == "print_json":
        # Print JSON for testing
        print(schema_entry)
        return jsonify({"success": True, "printed_json": schema_entry})
    
    # Prepare issue title and body for GitHub submission
    issue_title = f"New Submission: {schema_entry.get('name', 'Unknown Entry')}"
    issue_body = f"### Metadata Submission\n\n```json\n{json.dumps(schema_entry, indent=4)}\n```"

    # Create payload for GitHub
    payload = {
        "title": issue_title,
        "body": issue_body,
        "labels": ["metadata submission"]
    }
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Submit to GitHub API
    if action == "submit_to_github":
        response = requests.post(
            GITHUB_API_URL.format(owner=REPO_OWNER, repo=GITHUB_REPO),
            json=payload,
            headers=headers
        )

        # Log the response for debugging
        print(f"GitHub API Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Check the response from GitHub
        if response.status_code == 201:
            return jsonify({"success": True, "issue_url": response.json()["html_url"]})
        else:
            return jsonify({"success": False, "error": response.json()}), response.status_code
    
    # Update issue using GitHub API
    if action == "update_github" and issue_number is not None:
        print("issue_number", issue_number)
        issue_url = f"https://api.github.com/repos/{REPO_OWNER}/{GITHUB_REPO}/issues/{issue_number}"
        response = requests.patch(
            issue_url,
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            # Step 2: Add a comment to the issue (POST request)
            comments_url = f"https://api.github.com/repos/{REPO_OWNER}/{GITHUB_REPO}/issues/{issue_number}/comments"
            comment_payload = {
                "body": f"Entry updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"  # Add a timestamp for the update
            }
            comment_response = requests.post(comments_url, json=comment_payload, headers=headers)
            
            # Check if the comment was added successfully
            if comment_response.status_code == 201:
                return jsonify({"success": True, "message": "Issue updated and comment added successfully!"})
            else:
                return jsonify({"success": False, "error": comment_response.json()}), comment_response.status_code
            

    return jsonify({"success": False, "error": "Invalid action provided"}), 400
