**English** · [简体中文](README.zh-CN.md)

# ComfyUI Intel Arc Studio Pack

**No launcher UI by design** — engine + pipelines + SOP, straight out of the box.
A product gap-fill bundle for ComfyUI on Intel Arc (XPU): everything measured on real hardware,
every gap filled, nothing to configure.

> 📦 **Full bundle (84 GiB / 90,188,748,800 B)** — `Intel-Studio-Pack_full_v1.tar`: engine + 12 workflows +
> 13 models. **Single archive** — weights don't compress, so it's archived uncompressed; `tar -xf`
> extracts everything.
> - **Baidu Netdisk (CN)**: <https://pan.baidu.com/s/17AEswSAjSkif5MqV5Kj3kA> 提取码 `8sk3` (permanent).
>   Stored as **5 volumes** `Intel-Studio-Pack_full_v1.tar.01`–`.05` (18.04 GB each). Merge first:
>   `cat Intel-Studio-Pack_full_v1.tar.0* > Intel-Studio-Pack_full_v1.tar` (Git Bash) or
>   `copy /b Intel-Studio-Pack_full_v1.tar.01+…+.05 Intel-Studio-Pack_full_v1.tar` (cmd), then verify
>   against `SHA256_Intel-Studio-Pack_full_v1.txt`.
> - **USB copy**: the single `Intel-Studio-Pack_full_v1.tar` — no merge needed.
>
> 🪶 **Lightweight track (this repo)** — model manifest + byte-checked download script (13 models,
> ~76 GB via hf-mirror). Bring your own engine, or assemble from the handbook.

**Download notes (CN users)** — the full bundle is a single 81 GB archive on Baidu Netdisk by design
(GitHub Releases cap files at 2 GB):

1. **Normal**: open the share link in the Baidu client or browser — one file, queued like any download.
2. **Throttled?** Non-VIP accounts are slowed on large files. Load the share link into **Xunlei (迅雷)**
   or the Baidu client — both resume broken transfers and usually sidestep the worst of it.
3. **Fastest**: on-site installs / dealer delivery — USB copy, no throttling at all.

---

## Who this is for

The target machine is **8 GB VRAM + 32 GB system RAM** — and a large share of those machines are
**converted ex-server-room workstations**: only two DIMM slots (no room to grow), firmware-level
ECC toggles, blower-style card bays. Every parameter in this pack is frozen from real measurement
on exactly this class of hardware (the 10-12 core-refactor benchmark rig reports
`Total VRAM 31907 MB, total RAM 31860 MB`).

---

## vs. the Qiuye (秋叶) aki build

The Qiuye aki build (`ComfyUI-intel-aki-v1.1`) and this pack are both **Intel-only packages** with
different jobs: the aki build is the core-refactor workbench (OmniXPU adapter layer + VSA/SLA/SolAttn
nodes, with launcher UI); this pack is the product gap-fill bundle (no launcher, gaps filled,
ready to run). It does not replace the aki build — its pipelines and SOP inherit directly from
the 10-12 core-refactor measurements.

| Dimension | Qiuye aki build | This pack |
|---|---|---|
| Role | core-refactor workbench (v1.1) | **product gap-fill bundle** |
| Launch | launcher UI | **no launcher**, bat → main.py |
| Kernels | OmniXPU adapters (attention/fp8/int8/vram-trim) | inherits the same kernel posture |
| Workflows | DIY | **12 ready-to-run**, wired to PIKA H3 Flex |
| Memory SOP | posture frozen from 10-12 data | **hard 32G SOP** + troubleshooting table |
| Models | self-managed | 13-item manifest + byte-checked script |
| Deliverable | the workbench itself | full bundle (Netdisk) + lightweight track (this repo) |

### 10-12 core-refactor measurements

Same H3 image-to-video workflow (6-step turbo, 480P tier, B70 + 32 GB rig), single end-to-end round:

