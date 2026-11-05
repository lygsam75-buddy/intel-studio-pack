# -*- coding: utf-8 -*-
r"""ComfyUI Intel Arc 专版 - 模型下载脚本（轻量口径）。

网络：huggingface.co 直连不通时走 hf-mirror.com 镜像。
落地：脚本所在目录下的 ComfyUI\models\（解压包体后运行）。
重跑自动跳过已完整文件（按字节数校验）。

用法：
  python download_models.py               # 全部 13 个
  python download_models.py --only h3     # H3 视频线
  python download_models.py --only zimage # Z-Image 出图线
  python download_models.py --only aux    # 辅助件（taeh3 / upscaler / birefnet）

依赖：pip install huggingface_hub
"""
import argparse
import os
import shutil
import sys
import time

MIRROR = 'https://hf-mirror.com'
os.environ['HF_ENDPOINT'] = MIRROR
os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY', '1')

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, 'ComfyUI', 'models')
MANIFEST = os.path.join(HERE, '_dl_manifest.jsonl')

# (分组, repo, repo内路径, 本地相对路径, 期望字节数)
JOBS = [
    # ---- H3 视频线 ----
    ('h3', 'Comfy-Org/MiniMax-H3',
     'diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors',
     'diffusion_models/MiniMax/minimax_h3_fl2va_pruned_int8_convrot.safetensors',
     20970379616),
    ('h3', 'Comfy-Org/MiniMax-H3',
     'diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors',
     'diffusion_models/MiniMax/minimax_h3_ref2va_pruned_int8_convrot.safetensors',
     20970379616),
    ('h3', 'Comfy-Org/MiniMax-H3',
     'text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors',
     'text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors',
     15687142551),
    ('h3', 'Comfy-Org/MiniMax-H3',
     'vae/minimax_h3_video_vae_fp16.safetensors',
     'vae/minimax_h3_video_vae_fp16.safetensors',
     5207808496),
    ('h3', 'Comfy-Org/MiniMax-H3',
     'vae/minimax_h3_audio_vae_fp32.safetensors',
     'vae/minimax_h3_audio_vae_fp32.safetensors',
     605254808),
    ('h3', 'Comfy-Org/MiniMax-H3',
     'loras/pika_h3_flex_fl2va_v1_bf16.safetensors',
     'loras/pika_h3_flex_fl2va_v1_bf16.safetensors',
     1956172304),
    ('h3', 'Comfy-Org/MiniMax-H3',
     'loras/pika_h3_flex_ref2va_v1_bf16.safetensors',
     'loras/pika_h3_flex_ref2va_v1_bf16.safetensors',
     1956172304),
    # ---- Z-Image 出图线 ----
    ('zimage', 'Comfy-Org/Z-Image-Turbo',
     'split_files/diffusion_models/z_image_turbo_int8_convrot.safetensors',
     'diffusion_models/z_image_turbo_int8_convrot.safetensors',
     6201001296),
    ('zimage', 'Comfy-Org/Z-Image-Turbo',
     'split_files/text_encoders/qwen_3_4b_fp8_mixed.safetensors',
     'text_encoders/qwen_3_4b_fp8_mixed.safetensors',
     5631994051),
    ('zimage', 'Comfy-Org/Z-Image-Turbo',
     'split_files/vae/ae.safetensors',   # repo 内名 ae.safetensors，落地改名 ae_zimage
     'vae/ae_zimage.safetensors',
     335304388),
    # ---- 辅助件 ----
    ('aux', 'OzzyGT/taeh3',
     'taeh3.safetensors',
     'vae_approx/taeh3.safetensors',
     22709752),
    ('aux', 'Konteni2/Minimax_h3_latent_Upscaler',
     'minimax_h3_latent_upscaler_3d_fp16.safetensors',
     'latent_upscale_models/minimax_h3_latent_upscaler_3d_fp16.safetensors',
     690592672),
    ('aux', 'Comfy-Org/BiRefNet',
     'background_removal/birefnet.safetensors',
     'background_removal/birefnet.safetensors',
     444473596),
]


def rec(d):
    with open(MANIFEST, 'a', encoding='utf-8') as f:
        import json
        f.write(json.dumps(d, ensure_ascii=False) + '\n')


def complete(path, size):
    return os.path.isfile(path) and os.path.getsize(path) == size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='', help='h3 / zimage / aux，逗号分隔')
    args = ap.parse_args()
    only = {x.strip() for x in args.only.split(',') if x.strip()}

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        sys.exit('[X] 缺依赖：pip install huggingface_hub')

    import huggingface_hub
    print('[hf] %s | endpoint=%s' % (huggingface_hub.__version__, MIRROR), flush=True)

    jobs = [j for j in JOBS if not only or j[0] in only]
    ok = skip = fail = 0
    t_all = time.time()
    for grp, repo, rfile, rel, size in jobs:
        dest = os.path.join(MODELS, rel.replace('/', os.sep))
        if complete(dest, size):
            print('[跳过] 已完整 %s' % rel, flush=True)
            skip += 1
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        t0 = time.time()
        try:
            p = hf_hub_download(repo_id=repo, filename=rfile)
            # repo 内名与落地名不同时改名/挪位
            if os.path.abspath(p) != os.path.abspath(dest):
                shutil.move(p, dest)
            if not complete(dest, size):
                raise RuntimeError('size mismatch: got %s want %s' % (
                    os.path.getsize(dest) if os.path.exists(dest) else 'none', size))
            dt = time.time() - t0
            print('[OK] %s  %.2fGB  %.0fs' % (rel, size / 2 ** 30, dt), flush=True)
            rec(dict(group=grp, repo=repo, file=rfile, dest=dest,
                     gb=round(size / 2 ** 30, 3), sec=round(dt, 1), ok=True))
            ok += 1
        except Exception as e:
            print('[FAIL] %s :: %s' % (rel, e), flush=True)
            rec(dict(group=grp, repo=repo, file=rfile, dest=dest, ok=False, err=str(e)[:300]))
            fail += 1
            continue  # 单件失败不中断队列

    print('\n[DONE] ok=%d skip=%d fail=%d  %.0fs' % (ok, skip, fail, time.time() - t_all))
    if fail:
        sys.exit(1)


if __name__ == '__main__':
    main()
