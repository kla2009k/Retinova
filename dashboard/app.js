const input = document.querySelector('#imageInput');
const dropzone = document.querySelector('#dropzone');
const frame = document.querySelector('#previewFrame');
const image = document.querySelector('#previewImage');
const removeButton = document.querySelector('#removeImage');
const analyzeButton = document.querySelector('#analyzeButton');
const emptyResult = document.querySelector('#emptyResult');
const checkResult = document.querySelector('#checkResult');
const fileCheck = document.querySelector('#fileCheck');
const resolutionCheck = document.querySelector('#resolutionCheck');
const langButton = document.querySelector('#langButton');
const searchForm = document.querySelector('#searchForm');
const searchInput = document.querySelector('#searchInput');
const mainContent = document.querySelector('#mainContent');
const welcomeGate = document.querySelector('#welcomeGate');
const appShell = document.querySelector('#appShell');
const teamLoginForm = document.querySelector('#teamLoginForm');
const teamLoginButton = document.querySelector('#teamLoginButton');
const teamPasscode = document.querySelector('#teamPasscode');
const teamLoginStatus = document.querySelector('#teamLoginStatus');
const comparisonSlider = document.querySelector('#comparisonSlider');
const comparisonOverlay = document.querySelector('#comparisonOverlay');
const cameraPanel = document.querySelector('#cameraPanel');
const cameraVideo = document.querySelector('#cameraVideo');
const cameraCanvas = document.querySelector('#cameraCanvas');
const cameraStatus = document.querySelector('#cameraStatus');
const capturePhotoButton = document.querySelector('#capturePhotoButton');
const fundusEquipmentCheck = document.querySelector('#fundusEquipmentCheck');

const validViews = new Set(['home', 'analyze', 'history', 'eye-health', 'evidence']);
const viewTitles = {
  home: ['หน้าแรก', 'Home'],
  analyze: ['วิเคราะห์ภาพ', 'Analyze'],
  history: ['ผลล่าสุด', 'Session results'],
  'eye-health': ['ความรู้ดวงตา', 'Eye health'],
  evidence: ['หลักฐานโมเดล', 'Evidence'],
};
const classNames = {
  N: ['ปกติ', 'Normal'],
  D: ['เบาหวาน', 'Diabetes'],
  G: ['ต้อหิน', 'Glaucoma'],
  C: ['ต้อกระจก', 'Cataract'],
  A: ['จอประสาทตาเสื่อม', 'AMD'],
  H: ['ความดันโลหิต', 'Hypertension'],
  M: ['สายตาสั้นผิดปกติ', 'Myopia'],
  O: ['ความผิดปกติอื่น', 'Other'],
};

const MAX_SESSION_RESULTS = 50;
const sessionHistory = [];
let selectedFile = null;
let language = 'th';
let localModelReady = false;
let localAuthRequired = false;
let teamAuthenticated = false;
let activeView = 'home';
let cameraStream = null;
let cameraFacingMode = 'environment';
let selectedInputSource = 'file';
let selectedCaptureHasFundusOptics = false;

function translated(element) {
  return element.dataset[language] || element.textContent;
}

function applyLanguage(nextLanguage) {
  language = nextLanguage;
  document.documentElement.lang = language;
  document.querySelectorAll('[data-th][data-en]').forEach((element) => {
    element.textContent = translated(element);
  });
  document.querySelectorAll('[data-th-placeholder][data-en-placeholder]').forEach((element) => {
    element.placeholder = element.dataset[`${language}Placeholder`];
  });
  document.querySelectorAll('[data-welcome-language]').forEach((button) => {
    button.classList.toggle('active', button.dataset.welcomeLanguage === language);
  });
  langButton.textContent = language === 'th' ? 'EN' : 'TH';
  document.title = `Retinova — ${viewTitles[activeView][language === 'th' ? 0 : 1]}`;
  updateClock();
  renderSessionHistory();
  if (localModelReady) setLocalModelUi();
}

