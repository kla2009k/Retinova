import unittest
from io import BytesIO

import numpy as np
from PIL import Image

from retinova_ml.onnx_inference import decode_candidate_image, normalize_cam, preprocess_image


class ONNXPreprocessingTests(unittest.TestCase):
    def test_blank_upload_is_rejected_before_inference(self):
        buffer = BytesIO()
        Image.new("RGB", (400, 400), color=(40, 40, 40)).save(buffer, "PNG")
        with self.assertRaisesRegex(ValueError, "blank|contrast"):
            decode_candidate_image(buffer.getvalue())

    def test_varied_image_passes_technical_gate(self):
        pixels = np.zeros((300, 300, 3), dtype=np.uint8)
        pixels[:, 150:] = (220, 100, 70)
        buffer = BytesIO()
        Image.fromarray(pixels).save(buffer, "PNG")
        self.assertEqual((300, 300), decode_candidate_image(buffer.getvalue()).size)

    def test_gif_upload_is_rejected(self):
        buffer = BytesIO()
        Image.new("RGB", (300, 300), color="red").save(buffer, "GIF")
        with self.assertRaisesRegex(ValueError, "JPEG and PNG"):
            decode_candidate_image(buffer.getvalue())

    def test_corrupt_image_is_a_client_error(self):
        with self.assertRaisesRegex(ValueError, "invalid or unreadable image"):
            decode_candidate_image(b"not an image")

    def test_preprocess_produces_normalized_nchw_float32(self):
        source = Image.new("RGB", (400, 300), color=(128, 64, 32))

        tensor = preprocess_image(source, image_size=224, interpolation="bilinear")

        self.assertEqual((1, 3, 224, 224), tensor.shape)
        self.assertEqual(np.float32, tensor.dtype)
        self.assertTrue(np.isfinite(tensor).all())

    def test_unknown_interpolation_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported interpolation"):
            preprocess_image(Image.new("RGB", (300, 300)), 224, "nearestish")


class ONNXCamTests(unittest.TestCase):
    def test_cam_is_resized_normalized_and_finite(self):
        cam = np.asarray([[0.0, 2.0], [1.0, 4.0]], dtype=np.float32)

        normalized = normalize_cam(cam, image_size=16)

        self.assertEqual((16, 16), normalized.shape)
        self.assertEqual(np.float32, normalized.dtype)
        self.assertAlmostEqual(0.0, float(normalized.min()), places=6)
        self.assertAlmostEqual(1.0, float(normalized.max()), places=6)

    def test_constant_cam_becomes_zero_map(self):
        normalized = normalize_cam(np.ones((7, 7), dtype=np.float32), image_size=32)
        self.assertFalse(normalized.any())


if __name__ == "__main__":
    unittest.main()
