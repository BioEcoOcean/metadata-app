// Cache for ENVO data
let envoDataCache = null;

// Function to handle the searching of ENVO ontology
function searchEnvoKeywords(query) {
    return new Promise((resolve, reject) => {
        if (envoDataCache) {
            resolve(filterEnvoResults(envoDataCache, query));
        } else {
            fetch(`https://raw.githubusercontent.com/EnvironmentOntology/envo/master/envo.json`)
                .then(response => response.json())
                .then(data => {
                    envoDataCache = data;
                    resolve(filterEnvoResults(data, query));
                })
                .catch(error => reject("Error fetching ENVO data: " + error));
        }
    });
}

// Filter ENVO data
function filterEnvoResults(data, query) {
    const graphs = data.graphs || [];
    if (graphs.length === 0) return [];

    const nodes = graphs[0].nodes || [];
    return nodes
        .filter(node => node.type === "CLASS" && node.lbl && node.lbl.toLowerCase().includes(query.toLowerCase()))
        .map(node => ({ label: node.lbl, id: node.id }));
}

// Function to handle the searching of BODC NERC ontology through SPARQL
function searchBodcNercKeywords(query) {
    const sparqlQuery = `
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?uri ?label
        WHERE {
            ?uri a skos:Concept ;
                 skos:prefLabel ?label .
            FILTER (CONTAINS(LCASE(?label), "${query.toLowerCase()}"))
        }
        LIMIT 50
    `;

    const endpoint = "https://vocab.nerc.ac.uk/sparql/sparql";

    return fetch(endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/sparql-query",
            Accept: "application/json",
        },
        body: sparqlQuery,
    })
        .then(response => response.json())
        .then(data => {
            const results = data.results.bindings || [];
            return results.map(binding => ({
                label: binding.label.value,
                id: binding.uri.value,
            }));
        })
        .catch(error => {
            console.error("Error fetching data from BODC NERC SPARQL endpoint:", error);
            return [];
        });
}


// Function to perform a combined search in both ENVO and BODC NERC
function searchKeywords() {
    const query = document.getElementById("keyword-search").value.trim();
    if (!query) {
        alert("Please enter a keyword to search.");
        return;
    }

    const keywordResults = document.getElementById("keyword-results");
    keywordResults.innerHTML = "<p>Searching...</p>";

    Promise.all([searchEnvoKeywords(query), searchBodcNercKeywords(query)])
        .then(([envoResults, bodcResults]) => {
            keywordResults.innerHTML = ""; // Clear previous results

            const combinedResults = [...envoResults, ...bodcResults];
            if (combinedResults.length === 0) {
                keywordResults.innerHTML = "<p>No results found.</p>";
                return;
            }

            combinedResults.forEach(term => {
                const keyword = document.createElement("div");
                keyword.className = "keyword-item";
                keyword.textContent = `${term.label} (Source: ${term.id.includes("purl.obolibrary.org") ? "ENVO" : "BODC NERC"})`;

                keyword.addEventListener("click", () => addKeyword(term.label, term.id));

                keywordResults.appendChild(keyword);
            });
        })
        .catch(error => {
            console.error("Error during keyword search:", error);
            keywordResults.innerHTML = "<p>An error occurred while searching. Please try again.</p>";
        });
}

// Add selected keyword
function addKeyword(label, id) {
    const selectedKeywords = document.getElementById("selected-keywords");
    const hiddenKeywords = document.getElementById("selected-keywords-hidden");

    // Create a container for the selected keyword
    const keywordContainer = document.createElement("div");
    keywordContainer.className = "keyword-container";
    keywordContainer.style.display = "flex";
    keywordContainer.style.alignItems = "center";
    keywordContainer.style.marginBottom = "5px";

    // Create the remove button
    const removeButton = document.createElement("button");
    removeButton.textContent = "Remove";
    removeButton.type = "button";
    removeButton.style.marginRight = "10px";
    removeButton.onclick = function () {
        keywordContainer.remove(); // Remove the keyword container
        hiddenInput.remove(); // Remove the associated hidden input
    };
    keywordContainer.appendChild(removeButton);

    // Add the keyword label
    const keywordLabel = document.createElement("span");
    keywordLabel.textContent = label;
    keywordContainer.appendChild(keywordLabel);

    // Create the hidden input for form submission
    const hiddenInput = document.createElement("input");
    hiddenInput.type = "hidden";
    hiddenInput.name = "keywords[]"; // Use "keywords[]" for multiple selections
    hiddenInput.value = id;
    hiddenKeywords.appendChild(hiddenInput); // Append to the hidden div

    // Append the keyword container to the selected keywords div
    selectedKeywords.appendChild(keywordContainer);
}



