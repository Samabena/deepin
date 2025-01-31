
  // Check if the target date already exists in localStorage
  let targetDate = localStorage.getItem("countdownTargetDate");

  if (!targetDate) {
    // If no target date is set, create a new one (24 hours from now)
    targetDate = new Date();
    targetDate.setHours(targetDate.getHours() + 24);
    localStorage.setItem("countdownTargetDate", targetDate);
  } else {
    // Convert the stored date string back into a Date object
    targetDate = new Date(targetDate);
  }

  // Update the countdown every second
  const countdown = setInterval(() => {
    const now = new Date();
    const timeLeft = targetDate - now;

    // Calculate days, hours, minutes, and seconds
    const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

    // Display the result in the respective elements
    document.getElementById("days").textContent = days.toString().padStart(2, "0");
    document.getElementById("hours").textContent = hours.toString().padStart(2, "0");
    document.getElementById("minutes").textContent = minutes.toString().padStart(2, "0");
    document.getElementById("seconds").textContent = seconds.toString().padStart(2, "0");

    // If the countdown is over, clear the timer and update the message
    if (timeLeft < 0) {
      clearInterval(countdown);
      document.getElementById("countdown").innerHTML = "<h3 class='text-danger'>Promotion terminée !</h3>";
      // Clear the target date from localStorage
      localStorage.removeItem("countdownTargetDate");
    }
  }, 1000);




  document.addEventListener("DOMContentLoaded", () => {
    const navLinks = document.querySelectorAll(".nav-link");

    const currentPath = window.location.pathname;
    navLinks.forEach((link) => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }
    });

    navLinks.forEach((link) => {
        link.addEventListener("click", (event) => {
            navLinks.forEach((link) => link.classList.remove("active"));
            event.currentTarget.classList.add("active");
        });
    });
});



window.fetchPosts = function (button) {
  let page = button.getAttribute("data-page"); // Get the page number
  fetch(`/blog?page=${page}`)
      .then(response => response.text())
      .then(html => {
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, "text/html");
          document.querySelector(".container").innerHTML = doc.querySelector(".container").innerHTML;
      })
      .catch(error => console.error("Error fetching posts:", error));
};




document.addEventListener("DOMContentLoaded", function() {
  // Get the current page URL
  const postUrl = encodeURIComponent(window.location.href);
  const postTitle = encodeURIComponent(document.title); // Use page title

  // Facebook Share Link
  document.getElementById("facebookShare").href = `https://www.facebook.com/sharer/sharer.php?u=${postUrl}`;

  // WhatsApp Share Link
  document.getElementById("whatsappShare").href = `https://api.whatsapp.com/send?text=${postTitle}%20${postUrl}`;

  // LinkedIn Share Link
  document.getElementById("linkedinShare").href = `https://www.linkedin.com/sharing/share-offsite/?url=${postUrl}`;
});