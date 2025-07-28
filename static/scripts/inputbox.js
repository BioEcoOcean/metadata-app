function addRemoveButton(container) {
    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.textContent = "Remove";
    removeButton.className = "remove-btn";
    removeButton.onclick = function() {
        container.remove();
    };
    container.appendChild(removeButton);
}
function addKeywordInput() {
    const newInputContainer = document.createElement("div");
    newInputContainer.className = "keyword-input-container";
    newInputContainer.style.marginTop = "5px";  // Add some spacing for better visuals
    
    const newInput = document.createElement("input");
    newInput.type = "text";
    newInput.name = "keywords";  // Keep name="keywords" so Flask collects them as a list
    newInput.className = "keyword-input";
    newInput.placeholder = "Enter a keyword";
    newInput.style.marginTop = "5px";  // Add some spacing for better visuals  
    
    newInputContainer.appendChild(newInput);
    addRemoveButton(newInputContainer);
    // Append the new input to the container
    document.getElementById("keywords-container").appendChild(newInputContainer);
}
function addOutputInput(name ="", url = "") {
    const newInputContainer = document.createElement("div");
    newInputContainer.className = "outputs-container";
    newInputContainer.style.marginTop = "5px";  // Add some spacing for better visuals
    
    const newInput = document.createElement("input");
    newInput.type = "text";
    newInput.name = "outputs";  
    newInput.value = name;
    newInput.className = "outputs-input";
    newInput.placeholder = "e.g. name of a product, service, etc.";
    newInput.style.marginTop = "5px";  // Add some spacing for better visuals 

    const inputURL = document.createElement("input");
    inputURL.type = "text";
    inputURL.name = "outputs_url";
    inputURL.value = url;
    inputURL.className = "outputs-url";
    inputURL.placeholder = "url for product, service, etc.";
    inputURL.style.marginTop = "5px"; 
    
    newInputContainer.appendChild(newInput);
    newInputContainer.appendChild(inputURL);
    addRemoveButton(newInputContainer);
    // Append the new input to the container
    document.getElementById("outputs-container").appendChild(newInputContainer);
}
function addSOPInput(name ="", url = "", isOBPS = "") {
    const newInputContainer = document.createElement("div");
    newInputContainer.className = "sops-input-container";
    newInputContainer.style.marginTop = "5px";
    
    const sopName = document.createElement("input");
    sopName.type = "text";
    sopName.name = "sops_name";  
    sopName.className = "sops-name"; 
    sopName.placeholder = "Name of SOP e.g. MarineGEO Seagrass Habitat Monitoring Protocol";
    sopName.value = name;
    sopName.style.marginTop = "5px";
    
    const sopURL = document.createElement("input");
    sopURL.type = "url";
    sopURL.name = "sops_url";  
    sopURL.className = "sops-url"; 
    sopURL.placeholder = "Link to SOP e.g. https://repository.oceanbestpractices.org/handle/11329/2465";
    sopURL.value = url;
    sopURL.style.marginTop = "5px";

    // Create the checkbox for OBPs
    const checkboxContainer = document.createElement("div");
    checkboxContainer.style.marginTop = "5px";
    checkboxContainer.style.display = "flex"; // Use flexbox to align items on the same line
    checkboxContainer.style.alignItems = "center"; // Vertically align the checkbox and label

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.name = "sop_obps";
    checkbox.value = "yes";
    checkbox.id = `sop_obps_${Date.now()}`; // Unique ID for the checkbox

    const checkboxLabel = document.createElement("label");
    checkboxLabel.htmlFor = checkbox.id;
    checkboxLabel.textContent = "Is this SOP included in the Ocean Best Practices System (OBPS)?";
    checkboxLabel.style.marginLeft = "5px"; // Add some spacing between the checkbox and the label

    // Append the checkbox and label to the container
    checkboxContainer.appendChild(checkbox);
    checkboxContainer.appendChild(checkboxLabel);

    newInputContainer.appendChild(sopName);
    newInputContainer.appendChild(sopURL);
    //newInputContainer.appendChild(checkboxContainer);  / I have temporarily removed this line until confirming if this output is wanted
    if (isOBPS === "yes") checkbox.checked = true;
    addRemoveButton(newInputContainer);

    document.getElementById("sops-container").appendChild(newInputContainer);
    }
