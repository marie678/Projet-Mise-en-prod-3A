// ----------------------------------------------------
// File: scripts.js
// Description: JavaScript file creating functions to be used in the final result html page (templatev1.4.0.html).
// They enable interactional display of table or print to pdf functionality 
// (ensuring the pdf is rendered correctly with hidden table and without interactive butons).

// Show nutrition facts table when the "Show Table" button is clicked
document.getElementById('showTableButton').addEventListener('click', function() {
    document.getElementById('myTable').style.display = 'table'; 
});

// Add event listener to the print to pdf button
document.getElementById('printButton').addEventListener('click', function() {
window.print(); 
});