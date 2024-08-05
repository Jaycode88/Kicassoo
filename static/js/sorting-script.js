/* jshint esversion: 11, jquery: true */

/**
* Script to handle sorting functionality on products page.
* 
* * This script listens for changes to the #sort-selector dropdown,
* then updates the page URL based on the selected sorting option.
**/

// Listen for changes on the #sort-selector dropdown.
$('#sort-selector').change(function () {
    console.log("Sort selector changed"); // Debugging log
    // Store a reference to the changed select element.
    var selector = $(this);
    // Create a URL object based on the current window location.
    var currentUrl = new URL(window.location);

    // Get the value of the selected option.
    var selectedVal = selector.val();
    console.log("Selected value: ", selectedVal); // Debugging log
    // Check if the selected value is not 'reset'.
    if (selectedVal != "reset") {
        // Extract the sort field and direction from the selected value.
        var sort = selectedVal.split("_")[0]; // The field to sort by.
        var direction = selectedVal.split("_")[1]; // The direction of sorting.

        // Update the URL search parameters for sorting.
        currentUrl.searchParams.set("sort", sort);
        currentUrl.searchParams.set("direction", direction);

        // Redirect the browser to the updated URL.
        window.location.replace(currentUrl);
    } else {
        // If 'reset' is selected, remove the sorting parameters.
        currentUrl.searchParams.delete("sort");
        currentUrl.searchParams.delete("direction");
        // Redirect the browser to the updated URL without sorting parameters.
        window.location.replace(currentUrl);
    }
});
