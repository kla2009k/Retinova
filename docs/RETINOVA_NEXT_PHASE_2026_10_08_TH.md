# Retinova — ผลตรวจและแผนพัฒนาต่อ (8 ตุลาคม 2569)

## ภาพรวมที่ตรวจได้จริง

Retinova เป็นเว็บต้นแบบสำหรับภาพถ่ายจอประสาทตา **fundus** ไม่ใช่ภาพตาจากกล้องโทรศัพท์เปล่า ๆ งานปัจจุบันมีโมเดล EfficientNet-B0 จำแนก 8 ป้ายกำกับแบบเลือกหนึ่งป้าย, ไฟล์ ONNX ประมาณ 16 MB, และแผนที่อิทธิพลของคลาส (CAM) จากโมเดลเดียวกัน ไม่ใช่ segmentation หรือแผนที่รอยโรค

- **E1 — ชุดทดสอบเดิม:** `artifacts/evaluation_efficientnet_b0_v1.json` และ `docs/EVALUATION_BASELINE_V1.md` ระบุ test 957 ภาพจาก 503 ผู้ป่วย, macro F1 0.581 (95% CI 0.525–0.622), balanced accuracy 0.642 (95% CI 0.579–0.689), ผู้ป่วยซ้ำข้าม split = 0
- **E2 — โมเดลที่ใช้:** `models/efficientnet_b0_patient_grouped_v1/retinova_efficientnet_b0_cam.onnx` และ metadata ในโฟลเดอร์เดียวกัน; hash/checkpoint ต้นทางดูในเอกสารประเมิน
- **E3 — เว็บสาธารณะ:** `https://kla2009k.github.io/Retinova/` เปิดได้ แต่เป็นพรีวิวแบบ static; เว็บนี้ยังไม่ส่งภาพเข้าบริการโมเดลจริง
- **E4 — บริการ Render:** พบ service เดิมชื่อ `retinova` ในบัญชี Render ที่ URL จริง `https://retinova-f70k.onrender.com/health` (ไม่ใช่ `retinova.onrender.com`); endpoint นี้ตอบ HTTP 200 พร้อม `mode: cloud-research-model`, `auth_mode: team-passcode` ก่อน deploy รุ่นล่าสุด ยังต้องตรวจ login/inference หลัง deploy
- **E5 — Hugging Face:** การสร้าง Docker Space สำหรับ ONNX ถูกปฏิเสธ HTTP 402 ก่อนสร้าง Space เพราะบัญชีที่ใช้อยู่ต้องมีแพ็กเกจที่รองรับ compute Space; ไม่มีการอ้างว่าบริการนี้ deploy สำเร็จ
- **E6 — ชุดทดสอบโค้ด:** หลังปรับ contract ให้ตรงกับ UI สามภาษา มี 46 tests ผ่าน และ smoke inference ด้วยภาพสังเคราะห์ผ่าน; ภาพสังเคราะห์ไม่ใช่การทดสอบความแม่นทางคลินิก

## สิ่งที่พัฒนาในรอบนี้

1. เพิ่ม technical upload gate ฝั่ง ONNX: JPEG/PNG เท่านั้น, จำกัด 24 ล้านพิกเซล, ตรวจขนาดสั้นสุดและอัตราส่วนภาพ, ปฏิเสธภาพเกือบสีเดียวก่อน inference การตรวจนี้ตั้งใจจับไฟล์ผิดรูปแบบหรือภาพว่างชัดเจน **ไม่ใช่โมเดลตรวจคุณภาพ fundus**
2. เพิ่ม automated tests สำหรับภาพว่าง ภาพหลายสี และ GIF; ปรับ UI contract tests ให้รองรับภาษาจีนที่มีอยู่ก่อนแล้วโดยยังตรวจว่าไม่มีการเก็บภาพหรือรหัสผ่านใน browser storage
3. เตรียม `scripts/deploy_hf_space.py` สำหรับแพ็กเว็บ + ONNX + server ลง Docker Space พร้อม Team Login ที่เก็บรหัสเป็น secret ของ Space; ความพยายาม deploy ครั้งแรกติดข้อกำหนดบัญชีดัง E5
4. ปรับ README/model card ให้แยก public preview, local model, CAM และสถานะการเผยแพร่ checkpoint ให้ตรงกัน

## สิ่งที่ต้องทำต่อเพื่อให้ “ใช้จริง” มีน้ำหนัก

### A. กำหนดปัญหาทางคลินิกให้แคบลง

