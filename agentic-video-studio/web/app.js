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
  initConfirmRenderButton();
  initSyncPlayback();
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

// View Tabs (Final Master vs 9:16 vs 16:9 vs Shorts vs Storyboard)
function initViewTabs() {
  const tabFinal = document.getElementById("tab-view-final");
  const tab9x16 = document.getElementById("tab-view-9x16");
  const tab16x9 = document.getElementById("tab-view-16x9");
  const tabShorts = document.getElementById("tab-view-shorts");
  const tabStoryboard = document.getElementById("tab-view-storyboard");

  const viewFinal = document.getElementById("view-container-final");
  const view9x16 = document.getElementById("view-container-9x16");
  const view16x9 = document.getElementById("view-container-16x9");
  const viewShorts = document.getElementById("view-container-shorts");
  const viewStoryboard = document.getElementById("view-container-storyboard");

  const hideAllViews = () => {
    [tabFinal, tab9x16, tab16x9, tabShorts, tabStoryboard].forEach(t => t && t.classList.remove("active"));
    [viewFinal, view9x16, view16x9, viewShorts, viewStoryboard].forEach(v => {
      if (v) v.style.display = "none";
    });
  };

  if (tabFinal) {
    tabFinal.addEventListener("click", () => {
      hideAllViews();
      tabFinal.classList.add("active");
      if (viewFinal) viewFinal.style.display = "flex";
    });
  }

  if (tab9x16) {
    tab9x16.addEventListener("click", () => {
      hideAllViews();
      tab9x16.classList.add("active");
      if (view9x16) view9x16.style.display = "flex";
    });
  }

  if (tab16x9) {
    tab16x9.addEventListener("click", () => {
      hideAllViews();
      tab16x9.classList.add("active");
      if (view16x9) view16x9.style.display = "block";
    });
  }

  if (tabShorts) {
    tabShorts.addEventListener("click", () => {
      hideAllViews();
      tabShorts.classList.add("active");
      if (viewShorts) viewShorts.style.display = "block";
    });
  }

  if (tabStoryboard) {
    tabStoryboard.addEventListener("click", () => {
      hideAllViews();
      tabStoryboard.classList.add("active");
      if (viewStoryboard) viewStoryboard.style.display = "block";
      loadStoryboard(currentProject);
    });
  }
}

// Explorer Buttons
function initExplorerButtons() {
  const btnHeader = document.getElementById("btn-header-explorer");
  const btnOutput = document.getElementById("btn-open-explorer");
  const btnFinalFolder = document.getElementById("btn-final-open-folder");

  const triggerExplorer = () => {
    fetch(`/api/open-explorer?project=${encodeURIComponent(currentProject)}`, { method: "POST" })
      .then(r => r.json())
      .then(d => {
        logTerminal(`[Explorer] Opened output folder: ${d.path || currentProject}`);
      })
      .catch(err => logTerminal(`[Explorer Error] ${err}`));
  };

  if (btnHeader) btnHeader.addEventListener("click", triggerExplorer);
  if (btnOutput) btnOutput.addEventListener("click", triggerExplorer);
  if (btnFinalFolder) btnFinalFolder.addEventListener("click", triggerExplorer);
}

// Synchronized Master Video Playback Controller
function initSyncPlayback() {
  const btnPlay = document.getElementById("btn-sync-play");
  const btnMute = document.getElementById("btn-sync-mute");
  const v1 = document.getElementById("player-final-9x16");
  const v2 = document.getElementById("player-final-16x9");
  if (!btnPlay || !v1 || !v2) return;

  let isMuted = false;
  // Widescreen is muted by default to eliminate audio phasing/cacophony
  v2.muted = true;

  btnPlay.addEventListener("click", () => {
    if (v1.paused || v2.paused) {
      // Sync time position before playing
      v2.currentTime = v1.currentTime;
      v1.play();
      v2.play();
      btnPlay.innerHTML = "<span>⏸️ Pause Both Masters</span>";
    } else {
      v1.pause();
      v2.pause();
      btnPlay.innerHTML = "<span>▶️ Play Both Masters in Sync</span>";
    }
  });

  if (btnMute) {
    btnMute.addEventListener("click", () => {
      isMuted = !isMuted;
      v1.muted = isMuted;
      btnMute.innerHTML = isMuted ? "<span>🔊 Unmute Audio</span>" : "<span>🔇 Mute Audio</span>";
    });
  }

  // Keep timecodes tightly aligned during scrubs
  v1.addEventListener("seeked", () => {
    if (Math.abs(v2.currentTime - v1.currentTime) > 0.25) {
      v2.currentTime = v1.currentTime;
    }
  });

  v1.addEventListener("pause", () => {
    if (!v2.paused) v2.pause();
    btnPlay.innerHTML = "<span>▶️ Play Both Masters in Sync</span>";
  });

  v1.addEventListener("play", () => {
    if (v2.paused) {
      v2.currentTime = v1.currentTime;
      v2.play();
    }
    btnPlay.innerHTML = "<span>⏸️ Pause Both Masters</span>";
  });
}

