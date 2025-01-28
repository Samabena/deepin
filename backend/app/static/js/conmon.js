export function showPopupAlert(message) {
    const popupAlert = document.getElementById("popupAlert");
    const popupAlertMessage = document.getElementById("popupAlertMessage");

    popupAlertMessage.textContent = message;
    popupAlert.classList.remove("d-none");

    setTimeout(() => {
        popupAlert.classList.add("d-none");
    }, 3000);
}


export function showAlert(message, type, targetSelector) {
    const alertContainer = document.querySelector(targetSelector);
    if (alertContainer) {
        const alertElement = document.createElement("div");
        alertElement.className = `alert alert-${type} alert-dismissible fade show`;
        alertElement.role = "alert";
        alertElement.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        alertContainer.appendChild(alertElement);

        setTimeout(() => {
            alertElement.remove();
        }, 5000);
    }
}