from flask import Flask, session, render_template, request, jsonify, url_for, redirect
from dotenv import load_dotenv
import os
load_dotenv()

from flask_dance.contrib.github import make_github_blueprint, github
from flask_session import Session
#from redis import Redis
import json
import requests
import re
from flask_caching import Cache
from processMappings import map_form_to_schema
from generateForm import generate_form
from submitAction import process_submission_action
from makeFormIntoJson import makeFormJson
from datetime import datetime
from helpers import set_flask_environment
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
set_flask_environment(app=app)
# Add ProxyFix middleware to handle headers from Nginx
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# app.secret_key = os.environ.get("SECRET_KEY", "supersekrit")
# app.config["GITHUB_OAUTH_CLIENT_ID"] = os.environ.get("GITHUB_OAUTH_CLIENT_ID")
# app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.environ.get("GITHUB_OAUTH_CLIENT_SECRET")
# app.config['SESSION_TYPE'] = "redis"
# app.config['SESSION_REDIS'] = Redis(host='127.0.0.1', port=5000)
# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_USE_SIGNER'] = True
# Session(app)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Set up the OAuth
github_blueprint=make_github_blueprint(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    scope="public_repo"
#    redirect_url="https://eovmetadata.obis.org/login/github/authorized"
    )
app.register_blueprint(github_blueprint, url_prefix="/login")


# GitHub URLS 
REPO_OWNER = "BioEcoOcean"
GITHUB_REPO = "metadata-tracking-dev"
BRANCH = "refs/heads/main"
JSON_FOLDER = "jsonFiles"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{GITHUB_REPO}/issues"
GITHUB_API_JSONS = f"https://api.github.com/repos/{REPO_OWNER}/{GITHUB_REPO}/contents/{JSON_FOLDER}"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{GITHUB_REPO}/{BRANCH}/{JSON_FOLDER}"

@app.route("/")
def index():
    """ Landing page"""
    print("User Session  landing route:", session, flush=True)
    if not github.authorized:
        return render_template("landing.html", user=None)
    
    user = session.get("user")
    #session["GITHUB_TOKEN"] = github.token["access_token"]
    if not user:
        # Fetch user info from GitHub if not in session
        resp = github.get("/user")
        if not resp.ok:
            return redirect(url_for('index'))
        
        user_info = resp.json()
        session["user"] = user_info
        print("User Info Fetched and Saved:", session["user"], flush=True)
    return redirect(url_for("home"))

@app.route('/github/authorized')
def github_authorized():
    """Handle the OAuth callback from GitHub."""
    if not github.authorized:
        # Redirect to login if not authorized
        return redirect(url_for("github.login"))

    # Fetch user info from GitHub
    resp = github.get("/user")
    print("GitHub user Info:", resp, flush=True)
    if not resp.ok:
        return redirect(url_for('index')) 

    # Store user info in session
    user_info = resp.json()
    session["user"] = user_info
    #session["GITHUB_TOKEN"] = github.token["access_token"]
    #print("User Info & token Saved:", session["user"], session["GITHUB_TOKEN"], flush=True)
    return redirect(url_for('home'))

@app.route("/data")
def data():
    return render_template("data.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/dataproducer")
def dataproducer():
    user = session["user"]
    if not user:
        # Fetch user info from GitHub if not in session
        resp = github.get("/user")
        if not resp.ok:
            return redirect(url_for('index'))
        
        user_info = resp.json()
        session["user"] = user_info
        print("User Info Fetched and Saved:", session["user"], flush=True)
    
    # Retrieve the token from the session
    github_token = session.get("GITHUB_TOKEN")
    if not github_token:
        github_token = session.get("github_oauth_token", {}).get("access_token")
        if github_token:
            session["GITHUB_TOKEN"] = github_token
    print("GITHUB_TOKEN from session:", github_token, flush=True)

    projects = cache.get('projects')
    if projects is None:
        projects = fetch_projects_from_github()
        cache.set('projects', projects, timeout=60*60)  # Cache for 1 hour
    return render_template("metadata-landing.html", user=session.get("user"), projects=projects)

@app.route("/home")
def home():
    """Main page, also display list of current programs submitted."""
    if not github.authorized:
        return redirect(url_for("github.login"))
    
    # Fetch user data from session instead of making a new GitHub API request
    print("GitHub Authorized:", github.authorized, flush=True)
    print("Session User homeroute:", session["user"], flush=True)

    user = session["user"]
    if not user:
        # Fetch user info from GitHub if not in session
        resp = github.get("/user")
        if not resp.ok:
            return redirect(url_for('index'))
        
        user_info = resp.json()
        session["user"] = user_info
        print("User Info Fetched and Saved:", session["user"], flush=True)
    
    # Retrieve the token from the session
    github_token = session.get("GITHUB_TOKEN")
    if not github_token:
        github_token = session.get("github_oauth_token", {}).get("access_token")
        if github_token:
            session["GITHUB_TOKEN"] = github_token
    print("GITHUB_TOKEN from session:", github_token, flush=True)

    
    
    return render_template("home.html", user=session.get("user"))

