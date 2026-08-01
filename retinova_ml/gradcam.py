"""Class-specific Grad-CAM computed from the model's activation graph."""
import torch
from torch.nn import functional as F


class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.activations = None
        self._handle = target_layer.register_forward_hook(self._capture_activations)

    def _capture_activations(self, _module, _inputs, output):
        self.activations = output

    def __call__(self, inputs, class_indices=None):
        self.model.zero_grad(set_to_none=True)
        logits = self.model(inputs)
        if class_indices is None:
            class_indices = logits.argmax(dim=1)
        class_indices = class_indices.to(device=logits.device, dtype=torch.long)
        if class_indices.shape != (inputs.shape[0],):
            raise ValueError("class_indices must contain one class per input")
        selected_scores = logits.gather(1, class_indices[:, None]).sum()
        gradients = torch.autograd.grad(selected_scores, self.activations, retain_graph=False)[0]
        weights = gradients.mean(dim=(2, 3), keepdim=True)
        heatmaps = torch.relu((weights * self.activations).sum(dim=1, keepdim=True))
        heatmaps = F.interpolate(heatmaps, size=inputs.shape[-2:], mode="bilinear", align_corners=False)
        flat = heatmaps.flatten(1)
        minimum = flat.min(dim=1).values[:, None, None, None]
        maximum = flat.max(dim=1).values[:, None, None, None]
        heatmaps = (heatmaps - minimum) / (maximum - minimum).clamp_min(1e-8)
        return heatmaps.detach().cpu(), logits.detach().cpu()

    def close(self):
        if self._handle is not None:
            self._handle.remove()
            self._handle = None

    def __enter__(self):
        return self

    def __exit__(self, _exception_type, _exception, _traceback):
        self.close()
