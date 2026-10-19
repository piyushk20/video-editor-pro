// Video Editor Pro Studio - Interactive Client Controller

let currentProject = "stop_chasing_money";
let currentMode = "file"; // "file" or "url"
let selectedFile = null;
let activeJobId = null;
let pollTimer = null;
let elapsedTimer = null;
let startTime = 0;

document.addEventListener("DOMContentLoaded", () => {
  initModeTabs();
  initDropzone();
  initViewTabs();
  initExplorerButtons();
  initLaunchButton();
  loadProjectsList();
});

// Mode Toggling
function initModeTabs() {
  const tabFile = document.getElementById("tab-file-mode");
  const tabUrl = document.getElementById("tab-url-mode");
  const secFile = document.getElementById("section-file-upload");
  const secUrl = document.getElementById("section-url-input");
  const sourceBadge = document.getElementById("source-badge");

  tabFile.addEventListener("click", () => {
    tabFile.classList.add("active");
    tabUrl.classList.remove("active");
    secFile.style.display = "block";
    secUrl.style.display = "none";
    currentMode = "file";
    sourceBadge.textContent = "Local File Mode";
  });

  tabUrl.addEventListener("click", () => {
    tabUrl.classList.add("active");
    tabFile.classList.remove("active");
    secFile.style.display = "none";
    secUrl.style.display = "block";
    currentMode = "url";
    sourceBadge.textContent = "Web / URL Mode";
  });
}

// Drag & Drop File Handling
function initDropzone() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  const filenameElem = document.getElementById("drop-filename");
  const subtextElem = document.getElementById("drop-subtext");
  const previewCard = document.getElementById("file-preview-card");
  const previewName = document.getElementById("preview-filename");
  const previewSize = document.getElementById("preview-filesize");
  const projectInput = document.getElementById("project-name");

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  function handleFileSelected(file) {
    selectedFile = file;
    filenameElem.textContent = file.name;
    subtextElem.textContent = "File selected and ready to process";

    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    previewName.textContent = file.name;
    previewSize.textContent = `${sizeMB} MB`;
    previewCard.style.display = "block";

    // Auto-generate project slug from file name
    const slug = file.name.replace(/\.[^/.]+$/, "").replace(/[^a-zA-Z0-9_-]/g, "_").toLowerCase().slice(0, 30);
    if (!projectInput.value) {
      projectInput.value = slug;
    }
  }
}

// View Tabs (9:16 vs 16:9 vs Shorts)
function initViewTabs() {
  const tab9x16 = document.getElementById("tab-view-9x16");
  const tab16x9 = document.getElementById("tab-view-16x9");
  const tabShorts = document.getElementById("tab-view-shorts");

  const view9x16 = document.getElementById("view-container-9x16");
  const view16x9 = document.getElementById("view-container-16x9");
  const viewShorts = document.getElementById("view-container-shorts");

  tab9x16.addEventListener("click", () => {
    tab9x16.classList.add("active");
    tab16x9.classList.remove("active");
    tabShorts.classList.remove("active");
    view9x16.style.display = "flex";
    view16x9.style.display = "none";
    viewShorts.style.display = "none";
  });

  tab16x9.addEventListener("click", () => {
    tab16x9.classList.add("active");
    tab9x16.classList.remove("active");
    tabShorts.classList.remove("active");
    view9x16.style.display = "none";
    view16x9.style.display = "block";
    viewShorts.style.display = "none";
  });

  tabShorts.addEventListener("click", () => {
    tabShorts.classList.add("active");
    tab9x16.classList.remove("active");
    tab16x9.classList.remove("active");
    view9x16.style.display = "none";
    view16x9.style.display = "none";
    viewShorts.style.display = "block";
  });
}

// Explorer Buttons
function initExplorerButtons() {
  const btnHeader = document.getElementById("btn-header-explorer");
  const btnOutput = document.getElementById("btn-open-explorer");

  const triggerExplorer = () => {
    fetch(`/api/open-explorer?project=${encodeURIComponent(currentProject)}`, { method: "POST" })
      .then(r => r.json())
      .then(d => {
        logTerminal(`[Explorer] Opened output folder: ${d.path || currentProject}`);
      })
      .catch(err => logTerminal(`[Explorer Error] ${err}`));
  };

  btnHeader.addEventListener("click", triggerExplorer);
  btnOutput.addEventListener("click", triggerExplorer);
}