function showView(viewName, updateUrl = true) {
  const nextView = validViews.has(viewName) ? viewName : 'home';
  if (activeView === 'analyze' && nextView !== 'analyze') stopCamera();
  activeView = nextView;
  document.querySelectorAll('.app-view').forEach((view) => {
    view.hidden = view.dataset.page !== nextView;
  });
  document.querySelectorAll('.nav-item').forEach((button) => {
    const active = button.dataset.view === nextView;
    button.classList.toggle('active', active);
    if (active) button.setAttribute('aria-current', 'page');
    else button.removeAttribute('aria-current');
  });
  document.title = `Retinova — ${viewTitles[nextView][language === 'th' ? 0 : 1]}`;
  if (updateUrl) history.replaceState(null, '', `#${nextView}`);
  window.scrollTo({top: 0, behavior: 'auto'});
  mainContent.focus({preventScroll: true});
}

function enterApp(mode) {
  welcomeGate.hidden = true;
  appShell.hidden = false;
  const sessionButton = document.querySelector('#sessionButton');
  sessionButton.textContent = mode === 'team' ? 'ท' : 'ร';
  sessionButton.title = language === 'th' ? 'ออกจากเซสชัน' : 'Leave session';
  showView(location.hash.slice(1), false);
}

async function leaveSession() {
  if (teamAuthenticated) {
    try {
      await fetch('/session', {method: 'DELETE', credentials: 'same-origin'});
    } catch (_error) {
      // The page still returns safely to the welcome gate if the local server stopped.
    }
  }
  teamAuthenticated = false;
  localModelReady = !localAuthRequired && localModelReady;
  resetImage();
  appShell.hidden = true;
  welcomeGate.hidden = false;
  teamPasscode.value = '';
  await detectLocalModel();
}

function updateClock() {
  const now = new Date();
  document.querySelector('#clockTime').textContent = new Intl.DateTimeFormat(
    language === 'th' ? 'th-TH' : 'en-GB',
    {hour: '2-digit', minute: '2-digit', hour12: false},
  ).format(now);
  document.querySelector('#clockDate').textContent = new Intl.DateTimeFormat(
    language === 'th' ? 'th-TH' : 'en-GB',
    {weekday: 'short', day: 'numeric', month: 'short', year: 'numeric'},
  ).format(now);
}

function resetImage() {
  stopCamera();
  if (image.src.startsWith('blob:')) URL.revokeObjectURL(image.src);
  input.value = '';
  selectedFile = null;
  selectedInputSource = 'file';
  selectedCaptureHasFundusOptics = false;
  image.removeAttribute('src');
  frame.hidden = true;
  dropzone.hidden = false;
  analyzeButton.disabled = true;
  checkResult.hidden = true;
  emptyResult.hidden = false;
  document.querySelector('#modelOutput').hidden = true;
  document.querySelector('#previewNotice').hidden = false;
  document.querySelector('#cameraQualificationNotice').hidden = true;
  document.querySelector('#originalCompareImage').removeAttribute('src');
  document.querySelector('#gradcamCompareImage').removeAttribute('src');
}

function setCameraStatus(thaiText, englishText) {
  cameraStatus.dataset.th = thaiText;
  cameraStatus.dataset.en = englishText;
  cameraStatus.textContent = language === 'th' ? thaiText : englishText;
}

