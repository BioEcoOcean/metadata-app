from flask import Flask, session, render_template, request, jsonify, redirect, url_for, redirect
from flask_dance.contrib.github import make_github_blueprint, github
from flask_session import Session
from redis import Redis
import json
import requests
import re
import os
from processMappings import map_form_to_schema
from generateForm import generate_form
from submitAction import process_submission_action
from makeFormIntoJson import makeFormJson
from datetime import datetime
from helpers import set_flask_environment


app = Flask(__name__)
set_flask_environment(app=app)

# app.config['SESSION_TYPE'] = "redis"
# app.config['SESSION_REDIS'] = Redis(host='127.0.0.1', port=6379)
# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_USE_SIGNER'] = True
# Session(app)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000, ssl_context=("server.crt", "server.key"))

# Set up the OAuth
github_blueprint=make_github_blueprint(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    redirect_url="https://127.0.0.1:5000/github/authorized"
    )
app.register_blueprint(github_blueprint)


# GitHub URLS
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Use environment variables for security, pasted here so I can revert to this when ready
REPO_OWNER = "BioEcoOcean"
GITHUB_REPO = "metadata-tracking-dev"
BRANCH = "refs/heads/main"
JSON_FOLDER = "jsonFiles"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{GITHUB_REPO}/issues"
GITHUB_API_JSONS = f"https://api.github.com/repos/{REPO_OWNER}/{GITHUB_REPO}/contents/{JSON_FOLDER}"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{GITHUB_REPO}/{BRANCH}/{JSON_FOLDER}"


@app.route("/")
def index():
    """Display the homepage with GitHub login option."""
    if not github.authorized:
        return redirect(url_for("github.login"))
    user_info = github.get('/user')
    return render_template('home.html', user=user_info.json())

@app.route('/github')
def login():
    """Log in a registered or authenticated user."""
    if not github.authorized:
        return redirect(url_for('github.login'))
    res = github.get('/user')
    return f"You are logged in as {res.json()['login']} on GitHub."

@app.route('/github/authorized')
def github_authorized():
    """Handle the OAuth callback from GitHub."""
    response = github.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied or something went wrong.'

    # Store the access token
    session['github_oauth_token'] = (response['access_token'], '')

    # Fetch user information from GitHub
    user_info = github.get('/user')

    return render_template('home.html', user=user_info.json())


@app.route("/home")
def home():
    """Main page, also display list of current programs submitted."""
    # if not github.authorized:
    #     return redirect(url_for("github.login"))

    try:
            user_info = github.get("/user").json()

            # Fetch the list of directories in the JSON folder using GitHub API
            response = requests.get(GITHUB_API_JSONS)
            response.raise_for_status()
            contents = response.json()

            # Extract directories and construct URLs for submitted entries
            projects = []
            for item in contents:
                if item['type'] == 'dir':
                    folder_name = item['name']
                    print("folder name: ", folder_name)
                    folder_api_url = f"{GITHUB_API_JSONS}/{folder_name}"
                    folder_response = requests.get(folder_api_url)
                    folder_response.raise_for_status()
                    folder_contents = folder_response.json()

                    # Find JSON files and extract 'url' field
                    for file_item in folder_contents:
                        if file_item['name'].endswith(".json"):
                            json_url = file_item['download_url']
                            json_response = requests.get(json_url)
                            json_response.raise_for_status()
                            json_data = json_response.json()
                            project_url = json_data.get("url", "URL not found")

                            # Add project details
                            projects.append({
                                "name": folder_name,
                                "project_link": project_url,
                                "sitemap_link": f"{RAW_BASE_URL}/{folder_name}/sitemap.xml"
                            })

            # Render the index.html template
            return render_template("home.html", user=user_info, projects=projects)

    except requests.RequestException as e:
        return f"Error fetching data from GitHub: {e}", 500


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

def get_github_issues():
    try:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{GITHUB_REPO}/issues"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        params = {"labels": "metadata submission"}  # Filtering by label
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()  # Return the list of issues
        else:
                print(f"Failed to fetch issues: {response.status_code}")
                return []  # Return an empty list in case of failure
    except Exception as e:
        print(f"Error fetching issues: {e}")
        return []  # Return an empty list in case of an error

@app.route("/handle_form_submission", methods=["GET", "POST"])
def handle_form_submission():
    print(request.method)
    if request.method == "GET":
        return render_template("new_submission.html", form_html=generate_form(prefilled_data=None))
    elif request.method == "POST":
        return makeFormJson()
    return None

