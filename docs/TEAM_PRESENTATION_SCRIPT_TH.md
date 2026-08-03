# สคริปต์ทีม Retinova: ตั้งแต่เทรนโมเดลจนถึงวิธีใช้

เอกสารนี้เขียนให้พูดได้จริงประมาณ 5–7 นาที ตัวเลขทั้งหมดมาจาก pipeline ที่รันใน repository ณ 1 สิงหาคม 2026 ไม่ใช่ตัวเลขการตลาด

## สคริปต์หลัก

### 1. Retinova คืออะไร

> Retinova เป็นต้นแบบ AI เพื่อการวิจัยสำหรับวิเคราะห์ภาพถ่ายจอประสาทตาหรือ retinal fundus photograph ภาพชนิดนี้เห็นเส้นเลือด จุดภาพชัด และขั้วประสาทตา เราไม่ได้สแกนม่านตาเพื่อระบุตัวบุคคล และระบบยังไม่ใช่อุปกรณ์วินิจฉัย จุดประสงค์คือศึกษาการคัดกรองและแสดงให้ผู้ใช้เห็นทั้งผลของโมเดลและข้อจำกัดอย่างโปร่งใส

### 2. ใช้อะไรเทรนโมเดล

> เราเขียน training pipeline ด้วย Python และ PyTorch ใช้โมเดลจาก torchvision ที่ pretrain บน ImageNet แล้ว fine-tune กับภาพ fundus ของงานเรา ข้อมูลตั้งต้นเป็น ODIR-derived dataset จำนวน 6,392 ภาพ แบ่งเป็น 8 กลุ่ม ได้แก่ Normal, Diabetes, Glaucoma, Cataract, AMD, Hypertension, Myopia และ Other

> ODIR ต้นฉบับเป็นข้อมูลผู้ป่วยสองตาและอาจมีหลาย label แต่งานรุ่นนี้ลดรูปเป็นการจำแนกภาพเดี่ยวหนึ่ง label เราจึงระบุข้อจำกัดนี้ไว้ใน model card และไม่อ้างว่าแก้โจทย์ต้นฉบับได้ครบทั้งหมด

### 3. แบ่งข้อมูลอย่างไร

> จุดสำคัญคือเราไม่สุ่มแยกทีละภาพ เพราะตาซ้ายและตาขวาของคนเดียวกันอาจรั่วไปอยู่ทั้ง train และ test ทำให้คะแนนสูงเกินจริง เราใช้ StratifiedGroupKFold โดย group ตาม patient ID ได้ train 4,477 ภาพจาก 2,352 คน, validation 958 ภาพจาก 503 คน และ test 957 ภาพจาก 503 คน ตรวจแล้ว patient overlap เท่ากับศูนย์

### 4. เตรียมภาพและเทรนอย่างไร

> ตอน train เราเปิดภาพเป็น RGB, ทำ random resized crop, horizontal flip, หมุนเล็กน้อย และปรับสีแบบจำกัด จากนั้น normalize ด้วยค่า ImageNet ส่วน validation และ test ใช้ resize ด้านสั้นเป็น 256 แล้ว center crop 224 คงที่ EfficientNet ใช้ bicubic interpolation ตาม preprocessing ของ pretrained weights

> เราใช้ weighted cross-entropy เพื่อชดเชยจำนวนภาพแต่ละคลาสที่ไม่เท่ากัน ใช้ AdamW learning rate 0.0003, weight decay 0.0001 และ cosine annealing ตั้ง seed 42 เพื่อให้ทำซ้ำได้ เทรนไม่เกิน 8 epochs และเก็บ checkpoint ที่ validation macro F1 สูงที่สุด ไม่เลือกจาก accuracy และไม่ใช้ test set จูนโมเดล

### 5. ทำไมเลือก EfficientNet-B0

> เราเทียบ ResNet-18 กับ EfficientNet-B0 บน manifest และเงื่อนไขหลักชุดเดียวกัน ResNet ได้ validation macro F1 0.552 ส่วน EfficientNet ได้ 0.577 เราจึงเลือก EfficientNet ก่อนดูผล test หลังล็อกโมเดลแล้ว EfficientNet ได้ test macro F1 0.581 และ balanced accuracy 0.642 ส่วน ResNet ได้ 0.562 และ 0.617 ตามลำดับ

> ช่วงความเชื่อมั่น 95% จากการ bootstrap ตามผู้ป่วย 500 รอบของ EfficientNet คือ 0.525 ถึง 0.622 สำหรับ macro F1 และ 0.579 ถึง 0.689 สำหรับ balanced accuracy ช่วงยังค่อนข้างกว้างและทับกับโมเดลเปรียบเทียบ จึงยังสรุปไม่ได้ว่าเหนือกว่าในทุกประชากร

### 6. จุดอ่อนของโมเดล

