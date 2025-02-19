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
      showPopupAlert("Inscription réussie ! Veuillez consulter votre boîte e-mail.");
    
      const modal = bootstrap.Modal.getInstance(document.getElementById("registrationModal"));
      modal.hide();

      document.querySelector("form").reset();
    } else {
      const error = await response.json();
      showAlert(`Erreur: ${error.detail}`, 'danger', '#alertContainer');
    }
  });
  

  // SENDING MESSAGE FROM CONTACT US 

  document.getElementById("contactForm").addEventListener("submit", async function (event) {
    event.preventDefault(); 

    // Collect form data
    const formData = new FormData();
    formData.append("name", document.getElementById("name").value);
    formData.append("email", document.getElementById("email").value);
    formData.append("subject", document.getElementById("subject").value);
    formData.append("message", document.getElementById("message").value);

    // Send data to FastAPI backend
    try {
        const response = await fetch("/send-message", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            document.getElementById("responseMessage").innerText = result.message;
            document.getElementById("contactForm").reset();
            setTimeout(() => {
            document.getElementById("responseMessage").innerText = "";
          }, 5000);

        } else {
            document.getElementById("responseMessage").innerText = "Erreur : " + result.error;
            document.getElementById("responseMessage").style.color = "red";
            setTimeout(() => {
            document.getElementById("responseMessage").innerText = "";
          }, 5000);

        }
    } catch (error) {
        console.error("Erreur:", error);
        document.getElementById("responseMessage").innerText = "Une erreur est survenue.";
        document.getElementById("responseMessage").style.color = "red";
        setTimeout(() => {
        document.getElementById("responseMessage").innerText = "";
      }, 5000);
    }
});
