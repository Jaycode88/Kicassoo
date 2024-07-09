/* Script to Prevent Right Click(image copying) */
document.addEventListener('DOMContentLoaded', function () {
    var images = document.querySelectorAll('img'); // Select all images

    // Iterate over each image and attach an event listener
    images.forEach(function (img) {
        img.addEventListener('contextmenu', function (e) {
            e.preventDefault(); // Prevent the context menu from appearing
        });
    });
});
