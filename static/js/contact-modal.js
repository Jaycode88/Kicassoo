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
            .then(response => {
                // Check if the response is OK (status 200-299)
                if (!response.ok) {
                    // If not, return the error JSON response
                    return response.json().then(data => {
                        throw new Error(data.message || "There was an error with your submission.");
                    });
                }
                // Otherwise, return the successful JSON response
                return response.json();
            })
            .then(data => {
                const messagesContainer = document.getElementById("messages-container");
                messagesContainer.innerHTML = ''; // Clear existing messages

                // Create a new alert message element
                const alertDiv = document.createElement("div");
                alertDiv.classList.add("alert");

                // Set alert type and message content based on success status
                if (data.success) {
                    $('#contactModal').modal('hide'); // Close the modal on success
                    alertDiv.classList.add("alert-success");
                    alertDiv.textContent = data.message;
                    contactForm.reset(); // Reset form fields
                } else {
                    alertDiv.classList.add("alert-danger");
                    alertDiv.textContent = data.message;
                }

                messagesContainer.appendChild(alertDiv);

                // Automatically fade out message after 5 seconds
                setTimeout(() => {
                    alertDiv.remove();
                }, 5000);
            })
            .catch(error => {
                // Catch non-OK responses or other errors and display a message
                const messagesContainer = document.getElementById("messages-container");
                messagesContainer.innerHTML = ''; // Clear any existing messages

                const alertDiv = document.createElement("div");
                alertDiv.classList.add("alert", "alert-danger");
                alertDiv.textContent = error.message;
                messagesContainer.appendChild(alertDiv);

                setTimeout(() => {
                    alertDiv.remove();
                }, 5000);
            });
    });
});
