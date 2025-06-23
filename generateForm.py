import json
# Load form schema


def generate_form(prefilled_data=None):
    with open("schema.json") as f:
        form_schema = json.load(f)

        form_html = ""
        prefilled_data = prefilled_data or {}
        print(f"Prefilled data: {json.dumps(prefilled_data, indent=4)}")

        form_html += """
        <h2>General Information</h2>
        """
        # Project Name
        form_html += f"""
        <h4><label for='project_name'>Data Producer Name:<span class="required">*</span><span class="info-circle" data-tooltip="Enter the full name or title of the data producer.">ⓘ</span></label></h4>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('legalName', 'N/A')}</div>
        <input type='text' name='project_name' id='project_name' value="{prefilled_data.get('legalName', '')}" placeholder="Co-Creating Transformative Pathways to Biological and Ecosystem Ocean Observations" required><br><br>
        """
        # Project Acronym
        form_html += f"""
        <h4><label for='shortname'>Data Producer Acrynom:<span class="info-circle" data-tooltip="Enter the short name or acrynom of the data producer.">ⓘ</span></label></h4>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('name', 'N/A')}</div>
        <input type='text' name='shortname' id='shortname' value="{prefilled_data.get('name', '')}" placeholder="BioEcoOcean"><br><br>
        """
        # URL
        form_html += f"""
        <label for='url'>URL:<span class="required">*</span><span class="info-circle" data-tooltip="Provide the URL to the homepage for the data producer.">ⓘ</span></label>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('url', 'N/A')}</div>
        <input type='url' name='url' id='url' value="{prefilled_data.get('url', '')}" placeholder="https://bioecoocean.org/" required><br><br>
        """
        #Project ID
        form_html += f"""
        <label for='projid'>Data producer ID:<span class="info-circle" data-tooltip="Provide the ID for the entity producing EOV data, e.g. project, institution, programme, etc. IDs could include a Research Activity Identifier (RAiD), or Research Organization Registry identifier (ROR ID). If you do not currently have one it can be added later. The ID will facilitate connecting the data producer metadata with other outputs e.g. datasets in OBIS">ⓘ</span></label>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('identifier', {}).get('url', 'N/A')}</div>
        <input type='text' name='projid' id='projid' value="{prefilled_data.get('identifier', {}).get('url', 'N/A')}" placeholder="e.g. a RAiD, or ROR ID"><br><br>
        """

        # Description
        form_html += f"""
        <label for='description'>Description: <span class="info-circle" data-tooltip="Provide a brief description of the project.">ⓘ</span></label>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('description', 'N/A')}</div>
        <textarea name='description' id='description' maxlength="2000" placeholder="BioEcoOcean was funded by the European Union under grant agreement No. 101136748 with 5.7 million EUR to address this challenge. Over the course of 4 years, from February 2024 to January 2027, a consortium of 9 European partners aims to create, and demonstrate the value of, a globally applicable Blueprint for Integrated Ocean Science (BIOS).">{prefilled_data.get('description', '')}</textarea><br><br>
        """
        #keywords section
        # keywords = prefilled_data.get("keywords", [])
        # keywords_display = ", ".join(keywords) if keywords else "N/A"
        # form_html += "<label for='keywords'>Keywords: <span class='info-circle' data-tooltip='Enter relevant keywords for the project.'>ⓘ</span></label>"
        # form_html += f"""
        # <div class='previous'><strong>Previously entered: </strong>{keywords_display}</div>
        # """
        # form_html += "<div id='keywords-container'>"
        # for keyword in keywords:
        #     form_html += f'<input type="text" name="keywords" class="keyword-input" value="{keyword}" placeholder="Enter a keyword"><br>'
        # form_html += "</div>"
        # form_html += '<button type="button" onclick="addKeywordInput()">Add Another Keyword</button><br><br>'
        keywords = prefilled_data.get("keywords", [])
        keywords_display = ", ".join([keyword["name"] for keyword in keywords if "name" in keyword]) if keywords else "N/A"
        form_html += f"""
        <label for='keywords'>Keywords: <span class='info-circle' data-tooltip='Enter relevant keywords from controlled vocabulary collections for the data producer.'>ⓘ</span></label>
        Type in the box below to search for a keyword from a controlled vocabulary collection. This will query both The Environment Ontology (ENVO) and the BODC NERC Vocabulary Server.
        Please confirm a keyword is relevant by clicking the associated link and reading its definition.<br>
        <div class='previous'><strong>Previously entered: </strong>{keywords_display}</div>
        <div class="search-container">
            <input type="text" id="ontology-search" name="ontology_term" placeholder="Search using a minimum of 3 characters, e.g. 'coral', 'sea', etc." autocomplete="off">
            <button type="button" id="ontology-search-btn">Search</button>
        </div>

        <!-- Results Table -->
        <div class="table-scroll">
        <table id="results-table" class="scrollable-table" style="display:none;">
            <thead>
                <tr>
                    <th>Keyword</th>
                    <th>URL</th>
                    <th>Source</th>
                </tr>
            </thead>
            <tbody>
                <!-- Dynamically populated rows will go here -->
            </tbody>
        </table>
        </div>

        <p style="font-weight:bold">Selected Keywords:<p>
        <div id="selected-keywords-list" class="selected-keywords-list">
            <!-- Selected keywords will appear here -->
        </div>
        <input type="hidden" id="selected-keywords-json" name="selected-keywords-json" value="">
        <br>
        """

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
            <option value="asneeded" {'selected' if prefilled_data.get('frequency', '') == 'asneeded' else ''}>As Needed</option>
        </select>
        """
        form_html += "<hr style='border: none; border-bottom: dashed 2px #002366; '>"

        # Contact Information
        form_html += f"""
        <label for='contact_name'>
            <h2>Programme Contacts:<span class="required">*</span>
            <span class="info-circle" data-tooltip="Provide contact information for your project. Can be for individual person or organizational contact information.">ⓘ</span>
            </h2></label>
        <div class='previous'><strong>Previously entered:</strong> 
        Names: {", ".join(prefilled_data.get('contactPoint', {}).get('name', 'N/A')) if prefilled_data.get('contactPoint', {}).get('name') else "N/A"}; 
        Emails: {", ".join(prefilled_data.get('contactPoint', {}).get('email', 'N/A')) if prefilled_data.get('contactPoint', {}).get('email') else "N/A"};
        Roles: {", ".join(prefilled_data.get('contactPoint', {}).get('role', 'N/A')) if prefilled_data.get('contactPoint', {}).get('role') else "N/A"};
        Identifiers: {", ".join(prefilled_data.get('contactPoint', {}).get('identifier', 'N/A')) if prefilled_data.get('contactPoint', {}).get('identifier') else "N/A"}
         </div>

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
                contact_ids = contact.get("identifier", "")
                form_html += f"""
                <script>
                    addContactInput("{contact_names}", "{contact_emails}", "{contact_roles}", "{contact_ids}", true);
                </script>
                """
        else:
            form_html += """
            """
        # Add the dynamic container for new inputs
        form_html += "<div id='contacts-container'></div>"
        if not contacts:  # Only add the script if no prefilled data exists
            form_html += """
            <script>
                window.addEventListener("load", function() {
                    addContactInput();
                });
            </script>
            """
        form_html += """
        <button type="button" onclick="addContactInput()">Add Contact</button>
        <br>
        """
        form_html += "<hr style='border: none; border-bottom: dashed 2px #002366; '>"

        #Coverage
        form_html += "<h2>Coverage</h2>"
        #Temporal coverage
        form_html += f"""
        <h3><label for='temporal_coverage'>Temporal Coverage:<span class="info-circle" data-tooltip="Specify the date range for the project.">ⓘ</span></label></h3>
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('temporalCoverage', 'N/A')}</div>
        <div class="flex-col" style="max-width:600px;">
            <div class="flex-row">
                <b>Start date: </b> <input type='date' name='temporal_coverage_start' id='temporal_coverage_start'
                    value="{prefilled_data.get('temporalCoverage', '').split('/')[0] if prefilled_data.get('temporalCoverage') else ''}" >
            </div>
            <div class="flex-row">
                <b>End  date: </b> <input type='date' name='temporal_coverage_end' id='temporal_coverage_end'
                    value="{prefilled_data.get('temporalCoverage', '').split('/')[1] if prefilled_data.get('temporalCoverage') else ''}" >
            </div>
        </div><br>
        """

        # Spatial Coverage
        regional_id_str = 'MRGID: '
        form_html += f"""
        <h4><label for="spatial_coverage_name">Spatial Coverage: <span class='info-circle' data-tooltip='Specify the name and MRGID of the area where the programme takes place. Use the search box to select an area from Marine Regions. Use the map below to also add bounding area coordinates.'>ⓘ</span></label></h4>
        <a>Use the search box below to search for a marine location. Names are obtained from <a href="https://www.marineregions.org/gazetteer.php?p=search">Marine Regions Gazetteer</a>.
        <div class='previous'><strong>Previously entered:</strong> {prefilled_data.get('areaServed', {}).get("name", 'N/A')} {regional_id_str}{prefilled_data.get('areaServed', {}).get("identifier", 'N/A')}</div>
        <input type="text" id="search_regions" placeholder="Search for a region. Minimum 3 characters, e.g., 'hud', 'bay'" />
        <button type="button" id="search_regions_btn">Search</button>
        <br><br>
        <!-- Table to display search results -->
        <div class="table-scroll">
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
        </div>
        <a><i>Auto-populated fields:</i></a><br>
        Name: <input type="spatial" name="spatial_coverage_name" id="spatial_coverage_name" value="{prefilled_data.get('areaServed', {}).get("name", '')}" readonly>
        MRGID: <input type="text" name="spatial_coverage_identifier" id="spatial_coverage_identifier" value="{prefilled_data.get('areaServed', {}).get("identifier", '')}" readonly>
        <button type="button" onclick="clearMarineRegions()">Clear Location</button>
        <br><br>
        """

        boundingcoords = {prefilled_data.get('areaServed', {}).get("geo", {}).get("box", '')}
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
        <div id="map" style="width: 80vw; max-width: 100%; height: 50vh;"></div>
        <div class="flex-col" style="max-width:600px;">
            <div class="flex-row">
                <div class="flex-col">
                    <label for="maxy" id="maxy">North (max latitude):</label>
                    <input type="text" id="north" name="north" value="{north}">
                </div>
                <div class="flex-col">
                    <label for="south" id="miny">South (min latitude):</label>
                    <input type="text" id="south" name="south" value="{south}">
                </div>
            </div>
            <div class="flex-row">
                <div class="flex-col">
                    <label for="east" id="maxx">East (max longitude):</label>
                    <input type="text" id="east" name="east" value="{east}">
                </div>
                <div class="flex-col">
                    <label for="west" id="minx">West (min longitude):</label>
                    <input type="text" id="west" name="west" value="{west}">
                </div>
            </div>
            <div class="flex-col">
                <button type="button" onclick="clearBoundingCoordinates()">Clear Bounding Coordinates</button>
            </div>
        </div>

        """
        form_html += "<hr style='border: none; border-bottom: dashed 2px #002366; '>"

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
                    html += f"<div class='checkbox-container'>"

                    # --- Sort options alphabetically by name ---
                    sorted_options = sorted(field["options"].items(), key=lambda item: item[1]["name"].lower())

                    for option_key, option in sorted_options:
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
        form_html += "<label for='sops'><h4> Standard Operating Procedures <span class='info-circle' data-tooltip='Provide a link to any Methods or Standard Operating Procedures (SOPs) used. Check the box to indicate if the methods are listed as a best practice in Ocean Best Practices (OBPS)'>ⓘ</span></h4></label> "
        "Provide a link to any Methods or Standard Operating Procedures used. Check the box to indicate if the methods are listed as a best practice in Ocean Best Practices (OBPS)<br>"
        form_html += f"""
        <div class="previous"><strong>Previously entered:</strong> {sops_display}</div>
        """
        form_html += "<div id='sops-container'>"
        for sop_url in sops_urls:
            form_html += f'<input type="text" name="sops" class="sops-input" value="{sop_url}" placeholder="Enter a link to an SOP"><br>'
        form_html += "</div>"
        form_html += '<button type="button" onclick="addSOPInput()">Add a SOP link</button><br>'

        form_html += "<hr style='border: none; border-bottom: dashed 2px #002366; '>"

        #Ouputs section
        outputs = prefilled_data.get("isRelatedTo", [])
        outputs_display = ", ".join(outputs) if outputs else "N/A"
        form_html += "<label for='outputs'><h2>Outputs: <span class='info-circle' data-tooltip='Enter relevant outputs that are related to your entry.'>ⓘ</span></h2></label>"
        form_html += "<p>Please optionally provide the link to any relevant outputs that are associated with your entry. This may include products, portals, etc. If you have already linked any such outputs with ODIS or the BioEco Portal, you can provide them again here if you wish. Note that datasets published to OBIS would not need to be added here, and you can use the same data producer ID to ensure this entry is linked with OBIS data. </p>"
        form_html += f"""
        <div class='previous'><strong>Previously entered: </strong>{outputs_display}</div>
        """
        form_html += "<div id='outputs-container'>"
        for outputs in outputs:
            form_html += f'<input type="text" name="outputs" class="outputs-input" value="{outputs}" placeholder="Enter the link of an output"><br>'
        form_html += "</div>"
        form_html += '<button type="button" onclick="addOutputInput()">Add an Output</button><br>'

        form_html += "<hr style='border: none; border-bottom: dashed 2px #002366; '>"

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
        form_html += "<label for='funder-container'><h2>Funding Information <span class='info-circle' data-tooltip='Provide information about funding organizations and awards.'>ⓘ</span></h2></label>"
        form_html += "<p>Please provide information about the funding that supports your entry.</p>"
        
        funding_data = prefilled_data.get("funding", [])
        form_html += f"""
        <div class="previous"><strong>Previously entered:</strong> 
            Funder name: {", ".join(prefilled_data.get("funding", {}).get("funder", {}).get("name", [])) if prefilled_data.get("funding", {}).get("funder", {}).get("name") else "N/A"},
            Funder URL: {", ".join(prefilled_data.get("funding", {}).get("funder", {}).get("url", [])) if prefilled_data.get("funding", {}).get("funder", {}).get("url") else "N/A"},
            Funding award name: {", ".join(prefilled_data.get("funding", {}).get("name", [])) if prefilled_data.get("funding", {}).get("name") else "N/A"},
            Funding award identifier: {", ".join(prefilled_data.get("funding", {}).get("identifier", [])) if prefilled_data.get("funding", {}).get("identifier") else "N/A"}
        </div>
        """
        print("Funding data:", funding_data)

        # Normalize the funding data into a list of dictionaries
        if isinstance(funding_data, dict):  # If it's a dict of lists, restructure into list of dicts
            funding_list = []
            length = len(funding_data.get("name", []))
            for i in range(length):
                #funder_info = funding_data.get("funder", [{}])[i] if i < len(funding_data.get("funder", [])) else {}
                #print("Funder info:", funder_info)  # Debugging
                funding_entry = {
                    "funder_name": funding_data.get("funder", {}).get("name", [])[i] if i < len(funding_data.get("funder", {}).get("name", [])) else "",
                    "funder_url": funding_data.get("funder", {}).get("url", [])[i] if i < len(funding_data.get("funder", {}).get("url", [])) else "",
                    "name": funding_data.get("name", [])[i] if i < len(funding_data.get("name", [])) else "",
                    "identifier": funding_data.get("identifier", [])[i] if i < len(funding_data.get("identifier", [])) else ""
                }
                funding_list.append(funding_entry)
            funding_data = funding_list
        elif isinstance(funding_data, list):  # If it's already a list, use as is
            pass

        # Debug: Print the normalized funding data
        print("Normalized funding data:", funding_data)

        # Generate the form fields for prefilled funding data
        if funding_data:
            for funding in funding_data:
                form_html += f"""
                <div class="funding-container">
                    <input type="text" name="funder_name" value="{funding.get('funder_name', '')}" placeholder="Enter name of funding organization">
                    <input type="url" name="funder_url" value="{funding.get('funder_url', '')}" placeholder="Enter URL of funder">
                    <input type="text" name="funding_name" value="{funding.get('name', '')}" placeholder="Enter name of the funding award">
                    <input type="text" name="funding_identifier" value="{funding.get('identifier', '')}" placeholder="Enter the identifier of the funding award">
                </div>
                """
        else:
            form_html += """
            """
        # Add the dynamic container for new inputs
        form_html += "<div id='funder-container'></div>"
        if not funding_data:  # Only add the script if no prefilled data exists
            form_html += """
            <script>
                // Add one blank funding input set when the form is loaded
                window.addEventListener("load", function() {
                    addFunders();
                });
            </script>
            """
        form_html += '<button type="button" onclick="addFunders()">Add a Funder</button><br><br>'

        form_html += "<hr style='border: none; border-bottom: dashed 2px #002366; '>"

        eovs = prefilled_data.get("eovs", [])
        eovs_display = ", ".join(eovs) if eovs else "N/A"
        form_html += f"""
        <label for='eovs-standard'>EOVs: <span class='info-circle' data-tooltip='Select relevant EOVs from controlled vocabulary collections.'>ⓘ</span></label>
        This section is a work in progress to allow easier selection of EOVs.
        Type in the box below to search for an EOV from a controlled vocabulary collection. This will query both The Environment Ontology (ENVO) and the BODC NERC Vocabulary Server.<br>
        <div class='previous'><strong>Previously entered: </strong>{eovs_display}</div>
        <div class="search-container">
            <input type="text" id="eov-search" name="ontology_term" placeholder="Search for a term..." autocomplete="off">

        </div>

        <!-- Results Table -->
        <table id="eov-table" class="scrollable-table" style="display:none;">
            <thead>
                <tr>
                    <th>EOV</th>
                    <th>URL</th>
                    <th>Source</th>
                </tr>
            </thead>
            <tbody>
                <!-- Dynamically populated rows will go here -->
            </tbody>
        </table>

        <p style="font-weight:bold">Selected EOVs:<p>
        <div id="selected-eovs-list" class="selected-eovs-list">
            <!-- Selected keywords will appear here -->
        </div>
        <input type="hidden" id="selected-eovs-json" name="selected-eovs-json" value="">
        <br>
        """

        return form_html