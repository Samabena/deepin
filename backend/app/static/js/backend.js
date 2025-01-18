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
    
    const response = await fetch("http://127.0.0.1:8000/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    
    if (response.ok) {
      alert("Inscription réussie !");
    } else {
      const error = await response.json();
      alert(`Erreur: ${error.detail}`);
    }
  });
  