# Intel-Studio-Pack 下载、安装与补丁说明
# Download, Install & Patch Guide

> **本文件是下载与安装口径的唯一权威**：网盘链接、校验值、补丁方法全部以本文件为准。
> 解压后包内 `README.md` / `README.zh-CN.md` 保留的早期链接与校验值已过时，如与本文件不一致，以本文件为准。
>
> **This file is the single source of truth** for download links, checksums and patch instructions.
> The links/checksums embedded in the in-package `README.md` / `README.zh-CN.md` are outdated; whenever
> they differ from this file, follow this file.

---

## 1. 下载地址 / Download

**百度网盘分享（国内）/ Baidu Netdisk (CN)**：

- 链接 Link：<https://pan.baidu.com/s/1cScBbO7Z0pZ0iJAR8z4BtQ?pwd=1ccp>
- 提取码 Code：`1ccp`

---

## 2. 下载文件清单 / Files in the Share

把下列文件**全部下载到同一个文件夹**（英文界面亦同）。
Download **all** files below **into the same folder**.

| 文件 File | 大小 Size (bytes) | 说明 Note |
|---|---:|---|
| `Intel-Studio-Pack_full_v1.tar.01` | 18,253,611,008 | 分卷 1 / 5（volume 1/5） |
| `Intel-Studio-Pack_full_v1.tar.02` | 18,253,611,008 | 分卷 2 / 5（volume 2/5） |
| `Intel-Studio-Pack_full_v1.tar.03` | 18,253,611,008 | 分卷 3 / 5（volume 3/5） |
| `Intel-Studio-Pack_full_v1.tar.04` | 18,253,611,008 | 分卷 4 / 5（volume 4/5） |
| `Intel-Studio-Pack_full_v1.tar.05` | 17,180,735,488 | 分卷 5 / 5，尾卷（tail volume） |
| `merge_volumes.bat` | 小 small | 一键合并 + 校验脚本（merge & verify） |
| `SHA256SUMS_volumes.txt` | 小 small | 逐卷 SHA256（per-volume hashes） |
| `SHA256_Intel-Studio-Pack_full_v1.tar.txt` | 小 small | 合并后整包 SHA256（merged tar hash） |
| `hotfix_comfy_ldm_models_v1.zip` | 92,224 | **仅旧包补丁**，2026-11-16 前下载者使用；新用户不需要 |

> 五个分卷合计 **90,195,179,520 字节（约 85 GiB）**，合并后是一个完整的
> `Intel-Studio-Pack_full_v1.tar`（模型权重压不动，故不压缩打包，`tar -xf` 直接解出）。
>
> The 5 volumes total **90,195,179,520 bytes (~85 GiB)** and merge into one
> `Intel-Studio-Pack_full_v1.tar` (weights don't compress, so the archive is stored uncompressed;
> `tar -xf` extracts everything directly).

---

## 3. 校验值 / Checksums

**逐卷 SHA256 / Per-volume SHA256**（与 `SHA256SUMS_volumes.txt` 一致 / matches the txt file）：

| 文件 File | SHA256 |
|---|---|
| `…tar.01` | `b41a35ffea59ffb4c9b6300491272ab76830dd9693b984d85055163ce839d674` |
| `…tar.02` | `bfb735beb0833f7ce7ad9722eb4c5d5b50c578a62ccddd099b1b4eadd07dce51` |
| `…tar.03` | `76a1f4055830706266227e606df0a568380872e24332cbe6b12bdceb1b1657ac` |
| `…tar.04` | `4ebb48b58dd04adb8e5fd08c67006c9eedd0a0acf2c87bddcf7eef2f58e5fc4d` |
| `…tar.05` | `deb63c3420f05f7165bbfc42bb8095a138fdd870b52d16f2d41f039e5b9678ef` |

**合并后整包 / Merged tar**：

- 大小 Size：`90,195,179,520` 字节 bytes
- SHA256：`3aa5f13ce3d77c9ac57f46e94aa6f7b032baff15e47423e020a91f5b9c9a45ec`

---

## 4. 解压安装步骤 / Install Steps

> ⚠️ **磁盘空间 / Disk space**：分卷 85 GiB + 合并后 tar 85 GiB + 解包 85 GiB，峰值约需 **255 GiB 可用空间**。
> 合并校验通过后可删分卷，解包完成且能启动后可删 tar。
> Peak usage ≈ **255 GiB free**: volumes + merged tar + extracted tree. Delete the volumes after a
> verified merge, and the tar after the pack starts successfully.

