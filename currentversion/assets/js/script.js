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

/* script to add event to calender */
function addToCalendar() {
    window.open('https://calendar.google.com/calendar/render?action=TEMPLATE&text=This%20is%20Us:%20The%20Beauty%20Behind%20the%20Brush&dates=20241202T090000Z/20241231T170000Z&details=Kicassoo%27s%20exhibition%20displays%20a%20loving%20and%20truthful%20story%20of%20her%20journey%20in%20art.%20From%20tears%20to%20cheers,%20and%20black%20and%20white%20to%20bouncing%20bright%20colors,%20her%20work%20captures%20the%20essence%20of%20a%20person%27s%20emotions%20at%20a%20specific%20time%20and%20place.%20From%20her%20happiest%20moments%20to%20her%20deepest%20thoughts,%20Kicassoo%27s%20art%20speaks%20volumes.%20Some%20of%20her%20greatest%20works%20come%20from%20the%20Animal%20Kingdom%20collection,%20showcasing%20her%20passion%20and%20dedication.%20This%20exhibition%20is%20a%20testament%20to%20her%20hard%20work%20and%20artistic%20development%20over%20the%20past%20few%20years.%20Stay%20updated%20on%20more%20about%20this%20exhibition%20on%20Instagram:%20@kicassoo.&location=The%20People%27s%20Gallery,%20The%20Forum,%20Elmer%20Square,%20Southend-on-Sea,%20Essex,%20SS1%201NS', '_blank');
}