| Run | Delta | End-to-end | Takeaway |
|---|---|---|---|
| ab_A_r15 | baseline (no adapter layer) | 245.17 s | — |
| ab_B_r15 | OmniXPU adapters on (attention/fp8/int8/vram-trim) | **142.94 s** | **1.71×** end-to-end |
| ab_B pinned-memory attempt | pinned 3823 MB | crashed | XPU torch has no CUDA: `AssertionError: Torch not compiled with CUDA enabled` → **pinned memory is a no-go on XPU torch** (off by default: `OMNIXPU_PIN_MEMORY=0`) |

Boot chain (boot_clean): OmniXPU prestartup 2.8 s, H3-VSA-XPU 0.0 s.

---

## Hard requirements (pass/fail, not suggestions)

| Item | Requirement | Why |
|---|---|---|
| System RAM | **32 GB** (many boards have only two DIMM slots — do not count on upgrading) | residency floor for H3 text encoder + DiT |
| Page file | **REQUIRED**: 32G initial, 64G max, on SSD | the only expandable "RAM" on a 32 GB box — hard dep during H3 load |
| Text encoder | **nvfp4 build ONLY** | the int8 build (25.28 GB) segfaults at load on 32 GB |
| ECC | **OFF** (IGS → Graphics → ECC → Off → reboot) | ON = 27.25G visible; OFF = 31G; ships OFF |
| Resolution | both sides divisible by **32** | latent after /16 must be even×even for 2×2 patches |
| Pinned memory | off by default (`OMNIXPU_PIN_MEMORY=0`) | ±0.1% measured; steals non-pageable RAM on 32 GB boxes |

### Resolution quick reference (÷32 grid)

| Use case | Width × Height | Note |
|---|---|---|
| 720P portrait | **704 × 1280** | only legal value — **720×1280 crashes** |
| 540P portrait | 544 × 960 | VRAM-saving tier |
| 720P landscape | 1280 × 704 | same grid transposed |
| 1080P portrait | render 704×1280, then latent upscale | 1088×1920 direct does not fit |

Frame count: 17k+5 (k=0,1,2…), 243 frames = 10.125 s @ 24 fps.

---

## Quick start

1. Extract the full bundle anywhere (SSD, ≥100G free)
2. Double-click `启动_Intel_XPU.bat`
3. Open `http://127.0.0.1:8188`

Launch parameters frozen from B70 measurement:

```
--reserve-vram 5 --cache-classic
```

- `--reserve-vram 5`: reserve 5G for OS+display; only stable value under multi-card load
- `--cache-classic`: stops the new default cache from reloading the text encoder every round (~2.6 min saved per round)
- Alternative when VRAM-tight: `--enable-dynamic-vram --reserve-vram 4`; fall back to the default on DEVICE_LOST crashes

---

## Workflows (12, all wired to the PIKA H3 Flex path)

### H3 video (4)

| Workflow | Purpose |
|---|---|
| 图生视频_首帧_H3 | single image → video |
| 图生视频_首尾帧_H3 | first+last frame interpolation |
| 图生视频_二采_H3 | low-res render + latent upscale |
| 图生视频_打斗分镜_H3 | dynamic action shots |

The pipeline is already switched to **PIKA H3 Flex** (LoRAs attached: pika_h3_flex_fl2va / ref2va).
**Flex is a distillation adapter — do not stack other acceleration LoRAs on top** (stacking breaks the output).

### Z-Image (8)

t2i / i2i / multi-reference etc., on z_image_turbo_int8_convrot + qwen_3_4b_fp8_mixed.

---

## Model manifest (13 items, ~76 GB)

The full bundle ships them all; the lightweight track fetches them via `download_models.py` from hf-mirror.