function addContactInput(name = "", email = "", type = "", url = "") {
        // Create a new container for the contact
        const contactContainer = document.createElement("div");
        contactContainer.className = "contact-container flex-col";
        contactContainer.style.marginTop = "10px"; // Add spacing between pairs

        // Create the input for the contact type
        const typeSelect = document.createElement("select");
        typeSelect.name = "contact_types";  // Flask will collect these as a list
        typeSelect.className = "contact-type-select";
        typeSelect.style.marginRight = "10px";
        typeSelect.required = true;

        // Add a default "Select contact type" option
        const defaultOption = document.createElement("option");
        defaultOption.value = ""; // Empty value
        defaultOption.textContent = "Select contact type";
        defaultOption.disabled = true; // Make it unselectable
        defaultOption.selected = !type; // Select this by default if no type is provided
        typeSelect.appendChild(defaultOption);

        // Add dropdown options
        const types = ["General Inquiries", "Technical Support", "Regional Support", "Helpdesk", "Principle Investigator", "Other"];
        types.forEach(optionType  => {
            const option = document.createElement("option");
            option.value = optionType ;
            option.textContent = optionType ;
            if (optionType === type) {
                option.selected = true; // Preselect the type
            }
            typeSelect.appendChild(option);
        });

        // Create the input for the name of the contact
        const nameInput = document.createElement("input");
        nameInput.type = "text";
        nameInput.name = "contact_names";  // Flask will collect these as a list
        nameInput.className = "contact-name-input";
        nameInput.placeholder = "Enter contact name, e.g. Contact Us Page";
        nameInput.value = name;
        nameInput.style.marginRight = "10px"; // Add spacing between the two inputs
        nameInput.required = true;
    
        // Create the input for the contact email
        const emailInput = document.createElement("input");
        emailInput.type = "email";
        emailInput.name = "contact_emails";  // Flask will collect these as a list
        emailInput.className = "contact-email-input";
        emailInput.placeholder = "Enter contact email, e.g. helpdesk@company.org";
        emailInput.value = email;
        emailInput.required = false;

        // Create the input for the contact url
        const urlInput = document.createElement("input");
        urlInput.type = "url";
        urlInput.name = "contact_ids";  // Flask will collect these as a list
        urlInput.className = "contact-id-input";
        urlInput.placeholder = "Enter contact url, e.g. www.company.org/contact-us";
        urlInput.value = url; 
    
        // Append both inputs to the contact container
        contactContainer.appendChild(typeSelect);
        contactContainer.appendChild(nameInput);
        contactContainer.appendChild(emailInput);
        contactContainer.appendChild(urlInput);
        addRemoveButton(contactContainer);
        
    
        // Append the contact container to the main container
        document.getElementById("contacts-container").appendChild(contactContainer);
    }

function addFunders(name = "", url = "", award = "", identifier = "") {
        // Create a new container for the contact pair
        const funderContainer = document.createElement("div");
        funderContainer.className = "funder-container";
        funderContainer.style.marginTop = "10px"; // Add spacing between pairs
    
        // Create the input for the funder organization name
        const fundingOrg = document.createElement("input");
        fundingOrg.type = "text";
        fundingOrg.name = "funder_name";  // Flask will collect these as a list
        fundingOrg.className = "funder-name";
        fundingOrg.placeholder = "Funding organization name, e.g. European Union";
        fundingOrg.value = name;
        fundingOrg.style.marginRight = "10px"; // Add spacing between the two inputs
        
        // Create the input for the funder url
        const fundingURL = document.createElement("input");
        fundingURL.type = "url";
        fundingURL.name = "funder_url";  // Flask will collect these as a list
        fundingURL.className = "funder-url";
        fundingURL.placeholder = "Funding organization URL, e.g. https://european-union.europa.eu/";
        fundingURL.value = url;
        fundingURL.style.marginRight = "10px";
        
        // Create the input for the funder award
        const awardInput = document.createElement("input");
        awardInput.type = "text";
        awardInput.name = "funding_name";  // Flask will collect these as a list
        awardInput.className = "funding-name";
        awardInput.placeholder = "Funding award name, e.g. Horizon Europe";
        awardInput.value = award;
        awardInput.style.marginRight = "10px";
        
        // Create the input for the funder identifer
        const identiferFunding = document.createElement("input");
        identiferFunding.type = "text";
        identiferFunding.name = "funding_identifier";  // Flask will collect these as a list
        identiferFunding.className = "funding-identifier";
        identiferFunding.placeholder = "Funding award identifier number, e.g. 101136748";
        identiferFunding.value = identifier; 
    
        // Append both inputs to the contact container
        funderContainer.appendChild(fundingOrg);
        funderContainer.appendChild(fundingURL);
        funderContainer.appendChild(awardInput);
        funderContainer.appendChild(identiferFunding);
        addRemoveButton(funderContainer);
    
        // Append the contact container to the main container
        document.getElementById("funder-container").appendChild(funderContainer);
    }