def fetch_projects_from_github():
    """Fetch the list of projects from the GitHub repository."""
    try:
        response = requests.get(GITHUB_API_JSONS)
        response.raise_for_status()
        contents = response.json()

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
                            "project_link": project_url
                        })
        return projects
    except requests.RequestException as e:
        print(f"Error fetching data from GitHub: {e}")
        return []

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

def get_github_issues():
    GITHUB_TOKEN = session.get("github_oauth_token", {}).get("access_token")
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

def check_github_token_scopes(token, required_scopes):
    url = "https://api.github.com/user"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        scopes = response.headers.get("X-OAuth-Scopes", "")
        scopes_set = set(scopes.split(", "))
        required_scopes_set = set(required_scopes)
        return required_scopes_set.issubset(scopes_set)
    else:
        print(f"Failed to check token scopes: {response.status_code}")
        return False
    
@app.route("/submit", methods=["POST"])
def handle_submission():
    # Get the form data (action and schema_entry)
    action = request.form.get("action")
    schema_entry = makeFormJson()  # Assuming the form data is a dictionary
    print("attempting to get issue number")
    print("session issue number: ", session.get('issue_number', 'N/A'))
    
    GITHUB_TOKEN = session.get("github_oauth_token", {}).get("access_token")
    print("submission token: ", GITHUB_TOKEN)
    if not GITHUB_TOKEN:
        return jsonify({"success": False, "error": "GitHub token not found in session"}), 401
    # Check if the token has the required scopes
    required_scopes = ["public_repo"]
    if not check_github_token_scopes(GITHUB_TOKEN, required_scopes):
        return jsonify({"success": False, "error": "GitHub token does not have the required scopes"}), 403


    if action == "print_json":
        return render_template("print_json.html", schema_entry=json.dumps(schema_entry, indent=4))

    # Call the function to process the action
    result = process_submission_action(session.get('issue_number', None), action, schema_entry, GITHUB_API_URL, REPO_OWNER, GITHUB_REPO)
    print("ACTION RESULT: ", result)

    # Return the appropriate response based on the result from the function
    if action in ["submit_to_github", "update_github"]:  # Check if the action was a submission
        if result.get("success"):
            message = result.get("message", "Action completed successfully!")
            issue_url = result.get("issue_url")
            return render_template("success.html", message=message, issue_url=issue_url)
        else:
            error_message = result.get("error", "An unexpected error occurred.")
            error_details = result.get("details", None)  # Include additional details if available
            return render_template("error.html", error=error_message, details=error_details)
        # if isinstance(result, dict) and result.get("success"):
        #     message = "Issue submitted successfully!" if action == "submit_to_github" else "Issue updated successfully!"
        #     return render_template("success.html", message=message)
        # else:
        #     return result, 500
    else:
        return result

@app.route("/success")
def success():
    message = request.args.get("message", "Entry submitted successfully.")
    return render_template("success.html", message=message)

@app.route("/update_entry", methods=["GET", "POST"])
def update_entry():
    print(">>> ", request.method)
    GITHUB_TOKEN = session.get("github_oauth_token", {}).get("access_token")
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
                #print(f"Cleaned Issue Body: {issue_body_cleaned}")  # Log the cleaned version

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
    GITHUB_TOKEN = session.get("github_oauth_token", {}).get("access_token")

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
            issue_url = f"https://github.com/{REPO_OWNER}/{GITHUB_REPO}/issues/{issue_number}"
            return render_template("success.html", message="Issue updated successfully!", issue_url=issue_url)
        else:
            error_details = comment_response.json()
            return render_template("error.html", error="Failed to add update comment.", details=error_details)
            #return jsonify({"success": False, "error": comment_response.json()}), comment_response.status_code
    else:
        error_details = response.json()
        return render_template("error.html", error="Failed to update issue.", details=error_details)
        #return jsonify({"success": False, "error": response.json()}), response.status_code


def create_issue(title, body):
    """
    Create a new issue in the GitHub repository.
    """
    GITHUB_TOKEN = session.get("github_oauth_token", {}).get("access_token")
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    issue_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"

    data = {
        "title": title,
        "body": body,
    }

    response = requests.post(issue_url, json=data, headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Failed to create issue: {response.status_code}, {response.text}")
        return None

def update_issue(issue_number, title, body):
    """
    Update an existing issue in the GitHub repository.
    """
    GITHUB_TOKEN = session.get("github_oauth_token", {}).get("access_token")
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    issue_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{issue_number}"

    data = {
        "title": title,
        "body": body,
    }

    response = requests.patch(issue_url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to update issue: {response.status_code}, {response.text}")
        return None


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)  # , ssl_context=("server.crt", "server.key"))

# Removing this route, as Flask-Dance handles the OAuth login automatically apparently
# @app.route('/github')
# def login():
#     """Log in a registered or authenticated user."""
#     if not github.authorized:
#         return redirect(url_for('github.login'))
#     res = github.get('/user')
#     assert res.ok
#     return render_template("home.html", user=res)
    
    #if res.ok:
    #    res_json = res.json()
    #    return redirect(url_for("home")) #f"You are logged in as {res.json()['login']} on GitHub."