function cameraErrorMessage(error) {
  const messages = {
    NotAllowedError: ['ไม่ได้รับสิทธิ์ใช้กล้อง กรุณาอนุญาตในตั้งค่าเว็บไซต์แล้วลองใหม่', 'Camera permission was denied. Allow it in site settings and try again.'],
    NotFoundError: ['ไม่พบกล้องที่ใช้งานได้บนอุปกรณ์นี้', 'No available camera was found on this device.'],
    NotReadableError: ['กล้องอาจถูกใช้งานโดยแอปอื่น กรุณาปิดแอปนั้นแล้วลองใหม่', 'The camera may be in use by another app. Close it and try again.'],
    OverconstrainedError: ['กล้องไม่รองรับการตั้งค่าที่ขอ กรุณาลองสลับกล้อง', 'The camera does not support the requested settings. Try switching cameras.'],
  };
  return messages[error.name] || ['เปิดกล้องไม่สำเร็จ กรุณาตรวจสิทธิ์และลองใหม่', 'Could not start the camera. Check permission and try again.'];
}

function stopCamera(hidePanel = true) {
  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
  }
  cameraVideo.srcObject = null;
  capturePhotoButton.disabled = true;
  if (hidePanel) cameraPanel.hidden = true;
  if (hidePanel && !selectedFile) dropzone.hidden = false;
}

async function startCamera(resetEquipmentChoice = true) {
  if (resetEquipmentChoice) fundusEquipmentCheck.checked = false;
  cameraPanel.hidden = false;
  dropzone.hidden = true;
  capturePhotoButton.disabled = true;
  if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
    setCameraStatus(
      'เบราว์เซอร์นี้เปิดกล้องไม่ได้ ต้องใช้ HTTPS หรือ localhost และเบราว์เซอร์ที่รองรับ',
      'Camera access requires HTTPS or localhost and a supported browser.',
    );
    return;
  }
  stopCamera(false);
  setCameraStatus('กำลังขอสิทธิ์ใช้กล้อง…', 'Requesting camera permission…');
  try {
    // Standards: https://www.w3.org/TR/mediacapture-streams/#dom-mediadevices-getusermedia
    // Secure-context guidance: https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: {ideal: cameraFacingMode},
        width: {ideal: 1920},
        height: {ideal: 1080},
      },
      audio: false,
    });
    cameraVideo.srcObject = cameraStream;
    await cameraVideo.play();
    capturePhotoButton.disabled = false;
    setCameraStatus(
      cameraFacingMode === 'environment' ? 'กล้องหลังพร้อม · ภาพยังอยู่บนอุปกรณ์' : 'กล้องหน้าพร้อม · ภาพยังอยู่บนอุปกรณ์',
      cameraFacingMode === 'environment' ? 'Rear camera ready · frame remains on device' : 'Front camera ready · frame remains on device',
    );
  } catch (error) {
    stopCamera(false);
    const [thaiText, englishText] = cameraErrorMessage(error);
    setCameraStatus(thaiText, englishText);
  }
}

async function switchCamera() {
  cameraFacingMode = cameraFacingMode === 'environment' ? 'user' : 'environment';
  await startCamera(false);
}

function captureCameraFrame() {
  if (!cameraStream || cameraVideo.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) return;
  const sourceWidth = cameraVideo.videoWidth;
  const sourceHeight = cameraVideo.videoHeight;
  const maximumEdge = 1920;
  const scale = Math.min(1, maximumEdge / Math.max(sourceWidth, sourceHeight));
  cameraCanvas.width = Math.round(sourceWidth * scale);
  cameraCanvas.height = Math.round(sourceHeight * scale);
  const context = cameraCanvas.getContext('2d', {alpha: false});
  context.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);
  capturePhotoButton.disabled = true;
  cameraCanvas.toBlob((blob) => {
    if (!blob) {
      capturePhotoButton.disabled = false;
      setCameraStatus('สร้างภาพไม่สำเร็จ กรุณาลองถ่ายใหม่', 'Could not create the image. Try again.');
      return;
    }
    const capturedFile = new File([blob], `retinova-capture-${Date.now()}.jpg`, {type: 'image/jpeg'});
    selectedInputSource = 'camera';
    selectedCaptureHasFundusOptics = fundusEquipmentCheck.checked;
    stopCamera();
    selectFile(capturedFile);
  }, 'image/jpeg', 0.92);
}

