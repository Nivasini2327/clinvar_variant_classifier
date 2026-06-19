/**
 * Variant Pathogenicity Predictor - Main Logic
 */

// Initialize Lucide icons (finds elements with data-lucide attribute and replaces them with SVGs)
lucide.createIcons();

// Get references to DOM elements we will interact with
const loadExampleBtn = document.getElementById('load-example-btn');
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const vcfInput = document.getElementById('vcf-input');
const predictBtn = document.getElementById('predict-btn');

// Sample Variant Data (VCF format) to load when "Load Example" is clicked
const exampleData = `#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\nchr1\t12345\trs123\tA\tG\t30\tPASS\tDP=100\nchr2\t54321\t.\tT\tC\t50\tPASS\tDP=120`;

/**
 * Event Listener for "Load Example" button
 * Populates the textarea with sample VCF data and gives visual feedback
 */
loadExampleBtn.addEventListener('click', () => {
    // Set text area value to example string
    vcfInput.value = exampleData;
    
    // Provide mild visual feedback confirming the injection
    vcfInput.style.backgroundColor = '#ffffff';
    vcfInput.style.borderColor = 'var(--primary)';
    
    // Reset visual feedback after a short delay
    setTimeout(() => {
        vcfInput.style.backgroundColor = '';
        vcfInput.style.borderColor = '';
    }, 300);
});

/**
 * Event Listener for "Upload File" button
 * Programmatically triggers a click on the hidden file input
 */
uploadBtn.addEventListener('click', () => {
    fileInput.click();
});

/**
 * Event Listener for the hidden file input
 * Reads the content of the selected local file and places it into the textarea
 */
fileInput.addEventListener('change', (event) => {
    // Get the first file selected by the user
    const file = event.target.files[0];
    
    if (file) {
        // Create a FileReader to read the file contents
        const reader = new FileReader();
        
        // When the file is loaded, set its content to the textarea
        reader.onload = (e) => {
            vcfInput.value = e.target.result;
        };
        
        // Read the file as standard text
        reader.readAsText(file);
    }
    
    // Reset file input value so users can select the exact same file again if desired
    event.target.value = '';
});

/**
 * Event Listener for "Predict Pathogenicity" button
 * Simulates processing the input data and giving feedback
 */
predictBtn.addEventListener('click', () => {
    const data = vcfInput.value.trim();
    
    // Validate that data exists
    if (!data) {
        alert('Please enter or load VCF data first.');
        return;
    }
    
    // Define Loading UI states
    const originalText = predictBtn.textContent;
    predictBtn.textContent = 'Processing Data...';
    predictBtn.style.opacity = '0.85';
    predictBtn.style.pointerEvents = 'none'; // Prevent multiple clicks

    // Simulate Prediction Server Response network delay (1.2 seconds)
    setTimeout(() => {
        // Count lines of data (ignoring empty lines and header lines starting with #)
        const rowCount = data.split('\n').filter(line => !line.startsWith('#') && line.trim()).length;
        
        // Show mock result alert
        alert(`Successfully processed ${rowCount} variant(s). This is a mocked prediction sequence.`);
        
        // Revert Loading UI states back to normal
        predictBtn.textContent = originalText;
        predictBtn.style.opacity = '1';
        predictBtn.style.pointerEvents = 'auto'; // Re-enable clicks
    }, 1200);
});
