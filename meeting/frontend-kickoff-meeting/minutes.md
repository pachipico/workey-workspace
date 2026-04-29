# Frontend Kickoff Meeting — 회의록 (Minutes)

> 작성자: **minutes-writer**
> 회의: WorKey 모바일 앱(React Native) 개발 킥오프
> 일시: **2026-04-29**
> 형식: 3 Round 비동기 산출물 + Round 2 SendMessage 교차 질의

---

## 1. 회의 일시 및 참석자

| 항목 | 내용 |
|---|---|
| **일시** | 2026-04-29 |
| **장소** | 비동기 (산출물 Round 기반) |
| **사회** | moderator-lead (team-lead) |
| **참석자** | pm, backend, frontend, design, ux, moderator-lead(team-lead) |
| **서기** | minutes-writer (본 문서 작성자) |
| **회의 형식** | Round 1 → Round 2 (SendMessage 교차) → Round 3 → 종합 산출물 작성 |

### 1.1 회의 안건 (agenda.md 인용)

**회의 주제**: React Native 기반 모바일 앱 구현 전략 수립 및 네이티브 환경 최적화 검토

**핵심 논의 사항 4건**:
1. **모바일 최적화 API**: 앱 초기 로딩 시 데이터 요청을 최소화하기 위한 백엔드 응답 구조 개선
2. **네이티브 연동**: 푸시 알림, 로컬 스토리지 활용 등 React Native의 특징을 반영한 기능 구현 방식
3. **디자인 이식**: 모바일 컴포넌트(BottomSheet 등) 사용 시 디자인 시스템 가이드 준수 여부
4. **사용자 환경**: 바쁜 근무 현장에서 점장님이 한 손으로 일정 등록을 마칠 수 있는가? (최기준 페르소나 검증)

**필수 참조 경로**:
- 기획: `docs/WorKey - 기획서.md`
- 백엔드: `docs/WorKey - 백엔드.md`
- 프론트엔드: `docs/WorKey - 프론트엔드.md`
- 디자인: `docs/WorKey - 디자인.md`

---

## 2. Round 1 — 각 팀 1차 입장 정리

> 각 5명의 teammate가 자기 영역 기반 입장을 작성. 산출물 5건.

### 2.1 PM Round 1 핵심 (evidence/pm-round1.md)

- 백엔드 v1.1 SHIPPED (2026-04-28) 상태에서 RN 앱은 **팀 티어(월 19,900원) 매출 정당화 도구**. 직원 앱 미작동 시 가장 비싼 티어가 비어 있게 됨.
- **MUST 6개** 매트릭스: (1) 직원 앱 카카오 OAuth + 케이스 3 (2) 캘린더 + 휴무 신청 BottomSheet (3) FCM 푸시 (4) 휴무 수집 뷰 (5) 매장 등록 온보딩 (6) 직원 초대 BottomSheet
- **KPI 7종**: 첫 화면 TTI ≤ 1.5s, 깔때기 완료율 ≥ 85%, 휴무 신청 성공률 ≥ 95%, 푸시 오픈율 ≥ 35%, 캐시 적중률 ≥ 70%, 팀 티어 전환율 ≥ 5%, NPS ≥ 7.0
- **합격 시나리오**: "최기준 점장(45세, 강남 8평 카페, 직원 6명) 06:30 출근길 지하철, 한 손에 아이스 아메리카노" — 15분 내 다음 달 스케줄 생성

### 2.2 Backend Round 1 핵심 (evidence/backend-round1.md)

- 핵심 API 6개군(Auth/Me/Employee/Schedule/Store/Export) 명세 완료. v1.1에서 `GET /me/onboarding-status`로 케이스 1~5 분기 가능.
- v1.2 deferred 항목 6개: FCM 실연동, 관리자 API 인증(`anyRequest().permitAll()`), DEV 백도어 제거, 딥링크 정적 파일, BFF 홈 요약, 프로필 아바타 SVG.
- JWT 권고: AsyncStorage 평문 금지 → `expo-secure-store` (iOS Keychain / Android Keystore).
- **BFF `GET /me/home-summary` 제안** (v1.2 검토 권장).
- 스케줄 생성 API 응답: 직원 수 × 일수 비례, **1~5초 가능**, 클라이언트 타임아웃 10초 권장.
- CommonResponse 단건도 `result[0]` 접근 필요.

