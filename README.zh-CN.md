[English](README.md) · **简体中文**

# ComfyUI Intel Arc 专版（产品坑位包）

**不含管理器启动界面** —— 引擎 + 跑径 + SOP 直出。
ComfyUI on Intel Arc (XPU) 的产品坑位包：全部参数实测定版，坑位填平，开箱即用。

> 📦 **全量包（约 85 GB）** —— 引擎 + 12 条工作流 + 13 个模型，分卷压缩 + SHA256SUMS ——
> 走 **百度网盘** 分发（国内网盘下载；联系维护者获取分享链接）。
>
> 🪶 **轻量口径（本仓库）** —— 模型清单 + 字节校验下载脚本（13 个模型，约 76 GB，走 hf-mirror）。
> 引擎自备，或照主手册自行组装。

---

## 定位

目标机器是 **8G 显存 + 32GB 内存** —— 其中很大一部分是**机房退役/改造工作站**：
两条内存槽加不满、ECC 开关在固件里、显卡位是涡轮卡形态。本包所有参数按这批机器实测定版。
（10-12 核心改造测量机即是此配置：`Total VRAM 31907 MB, total RAM 31860 MB`。）

---

## 与秋叶 aki 版的对比

秋叶 aki 版（`ComfyUI-intel-aki-v1.1`）与本包同为 **Intel 专用包**，分工不同：
aki 版是「核心改造试验台」（OmniXPU 适配器层 + VSA/SLA/SolAttn 节点，带管理器），
本包是「产品坑位包」（无管理器、坑位填平、开箱即用）。不替代 aki 版 —— 本包的
跑径与 SOP 直接继承自它 10-12 的核心改造测量。

| 维度 | 秋叶 aki 版 | 本包 |
|---|---|---|
| 定位 | 核心改造试验台（v1.1） | **产品坑位包** |
| 启动方式 | 管理器启动界面 | **无启动器**，bat 直启 main.py |
| 内核 | OmniXPU 适配器层（attention/fp8/int8/vram-trim） | 继承同一内核口径 |
| 工作流 | 自配 | **12 条预挂 PIKA H3 Flex** 开箱即用 |
| 内存口径 | 10-12 实测后定口径 | **32G 硬口径**写成 SOP + 坑位表 |
| 模型管理 | 自管 | 13 件清单 + hf-mirror 脚本（字节校验） |
| 交付物 | 试验台本体 | 全量包（网盘）+ 轻量口径（本仓库） |

### 10-12 核心改造测量

同一 H3 图生视频工作流（6 步 turbo、480P 档、B70 + 32GB 内存机），端到端单轮：

| 测项 | 改动 | 端到端 | 结论 |
|---|---|---|---|
| ab_A_r15 | 基线（无适配器层） | 245.17 s | — |
| ab_B_r15 | OmniXPU 适配器层全开（attention/fp8/int8/vram-trim） | **142.94 s** | **1.71×** 端到端 |
| ab_B 锁页尝试 | pinned 3823 MB | 崩溃 | XPU torch 无 CUDA：`AssertionError: Torch not compiled with CUDA enabled` → **锁页内存不必开**（本包默认 `OMNIXPU_PIN_MEMORY=0`） |

启动链路（boot_clean）：OmniXPU 预启动 2.8 s、H3-VSA-XPU 0.0 s。

---

## 环境硬口径（先读这个 —— 以下不是建议，是能跑通的门槛）

| 项 | 口径 | 原因 |
|---|---|---|
| 系统内存 | **32 GB**（别指望加内存，很多机器只有两条槽） | H3 文本编码器 + DiT 的驻留底线 |
| 页面文件 | **必须设置**：初始 32G / 最大 64G，放 SSD | 32GB 机唯一可扩展的"内存"，H3 加载期硬依赖 |
| 文本编码器 | **只用 nvfp4 档** | int8 档 25.28 GB 在 32GB 机加载即段错误 |
| ECC | **关闭**（IGS → Graphics → ECC → 关闭 → 重启） | 开 = 可见 27.25G；关 = 31G。出货态默认关 |
| 分辨率 | 边长必须 **÷32** | VAE/16 后 patch 2×2 要求潜空间两边均偶 |
| 锁页内存 | 已默认关闭（`OMNIXPU_PIN_MEMORY=0`） | 实测 ±0.1% 无差别；32GB 机上反而硬占不可换出内存 |

### 分辨率速查（÷32 网格）

| 场景 | 宽 × 高 | 备注 |
|---|---|---|
| 720P 竖版 | **704 × 1280** | ✅ 唯一合法值；**720 × 1280 会崩** |
| 540P 竖版 | 544 × 960 | 省显存档 |
| 720P 横版 | 1280 × 704 | 同网格转置 |
| 1080P 竖版 | 704×1280 出片 + 二采放大 | 直出 1088×1920 显存不够 |

帧长：17k+5（k=0,1,2…），243 帧 = 10.125s @24fps。

---

## 快速开始

1. 整包解压到任意路径（建议 SSD，剩余 ≥100G）
2. 双击 `启动_Intel_XPU.bat`
3. 浏览器开 `http://127.0.0.1:8188`

启动参数已按 B70 实测口径固化在 bat 里：