function selectFile(file) {
  if (!file) return;
  const validType = ['image/jpeg', 'image/png'].includes(file.type);
  if (!validType || file.size > 10 * 1024 * 1024) {
    alert(language === 'th' ? 'รองรับเฉพาะ JPG/PNG ขนาดไม่เกิน 10 MB' : 'Use a JPG/PNG file no larger than 10 MB.');
    resetImage();
    return;
  }
  if (image.src.startsWith('blob:')) URL.revokeObjectURL(image.src);
  selectedFile = file;
  image.src = URL.createObjectURL(file);
  image.onload = () => {
    frame.hidden = false;
    dropzone.hidden = true;
    analyzeButton.disabled = false;
  };
  image.onerror = resetImage;
}

function checkReadiness() {
  if (!selectedFile || !image.naturalWidth) return;
  emptyResult.hidden = true;
  checkResult.hidden = false;
  fileCheck.textContent = `${selectedFile.type.replace('image/', '').toUpperCase()} · ${(selectedFile.size / 1024 / 1024).toFixed(2)} MB`;
  resolutionCheck.textContent = `${image.naturalWidth} × ${image.naturalHeight} px`;
  const cameraOutsideModelScope = selectedInputSource === 'camera' && !selectedCaptureHasFundusOptics;
  document.querySelector('#cameraQualificationNotice').hidden = !cameraOutsideModelScope;
  if (cameraOutsideModelScope) return;
  if (localModelReady) runLocalInference();
  else if (localAuthRequired && !teamAuthenticated) {
    alert(language === 'th' ? 'การใช้โมเดลจริงต้องเข้าสู่ระบบทีมก่อน' : 'Team Login is required to use the real model.');
  }
}

function fileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error('file read failed'));
    reader.readAsDataURL(file);
  });
}

async function runLocalInference() {
  const buttonLabel = analyzeButton.textContent;
  analyzeButton.disabled = true;
  analyzeButton.textContent = language === 'th' ? 'กำลังประมวลผลโมเดลจริง…' : 'Running the real model…';
  try {
    const response = await fetch('/predict', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({image: await fileAsDataUrl(selectedFile)}),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'inference failed');
    renderModelResult(result);
  } catch (error) {
    alert((language === 'th' ? 'โมเดลในเครื่องทำงานไม่สำเร็จ: ' : 'Local model failed: ') + error.message);
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.textContent = buttonLabel;
  }
}

function renderModelResult(result) {
  const modelOutput = document.querySelector('#modelOutput');
  const translatedClass = classNames[result.prediction];
  document.querySelector('#modelPrediction').textContent = translatedClass?.[language === 'th' ? 0 : 1] || result.prediction;
  document.querySelector('#modelProbability').textContent = `${(result.probability * 100).toFixed(1)}%`;
  document.querySelector('#originalCompareImage').src = image.src;
  document.querySelector('#gradcamCompareImage').src = result.gradcam_data_url;
  comparisonSlider.value = '50';
  comparisonOverlay.style.clipPath = 'inset(0 0 0 50%)';
  const list = document.querySelector('#probabilityList');
  list.replaceChildren();
  Object.entries(result.probabilities)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .forEach(([name, value]) => {
      const item = document.createElement('li');
      item.textContent = `${name} · ${(value * 100).toFixed(1)}%`;
      list.append(item);
    });
  const provenance = result.provenance;
  const inferenceText = Number.isFinite(result.inference_ms) ? ` · ${result.inference_ms} ms` : '';
  document.querySelector('#modelProvenance').textContent = `${provenance.architecture} · ${provenance.target_class} · ${provenance.target_layer} · ${provenance.model_revision.slice(0, 8)}${inferenceText}`;
  document.querySelector('#previewNotice').hidden = true;
  modelOutput.hidden = false;
  sessionHistory.unshift({
    timestamp: Date.now(),
    prediction: result.prediction,
    probability: result.probability,
    architecture: provenance.architecture,
    modelRevision: provenance.model_revision.slice(0, 8),
    inferenceMs: result.inference_ms,
  });
  sessionHistory.splice(MAX_SESSION_RESULTS);
  renderSessionHistory();
}

