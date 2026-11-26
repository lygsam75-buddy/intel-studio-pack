# -*- coding: utf-8 -*-
"""B580 分块超分节点（RealESRGAN x4plus · fp16 · tile 512 / overlap 32）。

为什么需要它：
  ComfyUI 自带的 ImageUpscaleWithModel 是**整帧一次性**过模型。1536x864 的 4 倍是 6144x3456，
  在 11.6G 的 B580 上必炸；而分块超分只在 tile 上算，显存恒定，实测 1.82 s/帧（1024x576→1536x864）。

行为与 D:/WorkBuddy/_handoff/b580_video_20261124/video_sr.py 完全一致：
  分块 4x（fp16）→ LANCZOS 缩到目标尺寸 → UnsharpMask(1.2, 45, 2)。
  小图（源像素 < 目标 60%）走超分，大图走 lanczos + 更重的锐化（超分收益小、耗时大）。

XPU 铁律：每块算完必须 torch.xpu.synchronize()，否则跨设备搬运会竞态出 NaN。
"""
import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image, ImageFilter

import folder_paths
import comfy.model_management as mm

NODE_NAME = "B580TiledUpscale"
_CACHE = {}


def _build_rrdb(nf=64, nb=23, gc=32):
    class ResidualDenseBlock(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(nf, gc, 3, 1, 1)
            self.conv2 = nn.Conv2d(nf + gc, gc, 3, 1, 1)
            self.conv3 = nn.Conv2d(nf + 2 * gc, gc, 3, 1, 1)
            self.conv4 = nn.Conv2d(nf + 3 * gc, gc, 3, 1, 1)
            self.conv5 = nn.Conv2d(nf + 4 * gc, nf, 3, 1, 1)
            self.lrelu = nn.LeakyReLU(0.2, True)

        def forward(self, x):
            x1 = self.lrelu(self.conv1(x))
            x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
            x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
            x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
            return self.conv5(torch.cat((x, x1, x2, x3, x4), 1)) * 0.2 + x

    class RRDB(nn.Module):
        def __init__(self):
            super().__init__()
            self.rdb1, self.rdb2, self.rdb3 = ResidualDenseBlock(), ResidualDenseBlock(), ResidualDenseBlock()

        def forward(self, x):
            return self.rdb3(self.rdb2(self.rdb1(x))) * 0.2 + x

    class RRDBNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv_first = nn.Conv2d(3, nf, 3, 1, 1)
            self.body = nn.Sequential(*[RRDB() for _ in range(nb)])
            self.conv_body = nn.Conv2d(nf, nf, 3, 1, 1)
            self.conv_up1 = nn.Conv2d(nf, nf, 3, 1, 1)
            self.conv_up2 = nn.Conv2d(nf, nf, 3, 1, 1)
            self.conv_hr = nn.Conv2d(nf, nf, 3, 1, 1)
            self.conv_last = nn.Conv2d(nf, 3, 3, 1, 1)
            self.lrelu = nn.LeakyReLU(0.2, True)

        def forward(self, x):
            f = self.conv_first(x)
            f = f + self.conv_body(self.body(f))
            f = self.lrelu(self.conv_up1(F.interpolate(f, scale_factor=2, mode="nearest")))
            f = self.lrelu(self.conv_up2(F.interpolate(f, scale_factor=2, mode="nearest")))
            return self.conv_last(self.lrelu(self.conv_hr(f)))

    return RRDBNet()


def _load(name):
    dev = mm.get_torch_device()
    key = (name, str(dev))
    if key in _CACHE:
        return _CACHE[key]
    path = folder_paths.get_full_path("upscale_models", name)
    if path is None:
        raise FileNotFoundError("找不到超分模型 %s（应在 models/upscale_models/）" % name)
    net = _build_rrdb().to(dev).eval().half()
    sd = torch.load(path, map_location="cpu")
    sd = sd.get("params_ema", sd)
    net.load_state_dict({k: v.half() for k, v in sd.items()}, strict=True)
    if str(dev).startswith("xpu"):
        torch.xpu.synchronize()          # 铁律：搬完立即同步，防竞态 NaN
    _CACHE[key] = (net, dev)
    return _CACHE[key]


def _sr_frame(net, dev, arr, tile, ov):
    H, W, _ = arr.shape
    out = np.zeros((H * 4, W * 4, 3), np.float32)
    for y in range(0, H, tile):
        for x in range(0, W, tile):
            y1, x1 = min(y + tile, H), min(x + tile, W)
            y0, x0 = max(0, y - ov), max(0, x - ov)
            y2, x2 = min(H, y1 + ov), min(W, x1 + ov)
            sub = arr[y0:y2, x0:x2]
            t = torch.from_numpy(sub.astype(np.float32) / 255.0).permute(2, 0, 1)[None].to(dev).half()
            with torch.no_grad():
                o = net(t).clamp(0, 1)
            if str(dev).startswith("xpu"):
                torch.xpu.synchronize()
            o = (o[0].permute(1, 2, 0).float().cpu().numpy() * 255).round().clip(0, 255).astype(np.uint8)
            cy, cx = (y - y0) * 4, (x - x0) * 4
            out[y * 4:y1 * 4, x * 4:x1 * 4] = o[cy:cy + (y1 - y) * 4, cx:cx + (x1 - x) * 4]
    return out


class B580TiledUpscale:
    @classmethod
    def INPUT_TYPES(cls):
        models = folder_paths.get_filename_list("upscale_models") or ["RealESRGAN_x4plus.pth"]
        return {
            "required": {
                "image": ("IMAGE",),
                "model_name": (models,),
                "tile": ("INT", {"default": 512, "min": 128, "max": 2048, "step": 64}),
                "overlap": ("INT", {"default": 32, "min": 0, "max": 256, "step": 8}),
                "target_width": ("INT", {"default": 1536, "min": 64, "max": 8192, "step": 8}),
                "target_height": ("INT", {"default": 864, "min": 64, "max": 8192, "step": 8}),
                "auto_skip_sr": ("BOOLEAN", {"default": True,
                                             "tooltip": "源像素≥目标 60% 时跳过超分，走 lanczos+锐化"}),
                "sharpen": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "upscale"
    CATEGORY = "B580/超分"

    def upscale(self, image, model_name, tile, overlap, target_width, target_height,
                auto_skip_sr=True, sharpen=True):
        try:
            import comfy.utils
            pbar = comfy.utils.ProgressBar(image.shape[0])
        except Exception:
            pbar = None

        b, h, w, _ = image.shape
        ratio = (w * h) / float(target_width * target_height)
        use_sr = (not auto_skip_sr) or ratio < 0.60
        net, dev = _load(model_name) if use_sr else (None, None)
        print("[B580 超分] %dx%d x%d 帧 → %dx%d  ratio %.2f  %s"
              % (w, h, b, target_width, target_height, ratio,
                 "RealESRGAN x4 tile=%d ov=%d" % (tile, overlap) if use_sr else "lanczos"), flush=True)

        outs = []
        for i in range(b):
            arr = (image[i].cpu().numpy() * 255.0).round().clip(0, 255).astype(np.uint8)
            im = Image.fromarray(arr)
            if use_sr:
                big = _sr_frame(net, dev, arr, tile, overlap)
                im = Image.fromarray(big).resize((target_width, target_height), Image.LANCZOS)
                if sharpen:
                    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=45, threshold=2))
            else:
                im = im.resize((target_width, target_height), Image.LANCZOS)
                if sharpen:
                    im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=70, threshold=2))
            outs.append(torch.from_numpy(np.asarray(im).astype(np.float32) / 255.0))
            if pbar is not None:
                pbar.update(1)
        return (torch.stack(outs, 0),)


NODE_CLASS_MAPPINGS = {NODE_NAME: B580TiledUpscale}
NODE_DISPLAY_NAME_MAPPINGS = {NODE_NAME: "B580 分块超分 (RealESRGAN x4)"}