### 2.3 Frontend Round 1 핵심 (evidence/frontend-round1.md)

- 4-layer 아키텍처: React Navigation v7 + TanStack Query v5 + Zustand v5 + MMKV v3.
- 라이브러리: `@gorhom/bottom-sheet` v5, `@react-native-firebase/messaging` v21, `@react-native-community/netinfo` v11, `react-native-reanimated` v3, `react-native-gesture-handler`.
- Navigation 5레이어 구조 (Auth/Onboarding/AdminTabs/EmployeeTabs/Modal) + SplashScreen 분기 로직.
- **JWT는 MMKV(AES-256)로 충분**하다고 1차 판단 (Round 2에서 자기 수정).
- **FCM 토큰 등록을 `POST /me/push-token { token, platform }`으로 가정** (Round 2에서 자기 수정).
- 오프라인 큐 (휴무 신청 / 근무 교환).

### 2.4 Design Round 1 핵심 (evidence/design-round1.md)

- sky-500 토큰 매핑 표 (10종) + RN `colors.ts` 분리 권고 + `minHeight: 48` 강제.
- BottomSheet/FAB/Tab Bar/Modal/Toast 5종 컴포넌트 RN 규격.
- Thumb Zone 가이드: 헤더 우측 = Dead Zone, 하단 = Thumb Zone.
- **Dark Mode 미정의** + **달력 today `#0EA5E9` + 흰 텍스트 = 2.9:1 ⚠️ 자기 발견** ("흰 텍스트 볼드 또는 #0369A1 배경 고려").
- 미결 리스크 6건: Dark Mode 🟠 / 오늘 날짜 대비 🟡 / fontSize 토큰 혼용 🟡 / 헤더 "생성 확정" 위치 🟠 / 이모지→SVG 🟢 / `#fff` 하드코딩 🟡.

### 2.5 UX Round 1 핵심 (evidence/ux-round1.md)

- **페르소나 재정의**: 38세 / 분식+카페 / 직원 8명(연동4·미연동4) / **매장 카운터, 영업 중, 형광등 직사광, 70~80dB 소음, 30~90초 자투리** / 노안 시작.
- **시나리오 A 4·7번 = "한 손 시나리오의 사망 지점"** — 충돌 셀 → 바텀시트 → 칩 드래그.
- **PP-1~PP-7 페인 포인트**:
  - PP-1 드래그&드롭 가림 / PP-2 충돌 사유 안 읽힘 / PP-3 "+ 수동 추가" 발견 어려움 / PP-4 PNG 카톡 잘림 / PP-5 알림 피로도 / PP-6 딥링크 OAuth 직진 / PP-7 균등/연속 라벨
- 알림 피로도(하루 5~7개) → 카테고리별 on/off + Daily Digest + 영업시간 silent + 권한 컨텍스트 타이밍 요구.
- **매장 모드(Store Mode) 토글 제안**: 폰트 +1단계, hit area +20%, 고대비, silent push.
- 4대 토픽별 점장 시각 요구 정리 + Round 2 질문 4개 후보.

### 2.6 Round 1 → Round 2 전환 시점

- 모든 R1 산출물(5건) 완료 후 team-lead가 Round 2 시작 신호.
- 각 teammate는 타 4팀 R1을 검토하고 SendMessage로 직접 질의 + rebuttal 산출물 작성.

---

## 3. Round 2 — SendMessage 교차 질의 + 반박/리뷰

> 각 teammate가 타 팀 R1을 검토하고 자기 입장을 더 단단하게 반박. 산출물 5건 (rebuttals/).

### 3.1 Round 2 SendMessage 교환 내역