**① 合并分卷 / Merge the volumes**

- **方式 A（推荐 / recommended）**：双击 `merge_volumes.bat`。脚本自动检查 5 个分卷齐全 → 合并 →
  校验字节数与 SHA256 → 通过后给出解包命令。
  Double-click `merge_volumes.bat`. It checks all 5 volumes, merges, verifies byte count + SHA256,
  then prints the extract command.
- **方式 B（手动 / manual）**：

  ```bat
  :: Windows cmd（+ 两侧无空格 / no spaces around +）
  copy /b Intel-Studio-Pack_full_v1.tar.01+Intel-Studio-Pack_full_v1.tar.02+Intel-Studio-Pack_full_v1.tar.03+Intel-Studio-Pack_full_v1.tar.04+Intel-Studio-Pack_full_v1.tar.05 Intel-Studio-Pack_full_v1.tar
  ```

  ```bash
  # Git Bash / WSL / Linux
  cat Intel-Studio-Pack_full_v1.tar.0[1-5] > Intel-Studio-Pack_full_v1.tar
  ```

**② 校验合并结果 / Verify the merged tar**（合并大小必须是 `90,195,179,520` 字节）

```bat
certutil -hashfile Intel-Studio-Pack_full_v1.tar SHA256
```

```bash
sha256sum -c SHA256_Intel-Studio-Pack_full_v1.tar.txt
```

输出应为 `3aa5f13ce3d77c9ac57f46e94aa6f7b032baff15e47423e020a91f5b9c9a45ec`。
Expected output: `3aa5f13c…a45ec` (full value in section 3).

**③ 解包 / Extract**

```bat
tar -xf Intel-Studio-Pack_full_v1.tar
```

得到 / produces：`Intel-Studio-Pack\`（整包内容全在这一个文件夹里 / everything inside this folder）。

**④ 启动 / Launch**

进入 `Intel-Studio-Pack\`，双击 **`启动_Intel_XPU.bat`**，等控制台加载完后浏览器打开
**<http://127.0.0.1:8188>**，即进入 ComfyUI 界面。首次启动模型加载约需 1~3 分钟。
Double-click **`启动_Intel_XPU.bat`** inside `Intel-Studio-Pack\`, wait for the console to finish
loading, then open **<http://127.0.0.1:8188>**. First launch takes ~1–3 min for model loading.

**⑤ 跑通示例 / Try the samples**：左侧「工作流 / Workflows」菜单内 13 条工作流可直接加载运行，
`ComfyUI\input\` 自带示例素材（首帧图、参考角色/场景图、参考音频、带水印示例视频）。
All 13 workflows run out of the box; sample assets are bundled in `ComfyUI\input\`.

---

## 5. 解压后的包组成 / Package Contents

```text
Intel-Studio-Pack\
├─ 启动_Intel_XPU.bat              一键启动引擎（XPU 加速） / one-click launcher
├─ README.md · README.zh-CN.md     产品说明（口径以本文件为准）/ product readme (see note at top)
├─ README_SOP.md                   标准操作流程 / standard operating procedure
├─ download_models.py              轻量口径模型下载脚本（全量包用户可忽略）/ lightweight-track downloader
├─ merge_volumes.bat · SHA256*     合并与校验工具 / merge & verify tools
├─ python_embeded\                 内置 Python 运行时 / bundled Python runtime
└─ ComfyUI\
   ├─ custom_nodes\                48 项插件：H3 视频、Z-Image 出图、补帧、水印等 / 48 plugins
   ├─ models\                      13 个模型，约 76 GB / 13 models, ~76 GB
   │   ├─ diffusion_models\        MiniMax-H3 fl2va / ref2va（int8）+ Z-Image-Turbo（int8）
   │   ├─ text_encoders\           Qwen3-VL-32B（nvfp4）+ Qwen3-4B（fp8）
   │   ├─ vae\                     Z-Image AE + H3 视频 VAE + H3 音频 VAE
   │   ├─ vae_approx\              taeh3（潜空间预览 / latent preview）
   │   ├─ latent_upscale_models\   H3 潜空间超分 / latent upscaler
   │   ├─ loras\                   PIKA H3 Flex fl2va / ref2va
   │   └─ background_removal\      BiRefNet 抠像 / matting
   ├─ user\default\workflows\      13 条工作流（见下）/ 13 workflows
   └─ input\                       示例素材：首帧图、邦女郎三关键帧、ref\角色A/B/场景+参考音频、
                                   带水印示例视频 / sample assets