ODIR เดิมเป็นข้อมูลระดับผู้ป่วยและตาสองข้าง บางป้ายกำกับเกี่ยวกับ systemic disease; โมเดลปัจจุบันลดเป็น 1 ภาพ → 1 ใน 8 ป้าย จึงไม่ควรใช้ผลทำนายเป็นการวินิจฉัยโรคทั้งหมดพร้อมกัน งานรอบถัดไปควรเลือกโจทย์คัดกรองหนึ่งอย่าง เช่น **referable diabetic retinopathy** พร้อมนิยามระดับความรุนแรงและ reference standard จากผู้เชี่ยวชาญ แล้วฝึก/ประเมินโมเดลใหม่ให้ตรงกับคำถามนั้น อย่าแปลงคะแนน 8 คลาสเดิมเป็นค่าความเสี่ยงทางคลินิกโดยตรง

### B. ข้อมูลและการประเมิน

- ทำ data manifest ที่บันทึก dataset license, ผู้ป่วย/ตาข้าง/เวลา/กล้อง, แหล่งภาพ, label provenance, split และ hash โดยไม่เผยข้อมูลส่วนบุคคล
- แยก train/validation/test ตาม patient ID; ถ้ามีภาพหลายครั้งจากผู้ป่วยเดียวกันให้คงไว้ใน split เดียวกัน; เก็บ external-site set ที่ไม่ใช้ปรับโมเดล
- รายงาน confusion matrix, sensitivity ต่อโรคเป้าหมาย, specificity, 95% CI, calibration และจำนวนภาพที่ abstain; วัดแยกตามชนิดกล้อง/ความคมชัด/กลุ่มข้อมูลที่มีจริง
- วางแผนขนาดชุดทดสอบจากผลลัพธ์หลัก (เช่น sensitivity ของ referable DR) และจำนวนเคสบวก/ลบจริง ไม่ใช้สูตรสัดส่วนเพื่อกำหนดจำนวนภาพฝึกโมเดล
- ทำ learning curve ของชุดฝึกเพื่อพิสูจน์ว่าการเพิ่มภาพช่วยจริงหรือไม่ พร้อมตรวจ label quality และ duplicate

### C. ทางผ่านความพร้อมของภาพ

Technical gate ปัจจุบันเป็นเพียง baseline ต้องเพิ่มและประเมิน **fundus-vs-non-fundus**, ungradable, blur, exposure, field-of-view, และภาพผิดโดเมนด้วยชุดที่ติดป้ายโดยผู้เชี่ยวชาญ บันทึก false rejection/false acceptance ก่อนบังคับใช้ เกณฑ์นี้ควรคืนผล “ตรวจไม่ได้/ต้องถ่ายใหม่” แทนการฝืนทำนายคลาส

### D. โมเดลและ UI

- Calibration และ abstention threshold ต้องจูนบน validation เท่านั้น; อย่าใช้ test set เดิมปรับต่อ
- ป้าย “model probability” บนเว็บต้องไม่ถูกสื่อว่าเป็นโอกาสเกิดโรคจริงจนกว่าจะวัด calibration
- CAM เป็น attribution ไม่ใช่ตำแหน่งรอยโรค; ถ้าต้องการ localization ให้เก็บ lesion annotations และวัด localization แยกต่างหาก
- แสดง workflow ชัดเจน: อัปโหลดภาพ fundus → ผ่าน quality gate → ผลคัดกรอง + uncertainty → คำแนะนำให้ผู้เชี่ยวชาญทบทวน → ส่งออกรายงานที่บอก provenance
- ตรวจ desktop/mobile, keyboard navigation, ภาษาไทย/อังกฤษ/จีน และข้อความในโหมด guest/team ให้ตรงกับ endpoint จริง

### E. การเปิดใช้เว็บ

GitHub Pages เป็นพรีวิวหน้าเว็บเท่านั้น; เว็บและโมเดลจริงอยู่บน Render ที่ `https://retinova-f70k.onrender.com/` พร้อม Team Login โค้ดสำหรับ Docker Space ถูกเตรียมแล้ว แต่สถานะบัญชี HF ปัจจุบันยังสร้าง compute Space ใหม่ไม่ได้ หลัง deploy รุ่นล่าสุดต้องตรวจ health check, login, inference จริง และ CAM ใน browser ก่อนส่งลิงก์ให้กรรมการ

## สิ่งที่นำเสนอได้ขณะนี้

สาธิตเว็บพรีวิว, โครงงานและผลทดสอบภายในที่แยกผู้ป่วย, ONNX inference และ CAM ในเครื่อง; Render มีบริการออนไลน์พร้อม Team Login แต่การทดสอบ end-to-end ด้วยรหัสทีมยังต้องตรวจเพิ่ม ส่วนที่ยังเป็นงานวิจัยต่อคือ external validation, quality model, calibration และ clinical workflow ห้ามเรียกคะแนน macro F1 ว่า “accuracy 94%” หรืออ้างว่า CAM เป็นการแบ่งรอยโรค
