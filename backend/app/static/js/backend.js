import {showPopupAlert, showAlert } from './conmon.js';


// POST FORM 

document.querySelector("form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = {
      full_name: document.getElementById("fullName").value,
      whatsapp_number: document.getElementById("whatsappNumber").value,
      email: document.getElementById("emailAddress").value,
      gender: document.getElementById("gender").value,
      preferred_course: document.getElementById("preferredCourse").value,
      agreement: document.getElementById("agreement").checked,
    };
    
    const response = await fetch("/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    
    if (response.ok) {
      showPopupAlert("Inscription réussie !");
    
      const modal = bootstrap.Modal.getInstance(document.getElementById("registrationModal"));
      modal.hide();

      document.querySelector("form").reset();
    } else {
      const error = await response.json();
      showAlert(`Erreur: ${error.detail}`, 'danger', '#alertContainer');
    }
  });
  