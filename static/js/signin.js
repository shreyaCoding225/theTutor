document.addEventListener("DOMContentLoaded", () => {
  const signinForm = document.getElementById("signinForm");

  if (signinForm) {
    signinForm.addEventListener("submit", async (e) => {
      e.preventDefault(); // 🛡️ Hard-stop native URL encoding transmission

      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      const payload = {
        email: email,
        password: password,
      };

      try {
        const response = await fetch("/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (data.status === "success" && data.user_id) {
          localStorage.setItem("session_user_id", String(data.user_id));

          if (localStorage.getItem("session_user_id")) {
            console.log("Session ID successfully locked. Redirecting now...");
            window.location.replace("/profile"); // Using replace prevents backward routing loops
          } else {
            console.error("LocalStorage write latency detected.");
          }
        } else {
          alert(data.message || "Invalid Email or Password!");
        }
        // if (response.ok) {
        //     localStorage.setItem('user_id', data.user_id);
        //     window.location.href = '/profile';
        // } else {
        //     alert(data.detail || 'Login failed.');
        // }
      } catch (error) {
        console.error("Network Error:", error);
      }
    });
  }
});
