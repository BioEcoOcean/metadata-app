function addRemoveButton(container) {
    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.textContent = "Remove";
    removeButton.style.marginLeft = "10px"; // Add some spacing for better visuals
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
function addOutputInput() {
    const newInputContainer = document.createElement("div");
    newInputContainer.className = "outputs-container";
    newInputContainer.style.marginTop = "5px";  // Add some spacing for better visuals
    
    const newInput = document.createElement("input");
    newInput.type = "text";
    newInput.name = "outputs";  // Keep name="keywords" so Flask collects them as a list
    newInput.className = "outputs-input";
    newInput.placeholder = "Enter an output";
    newInput.style.marginTop = "5px";  // Add some spacing for better visuals  
    
    newInputContainer.appendChild(newInput);
    addRemoveButton(newInputContainer);
    // Append the new input to the container
    document.getElementById("outputs-container").appendChild(newInputContainer);
}
function addSOPInput() {
    const newInputContainer = document.createElement("div");
    newInputContainer.className = "sops-input-container";
    newInputContainer.style.marginTop = "5px";
    
    const newInput = document.createElement("input");
    newInput.type = "url";
    newInput.name = "sops";  
    newInput.className = "sops-input"; newInput.placeholder = "Enter a link to an SOP";
    newInput.style.marginTop = "5px";
    
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
    checkboxLabel.textContent = "Is this SOP included in the Ocean Best Practices (OBPs)?";
    checkboxLabel.style.marginLeft = "5px"; // Add some spacing between the checkbox and the label

    // Append the checkbox and label to the container
    checkboxContainer.appendChild(checkbox);
    checkboxContainer.appendChild(checkboxLabel);

    newInputContainer.appendChild(newInput);
    newInputContainer.appendChild(checkboxContainer);
    addRemoveButton(newInputContainer);

    document.getElementById("sops-container").appendChild(newInputContainer);
    }
function addContactInput(name = "", email = "", role = "", id = "") {
        // Create a new container for the contact pair
        const contactContainer = document.createElement("div");
        contactContainer.className = "contact-container";
        contactContainer.style.marginTop = "10px"; // Add spacing between pairs
    
        // Create the input for the contact name
        const nameInput = document.createElement("input");
        nameInput.type = "text";
        nameInput.name = "contact_names";  // Flask will collect these as a list
        nameInput.className = "contact-name-input";
        nameInput.placeholder = "Enter contact name";
        nameInput.value = name;
        nameInput.style.marginRight = "10px"; // Add spacing between the two inputs
        nameInput.required = true;
    
        // Create the input for the contact email
        const emailInput = document.createElement("input");
        emailInput.type = "email";
        emailInput.name = "contact_emails";  // Flask will collect these as a list
        emailInput.className = "contact-email-input";
        emailInput.placeholder = "Enter contact email";
        emailInput.value = email;
        emailInput.required = true;

        // Create the input for the contact role
        const roleSelect = document.createElement("select");
        roleSelect.name = "contact_roles";  // Flask will collect these as a list
        roleSelect.className = "contact-role-select";
        roleSelect.style.marginRight = "10px";
        nameInput.required = true;

        // Add a default "Select contact type" option
        const defaultOption = document.createElement("option");
        defaultOption.value = ""; // Empty value
        defaultOption.textContent = "Select contact type";
        defaultOption.disabled = true; // Make it unselectable
        defaultOption.selected = !role; // Select this by default if no role is provided
        roleSelect.appendChild(defaultOption);
        
        // Add dropdown options
        const roles = ["Organization", "Contact Person", "Data collector", "Data manager", "Researcher", "Other"];
        roles.forEach(optionRole  => {
            const option = document.createElement("option");
            option.value = optionRole ;
            option.textContent = optionRole ;
            if (optionRole === role) {
                option.selected = true; // Preselect the role
            }
            roleSelect.appendChild(option);
        });

        // Create the input for the contact identifer
        const identiferInput = document.createElement("input");
        identiferInput.type = "url";
        identiferInput.name = "contact_ids";  // Flask will collect these as a list
        identiferInput.className = "contact-id-input";
        identiferInput.placeholder = "Enter contact id";
        identiferInput.value = id; 
    
        // Append both inputs to the contact container
        contactContainer.appendChild(nameInput);addRemoveButton(contactContainer);
        contactContainer.appendChild(emailInput);
        contactContainer.appendChild(roleSelect);
        contactContainer.appendChild(identiferInput);
        
    
        // Append the contact container to the main container
        document.getElementById("contacts-container").appendChild(contactContainer);
    }

    function addFunders(name = "", email = "", role = "", id = "") {
        // Create a new container for the contact pair
        const funderContainer = document.createElement("div");
        funderContainer.className = "funder-container";
        funderContainer.style.marginTop = "10px"; // Add spacing between pairs
    
        // Create the input for the funder organization name
        const fundingOrg = document.createElement("input");
        fundingOrg.type = "text";
        fundingOrg.name = "funder_name";  // Flask will collect these as a list
        fundingOrg.className = "funder-name";
        fundingOrg.placeholder = "Enter name of funding organization";
        fundingOrg.value = name;
        fundingOrg.style.marginRight = "10px"; // Add spacing between the two inputs
        
        // Create the input for the funder url
        const fundingURL = document.createElement("input");
        fundingURL.type = "url";
        fundingURL.name = "funder_url";  // Flask will collect these as a list
        fundingURL.className = "funder-url";
        fundingURL.placeholder = "Enter URL of funding organisation";
        
        fundingURL.style.marginRight = "10px";
        
        // Create the input for the funder award
        const awardInput = document.createElement("input");
        awardInput.type = "text";
        awardInput.name = "funding_name";  // Flask will collect these as a list
        awardInput.className = "funding-name";
        awardInput.placeholder = "Enter name of the funding award";
        awardInput.style.marginRight = "10px";
        
        // Create the input for the funder identifer
        const identiferFunding = document.createElement("input");
        identiferFunding.type = "text";
        identiferFunding.name = "funding_identifier";  // Flask will collect these as a list
        identiferFunding.className = "funding-identifier";
        identiferFunding.placeholder = "Enter the identifier of the funding award";
        identiferFunding.value = id; 
    
        // Append both inputs to the contact container
        funderContainer.appendChild(fundingOrg);addRemoveButton(funderContainer);
        funderContainer.appendChild(fundingURL);
        funderContainer.appendChild(awardInput);
        funderContainer.appendChild(identiferFunding);
    
        // Append the contact container to the main container
        document.getElementById("funder-container").appendChild(funderContainer);
    }