| From → To | 핵심 질문 |
|---|---|
| **pm → backend** | (B-1) FCM 실연동 v1.2 일정 확약 가능 여부 / (B-2) BFF 5일 견적 / (B-3) Phase 999 v1.2 차단 조건 격상 동의 |
| **pm → frontend** | (F-1) 인터랙션 매핑 short=선택/long=드래그 반대 변경 동의 / (F-2) client-side aggregation으로 TTI 충족 가능성 |
| **pm → design** | (D-1) 달력 today `#0369A1` 변경 동의 / (D-2) Dark Mode v1.3 강등 동의 |
| **pm → ux** | (U-1) Cold/Warm 두 단 분리 KPI 동의 / (U-2) 매장 모드 강등 + 3개 요소만 흡수 동의 |
| **backend → frontend** | (1) FCM 토큰 스펙 불일치 — `PATCH /me/fcm-token { fcmToken }`으로 맞출지 / (2) BFF + TanStack Query 캐시 키 전략 (Strategy A vs B) / (3) CommonResponse unwrap A/B/C 옵션 |
| **frontend → backend** | (1) `ScheduleDetailResponse.entries` Map → 배열 변경 / (2) Bulk PATCH 응답 형식 (204 vs diff) / (3) `POST /day-off-requests` idempotency / (4) onboarding-status `storeId` nullability |
| **frontend → design** | (1) BottomSheet 3단 snap 단계별 backdropOpacity / (2) 드래그 시 자동 축소 인터랙션 정의 / (3) 매장 모드 고대비 토큰 + FAB 그림자 / (4) DiceBear 그리드 레이아웃 |
| **design → ux** | (1) 터치 타겟 58dp 충분성 + 칩 32pt 첫 탭 잡힘 여부 / (2) sky-700 글레어 우려 + 매장 모드 라이트 고정 vs 다크 옵션 |
| **ux → pm** | 클릭 뎁스 임계값 / 우선 단축 대상 / KPI에 클릭 뎁스 추가 / 점심 피크 시연 추가 |
| **ux → frontend** | Bottom Tab 위치·크기 / iOS 22pt + Android 제스처 회피 / 매장 모드 +20% 호환 / 좌·우손 토글 양립 |

### 3.2 PM Round 2 핵심 (rebuttals/pm-round2.md)

- 4팀 R1을 비즈니스 우선순위·MVP 범위·KPI 측정성 기준으로 검토. **"단순 합의 회의가 아니라 MVP 범위 재정의 회의"**로 격상.
- **Backend 반박**: BFF v1.2 검토 권장 → **MUST 승격** / FCM "deferred" 일정 명시 → **확약 또는 비즈니스 모델 변경** / Phase 999 → **v1.2 MUST**
- **Frontend 반박**: MMKV JWT 단독 → **Keychain/Keystore 격리** / 드래그 매핑 (long-press=드래그) → **반대로** (short-press=선택, long-press=드래그)
- **Design 반박**: Dark Mode v1.2 진입 조건 격상 → **v1.3 강등** (UX 매장 라이트 권장 근거) / 달력 today 2.9:1 → **MVP 차단 조건** (sky-700)
- **UX 반박**: TTI 0.8s → **물리적 한계, Cold 1.5s/Warm 0.8s 두 단** / 매장 모드 토글 → **3요소만 흡수, 토글 자체는 v1.3** / PNG 멀티 → **fast-follow**
- 충돌 매트릭스 정리: TTI / JWT / 드래그 / Dark Mode / BFF / FCM / Phase 999 / Daily Digest / 매장 모드 / 달력 색.
- Round 1 PM 입장: **유지 3건 / 변경 5건 / 철회 1건** (DiceBear COULD 강등).
- v1.2 MUST 6개 → 10개로 확장 (BFF + Phase 999 + 알림 그룹화 + 달력 색 + JWT Keychain 추가).

### 3.3 Backend Round 2 핵심 (rebuttals/backend-round2.md)

- 수용·부분수용·거부 매트릭스로 4팀 R1 응답.
- **수용**: `/me/onboarding-status` 이미 완료 / 시간대 헤더 명문화 / MMKV 채택 / 충돌 검증 클라이언트화 / BFF aggregation (`/me/home-summary`로 통일)
- **부분 수용**: `/me/schedules` `?includeNext=true` / 푸시 토큰 idempotency (PATCH로 충분) / 오프라인 큐 `X-Idempotency-Key` (v1.2) / Daily digest 원칙 수용 / PNG 주간 슬라이스 검토
- **거부**: PNG CDN 절대 경로 (S3 인프라 선행) / cursor 페이지네이션 (offset 유지) / 다크모드 서버 응답 변경 불필요
- **즉시 조율 요구**: FCM 토큰 스펙 불일치 — frontend `POST /me/push-token { token, platform }` vs 실제 `PATCH /me/fcm-token { fcmToken }`
- 트랜잭션 정합성 위험 3건 식별 (휴무 신청+생성 동시 / Bulk+교환 동시 / 오프라인 큐 이중 제출).
- HTTP Cache-Control 헤더 v1.2 추가 계획.
- frontend에 3개 질문 발사 (DTO 구조 / BFF 캐시 키 전략 / CommonResponse unwrap A/B/C).

