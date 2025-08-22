let creatorCount = 0;

document.addEventListener("DOMContentLoaded", function() {
    
    // Function to add a new creator input
    window.addCreator = function(name = '', type = 'Organizational', givenName = '', familyName = '') {
        creatorCount++;
        const container = document.getElementById('creators-container');
        
        const creatorDiv = document.createElement('div');
        creatorDiv.className = 'creator-entry';
        creatorDiv.id = `creator-${creatorCount}`;
        creatorDiv.style.cssText = 'border: 1px solid #ddd; padding: 1px 5px; background-color: #fff;';
        
        creatorDiv.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h5 style="margin: 2px; font-weight: lighter; font-style: italic;">Creator ${creatorCount}</h5>
                <button type="button" onclick="removeCreator(${creatorCount})" style="background: #dc3545; color: white; border: none; padding: 2px 8px; border-radius: 3px;">Remove</button>
            </div>

            <label for="creator-type-${creatorCount}" style="font-size: medium;">Creator Type:</label>
            <select id="creator-type-${creatorCount}" name="creator-type-${creatorCount}" style="width: 100%; margin: 5px 0;" onchange="toggleCreatorFields(${creatorCount})">
                <option value="Organizational" ${type === 'Organizational' ? 'selected' : ''}>Organization</option>
                <option value="Personal" ${type === 'Personal' ? 'selected' : ''}>Person</option>
            </select>
            
            <!-- Organization name field -->
            <div id="org-name-field-${creatorCount}" style="${type === 'Personal' ? 'display: none;' : ''}">
                <label for="creator-name-${creatorCount}" style="font-size: medium;">Organization Name:</label>
                <input type="text" id="creator-name-${creatorCount}" name="creator-name-${creatorCount}" placeholder="Organization Name" value="${name}" style="width: 100%; margin: 5px 0;">
            </div>
            
            <!-- Person name fields -->
            <div id="person-name-fields-${creatorCount}" style="${type === 'Personal' ? '' : 'display: none;'}">
                <label for="creator-given-name-${creatorCount}" style="font-size: medium;">Given Name:</label>
                <input type="text" id="creator-given-name-${creatorCount}" name="creator-given-name-${creatorCount}" placeholder="Given Name" value="${givenName}" style="width: 100%; margin: 5px 0;">
                
                <label for="creator-family-name-${creatorCount}" style="font-size: medium;">Family Name:</label>
                <input type="text" id="creator-family-name-${creatorCount}" name="creator-family-name-${creatorCount}" placeholder="Family Name" value="${familyName}" style="width: 100%; margin: 5px 0;">
            </div>
        `;
        
        container.appendChild(creatorDiv);
    };

    // Function to remove a creator
    window.removeCreator = function(id) {
        const creatorDiv = document.getElementById(`creator-${id}`);
        if (creatorDiv) {
            creatorDiv.remove();
        }
    };

    // Function to toggle creator name fields based on type
    window.toggleCreatorFields = function(id) {
        const creatorType = document.getElementById(`creator-type-${id}`).value;
        const orgField = document.getElementById(`org-name-field-${id}`);
        const personFields = document.getElementById(`person-name-fields-${id}`);
        
        if (creatorType === 'Personal') {
            orgField.style.display = 'none';
            personFields.style.display = 'block';
        } else {
            orgField.style.display = 'block';
            personFields.style.display = 'none';
        }
    };

    // Prepopulate DOI form when it opens
    window.toggleDoiForm = function() {
        const container = document.getElementById('doi-form-container');
        const isVisible = container.style.display !== 'none';
        
        if (isVisible) {
            container.style.display = 'none';
            // Clear creators when closing
            document.getElementById('creators-container').innerHTML = '';
            creatorCount = 0;
        } else {
            // Prepopulate fields from main form
            document.getElementById('doi-title').value = document.getElementById('project_name').value || '';
            document.getElementById('doi-url').value = document.getElementById('url').value || '';
            document.getElementById('doi-publisher').value = document.getElementById('project_name').value || '';
            
            // Add first creator with project name as default
            addCreator(document.getElementById('project_name').value || '');
            
            container.style.display = 'block';
        }
    };

    window.submitDoiRequest = function() {
        const creators = [];
        const creatorEntries = document.querySelectorAll('.creator-entry');
        
        // Collect all creator data
        creatorEntries.forEach((entry, index) => {
            const id = entry.id.split('-')[1];
            const creatorType = document.getElementById(`creator-type-${id}`).value;
            
            let creatorData = {
                nameType: creatorType
            };
            
            if (creatorType === 'Personal') {
                const givenName = document.getElementById(`creator-given-name-${id}`).value;
                const familyName = document.getElementById(`creator-family-name-${id}`).value;
                creatorData.name = givenName && familyName ? `${familyName}, ${givenName}` : `${givenName} ${familyName}`.trim();
                creatorData.givenName = givenName;
                creatorData.familyName = familyName;
            } else {
                creatorData.name = document.getElementById(`creator-name-${id}`).value;
            }
            
            // Only add creator if name is provided
            if (creatorData.name.trim()) {
                creators.push(creatorData);
            }
        });

        const doiData = {
            title: document.getElementById('doi-title').value,
            url: document.getElementById('doi-url').value,
            creators: creators,
            publisher: document.getElementById('doi-publisher').value
        };

        // Validate required fields
        if (!doiData.title || !doiData.url || creators.length === 0) {
            document.getElementById('doi-result').textContent = "Error: Title, URL, and at least one Creator are required";
            return;
        }

        fetch('/generate_doi', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(doiData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.doi) {
                document.getElementById('doi-result').textContent = "DOI created: " + data.doi;
                document.getElementById('doi-form-container').style.display = 'none';
            } else {
                document.getElementById('doi-result').textContent = "Error: " + (typeof data.error === "string" ? data.error : JSON.stringify(data.error) || "Unknown error");
            }
        })
        .catch(error => {
            document.getElementById('doi-result').textContent = "Error: " + error.message;
        });
    };
});