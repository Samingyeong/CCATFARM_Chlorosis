# Potato Chlorosis AI Project

## Current Project State

현재 프로젝트는 초기 상태이다.

아직 다음 요소가 존재하지 않는다.

- Dataset
- Annotation
- Model code
- Training code
- Trained weights

따라서 첫 작업은 모델 구현이 아니라
프로젝트 bootstrap과 개발환경 구성이다.

---

# Final Goal

최종 목표는 Potato RGB image에서 각 잎을 instance 단위로 분리하고
다음 상태를 판별하는 AI 모델을 만드는 것이다.

Classes:

- Healthy
- Chlorosis
- Leaf Curling

참고 학습 흐름:

Potato RGB Images
→ Mask2Former
→ leaf instance segmentation
→ clearly labeled leaves + Unknown leaves
→ EfficientNet-B1
→ pseudo-label / label refinement
→ Healthy / Chlorosis / Leaf Curling
→ Mask2Former retraining
→ Final Instance Segmentation Model

---

# Development Strategy

현재는 데이터셋이 없으므로
dataset-specific code를 작성하지 않는다.

다음 순서로 진행한다.

## Phase 0 — Bootstrap

1. repository 구조 확인
2. Python 개발환경 제안
3. requirements 초안 작성
4. 기본 폴더 구조 생성
5. config 파일 틀 생성
6. README 작성
7. GPU / CUDA 환경 확인 방법 준비

실제 학습 코드는 아직 작성하지 않는다.

---

## Phase 1 — Dataset Inspection

데이터셋이 추가된 이후 수행.

반드시 확인:

- directory structure
- image count
- image resolution
- annotation format
- classes
- instance count
- train/val/test split
- Unknown class
- class imbalance

실제 파일 확인 전에는 annotation 구조를 가정하지 않는다.

---

## Phase 2 — Mask2Former Stage 1

목적:

potato leaf instance segmentation

데이터셋 annotation 형식이 확인된 이후 구현한다.

---

## Phase 3 — EfficientNet-B1

Stage 1에서 분리된 leaf instance를 사용한다.

목적:

- Healthy
- Chlorosis
- Leaf Curling

분류 및 Unknown label refinement.

---

## Phase 4 — Pseudo Label Refinement

Unknown sample에 대해
EfficientNet-B1 confidence를 기반으로 pseudo-label을 생성한다.

원본 annotation을 절대 덮어쓰지 않는다.

---

## Phase 5 — Final Mask2Former

refined annotation을 이용해 Mask2Former를 다시 학습한다.

최종 출력:

- instance mask
- class
- confidence

---

# Project Structure

data/
  raw/
  processed/
  refined_labels/
  splits/

configs/
  mask2former_stage1.yaml
  efficientnet_b1.yaml
  mask2former_final.yaml

src/
  datasets/
  segmentation/
  classification/
  pseudo_label/
  visualization/
  utils/

outputs/
  stage1/
  classifier/
  pseudo_labels/
  final/

scripts/

requirements.txt
README.md

---

# Environment Rules

환경 확인 전 특정 CUDA 버전을 가정하지 않는다.

먼저 확인:

- OS
- Python version
- GPU
- NVIDIA driver
- CUDA availability

그 결과에 맞춰 PyTorch 설치 방식을 결정한다.

---

# Code Rules

- dataset path 하드코딩 금지
- checkpoint path 하드코딩 금지
- 원본 데이터 수정 금지
- 큰 단일 스크립트 금지
- config 기반 관리
- 실행되지 않은 코드는 완료됐다고 하지 않는다
- 실제 데이터가 없을 때 dummy format을 정답처럼 만들지 않는다

---

# Shared Repository

Kiro와 Claude Code가 같은 프로젝트 파일을 사용한다.

Claude는 수정 전에:

1. repository 상태 확인
2. 관련 파일 읽기
3. git diff 확인
4. 기존 변경사항 보존

을 우선한다.

---

# First Task

첫 실행 시:

아직 모델을 만들지 말 것.

먼저 다음만 수행한다.

1. 현재 repository 구조 확인
2. 필요한 기본 폴더 구조 제안
3. Python 환경 구성 방식 제안
4. requirements 초안 제안
5. Mask2Former / EfficientNet-B1 구현 라이브러리 후보 비교
6. 향후 dataset이 들어왔을 때의 작업 흐름 정리

실제 파일 생성 또는 수정 전에
먼저 계획을 보고하고 기다린다.