### 3.4 Frontend Round 2 핵심 (rebuttals/frontend-round2.md)

- **Round 1 자기 수정 4건**:
  - FCM 토큰 엔드포인트: `POST /me/push-token` → **`PATCH /me/fcm-token`**
  - JWT 저장: MMKV → **Keychain/Keystore** (MMKV는 일반 캐시용)
  - 푸시 권한 시점: 앱 최초 → **첫 휴무 신청 완료 직후**
  - CommonResponse: 단건도 `result[0]`
- BottomSheet 3단(30/60/100) 60% 기본 시작.
- 생성 확정 → 하단 sticky CTA (헤더 제거).
- 드래그 fallback 제안 (long-press=드래그 / short-press=Relocate Picker) — PM이 R2에서 "반대로"라고 반박.
- ETag 우선 도입 요청 (스케줄 조회·연간 통계).
- 다크 모드 토큰 확정 대기 (RN 구현 전 필수).
- backend·design에 공식 질문 4건씩 발사.

### 3.5 Design Round 2 핵심 (rebuttals/design-round2.md)

- **BottomSheet 3단 30/60/100 확정** + 핸들 색 자기 수정 (`#7DD3FC`(2.1:1) → `#0369A1`(8.75:1)).
- **달력 today 배경 `#0EA5E9` → `#0369A1` 즉시 변경 결정** (R2에서 자기 확정).
- **Dark Mode 토큰 테이블 확정** (라이트/다크 매핑 10종) — 앱 내 독립 설정, 시스템 다크 추종 OFF.
- **매장 모드 고대비 토큰셋 신설** (storeModeOverrides + hit area ×1.2 + fontSize +2sp).
- 풀스크린 로딩 UX 스펙 (스케줄 생성 1~5초 응답).
- 드래그 시각 피드백: floating preview + 햅틱 + 5초 Undo 토스트(`#0C4A6E`).
- 충돌 셀 long-press → 미니 팝오버(달력 60% 노출 유지).
- Tab Bar 활성/비활성 아이콘 페어(filled/outlined) 채택.
- ux에 검토 요청 2건 (터치 타겟 58dp 현장 검증 / sky-700 글레어).

### 3.6 UX Round 2 핵심 (rebuttals/ux-round2.md)

- **페르소나 충돌 명시**: PM 45세/지하철 vs UX 38세/매장 카운터 → **두 시나리오 모두 합격 기준선 채택** 요구.
- TTI 0.8s 강력 요구 ("점장은 0.8초도 길다") → PM이 cold/warm 분리 안으로 합의.
- **시나리오 B (매장 영업 중 11~14시 점심 피크)** 추가 시연 요구.
- 좌·우손잡이 토글 도입 요구 (모든 팀이 우손 전제).
- 백엔드 5초 응답 비판 → 95p ≤ 2s SLO 또는 비동기+푸시 결과 모델 요구 (R3에서 동기 10초 + 안내로 합의).
- BottomSheet 핸들 sky-300 → sky-700 / EmployeeChip 32pt → 44pt 요구.
- **R3 합의 후보 21건** + **Red Line·Yellow Line 분류** 사전 정리.
- pm·frontend에 SendMessage 발사.

### 3.7 Round 2 → Round 3 전환 시점

- 모든 R2 rebuttal(5건) 완료 + 각 teammate가 받은 질문에 대한 공식 답변을 R3에 등록.
- 4팀이 R1·R2 입장의 [유지/수정/철회]를 명시하는 최종 종합 라운드로 전환.

---

## 4. Round 3 — 최종 입장 정리

> 각 팀이 R1·R2 입장 [유지/수정/철회] 명시 + 받은 질문 공식 답변 + 4대 토픽 최종 결론. 산출물 5건.

### 4.1 PM Round 3 핵심 (evidence/pm-round3.md)