// Pipeline Launch Handler
function initLaunchButton() {
  const btnLaunch = document.getElementById("btn-launch-pipeline");
  const projectInput = document.getElementById("project-name");
  const urlInput = document.getElementById("input-url");

  btnLaunch.addEventListener("click", async () => {
    const projectName = projectInput.value.trim() || `project_${Date.now()}`;
    currentProject = projectName;

    btnLaunch.disabled = true;
    btnLaunch.innerHTML = "<span>⏳ Processing In Pipeline...</span>";

    startElapsedTimer();
    resetStepper();
    logTerminal(`\n=== Launching AI Production Pipeline for '${projectName}' ===`);

    try {
      let resp;
      if (currentMode === "file") {
        if (!selectedFile) {
          alert("Please select a video file or enter a media URL first.");
          btnLaunch.disabled = false;
          btnLaunch.innerHTML = "<span>🚀 Initiate AI Production Pipeline</span>";
          return;
        }
        logTerminal(`[Upload] Uploading source footage (${(selectedFile.size/(1024*1024)).toFixed(1)} MB)...`);
        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("project_name", projectName);
        resp = await fetch("/api/upload", { method: "POST", body: formData });
      } else {
        const url = urlInput.value.trim();
        if (!url) {
          alert("Please enter a media URL.");
          btnLaunch.disabled = false;
          btnLaunch.innerHTML = "<span>🚀 Initiate AI Production Pipeline</span>";
          return;
        }
        logTerminal(`[Ingest] Fetching media stream from: ${url}...`);
        resp = await fetch("/api/process-url", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url, project_name: projectName })
        });
      }

      const data = await resp.json();
      if (!resp.ok || data.error) {
        throw new Error(data.error || "Failed to start processing job.");
      }

      activeJobId = data.job_id;
      logTerminal(`[Job Created] ID: ${activeJobId}. Streaming pipeline steps...`);
      startJobPolling(activeJobId);

    } catch (err) {
      logTerminal(`[Error] ${err.message}`);
      btnLaunch.disabled = false;
      btnLaunch.innerHTML = "<span>🚀 Initiate AI Production Pipeline</span>";
      stopElapsedTimer();
    }
  });
}

// Job Progress Polling & Live Updates
function startJobPolling(jobId) {
  if (pollTimer) clearInterval(pollTimer);

  pollTimer = setInterval(async () => {
    try {
      const res = await fetch(`/api/job/${jobId}`);
      if (!res.ok) return;
      const job = await res.json();

      updatePipelineUI(job);

      if (job.status === "completed") {
        clearInterval(pollTimer);
        stopElapsedTimer();
        onJobCompleted(job);
      } else if (job.status === "failed") {
        clearInterval(pollTimer);
        stopElapsedTimer();
        onJobFailed(job);
      }
    } catch (e) {
      console.warn("Poll error", e);
    }
  }, 1000);
}

function updatePipelineUI(job) {
  const progressBar = document.getElementById("progress-bar");
  const statusHeading = document.getElementById("pipeline-status-text");

  progressBar.style.width = `${job.progress || 0}%`;
  statusHeading.textContent = `Production Pipeline: ${job.current_activity || "Processing..."}`;

  // Update logs if new
  if (job.logs && job.logs.length > 0) {
    const terminal = document.getElementById("terminal-logs");
    terminal.innerHTML = job.logs.join("<br>");
    terminal.scrollTop = terminal.scrollHeight;
  }

  // Update Phase Steppers
  const currentPhase = job.phase !== undefined ? job.phase : 0;
  for (let i = 0; i <= 4; i++) {
    const el = document.getElementById(`step-${i}`);
    if (i < currentPhase) {
      el.className = "step-item completed";
    } else if (i === currentPhase && job.status === "running") {
      el.className = "step-item active";
    } else {
      el.className = "step-item";
    }
  }
}

function onJobCompleted(job) {
  logTerminal(`\n✨ [DONE] Production Pipeline Completed successfully! Deliverables ready.`);
  const btnLaunch = document.getElementById("btn-launch-pipeline");
  btnLaunch.disabled = false;
  btnLaunch.innerHTML = "<span>🚀 Initiate AI Production Pipeline</span>";

  for (let i = 0; i <= 4; i++) {
    document.getElementById(`step-${i}`).className = "step-item completed";
  }

  loadProjectsList();
  loadProject(currentProject);
}

function onJobFailed(job) {
  logTerminal(`\n❌ [FAILED] Pipeline stopped due to an error: ${job.error || "Unknown"}`);
  const btnLaunch = document.getElementById("btn-launch-pipeline");
  btnLaunch.disabled = false;
  btnLaunch.innerHTML = "<span>🚀 Initiate AI Production Pipeline</span>";
}

