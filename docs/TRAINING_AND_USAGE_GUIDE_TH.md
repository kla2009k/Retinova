# คู่มือ Retinova: ตั้งแต่ข้อมูล การเทรน จนถึงวิธีใช้

เอกสารนี้เป็นสคริปต์อ้างอิงสำหรับทีมและเป็นข้อกำหนดทางเทคนิคของโปรเจกต์ ข้อความสำคัญที่สุดคือ Retinova วิเคราะห์ **ภาพถ่ายจอประสาทตา (retinal fundus photograph)** ไม่ใช่ภาพม่านตา (iris) และยังเป็นต้นแบบวิจัย ไม่ใช่อุปกรณ์วินิจฉัยโรค

## 1. คำตอบสั้นสำหรับพูดบนเวที

> Retinova ใช้ภาพ fundus ที่มองเห็นจอประสาทตา เส้นเลือด จุดภาพชัด และขั้วประสาทตา ข้อมูลตั้งต้นมาจากชุด ODIR เราจัดปัญหาเป็นการจำแนกภาพเดี่ยว 8 กลุ่ม แยก train/validation/test ตามรหัสผู้ป่วยเพื่อไม่ให้ตาซ้ายกับตาขวาของคนเดียวกันรั่วข้ามชุด จากนั้น fine-tune โมเดลภาพใน PyTorch ประเมินด้วย macro F1, balanced accuracy, per-class sensitivity/specificity และ confusion matrix ส่วน Grad-CAM จะคำนวณจาก feature map ของโมเดลและคลาสเดียวกับผลทำนาย จึงเป็นคำอธิบายของโมเดลจริง ไม่ใช่สีที่วาดทับภาพ ระบบมีไว้ช่วยคัดกรองและส่งต่อ ไม่แทนจักษุแพทย์

## 2. ระบบใช้ข้อมูลอะไรเทรน

ข้อมูลในเครื่องเป็น ODIR-derived dataset โดยตาราง `full_df.csv` มี 6,392 แถวต่อภาพและ label แบบ one-hot เพียงหนึ่งกลุ่มต่อภาพ:

| กลุ่ม | รหัส | จำนวนภาพ |
|---|---|---:|
| ปกติ | N | 2,873 |
| เบาหวาน | D | 1,608 |
| ความผิดปกติอื่น | O | 708 |
| ต้อกระจก | C | 293 |
| ต้อหิน | G | 284 |
| จอประสาทตาเสื่อมตามอายุ | A | 266 |
| สายตาสั้นผิดปกติ | M | 232 |
| ความดันโลหิต | H | 128 |

