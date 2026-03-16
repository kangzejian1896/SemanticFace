#!/usr/bin/env bash
# -*- coding: utf-8 -*-
set -e
set -o pipefail
CONDA_ROOT="/opt/conda"

if [ -f "${CONDA_ROOT}/etc/profile.d/conda.sh" ]; then
  . "${CONDA_ROOT}/etc/profile.d/conda.sh"
else
  echo "ERROR: ${CONDA_ROOT}/etc/profile.d/conda.sh not found."
  exit 1
fi


export MODELSCOPE_CACHE=./cache  #The base model will be downloaded to this folder during the first run.
export PYTORCH_ALLOC_CONF=expandable_segments:True

export IMAGE_MAX_TOKEN_NUM=1024
export VIDEO_MAX_TOKEN_NUM=128
export FPS_MAX_FRAMES=16



CUDA_VISIBLE_DEVICES=0 \
VLLM_DISABLE_DISTRIBUTED=1 \
swift infer \
    --model Qwen/Qwen3-VL-4B-Instruct \
    --adapters ./adapters\
    --infer_backend vllm \
    --temperature 0 \
    --val_dataset ./example.jsonl\
    --result_path ./example_result.jsonl
