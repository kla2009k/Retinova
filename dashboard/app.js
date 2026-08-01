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