> Recall รายคลาสไม่เท่ากัน Cataract ได้ 0.909 และ Myopia ได้ 0.943 แต่ Hypertension ได้เพียง 0.389 และ Other ได้ 0.340 ตัวเลขนี้บอกว่าระบบยังพลาดภาพในสองกลุ่มดังกล่าวมาก จึงไม่เหมาะกับการใช้งานผู้ป่วยจริง และยังต้องมี external validation, calibration, quality gate และจักษุแพทย์ตรวจข้อผิดพลาด

### 7. Grad-CAM จริงทำงานอย่างไร

> Grad-CAM ของเราไม่ได้วาดวงสีด้วย CSS ระบบนำ gradient ของคะแนนคลาสเป้าหมายย้อนกลับไปยัง feature map ชั้น features.8 ของ EfficientNet-B0 แล้วคำนวณ heatmap จาก checkpoint เดียวกับที่ทำนาย ทุกผลเก็บ architecture, target class, target layer และ model revision ไว้เป็น provenance

> เรามี unit test ว่า heatmap อยู่ในช่วงศูนย์ถึงหนึ่ง ขนาดตรงกับ input และเปลี่ยนเมื่อเปลี่ยน target class แต่ Grad-CAM แปลได้เพียงบริเวณที่มีอิทธิพลต่อคะแนน ไม่ใช่ขอบเขตรอยโรคและไม่ยืนยันว่าคำตอบถูก ตัวอย่าง glaucoma หนึ่งภาพ heatmap สนใจ optic disc อย่างสมเหตุผล แต่โมเดลยังทำนายผิดเป็น Normal นี่คือเหตุผลที่เราไม่ใช้ภาพสวย ๆ แทนการวัดผลจริง

### 8. เว็บทำงานอย่างไร

> GitHub Pages ที่แชร์ด้วย QR เริ่มจากหน้า Welcome ผู้ใช้กดเข้าแบบ Guest ได้ หน้า Team Login จะทำงานจริงเฉพาะ local server ที่ทีมตั้ง passcode ไว้เท่านั้น ตัว public preview ไม่มีระบบบัญชี ไม่มี API key, checkpoint หรือการส่งภาพไปวิเคราะห์ ผู้ใช้เลือกภาพเพื่อทดสอบชนิดไฟล์ ขนาด และความละเอียดใน browser เท่านั้น เราตั้งใจไม่เปิดผลโรคสาธารณะ เพราะ checkpoint และสิทธิ์การเผยแพร่ข้อมูลยังต้องตรวจสอบ

> สำหรับเดโมโมเดลจริง เรารัน Python server เฉพาะ localhost หน้าเว็บจะตรวจพบ endpoint health และถ้าตั้ง RETINOVA_TEAM_PASSCODE ไว้ ผู้ใช้ต้องล็อกอินก่อนเรียก predict รหัสผ่านตรวจที่ server และ session cookie เป็น HttpOnly ภาพถูกส่งให้ checkpoint ในเครื่อง ระบบคืน probability ทั้ง 8 คลาสพร้อม Grad-CAM และ provenance หน้าเว็บมี slider เทียบภาพต้นฉบับกับ Grad-CAM จริง และเพิ่มรายการผลจริงเฉพาะในหน่วยความจำของแท็บโดยไม่เก็บภาพ ชื่อคน หรือชื่อไฟล์ เซิร์ฟเวอร์ bind ที่ 127.0.0.1 และไม่เขียนภาพลง log

### 9. สรุป

> สิ่งที่เราทำสำเร็จไม่ใช่แค่หน้าเว็บ แต่เป็นสายงานที่ตรวจสอบย้อนกลับได้ตั้งแต่ patient-grouped split, training config, checkpoint selection, test report, confidence interval ไปจนถึง Grad-CAM จากโมเดลเดียวกัน อย่างไรก็ตามผลยังเป็น research baseline เราเลือกความซื่อสัตย์ของหลักฐานก่อนการอ้างว่าวินิจฉัยได้ และขั้นต่อไปคือแก้จุดอ่อน H/O, เพิ่มการปฏิเสธภาพคุณภาพต่ำ, ทดสอบข้อมูลโรงพยาบาลอื่น และให้จักษุแพทย์ประเมิน

## วิธีเดโม

### Public preview

1. เปิด `https://kla2009k.github.io/Retinova/` หรือสแกน `docs/retinova-qr.png`
2. กด “เข้าชมแบบผู้เยี่ยมชม” และอธิบายว่า Team Login ไม่รับรหัสบน GitHub Pages
3. เลือกภาพ JPG/PNG ไม่เกิน 10 MB
4. กดตรวจความพร้อมของภาพ
5. เปิดหน้าผลล่าสุดและชี้ว่าเป็นศูนย์ เพราะ public preview ไม่สร้างผลโมเดลหรือประวัติผู้ป่วย
6. อธิบายว่าภาพอยู่ใน browser และหน้านี้ตั้งใจไม่คืนผลโรค

### Local real-model mode

