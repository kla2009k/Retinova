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

const validViews = new Set(['home', 'analyze', 'history', 'eye-health', 'evidence', 'settings']);
const supportedLanguages = ['th', 'en', 'zh'];
const viewTitles = {
  home: ['หน้าแรก', 'Home', '首页'],
  analyze: ['วิเคราะห์ภาพ', 'Analyze', '图像分析'],
  history: ['ผลล่าสุด', 'Session results', '本次结果'],
  'eye-health': ['ความรู้ดวงตา', 'Eye health', '眼健康'],
  evidence: ['หลักฐานโมเดล', 'Evidence', '模型证据'],
  settings: ['ตั้งค่า', 'Settings', '设置'],
};
const classNames = {
  N: ['ปกติ', 'Normal', '正常'],
  D: ['เบาหวาน', 'Diabetes', '糖尿病相关'],
  G: ['ต้อหิน', 'Glaucoma', '青光眼'],
  C: ['ต้อกระจก', 'Cataract', '白内障'],
  A: ['จอประสาทตาเสื่อม', 'AMD', '年龄相关性黄斑变性'],
  H: ['ความดันโลหิต', 'Hypertension', '高血压相关'],
  M: ['สายตาสั้นผิดปกติ', 'Myopia', '病理性近视'],
  O: ['ความผิดปกติอื่น', 'Other', '其他异常'],
};

