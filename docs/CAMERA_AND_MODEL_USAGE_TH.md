# คู่มือกล้องสดและสถานะโมเดล Retinova

เอกสารนี้อธิบายว่าเว็บทำอะไรได้จริง ณ 3 สิงหาคม 2026 วิธีใช้กล้องโทรศัพท์ และเหตุผลที่ภาพตาจากกล้องมือถือทั่วไปไม่ควรถูกส่งเข้าโมเดล fundus

## คำตอบตรง ๆ: ตอนนี้เว็บใช้โมเดลได้หรือยัง

**ได้เฉพาะ Local Model mode** และ **ยังใช้โมเดลบน GitHub Pages ไม่ได้**

| โหมด | เปิดกล้องสด | ตรวจไฟล์ | Prediction | Grad-CAM | ภาพออกจากอุปกรณ์หรือไม่ |
|---|---:|---:|---:|---:|---|
| GitHub Pages / Guest | ได้ | ได้ | ไม่ได้ | ไม่ได้ | ไม่ออกจาก browser |
| Local server แบบ open-local | ได้ | ได้ | ได้ | ได้ | ส่งจาก browser ไป `127.0.0.1` ในเครื่องเดียวกัน |
| Local server + Team Login | ได้ | ได้ | ได้หลังล็อกอิน | ได้หลังล็อกอิน | ส่งไป `127.0.0.1` ในเครื่องเดียวกัน |
| โทรศัพท์เปิด GitHub Pages แต่โมเดลรันบนโน้ตบุ๊ก | ได้เฉพาะกล้อง/ตรวจไฟล์ | ได้ | ไม่ได้ | ไม่ได้ | โทรศัพท์เข้าถึง loopback ของโน้ตบุ๊กไม่ได้ |

Public Preview ตั้งใจไม่มี checkpoint และ inference API การวางโมเดลไว้ใน JavaScript จะทำให้ weights ถูกดาวน์โหลดไปยังผู้ใช้ทุกคนและยังไม่แก้ปัญหาสิทธิ์เผยแพร่ การตรวจสอบทางคลินิก หรือการควบคุมเวอร์ชัน

## วิธีใช้กล้องสดบนโทรศัพท์

1. เปิด `https://kla2009k.github.io/Retinova/` ผ่าน HTTPS
2. กด “เข้าชมแบบผู้เยี่ยมชม”
3. เปิด “วิเคราะห์ภาพ” แล้วกด “เปิดกล้องสด”
4. อนุญาตสิทธิ์กล้องเมื่อ browser ถาม ระบบขอกล้องหลังเป็นค่าเริ่มต้น
5. กด “สลับกล้อง” หากเลือกกล้องผิดตัว
6. ถ้าถ่ายผ่านอะแดปเตอร์ fundus/condensing lens และภาพสดเห็นจอประสาทตาเป็นวง ให้ติ๊ก “ภาพนี้ใช้ชุดถ่าย fundus”
7. กด “ถ่ายภาพ” ภาพจะถูกย่อไม่เกินด้านยาว 1,920 px และแปลงเป็น JPEG ใน memory
8. กดตรวจความพร้อมของภาพ บน public site ระบบจะแสดงชนิดไฟล์ ขนาด และความละเอียดเท่านั้น

กล้องจะหยุดและคืน hardware ทันทีเมื่อปิดหน้ากล้อง เปลี่ยนหน้า ซ่อนแท็บ ออกจาก session หรือออกจากหน้าเว็บ Retinova ไม่ร้องขอเสียงและไม่เปิดไฟช่วยถ่ายอัตโนมัติ

## ขอบเขตทางกายภาพของภาพ

โมเดล Retinova เทรนกับ **retinal fundus photographs** ซึ่งเห็น optic disc, macula และ retinal vessels ไม่ใช่ภาพเปลือกตา กระจกตา รูม่านตา หรือม่านตาจากกล้องโทรศัพท์เปล่า

งานด้าน smartphone fundus photography ใช้อุปกรณ์เสริม เช่น smartphone adapter ร่วมกับ slit lamp หรือ condensing lens งานหนึ่งในปี 2025 ประเมินอะแดปเตอร์แม่เหล็กที่ใช้กับ slit lamp/condensing lens ส่วนบทความด้านเทคนิคระบุข้อจำกัดเรื่อง reflection, field of view, pupil size, alignment และ image quality ดังนั้น “เปิดกล้องโทรศัพท์แล้วจ่อดวงตา” ไม่ได้ทำให้ได้ภาพชนิดเดียวกับข้อมูลฝึกโดยอัตโนมัติ

เพื่อป้องกันผลที่ดูเหมือนจริงแต่ไม่มีความหมาย:

