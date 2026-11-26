# Running MiniMax H3 on a 12 GB GPU — Intel Arc B580 Patch Pack

**English | [简体中文](README.md)**

> The stock Intel Studio Pack is tuned for 24 GB+ cards. On a B580 (11.6 GiB) it either runs at half speed or the process vanishes mid-run with no traceback.
> This pack does one thing: **make a 12 GB card behave like a 12 GB card.**
> 3 launch flags + 4 workflows + 1 tiled-upscale node. **No models included.** 49 KB zipped.

---

## Test rig

| Item | Value |
|---|---|
| GPU | Intel Arc B580, **11.597 GiB** visible to `torch.xpu` |
| CPU / RAM | Ryzen 5 9600X / 32 GB |
| Page file | 96 GB on SSD |
| Driver | 32.0.101.9150 |
| Baseline | ComfyUI Intel Arc Studio Pack: ComfyUI 0.43.0 + torch 2.13.0+xpu + omni_xpu_kernel 0.2.0b2 |
| Data date | 2026-11-23, all numbers measured on this machine |

Every number is end-to-end (click Run → mp4 on disk), not a single-node timing. **Do not apply 12 GB numbers to a 16 GB or 32 GB card — or the reverse.**

---

## 1. Why 12 GB works at all

MiniMax H3 weights **do not fit in 12 GB**: the int8-quantized DiT is ~19.5 GB, the nvfp4 text encoder ~14.6 GB. Either one exceeds 11.597 GiB.

So the reason it runs isn't that the model "fits" — it's **streaming plus offload**: weights move into VRAM on demand and back out afterwards. That is the normal configuration path for 12 GB, not a hack. The price is that every transfer costs time, which reduces all optimization to two goals:

1. **Transfer less** — stop reloading the whole chain every run.
2. **Stop dying during transfers** — the pinned-memory crash path.

The four changes below are entirely about those two.

---

## 2. The four changes

| # | Flag / setting | Stock default | This pack | Evidence |
|---|---|---|---|---|
| 1 | `--reserve-vram` | `5` (frozen value for B70) | **`2`** | Reserving 5 GB on an 11.6 GB card gives away memory for nothing: end-to-end **20% slower** (171.6 s → 142.8 s). `2` and `4` are equivalent; `2` leaves 2 GB more for streaming. Fall back to `4` if the OS starts stealing VRAM |
| 2 | `--enable-dynamic-vram` | only as a fallback | **required** | With it off, the full chain reloads every run (`loads=4` for both fresh and cached), steady state **75% slower** (248 s → 143 s). Disable only as an emergency measure if you hit `DEVICE_LOST` |
| 3 | `--disable-pinned-memory` | **not passed** | **added** | `OMNIXPU_PIN_MEMORY=0` in the stock script is a **dead knob** — nothing in the engine tree reads it. A runtime probe shows `DISABLE_PINNED_MEMORY=False`, meaning pinned memory is still on, which is exactly the `cudaHostRegister` crash path in upstream issues #16804 / #16846. The real switch is this CLI flag. With it off: steady state ±0.1%, **cold start 9% faster** (172.74 s → 156.96 s) |
| 4 | Text-encoder caching | present but unverified | **kept and verified** | Without caching, the text encoder is reloaded every run. Under `--enable-dynamic-vram` it reports `loads=0`; `--cache-classic` stays on as a belt-and-braces measure |

The full launch line is in `b580-12g/启动_Intel_XPU_B580.bat` (pure ASCII + CRLF, double-click to run).

---

## 3. The four workflows