const zhTranslations = {
  'Open the live model · Team Login ↗': '打开在线模型 · 团队登录 ↗',
  'A fundus-image research prototype with measured evaluation and model attribution maps.': '眼底图像研究原型，展示实测评估和模型归因图。',
  'Compare the original with CAM (cloud) or Grad-CAM (local)': '比较原图与云端 CAM 或本地 Grad-CAM。',
  'Explore the preview, or use Team Login on the model server.': '浏览预览，或在模型服务器上使用团队登录。',
  'or · model server only': '或 · 仅限模型服务器',
  'Team Login is available on a model server with a team passcode.': '团队登录仅在配置团队密码的模型服务器上可用。',
  'GitHub Pages checks files in-browser; live inference is available through the Team Login model server.': 'GitHub Pages 只在浏览器中检查文件；真实推理需通过团队登录模型服务器。',
  'The GitHub Pages preview checks files only. Prediction and CAM/Grad-CAM require the model server.': 'GitHub Pages 仅检查文件；预测和 CAM/Grad-CAM 需要模型服务器。',
  'Research-model output': '研究模型输出',
  'Real inference requires the model server': '真实推理需要模型服务器',
  'Welcome': '欢迎',
  'Enter Retinova': '进入 Retinova',
  'Continue to the public demo, or use Team Login for a model running on this computer.': '继续进入公开演示，或使用团队登录连接本机模型。',
  'Continue as guest': '以访客身份继续',
  'Explore the UI, evidence, and file readiness': '浏览界面、模型证据与图像可用性检查',
  'Team login': '团队登录',
  'Team passcode': '团队密码',
  'or · local server only': '或 · 仅限本地服务器',
  'Open the local server with RETINOVA_TEAM_PASSCODE configured to enable this login.': '如需启用团队登录，请在本地服务器配置 RETINOVA_TEAM_PASSCODE。',
  'This local server has no team passcode; guest mode can use it.': '此本地服务器未设置团队密码，访客模式可直接使用。',
  'The server is ready for Team Login.': '服务器已准备接收团队登录。',
  'Home': '首页',
  'Analyze': '分析',
  'Session results': '本次结果',
  'Eye health': '眼健康',
  'Eye Health': '眼健康',
  'Measured evidence': '实测证据',
  'Settings': '设置',
  'Care for your eye health with Artificial Intelligence': '使用人工智能守护眼健康',
  'Check a fundus image instantly. With the local model connected, Retinova shows a screening result with traceable explanations.': '快速检查眼底图像。连接本地模型后，Retinova 将显示可追溯解释的筛查结果。',
  'Start eye analysis': '开始眼底分析',
  'Open analysis →': '打开分析 →',
  'Public demonstration ready': '公开演示已就绪',
  'Public preview mode': '公开预览模式',
  'Public website mode': '公开网站模式',
  'Analysis workspace': '分析工作区',
  'Retinal image analysis': '视网膜图像分析',
  'Drop an image here, or choose a file': '将图像拖到此处，或选择文件',
  'JPG/PNG up to 10 MB · Public Preview does not upload images': 'JPG/PNG，最大 10 MB · 公开预览不会上传图像',
  'Open live camera': '打开实时相机',
  'or choose a file below': '或在下方选择文件',
  'Image file': '图像文件',
  'Remove': '移除',
  'Check image readiness': '检查图像可用性',
  'Image details before analysis': '分析前的图像信息',
  'No analysis result yet': '尚无分析结果',
  'Upload an image to begin. No health score or fabricated finding is generated.': '请先上传图像。系统不会生成虚构的健康评分或检查结果。',
  'Readiness result': '可用性检查结果',
  'Supported image': '支持的图像',
  'Resolution': '分辨率',
  'Local research-model output': '本地研究模型输出',
  'Analysis result': '分析结果',
  'Model probability · not a clinical score': '模型概率 · 不是临床评分',
  'Original': '原图',
  'Slide to compare the original with CAM': '拖动滑块比较原图与 CAM',
  'CAM shows regions influencing the predicted class; it is not a lesion boundary.': 'CAM 显示影响预测类别的图像区域，并不代表病灶边界。',
  'Results this session': '本次会话结果',
  'Only real local-model results from this tab are shown; nothing is stored.': '仅显示此标签页中的真实本地模型结果，不会持久保存。',
  'No session results': '暂无本次结果',
  'Real result list': '真实结果列表',
  'Session-result trend': '本次结果趋势',
  'The chart uses only real local-model outputs and never draws a sample trend.': '图表仅使用真实本地模型输出，不绘制示例趋势。',
  'Fundus anatomy': '眼底结构',
  'Fundus images show the retina, vessels, macula, and optic disc—not the iris.': '眼底图像显示视网膜、血管、黄斑和视盘，而不是虹膜。',
  'Anatomy': '解剖结构',
  'Read urgent signs': '了解紧急症状',
  'Seek prompt care for sudden blurred vision, flashes, a rapid increase in floaters, severe eye pain, or vision loss.': '如突发视力模糊、闪光、飞蚊骤增、剧烈眼痛或视力丧失，请立即就医。',
  'Do not wait for a website result in an emergency': '紧急情况下不要等待网站结果',
  'System pipeline': '系统流程',
  'Receive': '接收',
  'Preprocess': '预处理',
  'Classify': '分类',
  'Validate': '验证',
  'AI Advice': 'AI 建议',
  'Model evidence and limitations': '模型证据与局限',
  'These figures come from a patient-grouped research baseline, not a clinical claim.': '这些数据来自按患者分组的研究基线，不构成临床声明。',
  'Patient-grouped test result: macro F1 0.581 (95% CI 0.525–0.622)': '按患者分组测试：宏平均 F1 0.581（95% CI 0.525–0.622）',
  'Test patients': '测试患者',
  'Eight research labels': '8 个研究类别',
  'Current decision': '当前模型选择',
  'Baseline method': '基线方法',
  'What remains unproven': '尚未验证的部分',
  'No external-site clinical validation': '尚无外部临床验证',
  'No approved quality rejection or probability calibration': '尚无经批准的质量拒绝机制或概率校准',
  'Not approved for public inference or clinical use': '未获准用于公开推理或临床用途',
  'Demonstration settings': '演示设置',
  'Review language, operating mode, and privacy boundaries before a judge tries the demo.': '请在评委试用前检查语言、运行模式与隐私边界。',
  'Language and display': '语言与显示',
  'Use the TH/EN button in the top bar. Content and safety warnings switch together.': '使用顶部的语言按钮，内容与安全警告会同步切换。',
  'Switch to ภาษาไทย': '切换至泰语',
  'Mode boundary': '运行模式边界',
  'Privacy': '隐私',
  'Public Preview does not upload or store images': '公开预览不会上传或保存图像',
  'History results remain only in this tab\'s memory': '历史结果仅保留在当前标签页内存中',
  'No fabricated patient records; images and passwords are not stored in the browser': '不生成虚构患者记录；浏览器不保存图像或密码',
  'NOT A DIAGNOSIS': '非医疗诊断',
  'Research screening output, not a diagnosis. CAM is not a lesion boundary.': '仅为研究筛查结果，不是诊断；CAM 不是病灶边界。',
  'Clear': '清除',
  'Close camera': '关闭相机',
  'Switch camera': '切换相机',
  'Capture': '拍照',
  'This capture uses fundus optics': '本次拍摄使用眼底成像光学附件',
  'A bare phone camera is not a fundus camera': '普通手机相机不是眼底相机',
  'Age-related macular degeneration': '年龄相关性黄斑变性',
  'An item is added only after a real local-model inference.': '仅在真实本地模型完成推理后才会新增记录。',
  'A retinal-fundus research prototype that shows measured evaluation, limitations, and real Grad-CAM from the local model.': '用于眼底图像筛查的研究原型，展示实测评估、模型局限以及本地模型生成的真实 Grad-CAM。',
  'Bare-phone external-eye photos are outside the model scope.': '普通手机拍摄的眼外观照片不在模型适用范围内。',
  'Cataract label': '白内障类别',
  'Check only when a fundus adapter/condensing lens is attached and the live view shows the circular retina, not the external eye. Otherwise, file checks remain available but model inference is blocked.': '仅在连接眼底适配器或聚光镜，且实时画面显示圆形眼底而非眼外观时勾选。否则仍可检查文件，但会阻止模型推理。',
  'Compare the original image with real Grad-CAM when using the local model': '使用本地模型时，可比较原图与真实 Grad-CAM',
  'Consult an ophthalmologist': '咨询眼科医生',
  'Continue with your image →': '继续使用您的图像 →',
  'Data boundary': '数据边界',
  'Demo image · not a patient result': '演示图像 · 非患者结果',
  'Diabetes-related findings': '糖尿病相关视网膜改变',
  'Educational image · not the user\'s image': '教学图像 · 非用户图像',
  'Fabricated health score': '虚构健康评分',
  'File': '文件',
  'file readiness': '文件可用性',
  'For urgent symptoms, do not wait for a website result.': '出现紧急症状时，请勿等待网站结果。',
  'Fundus image': '眼底图像',
  'GitHub Pages has no account system and receives no passwords. This is not a medical-record system.': 'GitHub Pages 没有账户系统，也不会接收密码。本系统不是医疗记录系统。',
  'Glaucoma label': '青光眼类别',
  'Hypertension recall 0.389 and Other recall 0.340 remain weak': '高血压类别召回率为 0.389，其他类别召回率为 0.340，表现仍然较弱',
  'Hypertension-related findings': '高血压相关视网膜改变',
  'Illustration only': '仅为示意图',
  'Image and derived-weight redistribution rights need confirmation': '图像及衍生模型权重的再分发权仍需确认',
  'Image input': '图像输入',
  'Images stored': '已保存图像',
  'Latest scan': '最近一次扫描',
  'No labelled target abnormality': '未发现数据标签定义的目标异常',
  'No local-model results yet': '尚无本地模型结果',
  'Not generated': '不生成',
  'Not stored in Public Preview': '公开预览模式下不保存',
  'ODIR is bilateral and multi-label; this baseline reduces it to a single-image label': 'ODIR 原始任务为双眼多标签数据，本基线将其简化为单图像单标签任务',
  'Only time, class, probability, model revision, and inference time are kept temporarily in page memory.': '页面内存仅临时保存时间、类别、概率、模型版本和推理耗时。',
  'Open evaluation report →': '打开评估报告 →',
  'Other labelled findings': '数据中标注的其他异常',
  'Pathological myopia label': '病理性近视类别',
  'Preview': '预览',
  'Public Preview checks the file in-browser; real inference runs only with the local server.': '公开预览仅在浏览器中检查文件属性；真实推理仅通过本地服务器运行。',
  'Ready': '就绪',
  'Real inference requires the local model server': '真实推理需要本地模型服务器',
  'REAL RESULTS ONLY': '仅显示真实结果',
  'Report limits': '报告局限',
  'Retinal imaging requires a suitable fundus adapter/condensing lens and a trained operator. A bare camera captures the external eye, which does not match the model\'s training data.': '视网膜成像需要合适的眼底适配器或聚光镜，并由受过训练的人员操作。普通相机只能拍摄眼外观，与模型训练数据不匹配。',
  'Retinova never enables the torch or flash automatically; do not aim a bright light close to the eye.': 'Retinova 不会自动开启补光灯或闪光灯；请勿将强光近距离照射眼睛。',
  'Review methods and limitations →': '查看方法与局限 →',
  'Sample': '示例',
  'Scan history': '扫描历史',
  'See the evidence before trusting an AI result': '在信任 AI 结果前先查看证据',
  'Source': '来源',
  'Storage': '存储',
  'The frame stays in this tab\'s memory. The camera stops when this panel closes, the page changes, or the tab is hidden.': '画面仅保留在当前标签页内存中；关闭面板、切换页面或隐藏标签页时，相机会停止。',
  'The illustration identifies the optic disc, macula, and vessels; it does not replace expert assessment.': '示意图用于识别视盘、黄斑和血管，不能替代专业人员评估。',
  'The public site checks file properties only. Prediction and Grad-CAM require the local model server.': '公开网站仅检查文件属性；预测和 Grad-CAM 需要本地模型服务器。',
  'The public site does not send images to a model or generate heatmaps, avoiding unvalidated medical output.': '公开网站不会把图像发送到模型，也不会生成热图，以避免输出未经验证的医疗结果。',
  'These details describe the image, not a patient record, and are not stored.': '这些信息仅描述图像，不属于患者病历，也不会被保存。',
  'This frame will not enter the model': '此画面不会进入模型',
  'This live-camera frame was captured without confirmed fundus optics. External-eye photos are outside the training domain, so only file properties are shown.': '该实时画面未确认使用眼底光学附件。眼外观照片不属于训练数据范围，因此仅显示文件属性。',
  'This tab only': '仅限当前标签页',
  'Traceable evidence': '可追溯证据',
  'Understand the input': '了解模型输入',
  'Upload or camera with fundus optics': '上传图像或使用配备眼底光学附件的相机',
  'Use the phone\'s rear camera': '使用手机后置相机',
  'Verified': '已验证',
  'Waiting for camera permission…': '正在等待相机权限…',
  'Search analysis, eye health, or evidence...': '搜索图像分析、眼健康或模型证据…',
};

