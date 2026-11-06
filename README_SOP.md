# ComfyUI Intel Arc 专版（产品坑位包）
# ComfyUI Intel Arc Studio Pack — Product Gap-Fill Bundle

**不含管理器启动界面**，引擎 + 跑径 + SOP 直出。
**No launcher UI by design** — engine + pipelines + SOP, straight out of the box.

---

## 一、双轨获取 / Distribution

| 口径 / Track | 内容 / Contents | 落点 / Where |
|---|---|---|
| 全量包 / Full bundle | 引擎 + 节点 + 12 条工作流 + 13 个模型（~85G）→ Engine + nodes + 12 workflows + 13 models (~85G) | 百度网盘（分卷压缩）/ Baidu Netdisk (split volumes) |
| 轻量口径 / Lightweight | 本 README + 下载脚本 + 模型清单 → README + model download script + manifest | GitHub（本仓库）/ GitHub (this repo) |

---

## 二、定位与对比 / Positioning

目标用户是 **8G 显存 + 32GB 内存** 的机器——其中很大一部分是**机房退役/改造工作站**：
两条内存槽加不满、ECC 开关在固件里、显卡位是涡轮卡形态。本包所有参数按这批机器实测定版。

The target machine is **8 GB VRAM + 32 GB system RAM** — and a large share of those machines are
**converted ex-server-room workstations**: only two DIMM slots (no room to grow), firmware-level
ECC toggles, blower-style card bays. Every parameter in this pack is frozen from real measurement
on exactly this class of hardware.

### 与秋叶整合包的对比 / vs. the Qiuye (秋叶) integration pack

秋叶整合包是中文社区最普及的 N 卡整合方案。本包不替代它——补的是它不覆盖的坑位。
The Qiuye pack is the most widely used NVIDIA bundle in the Chinese community. This pack does not
replace it — it fills the gap that bundle does not cover.

| 维度 / Dimension | 秋叶整合包 / Qiuye Pack | 本包 / This Pack |
|---|---|---|
| 硬件生态 / Hardware | NVIDIA CUDA 为主 / CUDA-centric | **Intel Arc XPU** 原生（SYCL）/ native SYCL |
| 启动方式 / Launch | 图形启动器（绘世 / ComfyUI 启动器）/ GUI launcher | **无启动器**，bat 直启 main.py / no launcher, bat → main.py |
| 目标配置 / Target rig | N 卡 8~24G 显存 + 16~32G 内存 / NVIDIA 8–24G VRAM | **8G 显存 + 32G 内存**（工作站改造机典型配置）/ converted-workstation class |
| H3 视频跑径 / H3 video pipelines | 通用包未内置，需自配 / not bundled, DIY | **PIKA H3 Flex 4 条工作流开箱即用** / 4 workflows ready to run |
| 内存口径 / Memory SOP | 通用建议 / generic advice | **32G 硬口径**：页面文件 + nvfp4 档 + ECC 关（实测定版）/ hard SOP, measured on 32G rigs |
| 模型管理 / Models | 启动器内下载管理 / launcher-managed | 13 件清单 + hf-mirror 脚本（字节校验 / 断点续跑）/ manifest + script (byte-checked, resumable) |
| 依赖卫生 / Dep hygiene | N/A（N 卡生态） | **零 CUDA 残留**（KJNodes Sage 已切除）/ zero CUDA leftovers |

一包一句话：**给 N 卡之外那批工作站，一套和秋叶同级的开箱即用。**
One line: for the workstations outside the NVIDIA fold — plug-and-play at the same bar.

---

## 三、环境硬口径（先读这个）
## Environment Hard Requirements (read this first)

**以下不是建议，是能跑通的门槛。**
These are pass/fail thresholds, not suggestions.

| 项 / Item | 口径 / Requirement | 原因 / Why |
|---|---|---|
| 系统内存 / System RAM | **32 GB**（别指望加内存，很多机器只有两条槽）/ 32 GB (many boards have only two DIMM slots) | H3 文本编码器 + DiT 的驻留底线 / residency floor for H3 text encoder + DiT |
| 页面文件 / Page file | **必须设置**：初始 32G / 最大 64G，放 SSD / REQUIRED: 32G initial, 64G max, on SSD | 32GB 机唯一可扩展的"内存"，H3 加载期硬依赖 / the only expandable "RAM" — hard dep during H3 load |
| 文本编码器 / Text encoder | **只用 nvfp4 档** / nvfp4 build ONLY | int8 档 25.28 GB 在 32GB 机加载即段错误 / the int8 build (25.28 GB) segfaults at load on 32 GB |
| ECC | **关闭**（IGS → Graphics → ECC → 关闭 → 重启）/ OFF (IGS → Graphics → ECC → Off → reboot) | 开 = 可见 27.25G；关 = 31G。出货态默认关 / ON = 27.25G visible; OFF = 31G; ships OFF |
| 分辨率 / Resolution | 边长必须 **÷32** / both sides divisible by **32** | VAE/16 后 patch 2×2 要求潜空间两边均偶 / latent after /16 must be even×even for 2×2 patches |
| 锁页内存 / Pinned memory | 已默认关闭（OMNIXPU_PIN_MEMORY=0）/ off by default | 实测 ±0.1% 无差别；32GB 机上反而硬占不可换出内存 / ±0.1% measured; steals non-pageable RAM |

