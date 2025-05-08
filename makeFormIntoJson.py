from flask import request
def clean_dict(data):
    return {k: v for k, v in data.items() if v}

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

        #Get outputs
        outputs = request.form.getlist("outputs")  # Collect all 'outputs' input values
        sanitized_outputs = [output.strip() for output in outputs if output.strip()]
        sanitized_data["outputs"] = sanitized_outputs if sanitized_outputs else []

        
        # Extract funding and funder details
        funder_name = sanitized_data.get("funder_name", [])
        funder_url = sanitized_data.get("funder_url", [])
        funding_name = sanitized_data.get("funding_name", [])
        funding_identifier = sanitized_data.get("funding_identifier", [])
        
        # Initialize the funding list
        funding = []
        # Iterate through funding information and create individual entries
        for i in range(max(len(funding_name), len(funding_identifier), len(funder_name), len(funder_url))):
            # Create a single funder entry
            funder = {
                "@type": "FundingAgency",
                "name": funder_name[i] if i < len(funder_name) else "",
                "legalName": funder_name[i] if i < len(funder_name) else "",
                "url": funder_url[i] if i < len(funder_url) else ""
            }

            # Create a single funding entry with its associated funder
            funding_entry = {
                "@type": "MonetaryGrant",
                "name": funding_name[i] if i < len(funding_name) else "",
                "identifier": funding_identifier[i] if i < len(funding_identifier) else "",
                "funder": [funder] if funder["name"] or funder["url"] else []  # Only add if funder has data
            }

            # Append the funding entry if it has meaningful data
            if funding_entry["name"] or funding_entry["identifier"] or funding_entry["funder"]:
                funding.append(funding_entry)

        # for i in range(max(len(funder_name), len(funder_url))):
        #     if funder_name or funder_url:
        #         funders.append({
        #             "@type": "FundingAgency",
        #             "name": funder_name[i] if i < len(funder_name) else "",
        #             "legalName": funder_name[i] if i < len(funder_name) else "",
        #             "url": funder_url[i] if i < len(funder_url) else ""
        #         })

        # # Restructure the funding field
        # funding = []
        # for i in range(max(len(funding_name), len(funding_identifier))):
        #     funding.append({
        #         "@type": "MonetaryGrant",
        #         "name": funding_name[i] if i < len(funding_name) else "",
        #         "identifier": funding_identifier[i] if i < len(funding_identifier) else "",
        #         "funder": funders if funders else None # Add the funders list
        #     })

        #Extract contact details
        #sanitized_data["contact_names"] = request.form.getlist("contact_names")
        #sanitized_data["contact_emails"] = request.form.getlist("contact_emails")
        #sanitized_data["contact_roles"] = request.form.getlist("contact_roles")
        #sanitized_data["contact_ids"] = request.form.getlist("contact_ids") if "contact_ids" in request.form else [] 


        print("bounds: ", sanitized_data.get("north", [""])[0])
        print("san data: ", sanitized_data)

        ########## Step 2: Build schema_entry JSON with mappings ##########
        schema_entry = {
            "@context": {
                "@vocab": "https://schema.org/",
                "geosparql": "http://www.opengis.net/ont/geosparql#"
            },
            "@type": "Project",
            "@id": f"https://example.com/json/{sanitized_data.get('project_name', ['Unnamed'])[0]}",
            "name": sanitized_data.get("project_name", [""])[0],
            "url": sanitized_data.get("url", [""])[0],          
            "frequency": sanitized_data.get("frequency", ["Never"])[0],
            "license": {
                "@type": "CreativeWork",
                "name": license_name,
                "url": license_url
            },
            "measurementTechnique": [],
        }

        # Conditionally add fields if they are not blank
        if sanitized_data.get("description", [""])[0]:
            schema_entry["description"] = sanitized_data.get("description", [""])[0]

        if sanitized_data.get("projid", [""])[0]:
            schema_entry["identifier"] = {
                "@type": "PropertyValue",
                "description": sanitized_data.get("project_name", [""])[0],
                #"propertyID": sanitized_data.get("TBD", [""])[0],
                "url": sanitized_data.get("projid", [""])[0],
            },

        keywords = [keyword.strip() for keyword in sanitized_data.get("keywords", []) if keyword.strip()]
        if keywords:
            schema_entry["keywords"] = keywords

        if temporal_coverage_start and temporal_coverage_end:
            schema_entry["temporalCoverage"] = f"{temporal_coverage_start}/{temporal_coverage_end}"
        elif temporal_coverage_start:
            schema_entry["temporalCoverage"] = temporal_coverage_start

        if sanitized_data.get("spatial_coverage_name", [""])[0] and sanitized_data.get("spatial_coverage_identifier", [""])[0]:
            spatial_coverage = {
                    "@type": "Place",
                    "name": sanitized_data.get("spatial_coverage_name", [""])[0],
                    "identifier": sanitized_data.get("spatial_coverage_identifier", [""])[0],
                }

            # Check if all geo coordinates are present
            south = sanitized_data.get("south", [""])[0]
            west = sanitized_data.get("west", [""])[0]
            north = sanitized_data.get("north", [""])[0]
            east = sanitized_data.get("east", [""])[0]

            if south and west and north and east:
                spatial_coverage["geo"] = {
                        "@type": "GeoShape",
                        "description": "schema.org expects lat long (Y X) coordinate order. Box syntax is: miny minx maxy maxx",
                        "box": f"{south} {west} {north} {east}"
                }
            schema_entry["spatialCoverage"] = [spatial_coverage]
        
        if sanitized_outputs:
            #schema_entry.setdefault("isRelatedTo", [])
            schema_entry["isRelatedTo"] = sanitized_outputs

        # if sanitized_data.get("funding", []):
        #     schema_entry["funding"] = sanitized_data.get("funding", [])
        if funding:  # Only add to schema_entry if the funding list is not empty
            schema_entry["funding"] = funding


        # Step 3: Handle EOVs, and append to variableMeasured
        variable_measured = []
        for eov_category in ['bioeco_eovs', 'other_eovs','ebvs']:
            if eov_category in sanitized_data:
                for eov in sanitized_data[eov_category]:
                    name, propertyID = eov.split("|")
                    if name and propertyID:  # Ensure both fields have data
                        variable_measured.append({
                            "@type": "PropertyValue",
                            "name": name,
                            "propertyID": propertyID
                        })
        # Add variableMeasured to schema_entry only if there are valid variables
        if variable_measured:
            schema_entry["variableMeasured"] = variable_measured

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

        contact_points = []

        # Iterate through the list, for the number of contacts
        for i in range(num_contacts):
            # Safely get each field for the current contact, defaulting to empty string if not available
            name = contact_names[i] if i < len(contact_names) else ""
            email = contact_emails[i] if i < len(contact_emails) else ""
            role = contact_roles[i] if i < len(contact_roles) else ""
            identifier = contact_ids[i] if i < len(contact_ids) else ""

            # Add the contact entry to the 'contactPoint' list
            if any([name, email, role, identifier]):
                contact_points.append({
                    "@type": "ContactPoint",
                    "name": name,
                    "email": email,
                    "role": role,
                    "identifier": identifier
                })

            if contact_points:
                schema_entry["contactPoint"] = contact_points
       
        # Add SOP URLs to measurementTechnique
        sop_urls = [url.strip() for url in request.form.getlist("sops") if url.strip()]
        sop_obps_values = request.form.getlist("sop_obps")  # Get the OBPs checkbox values

        if sop_urls:
            for i, sop in enumerate(sop_urls):
                # Start building the SOP entry
                sop_entry = {
                    "@type": "CreativeWork",
                    "url": sop
                }

                # Add isPartOf only if OBPs checkbox is "yes"
                if i < len(sop_obps_values) and sop_obps_values[i].lower() == "yes":
                    sop_entry["isPartOf"] = {
                        "@type": "CreativeWork",
                        "name": "Ocean Best Practices",
                        "url": "https://www.oceanbestpractices.org/"
                    }

                # Append the SOP entry to the measurementTechnique
                schema_entry["measurementTechnique"].append(sop_entry)
        return schema_entry  # Return the schema_entry object