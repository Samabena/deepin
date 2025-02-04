import {showPopupAlert, showAlert } from './conmon.js';

document.addEventListener("DOMContentLoaded", function () {
    const forgotPasswordForm = document.getElementById("forgotPasswordForm");
    const spinner = document.getElementById("spinner");
  
    forgotPasswordForm.addEventListener("submit", async function (event) {
      event.preventDefault(); 
  
      const formData = new FormData(forgotPasswordForm);
      spinner.classList.remove("d-none");
  
      try {
        const response = await fetch("/forgot-password/", {
          method: "POST",
          body: formData
        });
  
        spinner.classList.add("d-none");

        if (response.ok) {
            // Message de succès positif
            showPopupAlert("Si votre email est enregistré, vous recevrez un lien de réinitialisation de mot de passe.");
        } else {
            // Message d'erreur négatif
            const errorData = await response.json();
            showPopupAlert("Erreur : ${errorData.detail}");
        }
        } catch (error) {
        console.error("Erreur réseau :", error);
        showPopupAlert("Une erreur réseau est survenue. Veuillez vérifier votre connexion et réessayer.");
        }
    });
  });