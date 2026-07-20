document.addEventListener("DOMContentLoaded", () => {
    const coursesGrid = document.querySelector(".courses-grid");
    const searchInput = document.querySelector("#role-search");

    // Function A: Fetch and render courses from backend
    async function loadCourses(url = "/api/courses") {
        try {
            coursesGrid.innerHTML = '<div class="loading-placeholder">Loading catalog items...</div>';
            
            const response = await fetch(url);
            if (!response.ok) throw new Error("Failed to fetch catalog metrics.");
            
            const courses = await response.json();
            
            // Handle completely empty results gracefully
            if (courses.length === 0) {
                coursesGrid.innerHTML = '<div class="loading-placeholder">No courses found matching that role query.</div>';
                return;
            }

            // Map and inject course card layout strings into the grid array view
            coursesGrid.innerHTML = courses.map(course => `
                <div class="course-card">
                    <div>
                        <span class="course-badge">${course.difficulty || 'All Levels'}</span>
                        <h3>${course.title}</h3>
                        <p>${course.description}</p>
                    </div>
                    <a href="/course?id=${course.id}" class="view-btn">View Details</a>
                </div>
            `).join('');

        } catch (error) {
            console.error("Explore Fetch Error:", error);
            coursesGrid.innerHTML = '<div class="loading-placeholder" style="color: red;">Error loading catalog content.</div>';
        }
    }

    // Function B: Handle input search bar event actions
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const query = e.target.value.trim();
            
            if (query.length > 0) {
                // Hits the search role endpoint sequence loop
                loadCourses(`/api/search-role?role_name=${encodeURIComponent(query)}`);
            } else {
                // Wipes query parameter and reloads the absolute /static/css/style.css grid array list
                loadCourses();
            }
        });
    }

    // 🚀 Execution Entry Point: Fire off the initial page load loop tracking values
    loadCourses();
});