| # | Relative path | Size | repo |
|---|---|---|---|
| 1 | diffusion_models/MiniMax/minimax_h3_fl2va_pruned_int8_convrot.safetensors | 19.5G | Comfy-Org/MiniMax-H3 |
| 2 | diffusion_models/MiniMax/minimax_h3_ref2va_pruned_int8_convrot.safetensors | 19.5G | Comfy-Org/MiniMax-H3 |
| 3 | diffusion_models/z_image_turbo_int8_convrot.safetensors | 5.8G | Comfy-Org/Z-Image-Turbo |
| 4 | text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors | 14.6G | Comfy-Org/MiniMax-H3 |
| 5 | text_encoders/qwen_3_4b_fp8_mixed.safetensors | 5.2G | Comfy-Org/Z-Image-Turbo |
| 6 | vae/minimax_h3_video_vae_fp16.safetensors | 4.9G | Comfy-Org/MiniMax-H3 |
| 7 | vae/minimax_h3_audio_vae_fp32.safetensors | 578M | Comfy-Org/MiniMax-H3 |
| 8 | vae/ae_zimage.safetensors | 320M | Comfy-Org/Z-Image-Turbo (named `ae.safetensors` upstream) |
| 9 | loras/pika_h3_flex_fl2va_v1_bf16.safetensors | 1.9G | Comfy-Org/MiniMax-H3 |
| 10 | loras/pika_h3_flex_ref2va_v1_bf16.safetensors | 1.9G | Comfy-Org/MiniMax-H3 |
| 11 | vae_approx/taeh3.safetensors | 22M | OzzyGT/taeh3 |
| 12 | latent_upscale_models/minimax_h3_latent_upscaler_3d_fp16.safetensors | 659M | Konteni2/Minimax_h3_latent_Upscaler |
| 13 | background_removal/birefnet.safetensors | 424M | Comfy-Org/BiRefNet |

### Lightweight download

```bash
# dep: pip install huggingface_hub
python download_models.py                # all 13
python download_models.py --only h3     # H3 video line only
python download_models.py --only zimage # Z-Image line only
python download_models.py --only aux    # aux items
```

The script goes through the hf-mirror.com mirror, renames/creates directories as needed, and
re-runs automatically skip already-complete files (byte-count verified).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Text encoder crashes at load | used the int8 build | switch to the nvfp4 build (#4) |
| 720×1280 crashes instantly | side not divisible by 32 | use 704×1280 |
| VRAM reports 27.25G | ECC is on | disable ECC in IGS → reboot → 31G |
| Text encoder reloads every round | wrong cache flag | use the bundled bat's `--cache-classic` |
| Broken output after stacking LoRAs | Flex is a distillation adapter | keep Flex only |
| OOM or system hang | page file not set | see Hard requirements |

---

## Pinned versions (core)

Everything below is what the bundle actually ships (measured from the package, not quoted):

| Component | Version |
|---|---|
| ComfyUI | **0.43.0** |
| Python (embedded) | **3.13.14** |
| PyTorch | **2.13.0+xpu** — torchaudio 2.11.0+xpu, torchvision 0.28.0+xpu |
| Intel SYCL runtime (oneAPI) | **2026.0.0** (sycl9) |
| Intel oneMKL / OpenCL / OpenMP | 2026.0.0 |
| omni_xpu_kernel (XPU kernel pack) | **0.2.0b2+torch213.bmg** |
| TE-Speed-MiniMaxH3 | nodes.pyd build 2026-11-05 (no upstream version tag) |
| ComfyUI-KJNodes | **1.5.3** (CUDA-cleaned) |
| ComfyUI-VideoHelperSuite | **1.7.9** |
| PIKA H3 Flex LoRA | **v1** bf16 (pika_h3_flex_fl2va / ref2va) |
| H3 text encoder | qwen3vl-32B **nvfp4 AWQ** (the int8 build segfaults on 32 GB) |

Custom nodes: 40+ packs bundled (KJNodes, VideoHelperSuite, TE-Speed-MiniMaxH3, latent Upscaler,
Frame-Interpolation, LayerStyle, rgthree, …). Model versions/quant tiers: see the manifest table above.

---

## Directory layout

```
Intel-Studio-Pack/
├── 启动_Intel_XPU.bat      # double-click launch (no launcher)
├── README.md               # this file (English)
├── README.zh-CN.md         # 简体中文版
├── download_models.py      # model downloader (lightweight track)
├── python_embeded/         # bundled Python + Intel XPU runtime
└── ComfyUI/
    ├── custom_nodes/       # KJNodes (CUDA-cleaned) / TE-Speed-MiniMaxH3 + 40 more
    ├── user/default/workflows/  # 12 workflows
    ├── input/              # voices/ + sample assets
    └── models/             # 13 models (in the full bundle)
```

Sanitized: no manager components (no app.py / manager.json); zero CUDA leftovers
(Sage references excised from KJNodes).
