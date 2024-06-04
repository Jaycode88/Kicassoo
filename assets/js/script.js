/* Script to Prevent Right Click(image copying) */
document.addEventListener('DOMContentLoaded', function () {
    window.addEventListener('contextmenu', function (e) {
        e.preventDefault();
    });
});