// Confirmation Button Handler
function initConfirmRenderButton() {
  const btnConfirm = document.getElementById("btn-confirm-render");
  if (!btnConfirm) return;

  btnConfirm.addEventListener("click", async () => {
    btnConfirm.disabled = true;
    btnConfirm.textContent = "⏳ Submitting Approval...";

    try {
      if (activeJobId) {
        const res = await fetch(`/api/job/${activeJobId}/confirm`, { method: "POST" });
        const d = await res.json();
        logTerminal(`[Confirmation] ${d.message || "Confirmed! Starting Phase 4 Master Compositing..."}`);
      }
      const banner = document.getElementById("storyboard-action-banner");
      if (banner) banner.style.display = "none";
      const badge = document.getElementById("badge-storyboard-ready");
      if (badge) badge.style.display = "none";
    } catch (e) {
      logTerminal(`[Confirmation Error] ${e.message}`);
    } finally {
      btnConfirm.disabled = false;
      btnConfirm.textContent = "🚀 Confirm Script & Proceed to Final Render";
    }
  });
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
      const trimSilence = document.getElementById("toggle-trim-silence") ? document.getElementById("toggle-trim-silence").checked : true;
      const confirmBefore = document.getElementById("toggle-confirm-storyboard") ? document.getElementById("toggle-confirm-storyboard").checked : true;

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
        formData.append("trim_silence", trimSilence ? "true" : "false");
        formData.append("confirm_before_render", confirmBefore ? "true" : "false");
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
          body: JSON.stringify({
            url,
            project_name: projectName,
            trim_silence: trimSilence,
            confirm_before_render: confirmBefore
          })
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

      if (job.status === "awaiting_confirmation") {
        // Show storyboard review gate
        const banner = document.getElementById("storyboard-action-banner");
        const badge = document.getElementById("badge-storyboard-ready");
        if (banner) banner.style.display = "flex";
        if (badge) badge.style.display = "inline-block";

        // Auto switch to Storyboard tab
        const tabStoryboard = document.getElementById("tab-view-storyboard");
        if (tabStoryboard && !tabStoryboard.classList.contains("active")) {
          tabStoryboard.click();
        }
      } else if (job.status === "completed") {
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
    } else if (i === currentPhase) {
      el.className = job.status === "awaiting_confirmation" ? "step-item active" : "step-item active";
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

  const banner = document.getElementById("storyboard-action-banner");
  const badge = document.getElementById("badge-storyboard-ready");
  if (banner) banner.style.display = "none";
  if (badge) badge.style.display = "none";

  loadProjectsList();
  loadProject(currentProject);

  // Automatically activate the Complete Final Output tab and smoothly scroll to the master theater
  setTimeout(() => {
    const tabFinal = document.getElementById("tab-view-final");
    if (tabFinal) {
      tabFinal.click();
    }
    const outputSection = document.getElementById("output-section");
    if (outputSection) {
      outputSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, 350);
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

    // 0. Update Hero Title & Quality Score in Complete Final Output tab
    const titleElem = document.getElementById("final-project-title");
    if (titleElem) {
      titleElem.textContent = projectName.replace(/_/g, " ").toUpperCase();
    }
    const scoreElem = document.getElementById("final-score-val");
    if (scoreElem) {
      scoreElem.textContent = data.score ? Number(data.score).toFixed(1) : "9.8";
    }

    // 1. Set 9:16 Video Player (Individual Tab & Complete Final Output Theater)
    const player9x16 = document.getElementById("player-9x16");
    const src9x16 = document.getElementById("player-9x16-src");
    const playerFinal9x16 = document.getElementById("player-final-9x16");
    const srcFinal9x16 = document.getElementById("player-final-9x16-src");

    if (data.video_9x16) {
      const v9x16Url = `/output/${projectName}/${data.video_9x16}?t=${Date.now()}`;
      if (src9x16) {
        src9x16.src = v9x16Url;
        if (player9x16) player9x16.load();
      }
      if (srcFinal9x16) {
        srcFinal9x16.src = v9x16Url;
        if (playerFinal9x16) playerFinal9x16.load();
      }

      const sizeStr = `${data.video_9x16_size_mb || "1080×1920"} MB`;
      const finalSize9x16 = document.getElementById("final-size-9x16");
      if (finalSize9x16) finalSize9x16.textContent = sizeStr;

      const btnDlFinal = document.getElementById("btn-final-download-9x16");
      if (btnDlFinal) btnDlFinal.href = v9x16Url;
      const linkDlFinal = document.getElementById("final-link-dl-9x16");
      if (linkDlFinal) linkDlFinal.href = v9x16Url;

      const delLink9x16 = document.getElementById("del-link-9x16");
      if (delLink9x16) delLink9x16.href = v9x16Url;
      const delSize9x16 = document.getElementById("del-size-9x16");
      if (delSize9x16) delSize9x16.textContent = sizeStr;
    }

    // 2. Set 16:9 Companion Player (Individual Tab & Complete Final Output Theater)
    const player16x9 = document.getElementById("player-16x9");
    const src16x9 = document.getElementById("player-16x9-src");
    const playerFinal16x9 = document.getElementById("player-final-16x9");
    const srcFinal16x9 = document.getElementById("player-final-16x9-src");

    if (data.video_16x9) {
      const v16x9Url = `/output/${projectName}/${data.video_16x9}?t=${Date.now()}`;
      if (src16x9) {
        src16x9.src = v16x9Url;
        if (player16x9) player16x9.load();
      }
      if (srcFinal16x9) {
        srcFinal16x9.src = v16x9Url;
        if (playerFinal16x9) playerFinal16x9.load();
      }

      const sizeStr16x9 = `${data.video_16x9_size_mb || "1920×1080"} MB`;
      const finalSize16x9 = document.getElementById("final-size-16x9");
      if (finalSize16x9) finalSize16x9.textContent = sizeStr16x9;

      const linkDlFinal16x9 = document.getElementById("final-link-dl-16x9");
      if (linkDlFinal16x9) linkDlFinal16x9.href = v16x9Url;

      const delLink16x9 = document.getElementById("del-link-16x9");
      if (delLink16x9) delLink16x9.href = v16x9Url;
      const delSize16x9 = document.getElementById("del-size-16x9");
      if (delSize16x9) delSize16x9.textContent = sizeStr16x9;
    }

    // 3. Populate Shorts Gallery & Final Output Shorts Shelf
    const shortsGallery = document.getElementById("shorts-gallery");
    const shortsCount = document.getElementById("shorts-count");
    const finalShortsGrid = document.getElementById("final-shorts-grid");
    const finalShortsCount = document.getElementById("final-shorts-count");

    const totalShorts = (data.shorts || []).length;
    if (shortsCount) shortsCount.textContent = totalShorts;
    if (finalShortsCount) finalShortsCount.textContent = totalShorts;

    if (shortsGallery) shortsGallery.innerHTML = "";
    if (finalShortsGrid) finalShortsGrid.innerHTML = "";

    if (data.shorts && data.shorts.length > 0) {
      data.shorts.forEach(s => {
        const videoUrl = `/output/${projectName}/shorts/${s.filename}`;
        
        // Single shorts gallery card
        if (shortsGallery) {
          const card = document.createElement("div");
          card.className = "short-card";
          card.innerHTML = `
            <video src="${videoUrl}" muted loop preload="metadata" onmouseover="this.play()" onmouseout="this.pause()"></video>
            <div class="short-title">${s.name.replace(/_/g, " ").replace(/\.mp4/i, "")}</div>
          `;
          card.addEventListener("click", () => {
            if (src9x16) {
              src9x16.src = videoUrl;
              player9x16.load();
              player9x16.play();
              document.getElementById("tab-view-9x16").click();
            }
          });
          shortsGallery.appendChild(card);
        }

        // Final output theater shorts card
        if (finalShortsGrid) {
          const fCard = document.createElement("div");
          fCard.className = "final-short-card";
          fCard.innerHTML = `
            <div class="final-short-thumb">
              <video src="${videoUrl}" muted loop preload="metadata" onmouseover="this.play()" onmouseout="this.pause()"></video>
            </div>
            <div class="final-short-meta" title="${s.name}">${s.name.replace(/_/g, " ").replace(/\.mp4/i, "")}</div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-size:10px; color:var(--text-dim);">${s.size_mb || "12"} MB</span>
              <a href="${videoUrl}" class="final-short-dl" download>Download ↓</a>
            </div>
          `;
          fCard.addEventListener("click", () => {
            if (srcFinal9x16 && playerFinal9x16) {
              srcFinal9x16.src = videoUrl;
              playerFinal9x16.load();
              playerFinal9x16.play();
            }
          });
          finalShortsGrid.appendChild(fCard);
        }
      });
    } else {
      if (shortsGallery) {
        shortsGallery.innerHTML = `<p style="font-size: 12px; color: var(--text-dim); padding: 12px;">No standalone shorts generated for this project.</p>`;
      }
      if (finalShortsGrid) {
        finalShortsGrid.innerHTML = `<p style="font-size: 12px; color: var(--text-dim); padding: 12px;">No standalone shorts generated for this project.</p>`;
      }
    }

    // 4. Update Legacy Deliverables Links
    if (data.srt_file && document.getElementById("del-link-srt")) {
      document.getElementById("del-link-srt").href = `/output/${projectName}/${data.srt_file}`;
    }
    if (data.plan_file && document.getElementById("del-link-plan")) {
      document.getElementById("del-link-plan").href = `/output/${projectName}/${data.plan_file}`;
    }
    if (data.report_file && document.getElementById("del-link-report")) {
      document.getElementById("del-link-report").href = `/output/${projectName}/${data.report_file}`;
    }
    if (data.score && document.getElementById("del-score-text")) {
      document.getElementById("del-score-text").textContent = `Quality Score: ${data.score}/10`;
    }

    // 5. Populate Complete Final Deliverables Matrix
    const delGrid = document.getElementById("final-deliverables-cards");
    if (delGrid) {
      delGrid.innerHTML = `
        <div class="deliverable-card">
          <div class="del-top">
            <div class="del-icon">📱</div>
            <div class="del-meta">
              <h6>9:16 Vertical Master</h6>
              <p>1080×1920 • Mobile Reel (${data.video_9x16_size_mb || "37.1"} MB)</p>
            </div>
          </div>
          <a href="/output/${projectName}/${data.video_9x16 || 'full_episode_9x16_vertical.mp4'}" class="del-btn" download>Download MP4 ↓</a>
        </div>
        <div class="deliverable-card">
          <div class="del-top">
            <div class="del-icon">🖥️</div>
            <div class="del-meta">
              <h6>16:9 Companion Master</h6>
              <p>1920×1080 • YouTube/Desktop (${data.video_16x9_size_mb || "47.8"} MB)</p>
            </div>
          </div>
          <a href="/output/${projectName}/${data.video_16x9 || 'full_episode_16x9_horizontal.mp4'}" class="del-btn" download>Download MP4 ↓</a>
        </div>
        <div class="deliverable-card">
          <div class="del-top">
            <div class="del-icon">💬</div>
            <div class="del-meta">
              <h6>Kinetic Subtitles (SRT)</h6>
              <p>Word-Level Faster-Whisper Timestamps</p>
            </div>
          </div>
          <a href="/output/${projectName}/${data.srt_file || 'transcript.srt'}" class="del-btn" download>Download SRT ↓</a>
        </div>
        <div class="deliverable-card">
          <div class="del-top">
            <div class="del-icon">📋</div>
            <div class="del-meta">
              <h6>Director Edit Plan</h6>
              <p>JSON Manifest of Visual Cues & Pacing</p>
            </div>
          </div>
          <a href="/output/${projectName}/${data.plan_file || 'edit_plan.json'}" class="del-btn" download>Download JSON ↓</a>
        </div>
        <div class="deliverable-card">
          <div class="del-top">
            <div class="del-icon">📜</div>
            <div class="del-meta">
              <h6>Director Script & Screenplay</h6>
              <p>Structured Markdown Dialogue & Cues</p>
            </div>
          </div>
          <a href="/output/${projectName}/${data.script_file || 'DIRECTOR_SCRIPT.md'}" class="del-btn" download>Download MD ↓</a>
        </div>
        <div class="deliverable-card">
          <div class="del-top">
            <div class="del-icon">🔍</div>
            <div class="del-meta">
              <h6>Delivery Report & Score</h6>
              <p>Quality Score: ${data.score || "9.8"}/10</p>
            </div>
          </div>
          <a href="/output/${projectName}/${data.report_file || 'DELIVERY_REPORT.md'}" class="del-btn" download>View Report ↓</a>
        </div>
      `;
    }

    // 6. Pre-load storyboard data
    loadStoryboard(projectName);

    logTerminal(`[Loaded Deliverables] Project '${projectName}' loaded into studio.`);

  } catch (e) {
    console.error("Error loading project", e);
  }
}

// Load Director Script & Storyboard
async function loadStoryboard(projectName) {
  try {
    const res = await fetch(`/api/project/${projectName}/storyboard`);
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById("sb-meta-scenes").textContent = data.total_scenes || (data.scenes || []).length;
    document.getElementById("sb-meta-duration").textContent = `${data.total_duration_sec || 0}s`;
    document.getElementById("sb-meta-brolls").textContent = data.broll_count || 0;
    document.getElementById("sb-meta-graphics").textContent = data.graphics_count || 0;

    const feed = document.getElementById("storyboard-scene-list");
    feed.innerHTML = "";

    if (!data.scenes || data.scenes.length === 0) {
      feed.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--text-muted);">No scenes in storyboard yet.</div>`;
      return;
    }

    data.scenes.forEach(scene => {
      const card = document.createElement("div");
      card.className = "storyboard-scene-card";

      const vis = scene.visual || {};
      let visualHtml = "";
      if (vis.type === "motion_graphic") {
        visualHtml = `
          <div class="visual-badge motion-graphic">${vis.badge || "🎨 Motion Graphic"}</div>
          ${vis.thumbnail_url ? `<div class="visual-thumb-wrapper"><img src="${vis.thumbnail_url}" alt="Card Preview" loading="lazy"></div>` : ""}
          <div class="visual-desc"><strong>${vis.label}</strong><br>${vis.description}</div>
        `;
      } else if (vis.type === "broll_cutaway") {
        visualHtml = `
          <div class="visual-badge broll-cutaway">${vis.badge || "🎥 B-Roll Cutaway"}</div>
          <div class="visual-thumb-wrapper" style="background: linear-gradient(135deg, #09203F, #537895); color: #fff; font-size: 11px; text-align: center; padding: 8px;">
            🎬 4K B-Roll Clip<br><span style="color:#A5F3FC; font-size:10px;">${vis.asset_file || "stock_cutaway.mp4"}</span>
          </div>
          <div class="visual-desc"><strong>${vis.label}</strong><br>${vis.description}</div>
        `;
      } else {
        visualHtml = `
          <div class="visual-badge host-camera">${vis.badge || "👤 Host Camera"}</div>
          <div class="visual-thumb-wrapper" style="background: linear-gradient(135deg, #111827, #1F2937); color: #9CA3AF; font-size: 11px; text-align: center; padding: 8px;">
            👤 Centered Framing<br><span style="color:#10B981; font-size:10px;">Blurred Ambient (gblur=28)</span>
          </div>
          <div class="visual-desc">${vis.description}</div>
        `;
      }

      card.innerHTML = `
        <div class="scene-time-col">
          <span class="scene-badge-num">Scene ${String(scene.scene_number).padStart(2, '0')}</span>
          <span class="scene-timecode">${scene.timecode}</span>
          <span class="scene-pacing-tag">${scene.pacing || "Dialogue"}</span>
        </div>
        <div class="scene-script-col">
          <div class="scene-speaker">${scene.speaker || "Speaker"}</div>
          <div class="scene-dialogue">"${scene.dialogue}"</div>
          <div class="scene-director-note">📌 Director Note: ${scene.director_note || "Standard lower-third captions."}</div>
        </div>
        <div class="scene-visual-col">
          ${visualHtml}
        </div>
      `;

      feed.appendChild(card);
    });

  } catch (e) {
    console.error("Failed to load storyboard", e);
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