```

**13 条工作流 / 13 workflows**：

| 类别 Category | 工作流 Workflow（文件名去 .json / filename without .json） |
|---|---|
| H3 视频（5） | 图生视频_首帧_H3 · 图生视频_首尾帧_H3 · 打斗分镜_参考生视频_H3 · 二采H3工作流 · S4_演示_三关键帧_704x1280 |
| Z-Image 出图（7） | 人物档案_设定图_Z-Image · 参考重绘_单角色_Z-Image · 多参考出图_双人横版_Z-Image · 多参考出图_双人竖版_Z-Image · 定妆照_Z-Image-Turbo · 定妆照_定妆图_Z-Image · 提示词工坊_文生图_和参考生图 Z-Image |
| 视频工具（1） | 视频水印消除 |

---

## 6. hotfix 补丁说明 / Hotfix Patch（仅旧包用户 / for previous downloaders only）

**适用对象 / Who needs this**：**2026 年 11 月 16 日之前**下载过本整合包的用户。
如果这之后才下载（含本次分享的 5 分卷），**不需要**此补丁。
Users who downloaded the pack **before 16 Nov 2026**. If you downloaded after that date
(including the 5 volumes in this share), you do **not** need this patch.

**修复内容 / What it fixes**：旧包打包时有 3 处代码模块被误排除，导致启动报
`ModuleNotFoundError: comfy.ldm.models / comfy_api.input / src.models` 等缺件错误。
补丁共 45 个文件，**无需重新下载 85 GiB 全量包**。
Three code-module trees were mistakenly excluded from the old build, causing missing-module errors
at startup. This 45-file patch restores them — **no need to re-download the 85 GiB pack**.

**用法 / How to apply**：

1. 下载 `hotfix_comfy_ldm_models_v1.zip`（与分卷同一分享目录 / same share folder）。
2. 右键 →「解压到指定文件夹 / Extract to…」，目标选 **`Intel-Studio-Pack\` 包根目录**
   （即解压全量包后得到的那个文件夹，与 `ComfyUI\` 同级），勾选**覆盖/替换目标文件**。
   Extract into the **package root `Intel-Studio-Pack\`** (the folder produced when you extracted
   the big tar — the level that contains `ComfyUI\`), **overwriting** existing files.
3. zip 内路径以 `ComfyUI\…` 开头，解压后会自动落进包内对应位置，目录结构严丝合缝。
   Archive paths start with `ComfyUI\…`, so files land exactly where they belong.
4. 完成后照常双击 `启动_Intel_XPU.bat` 即可。
   Then launch `启动_Intel_XPU.bat` as usual.

**解压路径一句话 / In one line**：解压到 **`Intel-Studio-Pack\`** 包根目录下覆盖
（Extract to the `Intel-Studio-Pack\` package root, overwrite）。

---

## 7. 已知提示与常见问题 / Known Notices & FAQ

- **控制台提示 `seedvr2_videoupscaler` 导入警告，或 `VRGDG_LTXLoopingSampler` 提示缺
  `ComfyUI-LTXVideo`**：属已知非核心项（附属插件自身的入口问题/软依赖），包内 13 条工作流
  均不依赖它们，**不影响出图与出片**。
  Console warnings about `seedvr2_videoupscaler` or `VRGDG_LTXLoopingSampler` are known
  non-core items; none of the 13 workflows depend on them. Safe to ignore.
- **系统要求 / Requirements**：Windows 10/11 64 位、Intel Arc 独显（XPU）、建议系统内存 32 GB、
  显存 8 GB 起步。包内参数已按「8 GB 显存 + 32 GB 内存」实测定版，开箱即用。
  Windows 10/11 64-bit, Intel Arc discrete GPU (XPU), recommended 32 GB RAM + 8 GB VRAM or more.
  All presets are tuned for exactly this configuration.
- **下载慢 / Slow downloads**：非会员大文件会被限速，可用百度网盘客户端或迅雷断点续传；
  分卷的好处是断了只需补下那一个分卷。
  Non-VIP accounts get throttled; use the Baidu client or Xunlei with resume. With split volumes
  a broken transfer only requires re-downloading that one volume.
- **包内 README 的校验值对不上 / In-package README checksums don't match**：正常——那是早期口径。
  以本文件第 3 节为准。That's expected (old values). Use section 3 of this file.

---

*生成日期 / Generated: 2026-11-16 · 对应交付件 / for the 5-volume delivery in this share*
