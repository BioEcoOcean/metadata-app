from flask import request

def makeFormJson(): 
    if request.method == "POST":
        # Step 1: Collect and sanitize submitted form data
        submitted_data = request.form.to_dict(flat=False)  # Support multi-select fields
        sanitized_data = {}
        for key, value in submitted_data.items():
            sanitized_data[key] = value if isinstance(value, list) else value

        # Extract start and end dates from form submission
        temporal_coverage_start = sanitized_data.get("temporal_coverage_start", [""])[0]
        temporal_coverage_end = sanitized_data.get("temporal_coverage_end", [""])[0]

        # Handle keywords dynamically as a list
        keywords = request.form.getlist("keywords")  # Collect all 'keywords' input values
        sanitized_data["keywords"] = keywords if keywords else []

        # Handle the spatialCoverage field
        if sanitized_data["spatial_coverage_name"] and sanitized_data["spatial_coverage_identifier"]:
            sanitized_data["spatialCoverage"] = [{
                "@type": "Place",
                "name": sanitized_data["spatial_coverage_name"],
                "identifier": sanitized_data["spatial_coverage_identifier"]
            }]
        # Get the license field from the form submission
        license_data = sanitized_data.get("license", [""])[0]
        license_name, license_url = license_data.split("|") if license_data else (license_data, "")
        
        # Extract funding and funder details
        funder_name = sanitized_data.get("funder_name", [])
        funder_url = sanitized_data.get("funder_url", [])
        funding_name = sanitized_data.get("funding_name", [])
        funding_identifier = sanitized_data.get("funding_identifier", [])

        funders = []
        for i in range(max(len(funder_name), len(funder_url))):
            funders.append({
                "@type": "FundingAgency",
                "name": funder_name[i] if i < len(funder_name) else "",
                "legalName": funder_name[i] if i < len(funder_name) else "",
                "url": funder_url[i] if i < len(funder_url) else ""
            })

        # Restructure the funding field
        funding = []
        for i in range(max(len(funding_name), len(funding_identifier))):
            funding.append({
                "@type": "MonetaryGrant",
                "name": funding_name[i] if i < len(funding_name) else "",
                "identifier": funding_identifier[i] if i < len(funding_identifier) else "",
                "funder": funders  # Add the funders list
            })
        sanitized_data["funding"] = funding

        #Extract contact details
        #sanitized_data["contact_names"] = request.form.getlist("contact_names")
        #sanitized_data["contact_emails"] = request.form.getlist("contact_emails")
        #sanitized_data["contact_roles"] = request.form.getlist("contact_roles")
        #sanitized_data["contact_ids"] = request.form.getlist("contact_ids") if "contact_ids" in request.form else [] 


        print("bounds: ", sanitized_data.get("north", [""])[0])
        print("san data: ", sanitized_data)

        # Step 2: Build schema_entry JSON with mappings
        schema_entry = {
            "@context": {
                "@vocab": "https://schema.org/",
                "geosparql": "http://www.opengis.net/ont/geosparql#"
            },
            "@type": "Project",
            "@id": f"https://example.com/json/{sanitized_data.get('project_name', ['Unnamed'])[0]}",
            "name": sanitized_data.get("project_name", [""])[0],
            "url": sanitized_data.get("url", [""])[0],
            "description": sanitized_data.get("description", [""])[0],
            "contactPoint": [],
            "frequency": sanitized_data.get("frequency", ["Never"])[0],
            "temporalCoverage": f"{temporal_coverage_start}/{temporal_coverage_end}" if temporal_coverage_start and temporal_coverage_end else "",
            "keywords": [keyword.strip() for keyword in sanitized_data.get("keywords", []) if keyword.strip()],
            "license": {
                "@type": "CreativeWork",
                "name": license_name,
                "url": license_url
            },
            "spatialCoverage": [
                {
                    "@type": "Place",
                    "name": sanitized_data.get("spatial_coverage_name", [""])[0],
                    "identifier": sanitized_data.get("spatial_coverage_identifier", [""])[0],
                    "geo":{
                        "@type": "GeoShape",
                        "description": "schema.org expects lat long (Y X) coordinate order.  Box syntax is: miny minx maxy maxx",
                        "box": f'{sanitized_data.get("south", [""])[0]} {sanitized_data.get("west", [""])[0]} {sanitized_data.get("north", [""])[0]} {sanitized_data.get("east", [""])[0]}'
                    }
                }
            ],
            "variableMeasured": [],
            "measurementTechnique": [],
            "funding": sanitized_data.get("funding", [])
        }

        # Step 3: Handle BioEco EOVs and Other EOVs, and append to variableMeasured
        for eov_category in ['bioeco_eovs', 'other_eovs','ebvs']:
            if eov_category in sanitized_data:
                for eov in sanitized_data[eov_category]:
                    name, propertyID = eov.split("|")
                    schema_entry["variableMeasured"].append({
                        "@type": "PropertyValue",
                        "name": name,
                        "propertyID": propertyID
                    })

        # Step 4: Add measurementtechnique - platforms and SOPs, if applicable
        if 'measurement_platforms' in sanitized_data:
            for platform in sanitized_data['measurement_platforms']:
                name, propertyID = platform.split("|")
                schema_entry["measurementTechnique"].append({
                    "@type": "PropertyValue",
                    "name": name,
                    "propertyID": propertyID
                })

        # Add contact points
        contact_names = request.form.getlist("contact_names")
        contact_emails = request.form.getlist("contact_emails")
        contact_roles = request.form.getlist("contact_roles")
        contact_ids = request.form.getlist("contact_ids")
        num_contacts = max(len(contact_names), len(contact_emails), len(contact_roles), len(contact_ids))

        # Iterate through the list, for the number of contacts
        for i in range(num_contacts):
            # Safely get each field for the current contact, defaulting to empty string if not available
            name = contact_names[i] if i < len(contact_names) else ""
            email = contact_emails[i] if i < len(contact_emails) else ""
            role = contact_roles[i] if i < len(contact_roles) else ""
            identifier = contact_ids[i] if i < len(contact_ids) else ""

            # Add the contact entry to the 'contactPoint' list
            schema_entry['contactPoint'].append({
                "@type": "ContactPoint",
                "name": name,
                "email": email,
                "role": role,
                "identifier": identifier
            })
       
        # Add SOP URLs to measurementTechnique
        sop_urls = [url.strip() for url in request.form.getlist("sops") if url.strip()]
        if sop_urls:
            for sop in sop_urls:
                schema_entry["measurementTechnique"].append({
                    "@type": "URL",
                    "url": sop
                })
        return schema_entry  # Return the schema_entry object