Drop `workflows/*.json` into `ComfyUI\user\default\workflows\` and pick them from the UI.

| File | Preset | End-to-end (cold) | Use |
|---|---|--:|---|
| `B580_图生视频_首帧_H3_5s_864x480.json` | 480P · 5 s (124 frames) | 157 s | drafts, batch tests |
| `B580_图生视频_首帧_H3_5s_1280x704.json` | 720P · 5 s (124 frames) | **474 s (7:54)** | **recommended**, 3/3 cold starts stable |
| `B580_图生视频_首帧_H3_5s_1536x864.json` | 864P · 5 s (124 frames) | 638 s | final-quality shots |
| `B580_H3_出片超分一体_5s.json` | 1024×576 render → upscale 1536×864 | 8.8 min (5 render + 3.8 upscale) | one chain to a finished clip |

### Render + upscale in one chain (the everyday option)

```
H3 render 1024×576×124 → VAEDecode → B580 tiled upscale → 1536×864 → mp4
```

- **1024×576 is the efficiency knee on 12 GB**: above it, per-clip time grows faster than image quality. You get a 16:9 master, then upscale for delivery.
- **Why tiling is mandatory**: ComfyUI's built-in `ImageUpscaleWithModel` pushes the whole frame through the model at once — 4× of 1536×864 is 6144×3456, which always OOMs at 11.6 GB. Tiled upscaling works on tiles only, so VRAM stays flat: **1.82 s/frame** measured.
- **Same-frame double pinning**: wire both the first-frame and last-frame anchor to the same `LoadImage`. The character talks and gestures while the background does not move at all — the most reliable setup for explainer/talking-head clips.
- Tuned for 12 GB: `tile 512 / overlap 32 / target 1536×864 / auto_skip_sr on / sharpen on`. Drop tile to 384 if VRAM is tight.

---

## 4. Install — three steps

1. Unzip and **overwrite the whole folder into the root that contains `ComfyUI\`** (i.e. `Intel-Studio-Pack\`).
2. Copy `workflows\*.json` into `ComfyUI\user\default\workflows\`.
3. Double-click `启动_Intel_XPU_B580.bat`.

**Restart the engine once after overwriting** — that is when the tiled-upscale node gets loaded.

One test tells you whether it worked: **run one 720P clip. If it finishes under ten minutes, it's installed correctly.**

---

## 5. What is not included

| Missing | What to do |
|---|---|
| H3 model weights + text encoder | Bring your own. This pack never touches your model directory |
| `models/upscale_models/RealESRGAN_x4plus.pth` (~64 MB) | Required by the combined workflow. Use it if you already have it; otherwise search `RealESRGAN x4` in ComfyUI Manager or take it from the official repo |

---

## 6. System prerequisites (the pack cannot fix these)

| Item | Setting | Why |
|---|---|---|
| **TDR** | `TdrDelay=60`, `TdrDdiDelay=60` (registry, reboot required) | Windows kills long kernels after 2 s by default; the symptom is **the process disappearing with no traceback**. At 60 s, 3/3 runs pass |
| **Page file** | initial 32 GB / max 64 GB+, on SSD | The only expandable "memory" on a 32 GB machine; H3 loading depends on it |
| **ECC** | off (driver default — leave it alone) | On = 27.25 GB visible, off = 31 GB. On B580 there is no upside to enabling it |
| **Resolution** | both axes ÷32 | After ÷16, the latent still has to be even × even (2×2 patch). Portrait 720P is **704×1280**; 720×1280 always crashes |
| **Frame count** | `17k+5` | 124 frames = 5.17 s; 243 frames = 10.1 s |

---

## 7. Measured envelope (do not exceed casually)

| Dimension | Verified |
|---|---|
| Resolution | 864×480 → **1920×1088** (230 MP·frame) all pass; no wall found |
| Frame count | **362 frames (15.08 s)** at 480P |
| Combination | **Do not max out both at once**: 864P at 5 s; for 10 s+ drop to 480P / 576P |

---

## 8. Known limits and rollback

- Above 1920×1088, or very long frame counts, untested. If you hit a ceiling, step down a preset.
- On `DEVICE_LOST` (0 occurrences in the last 21 delivered clips): first roll back by disabling `--enable-dynamic-vram` — 75% slower but stable — then check the WATCHDOG dump, the TDR registry values, and the driver version.
- After a driver update (>32.0.101.9150), re-validate: three cold starts at 480P plus one 720P run (~30 minutes).

**Two different ceilings, two different diagnoses**:
- VRAM headroom exhausted + `OutOfMemoryError` = **capacity wall** (transient buffers). Step down a preset.
- Several GiB of headroom left + `DEVICE_LOST` = **async upload race**. Not reproduced on this engine (0.43).

---

## 9. Download

**Release (recommended)**
<https://github.com/lygsam75-buddy/intel-studio-pack/releases/tag/b580-12g-v1>

- Asset: `B580_12G_patch_pack_v1.zip` — 50,209 bytes
- SHA-256: `515eae1572d6c864377415c018747130e4b700ae1b6f8bb6731cb3f59909fff6`

**Or browse the folder** (grab files individually, no zip)
<https://github.com/lygsam75-buddy/intel-studio-pack/tree/main/b580-12g>

Verify:

```powershell
# Windows PowerShell
Get-FileHash .\B580_12G_patch_pack_v1.zip -Algorithm SHA256
```

---

## 10. License and feedback

The `.bat`, workflow JSONs, and tiled-upscale node in this pack may be used, modified, and redistributed freely — keep the attribution.
The baseline Studio Pack and the models used with it carry their own licenses; respect them.

Issues and counter-data are welcome. **Include your GPU model, driver version, page-file size, and the full error.** "It doesn't work" is not something I can debug.
