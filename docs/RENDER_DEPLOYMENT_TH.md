# คู่มือ Deploy Retinova บน Render สำหรับงานแข่ง 3 วัน

อัปเดตราคาและข้อกำหนดล่าสุด: 18 สิงหาคม 2026

## สรุปก่อนกดจ่าย

- ข้อความ `Blueprint file render.yaml not found on main branch` หมายถึง repository ยังไม่มีไฟล์ Blueprint ที่ root ไม่ได้หมายความว่าต้องซื้อแพ็กเกจก่อน
- Hobby workspace มีค่ารายเดือน $0 แต่ instance ที่รันโมเดลมีค่า compute แยกต่างหาก
- Starter ราคา $7/เดือน ให้ RAM 512 MB และ 0.5 CPU
- Standard ราคา $25/เดือน ให้ RAM 2 GB และ 1 CPU
- Render คิดค่า paid compute ตามเวลาที่ instance ทำงานจริงโดย prorate ถึงระดับวินาที
- ถ้าเปิด Standard ต่อเนื่อง 72 ชั่วโมง ค่า compute โดยประมาณอยู่ราว $2.42–$2.50 ตามจำนวนวันของเดือน ไม่ใช่ $25 เต็มเดือน ทั้งนี้ยังไม่รวมการใช้งานเกินโควตา bandwidth หรือ pipeline

Retinova เลือก **Standard** เพราะการวัดบนเครื่องพัฒนาหลัง inference + Grad-CAM พบ process RSS ประมาณ 740 MB เมื่อใช้ PyTorch build ที่ติดตั้งอยู่ จึงไม่ควรเสี่ยงกับ Starter/Free ที่มี RAM 512 MB แม้ CPU-only build บน Render อาจใช้ต่างกัน

แหล่งข้อมูลทางการ:

- Pricing: https://render.com/pricing
- Instance RAM/CPU: https://render.com/docs/compute-plans
- Billing แบบ prorated: https://render.com/docs/faq#what-does-render-bill-for
- Blueprint spec: https://render.com/docs/blueprint-spec
- Free-instance limitations: https://render.com/docs/free

## สิ่งที่ Blueprint นี้สร้าง

- Web Service ชื่อ `retinova`
- Region: Singapore
- Instance: Standard, 2 GB RAM, 1 CPU
- Python 3.14.3
- CPU-only PyTorch 2.11.0 และ torchvision 0.26.0
- Checkpoint: `models/efficientnet_b0_patient_grouped_v1/retinova_efficientnet_b0_best.pt`
- Health check: `/health`
- Auto deploy: ปิด
- `RETINOVA_TEAM_PASSCODE`: Render จะให้กรอกในหน้า Dashboard และค่าจะไม่อยู่ใน Git

## ขั้นตอนสร้างบริการ

1. เปิด `https://render.com/deploy?repo=https://github.com/kla2009k/Retinova`
2. กด Retry หลัง commit ที่มี `render.yaml` อยู่บน `main`
3. ตรวจว่ามีเพียงบริการเดียว ชื่อ `retinova`, region Singapore และ plan Standard
4. ตั้ง `RETINOVA_TEAM_PASSCODE` เป็นรหัสเฉพาะงานนี้อย่างน้อย 12 ตัวอักษร อย่าใช้รหัสเดียวกับอีเมลหรือ GitHub
5. ตรวจ Estimated cost ในหน้า Review แล้วจึงกด Deploy Blueprint
6. หลัง deploy สำเร็จ เปิด URL `https://<service-name>.onrender.com/health` ต้องได้ `status: ready` และ `mode: cloud-research-model`
7. เข้าเว็บ กรอกรหัส Team Login เลือกภาพ fundus ที่ถูกต้อง แล้วตรวจว่าได้ probability, provenance และ Grad-CAM จริง
8. ที่หน้า Blueprint Settings ตั้ง **Auto Sync = No** เพื่อให้การแก้ `render.yaml` ในอนาคตต้องผ่านการ review ด้วยมือก่อนเปลี่ยนค่าใช้จ่าย

## ความปลอดภัยและขอบเขตข้อมูล

- Cloud mode เริ่มทำงานไม่ได้ถ้าไม่ตั้ง Team Passcode
- Cookie เป็น `HttpOnly; Secure; SameSite=Strict`
- POST/DELETE ตรวจ same-origin เพื่อลด CSRF
- จำกัด request body และ login attempts
- ใช้ security headers รวม CSP, HSTS, frame blocking และ MIME sniffing protection
- ภาพถูกอ่านในหน่วยความจำเพื่อ inference และไม่ถูกเขียนลงไฟล์หรือฐานข้อมูล
- ผลไม่ใช่การวินิจฉัย และ Grad-CAM ไม่ใช่ขอบเขตรอยโรค
- กล้องมือถือเปล่าไม่ใช่ fundus camera; ต้องใช้อะแดปเตอร์/เลนส์ที่เหมาะสมและผ่าน quality gate

## ปิดหลังครบ 3 วัน

1. เก็บ URL หรือภาพหน้าจอที่ทีมต้องใช้ก่อน
2. Render Dashboard → service `retinova` → Settings → Delete Service
3. ยืนยันว่า service หายจากหน้า Services และตรวจ Billing → Usage ว่าไม่มี paid instance ทำงานต่อ
4. ลบรหัส Team Passcode ที่ทีมเคยแชร์และสร้างรหัสใหม่ถ้าจะเปิดรอบหน้า
5. ถ้าต้องการเก็บหน้าแนะนำฟรี ให้ใช้ GitHub Pages เดิมต่อไป; หน้า static ไม่รันโมเดลและไม่เสียค่า Standard compute

อย่าใช้ Maintenance Mode แทนการลบบริการเพื่อหยุดค่า compute เพราะ Maintenance Mode ยังปล่อย instance ทำงานอยู่
