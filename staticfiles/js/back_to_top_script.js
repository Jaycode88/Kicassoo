/* jshint esversion: 11, jquery: true */

$(document).ready(function () {
    // Show or hide the back to top button based on scroll position
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('#back-to-top').removeClass('d-none');
        } else {
            $('#back-to-top').addClass('d-none');
        }
    });

    // Scroll to top functionality
    $('#back-to-top').click(function (e) {
        e.preventDefault();
        // Ensure smooth scrolling for all browsers
        $('html, body').animate({ scrollTop: 0 }, 600);
    });
});