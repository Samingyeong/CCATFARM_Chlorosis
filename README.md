# Potato Chlorosis AI

감자 RGB 이미지에서 잎을 instance 단위로 분리하고 각 잎을 **Healthy / Chlorosis / Leaf Curling**으로 판별하는 모델 프로젝트.

참고 학습 흐름:

```
Potato RGB Images
→ Mask2Former (Stage 1, leaf instance segmentation)
→ clearly labeled leaves + Unknown leaves
→ EfficientNet-B1 (학습 단계 보조 모델)
→ pseudo-label / label refinement
→ Mask2Former retraining
→ Final Instance Segmentation Model (mask + class + confidence)
```

## 현재 상태

Phase 0 (bootstrap) — 폴더 구조, 환경, config 틀만 존재한다.
데이터셋, annotation, 모델/학습 코드는 아직 없다. 상세 원칙은 `CLAUDE.md` 참고.

## 폴더 구조

### 1) 프로젝트 구조 (git repo — 로컬/서버 공통)

GitHub 저장소의 구조. `git clone` 하면 로컬이든 서버든 동일하게 생성된다.
`data/raw`와 `outputs`는 내용이 git에 포함되지 않으므로 clone 직후에는 폴더만 있고 비어 있다.

```
chlorosis/            ← git repo 루트
  data/
    raw/              원본 데이터 (수정 금지, git 미포함 → clone 시 비어 있음)
    processed/        전처리 결과 (leaf crop 등)
    refined_labels/   pseudo-label로 정제된 annotation (원본과 별도)
    splits/           원본 이미지 단위 train/val/test split
  configs/
    base.yaml                 공통 경로 / seed / class
    mask2former_stage1.yaml
    efficientnet_b1.yaml
    mask2former_final.yaml
  src/
    datasets/ segmentation/ classification/ pseudo_label/ visualization/ utils/
  outputs/            실험 결과 (git 미포함)
    stage1/ classifier/ pseudo_labels/ final/   실험별 하위 폴더 (예: 2026-10-05_1530/)
    env/                                        check_env.py 결과
  scripts/
    check_env.py
```

### 2) 서버 실행 환경 구조 (연구실 GPU 서버)

서버에서는 **환경 폴더**와 **프로젝트(clone) 폴더**가 분리된다.
환경은 통째로 `rm -rf ~/chlorosis`로 지울 수 있도록 한곳에 격리한다.
학습은 서버에서만 수행하며, 데이터셋도 서버의 `data/raw`에만 둔다 (로컬에는 저장공간/GPU 없음).

```
~/chlorosis/          ← 환경 전용 (git repo 아님, 삭제 가능)
  env.sh              경로 / 캐시 위치 설정 스크립트
  .venv/              uv 가상환경 (Python 3.12)
  .tools/             uv 바이너리
  (HuggingFace 가중치 캐시 등)

<clone 위치>/chlorosis/   ← git repo (위 "1) 프로젝트 구조"와 동일)
  data/raw/           ★ 팀원이 데이터셋을 업로드하는 위치
  ...
```

## 환경 구성

권장: **Python 3.12 + venv**.
PyTorch는 CUDA 환경마다 설치 명령이 다르므로 `requirements.txt`에 포함하지 않고 먼저 따로 설치한다.

### 로컬 PC (Windows, NVIDIA GPU 없음 — 코드 작성 / 데이터 점검용)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
python scripts/check_env.py
```

### 연구실 서버 (CUDA GPU — 학습용)

확인된 환경 (2026-10-05, `outputs/env/env_gpu-server-2_*.json`):

| 항목 | 값 |
|---|---|
| OS | Ubuntu 22.04.5 LTS |
| GPU | NVIDIA GeForce RTX 5090 32GB (compute capability 12.0, Blackwell) |
| Driver | 595.91.07 (지원 CUDA 13.2) |
| 시스템 Python | 3.10.12 (`ensurepip` 없음 → `python3 -m venv` 불가) |
| 프로젝트 Python | 3.12.15 (uv managed) |
| PyTorch | 2.14.1+cu130 |

RTX 5090(sm_120)은 CUDA 12.8 이상 빌드가 필요하므로 cu126 이하 wheel은 사용하지 않는다.

시스템(sudo/apt)을 건드리지 않도록 **uv, Python, venv, 모든 캐시를 `~/chlorosis` 하나에 가둔다.**
`scripts/server_env.sh`가 서버의 `~/chlorosis/env.sh`로 복사되어 경로와 캐시 위치를 지정한다.

```bash
# 최초 1회 설치
mkdir -p ~/chlorosis && cd ~/chlorosis
# (scripts/server_env.sh → ~/chlorosis/env.sh, requirements.txt, scripts/ 복사)
source env.sh
curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$CHLOROSIS_HOME/.tools/bin" UV_NO_MODIFY_PATH=1 sh
uv venv --python 3.12 .venv
source env.sh
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130
uv pip install -r requirements.txt
python scripts/check_env.py      # torch.cuda_available == true 확인

# 이후 접속할 때마다
source ~/chlorosis/env.sh

# 전체 삭제 (venv, Python, 캐시, HF 가중치 포함)
rm -rf ~/chlorosis
```

서버에서 실제 설치된 버전은 `requirements.lock.gpu-server.txt`에 고정되어 있다:

```bash
uv pip install -r requirements.lock.gpu-server.txt --index-url https://download.pytorch.org/whl/cu130 --extra-index-url https://pypi.org/simple
```

## 주요 라이브러리 선택

| 역할 | 선택 | 이유 |
|---|---|---|
| Mask2Former | Hugging Face Transformers `Mask2FormerForUniversalSegmentation` | 유지보수 중, pip 설치만으로 동작, COCO-instance 사전학습 가중치 제공. 공식 Detectron2 기반 repo는 archived 상태이고 CUDA op 컴파일이 필요 |
| EfficientNet-B1 | torchvision `efficientnet_b1` (ImageNet) | 추가 의존성 없음. timm은 대안 |
| Segmentation 평가 | pycocotools | mask AP / AP50 / AP75 / class AP |
| Classification 평가 | scikit-learn | precision / recall / F1 / macro F1 / confusion matrix |

## 원칙 요약

- `data/raw/`의 원본 데이터와 원본 annotation은 수정하지 않는다.
- 경로, 하이퍼파라미터, class 이름, threshold는 `configs/*.yaml`에서 관리한다.
- split은 원본 이미지 단위로 한다 (같은 이미지의 leaf crop이 train/test에 나뉘지 않도록).
- Chlorosis는 색 변화 증상이므로 hue / saturation augmentation은 기본 비활성.
- 실행하지 않은 코드는 완료로 보고하지 않는다.
