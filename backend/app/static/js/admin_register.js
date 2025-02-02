import { showAlert} from './conmon.js';


document.addEventListener("DOMContentLoaded", function () {
    const sendButton = document.getElementById("send");
    const registrationForm = document.getElementById("registrationForm");

    // Other fields to validate
    const usernameField = document.getElementById("floatingUsername");
    const fullnameField = document.getElementById("floatingFullname");
    const emailField = document.getElementById("floatingInput");
    const passwordField = document.getElementById("floatingPassword");
    const confirmPasswordField = document.getElementById("floatingConfirmPassword");

sendButton.addEventListener("click", async function (event) {
    event.preventDefault(); // Prevent traditional form submission

    let isValid = true;

    // Username Validation
    const usernameRegex = /^[a-zA-Z][a-zA-Z0-9_]{2,14}$/;
    if (usernameField.value.trim() === "") {
        usernameField.classList.add("is-invalid");
        showAlert("Username cannot be empty!", "danger", "#alertContainer");
        isValid = false;
    } else if (!usernameRegex.test(usernameField.value)) {
        usernameField.classList.add("is-invalid");
        showAlert("Username must start with a letter, be between 3 to 15 characters, and contain only letters, numbers, and underscores.", "danger", "#alertContainer");
        isValid = false;
    } else {
        usernameField.classList.remove("is-invalid");
    }

    // Fullname Validation
    if (fullnameField.value.trim() === "") {
        fullnameField.classList.add("is-invalid");
        showAlert("Fullname cannot be empty!", "danger", "#alertContainer");
        isValid = false;
    } else {
        fullnameField.classList.remove("is-invalid");
    }

    // Email Validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (emailField.value.trim() === "" || !emailRegex.test(emailField.value)) {
        emailField.classList.add("is-invalid");
        showAlert("Please enter a valid email address!", "danger", "#alertContainer");
        isValid = false;
    } else {
        emailField.classList.remove("is-invalid");
    }

    // Password Validation
    const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&\-\+\.,_])[A-Za-z\d@$!%*?&\-\+\.,_]{8,}$/;
    if (!passwordRegex.test(passwordField.value)) {
        passwordField.classList.add("is-invalid");
        showAlert("Password must contain at least one uppercase letter, one number, and one special character.", "danger", "#alertContainer");
        isValid = false;
    } else {
        passwordField.classList.remove("is-invalid");
    }

    // Confirm Password Validation
    if (passwordField.value !== confirmPasswordField.value) {
        confirmPasswordField.classList.add("is-invalid");
        showAlert("Passwords do not match!", "danger", "#alertContainer");
        isValid = false;
    } else {
        confirmPasswordField.classList.remove("is-invalid");
    }

    if (!isValid) {
        registrationForm.classList.add("was-validated");
        return; // Do not proceed if form is invalid
    }

    // If valid, submit the form
    sendButton.disabled = true; // Prevent multiple submissions

    

    try {

        const form = document.getElementById("registrationForm");
        const formData = new FormData(form);
        const response = await fetch("/registration/", {
            method: "POST",
            body: formData  // 📩 Utiliser formData directement
        });
         // Replace with your backend call
        
         // Iterate over all key/value pairs and log them
        for (const [key, value] of formData.entries()) {
            console.log(`${key}: ${value}`);
        }
  
        console.log(response);

        showAlert("Registration successful!", "success", "#alertContainer");

        // Reset form fields and clear validation states
        registrationForm.reset();
        registrationForm.classList.remove("was-validated");
    } catch (error) {
        console.error("Registration error:", error);
        showAlert("Registration failed! Please try again.", "danger", "#alertContainer");
    } finally {
        sendButton.disabled = false; // Re-enable the button
    }
});

});