- ถ้าถ่ายจากกล้องสดโดยไม่ยืนยันอุปกรณ์ fundus เว็บจะตรวจไฟล์ได้ แต่จะไม่เรียก local model แม้โมเดลเชื่อมต่ออยู่
- การติ๊กยืนยันไม่ได้พิสูจน์คุณภาพภาพ เป็นเพียง safety gate ขั้นต้น
- ระบบยังไม่มี automated fundus-quality classifier จึงต้องมีผู้ปฏิบัติงานตรวจภาพ
- ห้ามใช้ prediction จากรุ่นนี้เพื่อตัดสินใจรักษาหรือแทนจักษุแพทย์

## เส้นทางข้อมูลของภาพจากกล้อง

```text
กล้องอุปกรณ์
  → MediaStream ใน browser (video only, no audio)
  → Canvas เฉพาะตอนกดถ่าย
  → JPEG Blob/File ใน memory
  → validation ชนิด/ขนาด/ความละเอียดเดิม
  ├─ Public Preview: จบที่ browser
  └─ Local Model + ผ่าน safety gate: POST /predict ไป 127.0.0.1
       → EfficientNet-B0 checkpoint
       → probabilities + real Grad-CAM + provenance
       → ไม่เขียนภาพลง history หรือ log
```

ไม่มี `localStorage`, `sessionStorage`, IndexedDB หรือฐานข้อมูลภาพใน flow นี้ หน้า “ผลล่าสุด” เก็บเฉพาะเวลา คลาส probability รุ่นโมเดล และเวลา inference ใน memory ไม่เกิน 50 รายการ

## วิธีรันโมเดลจริง

```powershell
$env:RETINOVA_TEAM_PASSCODE="ตั้งรหัสสุ่มยาวอย่างน้อย12ตัวอักษร"
python -m scripts.serve_retinova `
  --checkpoint models/efficientnet_b0_patient_grouped_v1/retinova_efficientnet_b0_best.pt
```

เปิด `http://127.0.0.1:8000` บนอุปกรณ์เครื่องเดียวกับ server แล้ว Team Login เมื่อสำเร็จหน้าเว็บจะเปลี่ยนเป็น “เชื่อมต่อโมเดลวิจัยในเครื่อง”

Local server bind เฉพาะ `127.0.0.1` โดยตั้งใจ จึงไม่ควรแก้เป็น `0.0.0.0` เพียงเพื่อให้โทรศัพท์ใน Wi-Fi เรียกได้ เพราะจะขยาย attack surface และยังไม่มี TLS/device authorization หากต้องการเดโมจากโทรศัพท์ถึงโมเดลบนโน้ตบุ๊ก ควรสร้าง secure gateway ที่มี HTTPS, short-lived authorization, size/rate limits และลบ payload หลัง inference ก่อน

## สิ่งที่ควรทำต่อ

### ระยะที่ทำได้ทันที

- ทดสอบกล้องจริงบน Android Chrome และ iPhone Safari หลายรุ่น
- เพิ่ม automated fundus/non-fundus quality gate ก่อนโมเดลโรค
- เพิ่ม blur, exposure, field-of-view และ optic-disc visibility checks
- ทำ capture protocol สำหรับชนิดอะแดปเตอร์ที่ทีมเลือก
- เก็บ device/browser metadata แบบไม่ระบุตัวบุคคลเฉพาะงานทดลองที่มี consent

### ก่อนเปิดโมเดลให้โทรศัพท์ใช้ออนไลน์

- ยืนยันสิทธิ์เผยแพร่ checkpoint และข้อมูล
- ทำ external validation กับภาพจากอะแดปเตอร์/กล้องเป้าหมายจริง
- ประเมิน domain shift แยกตามอุปกรณ์
- ทำ probability calibration และ rejection policy
- ใช้ HTTPS backend, production identity, audit log และ retention policy
- ผ่าน ethics/privacy/security review และผู้เชี่ยวชาญทางจักษุ

### ก่อนเรียกว่าใช้กับผู้ป่วยได้

- prospective clinical study
- predefined intended use และ referral pathway
- human-factors/usability testing
- failure-mode analysis
- regulatory assessment ตามพื้นที่ใช้งาน
- clinical monitoring และ incident response

## แหล่งอ้างอิง

- W3C Media Capture and Streams: https://www.w3.org/TR/mediacapture-streams/
- MDN `getUserMedia()` และ secure context: https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
- Design of a new 3D printed all-in-one magnetic smartphone adapter for fundus and anterior segment imaging (PMID 38644806): https://pubmed.ncbi.nlm.nih.gov/38644806/
- Technical and optical aspects of smartphone-based fundus photography (PMID 35043271): https://pubmed.ncbi.nlm.nih.gov/35043271/
