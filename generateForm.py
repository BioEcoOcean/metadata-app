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
        #Project ID
        form_html += f"""
        <label for='projid'>Data producer ID:<span class="info-circle" data-tooltip="Provide the ID for the entity producing EOV data, e.g. project, institution, programme, etc. If you do not currently have one it can be added later. The ID will facilitate connecting the data producer metadata with other outputs e.g. datasets in OBIS">ⓘ</span></label>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('pid', 'N/A')}</div>
        <input type='text' name='projid' id='projid' value="{prefilled_data.get('pid', '')}" ><br><br>
        """

        # Description
        form_html += f"""
        <label for='description'>Description: <span class="info-circle" data-tooltip="Provide a brief description of the project.">ⓘ</span></label>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('description', 'N/A')}</div>
        <textarea name='description' id='description'>{prefilled_data.get('description', '')}</textarea><br><br>
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

        # License section
        license_field = form_schema.get("categories_definition", {}).get("license", None)
        if license_field:
            license_value = prefilled_data.get("license", {}).get("name", 'N/A')

            # Show previously entered value above the field
            form_html += f"<label for='license'>{license_field['name']}:<span class='required'>*</span><span class='info-circle' data-tooltip='Select the most appropriate license for the programme metadata.'>ⓘ</span></label>"
            form_html += f"<p>Please select which Creative Commons license (<a href='https://creativecommons.org/share-your-work/cclicenses/'>https://creativecommons.org/share-your-work/cclicenses/</a>) you expect the programme metadata to be made available.</p>"
            if license_value:
                form_html += f"<div class='previous'><strong>Previously entered:</strong> {license_value}</div>"
            else:
                form_html += "<div class='previous'><strong>Previously entered:</strong> N/A</div>"

            # License dropdown
            form_html += "<select name='license' id='license' required>"
            form_html += "<option value='' selected>Select option</option>"

            for option_key, option in license_field['options'].items(): #option_key is necessary to get the key from schema
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

        # Contact Information
        form_html += f"""
        <label for='contact_name'><h3>Programme Contacts:<span class="required">*</span><span class="info-circle" data-tooltip="Provide contact information for your project. Can be for individual person or organizational contact information.">ⓘ</span></label></h3>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('contactPoint', {}).get('name', 'N/A')}, {prefilled_data.get('contactPoint', {}).get('email', '')} {prefilled_data.get('contactPoint', {}).get('role', '')} {prefilled_data.get('contactPoint', {}).get('identifier', '')}</div>

        """
        form_html += f"""
        <div id="contacts-container">
        </div>
        """
        contacts = prefilled_data.get("contactPoint", [])
        print("contact info:", contacts)
        print(f"Contacts data type: {type(contacts)}, content: {contacts}")

        if isinstance(contacts, dict):
            # Restructure the contacts from a dictionary of lists into a list of dictionaries
            contact_list = []
            length = len(contacts.get('name', []))
            for i in range(length):
                contact = {
                    'name': contacts.get('name', [])[i] if i < len(contacts.get('name', [])) else "",
                    'email': contacts.get('email', [])[i] if i < len(contacts.get('email', [])) else "",
                    'role': contacts.get('role', [])[i] if i < len(contacts.get('role', [])) else "",
                    'identifier': contacts.get('identifier', [])[i] if i < len(contacts.get('identifier', [])) else ""
                }
                contact_list.append(contact)
            contacts = contact_list
        elif isinstance(contacts, list):
            # If it's already a list, keep it as is
            pass

        print("Restructured contacts:", contacts)

        # Call the JavaScript function for each prefilled contact
        if contacts:
            if isinstance(contacts, dict):  # Single contact
                contacts = [contacts]
            for contact in contacts:
                contact_names = contact.get("name", "")
                contact_emails = contact.get("email", "")
                contact_roles = contact.get("role", "")
                contact_ids = contact.get("id", "")
                form_html += f"""
                <script>
                    addContactInput("{contact_names}", "{contact_emails}", "{contact_roles}", "{contact_ids}");
                </script>
                """
        else:
            form_html += """
            """

        # Add the dynamic container for new inputs
        form_html += """
        <div id="contacts-container"></div>
        <button type="button" onclick="addContactInput()">Add Contact</button>
        <br><br>
        """

        #Coverage
        form_html += "<h3>Coverage</h3>"
        #Temporal coverage
        form_html += f"""
        <h4><label for='temporal_coverage'>Temporal Coverage:<span class="info-circle" data-tooltip="Specify the date range for the project.">ⓘ</span></label></h4>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('temporalCoverage', 'N/A')}</div>
        <b>Start date: </b> <input type='date' name='temporal_coverage_start' id='temporal_coverage_start'
            value="{prefilled_data.get('temporalCoverage', '').split('/')[0] if prefilled_data.get('temporalCoverage') else ''}" ><br>
        <b>End date: </b> <input type='date' name='temporal_coverage_end' id='temporal_coverage_end'
            value="{prefilled_data.get('temporalCoverage', '').split('/')[1] if prefilled_data.get('temporalCoverage') else ''}" ><br><br>
        """

        # Spatial Coverage
        regional_id_str = 'MRGID: '
        form_html += f"""
        <h4><label for="spatial_coverage_name">Spatial Coverage: <span class='info-circle' data-tooltip='Specify the name and MRGID of the area where the programme takes place. Use the search box to select an area from Marine Regions. Use the map below to also add bounding area coordinates.'>ⓘ</span></label></h4>
        <a>Use the search box below to search for a marine location. Names are obtained from <a href="https://www.marineregions.org/gazetteer.php?p=search">Marine Regions Gazetteer</a>.
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('spatialCoverage', {}).get("name", 'N/A')} {regional_id_str}{prefilled_data.get('spatialCoverage', {}).get("identifier", 'N/A')}</div>
        <a>Search:</a>
        <input type="text" id="search_regions" placeholder="Search for a region..." />
        <br><br>
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
        <a><i>Auto-populated fields:</i></a><br>
        Name: <input type="spatial" name="spatial_coverage_name" id="spatial_coverage_name" value="{prefilled_data.get('spatialCoverage', {}).get("name", '')}" readonly>
        MRGID: <input type="text" name="spatial_coverage_identifier" id="spatial_coverage_identifier" value="{prefilled_data.get('spatialCoverage', {}).get("identifier", '')}" readonly>
        <button type="button" onclick="clearMarineRegions()">Clear Location</button>
        <br><br>
        """

        boundingcoords = {prefilled_data.get('spatialCoverage', {}).get("geo", {}).get("box", '')}
        if isinstance(boundingcoords, set):
            # Extract the string from the set
            boundingcoords = next(iter(boundingcoords))
        print("coords :", boundingcoords)
        coordinates = boundingcoords.split(" ") # Split the string into four parts
        south = coordinates[0] if len(coordinates) > 0 else ""
        west = coordinates[1] if len(coordinates) > 1 else ""
        north = coordinates[2] if len(coordinates) > 2 else ""
        east = coordinates[3] if len(coordinates) > 3 else ""

        form_html += f"""
        <a>Draw Bounding Area</a>
        <div id="map" style="width: 60%; height: 300px;"></div>
        <div class="grid-container">
            <div class="grid-item">
                <label for="maxy" id="maxy">North (max latitude):</label>
                <input type="text" id="north" name="north" value="{north}"><br>
            </div>
            <div class="grid-item">
                <label for="south" id="miny">South (min latitude):</label>
                <input type="text" id="south" name="south" value="{south}"><br>
            </div>
            <div class="grid-item">
                <button type="button" onclick="clearBoundingCoordinates()">Clear Bounding Coordinates</button>
            </div>
            <div class="grid-item">
                <label for="east" id="maxx">East (max longitude):</label>
                <input type="text" id="east" name="east" value="{east}"><br>
            </div>
            <div class="grid-item">
                <label for="west" id="minx">West (min longitude):</label>
                <input type="text" id="west" name="west" value="{west}"><br>
            </div>

        </div>

        """

        # EOVs and Variables
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
                    html += f"<label for='{field_key}'><h4>{field.get('name', 'Unknown Field')}</h4></label>"

                    # Ensure category_value is a list if it's a string
                    category_value_list = category_value.split(", ") if isinstance(category_value, str) else category_value
                    # Create a scrollable div for checkboxes
                    html += f"<div class='checkbox-container' style='max-height: 150px; overflow-y: auto;'>"

                    for option_key, option in field["options"].items():
                        # Check if the option name is in the list of previously entered values
                        checked = "checked" if option["name"] in category_value_list else ""
                        property_id = option.get("propertyID", "")
                        if isinstance(property_id, list):
                            property_id = ", ".join(property_id)
                        option_value = f"{option['name']}|{property_id}"
                        html += f"<input type='checkbox' name='{field_key}' value='{option_value}' {checked}> {option['name']}<br>"
                    html += "</div><br>"
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
            # print("cat value: ", category_value) #debugging
            # Display previously entered values
            form_html += f"<div class='previous'><strong>Previously entered:</strong> {category_value}</div>"

            # Process fields for this category
            fields = category.get("fields", {})
            form_html += process_fields(fields, prefilled_data,category_value)

        # SOP section
        sops= prefilled_data.get("measurementTechnique", [])
        # Extract URLs, skipping items without 'url'
        sops_urls = [item["url"] for item in sops if isinstance(item, dict) and "url" in item]
        sops_display = ", ".join(sops_urls) if sops_urls else "N/A"
        form_html += "<label for='sops'><h4> SOPs <span class='info-circle' data-tooltip='Provide a link to any Methods or Standard Operating Procedures used.'>ⓘ</span></h4></label> Provide a link to any Methods or Standard Operating Procedures used.<br>"
        form_html += f"""
        <div class="previous"><strong>Previously entered:</strong> {sops_display}</div>
        """
        form_html += "<div id='sops-container'>"
        for sop_url in sops_urls:
            form_html += f'<input type="text" name="sops" class="sops-input" value="{sop_url}" placeholder="Enter a link to an SOP"><br>'
        form_html += "</div><br>"
        form_html += '<button type="button" onclick="addSOPInput()">Add a SOP link</button><br><br>'

        #Ouputs section
        outputs = prefilled_data.get("outputs", [])
        outputs_display = ", ".join(outputs) if outputs else "N/A"
        form_html += "<label for='outputs'><h2>Outputs: <span class='info-circle' data-tooltip='Enter relevant outputs that are related to your entry.'>ⓘ</span></h2></label>"
        form_html += "<p>Please optionally provide the link to any relevant outputs.</p>"
        form_html += f"""
        <div class='previous'><strong>Previously entered: </strong>{outputs_display}</div>
        """
        form_html += "<div id='outputs-container'>"
        for outputs in outputs:
            form_html += f'<input type="text" name="outputs" class="outputs-input" value="{outputs}" placeholder="Enter the link of an output"><br>'
        form_html += "</div>"
        form_html += '<button type="button" onclick="addOutputInput()">Add an Output</button><br>'

        # Funding section
        # form_html += "<h2>Funding Information</h2>"
        # form_html += "<div>"
        # form_html += f"""
        #     <label for="funder_name">Funding Organization Name: <span class='info-circle' data-tooltip='Name of funding organization.'>ⓘ</span></label>
        #     <div class="previous"><strong>Previously entered:</strong> {prefilled_data.get('funding',{}).get("funder",{}).get("name", 'N/A')}</div>
        #     <input type="text" id="funder_name" name="funder_name" placeholder="Enter funder name" value="{prefilled_data.get('funding',{}).get("funder",{}).get("name", '')}"><br><br>

        #     <label for="funder_url">Funding Organization URL: <span class='info-circle' data-tooltip='URL of funding organization.'>ⓘ</span></label>
        #     <div class="previous"><strong>Previously entered:</strong> {prefilled_data.get('funding',{}).get("funder",{}).get('url', 'N/A')}</div>
        #     <input type="url" id="funder_url" name="funder_url" placeholder="Enter funder URL" value="{prefilled_data.get('funding',{}).get("funder",{}).get('url', '')}"><br><br>

        #     <label for="funding_name">Name of Funding Award: <span class='info-circle' data-tooltip='Name of the funding or award received, e.g. Horizon Europe'>ⓘ</span></label>
        #     <div class="previous"><strong>Previously entered:</strong> {prefilled_data.get('funding',{}).get('name', 'N/A')}</div>
        #     <input type="text" id="funding_name" name="funding_name" placeholder="Enter funding name" value="{prefilled_data.get('funding',{}).get('name', '')}"><br><br>

        #     <label for="funding_identifier">Funding Identifier Number: <span class='info-circle' data-tooltip='The identifier associated with the funding, e.g. grant number.'>ⓘ</span></label>
        #     <div class="previous"><strong>Previously entered:</strong> {prefilled_data.get('funding',{}).get('identifier', 'N/A')}</div>
        #     <input type="text" id="funding_identifier" name="funding_identifier" placeholder="Enter funding identifier" value="{prefilled_data.get('funding',{}).get('identifier', '')}"><br>
        # """
        # form_html += "</div>"
        # form_html += "<br>"

        # Funding section
        funders = prefilled_data.get("funding", [])
        # Extract funder details
        funders_display = ", ".join(
            [f"{funder.get('name', 'N/A')} ({funder.get('url', 'N/A')})" for funder in funders if isinstance(funder, dict)]
        ) if funders else "N/A"

        form_html += "<label for='funder-container'><h2>Funding Information <span class='info-circle' data-tooltip='Provide information about funding organizations and awards.'>ⓘ</span></h2></label>"
        form_html += "<p>Please provide information about the funding that supports your entry.</p>"
        form_html += f"""
        <div class="previous"><strong>Previously entered:</strong> {funders_display}</div>
        """
        form_html += "<div id='funder-container'>"
        # Loop through prefilled data and add existing funding inputs
        for funder in funders:
            funder_name = funder.get("funder",{}).get("name", 'N/A')
            funder_url = funder.get("funder",{}).get('url', 'N/A')
            funding_name = funder.get('name', 'N/A')  # Assuming awards are nested
            funding_identifier = funder.get('identifier', 'N/A')
            form_html += f"""
            <div class="funder-container">
                <input type="text" name="funder_name" class="funder-name" value="{funder_name}" placeholder="Enter name of funding organization">
                <input type="url" name="funder_url" class="funder-url" value="{funder_url}" placeholder="Enter URL of funder" >
                <input type="text" name="funding_name" class="funding-name" value="{funding_name}" placeholder="Enter name of the funding award" >
                Funding Identifier Number:
                <input type="text" name="funding_identifier" class="funding-identifier" value="{funding_identifier}" placeholder="Enter the identifier of the funding award">
                <button type="button" class="remove-funder-button" onclick="this.parentElement.remove()">Remove</button>
            </div>
            """
        form_html += "</div>"
        form_html += '<button type="button" onclick="addFunders()">Add a Funder</button><br><br>'

        form_html += f"""
        <div>
            <h2>Search for Keywords in Vocabulary Collections</h2>
            This is a work in progress. Full functionality coming soon!
            Type in the box below to search for a keyword. Searches query both The Environment Ontology (ENVO) and the BODC NERC Vocabulary Server.<br>
           <input type="text" id="keyword-search" placeholder="Enter keyword to search" onkeypress="if(event.key === 'Enter') {{ event.preventDefault(); searchKeywords(); }}">
            <button type="button" onclick="searchKeywords()">Search</button>
            <div class="previous"><strong>Previously entered:</strong> </div>
            <div id="keyword-results" style="margin-top: 10px; max-height: 200px; overflow-y: auto; border: 1px solid #ccc; padding: 10px;"></div>
                <div>
                    <h3>Selected Keywords</h3>
                    <div id="selected-keywords"></div>
                </div>
        </div>

        <!-- Hidden inputs for storing selected keywords for form submission -->
            <div id="selected-keywords-hidden" ></div>
        <br><br>
        """
        return form_html