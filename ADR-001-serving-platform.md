# ADR-001: ML 모델 서빙 플랫폼 선택

## Status
Accepted

## Context
- 개인 ML 프로덕트: 계층적 베이지안 모델 (PyMC) 추론 API
- 트래픽 예측 불가 (0~수백 req/day)
- 비용 민감 (개인 프로젝트)
- 모델 크기: ~2MB (posterior trace)
- GPU 추론 불필요 (numpy 연산만)
- 불확실성 포함 응답 (credible interval) 제공 필요

## Decision
Cloud Run (서버리스 컨테이너) 선택

## Alternatives Considered

| 옵션 | 장점 | 단점 | 기각 이유 |
|---|---|---|---|
| **Vertex Endpoint** | managed 서빙, A/B 내장, Model Registry 연동 | 최소 비용 ~$40/월 (min instance 1), 개인 프로젝트에 과잉 | 비용 대비 가치 부족 |
| **GKE** | 완전한 제어, GPU 지원 | 클러스터 운영 부담, 상시 비용 | Solo builder에게 과잉 |
| **Cloud Functions** | 더 가벼움, 코드만 배포 | 컨테이너 미지원, 메모리 제한, 의존성 관리 어려움 | arviz/numpy 스택에 부적합 |
| **GCE VM** | 최대 자유도 | 24시간 상시 비용, OS 관리 | 서버리스 대비 장점 없음 |

## Consequences

### 긍정적
- 비용 0 (무료 tier: 월 200만 요청 + 36만 vCPU초)
- 서버 관리 없음
- 자동 스케일링 (0 ↔ N)
- revision 기반 롤백 + 카나리 배포 가능
- Cold start 0.25초 (현재 모델 크기에서 문제 없음)

### 부정적/제약
- 모델 교체 시 이미지 재빌드 필요 (Option A: 이미지 내장)
- GPU 추론 불가 → 모델이 GPU 필요 시 Vertex Endpoint으로 마이그레이션 필요
- 최대 타임아웃 60분 (대규모 배치 부적합 → Cloud Run Jobs로 분리)

### 마이그레이션 트리거
- GPU 필요 → Vertex Endpoint
- 모델 >500MB → Option B (GCS 로드) + Vertex 고려
- A/B 테스트 고도화 → Vertex Endpoint (treatment assignment 프레이밍)
- 팀 협업 시작 → L2/L3 시나리오 진입
