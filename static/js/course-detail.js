document.addEventListener("DOMContentLoaded", async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const courseId = urlParams.get("id");

  if (!courseId) {
    window.location.href = "/explore";
    return;
  }

  const currentUserId = localStorage.getItem("session_user_id");
  const isValidUser =
    currentUserId && currentUserId !== "null" && currentUserId !== "undefined";

  try {
    const [courseResponse, progressResponse] = await Promise.all([
      fetch(`/api/course-details?id=${courseId}`),
      isValidUser
        ? fetch(`/api/user/completed-modules?user_id=${currentUserId}`)
        : Promise.resolve(null),
    ]);

    if (!courseResponse.ok) throw new Error("Course payload missing.");

    const data = await courseResponse.json();

    // Store normalized completed module titles
    let completedModules = new Set();
    if (progressResponse && progressResponse.ok) {
      const progressData = await progressResponse.json();

      console.log("DB Completed Modules Raw:", progressData.completed_modules);
      completedModules = new Set(
        progressData.completed_modules.map((id) =>
          String(id).toLowerCase().trim(),
        ),
      );
    }

    document.getElementById("detail-title").textContent = data.title;
    document.getElementById("detail-description").textContent =
      data.description;

    const badge = document.getElementById("detail-badge");
    badge.textContent = data.difficulty || "All Levels";

    const skillsList = document.getElementById("skills-list");
    if (data.skills.length === 0) {
      skillsList.innerHTML = `<p class="empty-notice">Detailed syllabus coming soon!</p>`;
    } else {
      skillsList.innerHTML = data.skills
  .map((skill) => {
    // Check skill.id or skill.module_id (whichever key holds the DB identifier)
    const skillIdentifier = String(skill.id || skill.module_id || skill.name).toLowerCase().trim();
    
    const isCompleted = completedModules.has(skillIdentifier);

    return `
      <a href="/workspace?course_id=${courseId}&module=${encodeURIComponent(skill.name)}" class="skill-node-link">
          <div class="skill-node-card">
              <h3>
                  ${skill.name}
                  ${isCompleted ? '<span class="completed-badge" style="color: #2ed573; margin-left: 10px; font-size: 0.9rem;">✔ Completed</span>' : ''}
              </h3>
              <p>${skill.description}</p>
          </div>
      </a>
    `;
  })
  .join("");
    }
  } catch (error) {
    console.error("Error rendering details view:", error);
  }
});
