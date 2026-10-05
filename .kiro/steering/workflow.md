---
inclusion: always
---

# Development Workflow

현재 프로젝트에는 아직:

- 모델 코드 없음
- 데이터셋 없음
- annotation 없음
- training environment 미구축

상태이다.

따라서 다음 순서로 개발한다.

## Phase 0 — Project Bootstrap

먼저:

1. 프로젝트 폴더 구조 생성
2. Python environment 구성 방법 결정
3. requirements 초안 작성
4. config 구조 생성
5. README 기본 작성
6. 실행 환경 확인
   - Python
   - PyTorch
   - CUDA
   - GPU

이 단계에서는 실제 모델 학습 코드를 만들지 않는다.

## Phase 1 — Dataset Integration

데이터셋이 추가된 뒤에:

1. 데이터셋 폴더 구조 확인
2. 이미지 개수 확인
3. annotation format 확인
4. class 확인
5. split 확인
6. Unknown label 존재 여부 확인

그 후에 dataset loader를 구현한다.

## Phase 2 — Stage 1 Mask2Former

데이터 구조가 확인된 뒤 구현한다.

## Phase 3 — EfficientNet-B1

leaf crop 생성과 label refinement 구현.

## Phase 4 — Pseudo Label

Unknown label refinement.

## Phase 5 — Final Mask2Former

refined annotation 기반 재학습.

## Important

데이터가 없는데 임의의 COCO / YOLO / mask format을 가정하지 않는다.

실행하지 않은 코드를 완료됐다고 보고하지 않는다.

Kiro와 Claude Code가 같은 파일을 공유하므로
동시에 같은 파일을 수정하지 않는다.