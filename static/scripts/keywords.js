// Cache for ENVO data
let envoDataCache = null;
const selectedKeywords = []; // Array to store selected keywords

document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("ontology-search");
    const searchBtn = document.getElementById("ontology-search-btn");
    const resultsTableElem = document.getElementById("results-table");
    const resultsTable = document.getElementById("results-table").querySelector("tbody");
    const selectedKeywordsList = document.getElementById("selected-keywords-list");
    const hiddenInput = document.getElementById("selected-keywords-json");

    function triggerKeywordSearch() {
        const query = searchInput.value.trim();
        if (query.length < 3) {
            resultsTable.innerHTML = ""; // Clear results if query is too short
            resultsTableElem.style.display = "none";
            return;
        }
        resultsTableElem.style.display = ""; // Show table

        Promise.all([searchOlsKeywords(query), searchBodcNercKeywords(query)])
            .then(([olsResults, bodcResults]) => {
                resultsTable.innerHTML = ""; // Clear previous results

                const combinedResults = [...olsResults, ...bodcResults];
                if (combinedResults.length === 0) {
                    resultsTable.innerHTML = "<tr><td colspan='3'>No results found</td></tr>";
                    return;
                }

                combinedResults.forEach(item => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${item.label}</td>
                        <td><a href ="${item.id}" target="_blank" rel="noopener noreferrer">${item.id}</a></td>
                        <td>${item.source}</td>
                    `;

                    row.addEventListener("click", function () {
                        addSelectedKeyword(item.label, item.id, item.source, item.obo_id);
                    });

                    resultsTable.appendChild(row);
                });
            })
            .catch(error => console.error("Error fetching ontology data:", error));
    }
    searchBtn.addEventListener("click", triggerKeywordSearch);
    searchInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            triggerKeywordSearch();
        }
    });

    function addSelectedKeyword(label, id, source, obo_id) {
        // Check if the keyword is already added
        if (selectedKeywordsList.querySelector(`[data-id="${id}"]`)) return;

        // Add keyword to the list in DOM
        const keywordDiv = document.createElement("div");
        keywordDiv.dataset.label = label;
        keywordDiv.dataset.id = id;
        keywordDiv.dataset.source = source;
        keywordDiv.dataset.obo_id = obo_id || "";

        keywordDiv.innerHTML = `
            <button class="remove-keyword">Remove</button>
            <span>${label} (${id})</span>
        `;

        keywordDiv.querySelector(".remove-keyword").addEventListener("click", function () {
            keywordDiv.remove();
            updateHiddenKeywordsInput(); // Update hidden input when removing
        });

        selectedKeywordsList.appendChild(keywordDiv);

        // Update hidden input when adding
        updateHiddenKeywordsInput();
    }

    function updateHiddenKeywordsInput() {
        const selectedKeywords = [];
        const keywordItems = selectedKeywordsList.querySelectorAll("div");

        keywordItems.forEach(item => {
            const label = item.dataset.label;
            const id = item.dataset.id;
            const source = item.dataset.source;
            const obo_id = item.dataset.obo_id;

            if (label && id) {
                selectedKeywords.push({ label, id, source, obo_id });
            }
        });

        // Update the hidden input with the JSON string
        hiddenInput.value = JSON.stringify(selectedKeywords);
    }

    function searchOlsKeywords(query) {
        const apiUrl = `https://www.ebi.ac.uk/ols4/api/search`;
        const params = new URLSearchParams({
            q: query,                  // The query term
            ontology: "envo",          // Restrict to the ENVO ontology
            queryFields: "label,synonym", // Search in labels and synonyms
            fieldList: "iri,label,short_form,obo_id,ontology_name", // Fields to return
            rows: 50,                  // Limit to 50 results per page
        });

        return fetch(`${apiUrl}?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                if (data.response && data.response.docs.length > 0) {
                    const uniqueResults = new Map(); // Map to store unique results by IRI
                
                    data.response.docs.forEach(item => {
                        if (!uniqueResults.has(item.iri)) {
                            uniqueResults.set(item.iri, {
                                label: item.label,
                                id: item.iri,       // Use the full URI (IRI)
                                obo_id: item.obo_id, // OBO ID if available
                                source: item.ontology_name || "Unknown" // Source is ontology name or "Unknown"
                            });
                        }
                    });

                    return Array.from(uniqueResults.values()); // Return the unique values as an array
                }
                return [];
            })
            .catch(error => {
                console.error("Error fetching OLS data:", error);
                return [];
            });
    }

    function searchBodcNercKeywords(query) {
        const sparqlQuery = `
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX dce: <http://purl.org/dc/elements/1.1/>

            SELECT ?uri ?label ?identifier
            WHERE {
                ?uri a skos:Concept ;
                    skos:prefLabel ?label  ;
                    dce:identifier ?identifier .
                FILTER (CONTAINS(LCASE(?label), "${query.toLowerCase()}"))
                FILTER NOT EXISTS {
                    ?uri dce:identifier ?excludedIdentifier .
                    FILTER (STRSTARTS(?excludedIdentifier, "SDN:P01::") || STRSTARTS(?excludedIdentifier, "SDN:S25::"))
                    }
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
                    obo_id: binding.identifier ? binding.identifier.value : "",
                    source: "BODC NERC"
                }));
            })
            .catch(error => {
                console.error("Error fetching data from BODC NERC SPARQL endpoint:", error);
                return [];
            });
    }
    
    // Function to get selected keywords as JSON
    window.getSelectedKeywordsJson = function () {
        return JSON.stringify(selectedKeywords, null, 2);
    };
});