const MAX_SESSION_RESULTS = 50;
const sessionHistory = [];
let selectedFile = null;
let language = 'th';
let localModelReady = false;
let localAuthRequired = false;
let teamAuthenticated = false;
let modelDeploymentMode = 'public';
let activeView = 'home';
let cameraStream = null;
let cameraFacingMode = 'environment';
let selectedInputSource = 'file';
let selectedCaptureHasFundusOptics = false;

function translated(element) {
  if (language === 'zh') return element.dataset.zh || zhTranslations[element.dataset.en] || element.dataset.en || element.textContent;
  return element.dataset[language] || element.textContent;
}

function languageIndex() {
  return supportedLanguages.indexOf(language);
}

function localize(thaiText, englishText, chineseText) {
  return language === 'th' ? thaiText : language === 'zh' ? (chineseText || englishText) : englishText;
}

function applyLanguage(nextLanguage) {
  language = supportedLanguages.includes(nextLanguage) ? nextLanguage : 'zh';
  localStorage.setItem('retinova-language', language);
  document.documentElement.lang = language;
  document.querySelectorAll('[data-th][data-en]').forEach((element) => {
    element.textContent = translated(element);
  });
  document.querySelectorAll('[data-th-placeholder][data-en-placeholder]').forEach((element) => {
    element.placeholder = language === 'zh'
      ? (element.dataset.zhPlaceholder || zhTranslations[element.dataset.enPlaceholder] || element.dataset.enPlaceholder)
      : element.dataset[`${language}Placeholder`];
  });
  document.querySelectorAll('[data-welcome-language]').forEach((button) => {
    button.classList.toggle('active', button.dataset.welcomeLanguage === language);
  });
  langButton.textContent = language === 'th' ? 'EN' : language === 'en' ? '中' : 'TH';
  document.title = `Retinova — ${viewTitles[activeView][languageIndex()]}`;
  updateClock();
  renderSessionHistory();
  detectLocalModel();
}