```
--reserve-vram 5 --cache-classic
```

- `--reserve-vram 5`：为系统/显示预留 5G，多卡负载唯一稳定值
- `--cache-classic`：避免新版默认缓存在 32GB 机上反复重载文本编码器（每轮省约 2.6 分钟）
- 备选（显存紧张时）：`--enable-dynamic-vram --reserve-vram 4`；遇 DEVICE_LOST 崩溃换回默认

---

## 工作流（12 条，已挂 PIKA H3 Flex 跑径）

### H3 视频（4 条）

| 工作流 | 用途 |
|---|---|
| 图生视频_首帧_H3 | 单图 → 视频 |
| 图生视频_首尾帧_H3 | 首尾帧夹逼 → 视频 |
| 图生视频_二采_H3 | 低分辨率出片 + latent 放大 |
| 图生视频_打斗分镜_H3 | 动态大分镜 |

跑径已切 **PIKA H3 Flex**（LoRA 已挂：pika_h3_flex_fl2va / ref2va）。
**PIKA Flex 是蒸馏适配器，不能再叠其他加速 LoRA**（叠了必坏）。

### Z-Image 出图（8 条）

文生图 / 图生图 / 多参考等，走 z_image_turbo_int8_convrot + qwen_3_4b_fp8_mixed。

---

## 模型清单（13 个，约 76G）

全量包已内置；轻量口径用 `download_models.py` 从 hf-mirror 自取。

| # | 相对路径 | 大小 | repo |
|---|---|---|---|
| 1 | diffusion_models/MiniMax/minimax_h3_fl2va_pruned_int8_convrot.safetensors | 19.5G | Comfy-Org/MiniMax-H3 |
| 2 | diffusion_models/MiniMax/minimax_h3_ref2va_pruned_int8_convrot.safetensors | 19.5G | Comfy-Org/MiniMax-H3 |
| 3 | diffusion_models/z_image_turbo_int8_convrot.safetensors | 5.8G | Comfy-Org/Z-Image-Turbo |
| 4 | text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors | 14.6G | Comfy-Org/MiniMax-H3 |
| 5 | text_encoders/qwen_3_4b_fp8_mixed.safetensors | 5.2G | Comfy-Org/Z-Image-Turbo |
| 6 | vae/minimax_h3_video_vae_fp16.safetensors | 4.9G | Comfy-Org/MiniMax-H3 |
| 7 | vae/minimax_h3_audio_vae_fp32.safetensors | 578M | Comfy-Org/MiniMax-H3 |
| 8 | vae/ae_zimage.safetensors | 320M | Comfy-Org/Z-Image-Turbo（repo 内名 ae.safetensors） |
| 9 | loras/pika_h3_flex_fl2va_v1_bf16.safetensors | 1.9G | Comfy-Org/MiniMax-H3 |
| 10 | loras/pika_h3_flex_ref2va_v1_bf16.safetensors | 1.9G | Comfy-Org/MiniMax-H3 |
| 11 | vae_approx/taeh3.safetensors | 22M | OzzyGT/taeh3 |
| 12 | latent_upscale_models/minimax_h3_latent_upscaler_3d_fp16.safetensors | 659M | Konteni2/Minimax_h3_latent_Upscaler |
| 13 | background_removal/birefnet.safetensors | 424M | Comfy-Org/BiRefNet |

### 轻量口径下载

```bash
# 依赖：pip install huggingface_hub
python download_models.py                # 全部 13 个
python download_models.py --only h3     # 只下 H3 视频线
python download_models.py --only zimage # 只下 Z-Image 线
python download_models.py --only aux    # 辅助件
```

脚本走 hf-mirror.com 镜像，落地自动改名/建目录，重跑自动跳过已完整文件（字节校验）。

---

## 常见坑位

| 现象 | 原因 | 处置 |
|---|---|---|
| 文本编码器加载即崩溃 | 用了 int8 档 | 必须换 nvfp4 档（清单 #4） |
| 720×1280 直接崩 | 边长不 ÷32 | 用 704×1280 |
| 显存报 27.25G | ECC 开着 | IGS 关 ECC → 重启 → 31G |
| 每轮重新加载文本编码器 | 缓存参数不对 | 用包内 bat 的 `--cache-classic` |
| 叠加速 LoRA 后画面坏 | PIKA Flex 是蒸馏适配器 | 只留 Flex |
| 内存爆 / 机器卡死 | 页面文件没设 | 见「环境硬口径」 |

---

## 目录结构

```
Intel-Studio-Pack/
├── 启动_Intel_XPU.bat      # 双击启动（无管理器）
├── README.md               # English edition
├── README.zh-CN.md         # 本文件（简体中文）
├── download_models.py      # 轻量口径：模型下载
├── python_embeded/         # 内置 Python + Intel XPU 运行时
└── ComfyUI/
    ├── custom_nodes/       # KJNodes(CUDA已清) / TE-Speed / H3-VSA-XPU
    ├── user/default/workflows/  # 12 条工作流
    ├── input/              # voices/ + 示例件
    └── models/             # 13 个模型（全量包内置）
```

已做卫生：零管理器件（无 app.py / manager.json）、零 CUDA 残留（KJNodes 已切除 Sage 引用）。
