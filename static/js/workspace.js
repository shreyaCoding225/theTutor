document.addEventListener("DOMContentLoaded", async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const moduleName = urlParams.get("module") || "CSS Grid Layouts";

  document.getElementById("workspace-module-title").textContent = moduleName;

  let steps = [];
  let currentStep = 0;

  // Dom Elements
  const stepTitle = document.getElementById("step-title");
  const instructionText = document.getElementById("instruction-text");
  const taskBox = document.getElementById("workspace-task-box");
  const taskText = document.getElementById("task-text");
  const backBtn = document.getElementById("workspace-back-btn");
  const actionBtn = document.getElementById("workspace-action-btn");
  const playground = document.getElementById("playground-panel");
  const codeInput = document.getElementById("code-input");

  //  1. Fetch data dynamically from our database API
  try {
    const response = await fetch(
      `/api/module-steps?module=${encodeURIComponent(moduleName)}`,
    );
    if (!response.ok)
      throw new Error("Failed to load backend syllabus timeline.");
    steps = await response.json();

    // Render dots dynamically depending on data row array length
    const dotsContainer = document.querySelector(".step-dots");
    dotsContainer.innerHTML = steps
      .map(
        (_, idx) =>
          `<div class="dot ${idx === 0 ? "active" : ""}" id="dot-${idx + 1}"></div>`,
      )
      .join("");

    // Initial core step render trigger
    renderStep();
  } catch (err) {
    console.error("Database connection failure:", err);
    instructionText.textContent = "Error loading curriculum structure.";
    return;
  }

  function renderStep() {
    if (steps.length === 0) return;
    const step = steps[currentStep];

    // Update Progress Indicators
    document.querySelectorAll(".dot").forEach((dot, idx) => {
      dot.classList.toggle("active", idx === currentStep);
    });

    stepTitle.textContent = step.title;
    instructionText.textContent = step.instruction;
    backBtn.style.display = currentStep > 0 ? "block" : "none";

    if (step.show_sandbox) {
      taskBox.style.display = "block";
      taskText.textContent = `🛠️ Target Goal: ${step.task}`;
      playground.style.display = "flex";
      if (!codeInput.value) codeInput.value = step.initial_code;
      actionBtn.textContent = "Verify Solution";
    } else {
      taskBox.style.display = "none";
      playground.style.display = "none";
      actionBtn.textContent = "Continue";
    }
  }

  actionBtn.addEventListener("click", async () => {
  const step = steps[currentStep];

  if (step.show_sandbox) {
    if (codeInput.value.includes(step.verify_keyword)) {
      alert("Fantastic work! Verification passes. You've completed this lab module!");

      // 1. Get module name and course ID from URL parameters
      const currentCourseId = urlParams.get("course_id");
      const currentModuleName = urlParams.get("module"); // e.g. "CSS Grid Layouts"

      // 2. Save progress to curriculum.db!
      if (currentModuleName) {
        await markModuleAsComplete(currentModuleName, currentStep, currentCourseId);
      }

      // 3. Dynamic Return Route (redirects AFTER DB update completes)
    //   if (currentCourseId) {
    //     window.location.href = `/course?id=${currentCourseId}`;
    //   } else {
    //     window.location.href = "javascript:history.back()";
    //   }

    } else {
      alert("Style rules are incomplete. Ensure your rule utilizes the specified parameters.");
    }
  } else {
    currentStep++;
    renderStep();
  }
});

  backBtn.addEventListener("click", () => {
    if (currentStep > 0) {
      currentStep--;
      renderStep();
    }
  });
});

async function markModuleAsComplete(moduleId, currentStep, courseId) {
  const currentUserId = localStorage.getItem("session_user_id");

  if (!currentUserId) {
    console.error("No active user session found.");
    return;
  }

  // 🔑 1. DEBUG LOG: See what moduleId is actually being sent!
  console.log("Sending payload with moduleId:", moduleId);

  const payload = {
    user_id: parseInt(currentUserId),
    module_id: String(moduleId), // Ensure string format
    step_index: currentStep,
    status: "completed",
  };

  try {
    // 🔑 2. AWAIT: Wait for the DB to complete writing before moving on!
    const response = await fetch("/api/complete-module", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("Failed to update progression status");
    }

    const data = await response.json();
    console.log("Progress tracked successfully:", data);

    // 🔑 3. REDIRECT HERE: Only navigate AFTER the backend confirms 200 OK
    if (courseId) {
      window.location.href = `/course?id=${courseId}`;
    }

  } catch (error) {
    console.error("Error tracking progress:", error);
  }
}