function showView(viewName, updateUrl = true) {
  const nextView = validViews.has(viewName) ? viewName : 'home';
  if (activeView === 'analyze' && nextView !== 'analyze') stopCamera();
  activeView = nextView;
  appShell.dataset.activeView = nextView;
  document.querySelectorAll('.app-view').forEach((view) => {
    view.hidden = view.dataset.page !== nextView;
  });
  document.querySelectorAll('.nav-item').forEach((button) => {
    const active = button.dataset.view === nextView;
    button.classList.toggle('active', active);
    if (active) button.setAttribute('aria-current', 'page');
    else button.removeAttribute('aria-current');
  });
  document.title = `Retinova — ${viewTitles[nextView][languageIndex()]}`;
  if (updateUrl) history.replaceState(null, '', `#${nextView}`);
  window.scrollTo({top: 0, behavior: 'auto'});
  mainContent.focus({preventScroll: true});
}

function enterApp(mode) {
  welcomeGate.hidden = true;
  appShell.hidden = false;
  const sessionButton = document.querySelector('#sessionButton');
  sessionButton.textContent = mode === 'team' ? 'ท' : 'ร';
  sessionButton.title = localize('ออกจากเซสชัน', 'Leave session', '退出会话');
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
    language === 'th' ? 'th-TH' : language === 'zh' ? 'zh-CN' : 'en-GB',
    {hour: '2-digit', minute: '2-digit', hour12: false},
  ).format(now);
  document.querySelector('#clockDate').textContent = new Intl.DateTimeFormat(
    language === 'th' ? 'th-TH' : language === 'zh' ? 'zh-CN' : 'en-GB',
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

function setCameraStatus(thaiText, englishText, chineseText = englishText) {
  cameraStatus.dataset.th = thaiText;
  cameraStatus.dataset.en = englishText;
  cameraStatus.dataset.zh = chineseText;
  cameraStatus.textContent = localize(thaiText, englishText, chineseText);
}

function cameraErrorMessage(error) {
  const messages = {
    NotAllowedError: ['ไม่ได้รับสิทธิ์ใช้กล้อง กรุณาอนุญาตในตั้งค่าเว็บไซต์แล้วลองใหม่', 'Camera permission was denied. Allow it in site settings and try again.', '相机权限被拒绝，请在网站设置中允许后重试。'],
    NotFoundError: ['ไม่พบกล้องที่ใช้งานได้บนอุปกรณ์นี้', 'No available camera was found on this device.', '此设备未找到可用相机。'],
    NotReadableError: ['กล้องอาจถูกใช้งานโดยแอปอื่น กรุณาปิดแอปนั้นแล้วลองใหม่', 'The camera may be in use by another app. Close it and try again.', '相机可能正被其他应用占用，请关闭该应用后重试。'],
    OverconstrainedError: ['กล้องไม่รองรับการตั้งค่าที่ขอ กรุณาลองสลับกล้อง', 'The camera does not support the requested settings. Try switching cameras.', '相机不支持所需设置，请尝试切换相机。'],
  };
  return messages[error.name] || ['เปิดกล้องไม่สำเร็จ กรุณาตรวจสิทธิ์และลองใหม่', 'Could not start the camera. Check permission and try again.', '无法启动相机，请检查权限后重试。'];
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
      '相机访问需要 HTTPS 或 localhost，并使用受支持的浏览器。',
    );
    return;
  }
  stopCamera(false);
  setCameraStatus('กำลังขอสิทธิ์ใช้กล้อง…', 'Requesting camera permission…', '正在请求相机权限…');
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
      cameraFacingMode === 'environment' ? '后置相机已就绪 · 画面保留在设备上' : '前置相机已就绪 · 画面保留在设备上',
    );
  } catch (error) {
    stopCamera(false);
    const [thaiText, englishText, chineseText] = cameraErrorMessage(error);
    setCameraStatus(thaiText, englishText, chineseText);
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
      setCameraStatus('สร้างภาพไม่สำเร็จ กรุณาลองถ่ายใหม่', 'Could not create the image. Try again.', '无法生成图像，请重新拍摄。');
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
    alert(localize('รองรับเฉพาะ JPG/PNG ขนาดไม่เกิน 10 MB', 'Use a JPG/PNG file no larger than 10 MB.', '仅支持不超过 10 MB 的 JPG/PNG 文件。'));
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
    alert(localize('การใช้โมเดลจริงต้องเข้าสู่ระบบทีมก่อน', 'Team Login is required to use the real model.', '使用真实模型前需要团队登录。'));
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
  analyzeButton.textContent = localize('กำลังประมวลผลโมเดลจริง…', 'Running the real model…', '正在运行真实模型…');
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
    alert(localize('โมเดลในเครื่องทำงานไม่สำเร็จ: ', 'Local model failed: ', '本地模型运行失败：') + error.message);
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.textContent = buttonLabel;
  }
}