- **유지 10건**: onboarding-status / 푸시 권한 타이밍 / OS 공유 시트 미사용 / AsyncStorage JWT 금지 / 직원 초대 MUST / 매장 등록 MUST / 카카오 OAuth MUST / 휴무 수집 뷰 MUST / 한 손 페르소나 검증 / KPI 7종.
- **수정 10건**: TTI 단일 → cold/warm 두 단 분리 / JWT MMKV 금지 → Keychain 강제 / MUST 6 → 11개 / 페르소나 45세 → 38세 UX 정의 / 시나리오 단일 → A+B 병행 / 자동 감지 → 좌우손 토글 / 드래그 인터랙션 매핑 / Dark Mode 토큰 v1.2 박힘 + UI v1.3 / DiceBear COULD → SHOULD lazy / 베타 5명 → 15명 + 일 단위 완수율.
- **철회 2건**: cursor 페이지네이션 / PNG CDN 절대 경로.
- UX 4개 질문 공식 답변 (CPTC 시나리오별 상한 / 단축 우선순위 / KPI 클릭 뎁스 추가 / 점심 피크 병행 동의).
- v1.2 MVP 매트릭스 최종: **MUST 11 / SHOULD 10 / COULD 5 / WON'T 5**.
- KPI 15종 (cold/warm TTI + CPTC + Misfire + 일 단위 완수율 + 저사양 기기 + 알림 끄기율 등 추가).
- **미해결 3건 명시 (PM 관점)**: O1 FCM 일정 / O2 CommonResponse 단건 분리 / O3 매장 모드 라이트 vs 다크.
- 의견 충돌 정리:
  - "PM TTI 1.5s 단일 vs UX cold/warm 분리 → cold 1.5s/warm 0.8s 합의"
  - "frontend long-press=드래그 vs PM short-press=선택 → PM 안 채택"
  - "design Dark Mode v1.2 진입 조건 vs PM v1.3 이월 → 토큰 박힘 + UI v1.3"

### 4.2 Backend Round 3 핵심 (evidence/backend-round3.md)

- frontend Round 2 4개 질문 최종 답변:
  - **Q1 entries Map → 배열**: `[{ employeeId, entries }]`로 v1.2 전환 수용. v1.1은 클라이언트 transform.
  - **Q2 Bulk PATCH 응답**: 현재 `CommonResponse<Void>` (200+빈배열). diff 응답은 v1.2 검토.
  - **Q3 day-off-requests idempotency**: 서버 단 중복 체크 존재. **`X-Idempotency-Key` v1.2 도입**.
  - **Q4 onboarding-status storeId**: **`@Nullable` 확정**. STORE_MISSING 시 null. status별 매트릭스 제공.
- BFF `/me/home-summary` 최종 응답 구조 확정 (employees·entries 등 대용량 제외, lazy 별도 호출).
- FCM 타임라인: v1.1 토큰 저장 ✅ / v1.2 Firebase Admin SDK 연동 (일정 미정).
- HTTP Cache-Control 5종 + ETag (스케줄·entries) v1.2 우선.
- v1.2 백엔드 작업 8개 우선순위 정리.
- 즉시 조치 3건: FCM 토큰 스펙 조율 완료 / storeId null 처리 / Bulk PATCH 응답 명확화.

### 4.3 Frontend Round 3 핵심 (evidence/frontend-round3.md)

- 수신 질문 답변:
  - **FCM 토큰**: (A) 프론트가 `PATCH /me/fcm-token { fcmToken }`로 수정 채택. `platform` 제거.
  - **TanStack Query 캐시**: **Strategy B (normalize + 개별 캐시 키 분배)** 채택.
  - **CommonResponse unwrap**: **(A) Axios interceptor 자동 unwrap** 채택 (단건 `result[0]` / 다건 `result`).
- design 질문 답변 수용 (3단 snap / 매장 모드 / 다크 토큰 / DiceBear 그리드).
- ux Thumb Zone 5문항 답변 (insets 자동 / 탭 auto-hide / 좌우손 Zustand+Reanimated / **3중 인코딩 전면 채택** / Bottom Tab 단일).
- BottomSheet 화면별 snap 확정 / tokens.ts 3종(라이트/다크/매장) 골격 / Tab Bar 3중 인코딩 / FAB 좌·우손 반전.
- 오프라인 큐 UUID v4 X-Idempotency-Key 헤더 + 적용 범위(휴무 신청·교환·재배치).
- 전체 라이브러리 최종 목록 16종.
- 미해결 의존성 6건 명시 (FCM / BFF / invite preview / notification-preferences / 매장 모드 / Phase 999).

