# Process

진행 상황 요약 (핵심만).

## Phase 0 — Bootstrap ✅ (2026-10-05)

**한 일**
- 프로젝트 전용 git repo 생성 (`main`)
- 폴더 구조: `data/`, `configs/`, `src/`, `outputs/`, `scripts/`
- `requirements.txt`, `README.md`, config 4개 (데이터 의존 값은 `null`)
- `scripts/check_env.py` — 환경 정보 JSON 기록
- README 가독성 개선 (목차 · 표 · 빠른 시작 섹션)

**환경**
| | 로컬 PC | 연구실 서버 (gpu-server-2) |
|---|---|---|
| 용도 | 코드 작성 / 데이터 점검 | 학습 |
| GPU | 없음 (Intel Iris Xe) | RTX 5090 32GB |
| Python | 3.14 (venv 미생성) | 3.12.15 (`~/chlorosis/.venv`) |
| PyTorch | 2.13 CPU | 2.14.1+cu130 ✔ CUDA 동작 확인 |

- 서버: `source ~/chlorosis/env.sh` 로 사용, `rm -rf ~/chlorosis` 로 전체 삭제
- 라이브러리: Mask2Former = HF Transformers, EfficientNet-B1 = torchvision

**미해결**
- 서버 비밀번호 변경 + SSH key 전환 권장
- 서버 코드 동기화: git clone/pull 방식으로 전환 (README 4장). 접속정보는 `.env`로 분리(`.env.example` 제공, `.env`는 git 제외)

## Phase 1 — Dataset Inspection ⏳ (2026-10-05~)

**데이터 위치 (서버)**
- 코드: `~/chlorosis_repo` (git clone, `07fcc97`)
- 원본: `data/raw/Potato Crop abiotic stressors interveinal Chlorosis and Leaf Curling.rar` (1.98GB, RAR5, 무결성 OK)
- 압축 해제본: `data/raw/potato_chlorosis/{images,labels}/` — 원본 rar와 함께 **읽기 전용**
- `unrar` 7.12 단독 바이너리: `~/chlorosis/.tools/rar/`

**확인 결과**
| 항목 | 값 |
|---|---|
| 구성 | PNG 149장 / txt 149개, stem 1:1 매칭 |
| 해상도 | 3456×3456 (127장), 3060×4080 (22장), 전부 RGB |
| Annotation | YOLO segmentation polygon (`class x1 y1 ...`, 0~1 정규화) |
| Instance | 총 4,244개, 이미지당 3~80 (평균 28.5), 빈/깨진 라벨 없음 |
| 공식 split | 없음 |

| id | class (사용자 확인) | instance | 포함 이미지 |
|---|---|---|---|
| 0 | Unknown | 1,239 | 119 |
| 1 | Interveinal Chlorosis | 802 | 68 |
| 2 | Leaf Curling | 820 | 68 |
| 3 | Healthy | 1,383 | 77 |

- `configs/base.yaml`에 dataset 경로 · 형식 · `raw_class_map` · `unknown_label` 반영

**남은 작업**
- polygon 시각화로 라벨 품질 확인
- 이미지 단위 train/val/test split 계획 (class 분포 고려)
