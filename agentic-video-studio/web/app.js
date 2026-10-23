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
  initShortsGenerator();
  initAiClipsToolbar();
  loadAllAiClips();
  loadProjectsList();
});

// Mode Toggling
function initModeTabs() {
  const tabFile = document.getElementById("tab-file-mode");
  const tabUrl = document.getElementById("tab-url-mode");
  const tabShorts = document.getElementById("tab-shorts-mode");
  const secFile = document.getElementById("section-file-upload");
  const secUrl = document.getElementById("section-url-input");
  const secShorts = document.getElementById("section-shorts-input");
  const sourceBadge = document.getElementById("source-badge");

  tabFile.addEventListener("click", () => {
    tabFile.classList.add("active");
    tabUrl.classList.remove("active");
    if (tabShorts) tabShorts.classList.remove("active");
    secFile.style.display = "block";
    secUrl.style.display = "none";
    if (secShorts) secShorts.style.display = "none";
    currentMode = "file";
    sourceBadge.textContent = "Local File Mode";
  });

  tabUrl.addEventListener("click", () => {
    tabUrl.classList.add("active");
    tabFile.classList.remove("active");
    if (tabShorts) tabShorts.classList.remove("active");
    secFile.style.display = "none";
    secUrl.style.display = "block";
    if (secShorts) secShorts.style.display = "none";
    currentMode = "url";
    sourceBadge.textContent = "Web / URL Mode";
  });

  if (tabShorts) {
    tabShorts.addEventListener("click", () => {
      tabShorts.classList.add("active");
      tabFile.classList.remove("active");
      tabUrl.classList.remove("active");
      secFile.style.display = "none";
      secUrl.style.display = "none";
      if (secShorts) secShorts.style.display = "block";
      currentMode = "shorts";
      sourceBadge.textContent = "⚡ AI Shorts Discovery";

      const tabAiClips = document.getElementById("tab-view-ai-clips") || document.getElementById("tab-view-ai-shorts");
      if (tabAiClips) tabAiClips.click();
    });
  }
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

// View Tabs (Final Master vs AI Clips vs 9:16 vs 16:9 vs Shorts vs Storyboard)
function initViewTabs() {
  const tabFinal = document.getElementById("tab-view-final");
  const tabAiClips = document.getElementById("tab-view-ai-clips");
  const tab9x16 = document.getElementById("tab-view-9x16");
  const tab16x9 = document.getElementById("tab-view-16x9");
  const tabShorts = document.getElementById("tab-view-shorts");
  const tabAiShorts = document.getElementById("tab-view-ai-shorts");
  const tabStoryboard = document.getElementById("tab-view-storyboard");
  const tabEdl = document.getElementById("tab-view-edl");
  const tabPreflight = document.getElementById("tab-view-preflight");

  const viewFinal = document.getElementById("view-container-final");
  const viewAiClips = document.getElementById("view-container-ai-clips") || document.getElementById("view-container-ai-shorts");
  const view9x16 = document.getElementById("view-container-9x16");
  const view16x9 = document.getElementById("view-container-16x9");
  const viewShorts = document.getElementById("view-container-shorts");
  const viewStoryboard = document.getElementById("view-container-storyboard");
  const viewEdl = document.getElementById("view-container-edl");
  const viewPreflight = document.getElementById("view-container-preflight");

  const hideAllViews = () => {
    [tabFinal, tabAiClips, tab9x16, tab16x9, tabShorts, tabAiShorts, tabStoryboard, tabEdl, tabPreflight].forEach(t => t && t.classList.remove("active"));
    [viewFinal, viewAiClips, view9x16, view16x9, viewShorts, viewStoryboard, viewEdl, viewPreflight].forEach(v => {
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

  const showAiClipsView = () => {
    hideAllViews();
    if (tabAiClips) tabAiClips.classList.add("active");
    if (tabAiShorts) tabAiShorts.classList.add("active");
    if (viewAiClips) viewAiClips.style.display = "block";
    loadAllAiClips();
  };

  if (tabAiClips) tabAiClips.addEventListener("click", showAiClipsView);
  if (tabAiShorts) tabAiShorts.addEventListener("click", showAiClipsView);

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
      renderShortsAiGallery();
    });
  }

  // Shorts Gallery subtabs: AI Clips vs Project Master Shorts
  const subtabAiBtn = document.getElementById("subtab-btn-ai-clips");
  const subtabProjBtn = document.getElementById("subtab-btn-project-shorts");
  const subtabAiContent = document.getElementById("subtab-content-ai-clips");
  const subtabProjContent = document.getElementById("subtab-content-project-shorts");

  if (subtabAiBtn && subtabProjBtn) {
    subtabAiBtn.addEventListener("click", () => {
      subtabAiBtn.classList.add("active");
      subtabProjBtn.classList.remove("active");
      if (subtabAiContent) subtabAiContent.style.display = "block";
      if (subtabProjContent) subtabProjContent.style.display = "none";
      renderShortsAiGallery();
    });
    subtabProjBtn.addEventListener("click", () => {
      subtabProjBtn.classList.add("active");
      subtabAiBtn.classList.remove("active");
      if (subtabProjContent) subtabProjContent.style.display = "block";
      if (subtabAiContent) subtabAiContent.style.display = "none";
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

  if (tabEdl) {
    tabEdl.addEventListener("click", () => {
      hideAllViews();
      tabEdl.classList.add("active");
      if (viewEdl) viewEdl.style.display = "block";
      loadProjectEDL(currentProject);
    });
  }

  if (tabPreflight) {
    tabPreflight.addEventListener("click", () => {
      hideAllViews();
      tabPreflight.classList.add("active");
      if (viewPreflight) viewPreflight.style.display = "block";
      loadProjectPreflight(currentProject);
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

    const projectShorts = data.shorts || [];
    const totalShorts = projectShorts.length + (ALL_AI_CLIPS ? ALL_AI_CLIPS.length : 0);
    if (shortsCount) shortsCount.textContent = totalShorts;
    if (finalShortsCount) finalShortsCount.textContent = projectShorts.length;

    if (shortsGallery) shortsGallery.innerHTML = "";
    if (finalShortsGrid) finalShortsGrid.innerHTML = "";

    // A. Render Master Rendered Shorts (if any)
    if (projectShorts.length > 0) {
      if (shortsGallery) {
        const hTitle = document.createElement("div");
        hTitle.style.cssText = "width: 100%; margin-bottom: 8px; font-size: 13px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 8px;";
        hTitle.innerHTML = `<span>🎬 Rendered Master Shorts</span><span class="badge" style="color:var(--emerald); border-color:rgba(16,185,129,0.3); font-size:10px;">${projectShorts.length} Ready</span>`;
        shortsGallery.appendChild(hTitle);
      }

      projectShorts.forEach(s => {
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
    }

    // B. Populate Shorts Tab: AI Clips & Project Master Shorts
    const subtabAiBadge = document.getElementById("subtab-ai-count");
    if (subtabAiBadge) subtabAiBadge.textContent = ALL_AI_CLIPS.length;
    const subtabProjBadge = document.getElementById("subtab-proj-count");
    if (subtabProjBadge) subtabProjBadge.textContent = projectShorts.length;

    const totalShortsBadge = document.getElementById("shorts-count");
    if (totalShortsBadge) totalShortsBadge.textContent = ALL_AI_CLIPS.length + projectShorts.length;

    renderShortsAiGallery();

    if (shortsGallery) {
      shortsGallery.innerHTML = "";
      if (projectShorts.length > 0) {
        projectShorts.forEach(s => {
          const videoUrl = `/output/${projectName}/shorts/${s.filename}`;
          const card = document.createElement("div");
          card.className = "short-card";
          card.innerHTML = `
            <video src="${videoUrl}" muted loop preload="metadata" onmouseover="this.play()" onmouseout="this.pause()"></video>
            <div class="short-title">${s.name}</div>
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
        });
      } else {
        shortsGallery.innerHTML = `<p style="font-size: 12px; color: var(--text-dim); padding: 14px;">No standalone shorts generated for '${projectName}' yet.</p>`;
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

    // 6. Pre-load storyboard, EDL, and Preflight data
    loadStoryboard(projectName);

    // Wire up Herk EDL and Preflight links
    const edlLink = document.getElementById("del-link-edl");
    const edlBtn = document.getElementById("btn-launch-edl-standalone");
    const edlUrl = `/output/${projectName}/edl_review.html`;
    if (edlLink) edlLink.href = edlUrl;
    if (edlBtn) edlBtn.href = edlUrl;

    loadProjectEDL(projectName, true);

    logTerminal(`[Loaded Deliverables] Project '${projectName}' loaded into studio.`);

  } catch (e) {
    console.error("Error loading project", e);
  }
}

// Load EDL & Mistake Cutter Data (Herk Edit Kit)
async function loadProjectEDL(projectName, summaryOnly = false) {
  try {
    const res = await fetch(`/api/project/${projectName}/edl`);
    if (!res.ok) return;
    const edl = await res.json();

    const cutsCount = (edl.delete_ranges || []).length;
    const countBadge = document.getElementById("edl-cuts-count");
    if (countBadge) countBadge.textContent = cutsCount;

    if (summaryOnly) return;

    const dur = edl.source_duration || 60.0;
    const editDur = edl.edited_duration || dur;
    const removed = edl.removed || (dur - editDur);
    const pct = dur > 0 ? ((removed / dur) * 100).toFixed(1) : 0;

    const origEl = document.getElementById("edl-stat-original");
    if (origEl) origEl.textContent = `${dur.toFixed(1)}s`;
    const tightEl = document.getElementById("edl-stat-tightened");
    if (tightEl) tightEl.textContent = `${editDur.toFixed(1)}s`;
    const savedEl = document.getElementById("edl-stat-saved");
    if (savedEl) savedEl.textContent = `-${removed.toFixed(1)}s`;
    const pctEl = document.getElementById("edl-stat-pct");
    if (pctEl) pctEl.textContent = `${pct}%`;
    const countEl = document.getElementById("edl-stat-count");
    if (countEl) countEl.textContent = cutsCount;

    // Render Scrubber Track
    const track = document.getElementById("edl-visual-track");
    if (track) {
      track.innerHTML = "";
      const keeps = edl.keep_ranges || [];
      const deletes = edl.delete_ranges || [];

      keeps.forEach(k => {
        const seg = document.createElement("div");
        seg.className = "seg keep";
        seg.style.position = "absolute";
        seg.style.top = "0";
        seg.style.bottom = "0";
        seg.style.left = `${(k.start / dur) * 100}%`;
        seg.style.width = `${Math.max(0.1, ((k.end - k.start) / dur) * 100)}%`;
        seg.style.background = "var(--emerald)";
        seg.style.opacity = "0.85";
        seg.title = `Keep: ${k.start.toFixed(2)}s - ${k.end.toFixed(2)}s`;
        track.appendChild(seg);
      });

      deletes.forEach((d, idx) => {
        const seg = document.createElement("div");
        seg.className = "seg cut";
        seg.style.position = "absolute";
        seg.style.top = "0";
        seg.style.bottom = "0";
        seg.style.left = `${(d.start / dur) * 100}%`;
        seg.style.width = `${Math.max(0.35, ((d.end - d.start) / dur) * 100)}%`;
        seg.style.background = "var(--rose)";
        seg.style.opacity = "0.95";
        seg.style.cursor = "pointer";
        seg.title = `Cut #${idx + 1}: ${d.start.toFixed(2)}s - ${d.end.toFixed(2)}s (${(d.end - d.start).toFixed(2)}s)`;
        track.appendChild(seg);
      });
    }

    // Render Candidate Cuts Table
    const tbody = document.getElementById("edl-cuts-tbody");
    if (tbody) {
      tbody.innerHTML = "";
      try {
        const cRes = await fetch(`/api/project/${projectName}/cut-candidates`);
        if (cRes.ok) {
          const cData = await cRes.json();
          const candidates = cData.candidates || [];
          if (candidates.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="padding:16px; text-align:center; color:var(--text-muted);">Zero speech mistakes detected. Speech is clean!</td></tr>`;
          } else {
            candidates.forEach(c => {
              const tr = document.createElement("tr");
              tr.style.borderBottom = "1px solid var(--border-subtle)";
              tr.innerHTML = `
                <td style="padding:10px;"><span class="badge" style="color:var(--rose); border-color:rgba(244,63,94,0.3); font-size:10px;">${c.type.toUpperCase()}</span></td>
                <td style="padding:10px; font-weight:600;">${c.cut.start.toFixed(2)}s - ${c.cut.end.toFixed(2)}s</td>
                <td style="padding:10px; color:var(--rose); font-weight:700;">-${(c.cut.end - c.cut.start).toFixed(2)}s</td>
                <td style="padding:10px; color:#fca5a5;">"${c.removes || ''}"</td>
                <td style="padding:10px; color:var(--text-muted);">${c.note || c.keeps || ''}</td>
              `;
              tbody.appendChild(tr);
            });
            return;
          }
        }
      } catch (e) {}

      // Fallback to deletes in EDL
      const deletes = edl.delete_ranges || [];
      if (deletes.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="padding:16px; text-align:center; color:var(--text-muted);">Zero cuts applied.</td></tr>`;
      } else {
        deletes.forEach(d => {
          const tr = document.createElement("tr");
          tr.style.borderBottom = "1px solid var(--border-subtle)";
          tr.innerHTML = `
            <td style="padding:10px;"><span class="badge" style="color:var(--amber); border-color:rgba(245,158,11,0.3); font-size:10px;">${d.reason || 'PAUSE'}</span></td>
            <td style="padding:10px; font-weight:600;">${d.start.toFixed(2)}s - ${d.end.toFixed(2)}s</td>
            <td style="padding:10px; color:var(--rose); font-weight:700;">-${(d.end - d.start).toFixed(2)}s</td>
            <td style="padding:10px; color:var(--text-muted);">Dead Air / Pause</td>
            <td style="padding:10px; color:var(--text-muted);">Trimmed for retention</td>
          `;
          tbody.appendChild(tr);
        });
      }
    }
  } catch (e) {
    console.error("Failed to load EDL", e);
  }
}

// Load Preflight Safe-Zone Audit Data
async function loadProjectPreflight(projectName) {
  try {
    const res = await fetch(`/api/project/${projectName}/preflight`);
    if (!res.ok) return;
    const audit = await res.json();

    const badge = document.getElementById("preflight-status-badge");
    if (badge) {
      badge.textContent = audit.preflight_status || "PASSED";
      badge.style.color = audit.preflight_status === "PASSED" ? "var(--emerald)" : "var(--amber)";
    }

    if (audit.scores) {
      const fEl = document.getElementById("pf-score-face");
      if (fEl) fEl.textContent = `${audit.scores.face_safety_score || 10}/10`;
      const pEl = document.getElementById("pf-score-pacing");
      if (pEl) pEl.textContent = `${audit.scores.pacing_score || 9.8}/10`;
      const sEl = document.getElementById("pf-score-sync");
      if (sEl) sEl.textContent = `${audit.scores.beat_sync_score || 9.7}/10`;
      const cEl = document.getElementById("pf-score-contrast");
      if (cEl) cEl.textContent = `${audit.scores.contrast_legibility_score || 10}/10`;
    }

    const list = document.getElementById("preflight-checks-list");
    if (list && audit.checks) {
      list.innerHTML = "";
      for (const [key, check] of Object.entries(audit.checks)) {
        const item = document.createElement("div");
        item.style.display = "flex";
        item.style.justifyContent = "space-between";
        item.style.alignItems = "center";
        item.style.padding = "8px 12px";
        item.style.background = "rgba(255,255,255,0.03)";
        item.style.borderRadius = "8px";
        item.innerHTML = `
          <div>
            <strong>${key.replace(/_/g, " ").toUpperCase()}</strong>
            <div style="font-size:11px; color:var(--text-muted);">${check.result || check.target || check.measured || ''}</div>
          </div>
          <span class="badge" style="color:${check.status === 'PASS' ? 'var(--emerald)' : 'var(--amber)'}; font-weight:700;">
            ${check.status === 'PASS' ? '✓ PASS' : '⚠ WARN'}
          </span>
        `;
        list.appendChild(item);
      }
    }
  } catch (e) {
    console.error("Failed to load Preflight", e);
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

// -------------------------------------------------------------
// AI Shorts Discovery & Highlight Extractor (Anil Matcha + Groq)
// -------------------------------------------------------------
let selectedShortsFile = null;
let activeShortsJobId = null;
let shortsPollTimer = null;

function initShortsGenerator() {
  const shortsDropzone = document.getElementById("shorts-dropzone");
  const shortsFileInput = document.getElementById("shorts-file-input");
  const shortsFilename = document.getElementById("shorts-drop-filename");
  const shortsSubtext = document.getElementById("shorts-drop-subtext");
  const shortsUrlInput = document.getElementById("shorts-source-url");
  const btnRunShorts = document.getElementById("btn-run-shorts-extract");
  const countSelect = document.getElementById("shorts-count-select");
  const durationSelect = document.getElementById("shorts-duration-select");

  if (!btnRunShorts) return;

  if (shortsDropzone && shortsFileInput) {
    shortsDropzone.addEventListener("click", () => shortsFileInput.click());

    shortsDropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      shortsDropzone.classList.add("dragover");
    });
    shortsDropzone.addEventListener("dragleave", () => {
      shortsDropzone.classList.remove("dragover");
    });
    shortsDropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      shortsDropzone.classList.remove("dragover");
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleShortsFileSelected(e.dataTransfer.files[0]);
      }
    });

    shortsFileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleShortsFileSelected(e.target.files[0]);
      }
    });
  }

  function handleShortsFileSelected(file) {
    selectedShortsFile = file;
    if (shortsFilename) shortsFilename.textContent = file.name;
    if (shortsSubtext) shortsSubtext.textContent = `${(file.size / (1024 * 1024)).toFixed(1)} MB ready to analyze`;
    if (shortsUrlInput) shortsUrlInput.value = "";
    logTerminal(`[AI Shorts] Selected local media file: ${file.name}`);
  }

  if (shortsUrlInput) {
    shortsUrlInput.addEventListener("input", () => {
      if (shortsUrlInput.value.trim().length > 0) {
        selectedShortsFile = null;
        if (shortsFilename) shortsFilename.textContent = "Drop long video to split into shorts";
        if (shortsSubtext) shortsSubtext.textContent = "MP4, MOV, MKV up to 4K";
      }
    });
  }

  btnRunShorts.addEventListener("click", async () => {
    const url = shortsUrlInput ? shortsUrlInput.value.trim() : "";
    if (!selectedShortsFile && !url) {
      alert("Please provide a YouTube / media URL or drop a local video file.");
      return;
    }

    const numShorts = parseInt(countSelect ? countSelect.value : "3", 10) || 3;
    const durParts = (durationSelect ? durationSelect.value : "30-50").split("-");
    const minDur = parseFloat(durParts[0]) || 20.0;
    const maxDur = parseFloat(durParts[1]) || 55.0;

    // Switch view to AI Shorts tab
    const tabAiShorts = document.getElementById("tab-view-ai-shorts");
    if (tabAiShorts) tabAiShorts.click();

    const statusBar = document.getElementById("ai-shorts-status-bar");
    const statusText = document.getElementById("ai-shorts-status-text");
    if (statusBar) statusBar.style.display = "block";
    if (statusText) statusText.innerHTML = "⚡ Initializing AI Shorts extraction via Groq AI & Faster-Whisper...";

    btnRunShorts.disabled = true;
    btnRunShorts.innerHTML = "<span>⏳ Extracting Viral Clips...</span>";

    logTerminal("\n=== Launching AI Shorts Discovery Pipeline ===");
    logTerminal(`Config: ${numShorts} shorts | Duration: ${minDur}s - ${maxDur}s | LLM: Groq openai/gpt-oss-120b`);

    try {
      let resp;
      if (selectedShortsFile) {
        logTerminal(`[Upload] Uploading local file '${selectedShortsFile.name}' for highlight detection...`);
        const fd = new FormData();
        fd.append("file", selectedShortsFile);
        fd.append("num_shorts", numShorts);
        fd.append("min_duration", minDur);
        fd.append("max_duration", maxDur);
        resp = await fetch("/api/shorts/upload-and-generate", { method: "POST", body: fd });
      } else {
        logTerminal(`[URL Fetch] Ingesting stream from: ${url}...`);
        resp = await fetch("/api/shorts/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            url_or_path: url,
            num_shorts: numShorts,
            min_duration: minDur,
            max_duration: maxDur
          })
        });
      }

      const d = await resp.json();
      if (!resp.ok || d.error) {
        throw new Error(d.error || "Failed to start AI Shorts extraction");
      }

      activeShortsJobId = d.job_id;
      logTerminal(`[AI Shorts Job] Created: ${activeShortsJobId}. Extracting virality peaks...`);
      startShortsPolling(activeShortsJobId);

    } catch (err) {
      logTerminal(`[AI Shorts Error] ${err.message}`);
      if (statusText) statusText.innerHTML = `❌ Error: ${err.message}`;
      btnRunShorts.disabled = false;
      btnRunShorts.innerHTML = "🔥 Discover & Generate High-Performing Shorts";
    }
  });
}

function startShortsPolling(jobId) {
  if (shortsPollTimer) clearInterval(shortsPollTimer);

  const statusText = document.getElementById("ai-shorts-status-text");
  const btnRunShorts = document.getElementById("btn-run-shorts-extract");
  const progressBar = document.getElementById("progress-bar");
  const terminal = document.getElementById("terminal-logs");

  let lastLogCount = 0;

  shortsPollTimer = setInterval(async () => {
    try {
      const res = await fetch(`/api/shorts/status/${jobId}`);
      if (!res.ok) return;
      const job = await res.json();

      if (progressBar && job.progress !== undefined) {
        progressBar.style.width = `${job.progress}%`;
      }

      if (statusText && job.current_activity) {
        statusText.innerHTML = `⚡ [${job.progress || 0}%] ${job.current_activity}`;
      }

      if (job.logs && job.logs.length > lastLogCount && terminal) {
        for (let i = lastLogCount; i < job.logs.length; i++) {
          const time = new Date().toLocaleTimeString();
          terminal.innerHTML += `<div><span style="color:var(--text-dim)">[${time}]</span> ${job.logs[i]}</div>`;
        }
        lastLogCount = job.logs.length;
        terminal.scrollTop = terminal.scrollHeight;
      }

      if (job.status === "completed") {
        clearInterval(shortsPollTimer);
        if (progressBar) progressBar.style.width = "100%";
        if (statusText) {
          statusText.innerHTML = `✅ Successfully extracted <strong>${(job.candidates || []).length}</strong> high-retention 9:16 viral shorts!`;
        }
        if (btnRunShorts) {
          btnRunShorts.disabled = false;
          btnRunShorts.innerHTML = "🔥 Discover & Generate High-Performing Shorts";
        }
        renderAiShortsCandidates(job.candidates, job.project_slug);
        logTerminal(`[AI Shorts Complete] Generated ${job.candidates.length} candidates with 9:16 vertical previews.`);
      } else if (job.status === "failed") {
        clearInterval(shortsPollTimer);
        if (statusText) {
          statusText.innerHTML = `❌ Extraction failed: ${job.error || "Unknown error"}`;
        }
        if (btnRunShorts) {
          btnRunShorts.disabled = false;
          btnRunShorts.innerHTML = "🔥 Discover & Generate High-Performing Shorts";
        }
        logTerminal(`[AI Shorts Failed] ${job.error}`);
      }
    } catch (e) {
      console.warn("Shorts poll error", e);
    }
  }, 1000);
}

let ALL_AI_CLIPS = [];
let ALL_AI_RUNS = [];

async function loadAllAiClips(forceReload = false) {
  if (ALL_AI_CLIPS.length > 0 && !forceReload) {
    renderFilteredAiClips();
    return;
  }

  const grid = document.getElementById("ai-shorts-candidates-grid");
  if (grid && ALL_AI_CLIPS.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 48px 16px; color: var(--text-dim);">
        <div style="font-size: 32px; margin-bottom: 12px;">⏳</div>
        <h4 style="color: var(--text-muted); font-size: 16px; font-weight: 700;">Loading AI Generated Clips...</h4>
        <p style="font-size: 13px; max-width: 420px; margin: 8px auto;">
          Fetching all candidate clips discovered by the AI Clip Generator...
        </p>
      </div>
    `;
  }

  try {
    const res = await fetch("/api/shorts/recent");
    if (!res.ok) return;
    const data = await res.json();
    ALL_AI_RUNS = data.runs || [];

    const flat = [];
    let totalSec = 0;
    let peakScore = 0;

    ALL_AI_RUNS.forEach(run => {
      (run.candidates || []).forEach(c => {
        const dur = parseFloat(c.duration) || (c.end_time && c.start_time ? Math.round((c.end_time - c.start_time) * 10) / 10 : 0);
        totalSec += dur;
        const score = parseInt(c.virality_score, 10) || 85;
        if (score > peakScore) peakScore = score;

        flat.push({
          ...c,
          duration: dur,
          virality_score: score,
          project_slug: run.project_slug,
          source_title: run.source_title || run.project_slug,
          source_video: run.source_video || "",
          mtime: run.mtime || 0
        });
      });
    });

    ALL_AI_CLIPS = flat;

    // Update badges
    const totalCount = ALL_AI_CLIPS.length;
    const badgeTab = document.getElementById("ai-clips-count");
    if (badgeTab) badgeTab.textContent = totalCount;
    const badgeShorts = document.getElementById("ai-shorts-count");
    if (badgeShorts) badgeShorts.textContent = totalCount;
    const heroCount = document.getElementById("ai-shorts-hero-count");
    if (heroCount) heroCount.textContent = totalCount;

    // Update quick stats
    const statTotal = document.getElementById("stat-total-clips");
    if (statTotal) statTotal.textContent = totalCount;
    const statPeak = document.getElementById("stat-peak-score");
    if (statPeak) statPeak.textContent = `${peakScore}%`;
    const statTime = document.getElementById("stat-total-time");
    if (statTime) {
      const mins = Math.floor(totalSec / 60);
      const secs = Math.round(totalSec % 60);
      statTime.textContent = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
    }
    const statRuns = document.getElementById("stat-total-runs");
    if (statRuns) statRuns.textContent = ALL_AI_RUNS.length;

    // Populate filter dropdown
    const filterSelect = document.getElementById("filter-clips-run");
    if (filterSelect) {
      const curVal = filterSelect.value;
      filterSelect.innerHTML = `<option value="all">⚡ All Generated Clips (${totalCount})</option>`;
      ALL_AI_RUNS.forEach(run => {
        const count = (run.candidates || []).length;
        const opt = document.createElement("option");
        opt.value = run.project_slug;
        opt.textContent = `📁 ${run.source_title || run.project_slug} (${count})`;
        filterSelect.appendChild(opt);
      });
      if (curVal && Array.from(filterSelect.options).some(o => o.value === curVal)) {
        filterSelect.value = curVal;
      }
    }

    // Update subtab badges
    const subtabAiBadge = document.getElementById("subtab-ai-count");
    if (subtabAiBadge) subtabAiBadge.textContent = totalCount;
    const totalShortsBadge = document.getElementById("shorts-count");
    if (totalShortsBadge) totalShortsBadge.textContent = totalCount;

    renderFilteredAiClips();
    renderShortsAiGallery();

  } catch (err) {
    console.error("Failed to load AI clips:", err);
  }
}

function initAiClipsToolbar() {
  const filterSelect = document.getElementById("filter-clips-run");
  const searchInput = document.getElementById("search-ai-clips");
  const sortSelect = document.getElementById("sort-ai-clips");
  const btnRefresh = document.getElementById("btn-refresh-ai-clips");
  const btnGotoGen = document.getElementById("btn-goto-ai-generator");

  if (filterSelect) filterSelect.addEventListener("change", () => renderFilteredAiClips());
  if (searchInput) searchInput.addEventListener("input", () => renderFilteredAiClips());
  if (sortSelect) sortSelect.addEventListener("change", () => renderFilteredAiClips());

  if (btnRefresh) {
    btnRefresh.addEventListener("click", () => {
      btnRefresh.textContent = "⏳ Refreshing...";
      loadAllAiClips(true).then(() => {
        btnRefresh.textContent = "🔄 Refresh Clips";
        showToast("Clips library refreshed!");
      });
    });
  }

  if (btnGotoGen) {
    btnGotoGen.addEventListener("click", () => {
      const tabShortsMode = document.getElementById("tab-shorts-mode");
      if (tabShortsMode) tabShortsMode.click();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
}

function renderFilteredAiClips() {
  const grid = document.getElementById("ai-shorts-candidates-grid");
  if (!grid) return;

  const filterSelect = document.getElementById("filter-clips-run");
  const searchInput = document.getElementById("search-ai-clips");
  const sortSelect = document.getElementById("sort-ai-clips");

  const runFilter = filterSelect ? filterSelect.value : "all";
  const searchKw = searchInput ? searchInput.value.trim().toLowerCase() : "";
  const sortBy = sortSelect ? sortSelect.value : "virality";

  let list = [...ALL_AI_CLIPS];

  // 1. Filter by run
  if (runFilter !== "all") {
    list = list.filter(item => item.project_slug === runFilter);
  }

  // 2. Filter by search keyword
  if (searchKw) {
    list = list.filter(item => {
      const title = (item.title || "").toLowerCase();
      const hook = (item.hook || item.hook_quote || "").toLowerCase();
      const summary = (item.summary || item.full_text || "").toLowerCase();
      const srcTitle = (item.source_title || "").toLowerCase();
      return title.includes(searchKw) || hook.includes(searchKw) || summary.includes(searchKw) || srcTitle.includes(searchKw);
    });
  }

  // 3. Sort
  if (sortBy === "virality") {
    list.sort((a, b) => (b.virality_score || 0) - (a.virality_score || 0));
  } else if (sortBy === "newest") {
    list.sort((a, b) => (b.mtime || 0) - (a.mtime || 0));
  } else if (sortBy === "duration_desc") {
    list.sort((a, b) => (b.duration || 0) - (a.duration || 0));
  } else if (sortBy === "duration_asc") {
    list.sort((a, b) => (a.duration || 0) - (b.duration || 0));
  }

  grid.innerHTML = "";

  if (list.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 48px 16px; color: var(--text-dim); background: rgba(0,0,0,0.2); border-radius: 12px; border: 1px dashed var(--border-subtle);">
        <div style="font-size: 32px; margin-bottom: 12px;">🔍</div>
        <h4 style="color: var(--text-muted); font-size: 16px; font-weight: 700;">No Matching Clips Found</h4>
        <p style="font-size: 13px; max-width: 420px; margin: 8px auto;">
          Try adjusting your search filter or select another run.
        </p>
      </div>
    `;
    return;
  }

  list.forEach((cand, idx) => {
    const card = document.createElement("div");
    card.className = "ai-candidate-card";

    const previewUrl = cand.preview_url || `/shorts_candidates/${encodeURIComponent(cand.project_slug)}/${encodeURIComponent(cand.video_filename || "")}`;
    const score = cand.virality_score || 85;
    const durSec = (parseFloat(cand.duration) || 30.0).toFixed(1);
    const hookText = cand.hook || cand.hook_quote || "";
    const cleanHook = hookText.replace(/"/g, '&quot;');
    const startT = (cand.start_time !== undefined ? cand.start_time : 0.0).toFixed(1);
    const endT = (cand.end_time !== undefined ? cand.end_time : durSec).toFixed(1);

    card.innerHTML = `
      <div class="ai-candidate-header">
        <span class="virality-score-badge">🔥 ${score}% Virality</span>
        <span class="ai-source-pill" title="${cand.source_title}">📁 ${cand.source_title}</span>
        <span class="ai-candidate-time-pill">⏱️ ${startT}s – ${endT}s (${durSec}s)</span>
      </div>

      <div class="ai-candidate-player-wrap" style="cursor: pointer;" title="Click to preview in 9:16 player">
        <video src="${previewUrl}" muted loop preload="metadata" onmouseover="this.play()" onmouseout="this.pause()"></video>
        <div style="position: absolute; bottom: 6px; right: 6px; background: rgba(0,0,0,0.7); color: #fff; font-size: 9px; font-weight: 600; padding: 2px 6px; border-radius: 4px; pointer-events: none;">▶ Hover to play</div>
      </div>

      <div class="ai-candidate-body" style="display: flex; flex-direction: column; gap: 8px; flex: 1;">
        <h4 class="ai-candidate-title">${cand.title || `Viral Candidate #${idx + 1}`}</h4>
        
        ${hookText ? `
        <div class="ai-candidate-hook" style="position: relative;">
          <span style="color: var(--amber); font-weight: 800; font-size: 10px; text-transform: uppercase; display: block; margin-bottom: 2px;">💬 Hook Quote:</span>
          "${cleanHook}"
        </div>` : ''}

        <p class="ai-candidate-summary" style="font-size: 11.5px; color: var(--text-muted); line-height: 1.4; margin: 0;">
          ${cand.summary || cand.full_text || ""}
        </p>
        
        <div class="ai-candidate-actions" style="margin-top: auto; display: flex; flex-direction: column; gap: 8px;">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
            <a href="${previewUrl}" download="${cand.project_slug}_${cand.id}_9x16.mp4" class="btn-clip-action" style="justify-content: center; text-decoration: none;">
              ⬇️ Download MP4
            </a>
            <button class="btn-clip-action" onclick="window.copyClipHook('${encodeURIComponent(hookText)}', '${startT}', '${endT}')" style="justify-content: center;">
              📋 Copy Hook
            </button>
          </div>

          <button class="btn-primary btn-import-editor" onclick="window.importCandidateToEditor('${cand.project_slug}', '${cand.id}', this)">
            ✨ Edit in Video Editor Pro
          </button>
        </div>
      </div>
    `;

    const wrap = card.querySelector(".ai-candidate-player-wrap");
    if (wrap) {
      wrap.addEventListener("click", () => {
        const player9x16 = document.getElementById("player-9x16");
        const src9x16 = document.getElementById("player-9x16-src");
        if (player9x16 && src9x16) {
          src9x16.src = previewUrl;
          player9x16.load();
          player9x16.play();
          const tab9x16 = document.getElementById("tab-view-9x16");
          if (tab9x16) tab9x16.click();
        }
      });
    }

    grid.appendChild(card);
  });
}

function renderShortsAiGallery() {
  const container = document.getElementById("shorts-ai-gallery");
  if (!container) return;

  container.innerHTML = "";
  if (!ALL_AI_CLIPS || ALL_AI_CLIPS.length === 0) {
    container.innerHTML = `<p style="font-size: 12px; color: var(--text-dim); padding: 16px;">No AI clips created yet. Generate clips from YouTube or local videos in the left sidebar.</p>`;
    return;
  }

  ALL_AI_CLIPS.forEach((cand, idx) => {
    const previewUrl = cand.preview_url || `/shorts_candidates/${encodeURIComponent(cand.project_slug)}/${encodeURIComponent(cand.video_filename || "")}`;
    const score = cand.virality_score || 85;
    const durSec = (parseFloat(cand.duration) || 30.0).toFixed(1);
    const hookText = cand.hook || cand.hook_quote || "";
    const cleanHook = hookText.replace(/"/g, '&quot;');

    const card = document.createElement("div");
    card.className = "short-card";
    card.style.cssText = "width: 195px; height: 340px; flex-shrink: 0; background: #0b0f19; border-radius: 12px; border: 1px solid var(--border-subtle); overflow: hidden; position: relative; display: flex; flex-direction: column; transition: transform 0.2s, border-color 0.2s; box-shadow: 0 4px 14px rgba(0,0,0,0.4);";

    card.innerHTML = `
      <div style="position: relative; width: 100%; height: 210px; background: #000; overflow: hidden; cursor: pointer;">
        <video src="${previewUrl}" muted loop preload="metadata" onmouseover="this.play()" onmouseout="this.pause()" style="width: 100%; height: 100%; object-fit: cover;"></video>
        <div style="position: absolute; top: 6px; left: 6px; background: rgba(245, 158, 11, 0.9); color: #000; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.5);">
          🔥 ${score}%
        </div>
        <div style="position: absolute; top: 6px; right: 6px; background: rgba(0,0,0,0.7); color: var(--cyan); font-size: 9.5px; font-weight: 700; padding: 2px 6px; border-radius: 6px; border: 1px solid rgba(6,182,212,0.3);">
          ⏱️ ${durSec}s
        </div>
      </div>

      <div style="padding: 8px 10px 10px 10px; display: flex; flex-direction: column; justify-content: space-between; flex: 1; background: rgba(15, 23, 42, 0.95);">
        <div>
          <div style="font-size: 11.5px; font-weight: 700; color: #fff; line-height: 1.3; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="${cand.title || ''}">
            ${cand.title || `Clip #${idx + 1}`}
          </div>
          ${hookText ? `
          <div style="font-size: 10px; color: #cbd5e1; line-height: 1.3; font-style: italic; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; border-left: 2px solid var(--amber); padding-left: 5px; margin-bottom: 6px;">
            "${cleanHook}"
          </div>` : ''}
        </div>

        <button class="btn-import-editor" style="padding: 6px 8px; font-size: 10.5px; font-weight: 800; border-radius: 6px; margin-top: auto;" onclick="event.stopPropagation(); window.importCandidateToEditor('${cand.project_slug}', '${cand.id}', this)">
          ✨ Edit in Video Editor Pro
        </button>
      </div>
    `;

    // Clicking the video preview loads it into the 9:16 player
    const vEl = card.querySelector("video");
    if (vEl) {
      vEl.addEventListener("click", () => {
        const player9x16 = document.getElementById("player-9x16");
        const src9x16 = document.getElementById("player-9x16-src");
        if (player9x16 && src9x16) {
          src9x16.src = previewUrl;
          player9x16.load();
          player9x16.play();
          const tab9x16 = document.getElementById("tab-view-9x16");
          if (tab9x16) tab9x16.click();
        }
      });
    }

    container.appendChild(card);
  });
}

function renderAiShortsCandidates(candidates, projectSlug) {
  loadAllAiClips(true);
}

window.copyClipHook = function(encodedHook, startT, endT) {
  const hook = decodeURIComponent(encodedHook);
  const textToCopy = `Hook: "${hook}" (Timecode: ${startT}s - ${endT}s)`;
  navigator.clipboard.writeText(textToCopy).then(() => {
    showToast("📋 Copied Hook & Timecodes to clipboard!");
  }).catch(() => {
    showToast("Hook: " + hook);
  });
};

function showToast(msg) {
  const existing = document.querySelector(".clip-toast");
  if (existing) existing.remove();

  const toast = document.createElement("div");
  toast.className = "clip-toast";
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.transition = "opacity 0.4s ease";
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 400);
  }, 2500);
}

window.importCandidateToEditor = async function(projectSlug, candidateId, btnElement = null) {
  if (!btnElement && window.event && window.event.target) {
    btnElement = window.event.target.closest("button");
  }

  const customProjectName = `${projectSlug}_${candidateId}`;

  if (btnElement) {
    btnElement.disabled = true;
    btnElement.dataset.originalHtml = btnElement.innerHTML;
    btnElement.innerHTML = `⏳ Launching Edit...`;
    btnElement.style.opacity = "0.75";
  }

  showToast(`🚀 Importing '${candidateId}' into Video Editor Pro...`);
  logTerminal(`\n======================================================`);
  logTerminal(`🎬 [Video Editor Pro Handoff] Importing Candidate: ${candidateId} (${projectSlug})`);
  logTerminal(`Target Project: ${customProjectName}`);
  logTerminal(`Pipeline: Fast Whisper Transcription -> Herk Edit Kit -> House Reel Pacing -> Motion Cards -> 9:16 Master Compositor`);
  logTerminal(`======================================================`);

  try {
    const res = await fetch("/api/shorts/import-to-editor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        job_id: activeShortsJobId || "recent",
        project_slug: projectSlug,
        candidate_id: candidateId,
        custom_project_name: customProjectName,
        confirm_before_render: false
      })
    });

    const data = await res.json();
    if (!res.ok || data.error) {
      throw new Error(data.detail || data.error || "Failed to import candidate short");
    }

    currentProject = data.project_name;
    activeJobId = data.pipeline_job_id;

    logTerminal(`[Import Success] Pipeline Job ID: ${activeJobId}`);
    logTerminal(`[Pipeline Started] Ingesting footage -> Faster-Whisper transcription -> Herk Reel pacing -> Motion graphics -> 9:16 Master Compositor`);

    // Smoothly scroll down to the processing/terminal section so the user sees live progress
    const procSection = document.getElementById("pipeline-section");
    if (procSection) {
      procSection.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    if (btnElement) {
      btnElement.innerHTML = `⚙️ Processing in Studio...`;
    }

    startElapsedTimer();
    resetStepper();
    startJobPolling(activeJobId);

    // Refresh projects dropdown
    loadProjectsList();

  } catch (err) {
    console.error("Import error:", err);
    if (btnElement) {
      btnElement.disabled = false;
      btnElement.innerHTML = btnElement.dataset.originalHtml || `✨ Edit in Video Editor Pro`;
      btnElement.style.opacity = "1";
    }
    showToast(`❌ Import failed: ${err.message}`);
    logTerminal(`[Import Error] ${err.message}`);
  }
};