```powershell
$env:RETINOVA_TEAM_PASSCODE="รหัสยาวแบบสุ่มสำหรับการเดโม"
python -m scripts.serve_retinova `
  --checkpoint models/efficientnet_b0_patient_grouped_v1/retinova_efficientnet_b0_best.pt
```

จากนั้นเปิด `http://127.0.0.1:8000`, ใส่รหัสผ่านทีม, เลือกภาพ fundus และกดวิเคราะห์ด้วยโมเดลจริง ควรชี้ให้เห็น probability ทุกคลาส, slider เปรียบเทียบ Grad-CAM จริง, architecture, target class, target layer, model revision, เวลา inference และคำเตือน จากนั้นเปิด “ผลล่าสุด” เพื่อแสดงว่ารายการมาจากผลที่เพิ่งรันจริงและหายเมื่อ refresh

**คำอธิบายสิ่งที่ไม่ใช้จากเว็บรุ่นเก่า:** เราไม่ใช้เลข 94.2% เพราะไม่มี test report รองรับ, ไม่สร้างชื่อหรือประวัติผู้ป่วยจำลอง, ไม่สร้าง Eye Health Score ที่ไม่มีนิยามการตรวจสอบ และไม่วาด heatmap ด้วย CSS สิ่งทดแทนคือ metrics จาก patient-grouped test, session result จริง, model probability ที่ติดป้ายข้อจำกัด และ Grad-CAM จาก checkpoint เดียวกับ prediction

## คำถามกรรมการที่น่าจะเจอ

**ถาม: ตัวเว็บใช้อะไร train model?**

ตอบ: ตัวเว็บไม่ได้เทรนเอง เราเทรนออฟไลน์ด้วย Python, PyTorch และ torchvision บน GPU แล้วโหลด checkpoint ที่เลือกจาก validation macro F1 เข้า local inference server ส่วน GitHub Pages เป็น frontend static เท่านั้น

**ถาม: ทำไมไม่ใช้ accuracy?**

ตอบ: คลาสไม่สมดุลมาก Accuracy อาจดูดีเพราะคลาส Normal มีเยอะ เราจึงใช้ macro F1 ที่ให้น้ำหนักแต่ละคลาสเท่ากัน และ balanced accuracy ที่เฉลี่ย recall ทุกคลาส

**ถาม: 0.581 หรือ 58.1% คือความแม่นยำใช่ไหม?**

ตอบ: ไม่ใช่ นั่นคือ macro F1 ซึ่งรวม precision และ recall ของทุกคลาสแล้วเฉลี่ยเท่ากัน ต้องเรียกชื่อ metric ให้ถูก และต้องพูดคู่กับช่วงความเชื่อมั่นกับผลรายคลาส

**ถาม: Grad-CAM พิสูจน์ว่า AI มองรอยโรคถูกจุดหรือไม่?**

ตอบ: ไม่พิสูจน์ Grad-CAM เป็น attribution ของคะแนนโมเดล ไม่ใช่ segmentation หรือเหตุผลเชิงสาเหตุ เราใช้เพื่อช่วยตรวจ shortcut และต้องให้ผู้เชี่ยวชาญทบทวน

**ถาม: ใช้กับคนไข้ได้หรือยัง?**

ตอบ: ยังไม่ได้ เพราะยังไม่มี external clinical validation, calibration, quality rejection, regulatory approval และ clinical workflow ที่ผ่านการทดสอบ

**ถาม: ทำไมไม่ทำม่านตา?**

ตอบ: เป้าหมายคือความผิดปกติที่เห็นจากจอประสาทตา จึงต้องใช้ภาพ fundus ม่านตาเป็นโครงสร้างด้านหน้าของตาและมักเกี่ยวข้องกับงานยืนยันตัวบุคคล เป็นคนละชนิดภาพและคนละโจทย์

**ถาม: ทำไมไม่อัปโหลด checkpoint ขึ้น GitHub?**

ตอบ: repository เปิดเผยโค้ดและหลักฐานที่ทำซ้ำได้ แต่ยังเก็บภาพและ weights ไว้ในเครื่องจนกว่าจะยืนยันสิทธิ์การเผยแพร่ ODIR และ derived weights ชัดเจน

## ตัวเลขที่ต้องจำ

| รายการ | ค่า |
|---|---:|
| ภาพทั้งหมด | 6,392 |
| Train / validation / test | 4,477 / 958 / 957 |
| ผู้ป่วย test | 503 |
| Patient overlap | 0 |
| โมเดลที่เลือก | EfficientNet-B0 |
| Validation macro F1 | 0.577 |
| Test macro F1 | 0.581 (95% CI 0.525–0.622) |
| Test balanced accuracy | 0.642 (95% CI 0.579–0.689) |
| Grad-CAM target layer | `features.8` |

อย่าพูดว่า “แม่นยำ 58.1%” และอย่าพูดว่า “วินิจฉัยได้” ให้พูดชื่อ metric, ขอบเขตข้อมูล และสถานะ research baseline ทุกครั้ง
