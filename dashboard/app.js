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

let selectedFile = null;
let language = 'th';
let localModelReady = false;

const classNames = {
  N: ['ปกติ', 'Normal'], D: ['เบาหวาน', 'Diabetes'], G: ['ต้อหิน', 'Glaucoma'],
  C: ['ต้อกระจก', 'Cataract'], A: ['จอประสาทตาเสื่อม', 'AMD'],
  H: ['ความดันโลหิต', 'Hypertension'], M: ['สายตาสั้นผิดปกติ', 'Myopia'],
  O: ['ความผิดปกติอื่น', 'Other'],
};

function translated(element) {
  return element.dataset[language] || element.textContent;
}

function applyLanguage(nextLanguage) {
  language = nextLanguage;
  document.documentElement.lang = language;
  document.querySelectorAll('[data-th][data-en]').forEach((element) => {
    element.textContent = translated(element);
  });
  langButton.textContent = language === 'th' ? 'EN' : 'TH';
}

function resetImage() {
  if (image.src.startsWith('blob:')) URL.revokeObjectURL(image.src);
  input.value = '';
  selectedFile = null;
  image.removeAttribute('src');
  frame.hidden = true;
  dropzone.hidden = false;
  analyzeButton.disabled = true;
  checkResult.hidden = true;
  emptyResult.hidden = false;
}

function selectFile(file) {
  if (!file) return;
  const validType = ['image/jpeg', 'image/png'].includes(file.type);
  if (!validType || file.size > 10 * 1024 * 1024) {
    alert(language === 'th' ? 'รองรับเฉพาะ JPG/PNG ขนาดไม่เกิน 10 MB' : 'Use a JPG/PNG file no larger than 10 MB.');
    resetImage();
    return;
  }
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
  if (localModelReady) runLocalInference();
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
      method: 'POST', headers: {'Content-Type': 'application/json'},
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
  document.querySelector('#modelPrediction').textContent = classNames[result.prediction]?.[language === 'th' ? 0 : 1] || result.prediction;
  document.querySelector('#modelProbability').textContent = `${(result.probability * 100).toFixed(1)}%`;
  document.querySelector('#gradcamImage').src = result.gradcam_data_url;
  const list = document.querySelector('#probabilityList');
  list.replaceChildren();
  Object.entries(result.probabilities).sort((a, b) => b[1] - a[1]).slice(0, 3).forEach(([name, value]) => {
    const item = document.createElement('li');
    item.textContent = `${name} · ${(value * 100).toFixed(1)}%`;
    list.append(item);
  });
  const provenance = result.provenance;
  document.querySelector('#modelProvenance').textContent = `${provenance.architecture} · ${provenance.target_class} · ${provenance.target_layer} · ${provenance.model_revision.slice(0, 8)}`;
  modelOutput.hidden = false;
}

async function detectLocalModel() {
  if (!['127.0.0.1', 'localhost'].includes(location.hostname)) return;
  try {
    const response = await fetch('/health', {cache: 'no-store'});
    const status = await response.json();
    localModelReady = response.ok && status.mode === 'local-research-model';
    if (localModelReady) analyzeButton.textContent = language === 'th' ? 'วิเคราะห์ด้วยโมเดลจริงในเครื่อง' : 'Analyze with local model';
  } catch (_error) {
    localModelReady = false;
  }
}

input.addEventListener('change', () => selectFile(input.files[0]));
removeButton.addEventListener('click', resetImage);
analyzeButton.addEventListener('click', checkReadiness);
langButton.addEventListener('click', () => applyLanguage(language === 'th' ? 'en' : 'th'));

['dragenter', 'dragover'].forEach((eventName) => dropzone.addEventListener(eventName, (event) => {
  event.preventDefault();
  dropzone.classList.add('drag');
}));
['dragleave', 'drop'].forEach((eventName) => dropzone.addEventListener(eventName, (event) => {
  event.preventDefault();
  dropzone.classList.remove('drag');
}));
dropzone.addEventListener('drop', (event) => selectFile(event.dataTransfer.files[0]));

applyLanguage('th');
detectLocalModel();
