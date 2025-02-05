import { showAlert, showPopupAlert} from './conmon.js';

document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();  // Empêche le formulaire de s'envoyer de manière traditionnelle

        // Extraire les valeurs du formulaire
        const formData = new FormData(loginForm);

        try {
            // Faire une requête POST vers le serveur pour la connexion
            const response = await fetch("/login/", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                let errorMessage = "Échec de la connexion ! réessayez encore.";
                
                if (errorData && errorData.detail) {
                    errorMessage = errorData.detail;
                }

                showPopupAlert(errorMessage);
                return;
            }
            const responseData = await response.json();

            document.addEventListener("DOMContentLoaded", () => {
                const logoModalElement = document.getElementById("logoTransitionModal");
                // Vous pouvez ajouter ici le code nécessaire pour manipuler le modal si besoin
            });

            if (responseData.redirect_url) {
                window.location.href = responseData.redirect_url;
            } else {
                alert("Connexion réussie ! Redirection vers la page d'accueil...");
            }

        } catch (error) {
            showPopupAlert("Une erreur réseau s'est produite. Veuillez vérifier votre connexion et réessayer.");
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
                showPopupAlert("Échec de la déconnexion. Veuillez réessayer.");
            }
        } catch (error) {
            showPopupAlert("Une erreur réseau s'est produite. Veuillez réessayer plus tard.");
        }
    });
});