// old
// // Cache for ENVO data
// let envoDataCache = null;

// // Function to handle the searching of ENVO ontology
// function searchEnvoKeywords(query) {
//     return new Promise((resolve, reject) => {
//         if (envoDataCache) {
//             resolve(filterEnvoResults(envoDataCache, query));
//         } else {
//             fetch(`https://raw.githubusercontent.com/EnvironmentOntology/envo/master/envo.json`)
//                 .then(response => response.json())
//                 .then(data => {
//                     envoDataCache = data;
//                     resolve(filterEnvoResults(data, query));
//                 })
//                 .catch(error => reject("Error fetching ENVO data: " + error));
//         }
//     });
// }

// // Filter ENVO data
// function filterEnvoResults(data, query) {
//     const graphs = data.graphs || [];
//     if (graphs.length === 0) return [];

//     const nodes = graphs[0].nodes || [];
//     return nodes
//         .filter(node => node.type === "CLASS" && node.lbl && node.lbl.toLowerCase().includes(query.toLowerCase()))
//         .map(node => ({ label: node.lbl, id: node.id }));
// }

// // Function to handle the searching of BODC NERC ontology through SPARQL
// function searchBodcNercKeywords(query) {
//     const sparqlQuery = `
//         PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
//         SELECT ?uri ?label
//         WHERE {
//             ?uri a skos:Concept ;
//                  skos:prefLabel ?label .
//             FILTER (CONTAINS(LCASE(?label), "${query.toLowerCase()}"))
//         }
//         LIMIT 50
//     `;

//     const endpoint = "https://vocab.nerc.ac.uk/sparql/sparql";

//     return fetch(endpoint, {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/sparql-query",
//             Accept: "application/json",
//         },
//         body: sparqlQuery,
//     })
//         .then(response => response.json())
//         .then(data => {
//             const results = data.results.bindings || [];
//             return results.map(binding => ({
//                 label: binding.label.value,
//                 id: binding.uri.value,
//             }));
//         })
//         .catch(error => {
//             console.error("Error fetching data from BODC NERC SPARQL endpoint:", error);
//             return [];
//         });
// }


// // Function to perform a combined search in both ENVO and BODC NERC
// function searchKeywords() {
//     const query = document.getElementById("keyword-search").value.trim();
//     if (!query) {
//         alert("Please enter a keyword to search.");
//         return;
//     }

//     const keywordResults = document.getElementById("keyword-results");
//     keywordResults.innerHTML = "<p>Searching...</p>";

//     Promise.all([searchEnvoKeywords(query), searchBodcNercKeywords(query)])
//         .then(([envoResults, bodcResults]) => {
//             keywordResults.innerHTML = ""; // Clear previous results

//             const combinedResults = [...envoResults, ...bodcResults];
//             if (combinedResults.length === 0) {
//                 keywordResults.innerHTML = "<p>No results found.</p>";
//                 return;
//             }

//             combinedResults.forEach(term => {
//                 const keyword = document.createElement("div");
//                 keyword.className = "keyword-item";
//                 keyword.textContent = `${term.label} (Source: ${term.id.includes("purl.obolibrary.org") ? "ENVO" : "BODC NERC"})`;

//                 keyword.addEventListener("click", () => addKeyword(term.label, term.id));

//                 keywordResults.appendChild(keyword);
//             });
//         })
//         .catch(error => {
//             console.error("Error during keyword search:", error);
//             keywordResults.innerHTML = "<p>An error occurred while searching. Please try again.</p>";
//         });
// }

// // Add selected keyword
// function addKeyword(label, id) {
//     const selectedKeywords = document.getElementById("selected-keywords");
//     const hiddenKeywords = document.getElementById("selected-keywords-hidden");

//     // Create a container for the selected keyword
//     const keywordContainer = document.createElement("div");
//     keywordContainer.className = "keyword-container";
//     keywordContainer.style.display = "flex";
//     keywordContainer.style.alignItems = "center";
//     keywordContainer.style.marginBottom = "5px";

//     // Create the remove button
//     const removeButton = document.createElement("button");
//     removeButton.textContent = "Remove";
//     removeButton.type = "button";
//     removeButton.style.marginRight = "10px";
//     removeButton.onclick = function () {
//         keywordContainer.remove(); // Remove the keyword container
//         hiddenInput.remove(); // Remove the associated hidden input
//     };
//     keywordContainer.appendChild(removeButton);

//     // Add the keyword label
//     const keywordLabel = document.createElement("span");
//     keywordLabel.textContent = label;
//     keywordContainer.appendChild(keywordLabel);

//     // Create the hidden input for form submission
//     const hiddenInput = document.createElement("input");
//     hiddenInput.type = "hidden";
//     hiddenInput.name = "keywords[]"; // Use "keywords[]" for multiple selections
//     hiddenInput.value = id;
//     hiddenKeywords.appendChild(hiddenInput); // Append to the hidden div

//     // Append the keyword container to the selected keywords div
//     selectedKeywords.appendChild(keywordContainer);
// }