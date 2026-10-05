---
inclusion: always
---

# Project Structure

기본 프로젝트 구조:

project/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── refined_labels/
│   └── splits/
│
├── configs/
│   ├── mask2former_stage1.yaml
│   ├── efficientnet_b1.yaml
│   └── mask2former_final.yaml
│
├── src/
│   ├── datasets/
│   ├── segmentation/
│   ├── classification/
│   ├── pseudo_label/
│   ├── visualization/
│   └── utils/
│
├── outputs/
│   ├── stage1/
│   ├── classifier/
│   ├── pseudo_labels/
│   └── final/
│
├── scripts/
│
├── CLAUDE.md
├── requirements.txt
├── README.md
└── .gitignore

## Rules

- data/raw는 원본 데이터 전용
- 원본 데이터는 수정하지 않는다
- 학습 결과는 outputs에 저장
- 설정값은 configs에서 관리
- 모델별 역할을 파일 단위로 분리
- 임시 파일을 프로젝트 루트에 흩뿌리지 않는다