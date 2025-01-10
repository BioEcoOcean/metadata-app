var map = L.map('map').setView([0, 0], 1);  // Default position
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    }).addTo(map);
                    
                    var rectangle = L.rectangle([[40,-60], [10, -20]]);
                    rectangle.editing.enable();
                    map.addLayer(rectangle);
        
                    // Initialize the drawn items layer group
                    var drawnItems = new L.FeatureGroup();
                    map.addLayer(drawnItems);
        
                    // Event listener for when the rectangle is drawn or edited
                    rectangle.on('edit', function() {
                        var bounds = rectangle.getBounds();
                        // Update the input fields with the coordinates from the rectangle
                        document.getElementById('north').value = bounds.getNorth();
                        document.getElementById('south').value = bounds.getSouth();
                        document.getElementById('east').value = bounds.getEast();
                        document.getElementById('west').value = bounds.getWest();
                    });