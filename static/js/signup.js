document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // 🛡️ Stop the browser from doing a traditional form reload

    // 1. Grab the raw text strings from your beautiful input lines
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirm_password = document.getElementById('confirm_password').value;

    // 2. Package the fields into a modern JSON block object
    const payload = {
        name: name,
        email: email,
        password: password,
        confirm_password: confirm_password
    };

    try {
        // 3. Shoot the data packet down the pipeline to your FastAPI endpoint
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload) // Convert the JS object to a JSON string
        });

        // 4. Handle the server's reply
        if (response.ok) {
            // Success! Send them straight to your login dashboard page
            window.location.href = '/profile';
        } else {
            // Extract the error message we wrote in FastAPI (like "Passwords do not match")
            const errorData = await response.json();
            alert(errorData.detail || 'Registration failed.');
        }
    } catch (error) {
        console.error('Network Error:', error);
        alert('Server is down or unreachable. Check your terminal!');
    }
});