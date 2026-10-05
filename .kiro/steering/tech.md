---
inclusion: always
---

# Technology Stack

## Core

- Python
- PyTorch
- CUDA GPU 사용 고려

## Segmentation

최종 후보:
- Mask2Former

우선 검토:
- Hugging Face Transformers
- Detectron2

유지보수 가능한 구현을 우선한다.

## Classification

- EfficientNet-B1

권장 구현:
- torchvision
또는
- timm

## Supporting Libraries

예상 후보:

- torch
- torchvision
- transformers
- accelerate
- timm
- opencv-python
- pillow
- numpy
- pandas
- scikit-learn
- matplotlib
- pyyaml

실제 requirements는 구현 방식이 정해진 뒤 확정한다.

## Configuration

다음 값은 코드에 하드코딩하지 않는다.

- dataset path
- checkpoint path
- batch size
- learning rate
- epochs
- input size
- seed
- num workers
- class names
- confidence threshold
- pseudo-label threshold

YAML config 기반으로 관리한다.

## Important

데이터셋이 아직 존재하지 않으므로
dataset-specific loader를 먼저 만들지 않는다.

가짜 annotation 구조를 가정해서 구현하지 않는다.

환경 설정과 프로젝트 구조를 먼저 만든다.