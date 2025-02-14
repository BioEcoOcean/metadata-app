from datetime import datetime
import json
import requests
import os
from flask import jsonify, request, session, redirect, url_for

# Function to handle the action based on the form submission
def process_submission_action(issue_number, action, schema_entry, GITHUB_API_URL, REPO_OWNER, GITHUB_REPO): #i revmoed github_token from this so that it imports it
    if action == "print_json":
        # Print JSON for testing
        print(schema_entry)
        return jsonify({"success": True, "printed_json": schema_entry})

    GITHUB_TOKEN = session.get("github_oauth_token", {}).get("access_token")
    if not GITHUB_TOKEN:
        GITHUB_TOKEN = session.get("github_oauth_token", {}).get("access_token")
        print("GitHub token:", GITHUB_TOKEN)
        if not GITHUB_TOKEN:
            return jsonify({"success": False, "error": "GitHub token not found in session"}), 401

    # Prepare issue title and body for GitHub submission
    issue_title = f"New Submission: {schema_entry.get('name', 'EOV Metadata Entry')}"
    issue_body = f"### Metadata Submission\n\n```json\n{json.dumps(schema_entry, indent=4)}\n```"

    # Create payload for GitHub
    payload = {
        "title": issue_title,
        "body": issue_body,
        "labels": ["metadata submission"]
    }
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    print("Payload:", payload)

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
            issue_url = response.json()["html_url"]
            if "metadata submission" not in response.json().get("labels", []):
                print("User does not have permission to add labels. Using admin token as fallback.")
                fallback_add_labels(response.json().get("number"), REPO_OWNER, GITHUB_REPO)
            return {"success": True, "message": "Issue submitted successfully!", "issue_url": issue_url}
            #return jsonify({"success": True, "issue_url": response.json()["html_url"]})
        else:
            return {"success": False, "error": response.json()}, response.status_code
            #return jsonify({"success": False, "error": response.json()}), response.status_code

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
                issue_url = f"https://github.com/{REPO_OWNER}/{GITHUB_REPO}/issues/{issue_number}"
                return {"success": True, "message": "Issue updated and comment added successfully!", "issue_url": issue_url}
                #return jsonify({"success": True, "message": "Issue updated and comment added successfully!"})
            else:
                return {"success": False, "error": comment_response.json()}
                #return jsonify({"success": False, "error": comment_response.json()}), comment_response.status_code


    return {"success": False, "error": "Invalid action provided"}
    #return jsonify({"success": False, "error": "Invalid action provided"}), 400

# handle label assignment using the admin token:
def fallback_add_labels(issue_number, REPO_OWNER, GITHUB_REPO):
    admin_token = os.getenv('ADMIN_GITHUB_TOKEN')  # Admin token stored securely in environment variables
    if not admin_token:
        print("Admin token not configured. Unable to add labels.")
        return

    headers = {"Authorization": f"token {admin_token}"}
    label_url = f"https://api.github.com/repos/{REPO_OWNER}/{GITHUB_REPO}/issues/{issue_number}"
    payload = {"labels": ["metadata submission"]}

    response = requests.patch(label_url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Labels added successfully to issue #{issue_number}.")
    else:
        print(f"Failed to add labels to issue #{issue_number}. Response: {response.json()}")
