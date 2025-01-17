function addKeywordInput() {
// Create a new input element
    const newInput = document.createElement("input");
    newInput.type = "text";
    newInput.name = "keywords";  // Keep name="keywords" so Flask collects them as a list
    newInput.className = "keyword-input";
    newInput.placeholder = "Enter a keyword";
    newInput.style.marginTop = "5px";  // Add some spacing for better visuals    
    // Append the new input to the container
    document.getElementById("keywords-container").appendChild(newInput);
}
function addSOPInput() {
    // Create a new input element
    const newInput = document.createElement("input");
    newInput.type = "url";
    newInput.name = "sops";  // Keep name="keywords" so Flask collects them as a list
    newInput.className = "sops-input"; newInput.placeholder = "Enter a link to an SOP";
    newInput.style.marginTop = "5px";  // Add some spacing for better visuals
    // Append the new input to the container
    document.getElementById("sops-container").appendChild(newInput);
    }
function addContactInput() {
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
        nameInput.style.marginRight = "10px"; // Add spacing between the two inputs
    
        // Create the input for the contact email
        const emailInput = document.createElement("input");
        emailInput.type = "email";
        emailInput.name = "contact_emails";  // Flask will collect these as a list
        emailInput.className = "contact-email-input";
        emailInput.placeholder = "Enter contact email";

        // Create the input for the contact role
        const roleSelect = document.createElement("select");
        roleSelect.name = "contact_roles";  // Flask will collect these as a list
        roleSelect.className = "contact-role-select";
        roleSelect.style.marginRight = "10px";

        // Create the input for the contact identifer
        const identiferInput = document.createElement("input");
        identiferInput.type = "url";
        identiferInput.name = "contact_ids";  // Flask will collect these as a list
        identiferInput.className = "contact-id-input";
        identiferInput.placeholder = "Enter contact id";

        // Add dropdown options
        const roles = ["Contact Person", "Data collector", "Data manager", "Researcher", "Other"];
        roles.forEach(role => {
            const option = document.createElement("option");
            option.value = role;
            option.textContent = role;
            roleSelect.appendChild(option);
        });
    
        // Append both inputs to the contact container
        contactContainer.appendChild(nameInput);
        contactContainer.appendChild(emailInput);
        contactContainer.appendChild(roleSelect);
        contactContainer.appendChild(identiferInput);
    
        // Append the contact container to the main container
        document.getElementById("contacts-container").appendChild(contactContainer);
    }
    