// Load Past Projects List
async function loadProjectsList() {
  try {
    const res = await fetch("/api/projects");
    const projects = await res.json();
    const container = document.getElementById("past-projects-list");
    container.innerHTML = "";

    if (!projects || projects.length === 0) {
      container.innerHTML = `<span class="chip">No projects in output folder yet</span>`;
      return;
    }

    projects.forEach(proj => {
      const chip = document.createElement("span");
      chip.className = `chip ${proj.name === currentProject ? "active" : ""}`;
      chip.textContent = `🎬 ${proj.name.replace(/_/g, " ")}`;
      chip.addEventListener("click", () => {
        document.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
        chip.classList.add("active");
        currentProject = proj.name;
        document.getElementById("project-name").value = proj.name;
        loadProject(proj.name);
      });
      container.appendChild(chip);
    });

    // Auto load current or first project
    if (projects.some(p => p.name === currentProject)) {
      loadProject(currentProject);
    } else if (projects.length > 0) {
      currentProject = projects[0].name;
      loadProject(currentProject);
    }
  } catch (e) {
    console.error("Failed to load projects", e);
  }
}

// Load Specific Project Deliverables
async function loadProject(projectName) {
  try {
    const res = await fetch(`/api/project/${projectName}`);
    if (!res.ok) return;
    const data = await res.json();

    // 1. Set 9:16 Video Player
    const player9x16 = document.getElementById("player-9x16");
    const src9x16 = document.getElementById("player-9x16-src");
    if (data.video_9x16) {
      src9x16.src = `/output/${projectName}/${data.video_9x16}?t=${Date.now()}`;
      player9x16.load();
      document.getElementById("del-link-9x16").href = src9x16.src;
      document.getElementById("del-size-9x16").textContent = `${data.video_9x16_size_mb || "1080×1920"} MB`;
    }

    // 2. Set 16:9 Companion Player
    const player16x9 = document.getElementById("player-16x9");
    const src16x9 = document.getElementById("player-16x9-src");
    if (data.video_16x9) {
      src16x9.src = `/output/${projectName}/${data.video_16x9}?t=${Date.now()}`;
      player16x9.load();
      document.getElementById("del-link-16x9").href = src16x9.src;
      document.getElementById("del-size-16x9").textContent = `${data.video_16x9_size_mb || "1920×1080"} MB`;
    }

    // 3. Populate Shorts Gallery
    const shortsGallery = document.getElementById("shorts-gallery");
    const shortsCount = document.getElementById("shorts-count");
    shortsGallery.innerHTML = "";
    shortsCount.textContent = (data.shorts || []).length;

    if (data.shorts && data.shorts.length > 0) {
      data.shorts.forEach(s => {
        const card = document.createElement("div");
        card.className = "short-card";
        const videoUrl = `/output/${projectName}/shorts/${s.filename}`;
        card.innerHTML = `
          <video src="${videoUrl}" muted loop preload="metadata" onmouseover="this.play()" onmouseout="this.pause()"></video>
          <div class="short-title">${s.name.replace(/_/g, " ").replace(/\.mp4/i, "")}</div>
        `;
        card.addEventListener("click", () => {
          src9x16.src = videoUrl;
          player9x16.load();
          player9x16.play();
          document.getElementById("tab-view-9x16").click();
        });
        shortsGallery.appendChild(card);
      });
    } else {
      shortsGallery.innerHTML = `<p style="font-size: 12px; color: var(--text-dim); padding: 12px;">No standalone shorts generated for this project.</p>`;
    }

    // 4. Update Deliverables Links
    if (data.srt_file) {
      document.getElementById("del-link-srt").href = `/output/${projectName}/${data.srt_file}`;
    }
    if (data.plan_file) {
      document.getElementById("del-link-plan").href = `/output/${projectName}/${data.plan_file}`;
    }
    if (data.report_file) {
      document.getElementById("del-link-report").href = `/output/${projectName}/${data.report_file}`;
    }
    if (data.score) {
      document.getElementById("del-score-text").textContent = `Quality Score: ${data.score}/10`;
    }

    logTerminal(`[Loaded Deliverables] Project '${projectName}' loaded into studio.`);

  } catch (e) {
    console.error("Error loading project", e);
  }
}

// Helpers
function resetStepper() {
  for (let i = 0; i <= 4; i++) {
    document.getElementById(`step-${i}`).className = "step-item";
  }
  document.getElementById("progress-bar").style.width = "0%";
}

function startElapsedTimer() {
  startTime = Date.now();
  const el = document.getElementById("elapsed-time");
  if (elapsedTimer) clearInterval(elapsedTimer);
  elapsedTimer = setInterval(() => {
    const diff = Math.floor((Date.now() - startTime) / 1000);
    const m = String(Math.floor(diff / 60)).padStart(2, '0');
    const s = String(diff % 60).padStart(2, '0');
    el.textContent = `${m}:${s}`;
  }, 1000);
}

function stopElapsedTimer() {
  if (elapsedTimer) clearInterval(elapsedTimer);
}

function logTerminal(msg) {
  const t = document.getElementById("terminal-logs");
  const time = new Date().toLocaleTimeString();
  t.innerHTML += `<div><span style="color:var(--text-dim)">[${time}]</span> ${msg}</div>`;
  t.scrollTop = t.scrollHeight;
}
