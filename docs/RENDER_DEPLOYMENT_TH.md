# คู่มือ Deploy Retinova บน Render สำหรับงานแข่ง 3 วัน

อัปเดตราคาและข้อกำหนดล่าสุด: 18 สิงหาคม 2026

## สรุปการใช้งานแบบไม่เสียค่า compute

- ข้อความ `Blueprint file render.yaml not found on main branch` หมายถึง repository ยังไม่มีไฟล์ Blueprint ที่ root ไม่ได้หมายความว่าต้องซื้อแพ็กเกจก่อน
- Blueprint รุ่นนี้ใช้ Render Free และไม่ต้องติดตั้ง PyTorch/torchvision บนเซิร์ฟเวอร์
- ระบบใช้ ONNX Runtime กับ EfficientNet-B0 ขนาดประมาณ 16 MB และสร้าง CAM ในรอบ inference เดียวกัน
- Free instance มี RAM 512 MB และจะหยุดพักเมื่อไม่มีการใช้งาน จึงมีเวลารอเมื่อเปิดครั้งแรกหลังพัก
- หากใช้งานเกินโควตาหรือเปลี่ยนเป็น paid instance Render อาจคิดค่าใช้จ่ายตามแผนที่เลือก

รุ่น PyTorch เดิมใช้หน่วยความจำหลัง inference และ Grad-CAM ประมาณ 740 MB จึงเกินขอบเขต Free แต่รุ่น deploy ปัจจุบันส่งออกเป็น ONNX และใช้ class activation mapping (CAM) ซึ่งไม่ต้องใช้ autograd ทำให้ลดภาระหน่วยความจำอย่างมาก โดยยังตรวจเทียบ logits และ CAM กับโมเดลต้นฉบับทุกครั้งที่ export

แหล่งข้อมูลทางการ:

- Pricing: https://render.com/pricing
- Instance RAM/CPU: https://render.com/docs/compute-plans
- Billing แบบ prorated: https://render.com/docs/faq#what-does-render-bill-for
- Blueprint spec: https://render.com/docs/blueprint-spec
- Free-instance limitations: https://render.com/docs/free

## สิ่งที่ Blueprint นี้สร้าง

- Web Service ชื่อ `retinova`
- Region: Singapore
- Instance: Free, 512 MB RAM
- Python 3.14.3
- ONNX Runtime แบบ CPU โดยไม่มี PyTorch ใน production
- Model: `models/efficientnet_b0_patient_grouped_v1/retinova_efficientnet_b0_cam.onnx`
- Health check: `/health`
- Auto deploy: ปิด
- `RETINOVA_TEAM_PASSCODE`: Render จะให้กรอกในหน้า Dashboard และค่าจะไม่อยู่ใน Git

## ขั้นตอนสร้างบริการ

1. เปิด `https://render.com/deploy?repo=https://github.com/kla2009k/Retinova`
2. กด Retry หลัง commit ที่มี `render.yaml` อยู่บน `main`
3. ตรวจว่ามีเพียงบริการเดียว ชื่อ `retinova`, region Singapore และ plan Free
4. ตั้ง `RETINOVA_TEAM_PASSCODE` เป็นรหัสเฉพาะงานนี้อย่างน้อย 12 ตัวอักษร อย่าใช้รหัสเดียวกับอีเมลหรือ GitHub
5. ตรวจหน้า Review ว่าแสดง Free ก่อนกด Deploy Blueprint
6. หลัง deploy สำเร็จ เปิด URL `https://<service-name>.onrender.com/health` ต้องได้ `status: ready` และ `mode: cloud-research-model`
7. เข้าเว็บ กรอกรหัส Team Login เลือกภาพ fundus ที่ถูกต้อง แล้วตรวจว่าได้ probability, provenance และ CAM จริง
8. ที่หน้า Blueprint Settings ตั้ง **Auto Sync = No** เพื่อให้การแก้ `render.yaml` ในอนาคตต้องผ่านการ review ด้วยมือก่อนเปลี่ยนค่าใช้จ่าย

## ความปลอดภัยและขอบเขตข้อมูล

- Cloud mode เริ่มทำงานไม่ได้ถ้าไม่ตั้ง Team Passcode
- Cookie เป็น `HttpOnly; Secure; SameSite=Strict`
- POST/DELETE ตรวจ same-origin เพื่อลด CSRF
- จำกัด request body และ login attempts
- ใช้ security headers รวม CSP, HSTS, frame blocking และ MIME sniffing protection
- ภาพถูกอ่านในหน่วยความจำเพื่อ inference และไม่ถูกเขียนลงไฟล์หรือฐานข้อมูล
- ผลไม่ใช่การวินิจฉัย และ CAM ไม่ใช่ขอบเขตรอยโรคหรือหลักฐานว่าโมเดลทำนายถูก
- กล้องมือถือเปล่าไม่ใช่ fundus camera; ต้องใช้อะแดปเตอร์/เลนส์ที่เหมาะสมและผ่าน quality gate

## ปิดหลังครบ 3 วัน

1. เก็บ URL หรือภาพหน้าจอที่ทีมต้องใช้ก่อน
2. Render Dashboard → service `retinova` → Settings → Delete Service
3. ยืนยันว่า service หายจากหน้า Services และตรวจ Billing → Usage ว่าไม่มีบริการที่ไม่ต้องการทำงานต่อ
4. ลบรหัส Team Passcode ที่ทีมเคยแชร์และสร้างรหัสใหม่ถ้าจะเปิดรอบหน้า
5. ถ้าต้องการเก็บหน้าแนะนำฟรี ให้ใช้ GitHub Pages เดิมต่อไป; หน้า static ไม่รันโมเดล

หมายเหตุ: CAM ในรุ่น ONNX เป็น class-specific attribution จาก feature maps และน้ำหนัก classifier โดยตรง ส่วนโหมด PyTorch ในเครื่องยังรองรับ Grad-CAM เดิม เอกสารหรือสไลด์ต้องแยกชื่อสองวิธีนี้ให้ถูกต้อง
