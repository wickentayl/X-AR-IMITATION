document.addEventListener("DOMContentLoaded", () => {
  let currentStep = 0;
  const totalSteps = 4;

  const btnNext = document.getElementById("btn-next");
  const btnPrev = document.getElementById("btn-prev");
  const btnStartWizard = document.getElementById("btn-start-wizard");
  const btnSkip = document.getElementById("btn-skip");
  const btnSaveNext = document.getElementById("btn-save-next");
  const btnRecheck = document.getElementById("btn-recheck");
  const btnReset = document.getElementById("btn-reset");
  const btnToggleWasd = document.getElementById("btn-toggle-wasd");
  const wasdHud = document.getElementById("wasd-hud");
  const wasdStatusText = document.getElementById("wasd-status-text");
  const wasdInlinePreview = document.getElementById("wasd-inline-preview");
  const wasdInlinePreviewWrap = document.getElementById(
    "wasd-inline-preview-wrap",
  );

  const stepPages = document.querySelectorAll(".step-page");
  const stepDots = document.querySelectorAll(".step-dot");
  const progressBar = document.getElementById("progress-bar");
  const statusMsg = document.getElementById("status-message");
  const progressContainer = document.getElementById("progress-container");
  const wizardControls = document.getElementById("wizard-controls");

  const formUdpTgtIp = document.getElementById("udp_target_ip");
  const formUdpTgtPort = document.getElementById("udp_target_port");
  const formUnityTgtIp = document.getElementById("unity_target_ip");
  const formUnitySyncPort = document.getElementById("unity_sync_port");

  const formPosX = document.getElementById("pos_offset_x");
  const formPosY = document.getElementById("pos_offset_y");
  const formPosZ = document.getElementById("pos_offset_z");
  const formEulX = document.getElementById("euler_offset_x");
  const formEulY = document.getElementById("euler_offset_y");
  const formEulZ = document.getElementById("euler_offset_z");

  const formKfx = document.getElementById("cam_k_fx");
  const formKfy = document.getElementById("cam_k_fy");
  const formKcx = document.getElementById("cam_k_cx");
  const formKcy = document.getElementById("cam_k_cy");
  const formD = [
    document.getElementById("cam_d_0"),
    document.getElementById("cam_d_1"),
    document.getElementById("cam_d_2"),
    document.getElementById("cam_d_3"),
    document.getElementById("cam_d_4"),
  ];
  const formMoveDelay = document.getElementById("movement_delay_ms");

  let systemConfig = {};
  let isDeviceChecked = false;

  function initialize() {
    fetch("/api/config")
      .then((res) => res.json())
      .then((data) => {
        if (data.success && data.config.network) {
          systemConfig = data.config.network;

          if (systemConfig.udp_target_ip)
            formUdpTgtIp.value = systemConfig.udp_target_ip;
          if (systemConfig.udp_target_port)
            formUdpTgtPort.value = systemConfig.udp_target_port;
          if (systemConfig.unity_target_ip)
            formUnityTgtIp.value = systemConfig.unity_target_ip;
          if (systemConfig.unity_sync_port)
            formUnitySyncPort.value = systemConfig.unity_sync_port;

          if (systemConfig.pos_offset) {
            formPosX.value = systemConfig.pos_offset[0] ?? 0;
            formPosY.value = systemConfig.pos_offset[1] ?? 0.16;
            formPosZ.value = systemConfig.pos_offset[2] ?? 0;
          }
          if (systemConfig.euler_offset) {
            formEulX.value = systemConfig.euler_offset[0] ?? 0;
            formEulY.value = systemConfig.euler_offset[1] ?? 0;
            formEulZ.value = systemConfig.euler_offset[2] ?? 0;
          }
          if (systemConfig.movement_delay_ms) {
            formMoveDelay.value = systemConfig.movement_delay_ms;
          }

          if (data.config.K && data.config.K.length >= 2) {
            if (formKfx) formKfx.value = data.config.K[0][0];
            if (formKfy) formKfy.value = data.config.K[1][1];
            if (formKcx) formKcx.value = data.config.K[0][2];
            if (formKcy) formKcy.value = data.config.K[1][2];
          }
          if (data.config.D && data.config.D.length >= 5) {
            for (let i = 0; i < 5; i++) {
              if (formD[i]) formD[i].value = data.config.D[i];
            }
          }
        }

        const flipCfg = data.config.video_flip || {};
        const flipH = document.getElementById("flip_horizontal");
        const flipV = document.getElementById("flip_vertical");
        if (flipH) flipH.checked = !!flipCfg.horizontal;
        if (flipV) flipV.checked = !!flipCfg.vertical;

        fetch("/api/status")
          .then((r) => r.json())
          .then((sts) => {
            if (sts.running) {
              currentStep = 3;
              updateUI();
              runDeviceChecks();
            } else {
              updateUI();
            }
          })
          .catch((e) => updateUI());
      })
      .catch((e) => {
        console.log("Init fetch config failed", e);
        updateUI();
      });

    fetch("/api/version")
      .then((r) => r.json())
      .then((v) => {
        const badgeWebui = document.getElementById("badge-webui");
        const badgeEngine = document.getElementById("badge-engine");
        if (badgeWebui && v.webui) {
          badgeWebui.textContent = `WebUI v${v.webui.version}`;
          badgeWebui.title = `${v.webui.name}\nBuild: ${v.webui.build}`;
        }
        if (badgeEngine && v.engine) {
          const ev =
            v.engine.version === "unknown" ? "—" : `v${v.engine.version}`;
          badgeEngine.textContent = `Engine ${ev}`;
          badgeEngine.title = `${v.engine.name}\nBuild: ${v.engine.build}\nPath: ${v.engine.path}`;
          if (
            v.engine.version === "unknown" ||
            v.engine.version.startsWith("error")
          ) {
            badgeEngine.style.borderColor = "rgba(255,100,100,0.4)";
            badgeEngine.style.color = "#ff8a8a";
          }
        }
      })
      .catch(() => {});
  }

  function showStatus(msg, typeAction = "info") {
    statusMsg.style.color =
      typeAction === "error"
        ? "red"
        : typeAction === "warn"
          ? "yellow"
          : "#0f0";
    statusMsg.textContent = msg;
    setTimeout(() => (statusMsg.textContent = ""), 4000);
  }

  function updateUI() {
    stepPages.forEach((page, idx) => {
      if (idx === currentStep) {
        page.classList.add("active");
      } else {
        page.classList.remove("active");
      }
    });

    if (currentStep === 0) {
      progressContainer.style.display = "none";
      wizardControls.style.display = "none";
      return;
    } else {
      progressContainer.style.display = "block";
      wizardControls.style.display = "flex";
    }

    stepDots.forEach((dot, idx) => {
      const dotStep = idx + 1;
      if (dotStep === currentStep) {
        dot.classList.add("active");
        dot.classList.remove("completed");
      } else if (dotStep < currentStep) {
        dot.classList.add("completed");
        dot.classList.remove("active");
      } else {
        dot.classList.remove("active");
        dot.classList.remove("completed");
      }
    });

    const progressPercentage = ((currentStep - 1) / (totalSteps - 1)) * 100;
    progressBar.style.width = progressPercentage + "%";

    btnPrev.disabled = currentStep === 1;
    btnNext.style.display = "block";
    btnSkip.style.display = "none";
    btnSaveNext.style.display = "none";
    btnReset.style.display = "none";
    btnNext.disabled = false;

    if (currentStep === 2) {
      btnNext.style.display = "none";
      btnSkip.style.display = "inline-block";
      btnSaveNext.style.display = "inline-block";
    } else if (currentStep === 3) {
      if (!isDeviceChecked) {
        btnNext.disabled = true;
        runDeviceChecks();
      }
    } else if (currentStep === 4) {
      btnNext.style.display = "none";
      btnPrev.style.display = "inline-block";
      btnReset.style.display = "inline-block";
      updateDashboardVars();
    }
  }

  function getFormData() {
    const flipH = document.getElementById("flip_horizontal");
    const flipV = document.getElementById("flip_vertical");
    return {
      udp_target_ip: formUdpTgtIp.value,
      udp_target_port: parseInt(formUdpTgtPort.value),
      unity_target_ip: formUnityTgtIp.value,
      unity_sync_port: parseInt(formUnitySyncPort.value),
      pos_offset: [
        parseFloat(formPosX.value) || 0,
        parseFloat(formPosY.value) || 0,
        parseFloat(formPosZ.value) || 0,
      ],
      euler_offset: [
        parseFloat(formEulX.value) || 0,
        parseFloat(formEulY.value) || 0,
        parseFloat(formEulZ.value) || 0,
      ],
      video_flip: {
        horizontal: flipH ? flipH.checked : false,
        vertical: flipV ? flipV.checked : false,
      },
      movement_delay_ms: parseInt(formMoveDelay.value) || 0,
      K: [
        [parseFloat(formKfx.value) || 0, 0, parseFloat(formKcx.value) || 0],
        [0, parseFloat(formKfy.value) || 0, parseFloat(formKcy.value) || 0],
        [0, 0, 1],
      ],
      D: formD.map((input) => parseFloat(input.value) || 0),
    };
  }

  const btnOffsetDefault = document.getElementById("btn-offset-default");
  if (btnOffsetDefault) {
    btnOffsetDefault.addEventListener("click", () => {
      formPosX.value = 0;
      formPosY.value = 0.16;
      formPosZ.value = 0;
      formEulX.value = 0;
      formEulY.value = 0;
      formEulZ.value = 0;
      showStatus("已恢复官方默认偏移量: [0, 0.16, 0] / [0, 0, 0]", "success");
    });
  }

  const engineUploadBox =
    document.getElementById("engine-upload-card") ||
    document.getElementById("engine-upload-box");
  const engineFileInput = document.getElementById("engine-file-input");
  const engineProgressDiv = document.getElementById("engine-upload-progress");
  const engineProgressBar = document.getElementById("engine-progress-bar");
  const engineUploadStatus = document.getElementById("engine-upload-status");

  if (engineUploadBox && engineFileInput) {
    engineUploadBox.addEventListener("click", () => engineFileInput.click());
    engineUploadBox.addEventListener("dragover", (e) => {
      e.preventDefault();
    });
    engineUploadBox.addEventListener("drop", (e) => {
      e.preventDefault();
      if (e.dataTransfer.files.length) {
        engineFileInput.files = e.dataTransfer.files;
        handleEngineUpload(e.dataTransfer.files[0]);
      }
    });
    engineFileInput.addEventListener("change", () => {
      if (engineFileInput.files.length)
        handleEngineUpload(engineFileInput.files[0]);
    });

    function handleEngineUpload(file) {
      if (!file) return;
      if (
        !confirm(
          `确认要上传 "${file.name}" 替换裁判引擎 (app)？\n\n请确保系统已停止运行！`,
        )
      )
        return;

      engineProgressDiv.style.display = "block";
      engineProgressBar.style.width = "0%";
      engineUploadStatus.textContent = "准备上传...";
      engineUploadStatus.style.color = "#0aa";
      engineProgressBar.style.background = "var(--primary)";

      const formData = new FormData();
      formData.append("engine", file);

      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/api/upload_engine", true);

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          const pct = Math.round((e.loaded / e.total) * 100);
          engineProgressBar.style.width = pct + "%";
          engineUploadStatus.textContent = `上传中 ${pct}%... (${(e.loaded / 1024 / 1024).toFixed(1)}MB / ${(e.total / 1024 / 1024).toFixed(1)}MB)`;
        }
      };

      xhr.onload = () => {
        if (xhr.status === 200) {
          const res = JSON.parse(xhr.responseText);
          if (res.success) {
            engineProgressBar.style.width = "100%";
            engineProgressBar.style.background = "#28a745";
            engineUploadStatus.textContent =
              "✅ 引擎升级成功！文件已替换: " + (res.path || "app");
            engineUploadStatus.style.color = "#28a745";
          } else {
            engineProgressBar.style.background = "#ff4d4f";
            engineUploadStatus.textContent = "❌ 升级失败: " + res.error;
            engineUploadStatus.style.color = "#ff4d4f";
          }
        } else {
          engineProgressBar.style.background = "#ff4d4f";
          engineUploadStatus.textContent = "❌ 服务器错误: " + xhr.status;
          engineUploadStatus.style.color = "#ff4d4f";
        }
      };

      xhr.onerror = () => {
        engineProgressBar.style.background = "#ff4d4f";
        engineUploadStatus.textContent = "❌ 网络通信失败";
        engineUploadStatus.style.color = "#ff4d4f";
      };

      xhr.send(formData);
    }
  }

  const btnPresetA = document.getElementById("btn-import-preset-a");
  const btnPresetB = document.getElementById("btn-import-preset-b");
  const uploadBox = document.getElementById("scene-upload-box");
  const fileInput = document.getElementById("scene-file-input");
  const presetFileInput = document.getElementById("preset-file-input");
  const progContainer = document.getElementById("upload-progress-container");
  const progBar = document.getElementById("upload-progress-bar");
  const progText = document.getElementById("upload-status-text");

  let currentPresetUploadName = "";

  function updateProgressUI(pct, text, isError = false) {
    progContainer.style.display = "block";
    progBar.style.width = pct + "%";
    progBar.style.background = isError ? "#ff4d4f" : "var(--primary)";
    progText.textContent = text;
    progText.style.color = isError ? "#ff4d4f" : "#0aa";
  }

  function handleImportPreset(btn, presetName) {
    if (!btn) return;
    btn.disabled = true;
    btnNext.disabled = true;
    updateProgressUI(50, `正在解压 ${presetName}...`);
    fetch("/api/import_preset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ preset: presetName }),
    })
      .then((r) => r.json())
      .then((res) => {
        if (res.success) {
          updateProgressUI(100, `场景解压完成 ✅`);
          setTimeout(() => (btnNext.disabled = false), 500);
        } else {
          updateProgressUI(100, "失败: " + res.error, true);
          btn.disabled = false;
          btnNext.disabled = false;
        }
      })
      .catch((e) => {
        updateProgressUI(100, "请求出错", true);
        btn.disabled = false;
        btnNext.disabled = false;
      });
  }

  function bindPresetButtons(availablePresets) {
    document.querySelectorAll(".preset-card").forEach((card) => {
      const presetName = card.getAttribute("data-preset");
      const btn = card.querySelector(".preset-btn");
      if (!btn) return;

      const newBtn = btn.cloneNode(true);
      btn.parentNode.replaceChild(newBtn, btn);

      if (availablePresets.includes(presetName)) {
        newBtn.textContent = "一键导入";
        newBtn.classList.remove("trigger-scene-upload");
        newBtn.onclick = () => handleImportPreset(newBtn, presetName);
      } else {
        newBtn.textContent = "待上传";
        newBtn.classList.add("trigger-scene-upload");
        newBtn.onclick = () => {
          currentPresetUploadName = presetName;
          if (presetFileInput) presetFileInput.click();
        };
      }
    });
  }

  if (presetFileInput) {
    presetFileInput.addEventListener("change", () => {
      if (presetFileInput.files.length && currentPresetUploadName) {
        handlePresetUpload(presetFileInput.files[0], currentPresetUploadName);
      }
    });
  }

  function handlePresetUpload(file, presetName) {
    if (!file) return;
    updateProgressUI(50, `正在上传 ${presetName} 压缩包...`);
    const formData = new FormData();
    formData.append("archive", file);
    formData.append("preset_name", presetName);

    fetch("/api/upload_preset_zip", {
      method: "POST",
      body: formData,
    })
      .then((r) => r.json())
      .then((res) => {
        if (res.success) {
          updateProgressUI(100, `${presetName} 上传成功 ✅`);
          presetFileInput.value = "";
          checkAvailablePresets();
        } else {
          updateProgressUI(100, "失败: " + res.error, true);
          presetFileInput.value = "";
        }
      })
      .catch((e) => {
        updateProgressUI(100, "请求出错", true);
        presetFileInput.value = "";
      });
  }

  function checkAvailablePresets() {
    fetch("/api/check_preset")
      .then((r) => r.json())
      .then((res) => {
        if (res.success) {
          bindPresetButtons(res.available);
        } else {
          bindPresetButtons([]);
        }
      })
      .catch((e) => {
        bindPresetButtons([]);
      });
  }

  checkAvailablePresets();

  if (uploadBox && fileInput) {
    uploadBox.addEventListener("click", () => fileInput.click());

    uploadBox.addEventListener("dragover", (e) => {
      e.preventDefault();
      uploadBox.style.borderColor = "var(--primary)";
    });

    uploadBox.addEventListener("dragleave", (e) => {
      e.preventDefault();
      uploadBox.style.borderColor = "var(--border-color)";
    });

    uploadBox.addEventListener("drop", (e) => {
      e.preventDefault();
      uploadBox.style.borderColor = "var(--border-color)";
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleUpload(fileInput.files[0]);
      }
    });

    fileInput.addEventListener("change", () => {
      if (fileInput.files.length) handleUpload(fileInput.files[0]);
    });

    function handleUpload(file) {
      if (!file) return;

      if (!file.name.toLowerCase().endsWith(".zip")) {
        updateProgressUI(100, "格式错误：仅支持跨平台的 .zip 格式", true);
        return;
      }

      btnNext.disabled = true;
      uploadBox.querySelector(".upload-text").textContent =
        "准备上传: " + file.name;

      const formData = new FormData();
      formData.append("archive", file);

      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/api/upload_scene", true);

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          const pct = Math.round((e.loaded / e.total) * 90);
          updateProgressUI(pct, `上传中 ${pct}%...`);
        }
      };

      xhr.onload = () => {
        btnNext.disabled = false;
        if (xhr.status === 200) {
          const res = JSON.parse(xhr.responseText);
          if (res.success) {
            updateProgressUI(100, "处理完毕，导入成功 ✅");
          } else {
            updateProgressUI(100, "解压失败: " + res.error, true);
          }
        } else {
          updateProgressUI(100, "服务器错误: " + xhr.status, true);
        }
      };

      xhr.onerror = () => {
        btnNext.disabled = false;
        updateProgressUI(100, "网络通信失败", true);
      };

      xhr.send(formData);
    }
  }

  let logPollInterval = null;
  let statusPollInterval = null;

  let checksPassed = {
    camera: false,
    json: false,
    network: false,
  };

  let pendingChecks = {
    camera: false,
    json: false,
    network: false,
  };

  let checkAnimationRunning = false;
  let checkQueue = [];

  function runDeviceChecks() {
    const uiConnObj = {
      status: document.getElementById("status-camera-connect"),
      fix: document.getElementById("fix-camera-connect"),
    };
    const uiPermObj = {
      status: document.getElementById("status-camera-perm"),
      fix: document.getElementById("fix-camera-perm"),
    };
    const uiStreamObj = {
      status: document.getElementById("status-video-stream"),
      fix: document.getElementById("fix-video-stream"),
    };

    [uiConnObj, uiPermObj, uiStreamObj].forEach((ui) => {
      ui.status.className = "check-status status-loading";
      ui.status.innerHTML = '<span class="status-spinner"></span> 校验中...';
      ui.fix.textContent = "";
    });

    checksPassed = { camera: false, json: false, network: false };
    pendingChecks = { camera: false, json: false, network: false };
    checkAnimationRunning = false;
    checkQueue = [];

    isDeviceChecked = false;
    btnNext.disabled = true;

    showStatus("配置完毕！正在启动主进程进行自检...", "success");

    document.getElementById("summary-card").style.display = "block";
    document.querySelector("#summary-card .loading-scanner").innerHTML =
      "正在等待系统日志...";

    fetch("/api/launch", { method: "POST" })
      .then((r) => r.json())
      .then((lRes) => {
        if (lRes.success || lRes.error.includes("already running")) {
          startLogPollingForChecks(uiConnObj, uiPermObj, uiStreamObj);
        } else {
          setCheckFail(uiConnObj, "启动失败 ❌", lRes.error);
        }
      })
      .catch((e) => {
        setCheckFail(uiConnObj, "启动请求异常 ❌", "网络丢失或后端崩溃");
      });
  }

  function startLogPollingForChecks(uiConnObj, uiPermObj, uiStreamObj) {
    if (logPollInterval) clearInterval(logPollInterval);

    logPollInterval = setInterval(() => {
      fetch("/api/logs")
        .then((r) => r.json())
        .then((data) => {
          if (data.logs && data.logs.length > 0) {
            const fullLog = data.logs.join("");

            if (
              !pendingChecks.camera &&
              (fullLog.includes("[CAM] Opening") ||
                fullLog.includes("[CAM] ✅ 成功"))
            ) {
              pendingChecks.camera = true;
              if (!checkQueue) checkQueue = [];
              checkQueue.push({
                ui: uiConnObj,
                msg: "硬件引擎连接成功 ✅",
                key: "camera",
              });
            }

            if (!pendingChecks.json && fullLog.includes("[SCENE] Updated")) {
              pendingChecks.json = true;
              if (!checkQueue) checkQueue = [];
              checkQueue.push({
                ui: uiPermObj,
                msg: "场景/参数文件加载成功 ✅",
                key: "json",
              });
            }

            if (
              !pendingChecks.network &&
              (fullLog.includes("[CTRL] Listening") ||
                fullLog.includes("[OBJ_UDP] Listening") ||
                fullLog.includes("[HTTP] Streaming"))
            ) {
              pendingChecks.network = true;
              if (!checkQueue) checkQueue = [];
              checkQueue.push({
                ui: uiStreamObj,
                msg: "通信端口绑定成功 🌐✅",
                key: "network",
              });
            }

            const logBox = document.querySelector(
              "#summary-card .loading-scanner",
            );
            const lastLines = data.logs.slice(-5).join("");
            logBox.style.fontSize = "0.8rem";
            logBox.style.lineHeight = "1.2";

            if (!document.getElementById("runtime-logs-pre")) {
              logBox.innerHTML = `<strong>最新日志:</strong><br><pre id="runtime-logs-pre" style="white-space: pre-wrap; font-family: monospace; color: #0f0; margin-top:5px; background: rgba(0,0,0,0.5); padding: 5px;"></pre><div id="check-sequence-text" style="margin-top: 10px;"></div>`;
            }

            document.getElementById("runtime-logs-pre").textContent = lastLines;

            if (checkQueue && checkQueue.length > 0 && !checkAnimationRunning) {
              checkAnimationRunning = true;
              function processNextCheck() {
                if (checkQueue.length === 0) {
                  checkAnimationRunning = false;

                  if (
                    pendingChecks.camera &&
                    pendingChecks.json &&
                    pendingChecks.network &&
                    !isDeviceChecked
                  ) {
                    isDeviceChecked = true;
                    const seqBox = document.getElementById(
                      "check-sequence-text",
                    );
                    setTimeout(() => {
                      btnNext.disabled = false;
                      btnNext.focus();

                      const streamAddrRaw =
                        document.getElementById("stream-address-raw");
                      const streamAddrAR =
                        document.getElementById("stream-address-ar");
                      const currentHref = window.location.href;
                      const urlObj = new URL(currentHref);
                      if (streamAddrRaw) {
                        streamAddrRaw.textContent = `http://${urlObj.hostname}:8080/video_feed`;
                        const aTagRaw = streamAddrRaw.nextElementSibling;
                        if (aTagRaw && aTagRaw.tagName === "A")
                          aTagRaw.href = streamAddrRaw.textContent;
                      }
                      if (streamAddrAR) {
                        streamAddrAR.textContent = `http://${urlObj.hostname}:8080/ar_feed`;
                        const aTagAR = streamAddrAR.nextElementSibling;
                        if (aTagAR && aTagAR.tagName === "A")
                          aTagAR.href = streamAddrAR.textContent;
                      }

                      if (
                        seqBox &&
                        !seqBox.innerHTML.includes("系统全检通过")
                      ) {
                        seqBox.innerHTML += `<br><span style="color:#0f0; font-weight:bold; font-size: 1rem;">>>> 系统全检通过！请点击下一步。</span>`;
                      }
                    }, 500);
                  }
                  return;
                }
                const item = checkQueue.shift();
                setTimeout(() => {
                  setCheckPass(item.ui, item.msg);
                  processNextCheck();
                }, 800);
              }
              processNextCheck();
            }
          }
        })
        .catch((e) => {});
    }, 800);
  }

  function setCheckPass(uiObj, msg) {
    uiObj.status.className = "check-status status-pass";
    uiObj.status.textContent = msg;
  }

  function setCheckFail(uiObj, msg, fix) {
    uiObj.status.className = "check-status status-fail";
    uiObj.status.textContent = msg;
    uiObj.fix.textContent = "💡建议: " + fix;
  }

  function stopSystem() {
    showStatus("正在停止系统进程...", "warn");
    fetch("/api/stop", { method: "POST" })
      .then((res) => res.json())
      .then((data) => {
        if (data.success || data.error.includes("not running")) {
          showStatus("系统已停止", "success");
          isDeviceChecked = false;
          currentStep = 1;
          updateUI();
        } else {
          showStatus("停止失败: " + data.error, "error");
        }
      })
      .catch((e) => {
        showStatus("请求终止异常", "error");
      });
  }

  function updateDashboardVars() {
    const formData = getFormData();
    const dIp = document.getElementById("display-udp-ip");
    if (dIp) dIp.textContent = formData.udp_target_ip || "127.0.0.1";

    const dPort = document.getElementById("display-udp-port");
    if (dPort) dPort.textContent = formData.udp_target_port || 9000;

    const wasdPortElem = document.getElementById("wasd-udp-port");
    if (wasdPortElem)
      wasdPortElem.textContent = systemConfig.control_port || 9005;
  }

  const btnStartPreview = document.getElementById("btn-start-preview");
  const btnStopPreview = document.getElementById("btn-stop-preview");
  const btnCopyStream = document.getElementById("btn-copy-stream");

  if (btnCopyStream) {
    btnCopyStream.addEventListener("click", () => {
      const streamUrl = document.getElementById("stream-address").innerText;

      const fallbackCopy = (text) => {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-9999px";
        document.body.appendChild(textArea);
        textArea.select();
        try {
          document.execCommand("copy");
        } catch (err) {}
        document.body.removeChild(textArea);
      };

      const showCopied = () => {
        btnCopyStream.textContent = "已复制!";
        btnCopyStream.style.background = "#28a745";
        btnCopyStream.style.borderColor = "#28a745";
        btnCopyStream.style.color = "#fff";
        setTimeout(() => {
          btnCopyStream.textContent = "复制";
          btnCopyStream.style.background = "";
          btnCopyStream.style.borderColor = "";
          btnCopyStream.style.color = "";
        }, 2000);
      };

      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard
          .writeText(streamUrl)
          .then(showCopied)
          .catch((e) => {
            fallbackCopy(streamUrl);
            showCopied();
          });
      } else {
        fallbackCopy(streamUrl);
        showCopied();
      }
    });
  }

  btnStartPreview.addEventListener("click", () => {
    if (btnStartPreview.classList.contains("disabled")) return;

    btnStartPreview.classList.add("disabled");
    btnStartPreview.textContent = "⏳ 正在请求拉起 ar_receiver.py ...";

    fetch("/api/start_preview", { method: "POST" })
      .then((r) => r.json())
      .then((res) => {
        if (res.success) {
          btnStartPreview.textContent = "✅ 已运行 (请在后端屏幕查看窗口)";
          btnStopPreview.style.display = "inline-block";
        } else {
          btnStartPreview.classList.remove("disabled");
          btnStartPreview.textContent = "❌ 启动失败，点击重试";
          showStatus(res.error, "error");
        }
      })
      .catch((e) => {
        btnStartPreview.classList.remove("disabled");
        btnStartPreview.textContent = "🖥️ 打开 X板卡端的AR 融合预览窗口";
      });
  });

  btnStopPreview.addEventListener("click", () => {
    btnStopPreview.textContent = "⏳ 正在关闭...";
    fetch("/api/stop_preview", { method: "POST" })
      .then((r) => r.json())
      .then((res) => {
        btnStartPreview.classList.remove("disabled");
        btnStartPreview.textContent = "🖥️ 打开 X板卡端的AR 融合预览窗口";
        btnStopPreview.style.display = "none";
        btnStopPreview.textContent = "⏹️ 关闭预览窗口";
      });
  });

  btnStartWizard.addEventListener("click", () => {
    currentStep = 1;
    updateUI();
    progressContainer.style.display = "block";
    wizardControls.style.display = "flex";
  });

  btnPrev.addEventListener("click", () => {
    if (currentStep === 3 && (isDeviceChecked || checksPassed.camera)) {
      showStatus(
        "🚫 请先点击【⛔ 停止运行系统】后再返回上一步修改网络配置。",
        "warn",
      );
      return;
    }
    if (currentStep > 1) {
      currentStep--;
      updateUI();
    }
  });

  btnNext.addEventListener("click", () => {
    if (currentStep < totalSteps) {
      currentStep++;
      updateUI();
    }
  });

  btnSkip.addEventListener("click", () => {
    currentStep = 3;
    updateUI();
  });

  btnSaveNext.addEventListener("click", () => {
    const data = getFormData();
    btnSaveNext.disabled = true;
    fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((res) => res.json())
      .then((result) => {
        btnSaveNext.disabled = false;
        if (result.success) {
          showStatus("网络配置保存成功", "success");
          currentStep = 3;
          updateUI();
        } else {
          showStatus("保存文件失败: " + result.error, "error");
        }
      })
      .catch((err) => {
        btnSaveNext.disabled = false;
        showStatus("网络保存失败", "error");
      });
  });

  btnReset.addEventListener("click", () => {
    stopSystem();
  });

  const btnStopSystem = document.getElementById("btn-stop-system");
  if (btnStopSystem) {
    btnStopSystem.addEventListener("click", () => {
      if (currentStep === 3) {
        stopSystem();
      }
    });
  }

  btnRecheck.addEventListener("click", () => {
    if (currentStep === 3) {
      runDeviceChecks();
    }
  });

  document
    .getElementById("btn-download-json")
    .addEventListener("click", (e) => {
      e.preventDefault();
      const demoObj = {
        type: "robot_position",
        pos: [1.5, 0.0, -2.0],
        euler: [0.0, 45.0, 0.0],
        seq: 1024,
        timestamp: new Date().getTime() / 1000.0,
      };
      const dataStr =
        "data:text/json;charset=utf-8," +
        encodeURIComponent(JSON.stringify(demoObj, null, 2));
      const dlAnchorElem = document.createElement("a");
      dlAnchorElem.setAttribute("href", dataStr);
      dlAnchorElem.setAttribute("download", "external_pose_demo.json");
      dlAnchorElem.click();
    });

  let isWasdActive = false;
  const heldWasdKeys = new Set();
  let wasdTimer = null;
  let wasdRequestActive = false;

  function clearWasdKeys() {
    heldWasdKeys.clear();
    if (wasdTimer) {
      clearInterval(wasdTimer);
      wasdTimer = null;
    }
    wasdRequestActive = false;
  }

  function sendWasdKeys() {
    if (!isWasdActive || heldWasdKeys.size === 0 || wasdRequestActive) return;
    wasdRequestActive = true;
    fetch("/api/sim_control", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ keys: Array.from(heldWasdKeys) }),
    })
      .then((r) => r.json())
      .then((res) => {
        if (res.success) updateWasdInputs(res);
      })
      .finally(() => {
        wasdRequestActive = false;
      });
  }

  function ensureWasdLoop() {
    if (!wasdTimer) {
      sendWasdKeys();
      wasdTimer = setInterval(sendWasdKeys, 45);
    }
  }

  if (btnToggleWasd) {
    btnToggleWasd.addEventListener("click", () => {
      isWasdActive = !isWasdActive;
      if (isWasdActive) {
        wasdHud.style.display = "block";
        btnToggleWasd.textContent = "⏹ 退出遥控模式";
        btnToggleWasd.style.background = "#ff4d4f";
        btnToggleWasd.style.borderColor = "#ff4d4f";
        if (wasdInlinePreview && wasdInlinePreviewWrap) {
          wasdInlinePreview.src = `${window.location.protocol}//${window.location.hostname}:8080/ar_feed?t=${Date.now()}`;
          wasdInlinePreviewWrap.style.display = "block";
        }
      } else {
        clearWasdKeys();
        wasdHud.style.display = "none";
        btnToggleWasd.textContent = "▶ 激活动态虚拟摇杆";
        btnToggleWasd.style.background = "#28a745";
        btnToggleWasd.style.borderColor = "#28a745";
        if (wasdInlinePreview && wasdInlinePreviewWrap) {
          wasdInlinePreview.removeAttribute("src");
          wasdInlinePreviewWrap.style.display = "none";
        }
      }
    });
  }

  document.addEventListener("keydown", (e) => {
    if (!isWasdActive) return;

    const key = e.key.toLowerCase();
    if (["w", "a", "s", "d"].includes(key)) {
      e.preventDefault();
      heldWasdKeys.add(key);
      ensureWasdLoop();
    } else if (key === "q") {
      btnToggleWasd.click();
    }
  });

  document.addEventListener("keyup", (e) => {
    if (!isWasdActive) return;

    const key = e.key.toLowerCase();
    if (["w", "a", "s", "d"].includes(key)) {
      e.preventDefault();
      heldWasdKeys.delete(key);
      if (heldWasdKeys.size === 0) {
        clearWasdKeys();
      }
    }
  });

  function updateWasdInputs(res) {
    const xInput = document.getElementById("wasd-manual-x");
    const yInput = document.getElementById("wasd-manual-y");
    const zInput = document.getElementById("wasd-manual-z");
    const yawInput = document.getElementById("wasd-manual-yaw");
    if (xInput) xInput.value = res.pos[0].toFixed(2);
    if (yInput) yInput.value = res.pos[1].toFixed(2);
    if (zInput) zInput.value = res.pos[2].toFixed(2);
    if (yawInput) yawInput.value = res.yaw.toFixed(1);
    wasdStatusText.textContent = `X: ${res.pos[0].toFixed(2)} \xA0 Y: ${res.pos[1].toFixed(2)} \xA0 Z: ${res.pos[2].toFixed(2)} \xA0 YAW: ${res.yaw.toFixed(1)}°`;
  }

  ["x", "y", "z", "yaw"].forEach((axis) => {
    const input = document.getElementById(`wasd-manual-${axis}`);
    if (input) {
      input.addEventListener("change", (e) => {
        fetch("/api/sim_control", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            key: `set_${axis}`,
            val: parseFloat(e.target.value),
          }),
        })
          .then((r) => r.json())
          .then((res) => {
            if (res.success) updateWasdInputs(res);
          });
      });
    }
  });

  const btnWasdInit = document.getElementById("btn-wasd-init");
  if (btnWasdInit) {
    btnWasdInit.addEventListener("click", () => {
      fetch("/api/sim_control", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key: "init_xz_yaw" }),
      })
        .then((r) => r.json())
        .then((res) => {
          if (res.success) updateWasdInputs(res);
        });
    });
  }

  const matchRecordsList = document.getElementById("match-records-list");
  const btnRefreshRecords = document.getElementById("btn-refresh-records");
  const viewerModal = document.getElementById("referee-viewer-modal");
  const viewerTitle = document.getElementById("viewer-title");
  const viewerSubtitle = document.getElementById("viewer-subtitle");
  const viewerStats = document.getElementById("viewer-stats");
  const viewerEvents = document.getElementById("viewer-events");
  const btnCloseViewer = document.getElementById("btn-close-viewer");

  function loadMatchRecords() {
    if (!matchRecordsList) return;
    matchRecordsList.innerHTML =
      '<div style="text-align:center;color:var(--text-muted);padding:20px;">⏳ 加载中...</div>';

    fetch("/api/match_records")
      .then((r) => r.json())
      .then((res) => {
        if (!res.success || !res.records || res.records.length === 0) {
          matchRecordsList.innerHTML =
            '<div style="text-align:center;color:var(--text-muted);padding:20px;">暂无比赛记录</div>';
          return;
        }

        let html = "";
        res.records.forEach((rec) => {
          const evtCount = rec.total_events;
          const evtLabel =
            evtCount < 0
              ? "⚠ 解析失败"
              : evtCount === 0
                ? "无事件"
                : `${evtCount} 个事件`;
          const evtColor =
            evtCount > 0
              ? "#0f0"
              : evtCount === 0
                ? "var(--text-muted)"
                : "#ff4d4f";
          const dateStr =
            rec.match_date ||
            rec.filename.replace("match_record_", "").replace(".json", "");

          html += `
                    <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;border-bottom:1px solid rgba(255,255,255,0.06);transition:background 0.2s;" 
                         onmouseover="this.style.background='rgba(0,255,170,0.05)'" onmouseout="this.style.background='transparent'">
                        <div style="flex:1;">
                            <div style="font-size:0.9rem;font-weight:500;color:#eee;">📄 ${dateStr}</div>
                            <div style="font-size:0.78rem;color:${evtColor};margin-top:2px;">${evtLabel}</div>
                        </div>
                        <div style="display:flex;gap:6px;">
                            <button class="btn-ghost" style="font-size:0.75rem;padding:4px 10px;" 
                                    onclick="window._viewRecord('${rec.filename}')">👁 查看</button>
                            <a href="/api/match_record/${rec.filename}/download" class="btn-ghost" 
                               style="font-size:0.75rem;padding:4px 10px;text-decoration:none;color:inherit;display:inline-flex;align-items:center;">⬇ 下载</a>
                        </div>
                    </div>`;
        });
        matchRecordsList.innerHTML = html;
      })
      .catch((e) => {
        matchRecordsList.innerHTML =
          '<div style="text-align:center;color:#ff4d4f;padding:20px;">加载失败</div>';
      });
  }

  const EVENT_CONFIG = {
    COLLISION: { icon: "💥", color: "#ff4d4f", label: "碰撞" },
    TRAFFIC: { icon: "🚦", color: "#faad14", label: "红绿灯" },
    LAP: { icon: "🏁", color: "#1890ff", label: "圈数" },
    SYSTEM: { icon: "⚙️", color: "#888", label: "系统" },
  };

  window._viewRecord = function (filename) {
    fetch(`/api/match_record/${filename}`)
      .then((r) => r.json())
      .then((res) => {
        if (!res.success) {
          alert("加载失败: " + (res.error || ""));
          return;
        }
        const data = res.data;
        const events = data.events || [];

        viewerTitle.textContent = "📋 " + (data.match_date || filename);
        viewerSubtitle.textContent = `共 ${events.length} 个事件 | 文件: ${filename}`;

        const counts = {};
        events.forEach((ev) => {
          const t = ev.type || "UNKNOWN";
          counts[t] = (counts[t] || 0) + 1;
        });

        let statsHtml = "";
        statsHtml += `<div style="background:rgba(255,255,255,0.06);border-radius:8px;padding:10px 16px;text-align:center;min-width:80px;">
                    <div style="font-size:1.5rem;font-weight:bold;color:var(--primary);">${events.length}</div>
                    <div style="font-size:0.75rem;color:var(--text-muted);">总事件</div>
                </div>`;

        for (const [type, count] of Object.entries(counts)) {
          const cfg = EVENT_CONFIG[type] || {
            icon: "❓",
            color: "#ccc",
            label: type,
          };
          statsHtml += `<div style="background:rgba(255,255,255,0.06);border-radius:8px;padding:10px 16px;text-align:center;min-width:80px;">
                        <div style="font-size:1.5rem;font-weight:bold;color:${cfg.color};">${count}</div>
                        <div style="font-size:0.75rem;color:var(--text-muted);">${cfg.icon} ${cfg.label}</div>
                    </div>`;
        }
        viewerStats.innerHTML = statsHtml;

        if (events.length === 0) {
          viewerEvents.innerHTML =
            '<div style="text-align:center;color:var(--text-muted);padding:30px;">本场比赛没有产生任何裁判事件</div>';
        } else {
          let evHtml = "";
          events.forEach((ev, idx) => {
            const cfg = EVENT_CONFIG[ev.type] || {
              icon: "❓",
              color: "#ccc",
              label: ev.type,
            };
            const timeStr = ev.time_str || "";
            const elapsed =
              ev.elapsed_seconds != null ? `${ev.elapsed_seconds}s` : "";
            const msg = ev.message || "";
            const extraData = ev.data || {};

            let chips = "";
            for (const [k, v] of Object.entries(extraData)) {
              let chipColor = "#555";
              let chipText = `${k}: ${v}`;
              if (k === "light") {
                const lightNames = { 0: "🔴 红灯", 1: "🟢 绿灯", 2: "🟡 黄灯" };
                chipText = lightNames[v] || `灯态=${v}`;
                chipColor =
                  v === 0 ? "#8B0000" : v === 1 ? "#006400" : "#8B8000";
              } else if (k === "name") {
                chipText = `物体: ${v}`;
              } else if (k === "lap") {
                chipText = `第 ${v} 圈`;
                chipColor = "#1a3a5c";
              }
              chips += `<span style="display:inline-block;background:${chipColor};color:#eee;padding:2px 8px;border-radius:10px;font-size:0.7rem;margin-left:5px;">${chipText}</span>`;
            }

            evHtml += `
                        <div style="display:flex;align-items:flex-start;gap:10px;padding:8px 5px;border-left:3px solid ${cfg.color};margin-bottom:6px;background:rgba(0,0,0,0.15);border-radius:0 6px 6px 0;">
                            <div style="min-width:28px;text-align:center;font-size:1.1rem;">${cfg.icon}</div>
                            <div style="flex:1;">
                                <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                                    <span style="font-size:0.9rem;font-weight:500;color:#eee;">${msg}</span>
                                    ${chips}
                                </div>
                                <div style="font-size:0.72rem;color:var(--text-muted);margin-top:3px;">
                                    #${ev.index || idx + 1} | ${timeStr} | 经过 ${elapsed} | ID: ${ev.obj_id != null ? ev.obj_id : "-"}
                                </div>
                            </div>
                        </div>`;
          });
          viewerEvents.innerHTML = evHtml;
        }

        viewerModal.style.display = "block";
        viewerModal.scrollIntoView({ behavior: "smooth" });
      })
      .catch((e) => alert("请求失败"));
  };

  if (btnCloseViewer) {
    btnCloseViewer.addEventListener("click", () => {
      viewerModal.style.display = "none";
    });
  }

  if (btnRefreshRecords) {
    btnRefreshRecords.addEventListener("click", () => {
      loadMatchRecords();
    });
  }

  const origUpdateUI = updateUI;
  updateUI = function () {
    origUpdateUI();
    if (currentStep === 4) {
      loadMatchRecords();
    }
  };

  const btnRunAi = document.getElementById("btn-run-ai");
  const btnStopAi = document.getElementById("btn-stop-ai");
  const aiAutoLoop = document.getElementById("ai-auto-loop");
  const aiLoopIntervalInput = document.getElementById("ai-loop-interval");
  const aiTokenInput = document.getElementById("ai-token");
  const aiPromptInput = document.getElementById("ai-prompt");
  const aiResultBox = document.getElementById("ai-result-box");
  const aiStatusInd = document.getElementById("ai-status-indicator");

  let isAiRunning = false;
  let aiLoopTimer = null;

  function stopInference() {
    if (aiLoopTimer) clearTimeout(aiLoopTimer);
    if (aiAutoLoop) aiAutoLoop.checked = false;
    isAiRunning = false;
    aiStatusInd.textContent = "(停止推理)";
    btnRunAi.disabled = false;
    btnRunAi.style.background = "#ffaa00";
    btnRunAi.style.borderColor = "#ffaa00";
    btnRunAi.innerHTML = "⚡ 实时推理";
  }

  async function startInference() {
    if (isAiRunning) return;

    const token = aiTokenInput.value.trim();
    const prompt = aiPromptInput.value.trim();

    if (!token) {
      alert("请先填写 AI Studio Access Token！");
      if (aiAutoLoop) aiAutoLoop.checked = false;
      return;
    }

    isAiRunning = true;
    btnRunAi.innerHTML = "⏹️ 停止推理";
    btnRunAi.style.background = "#ff4d4f";
    btnRunAi.style.borderColor = "#ff4d4f";
    aiStatusInd.textContent = "(请求中)";

    const timestamp = new Date().toLocaleTimeString();
    const roundHeader = document.createElement("div");
    roundHeader.style.margin = "20px 0 10px 0";
    roundHeader.style.padding = "5px 10px";
    roundHeader.style.background = "rgba(255,170,0,0.15)";
    roundHeader.style.borderLeft = "4px solid #ffaa00";
    roundHeader.style.fontSize = "0.85rem";
    roundHeader.style.color = "#ffaa00";
    roundHeader.innerHTML = `<strong>🕒 ${timestamp} 画面解说请求轮次</strong>`;
    aiResultBox.appendChild(roundHeader);

    const contentContainer = document.createElement("div");
    contentContainer.style.marginBottom = "10px";
    aiResultBox.appendChild(contentContainer);
    aiResultBox.scrollTop = aiResultBox.scrollHeight;

    try {
      const response = await fetch("/api/test_llm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, prompt }),
      });

      if (!response.ok) throw new Error("HTTP 错误: " + response.status);

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (isAiRunning) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop();

        for (const chunk of lines) {
          const eventMatch = chunk.match(/event: (.*)\n/);
          const dataMatch = chunk.match(/data: (.*)/);

          if (eventMatch && dataMatch) {
            const eventType = eventMatch[1];
            let dataText = dataMatch[1].replace(/\\n/g, "\n");

            if (eventType === "content") {
              const span = document.createElement("span");
              span.textContent = dataText;
              contentContainer.appendChild(span);
            } else if (eventType === "error") {
              const errSpan = document.createElement("div");
              errSpan.style.color = "#ff4d4f";
              errSpan.style.marginTop = "5px";
              errSpan.textContent = "[错误] " + dataText;
              contentContainer.appendChild(errSpan);
            }
            aiResultBox.scrollTop = aiResultBox.scrollHeight;
          }
        }
      }
      if (isAiRunning) aiStatusInd.textContent = "(解说完成)";
    } catch (err) {
      if (isAiRunning) {
        const errDiv = document.createElement("div");
        errDiv.style.color = "#ff4d4f";
        errDiv.textContent = "❌ 推理异常: " + err.message;
        contentContainer.appendChild(errDiv);
        aiStatusInd.textContent = "(异常)";
        if (aiAutoLoop) aiAutoLoop.checked = false;
      }
    } finally {
      if (!aiAutoLoop || !aiAutoLoop.checked || !isAiRunning) {
        stopInference();
      } else {
        let interval = parseInt(aiLoopIntervalInput.value) || 5;
        if (interval < 5) interval = 5;
        isAiRunning = false;

        aiStatusInd.textContent = `(${interval}秒后自动发起下次请求...)`;
        aiLoopTimer = setTimeout(() => {
          isAiRunning = false;
          startInference();
        }, interval * 1000);
      }
    }
  }

  if (btnRunAi) {
    btnRunAi.addEventListener("click", () => {
      if (isAiRunning || aiLoopTimer) {
        stopInference();
      } else {
        startInference();
      }
    });
  }

  if (aiAutoLoop) {
    aiAutoLoop.addEventListener("change", () => {
      if (aiAutoLoop.checked && !isAiRunning) {
        startInference();
      } else if (!aiAutoLoop.checked) {
        if (aiLoopTimer) clearTimeout(aiLoopTimer);
        aiStatusInd.textContent = "(循环已停止)";
      }
    });
  }

  (function () {
    const dropzone = document.getElementById("selfupdate-dropzone");
    const fileInput = document.getElementById("selfupdate-file-input");
    const progWrap = document.getElementById("selfupdate-progress-wrap");
    const progBar = document.getElementById("selfupdate-progress-bar");
    const statusEl = document.getElementById("selfupdate-status");
    const dropText = document.getElementById("selfupdate-dropzone-text");

    if (!dropzone || !fileInput) return;

    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.style.borderColor = "var(--primary)";
    });
    dropzone.addEventListener("dragleave", () => {
      dropzone.style.borderColor = "#444";
    });
    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.style.borderColor = "#444";
      if (e.dataTransfer.files.length)
        handleSelfUpdate(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener("change", () => {
      if (fileInput.files.length) handleSelfUpdate(fileInput.files[0]);
    });

    function handleSelfUpdate(file) {
      if (
        !confirm(
          `确认要上传 "${file.name}" 替换当前 WebUI (setup_webui)？\n\n上传完成后系统将自动重启，页面会短暂断开。`,
        )
      )
        return;

      const formData = new FormData();
      formData.append("webui", file);

      progWrap.style.display = "block";
      progBar.style.width = "0%";
      progBar.style.background = "var(--primary)";
      statusEl.style.color = "#0aa";
      statusEl.textContent = "准备上传...";
      dropText.textContent = `上传中: ${file.name}`;

      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/api/self_update", true);

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          const pct = Math.round((e.loaded / e.total) * 95);
          progBar.style.width = pct + "%";
          statusEl.textContent = `上传中 ${pct}%... (${(e.loaded / 1024 / 1024).toFixed(1)}MB / ${(e.total / 1024 / 1024).toFixed(1)}MB)`;
        }
      };

      xhr.onload = () => {
        progBar.style.width = "100%";
        if (xhr.status === 200) {
          let res = {};
          try {
            res = JSON.parse(xhr.responseText);
          } catch (_) {}
          if (res.success) {
            progBar.style.background = "#28a745";
            statusEl.style.color = "#28a745";
            statusEl.textContent =
              "✅ 上传成功！WebUI 将在 3 秒后重启，页面自动重连...";
            dropText.textContent = "✅ 完成";

            let countdown = 6;
            const timer = setInterval(() => {
              countdown--;
              statusEl.textContent = `✅ 上传成功！页面将在 ${countdown} 秒后自动刷新重连...`;
              if (countdown <= 0) {
                clearInterval(timer);
                window.location.reload();
              }
            }, 1000);
          } else {
            progBar.style.background = "#ff4d4f";
            statusEl.style.color = "#ff4d4f";
            statusEl.textContent = "❌ 失败: " + (res.error || "未知错误");
            dropText.textContent = "点击或拖拽 setup_webui 文件到这里";
          }
        } else {
          progBar.style.background = "#ff4d4f";
          statusEl.style.color = "#ff4d4f";
          statusEl.textContent = "❌ 服务器错误: HTTP " + xhr.status;
          dropText.textContent = "点击或拖拽 setup_webui 文件到这里";
        }
        fileInput.value = "";
      };

      xhr.onerror = () => {
        progBar.style.background = "#ff4d4f";
        statusEl.style.color = "#ff4d4f";
        statusEl.textContent = "❌ 网络通信失败";
        fileInput.value = "";
      };

      xhr.send(formData);
    }
  })();

  initialize();
});
