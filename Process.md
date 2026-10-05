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

## Phase 1 — Dataset Inspection ⏳

- 대기: `data/raw/`에 데이터셋 추가 필요