### 分辨率速查 / Resolution quick reference（÷32 网格 / grid）

| 场景 / Use case | 宽 × 高 | 备注 / Note |
|---|---|---|
| 720P 竖版 / 720P portrait | **704 × 1280** | ✅ 唯一合法值；**720 × 1280 会崩** / only legal value — **720×1280 crashes** |
| 540P 竖版 / 540P portrait | 544 × 960 | 省显存档 / VRAM-saving tier |
| 720P 横版 / 720P landscape | 1280 × 704 | 同网格转置 / same grid transposed |
| 1080P 竖版 / 1080P portrait | 704×1280 出片 + 二采放大 / render at 704×1280, then latent upscale | 直出 1088×1920 显存不够 / 1088×1920 direct does not fit |

帧长 / Frame count：17k+5（k=0,1,2…），243 帧 = 10.125s @24fps。

---

## 四、启动 / Quick Start

1. 整包解压到任意路径（建议 SSD，剩余 ≥100G）/ Extract anywhere (SSD, ≥100G free)
2. 双击 `启动_Intel_XPU.bat` / Double-click `启动_Intel_XPU.bat`
3. 浏览器开 `http://127.0.0.1:8188` / Open in browser

启动参数已按 B70 实测口径固化在 bat 里 / Launch parameters frozen from B70 measurement:

```
--reserve-vram 5 --cache-classic
```

- `--reserve-vram 5`：为系统/显示预留 5G，多卡负载唯一稳定值 / reserve 5G for OS+display; only stable value under multi-card load
- `--cache-classic`：避免新版默认缓存在 32GB 机上反复重载文本编码器（每轮省约 2.6 分钟）/ stops the new default cache from reloading the text encoder every round (~2.6 min saved per round)
- 备选 / Alternative（显存紧张时 try when VRAM-tight）：`--enable-dynamic-vram --reserve-vram 4`；遇 DEVICE_LOST 崩溃换回默认 / fall back to the default on DEVICE_LOST crashes

---

## 五、工作流 / Workflows（12 条，已挂 PIKA H3 Flex 跑径 / all wired to the PIKA H3 Flex path）

### H3 视频 / H3 video（4 条 / 4 items）

| 工作流 / Workflow | 用途 / Purpose |
|---|---|
| 图生视频_首帧_H3 | 单图 → 视频 / single image → video |
| 图生视频_首尾帧_H3 | 首尾帧夹逼 → 视频 / first+last frame interpolation |
| 图生视频_二采_H3 | 低分辨率出片 + latent 放大 / low-res render + latent upscale |
| 图生视频_打斗分镜_H3 | 动态大分镜 / dynamic action shots |

跑径已切 **PIKA H3 Flex**（LoRA 已挂：pika_h3_flex_fl2va / ref2va）。注意：**PIKA Flex 是蒸馏适配器，不能再叠其他加速 LoRA**（叠了必坏）。
The pipeline is already switched to **PIKA H3 Flex** (LoRAs attached: pika_h3_flex_fl2va / ref2va).
Note: **Flex is a distillation adapter — do not stack other acceleration LoRAs on top** (stacking breaks the output).

### Z-Image 出图 / Z-Image（8 条 / 8 items）

文生图 / 图生图 / 多参考等，走 z_image_turbo_int8_convrot + qwen_3_4b_fp8_mixed。
t2i / i2i / multi-reference etc., on z_image_turbo_int8_convrot + qwen_3_4b_fp8_mixed.

---

## 六、模型清单 / Model Manifest（13 个 / items，~76G）

全量包已内置；轻量口径用 `download_models.py` 从 hf-mirror 自取。
The full bundle ships them all; the lightweight track fetches them via `download_models.py` from hf-mirror.

