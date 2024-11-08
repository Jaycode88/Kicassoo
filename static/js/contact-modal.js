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
                    // Close the modal
                    $('#contactModal').modal('hide');

                    // Display message on the main page
                    const messagesContainer = document.getElementById("messages-container");
                    messagesContainer.innerHTML = ''; // Clear existing messages

                    // Create the new alert message element
                    const alertDiv = document.createElement("div");
                    alertDiv.classList.add("alert", "alert-success"); // Use "alert-danger" if it's an error
                    alertDiv.textContent = data.message || "Your message has been sent successfully!";

                    messagesContainer.appendChild(alertDiv);

                    // Reset the form
                    contactForm.reset();

                    // Automatically fade out message after a few seconds
                    setTimeout(() => {
                        alertDiv.remove();
                    }, 5000);
                } else {
                    // Handle errors in form submission
                    const messagesContainer = document.getElementById("messages-container");
                    messagesContainer.innerHTML = ''; // Clear existing messages

                    const alertDiv = document.createElement("div");
                    alertDiv.classList.add("alert", "alert-danger");
                    alertDiv.textContent = data.message || "There was an error with your submission.";
                    messagesContainer.appendChild(alertDiv);
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred. Please try again.");
            });
    });
});