@app.route("/submit", methods=["POST"])
def handle_submission():
    # Get the form data (action and schema_entry)
    action = request.form.get("action")
    schema_entry = makeFormJson()  # Assuming the form data is a dictionary
    print("attempting to get issue number")
    print("session issue number: ", session.get('issue_number', 'N/A'))

    # Call the function to process the action
    result = process_submission_action(session.get('issue_number', None), action, schema_entry, GITHUB_TOKEN, GITHUB_API_URL, REPO_OWNER, GITHUB_REPO)

    # Return the appropriate response based on the result from the function
    if isinstance(result, dict) and result.get("success"):
        return result
    else:
        return result

@app.route('/success')
def success():
    issue_number = request.args.get('issue_number', 'Unknown')
    return render_template('success.html', issue_number=issue_number)

@app.route("/update_entry", methods=["GET", "POST"])
def update_entry():
    print(">>> ", request.method)
    issues = get_github_issues()
    filtered_issues = [
        issue for issue in issues if "metadata submission" in [label["name"] for label in issue.get("labels", [])]
    ]

    if request.method == "GET":
        return render_template("update_entry.html", issues=filtered_issues)

    elif request.method == "POST":
        print(request.get_data())
        # Fetch the selected issue
        print(str(request))
        print('setting default value')
        #session['issue_number'] = 'woo'
        print("session issue number after setting default value: ", session.get('issue_number', 'N/A'))
        issue_number = request.form.get("selected_issue", 'N/A')
        if issue_number:
            # Get the GitHub issue data
            print("issue number: ", issue_number, "type: ", type(issue_number), "request: ", request.method)
            session['issue_number'] = issue_number
            print("session issue number after setting it with real value: ", session.get('issue_number', 'N/A'))
            issue_url = f"https://api.github.com/repos/{REPO_OWNER}/{GITHUB_REPO}/issues/{issue_number}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            response = requests.get(issue_url, headers=headers)
            response_data = response.json()  # Debug: Inspect the full response from GitHub
            print(f"Response Data: {response_data}")

            if response.status_code == 200:
                # Parse the issue data
                issue_data = response.json()
                issue_body = issue_data["body"]
                issue_body_cleaned = re.sub(r"^### Metadata Submission[\r\n]*\`*json", "", issue_body)
                issue_body_cleaned = re.sub(r"\`*$", "", issue_body_cleaned)
                #print(f"Issue Body: {issue_body}")  # Log the original body
                print(f"Cleaned Issue Body: {issue_body_cleaned}")  # Log the cleaned version

                # Parse the body of the GitHub issue into a Python dictionary (assuming it's a JSON string)
                try:
                    issue_data_json = json.loads(issue_body_cleaned)  # Remove the header text if present
                except json.JSONDecodeError as e:
                    return jsonify({"success": False, "error": f"Error parsing JSON: {e}"})

                print("Parsed JSON:", issue_data_json)  # Debug: Check the parsed JSON

                # Map the GitHub issue data to schema format
                schema_entry = map_form_to_schema(issue_data_json)

                # Generate the form with the mapped data
                form_html = generate_form(prefilled_data=schema_entry)

                return render_template("update_entry.html", issues=filtered_issues, form_html=form_html, issue_number=issue_number)
            else:
                return jsonify({"success": False, "error": response.json()})
        else:
            return jsonify({"success": False, "error": "No issue selected."})

@app.route("/submit_update", methods=["POST"])
def submit_update():
    updated_data = request.form.to_dict()  # Get form data as a dictionary
    issue_number = request.form.get("issue_number")  # Get the selected issue number

    # Map the form data to the schema format
    schema_entry = makeFormJson(updated_data)  # Mapping form data to schema format

    # Construct the GitHub issue URL and the payload to send
    issue_url = f"https://api.github.com/repos/{REPO_OWNER}/{GITHUB_REPO}/issues/{issue_number}"
    comments_url = f"https://api.github.com/repos/{REPO_OWNER}/{GITHUB_REPO}/issues/{issue_number}/comments"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # GitHub Payload includes the title and body, with the body containing the metadata as formatted JSON
    payload = {
        "title": f"Updated Submission: {updated_data.get('name', 'Unnamed Program')}",
        "body": "### Metadata Submission\n\n" + json.dumps(schema_entry, indent=4)  # Send the mapped schema as part of the body
    }

    # Step 1: Update the issue with new data (PATCH request)
    response = requests.patch(issue_url, json=payload, headers=headers)

    # Check if the issue was updated successfully
    if response.status_code == 200:
        # Step 2: Add a comment to the issue (POST request)
        comment_payload = {
            "body": f"Entry updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"  # Add a timestamp for the update
        }
        comment_response = requests.post(comments_url, json=comment_payload, headers=headers)

        # Check if the comment was added successfully
        if comment_response.status_code == 201:
            return jsonify({"success": True, "message": "Issue updated and comment added successfully!"})
        else:
            return jsonify({"success": False, "error": comment_response.json()}), comment_response.status_code
    else:
        return jsonify({"success": False, "error": response.json()}), response.status_code

