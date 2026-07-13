document.addEventListener("DOMContentLoaded", () => {
    const urlParams = new URLSearchParams(window.location.search);
    const authSession = urlParams.get('auth_session');

    if (authSession) {
        // Drop the session ID into the local storage locker!
        localStorage.setItem("session_user_id", authSession);
        
        // Clean up the URL instantly so the user doesn't see "?auth_session=..." in the browser address bar
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    // Your existing auth checking loop continues right down here...
    const userId = localStorage.getItem("session_user_id");
    
    fetchUserProfile();
});

async function fetchUserProfile() {
    const userId = localStorage.getItem("session_user_id");
    
    // if (!userId) {
    //     window.location.href = "/sign-in";
    //     return;
    // }
    // console.log("Debug - Raw LocalStorage Value:", userId);

    if (!userId || userId === "null") {
        document.getElementById("name").textContent = "Authentication Error";
        document.getElementById("email").textContent = "Reason: session_user_id is missing or null in LocalStorage.";
        return; 
    }

    try {
        const response = await fetch(`/api/user/me?user_id=${userId}`);
        
        if (!response.ok) throw new Error("Profile fetch failed");
        
        const userData = await response.json();
        
        document.getElementById("name").textContent = userData.name;
        document.getElementById("email").textContent = userData.email;
        
    } catch (error) {
        console.error("Error loading profile:", error);
    }
}



// Logout Button 


document.addEventListener("DOMContentLoaded", () => {
    const userId = localStorage.getItem("session_user_id");
    const overlay = document.querySelector(".logout-blur");

    //  CASE A: User is NOT logged in (Activate the blur gate)
    if (!userId || userId === "null") {
        if (overlay) {
            overlay.classList.add("active");
            overlay.innerHTML = `
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 1rem; color: white; font-family: sans-serif;">
                    <p>Please sign in to view your dashboard.</p>
                    <a href="/sign-in" style="background: #59a3f8; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Go to Sign In</a>
                </div>
            `;
        }
        return; 
    }

    //  CASE B: User IS logged in (Keep overlay hidden, fetch data)
    if (overlay) {
        overlay.classList.remove("active"); // Enforce hiding the blur screen
    }
    fetchUserProfile(userId);
});

document.getElementById("logout").addEventListener("click", function() {
    localStorage.removeItem("session_user_id"); 

    const overlay = document.querySelector(".logout-blur");
    if (overlay) {
        // Clear old guest text and trigger the blur animation state instantly
        overlay.innerHTML = ""; 
        overlay.classList.add("active");
    }

    setTimeout(() => {
        window.location.replace("/profile"); // Reloads profile to trigger the logged-out auth gate
    }, 500);
});