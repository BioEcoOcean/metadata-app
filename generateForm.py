import json
# Load form schema


def generate_form(prefilled_data=None):
    with open("schema.json") as f:
        form_schema = json.load(f)

        form_html = ""
        prefilled_data = prefilled_data or {}
        print(f"Prefilled data: {json.dumps(prefilled_data, indent=4)}")

        form_html += """
        <h2>General programme info</h2>
        """
        # Project Name
        form_html += f"""
        <label for='project_name'>Project Name:<span class="required">*</span><span class="info-circle" data-tooltip="Enter the title of the programme/project.">ⓘ</span></label>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('name', 'N/A')}</div>
        <input type='text' name='project_name' id='project_name' value="{prefilled_data.get('name', '')}" required><br><br>
        """
        # URL
        form_html += f"""
        <label for='url'>URL:<span class="required">*</span><span class="info-circle" data-tooltip="Provide the URL for the project.">ⓘ</span></label>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('url', 'N/A')}</div>
        <input type='url' name='url' id='url' value="{prefilled_data.get('url', '')}" required><br><br>
        """
        # Description
        form_html += f"""
        <label for='description'>Description: <span class="info-circle" data-tooltip="Provide a brief description of the project.">ⓘ</span></label>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('description', 'N/A')}</div>
        <textarea name='description' id='description'>{prefilled_data.get('description', '')}</textarea><br><br>
        """
        # Contact Information
        form_html += f"""
        <label for='contact_name'>Programme Contacts:<span class="required">*</span><span class="info-circle" data-tooltip="Provide contact information for your project.">ⓘ</span></label>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('contactPoint', {}).get('name', 'N/A')}</div>
        
        """
        # <input type='text' name='contact_name' id='contact_name' value="{prefilled_data.get('contactPoint', {}).get('name', '')}" required><br><br>
        # # Contact email
        # form_html += f"""
        # <label for='contact_email'>Contact Email:<span class="required">*</span><span class="info-circle" data-tooltip="Enter the contact email address.">ⓘ</span></label>
        # <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('contactPoint', {}).get('email', 'N/A')}</div>
        # <input type='email' name='contact_email' id='contact_email' value='{prefilled_data.get('contactPoint', {}).get('email', '')}' required><br><br>
        # """
        form_html += f"""
        <div id="contacts-container">
        <!-- New contact inputs will be added here -->
        </div>
        <button type="button" onclick="addContactInput()">Add Contact</button>
        <br><br>
        """

        #Temporal coverage
        form_html += f"""
        <label for='temporal_coverage'>Temporal Coverage:<span class="required">*</span></span><span class="info-circle" data-tooltip="Specify the date range for the project.">ⓘ</span></label>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('temporalCoverage', 'N/A')}</div>
        <b>Start date: </b> <input type='date' name='temporal_coverage_start' id='temporal_coverage_start'
            value="{prefilled_data.get('temporalCoverage', 'YYYY-MM-DD').split('/')[0] if prefilled_data.get('temporalCoverage') else 'YYYY-MM-DD'}" required><br><br>
        <b>End date: </b> <input type='date' name='temporal_coverage_end' id='temporal_coverage_end'
            value="{prefilled_data.get('temporalCoverage', 'YYYY-MM-DD').split('/')[1] if prefilled_data.get('temporalCoverage') else 'YYYY-MM-DD'}" required><br><br>
        """
        #keywords section
        keywords = prefilled_data.get("keywords", [])
        keywords_display = ", ".join(keywords) if keywords else "N/A"
        form_html += "<label for='keywords'>Keywords: <span class='info-circle' data-tooltip='Enter relevant keywords for the project.'>ⓘ</span></label>"
        form_html += f"""
        <div class='previous'><strong>Previously entered: </strong>{keywords_display}</div>
        """
        form_html += "<div id='keywords-container'>"
        for keyword in keywords:
            form_html += f'<input type="text" name="keywords" class="keyword-input" value="{keyword}" placeholder="Enter a keyword"><br>'
        form_html += "</div>"
        form_html += '<button type="button" onclick="addKeywordInput()">Add Another Keyword</button><br><br>'


        # Spatial Coverage
        regional_id_str = 'MRGID: '
        form_html += f"""
        <label for="spatial_coverage_name">Spatial Coverage <span class='info-circle' data-tooltip='Specify the name and MRGID of the area where the programme takes place. Use the search box to select an area from Marine Regions. Use the map below to also add bounding area coordinates.'>ⓘ</span></label>Start typing to search for a marine location. Names are obtained from <a href="https://www.marineregions.org/gazetteer.php?p=search">Marine Regions Gazetteer</a>.<br>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('spatialCoverage', {}).get("name", 'N/A')} {regional_id_str}{prefilled_data.get('spatialCoverage', {}).get("identifier", 'N/A')}

        </div>
        <!-- Search Box -->
        <input type="text" id="search_regions" placeholder="Search for a region..." />

        <!-- Table to display search results -->
        <table id="regions_table" style="width:100%; display:none;">
            <thead>
                <tr>
                    <th>Region Name</th>
                    <th>Type</th>
                    <th>Source</th>
                </tr>
            </thead>
            <tbody>
                <!-- Dynamically populated rows will go here -->
            </tbody>
        </table>
        <label for="spatial_coverage_identifier">Auto-populated fields:</label>
        Name: <input type="text" name="spatial_coverage_name" id="spatial_coverage_name" value="{prefilled_data.get('spatialCoverage', {}).get("name", '')}" readonly><br>
        MRGID: <input type="text" name="spatial_coverage_identifier" id="spatial_coverage_identifier" value="{prefilled_data.get('spatialCoverage', {}).get("identifier", '')}" readonly><br><br>
        """
        form_html += f"""
        <a>Draw Bounding Area</a>
        <div id="map" style="width: 60%; height: 300px;"></div>
        <label for="maxy" id="maxy">North (max latitude):</label>
        <input type="text" id="north" name="north" readonly><br>

        <label for="south" id="miny">South (min latitude):</label>
        <input type="text" id="south" name="south" readonly><br>

        <label for="east" id="maxx">East (max longitude):</label>
        <input type="text" id="east" name="east" readonly><br>

        <label for="west" id="minx">West (min longitude):</label>
        <input type="text" id="west" name="west" readonly><br>
        <br>

        """
        # License section
        license_field = form_schema.get("categories_definition", {}).get("license", None)
        if license_field:
            license_value = prefilled_data.get("license", {}).get("name", 'N/A')

            # Show previously entered value above the field
            form_html += f"<label for='license'>{license_field['name']}:<span class='required'>*</span><span class='info-circle' data-tooltip='Select the most appropriate license for the programme metadata.'>ⓘ</span></label>"
            form_html += f"<p>{license_field['description']}</p>"
            if license_value:
                form_html += f"<div class='previous'><strong>Previously entered:</strong> {license_value}</div>"
            else:
                form_html += "<div class='previous'><strong>Previously entered:</strong> N/A</div>"

            # License dropdown
            form_html += "<select name='license' id='license' required>"
            form_html += "<option value='' disabled>Select option</option>"
            for option_key, option in license_field['options'].items():
                selected = "selected" if option['name'] == license_value else ""
                form_html += f"<option value='{option['name']}|{option['url']}' {selected}>{option['name']}</option>"

            form_html += "</select><br><br>"
        else:
            # Handle the case where 'license' is missing
            form_html += "<p><strong>Error: License field is missing in the schema.</strong></p>"

        #Update frequency
        form_html += f"""
        <label for='frequency'>Update frequency:<span class="required">*</span><span class='info-circle' data-tooltip='Select the frequency you expect metadata to be updated.'>ⓘ</span></label>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('frequency', 'N/A')}</div>
        <select name="frequency" id="frequency" required>
            <option value="" disabled {'selected' if not prefilled_data.get('frequency', '') else ''}>Select an option</option>
            <option value="never" {'selected' if prefilled_data.get('frequency', '') == 'never' else ''}>Never</option>
            <option value="yearly" {'selected' if prefilled_data.get('frequency', '') == 'yearly' else ''}>Yearly</option>
            <option value="monthly" {'selected' if prefilled_data.get('frequency', '') == 'monthly' else ''}>Monthly</option>
            <option value="weekly" {'selected' if prefilled_data.get('frequency', '') == 'weekly' else ''}>Weekly</option>
            <option value="daily" {'selected' if prefilled_data.get('frequency', '') == 'daily' else ''}>Daily</option>
            <option value="hourly" {'selected' if prefilled_data.get('frequency', '') == 'hourly' else ''}>Hourly</option>
        </select>
        """

        def format_special_category_values(prefilled_data, category_key):
            """
            Handles special formatting for `variableMeasured` and `measurementTechnique`.
            """
            if category_key in prefilled_data:
                items = prefilled_data[category_key]
                return ", ".join([item["name"] for item in items if "name" in item]) if items else "N/A"
            return "N/A"
        def process_fields(fields, prefilled_data, category_value):
            """
            Processes fields within a category and generates the HTML for them.
            """
            html = ""
            for field_key, field in fields.items():
                value = prefilled_data.get(field_key, [])
                if "options" in field:  # Checkbox handling
                    html += f"<label for='{field_key}'>{field.get('name', 'Unknown Field')}</label>"

                    # Ensure category_value is a list if it's a string
                    category_value_list = category_value.split(", ") if isinstance(category_value, str) else category_value

                    for option_key, option in field["options"].items():
                        # Check if the option name is in the list of previously entered values
                        checked = "checked" if option["name"] in category_value_list else ""
                        property_id = option.get("propertyID", "")
                        if isinstance(property_id, list):
                            property_id = ", ".join(property_id)
                        option_value = f"{option['name']}|{property_id}"
                        html += f"<input type='checkbox' name='{field_key}' value='{option_value}' {checked}> {option['name']}<br>"
                    html += "<br>"
                elif field.get("type") == "text":  # Text input handling
                    html += f"<label for='{field_key}'>{field.get('name', 'Unknown Field')}</label>"
                    html += f"<input type='text' name='{field_key}' id='{field_key}' value='{value}'>"
            return html

        # EOV Info and Other Dynamic Fields
        form_html += "<h2>EOV info<span class='info-circle' data-tooltip='For each section below, check the variables measured'>ⓘ</span></h2>"
        variables_measured = form_schema.get("categories_definition", {}).get("variable_measured", "N/A")
        measurement_techniques = form_schema.get("categories_definition", {}).get("measurementTechnique", "N/A")
        #print("measuremenets:", measurement_techniques)

        filtered_categories = {
            "variableMeasured": variables_measured,
            "measurementTechnique": measurement_techniques,
            **{key: val for key, val in form_schema.get("categories_definition").items() if key not in ["license", "variable_measured", "measurementTechnique"]}
        }

        # Iterate through categories and generate HTML
        for category_key, category in filtered_categories.items():
            # Add category name and description
            form_html += f"<h3>{category.get('name', 'Unknown Category')}<span class='info-circle' data-tooltip='{category.get('description', '')}'>ⓘ</span></h3>"
            # Special handling for `variableMeasured` and `measurementTechnique`
            if category_key in ["variableMeasured", "measurementTechnique"]:
                category_value = format_special_category_values(prefilled_data, category_key)
            else:
                category_value = prefilled_data.get(category_key, "N/A")
            print("cat value: ", category_value)
            # Display previously entered values
            form_html += f"<div class='previous'><strong>Previously entered:</strong> {category_value}</div>"

            # Process fields for this category
            fields = category.get("fields", {})
            form_html += process_fields(fields, prefilled_data,category_value)

        # for category_key, category in filtered_categories.items():
        #     # Add category name and description
        #     form_html += f"<h3>{category.get('name', 'Unknown Category')}</h3>"
        #     form_html += f"<p>{category.get('description', '')}</p>"

        #     # Check if there's a previously entered value for this category
        #     category_value = prefilled_data.get(category_key, "")
        #     print("Cat value:", category_value)

        #     # Special handling for variableMeasured and measurementTechnique
        #     if category_key == "variableMeasured" and "variableMeasured" in prefilled_data:
        #         variable_measured = prefilled_data["variableMeasured"]
        #         print("vars measured:", variable_measured)
        #         names = [item["name"] for item in variable_measured if "name" in item]
        #         category_value = ", ".join(names) if names else "N/A"

        #     elif category_key == "measurementTechnique" and "measurementTechnique" in prefilled_data:
        #         measurement_techniques = prefilled_data["measurementTechnique"]
        #         names = [item["name"] for item in measurement_techniques if "name" in item]
        #         category_value = ", ".join(names) if names else "N/A"

        #     if category_value:
        #         form_html += f"<div class='previous'><strong>Previously entered:</strong> {category_value}</div>"
        #     else:
        #         form_html += "<div class='previous'><strong>Previously entered:</strong> N/A</div>"

        #     # Process fields within the category
        #     for field_key, field in category.get("fields", {}).items():
        #         value = prefilled_data.get(field_key, "")
        #         # Check if the field has options (for dropdown fields with options)
        #         if "options" in field:
        #             multiple_attr = "multiple" if field.get("allow_multiple", False) else ""
        #             form_html += f"<label for='{field_key}'>{field.get('name', 'Unknown Field')}</label>"
        #             form_html += f"<select name='{field_key}' id='{field_key}' {multiple_attr}>"

        #             for option_key, option in field["options"].items():
        #                 # Handle propertyID for options (it can be a string or list)
        #                 selected = "selected" if option['name'] in value else ""
        #                 property_id = option.get('propertyID', '')
        #                 if isinstance(property_id, list):
        #                     property_id = ', '.join(property_id)  # Join list into a string
        #                 option_value = option['name'] + "|" + property_id
        #                 form_html += f"<option value='{option_value}' {selected}>{option['name']}</option>"
        #             form_html += "</select><br><br>"

        #         elif field.get("type") == "text":
        #             form_html += f"<label for='{field_key}'>{field.get('name', 'Unknown Field')}</label>"
        #             form_html += f"<input type='text' name='{field_key}' id='{field_key}' value='{value}'><br><br>"

        # SOP section
        sops= prefilled_data.get("measurementTechnique", [])
        # Extract URLs, skipping items without 'url'
        sops_urls = [item["url"] for item in sops if isinstance(item, dict) and "url" in item]
        sops_display = ", ".join(sops_urls) if sops_urls else "N/A"
        form_html += "<label for='sops'> SOPs <span class='info-circle' data-tooltip='Provide a link to any Methods or Standard Operating Procedures used.'>ⓘ</span></label> Provide a link to any Methods or Standard Operating Procedures used.<br>"
        form_html += f"""
        <div class="previous"><strong>Previously entered:</strong> {sops_display}</div>
        """
        form_html += "<div id='sops-container'>"
        for sop_url in sops_urls:
            form_html += f'<input type="text" name="sops" class="sops-input" value="{sop_url}" placeholder="Enter a link to an SOP"><br>'
        form_html += "</div>"
        form_html += '<button type="button" onclick="addSOPInput()">Add a SOP link</button>'

        # Funding section
        form_html += "<h2>Funding Information</h2>"
        form_html += "<div>"
        form_html += f"""
            <label for="funder_name">Funding Organization Name: <span class='info-circle' data-tooltip='Name of funding organization.'>ⓘ</span></label>
            <div class="previous"><strong>Previously entered:</strong> {prefilled_data.get('funding',{}).get("funder",{}).get("name", 'N/A')}</div>
            <input type="text" id="funder_name" name="funder_name" placeholder="Enter funder name" value="{prefilled_data.get('funding',{}).get("funder",{}).get("name", '')}"><br>

            <label for="funder_url">Funding Organization URL: <span class='info-circle' data-tooltip='URL of funding organization.'>ⓘ</span></label>
            <div class="previous"><strong>Previously entered:</strong> {prefilled_data.get('funding',{}).get("funder",{}).get('url', 'N/A')}</div>
            <input type="url" id="funder_url" name="funder_url" placeholder="Enter funder URL" value="{prefilled_data.get('funding',{}).get("funder",{}).get('url', '')}"><br>

            <label for="funding_name">Name of Funding Award: <span class='info-circle' data-tooltip='Name of the funding or award received, e.g. Horizon Europe'>ⓘ</span></label>
            <div class="previous"><strong>Previously entered:</strong> {prefilled_data.get('funding',{}).get('name', 'N/A')}</div>
            <input type="text" id="funding_name" name="funding_name" placeholder="Enter funding name" value="{prefilled_data.get('funding',{}).get('name', '')}"><br>

            <label for="funding_identifier">Funding Identifier Number: <span class='info-circle' data-tooltip='The identifier associated with the funding, e.g. grant number.'>ⓘ</span></label>
            <div class="previous"><strong>Previously entered:</strong> {prefilled_data.get('funding',{}).get('identifier', 'N/A')}</div> E.g. grant number<br>
            <input type="text" id="funding_identifier" name="funding_identifier" placeholder="Enter funding identifier" value="{prefilled_data.get('funding',{}).get('identifier', '')}"><br>
        """
        form_html += "</div>"
        form_html += "<br>"
        return form_html