function renderModelResult(result) {
  const modelOutput = document.querySelector('#modelOutput');
  const translatedClass = classNames[result.prediction];
  document.querySelector('#modelPrediction').textContent = translatedClass?.[languageIndex()] || result.prediction;
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
    const classLabel = classNames[record.prediction]?.[languageIndex()] || record.prediction;
    const title = document.createElement('strong');
    title.textContent = classLabel;
    const probability = document.createElement('span');
    probability.textContent = `${(record.probability * 100).toFixed(1)}%`;
    heading.append(title, probability);
    const metadata = document.createElement('p');
    const time = new Intl.DateTimeFormat(language === 'th' ? 'th-TH' : language === 'zh' ? 'zh-CN' : 'en-GB', {hour: '2-digit', minute: '2-digit', second: '2-digit'}).format(record.timestamp);
    const duration = Number.isFinite(record.inferenceMs) ? ` · ${record.inferenceMs} ms` : '';
    metadata.textContent = `${time} · ${record.architecture} · ${record.modelRevision}${duration}`;
    const boundary = document.createElement('small');
    boundary.textContent = localize('ความน่าจะเป็นของโมเดล · ไม่ใช่คะแนนสุขภาพ', 'Model probability · not a health score', '模型概率 · 不是健康评分');
    item.append(heading, metadata, boundary);
    list.append(item);
  });
  empty.hidden = sessionHistory.length > 0;
  list.hidden = sessionHistory.length === 0;
  renderSessionChart();
}

