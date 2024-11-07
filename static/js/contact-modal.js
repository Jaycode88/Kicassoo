document.addEventListener("DOMContentLoaded", function () {
    const contactForm = document.getElementById("contactForm");
    const contactUrl = contactForm.getAttribute("data-url");
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    contactForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const formData = new FormData(contactForm);

        fetch(contactUrl, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrfToken,
            },
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Your message was sent successfully!");
                    contactForm.reset();
                    $('#contactModal').modal('hide');
                } else {
                    alert("An error occurred. Please try again.");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred. Please try again.");
            });
    });
});
