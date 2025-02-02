document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();  // Prevent the form from submitting in the traditional way

        // Extract form values
        const formData = new FormData(loginForm);

        try {
            // Make a POST request to the server for login
            const response = await fetch("/login/", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                let errorMessage = "Login failed. Please try again.";
                
                if (errorData && errorData.detail) {
                    errorMessage = errorData.detail;
                }

                showAlert(errorMessage, "danger", "#alertContainer");
                return;
            }

            alert('loggining!!')

            // If the response is okay, assume login is successful
            const responseData = await response.json();
            alert('loggining innnnnn!!')

            document.addEventListener("DOMContentLoaded", () => {
                const logoModalElement = document.getElementById("logoTransitionModal");
            
                if (logoModalElement) {
                    // Show the modal
                    logoModalElement.classList.add("visible");
                    logoModalElement.classList.remove("hidden");
                    console.log("Logo modal displayed");
            
                    // Hide the modal after 5 seconds
                    setTimeout(() => {
                        logoModalElement.classList.add("hidden");
                        logoModalElement.classList.remove("visible");
                        console.log("Logo modal hidden");
                    }, 5000);
                } else {
                    console.error("Modal element not found in DOM.");
                }
            });

            if (responseData.redirect_url) {
                window.location.href = responseData.redirect_url;
            } else {
                showAlert("Login successful! Redirecting to home...", "success", "#alertContainer");
                /* setTimeout(() => {
                    window.location.href = "/home";
                }, 1000);*/
            }

        } catch (error) {
            console.error("Network Error:", error);
            showAlert("A network error occurred. Please check your network and try again.", "danger", "#alertContainer");
        }
    });
});

// LOGOUT BUTTON SETTINGS

document.addEventListener("DOMContentLoaded", function () {
    const logoutButton = document.getElementById("logoutButton");

    // Add event listener for logout button
    logoutButton.addEventListener("click", async function (event) {
        event.preventDefault();  // Prevent the default link behavior

        try {
            // Send POST request to /logout/ endpoint
            const response = await fetch("/logout/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            });

            // If logout is successful, redirect to login page
            if (response.ok) {
                window.location.href = "/admin-login";
            } else {
                const errorData = await response.json();
                console.error("Erreur de déconnexion :", errorData);
                alert("Échec de la déconnexion. Veuillez réessayer.");
            }
        } catch (error) {
            console.error("Erreur réseau :", error);
            alert("Une erreur réseau s'est produite. Veuillez réessayer plus tard.");
        }
    });
});