function renderSessionChart() {
  const chart = document.querySelector('#sessionChart');
  const emptyCopy = document.querySelector('#chartEmptyCopy');
  const probabilities = sessionHistory.map((record) => record.probability).slice().reverse();
  chart.replaceChildren();
  chart.hidden = probabilities.length === 0;
  emptyCopy.hidden = probabilities.length > 0;
  if (!probabilities.length) return;
  const points = probabilities.map((probability, index) => {
    const x = probabilities.length === 1 ? 400 : 40 + (index / (probabilities.length - 1)) * 720;
    const y = 140 - Math.max(0, Math.min(1, probability)) * 110;
    return {x, y};
  });
  const namespace = 'http://www.w3.org/2000/svg';
  if (points.length > 1) {
    const line = document.createElementNS(namespace, 'polyline');
    line.setAttribute('points', points.map(({x, y}) => `${x},${y}`).join(' '));
    line.setAttribute('class', 'session-chart-line');
    chart.append(line);
  }
  points.forEach(({x, y}) => {
    const dot = document.createElementNS(namespace, 'circle');
    dot.setAttribute('cx', x);
    dot.setAttribute('cy', y);
    dot.setAttribute('r', 5);
    dot.setAttribute('class', 'session-chart-dot');
    chart.append(dot);
  });
}

