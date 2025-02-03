import {showPopupAlert, showAlert } from './conmon.js';



// BLOG POST SETTINGS 
document.getElementById("blogForm")?.addEventListener("submit", async function(event) {
  
  event.preventDefault();  // ✅ Prevents default GET request
  event.stopPropagation(); // ✅ Prevents propagation issues


  console.log("Submitting form..."); // ✅ Debugging log

  const formData = new FormData(this);
  const imageFile = formData.get("image");

  if (!imageFile) {
      alert("📸 Veuillez sélectionner une image avant de publier !");
      return;
  }

  try {
      // 🔹 Upload Image to Cloudinary
      const cloudinaryForm = new FormData();
      cloudinaryForm.append("file", imageFile);
      cloudinaryForm.append("upload_preset", "my_preset");
      cloudinaryForm.append("folder", "blog_images");

      const cloudinaryResponse = await fetch("https://api.cloudinary.com/v1_1/dfsw4wv22/image/upload", {
          method: "POST",
          body: cloudinaryForm
      });

      const cloudinaryData = await cloudinaryResponse.json();
      if (!cloudinaryData.secure_url) {
          throw new Error("Cloudinary upload failed.");
      }

      const imageUrl = cloudinaryData.secure_url;

      // 🔹 Now send all data (including image URL) to Backend
      formData.set("header_image", imageUrl);
      formData.delete("image");

      const response = await fetch("/submit-blog", {
          method: "POST",
          body: formData,
          headers: { "Accept": "application/json" }
      });

      if (response.redirected) {
        window.location.href = response.url;  // ✅ Redirect to the new blog post
    } else {
        const result = await response.json();
        showPopupAlert(result.message || "Une erreur est survenue.");
    }
      
  } catch (error) {
      console.error("❌ Error:", error);
      alert("❌ Échec de l’envoi. Veuillez réessayer.");
  }
});


// REGISTRATION FORM 
document.querySelector("form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    e.stopPropagation();
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
document.getElementById("contactForm")?.addEventListener("submit", async function (event) {
    event.preventDefault(); 
    event.stopPropagation();

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