// // Function to handle the searching the ENVO ontology
// let envoDataCache = null;

// function searchEnvoKeywords(query) {
//     // Make the fetch request to the ENVO JSON data
//     if (envoDataCache) {
//         displayMatchingTerms(envoDataCache);
//     } else {
//     fetch(`https://raw.githubusercontent.com/EnvironmentOntology/envo/refs/heads/master/envo.json`)
//         .then(response => response.json()) // Parse the response body to JSON
//         .then(data => {
//             // Log the data to inspect its structure
//             console.log("Received data:", data);

//             // Clear previous results
//             const keywordResults = document.getElementById("keyword-results");
//             keywordResults.innerHTML = "";

//             // Navigate to the "nodes" array within the "graphs" array
//             const graphs = data.graphs || [];
//             if (graphs.length === 0) {
//                 keywordResults.innerHTML = "<p>No results found.</p>";
//                 return;
//             }

//             const nodes = graphs[0].nodes || [];

//             // Filter nodes by "type: CLASS" and search the "lbl" field
//             const matchingTerms = nodes.filter(node =>
//                 node.type === "CLASS" && node.lbl && node.lbl.toLowerCase().includes(query.toLowerCase())
//             );

//             // Show the results or a message if no results are found
//             if (matchingTerms.length === 0) {
//                 keywordResults.innerHTML = "<p>No results found.</p>";
//             } else {
//                 matchingTerms.forEach(term => {
//                     const keyword = document.createElement("div");
//                     keyword.className = "keyword-item";
//                     keyword.textContent = term.lbl;

//                     // Add a click event to select the keyword
//                     keyword.addEventListener("click", function () {
//                         addKeyword(term.lbl, term.id);
//                     });

//                     keywordResults.appendChild(keyword);
//                 });
//             }
//         })
//         .catch(error => console.error("Error fetching data from ENVO JSON:", error));
// }}

// function searchBodcNercKeywords(query) {
//     fetch(`https://vocab.nerc.ac.uk/search?query=${encodeURIComponent(query)}&format=json`)
//         .then(response => response.json())
//         .then(data => {
//             console.log("BODC NERC Results:", data);

//             const keywordResults = document.getElementById("keyword-results");
//             keywordResults.innerHTML = "";

//             const results = data.results || [];
//             if (results.length === 0) {
//                 keywordResults.innerHTML += "<p>No results found in BODC NERC.</p>";
//             } else {
//                 results.forEach(item => {
//                     const keyword = document.createElement("div");
//                     keyword.className = "keyword-item";
//                     keyword.textContent = item.prefLabel;

//                     // Add click event to select keyword
//                     keyword.addEventListener("click", function () {
//                         addKeyword(item.prefLabel, item.uri);
//                     });

//                     keywordResults.appendChild(keyword);
//                 });
//             }
//         })
//         .catch(error => console.error("Error fetching BODC NERC data:", error));
// }


// // Function to add selected keyword to the list
// function addKeyword(label, id) {
//     const selectedKeywords = document.getElementById("selected-keywords");
//     const hiddenKeywords = document.getElementById("selected-keywords-hidden");

//     const keywordContainer = document.createElement("div");
//     keywordContainer.className = "keyword-container";

//     const removeButton = document.createElement("button");
//     removeButton.textContent = "Remove";
//     removeButton.type = "button";
//     removeButton.onclick = function () {
//         keywordContainer.remove();
//         hiddenInput.remove(); // Remove the hidden input when the keyword is removed
//     };
//     keywordContainer.appendChild(removeButton);

//     const keywordLabel = document.createElement("span");
//     keywordLabel.textContent = label;
//     keywordContainer.appendChild(keywordLabel);

//     const hiddenInput = document.createElement("input");
//     hiddenInput.type = "hidden";
//     hiddenInput.name = "keywords[]"; // Use "keywords[]" for multiple selections
//     hiddenInput.value = id;
//     hiddenKeywords.appendChild(hiddenInput); // Append to hidden div

//     selectedKeywords.appendChild(keywordContainer);
// }

// Add event listener to handle "Enter" key press and trigger search
document.getElementById('keyword-search').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent form submission on Enter key
        const query = event.target.value;
        searchEnvoKeywords(query); // Trigger the search
    }
});