### 4.4 Design Round 3 핵심 (evidence/design-round3.md)

- PM D-1 (`#0369A1` 변경) ✅ 동의 / PM D-2 (Dark Mode v1.3 강등) ✅ 동의.
- frontend Q1~Q4 답변:
  - **Q1**: BottomSheet 3단 backdropOpacity 0.15/0.40/0.60 + 핸들 색 30%=sky-200 / 60%+=sky-700.
  - **Q2**: 드래그 시 `snapToIndex(0)` 자동 수축 인터랙션 시퀀스 정의.
  - **Q3**: 매장 모드 `--ts-primary-hc`(sky-700) + FAB/CTA 그림자 강화.
  - **Q4**: DiceBear 5열 6행, 셀 56pt, 상단 2행 추천.
- UX R2 §4.1~§4.6 수용 (오늘 색 / 다크·매장 토큰 / 핸들 sky-700 / Tab 아이콘 페어 / Chip 44pt+).
- 검토 요청 1·2 점장 답변 통합: 58dp 충분 / 매장 모드 **라이트 고대비로 고정** / 다크는 직원 앱 야간만 v1.3.
- 컬러 토큰 / 컴포넌트 / Figma→RN 매핑 최종 확정.
- **v1.2 디자인 차단 조건 7개** 명시.
- v1.3 백로그 6건 (다크 모드 / 매장 모드 토글 / 좌우손 / Daily Digest / SVG 전환 / PNG 주간).

### 4.5 UX Round 3 핵심 (evidence/ux-round3.md)

- **PP-1~PP-7 판정**: **해결 3건 (PP-1·PP-2·PP-7)** / **부분해결 3건 (PP-4·PP-5·PP-6)** / **미해결 1건 (PP-3)**.
- **Red Line 8건** 정식 등록 (R-1~R-8). 출시 차단 4건 = R-1·R-2·R-3·R-6.
- **Yellow Line 7건** 등록 (Y-1~Y-7). 양보 조건 명시.
- **미해결 5건 (U-1~U-5)** 등록:
  - U-1 PP-3 코치마크
  - U-2 인터랙션 매핑 (UX 권고: PM 안 채택)
  - U-3 CommonResponse unwrap
  - U-4 FCM 일정 확약
  - U-5 Dark Mode 활성화 시점
- 4대 토픽 최종 결론: 합의 12건 + 부분합의 5건 + 이월 4건 = R2 §5에서 제시한 "최소 15건 합의" 기준선 충족.
- 디자인 검토 요청 2건 답변 (58dp 충분 / sky-700 글레어 OK / 매장 모드 라이트 고정).
- 점장 1인칭 결론: **"카톡으로 돌아가지 않는 워키. 그 한 줄이 R3의 결론이다."**

### 4.6 Round 3 의견 충돌 해결 정리

| 충돌 지점 | Round 1·2 입장 | Round 3 합의 |
|---|---|---|
| **TTI 목표** | PM 1.5s 단일 vs UX 0.8s | **Cold 1.5s / Warm 0.8s 두 단 분리** |
| **JWT 저장** | frontend MMKV vs backend·pm Keychain | **Keychain/Keystore 강제, MMKV는 비민감** |
| **드래그 인터랙션** | frontend long-press=드래그 vs PM short-press=선택 | **PM 안 채택** (UX 권고 일치) |
| **Dark Mode** | design v1.2 진입 조건 vs pm v1.3 / ux 라이트 권장 | **토큰 v1.2 박힘 + UI 토글 v1.3** |
| **BFF 엔드포인트** | backend "v1.2 검토" vs pm·ux MUST | **v1.2 MUST + frontend client-side fallback** |
| **FCM 실연동** | backend "deferred 일정 미정" | **v1.2 MUST + 일정 확약 요구 (U-4)** |
| **페르소나** | pm 45세/지하철 vs ux 38세/매장 | **UX 정의 통합 교체** |
| **시나리오** | pm 출근길 단일 vs ux 매장 카운터 추가 | **A + B 병행 합격** |
| **매장 모드 토글** | ux 강력 요구 vs pm 강등 | **3요소만 v1.2 흡수, 토글 UI v1.3** |
| **달력 today 색** | design 2.9:1 ⚠️ | **`#0369A1` (8.75:1) MVP 차단 조건** |
| **PNG 멀티 이미지** | ux PP-4 강력 요구 | **v1.2 fast-follow + 베타 인터뷰 후 결정** |
| **CommonResponse** | backend A/B/C 옵션 | **(A) Axios interceptor 자동 unwrap** |
| **entries 구조** | frontend Map → 배열 요구 | **v1.2 배열 전환 수용** |

