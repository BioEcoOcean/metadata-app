// Form validation
function validateForm() {
        // Required fields with corresponding error messages
        const requiredFields = [
            { id: "project_name", message: "Project Name is required." },
            { id: "url", message: "Project URL is required." },
            { id: "contact_email", message: "Contact Email is required." },
            { id: "license", message: "Please select a license." }
        ];

        // Check Required Fields
        for (let field of requiredFields) {
            const value = document.getElementById(field.id).value.trim();
            if (value === "") {
                alert(field.message);
                return false;
            }
        }
        // 2. Validate Dates
        const startDate = document.getElementById("start_date").value;
        const endDate = document.getElementById("end_date").value;

        if (startDate && endDate) { // Only check if both dates are provided
            if (new Date(startDate) > new Date(endDate)) {
                alert("Start Date cannot be after End Date.");
                return false;
            }
        }
        // Validate URLs
        const projectUrl = document.getElementById("url").value.trim();
        const sopInputs = document.getElementsByName("sop_urls");
        const sopUrls = Array.from(sopInputs).map(input => input.value.trim()).filter(url => url !== ""); // Collect non-empty SOP URLs
        const funderUrl = document.getElementById("funder_url").value.trim();
        const funderName = document.getElementById("funder_name") ? document.getElementById("funder_name").value.trim() : "";

        // Create a list of URLs to validate, with friendly error messages
        const urlsToValidate = [
            { url: projectUrl, message: "Please enter a valid Project URL." },
            ...sopUrls.map(url => ({ url, message: "Please enter a valid SOP URL." })),
            ...(funderName || funderUrl ? [{ url: funderUrl, message: "Please enter a valid Funder URL." }] : [])
        ];

        // Validate all URLs
        for (let item of urlsToValidate) {
            if (!isValidURL(item.url)) {
                alert(item.message);
                return false;
            }
        }
        return true; // Allow form submission
    }
    // Helper function to validate a URL
    function isValidURL(url) {
        try {
            new URL(url);
            return true;
        } catch (e) {
            return false;
        }
}