| # | 相对路径 / Relative path | 大小 / Size | repo |
|---|---|---|---|
| 1 | diffusion_models/MiniMax/minimax_h3_fl2va_pruned_int8_convrot.safetensors | 19.5G | Comfy-Org/MiniMax-H3 |
| 2 | diffusion_models/MiniMax/minimax_h3_ref2va_pruned_int8_convrot.safetensors | 19.5G | Comfy-Org/MiniMax-H3 |
| 3 | diffusion_models/z_image_turbo_int8_convrot.safetensors | 5.8G | Comfy-Org/Z-Image-Turbo |
| 4 | text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors | 14.6G | Comfy-Org/MiniMax-H3 |
| 5 | text_encoders/qwen_3_4b_fp8_mixed.safetensors | 5.2G | Comfy-Org/Z-Image-Turbo |
| 6 | vae/minimax_h3_video_vae_fp16.safetensors | 4.9G | Comfy-Org/MiniMax-H3 |
| 7 | vae/minimax_h3_audio_vae_fp32.safetensors | 578M | Comfy-Org/MiniMax-H3 |
| 8 | vae/ae_zimage.safetensors | 320M | Comfy-Org/Z-Image-Turbo（repo 内名 ae.safetensors / named ae.safetensors upstream） |
| 9 | loras/pika_h3_flex_fl2va_v1_bf16.safetensors | 1.9G | Comfy-Org/MiniMax-H3 |
| 10 | loras/pika_h3_flex_ref2va_v1_bf16.safetensors | 1.9G | Comfy-Org/MiniMax-H3 |
| 11 | vae_approx/taeh3.safetensors | 22M | OzzyGT/taeh3 |
| 12 | latent_upscale_models/minimax_h3_latent_upscaler_3d_fp16.safetensors | 659M | Konteni2/Minimax_h3_latent_Upscaler |
| 13 | background_removal/birefnet.safetensors | 424M | Comfy-Org/BiRefNet |

### 轻量口径下载 / Lightweight download

```bash
# 依赖 / dep: pip install huggingface_hub
python download_models.py                # 全部 13 个 / all 13
python download_models.py --only h3     # 只下 H3 视频线 / H3 video line only
python download_models.py --only zimage # 只下 Z-Image 线 / Z-Image line only
python download_models.py --only aux    # 辅助件 / aux items
```

脚本走 hf-mirror.com 镜像，落地自动改名/建目录，重跑自动跳过已完整文件（字节校验）。
The script goes through the hf-mirror.com mirror, renames/creates directories as needed, and
re-runs automatically skip already-complete files (byte-count verified).

---

## 七、常见坑位 / Troubleshooting

| 现象 / Symptom | 原因 / Cause | 处置 / Fix |
|---|---|---|
| 文本编码器加载即崩溃 / Text encoder crashes at load | 用了 int8 档 / used the int8 build | 必须换 nvfp4 档（清单 #4）/ switch to the nvfp4 build (#4) |
| 720×1280 直接崩 / 720×1280 crashes instantly | 边长不 ÷32 / side not divisible by 32 | 用 704×1280 / use 704×1280 |
| 显存报 27.25G / VRAM reports 27.25G | ECC 开着 / ECC is on | IGS 关 ECC → 重启 → 31G / disable ECC in IGS → reboot → 31G |
| 每轮重新加载文本编码器 / Text encoder reloads every round | 缓存参数不对 / wrong cache flag | 用包内 bat 的 `--cache-classic` / use the bundled bat's `--cache-classic` |
| 叠加速 LoRA 后画面坏 / Broken output after stacking LoRAs | PIKA Flex 是蒸馏适配器 / Flex is a distillation adapter | 只留 Flex / keep Flex only |
| 内存爆 / 机器卡死 / OOM or system hang | 页面文件没设 / page file not set | 见「环境硬口径」/ see Environment Hard Requirements |

---

## 八、目录结构 / Directory Layout

```
Intel-Studio-Pack/
├── 启动_Intel_XPU.bat      # 双击启动（无管理器）/ double-click launch (no launcher)
├── README_SOP.md           # 本文件 / this file
├── download_models.py      # 轻量口径：模型下载 / model downloader (lightweight track)
├── python_embeded/         # 内置 Python + Intel XPU 运行时 / bundled Python + Intel XPU runtime
└── ComfyUI/
    ├── custom_nodes/       # KJNodes(CUDA已清/CUDA-cleaned) / TE-Speed / H3-VSA-XPU
    ├── user/default/workflows/  # 12 条工作流 / 12 workflows
    ├── input/              # voices/ + 示例件 / sample assets
    └── models/             # 13 个模型（全量包内置）/ 13 models (in the full bundle)
```

已做卫生 / Sanitized：零管理器件（无 app.py / manager.json）、零 CUDA 残留（KJNodes 已切除 Sage 引用）。
No manager components (no app.py / manager.json); zero CUDA leftovers (Sage references excised from KJNodes).
