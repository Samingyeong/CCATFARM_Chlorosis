---
inclusion: always
---

# Product Overview

본 프로젝트는 감자 잎의 황화(Chlorosis), 정상(Healthy), 잎 말림(Leaf Curling)을
인식하는 AI 모델을 개발하기 위한 연구/개발 프로젝트이다.

최종적으로 스마트팜 순찰 로봇의 RGB 카메라 이미지에서
각 잎을 instance 단위로 분리하고 상태를 판별하는 것을 목표로 한다.

참고 파이프라인:

Potato RGB Images
→ Mask2Former
→ leaf instance segmentation
→ 명확한 label + Unknown label
→ EfficientNet-B1
→ Partial Label Learning / pseudo-label refinement
→ Healthy / Chlorosis / Leaf Curling
→ refined annotation
→ Mask2Former retraining
→ final instance segmentation model

현재 단계에서는 아직 데이터셋과 모델 코드가 존재하지 않는다.

따라서 첫 목표는
프로젝트 기본 개발환경과 코드 구조를 먼저 생성하고,
향후 데이터셋이 추가되면 그때 실제 데이터 구조를 분석하는 것이다.

원본 데이터가 들어오기 전에는
annotation format, class count, split 구조 등을 임의로 가정하지 않는다.