---

## 5. 회의 종료

- 4팀 모두 Round 3 산출물 작성 완료 (2026-04-29).
- minutes-writer가 종합 산출물 2건(decision.md, minutes.md) 작성으로 회의 클로징.
- 다음 단계: team-lead가 두 산출물을 검수하고 킥오프 직후 1:1 후속 합의 4건 (U-1~U-5 결정) 진행.

---

## 6. 산출물 인벤토리

### 6.1 Round 별 입력 파일 15건

| 카테고리 | 파일 경로 | 작성자 | 라인 수 (참고) |
|---|---|---|---|
| 안건 | `meeting/frontend-kickoff-meeting/agenda.md` | team-lead | 17 |
| **Round 1** | `evidence/pm-round1.md` | pm | 242 |
| Round 1 | `evidence/backend-round1.md` | backend | 369 |
| Round 1 | `evidence/frontend-round1.md` | frontend | 463 |
| Round 1 | `evidence/design-round1.md` | design | 268 |
| Round 1 | `evidence/ux-round1.md` | ux | 205 |
| **Round 2** | `rebuttals/pm-round2.md` | pm | 354 |
| Round 2 | `rebuttals/backend-round2.md` | backend | 528 |
| Round 2 | `rebuttals/frontend-round2.md` | frontend | 524 |
| Round 2 | `rebuttals/design-round2.md` | design | 477 |
| Round 2 | `rebuttals/ux-round2.md` | ux | 206 |
| **Round 3** | `evidence/pm-round3.md` | pm | 280 |
| Round 3 | `evidence/backend-round3.md` | backend | 510 |
| Round 3 | `evidence/frontend-round3.md` | frontend | 686 |
| Round 3 | `evidence/design-round3.md` | design | 546 |
| Round 3 | `evidence/ux-round3.md` | ux | 206 |

### 6.2 종합 산출물 2건 (본 회의 클로징)

| 파일 | 작성자 | 성격 |
|---|---|---|
| `meeting/frontend-kickoff-meeting/decision.md` | minutes-writer | **실행 가능한 결정문서 + 로드맵** (4대 토픽 합의안 / Red·Yellow Line / 미해결 / 로드맵 / KPI / 액션 아이템) |
| `meeting/frontend-kickoff-meeting/minutes.md` | minutes-writer | **시간순 회의 기록** (Round별 요약 / SendMessage 교환 내역 / 의견 충돌 해결 / 산출물 인벤토리) |

### 6.3 총계

- **입력 파일**: 16건 (agenda 1 + round 15) / 약 6,000+ 라인
- **출력 파일**: 2건 (decision.md + minutes.md)
- **총 산출**: 18건

---

## 7. 회의록 작성자 비고

- 본 회의는 **비동기 라운드 기반 산출물 회의**로, 시간 단위 발언 로그 대신 Round별 산출물 요약을 시간 축으로 사용함.
- SendMessage 교환 내역은 각 round2 파일 내 "질문" 섹션에서 직접 추출 (실제 SendMessage 도구 노출이 일부 teammate에 제한되어, round2 파일 본문에 명문화된 질문을 채택).
- UX의 **PP-1~PP-7 / R-1~R-8 / Y-1~Y-7 / U-1~U-5** 키워드는 ux-round1·round2·round3에 일관되게 등장하므로 본 회의록에서도 동일 키워드를 인용.
- 의견 충돌 지점은 §4.6 표에 별도 정리하여 회의 흐름의 핵심 결정 포인트를 추적 가능하게 함.

---

*Minutes written by minutes-writer (2026-04-29). 종합 산출물 작성 완료. team-lead의 검수 + 킥오프 후속 1:1 합의(U-1~U-5)를 기다림.*
