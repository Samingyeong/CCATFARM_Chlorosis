# Perilla leaves(Potato) Chlorosis AI

깻잎(감자) RGB 이미지에서 잎을 instance 단위로 분리하고 각 잎을 **Healthy / Chlorosis / Leaf Curling**으로 판별하는 모델 프로젝트.

| Class | 설명 | 시각화 색 |
|---|---|---|
| Healthy | 정상 잎 | 🟩 Green |
| **Chlorosis** | 황화 (핵심 대상) | 🟨 Yellow |
| Leaf Curling | 잎 말림 | 🟧 Orange |

> **현재 상태: Phase 0 완료** — 폴더 구조 · 환경 · config 틀만 존재.
> 데이터셋 / 모델 / 학습 코드는 아직 없음. 진행 기록은 [`Process.md`](Process.md), 작업 원칙은 [`CLAUDE.md`](CLAUDE.md).

---

## 목차

1. [학습 파이프라인](#1-학습-파이프라인)
2. [빠른 시작 (연구실 서버)](#2-빠른-시작-연구실-서버)
3. [폴더 구조](#3-폴더-구조)
4. [환경 설치](#4-환경-설치)
5. [기술 스택](#5-기술-스택)
6. [작업 원칙](#6-작업-원칙)

---

## 1. 학습 파이프라인

| 단계 | 모델 / 작업 | 출력 |
|:---:|---|---|
| 1 | **Mask2Former** (Stage 1) | 잎 instance mask (명확한 label + Unknown) |
| 2 | **EfficientNet-B1** | 잎 crop 분류 확률 |
| 3 | **Pseudo-label refinement** | Unknown 잎 → 정제된 label (별도 파일) |
| 4 | **Mask2Former** 재학습 (Final) | mask + class + confidence |

- EfficientNet-B1은 **학습 단계 보조 모델**이다. 최종 서비스에는 들어가지 않는다.
- 최종 서비스: `RGB Camera → Final Mask2Former → mask + class + confidence`

---

## 2. 빠른 시작 (연구실 서버)

학습은 **연구실 GPU 서버에서만** 한다. 서버 접속 후:

```bash
source ~/chlorosis/env.sh        # 가상환경 + 경로 설정 (접속할 때마다)
cd ~/chlorosis_repo              # 프로젝트(git) 폴더로 이동
git pull                         # 최신 코드 반영
python scripts/check_env.py      # (선택) GPU / 패키지 확인
```

| 하고 싶은 것 | 명령 |
|---|---|
| 환경 활성화 | `source ~/chlorosis/env.sh` |
| 환경 확인 | `python scripts/check_env.py` |
| 환경 전체 삭제 | `rm -rf ~/chlorosis` |

---

## 3. 폴더 구조

### 3-1. 프로젝트 (git repo — 로컬 / 서버 공통)

`git clone`하면 어디서든 같은 구조가 생긴다.
`data/`와 `outputs/`의 **내용물은 git에 포함되지 않으므로** clone 직후에는 빈 폴더다.

```
chlorosis/
├── data/                       ※ 내용물 git 미포함
│   ├── raw/                    원본 데이터 (수정 금지)
│   ├── processed/              전처리 결과 (leaf crop 등)
│   ├── refined_labels/         pseudo-label로 정제된 annotation
│   └── splits/                 원본 이미지 단위 train / val / test
├── configs/
│   ├── base.yaml               공통: 경로 · seed · class
│   ├── mask2former_stage1.yaml
│   ├── efficientnet_b1.yaml
│   └── mask2former_final.yaml
├── src/
│   ├── datasets/  segmentation/  classification/
│   └── pseudo_label/  visualization/  utils/
├── outputs/                    ※ 내용물 git 미포함
│   ├── stage1/  classifier/  pseudo_labels/  final/   (실험별 하위 폴더)
│   └── env/                    check_env.py 결과
├── scripts/
│   ├── check_env.py            환경 정보 기록
│   └── server_env.sh           서버 ~/chlorosis/env.sh 원본
├── requirements.txt
└── requirements.lock.gpu-server.txt
```

### 3-2. 연구실 서버

서버에서는 **환경 폴더**와 **프로젝트 폴더**가 따로 있다.

| 폴더 | 역할 | git |
|---|---|---|
| `~/chlorosis/` | 환경 전용: `env.sh`, `.venv/`, `.tools/`, 캐시 · HF 가중치 | ❌ (통째로 삭제 가능) |
| `<clone 위치>/chlorosis/` | 프로젝트 코드 (3-1과 동일) | ✅ |
| `<clone 위치>/chlorosis/data/raw/` | ★ **데이터셋 업로드 위치** | ❌ |

> 데이터셋은 서버에만 둔다 (로컬 PC는 GPU · 저장공간 부족).

---

## 4. 코드 동기화 (git clone / pull)

서버에는 `pscp` 수동 복사 대신 git으로 코드를 받는다.
**환경 폴더(`~/chlorosis`)와 코드 폴더(git clone)는 분리한다.**

접속 정보(호스트 · 포트 · 계정)는 git에 올리지 않고 로컬 `.env`로 관리한다.
`.env.example`을 복사해 값을 채운다 (`cp .env.example .env`).

```bash
# 교내망(내부) 접속
ssh <SERVER_USER>@<SERVER_HOST>

# 교외망(외부) 접속 — 포트 지정
ssh -p <SERVER_EXTERNAL_PORT> <SERVER_USER>@<SERVER_EXTERNAL_HOST>

# 최초 1회: 코드 clone (환경 폴더 ~/chlorosis 와는 별도 위치)
cd ~
git clone https://github.com/Samingyeong/CCATFARM_Chlorosis.git chlorosis_repo

# 이후 최신 코드 반영
cd ~/chlorosis_repo
git pull
```

> 데이터셋(`data/raw/`)과 학습 결과(`outputs/`)는 git에 포함되지 않으므로
> `git pull` 로 덮어쓰이거나 삭제되지 않는다. 서버에 올려둔 데이터는 그대로 유지된다.

---

## 5. 환경 설치

PyTorch는 CUDA 버전마다 설치 명령이 달라서 `requirements.txt`에 넣지 않았다. **먼저 따로 설치한다.**

### 5-1. 연구실 서버 (학습용)

**확인된 사양** (2026-10-05)

| 항목 | 값 |
|---|---|
| OS | Ubuntu 22.04.5 LTS |
| GPU | RTX 5090 32GB (Blackwell, sm_120) |
| Driver | 595.91.07 (CUDA 13.2까지 지원) |
| Python | 3.12.15 (uv로 설치, 시스템 Python 3.10은 사용 안 함) |
| PyTorch | 2.14.1 + cu130 |

> ⚠️ RTX 5090은 **CUDA 12.8 이상** 빌드가 필요하다. `cu126` 이하 wheel은 쓰지 않는다.

**최초 1회 설치**

sudo / apt를 쓰지 않고 uv · Python · venv · 캐시를 전부 `~/chlorosis` 안에 둔다.

```bash
# 0. clone한 repo에서 env.sh(= scripts/server_env.sh), requirements.txt, scripts/ 를 ~/chlorosis 로 복사
mkdir -p ~/chlorosis
cp ~/chlorosis_repo/scripts/server_env.sh ~/chlorosis/env.sh
cp ~/chlorosis_repo/requirements.txt ~/chlorosis/
cp -r ~/chlorosis_repo/scripts ~/chlorosis/
cd ~/chlorosis
source env.sh

# 1. uv 설치 (~/chlorosis/.tools/bin 안에만)
curl -LsSf https://astral.sh/uv/install.sh \
  | env UV_INSTALL_DIR="$CHLOROSIS_HOME/.tools/bin" UV_NO_MODIFY_PATH=1 sh

# 2. Python 3.12 가상환경
uv venv --python 3.12 .venv
source env.sh

# 3. 패키지 설치
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130
uv pip install -r requirements.txt

# 4. 확인 → torch.cuda_available 이 true 여야 함
python scripts/check_env.py
```

**고정 버전으로 재설치** (`requirements.lock.gpu-server.txt`, 아직 실행 검증 안 됨)

```bash
uv pip install -r requirements.lock.gpu-server.txt \
  --index-url https://download.pytorch.org/whl/cu130 \
  --extra-index-url https://pypi.org/simple
```

### 5-2. 로컬 PC (코드 작성 / 점검용, GPU 없음)

> ⚠️ 현재 로컬 PC에는 Python 3.12가 없다 (3.14만 있음). 로컬 venv는 아직 만들지 않았다.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
python scripts/check_env.py
```

---

## 6. 기술 스택

| 역할 | 선택 | 이유 |
|---|---|---|
| Instance segmentation | HF Transformers `Mask2FormerForUniversalSegmentation` | 유지보수 중, pip만으로 설치, COCO 사전학습 가중치 제공 |
| 분류 (보조) | torchvision `efficientnet_b1` (ImageNet) | 추가 의존성 없음 (timm은 대안) |
| Segmentation 평가 | pycocotools | mask AP · AP50 · AP75 · class AP |
| 분류 평가 | scikit-learn | precision · recall · F1 · confusion matrix |

> Detectron2 기반 공식 Mask2Former repo는 archived 상태이고 CUDA op 컴파일이 필요해서 쓰지 않는다.

---

## 7. 작업 원칙

- 🔒 `data/raw/`의 원본 데이터 · annotation은 **절대 수정하지 않는다.**
- ⚙️ 경로 · 하이퍼파라미터 · class 이름 · threshold는 **`configs/*.yaml`** 에서 관리한다.
- ✂️ split은 **원본 이미지 단위**로 나눈다 (같은 이미지의 잎이 train / test에 섞이지 않게).
- 🎨 Chlorosis는 색 변화 증상이다. hue / saturation augmentation은 **기본적으로 끈다.**
- ✅ 실행해보지 않은 코드는 완료로 보고하지 않는다.