function setLocalModelUi() {
  if (localModelReady) {
    const isCloud = modelDeploymentMode === 'cloud';
    analyzeButton.textContent = localize(
      isCloud ? 'วิเคราะห์ด้วยโมเดลจริงบนเซิร์ฟเวอร์' : 'วิเคราะห์ด้วยโมเดลจริงในเครื่อง',
      isCloud ? 'Analyze with cloud model' : 'Analyze with local model',
      isCloud ? '使用云端真实模型分析' : '使用本地真实模型分析',
    );
    const modeChip = document.querySelector('#modeChip');
    modeChip.textContent = localize(
      isCloud ? 'เชื่อมต่อโมเดลวิจัยบนเซิร์ฟเวอร์' : 'เชื่อมต่อโมเดลวิจัยในเครื่อง',
      isCloud ? 'Cloud research model connected' : 'Local research model connected',
      isCloud ? '已连接云端研究模型' : '已连接本地研究模型',
    );
    modeChip.classList.add('success');
  }
}

async function detectLocalModel() {
  try {
    const response = await fetch('/health', {cache: 'no-store', credentials: 'same-origin'});
    const status = await response.json();
    const modelModes = new Set(['local-research-model', 'cloud-research-model']);
    const isModelServer = response.ok && modelModes.has(status.mode);
    if (!isModelServer) {
      modelDeploymentMode = 'public';
      localModelReady = false;
      localAuthRequired = false;
      teamLoginButton.disabled = true;
      teamLoginStatus.textContent = localize(
        'Team Login ใช้งานได้เมื่อเปิดด้วย local model server เท่านั้น',
        'Team Login is available only through the local model server.',
        '团队登录仅可通过本地模型服务器使用。',
      );
      return;
    }
    modelDeploymentMode = status.mode === 'cloud-research-model' ? 'cloud' : 'local';
    localAuthRequired = status.auth_mode === 'team-passcode';
    teamAuthenticated = Boolean(status.authenticated);
    localModelReady = !localAuthRequired || teamAuthenticated;
    teamLoginButton.disabled = !localAuthRequired;
    if (localAuthRequired) {
      teamLoginStatus.textContent = teamAuthenticated
        ? localize('เซสชันทีมนี้ยืนยันแล้ว', 'This team session is authenticated.', '此团队会话已通过验证。')
        : localize('เซิร์ฟเวอร์พร้อมรับรหัสผ่านทีม', 'The server is ready for Team Login.', '服务器已准备接收团队密码。');
    } else {
      teamLoginStatus.textContent = localize(
        'local server นี้ไม่ได้ตั้งรหัสผ่านทีม — ใช้โหมดผู้เยี่ยมชมได้',
        'This local server has no team passcode; guest mode can use it.',
        '此本地服务器未设置团队密码，访客模式可直接使用。',
      );
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
  teamLoginStatus.textContent = localize('กำลังตรวจสอบ…', 'Checking…', '正在检查…');
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
    teamLoginStatus.textContent = localize(`เข้าสู่ระบบไม่สำเร็จ: ${error.message}`, `Login failed: ${error.message}`, `登录失败：${error.message}`);
    teamLoginButton.disabled = !localAuthRequired;
    teamPasscode.focus();
  }
}

function searchDestination(query) {
  const normalized = query.trim().toLowerCase();
  if (/วิเคราะห์|analy|upload|ภาพ|分析|上传|图像/.test(normalized)) return 'analyze';
  if (/ล่าสุด|ประวัติ|session|history|结果|历史/.test(normalized)) return 'history';
  if (/ดวงตา|จอประสาท|retina|eye|โรค|眼|视网膜|疾病/.test(normalized)) return 'eye-health';
  if (/หลักฐาน|โมเดล|metric|evidence|f1|grad|证据|模型|指标/.test(normalized)) return 'evidence';
  if (/ตั้งค่า|setting|ภาษา|language|privacy|ส่วนตัว|设置|语言|隐私/.test(normalized)) return 'settings';
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
langButton.addEventListener('click', () => applyLanguage(supportedLanguages[(languageIndex() + 1) % supportedLanguages.length]));
document.querySelector('#settingsLanguageButton').addEventListener('click', () => applyLanguage(supportedLanguages[(languageIndex() + 1) % supportedLanguages.length]));
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

applyLanguage(localStorage.getItem('retinova-language') || 'zh');
updateClock();
setInterval(updateClock, 30_000);
detectLocalModel();
