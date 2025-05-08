// Search the Marine Regions API based on input
document.getElementById("search_regions").addEventListener("input", function () {
    const query = this.value.trim();

    if (query.length >= 3) {  // Only search after the user types at least 3 characters
        fetch(`https://www.marineregions.org/rest/getGazetteerRecordsByName.json/${query}/`)
            .then(response => response.json())
            .then(data => {
                const tableBody = document.getElementById("regions_table").getElementsByTagName("tbody")[0];
                tableBody.innerHTML = "";  // Clear the previous table rows
                const table = document.getElementById("regions_table");
                table.style.display = "block";  // Show the table

                // Populate the table with search results
                data.forEach(region => {
                    const row = document.createElement("tr");

                    // Create the region name cell
                    const regionNameCell = document.createElement("td");
                    regionNameCell.textContent = region.preferredGazetteerName;
                    row.appendChild(regionNameCell);

                    // Create the type cell
                    const typeCell = document.createElement("td");
                    typeCell.textContent = region.placeType;
                    row.appendChild(typeCell);

                    // Create the source cell
                    const sourceCell = document.createElement("td");
                    sourceCell.textContent = region.gazetteerSource;
                    row.appendChild(sourceCell);

                    // Add click event to the row
                    row.addEventListener("click", function () {
                        // Construct the full URL for MRGID
                        const mrgidUrl = `http://marineregions.org/mrgid/${region.MRGID}`;
                        // When the user clicks the row, populate the name and identifier
                        document.getElementById("spatial_coverage_name").value = region.preferredGazetteerName;
                        document.getElementById("spatial_coverage_identifier").value = mrgidUrl;
                        table.style.display = "none";  // Hide the table after selection
                    });

                    tableBody.appendChild(row);
                });
            })
            .catch(error => console.error("Error fetching data from Marine Regions API:", error));
    } else {
        // Hide the table if the search query is too short
        document.getElementById("regions_table").style.display = "none";
    }
});

function clearMarineRegions() {
    document.getElementById("spatial_coverage_name").value = '';
    document.getElementById("spatial_coverage_identifier").value = '';
}