ODIR ต้นฉบับถูกออกแบบเป็นข้อมูลผู้ป่วยที่มีภาพตาซ้ายและขวาและสามารถมีหลาย label ได้ งาน Retinova รุ่นปัจจุบันลดรูปเป็น **single-image, single-label, 8-class research task** จึงต้องพูดขอบเขตนี้ตรง ๆ ไม่อ้างว่าแก้โจทย์ bilateral multi-label ต้นฉบับครบถ้วน ดูคำอธิบายชุดข้อมูลและงาน benchmark ได้ที่ [ODIR paper](https://arxiv.org/abs/2102.07978)

## 3. ทำไมต้องแบ่งข้อมูลตามผู้ป่วย

ถ้าสุ่มแยกทีละภาพ ตาซ้ายอาจอยู่ train แต่ตาขวาของคนเดียวกันอยู่ test ลักษณะกล้อง แสง อายุ และกายวิภาคของคนเดียวกันทำให้คะแนนดูสูงเกินจริง การตรวจเบื้องต้นพบผู้ป่วย 545 รายที่มีทั้งสองตาใน subset เดิม จึงห้ามใช้ split เดิมเป็นหลักฐานประสิทธิภาพ

กระบวนการที่ถูกต้อง:

1. สกัด `patient_id` จาก metadata/ชื่อไฟล์ก่อนแตะ label
2. ใช้ grouped stratified split เป็น train 70%, validation 15%, test 15%
3. ล็อก random seed และบันทึกรายชื่อ patient ID ของแต่ละ split
4. fit preprocessing, class weights และ threshold จาก train/validation เท่านั้น
5. เปิด test set เพียงครั้งเดียวหลังล็อกโมเดล
6. ตรวจว่า patient ID intersection ระหว่างทุก split เป็นศูนย์ด้วย unit test

## 4. การเตรียมภาพ

ขั้นมาตรฐานที่แนะนำ:

1. อ่านภาพและบังคับ RGB
2. ตรวจว่าเป็นภาพที่เปิดอ่านได้และมีขนาดขั้นต่ำตาม config
3. crop ขอบดำโดยไม่ตัด retinal field of view
4. resize เป็น 224×224 สำหรับ baseline
5. normalize ด้วยสถิติของ pretrained backbone
6. augmentation เฉพาะ train: horizontal flip, rotation เล็กน้อย, color jitter แบบจำกัด
7. หลีกเลี่ยง augmentation ที่เปลี่ยนลักษณะรอยโรคจนไม่สมจริง

ต้องเก็บ preprocessing เดียวกันไว้ใน checkpoint metadata เพื่อให้ training และ inference ตรงกัน

## 5. โมเดลและการเทรน

baseline ที่ควรเริ่มคือ EfficientNet-B0 หรือ ResNet-18 ที่ pretrain บน ImageNet แล้วเปลี่ยนหัว classifier เป็น 8 outputs เหตุผลคือขนาดพอเหมาะ ตรวจสอบง่าย และชั้น convolution สุดท้ายรองรับ Grad-CAM โดยตรง

ลำดับการเทรน:

1. ตั้ง seed สำหรับ Python, NumPy และ PyTorch
2. สร้าง DataLoader จาก patient-grouped manifest
3. ใช้ weighted cross-entropy หรือ weighted sampler เพื่อรับมือ class imbalance
4. optimizer: AdamW; scheduler: cosine decay หรือ ReduceLROnPlateau
5. train ตามจำนวน epoch ที่กำหนด โดยบันทึก loss และ metrics ทุก epoch
6. เลือก checkpoint จาก validation macro F1 ไม่ใช่ accuracy อย่างเดียว
7. early stopping เมื่อ validation ไม่ดีขึ้นตาม patience
8. บันทึก model weights, class order, preprocessing, config, commit SHA และ dataset fingerprint

ห้ามเลือกโมเดลจาก test set และห้ามรายงานเลขจาก Roboflow dashboard เป็นผลของ pipeline ใหม่

## 6. วัดผลอย่างไร

เพราะข้อมูลไม่สมดุล accuracy เพียงตัวเดียวไม่พอ ต้องรายงานอย่างน้อย:

- macro F1: ให้ความสำคัญทุกคลาสเท่ากัน
- balanced accuracy: เฉลี่ย recall ของทุกคลาส
- per-class sensitivity/recall: พบผู้ป่วยในคลาสนั้นได้เท่าไร
- per-class specificity: กันผลบวกลวงได้เท่าไร
- confusion matrix: โมเดลสับสนคลาสใดกับคลาสใด
- calibration เช่น Expected Calibration Error และ reliability diagram
- bootstrap 95% confidence interval ที่ resample ตามผู้ป่วย

ต้องแยก “ผล validation ระหว่างพัฒนา” ออกจาก “ผล test หลังล็อกโมเดล” บนสไลด์เสมอ

## 7. Grad-CAM จริงคืออะไร

Grad-CAM ใช้ gradient ของคะแนนคลาสเป้าหมายต่อ feature maps ของ convolution layer แล้วเฉลี่ย gradient เป็นน้ำหนัก จากนั้นรวม feature maps, ผ่าน ReLU, resize และ normalize เป็น heatmap ตามงานต้นฉบับ [Grad-CAM, ICCV 2017](https://openaccess.thecvf.com/content_iccv_2017/html/Selvaraju_Grad-CAM_Visual_Explanations_ICCV_2017_paper.html)

เงื่อนไขที่ Retinova จะเรียกว่า “Grad-CAM จริง”:

1. heatmap มาจาก checkpoint เดียวกับผล prediction
2. target class ระบุชัดและตรงกับผลที่แสดง
3. ระบุ layer ที่ hook ไว้
4. heatmap เปลี่ยนเมื่อเปลี่ยน target class ใน sanity test
5. ไม่มี CSS radial-gradient หรือวงกลมวางตำแหน่งตายตัว
6. เก็บ `model_version`, `target_class`, `target_layer`, preprocessing และเวลา inference เป็น provenance
7. คำอธิบายบนเว็บใช้ว่า “บริเวณที่มีอิทธิพลต่อคะแนนโมเดล” ไม่ใช้ว่า “ตำแหน่งรอยโรคที่ยืนยันแล้ว”

Grad-CAM ช่วยตรวจพฤติกรรมโมเดล แต่ไม่ได้พิสูจน์เหตุและไม่ใช่ segmentation mask ของรอยโรค

## 8. เส้นทางข้อมูลเวลาใช้งานจริง

```text
ผู้ใช้เลือกภาพ
  → browser ตรวจชนิด/ขนาด
  → backend ตรวจ payload และ decode ภาพ
  → quality gate
  → preprocessing ตาม model metadata
  → model forward pass
  → probabilities + uncertainty policy
  → Grad-CAM สำหรับ target class เดียวกัน
  → response พร้อม model provenance
  → หน้าเว็บแสดงผล/ข้อจำกัด/แนวทางส่งต่อ
```

API key และ checkpoint ต้องอยู่ฝั่ง server เท่านั้น GitHub Pages เป็น static hosting จึงไม่ควรเรียก inference provider ด้วย secret จาก JavaScript

## 9. วิธีใช้ Public Preview ปัจจุบัน

1. เปิด `https://kla2009k.github.io/Retinova/`
2. เลือก JPG/PNG ไม่เกิน 10 MB
3. หน้าเว็บแสดงภาพเฉพาะใน browser และตรวจว่าไฟล์เปิดอ่านได้
4. กด “ตรวจความพร้อมของภาพ” เพื่อดูชนิด ขนาด และความละเอียด
5. ระบบรุ่นนี้ยังไม่ส่งภาพ ไม่คืนชื่อโรค และไม่สร้าง heatmap

เมื่อ backend รุ่นตรวจสอบแล้วพร้อม ขั้นตอน 3–5 จะเพิ่ม quality score, prediction, probability, model version และ Grad-CAM โดยหน้าตาจะยังแสดงสถานะหลักฐานชัดเจน

## 10. คำที่ควรและไม่ควรพูด

พูดได้:

- “ต้นแบบช่วยคัดกรองภาพ fundus เพื่อการวิจัย”
- “กำลังประเมินด้วยการแบ่งข้อมูลตามผู้ป่วย”
- “Grad-CAM แสดงบริเวณที่มีอิทธิพลต่อคะแนนโมเดล”
- “ผลต้องได้รับการยืนยันโดยจักษุแพทย์”

อย่าพูด:

- “วินิจฉัยโรคได้ 94.2%” จนกว่าจะมี test report ที่ตรวจสอบได้
- “heatmap คือจุดที่เป็นโรคแน่นอน”
- “ข้อมูลเข้ารหัสและปลอดภัย 100%” โดยไม่มีระบบและ threat model รองรับ
- “เป็นระบบตรวจม่านตา” เพราะเป็นคนละอวัยวะและคนละงาน
- “ใช้ได้กับผู้ป่วยจริง” ก่อนมีการตรวจสอบภายนอก จริยธรรม และข้อกำกับที่เกี่ยวข้อง

## 11. Checklist ก่อนสาธิตโมเดลจริง

- [ ] ไม่มี patient leakage
- [ ] class order ตรงกันตั้งแต่ manifest ถึงหน้าเว็บ
- [ ] test metrics มี confusion matrix และ confidence interval
- [ ] checkpoint มี hash/version และ model card
- [ ] Grad-CAM ผูกกับ prediction เดียวกันและผ่าน sanity tests
- [ ] input ที่ไม่ใช่ fundus หรือคุณภาพต่ำถูกปฏิเสธ/ส่งต่อ
- [ ] ไม่มี secret หรือข้อมูลผู้ป่วยใน repository/log
- [ ] หน้าเว็บไม่ใช้คำวินิจฉัยและมีคำเตือนภาวะฉุกเฉิน
- [ ] มี human review ก่อนใช้ผลในการตัดสินใจ

## 12. แหล่งอ้างอิงหลัก

- ODIR benchmark paper: https://arxiv.org/abs/2102.07978
- Grad-CAM paper: https://openaccess.thecvf.com/content_iccv_2017/html/Selvaraju_Grad-CAM_Visual_Explanations_ICCV_2017_paper.html
- PyTorch transfer learning tutorial: https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html
- PyTorch reproducibility notes: https://docs.pytorch.org/docs/stable/notes/randomness.html

หมายเหตุ: รายละเอียดทางการแพทย์บนเว็บไซต์ต้องผ่านการทบทวนโดยจักษุแพทย์ก่อนใช้กับบริบทนอกการสาธิต

## 13. ผล baseline ที่ทำซ้ำได้ ณ 1 สิงหาคม 2026

Retinova เทรน ResNet-18 จำนวน 8 epochs บน split ที่แยกผู้ป่วยแล้ว โดยเลือก checkpoint จาก validation macro F1:

- test 957 ภาพ จาก 503 ผู้ป่วย
- macro F1 = 0.562; patient-bootstrap 95% interval = 0.507–0.603
- balanced accuracy = 0.617; patient-bootstrap 95% interval = 0.555–0.667
- recall ต่ำสุดคือ Other 0.264 และ Hypertension 0.444
- patient overlap ระหว่าง train/validation/test = 0

ผลนี้ดีกว่าการไม่มี baseline ที่ตรวจสอบได้ แต่ยังไม่พอสำหรับใช้งานคลินิก การพบ shortcut บริเวณขอบภาพจาก Grad-CAM ยืนยันว่าต้องเพิ่ม quality control, external validation และผู้เชี่ยวชาญตรวจ failure cases ก่อนเปิด inference สาธารณะ ดูรายละเอียดที่ [Baseline Evaluation v1](EVALUATION_BASELINE_V1.md)
