document.addEventListener("DOMContentLoaded", () => {
  const hamburger = document.getElementById("hamburger");
  const navMenu = document.querySelector(".nav-menu");

  hamburger.addEventListener("click", () => {
    navMenu.classList.toggle("show");

    if (navMenu.classList.contains("show")) {
      hamburger.classList.remove("fa-bars");
      hamburger.classList.add("fa-xmark");
    } else {
      hamburger.classList.remove("fa-xmark");
      hamburger.classList.add("fa-bars");
    }
  });

  // Listen for the user resizing their browser window
  window.addEventListener("resize", () => {
    // If the window grows past 700px, clean up the mobile states
    if (window.innerWidth > 700) {
      navMenu.classList.remove("show");

      // Reset the icon back to the standard hamburger bars
      hamburger.classList.remove("fa-xmark");
      hamburger.classList.add("fa-bars");
    }
  });
});
