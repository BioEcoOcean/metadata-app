// Initialize the map
var map = L.map('map').setView([0, 0], 1);  // Default position
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Function to update the rectangle's bounds
function updateRectangleFromInputs() {
    // Get the values from the input fields
    var north = parseFloat(document.getElementById('north').value) || 40;
    var south = parseFloat(document.getElementById('south').value) || 10;
    var east = parseFloat(document.getElementById('east').value) || -60;
    var west = parseFloat(document.getElementById('west').value) || -20;

    // Disable editing temporarily
    rectangle.editing.disable();

    // Update the rectangle's bounds
    rectangle.setBounds([[south, west], [north, east]]);
    
    // Re-enable editing so the handles move with the updated rectangle
    rectangle.editing.enable();
    map.fitBounds(rectangle.getBounds());  // Adjust the map view to the rectangle
}

// Create the rectangle and add it to the map
var rectangle = L.rectangle([[40, -60], [10, -20]]);
rectangle.editing.enable();
map.addLayer(rectangle);

// Initialize the drawn items layer group
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

// Event listener for when the rectangle is drawn or edited
rectangle.on('edit', function() {
    var bounds = rectangle.getBounds();
    // Update the input fields with the coordinates from the rectangle
    document.getElementById('north').value = bounds.getNorth().toFixed(3);
    document.getElementById('south').value = bounds.getSouth().toFixed(3);
    document.getElementById('east').value = bounds.getEast().toFixed(3);
    document.getElementById('west').value = bounds.getWest().toFixed(3);
});

// Update the rectangle when the inputs are prepopulated
document.addEventListener('DOMContentLoaded', function() {
    updateRectangleFromInputs();    
});

// Add event listeners to update the rectangle when input values change
['north', 'south', 'east', 'west'].forEach(function(id) {
    document.getElementById(id).addEventListener('input', updateRectangleFromInputs);
});
