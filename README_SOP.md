# ComfyUI Intel Arc 专版（产品坑位包）

**不含管理器启动界面**，引擎 + 跑径 + SOP 直出。双轨获取：

| 口径 | 内容 | 落点 |
|---|---|---|
| 全量包 | 引擎 + 节点 + 12 条工作流 + 13 个模型（~85G） | 百度网盘（分卷压缩） |
| 轻量口径 | 本 README + 下载脚本 + 模型清单 | GitHub |

---

## 一、环境硬口径（先读这个）

**目标配置 = 90% 用户的真实配置：8G 显存 + 32 GB 内存。** 以下是能跑通的门槛，不是建议。

| 项 | 口径 | 原因 |
|---|---|---|
| 系统内存 | **32 GB**（不要指望加内存，很多机器只有两条槽） | H3 文本编码器 + DiT 的驻留底线 |
| 页面文件 | **必须设置**，建议初始 32G / 最大 64G，放 SSD | 32GB 机唯一可扩展的"内存"，H3 加载期硬性依赖 |
| 文本编码器 | **只用 nvfp4 档**（qwen3vl_32b_minimax_h3_nvfp4_awq） | int8 档 25.28 GB 在 32GB 机加载即段错误崩溃 |
| ECC | **关闭**（IGS → Graphics → ECC → 关闭 → 重启） | 开 ECC 可见显存 27.25G，关后 31G；出货态默认关 |
| 分辨率 | 边长必须 **÷32** | H3 的 VAE/16 后 patch 2×2 要求潜空间两边均偶 |
| 锁页内存 | 已默认关闭（OMNIXPU_PIN_MEMORY=0） | 实测端到端 ±0.1% 无差别，32GB 机上反而硬占不可换出内存 |

### 分辨率速查（÷32 网格，常用档）

| 场景 | 宽 × 高 | 备注 |
|---|---|---|
| 720P 竖版 | **704 × 1280** | ✅ 唯一合法值，**720 × 1280 会崩** |
| 540P 竖版 | 544 × 960 | 省显存档 |
| 720P 横版 | 1280 × 704 | 同网格转置 |
| 1080P 竖版 | 704 × 1280 ×2 采样后二采放大 | 直接 1088×1920 显存不够 |

帧长：17k+5（k=0,1,2…），243 帧 = 10.125s @24fps。

---

## 二、启动

1. 整包解压到任意路径（建议 SSD，剩余空间 ≥100G）
2. 双击 `启动_Intel_XPU.bat`
3. 浏览器开 `http://127.0.0.1:8188`

启动参数已按 B70 实测口径固化在 bat 里：

```
--reserve-vram 5 --cache-classic
```

- `--reserve-vram 5`：为系统/显示预留 5G，多卡负载唯一稳定值
- `--cache-classic`：避免新版默认缓存在 32GB 机上反复重载文本编码器（每轮省约 2.6 分钟）
- 备选（显存紧张试）：`--enable-dynamic-vram --reserve-vram 4`，遇 DEVICE_LOST 崩溃换回默认

---

## 三、工作流（12 条，已挂 PIKA H3 Flex 跑径）

### H3 视频（4 条）

| 工作流 | 用途 |
|---|---|
| 图生视频_首帧_H3 | 单图 → 视频 |
| 图生视频_首尾帧_H3 | 首尾帧夹逼 → 视频 |
| 图生视频_二采_H3 | 低分辨率出片 + latent 放大 |
| 图生视频_打斗分镜_H3 | 动态大分镜 |

跑径已切 **PIKA H3 Flex**（LoRA 已挂：pika_h3_flex_fl2va / ref2va）。注意：**PIKA Flex 是蒸馏适配器，不能再叠其他加速 LoRA**（叠了必坏）。

### Z-Image 出图（8 条）

文生图 / 图生图 / 多参考等，走 z_image_turbo_int8_convrot + qwen_3_4b_fp8_mixed。

---

## 四、模型清单（13 个，~76G）

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
python download_models.py            # 全部 13 个
python download_models.py --only h3  # 只下 H3 视频线（1/2/4/6/7/9/10/11/12）
python download_models.py --only zimage  # 只下 Z-Image 线（3/5/8）
```

脚本走 hf-mirror.com 镜像，落地自动改名/建目录，重跑自动跳过已完整文件。

---

## 五、常见坑位

| 现象 | 原因 | 处置 |
|---|---|---|
| 文本编码器加载即崩溃 | 用了 int8 档 | 必须换 nvfp4 档（清单 #4） |
| 720×1280 直接崩 | 边长不 ÷32 | 用 704×1280 |
| 显存报 27.25G | ECC 开着 | IGS 关 ECC → 重启 → 31G |
| 每轮重新加载文本编码器 | 缓存参数不对 | 用包内 bat 的 `--cache-classic` |
| 叠加速 LoRA 后画面坏 | PIKA Flex 是蒸馏适配器 | 移除其他加速 LoRA 只留 Flex |
| 内存爆 / 机器卡死 | 页面文件没设 | 见「一、环境硬口径」 |

---

## 六、目录结构

```
Intel-Studio-Pack/
├── 启动_Intel_XPU.bat      # 双击启动（无管理器）
├── README_SOP.md           # 本文件
├── download_models.py      # 轻量口径：模型下载脚本
├── python_embeded/         # 内置 Python + Intel XPU 运行时
└── ComfyUI/
    ├── custom_nodes/       # KJNodes(CUDA已清) / TE-Speed / H3-VSA-XPU 等
    ├── user/default/workflows/  # 12 条工作流
    ├── input/              # voices/ + 示例件
    └── models/             # 13 个模型（全量包内置）
```

已做卫生：零管理器件（无 app.py / manager.json）、零 CUDA 残留（KJNodes 已切除 Sage 引用）。