function renderSessionHistory() {
  const list = document.querySelector('#historyList');
  const empty = document.querySelector('#historyEmpty');
  document.querySelector('#historyCount').textContent = String(sessionHistory.length);
  list.replaceChildren();
  sessionHistory.forEach((record) => {
    const item = document.createElement('li');
    const heading = document.createElement('div');
    const classLabel = classNames[record.prediction]?.[language === 'th' ? 0 : 1] || record.prediction;
    const title = document.createElement('strong');
    title.textContent = classLabel;
    const probability = document.createElement('span');
    probability.textContent = `${(record.probability * 100).toFixed(1)}%`;
    heading.append(title, probability);
    const metadata = document.createElement('p');
    const time = new Intl.DateTimeFormat(language === 'th' ? 'th-TH' : 'en-GB', {hour: '2-digit', minute: '2-digit', second: '2-digit'}).format(record.timestamp);
    const duration = Number.isFinite(record.inferenceMs) ? ` · ${record.inferenceMs} ms` : '';
    metadata.textContent = `${time} · ${record.architecture} · ${record.modelRevision}${duration}`;
    const boundary = document.createElement('small');
    boundary.textContent = language === 'th' ? 'ความน่าจะเป็นของโมเดล · ไม่ใช่คะแนนสุขภาพ' : 'Model probability · not a health score';
    item.append(heading, metadata, boundary);
    list.append(item);
  });
  empty.hidden = sessionHistory.length > 0;
  list.hidden = sessionHistory.length === 0;
}

function setLocalModelUi() {
  if (localModelReady) {
    analyzeButton.textContent = language === 'th' ? 'วิเคราะห์ด้วยโมเดลจริงในเครื่อง' : 'Analyze with local model';
    const modeChip = document.querySelector('#modeChip');
    modeChip.textContent = language === 'th' ? 'เชื่อมต่อโมเดลวิจัยในเครื่อง' : 'Local research model connected';
    modeChip.classList.add('success');
  }
}

async function detectLocalModel() {
  if (!['127.0.0.1', 'localhost'].includes(location.hostname)) return;
  try {
    const response = await fetch('/health', {cache: 'no-store', credentials: 'same-origin'});
    const status = await response.json();
    const isModelServer = response.ok && status.mode === 'local-research-model';
    if (!isModelServer) {
      localModelReady = false;
      localAuthRequired = false;
      teamLoginButton.disabled = true;
      teamLoginStatus.textContent = language === 'th'
        ? 'Team Login ใช้งานได้เมื่อเปิดด้วย local model server เท่านั้น'
        : 'Team Login is available only through the local model server.';
      return;
    }
    localAuthRequired = status.auth_mode === 'team-passcode';
    teamAuthenticated = Boolean(status.authenticated);
    localModelReady = !localAuthRequired || teamAuthenticated;
    teamLoginButton.disabled = !localAuthRequired;
    if (localAuthRequired) {
      teamLoginStatus.textContent = teamAuthenticated
        ? (language === 'th' ? 'เซสชันทีมนี้ยืนยันแล้ว' : 'This team session is authenticated.')
        : (language === 'th' ? 'local server พร้อมรับรหัสผ่านทีม' : 'The local server is ready for Team Login.');
    } else {
      teamLoginStatus.textContent = language === 'th'
        ? 'local server นี้ไม่ได้ตั้งรหัสผ่านทีม — ใช้โหมดผู้เยี่ยมชมได้'
        : 'This local server has no team passcode; guest mode can use it.';
    }
    setLocalModelUi();
  } catch (_error) {
    localModelReady = false;
    localAuthRequired = false;
  }
}

