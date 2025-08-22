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
import csv
from flask_caching import Cache
from mappings import schema_field_mapping, actions_field_mapping, frequency_field_mapping
from processMappings import map_form_to_schema
from generateForm import generate_form
from submitAction import process_submission_action
from makeFormIntoJson import makeFormJson
from datetime import datetime
from helpers import set_flask_environment
from werkzeug.middleware.proxy_fix import ProxyFix
from dois import ObisDoi

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
        print("Calling GitHub API on landing page...", flush=True) # debugging why hanging
        resp = github.get("/user", timeout=10)
        print("GitHub API responded", flush=True)
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
        print("Calling GitHub API for getting issues...", flush=True)
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print("GitHub API responded", flush=True)
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
    schema_entry, actions_json, metadata_frequency = makeFormJson()  #pass the form output to makeFormJson function
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

    # Call the function to process the action, passing all 3 json objects
    result = process_submission_action(
        session.get('issue_number', None), 
        action, 
        schema_entry, actions_json, metadata_frequency,
        GITHUB_API_URL, REPO_OWNER, GITHUB_REPO)
    print("ACTION RESULT: ", result)
    
    # Handle print_json action
    if action == "print_json":
        return render_template("print_json.html", 
        schema_entry=json.dumps(schema_entry, indent=4),
        actions_json=json.dumps(actions_json, indent=4),
        metadata_frequency=json.dumps(metadata_frequency, indent=4))

    # Handle save draft action
    if action == "save_draft":
        if result.get("success"):
            message = result.get("message", "Draft saved successfully!")
            issue_url = result.get("issue_url")
            return render_template("success.html", message=message, issue_url=issue_url)
        else:
            error_message = result.get("error", "An unexpected error occurred.")
            error_details = result.get("details", None)
            return render_template("error.html", error=error_message, details=error_details)   

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
        issue for issue in issues
        if any(label["name"] in ["metadata submission", "draft submission"] for label in issue.get("labels", []))
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
            #print("Calling GitHub API in update entry route...", flush=True) #debugging
            response = requests.get(issue_url, headers=headers, timeout=10)
            #print("GitHub API responded", flush=True)
            response_data = response.json()  # Debug: Inspect the full response from GitHub
            print(f"Response Data: {response_data}")

            if response.status_code == 200:
                # Parse the issue data
                issue_data = response.json()
                issue_body = issue_data["body"]
                json_blocks = extract_json_blocks(issue_body)
                schema_entry = json_blocks.get("Metadata Submission")
                actions_json = json_blocks.get("Actions JSON")
                metadata_frequency = json_blocks.get("Metadata Frequency")

                # Map the GitHub issue data to schema format
                mapped_schema_entry = map_form_to_schema(schema_entry, schema_field_mapping)
                mapped_actions_entry = map_form_to_schema(actions_json, actions_field_mapping)
                mapped_metadata_frequency = map_form_to_schema(metadata_frequency, frequency_field_mapping)
                form_html = generate_form(prefilled_data=mapped_schema_entry,
                    actions_data=mapped_actions_entry,
                    frequency_data=mapped_metadata_frequency)

                return render_template("update_entry.html", issues=filtered_issues, form_html=form_html, issue_number=issue_number)
            else:
                return jsonify({"success": False, "error": response.json()})
        else:
            return jsonify({"success": False, "error": "No issue selected."})

@app.route("/remove_entry", methods=["GET", "POST"])
def remove_entry():
    if not github.authorized:
        return redirect(url_for("github.login"))

    user = session.get("user")
    if not user:
        resp = github.get("/user")
        if not resp.ok:
            return redirect(url_for('index'))
        user = resp.json()
        session["user"] = user

    github_token = session.get("github_oauth_token", {}).get("access_token")
    headers = {"Authorization": f"token {github_token}"}
    username = user.get("login")

    # Fetch issues created by this user with the "metadata submission" label
    params = {"creator": username, "labels": "metadata submission"}
    response = requests.get(GITHUB_API_URL, headers=headers, params=params, timeout=10)
    issues = response.json() if response.status_code == 200 else []

    if request.method == "POST":
        issue_number = request.form.get("selected_issue")
        if not issue_number:
            return render_template("remove_entry.html", issues=issues, error="No issue selected.")

        # Update labels on the selected issue
        issue_url = f"{GITHUB_API_URL}/{issue_number}"
        # Get current labels
        issue_resp = requests.get(issue_url, headers=headers, timeout=10)
        if issue_resp.status_code != 200:
            return render_template("remove_entry.html", issues=issues, error="Could not fetch issue details.")

        current_labels = [label["name"] for label in issue_resp.json().get("labels", [])]
        # Remove "metadata submission", add "remove entry"
        new_labels = [l for l in current_labels if l != "metadata submission"]
        if "remove entry" not in new_labels:
            new_labels.append("remove entry")

        patch_resp = requests.patch(issue_url, headers=headers, json={"labels": new_labels})
        if patch_resp.status_code == 200:
            return render_template("success.html", issue_url=issue_url, message="Entry marked for removal.")
        else:
            return render_template("remove_entry.html", issues=issues, issue_url=issue_url, error="Failed to update issue labels.")

    return render_template("remove_entry.html", issues=issues)