async function loginTeam(event) {
  event.preventDefault();
  teamLoginButton.disabled = true;
  teamLoginStatus.textContent = language === 'th' ? 'กำลังตรวจสอบ…' : 'Checking…';
  try {
    const response = await fetch('/session', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({passcode: teamPasscode.value}),
    });
    const result = await response.json();
    teamPasscode.value = '';
    if (!response.ok) throw new Error(result.error || 'login failed');
    teamAuthenticated = true;
    localModelReady = true;
    setLocalModelUi();
    enterApp('team');
  } catch (error) {
    teamLoginStatus.textContent = language === 'th' ? `เข้าสู่ระบบไม่สำเร็จ: ${error.message}` : `Login failed: ${error.message}`;
    teamLoginButton.disabled = !localAuthRequired;
    teamPasscode.focus();
  }
}

function searchDestination(query) {
  const normalized = query.trim().toLowerCase();
  if (/วิเคราะห์|analy|upload|ภาพ/.test(normalized)) return 'analyze';
  if (/ล่าสุด|ประวัติ|session|history/.test(normalized)) return 'history';
  if (/ดวงตา|จอประสาท|retina|eye|โรค/.test(normalized)) return 'eye-health';
  if (/หลักฐาน|โมเดล|metric|evidence|f1|grad/.test(normalized)) return 'evidence';
  return 'home';
}

document.querySelectorAll('[data-view]').forEach((button) => {
  button.addEventListener('click', () => showView(button.dataset.view));
});
document.querySelectorAll('[data-welcome-language]').forEach((button) => {
  button.addEventListener('click', () => applyLanguage(button.dataset.welcomeLanguage));
});
document.querySelector('#guestButton').addEventListener('click', () => enterApp('guest'));
document.querySelector('#sessionButton').addEventListener('click', leaveSession);
document.querySelector('#clearHistoryButton').addEventListener('click', () => {
  sessionHistory.splice(0, sessionHistory.length);
  renderSessionHistory();
});
document.querySelector('#openCameraButton').addEventListener('click', () => startCamera());
document.querySelector('#switchCameraButton').addEventListener('click', switchCamera);
document.querySelector('#closeCameraButton').addEventListener('click', () => stopCamera());
capturePhotoButton.addEventListener('click', captureCameraFrame);
teamLoginForm.addEventListener('submit', loginTeam);
comparisonSlider.addEventListener('input', () => {
  comparisonOverlay.style.clipPath = `inset(0 0 0 ${comparisonSlider.value}%)`;
});
input.addEventListener('change', () => {
  selectedInputSource = 'file';
  selectedCaptureHasFundusOptics = false;
  selectFile(input.files[0]);
});
removeButton.addEventListener('click', resetImage);
analyzeButton.addEventListener('click', checkReadiness);
langButton.addEventListener('click', () => applyLanguage(language === 'th' ? 'en' : 'th'));
searchForm.addEventListener('submit', (event) => {
  event.preventDefault();
  showView(searchDestination(searchInput.value));
  searchInput.blur();
});

['dragenter', 'dragover'].forEach((eventName) => dropzone.addEventListener(eventName, (event) => {
  event.preventDefault();
  dropzone.classList.add('drag');
}));
['dragleave', 'drop'].forEach((eventName) => dropzone.addEventListener(eventName, (event) => {
  event.preventDefault();
  dropzone.classList.remove('drag');
}));
dropzone.addEventListener('drop', (event) => {
  selectedInputSource = 'file';
  selectedCaptureHasFundusOptics = false;
  selectFile(event.dataTransfer.files[0]);
});
document.addEventListener('visibilitychange', () => {
  if (document.hidden) stopCamera();
});
window.addEventListener('pagehide', () => stopCamera());

applyLanguage('th');
updateClock();
setInterval(updateClock, 30_000);
detectLocalModel();