@app.route('/generate_doi', methods=['POST'])
def generate_doi():
    data = request.json
    doi_obj = ObisDoi()
    
    # Set basic info
    doi_obj.title = data.get('title')
    doi_obj.url = data.get('url')
    
    # Set creators info (now supports multiple)
    creators_data = data.get('creators', [])
    if creators_data:
        doi_obj.creators = []
        for creator in creators_data:
            creator_entry = {
                "name": creator.get('name'),
                "nameType": creator.get('nameType', 'Organizational')
            }
            
            # Add given/family names for Personal type
            if creator.get('nameType') == 'Personal':
                if creator.get('givenName'):
                    creator_entry['givenName'] = creator.get('givenName')
                if creator.get('familyName'):
                    creator_entry['familyName'] = creator.get('familyName')
            
            doi_obj.creators.append(creator_entry)
    else:
        # Fallback to default OBIS creator if no creators provided
        doi_obj.creators = [{
            "name": "Ocean Biodiversity Information System (OBIS)",
            "nameType": "Organizational",
        }]
    
    # Set publisher
    doi_obj.publisher = data.get('publisher', 'Ocean Biodiversity Information System (OBIS)')
    
    try:
        result = doi_obj.reserve()
        # DataCite returns the DOI in result['data']['id']
        if 'data' in result and 'id' in result['data']:
            return jsonify({'doi': result['data']['id']})
        else:
            return jsonify({'error': result}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @app.route("/submit_update", methods=["POST"])  #Note to self: check why I have this route still? I thik it's included in submitAction so doesn't need to be included here anymore
# def submit_update():
#     updated_data = request.form.to_dict()  # Get form data as a dictionary
#     issue_number = request.form.get("issue_number")  # Get the selected issue number
#     GITHUB_TOKEN = session.get("github_oauth_token", {}).get("access_token")

#     # Map the form data to the schema format
#     schema_entry = makeFormJson(updated_data)  # Mapping form data to schema format

#     # Construct the GitHub issue URL and the payload to send
#     issue_url = f"https://api.github.com/repos/{REPO_OWNER}/{GITHUB_REPO}/issues/{issue_number}"
#     comments_url = f"https://api.github.com/repos/{REPO_OWNER}/{GITHUB_REPO}/issues/{issue_number}/comments"
#     headers = {"Authorization": f"token {GITHUB_TOKEN}"}

#     # GitHub Payload includes the title and body, with the body containing the metadata as formatted JSON
#     payload = {
#         "title": f"Updated Submission: {updated_data.get('name', 'Unnamed Program')}",
#         "body": "### Metadata Submission\n\n" + json.dumps(schema_entry, indent=4)  # Send the mapped schema as part of the body
#     }

#     # Step 1: Update the issue with new data (PATCH request)
#     response = requests.patch(issue_url, json=payload, headers=headers)

#     # Check if the issue was updated successfully
#     if response.status_code == 200:
#         # Step 2: Add a comment to the issue (POST request)
#         comment_payload = {
#             "body": f"Entry updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"  # Add a timestamp for the update
#         }
#         comment_response = requests.post(comments_url, json=comment_payload, headers=headers)

#         # Check if the comment was added successfully
#         if comment_response.status_code == 201:
#             issue_url = f"https://github.com/{REPO_OWNER}/{GITHUB_REPO}/issues/{issue_number}"
#             return render_template("success.html", message="Issue updated successfully!", issue_url=issue_url)
#         else:
#             error_details = comment_response.json()
#             return render_template("error.html", error="Failed to add update comment.", details=error_details)
#     else:
#         error_details = response.json()
#         return render_template("error.html", error="Failed to update issue.", details=error_details)

####### Helper functions ########
def fetch_projects_from_github():
    """Fetch the list of projects from the csv in the GitHub repository"""
    csv_url = "https://raw.githubusercontent.com/BioEcoOcean/metadata-tracking-dev/refs/heads/main/data/bioeco_list.csv"
    projects = []
    try:
        response = requests.get(csv_url, timeout=10)
        response.raise_for_status()
        decoded_content = response.content.decode('utf-8')
        reader = csv.DictReader(decoded_content.splitlines())
        
        for row in reader:
            # Expecting columns: 'name', 'project_link'
            projects.append({
                "name": row.get("Project Name", "Unnamed"),
                "project_link": row.get("URL", "")
            })
        # Sort projects alphabetically by name (case-insensitive)
        projects.sort(key=lambda x: x["name"].lower())
        return projects
    except Exception as e:
        print(f"Error fetching or parsing CSV: {e}")
        return []

def check_github_token_scopes(token, required_scopes):
    url = "https://api.github.com/user"
    headers = {"Authorization": f"token {token}"}
    print("Calling GitHub API...", flush=True) # debugging why hanging
    response = requests.get(url, headers=headers, timeout=10)
    print("GitHub API responded", flush=True)
    
    if response.status_code == 200:
        scopes = response.headers.get("X-OAuth-Scopes", "")
        scopes_set = set(scopes.split(", "))
        required_scopes_set = set(required_scopes)
        return required_scopes_set.issubset(scopes_set)
    else:
        print(f"Failed to check token scopes: {response.status_code}")
        return False

def extract_json_blocks(issue_body):
    # Find all blocks between ```json ... ```
    blocks = re.findall(r"### (.*?)\n```json\n(.*?)\n```", issue_body, re.DOTALL)
    result = {}
    for header, json_str in blocks:
        try:
            result[header.strip()] = json.loads(json_str)
        except Exception as e:
            result[header.strip()] = None
    return result




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