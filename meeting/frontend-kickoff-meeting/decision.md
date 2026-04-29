# Frontend Kickoff Meeting — 최종 결정문서 (Decision)

> 작성자: **minutes-writer**
> 회의: WorKey 모바일 앱(React Native) 개발 킥오프
> 일시: **2026-04-29**
> 산출 근거: round1 5건 + round2 5건 + round3 5건 (총 15건) + agenda.md

---

## 0. 요약 (Executive Summary)

WorKey v1.2 RN 앱 킥오프 3 Round 회의 결과, **합의 21건 / 부분합의 5건 / 이월 4건**으로 수렴되었으며, **MUST 11개 / SHOULD 10개 / COULD 5개 / WON'T 5개**의 v1.2 MVP 매트릭스를 확정한다. 페르소나는 PM 1차안(45세/지하철)에서 **UX 정의(38세/매장 카운터/30~90초 자투리/형광등 직사광/70~80dB)**로 통합 교체되었고, 합격 시나리오는 **A(출근길 06:30~06:45 15분) + B(점심 피크 11~14시 누적 30분) 병행**이다. UX의 **Red Line 8건(출시 차단 4건 포함) + Yellow Line 7건 + 미해결 5건(U-1~U-5)**이 명시적으로 등록되었다.

---

## 1. 회의 개요

| 항목 | 내용 |
|---|---|
| **안건** | WorKey 모바일 앱(React Native) 구현 전략 수립 및 네이티브 환경 최적화 검토 |
| **일시** | 2026-04-29 |
| **참석자** | pm, backend, frontend, design, ux, moderator-lead(team-lead) |
| **회의 형식** | 3 Round 비동기 산출물 작성 + Round 2 SendMessage 교차 질의 |
| **필수 참조** | `docs/WorKey - 기획서.md`, `docs/WorKey - 백엔드.md`, `docs/WorKey - 프론트엔드.md`, `docs/WorKey - 디자인.md` |
| **핵심 토픽 4개** | (T1) 모바일 최적화 API · (T2) RN 네이티브 연동 · (T3) 디자인 ↔ 모바일 컴포넌트 · (T4) 한 손 조작 |

---

## 2. 4대 핵심 토픽 합의안 매트릭스

### 2.1 토픽 1 — 모바일 최적화 API

#### 합의 사항 (책임: backend / frontend)

| # | 결정 | 근거 |
|---|---|---|
| T1-1 | **BFF `GET /me/home-summary` v1.2 MUST 도입** (5일 이상 소요 시 frontend client-side aggregation으로 fallback) | pm-round2 §1.2 / backend-round2 §2-2 / ux-round2 §2-1 |
| T1-2 | **TTI KPI 두 단 분리: Cold(cache miss) ≤ 1.5s P95 / Warm(cache hit) ≤ 0.8s P95** | ux-round1 §6.T1 (0.8s) vs frontend-round2 §3-3 (RN cold start 800ms~1.2s) → pm-round3 M1 합의 |
| T1-3 | TanStack Query Strategy B (normalize + 개별 캐시 키 분배) 채택 | backend-round2 §8 Q2 / frontend-round3 §0 답변 2 |
| T1-4 | **CommonResponse 처리 = (A) Axios interceptor 자동 unwrap** (단건 `result[0]` / 다건 `result`) | backend-round2 §8 Q3 / frontend-round3 §0 답변 3 |
| T1-5 | `?includeNext=true` 다음 달 합산 옵션 | backend-round2 §1-2 부분 수용 |
| T1-6 | ETag 우선 도입 — 스케줄 조회 / 연간 통계 / entries | frontend-round2 §1-4 / ux-round2 §2-4 / backend-round3 §3 |
| T1-7 | `X-Timezone: Asia/Seoul` 응답 헤더 + contract 명문화 | backend-round2 §1-5 |
| T1-8 | Cache-Control: employees 5분 / schedule 1분 / annual 1시간 / onboarding-status no-cache | backend-round2 §6-2 / backend-round3 §3 |
| T1-9 | 스케줄 생성 API: P95 ≤ 5s, 클라이언트 타임아웃 10s, 풀스크린 로딩 오버레이("약 3~5초 소요") | backend-round2 §6-1 / design-round2 §2 / frontend-round2 §1-3 |
| T1-10 | **`ScheduleDetailResponse.entries`: Map → 배열 `[{ employeeId, entries }]` 전환 (v1.2)** | frontend-round2 §7 Q1 / backend-round3 §1 답변 1 |

#### 부분 합의 / 잔여 이슈

- **cursor 페이지네이션** → backend-round2 §1-6 거부, offset 유지 (v2.0 재논의) — pm-round3 W1 철회
- **PNG CDN 절대 경로** → backend-round2 §1-3 거부 (S3 인프라 선행) — pm-round3 W2 철회
- **스케줄 생성 비동기 잡 + 푸시 결과 모델** (ux-round2 §2-2 제안) → 동기 + 안내로 합의, 직원 15명+ 매장은 v1.3 검토

**책임 부서**: backend (구현) / frontend (caching·interceptor·BFF fallback)

---

### 2.2 토픽 2 — RN 네이티브 연동 (푸시·로컬스토리지)

#### 합의 사항 (책임: frontend / backend)

| # | 결정 | 근거 |
|---|---|---|
| T2-1 | **JWT 저장: `react-native-keychain`** (iOS Keychain / Android Keystore) — MMKV 평문 금지 | backend-round1 §3 / pm-round1 §3.3 / frontend-round2 §0 자기수정 / **Red Line R-4** |
| T2-2 | 비민감 캐시·오프라인 큐: `react-native-mmkv` (AES-256 옵션) | frontend-round2 §5-1 / backend-round2 §2-4 |
| T2-3 | **FCM 토큰 등록: `PATCH /me/fcm-token { fcmToken }`** (frontend Round 1 `POST /me/push-token { token, platform }` 오류 수정) | backend-round2 §2-1 / frontend-round2 §0 자기수정 / frontend-round3 §0 답변 1 (A) |
| T2-4 | **푸시 권한 요청 = 첫 휴무 신청 완료 직후** (4팀 만장일치) | pm-round1 §3.3 / ux-round1 §3 / frontend-round2 §0 / **Red Line R-5** |
| T2-5 | 알림 카테고리 그룹화: Android `NotificationChannel` 4종 / iOS `thread-id` 4종 | ux-round1 §3 / frontend-round2 §4-2 |
| T2-6 | 영업시간 silent push (FCM 인프라와 동시 적용, MUST) | ux-round1 §3 / pm-round2 §4.3 / **Red Line R-5** |
| T2-7 | Splash 캐시 우선 라우팅: MMKV onboarding-status 캐시 hit 시 즉시 라우팅 + 백그라운드 재검증 | ux-round2 §3-1 / frontend-round2 §3-3 |
| T2-8 | 오프라인 큐 적용 범위: 휴무 신청 + 근무 교환 + **휴무 재배치** 3종 + UUID v4 `X-Idempotency-Key` 헤더 | ux-round2 §3-4 / backend-round2 §2-5 / frontend-round3 §5 |
| T2-9 | 딥링크: `GET /invite/{token}/preview` 미리보기 API + Universal Links/App Links (SHOULD, 도메인 발급 일정 의존) | ux-round1 PP-6 / backend-round2 §5 PP-6 |
| T2-10 | onboarding-status `storeId` `@Nullable` 확정 (STORE_MISSING 시 null) | frontend-round2 §7 Q4 / backend-round3 §1 답변 4 |

#### 부분 합의 / 잔여 이슈 — **U-4 (FCM 실연동 일정)**

- **FCM 실연동 v1.2 출시일 일정 확약 미수신** → 킥오프 직후 backend 책임자와 1:1 합의. 일정 확약 불가 시 PM이 비즈니스 모델 §7을 "팀 티어 베타 50% 할인"으로 변경 책임
- Daily Digest 알림 / `PATCH /me/notification-preferences` → **v1.3 이월** (Yellow Line Y-3)

**책임 부서**: frontend (RN 통합·Keychain·MMKV·오프라인 큐) / backend (FCM SDK 연동·notification-preferences API·딥링크 정적 파일)

---

### 2.3 토픽 3 — 디자인 시스템 ↔ 모바일 컴포넌트

#### 합의 사항 (책임: design / frontend)

| # | 결정 | 근거 |
|---|---|---|
| T3-1 | **BottomSheet 3단 snap 표준화** | design-round2 §1.1 / design-round3 §2 Q1 |
| | - InviteBottomSheet: `['40%']` | |
| | - LeaveRequestSheet: `['50%','92%']` | |
| | - DayOffConflictSheet: `['30%','60%','92%']` (initialIndex=1, 60% 시작) | |
| | - ShiftSwapSheet: `['60%','92%']` | |
| T3-2 | 핸들 너비 40dp, 색상 `#0369A1` (sky-700, 8.75:1) — 기존 sky-300(2.1:1) 폐기 | design-round2 §1.1 자기 발견 / ux-round2 §4-3 |
| T3-3 | **`--ts-cal-today-bg`: `#0EA5E9` → `#0369A1` 변경** (2.9:1 → 8.75:1) | design-round1 §2.4 자기 발견 / pm-round2 §3.2 반박 3 / **Red Line R-1 (출시 차단)** |
| T3-4 | **"생성 확정" CTA: 헤더 우측 → 하단 full-width sticky 56dp** (만장일치) | design-round1 §2.3 / pm-round2 §3.2 / frontend-round2 §2-2 / ux-round2 §4-5 / **Red Line R-6 (출시 차단)** |
| T3-5 | EmployeeChip minHeight: 32pt → **44pt** + hitSlop 6pt | ux-round2 §4-6 / design-round3 §3 / **Red Line R-8** |
| T3-6 | **Tab Bar 활성/비활성 3중 인코딩**: 색 + 아이콘 형태(filled/outlined) + 라벨 볼드(700/400) | ux-round2 §4-4 / frontend-round3 §0 답변 4 / design-round3 §3 |
| T3-7 | Tab Bar 활성 색: sky-500 → `#0369A1` (sky-700) — 직사광 시인성 보강 | design-round3 §4.2 |
| T3-8 | 드래그 시각 피드백: floating preview(손가락 위 20dp) + 햅틱 Medium + 5초 Undo 토스트(`#0C4A6E` 배경) | ux-round1 PP-1 / design-round2 §1.3 / **Red Line R-3 (출시 차단)** |
| T3-9 | 충돌 셀 long-press → 미니 팝오버(달력 60% 노출 유지) | ux-round1 PP-2 / design-round2 §4.2 |
| T3-10 | DayOffConflictSheet 드래그 시작 → `snapToIndex(0)` 자동 수축 → 드롭 후 `snapToIndex(1)` 복귀 | design-round3 §2 Q2 |
| T3-11 | Dark Mode 토큰 테이블 v1.2 코드에 박힘 / UI 토글 활성화는 **v1.3** (시스템 다크 추종 OFF) | pm-round2 §3.2 / design-round3 §1 D-2 / ux-round3 §6 U-5 |
| T3-12 | 매장 모드 3요소만 v1.2 흡수: (a) hit area 48dp 기본 (b) 영업시간 silent push (c) primary-ink 자동 적용 | pm-round2 §4.2 / design-round3 §2 Q3 / **Red Line R-7** |
| T3-13 | DiceBear 아바타 그리드: 5열 × 6행, 셀 56×56pt, 상단 2행 추천 | design-round3 §2 Q4 |
| T3-14 | design 검수 7개 차단 조건 (PR 머지 게이트) | design-round3 §6 |

#### 디자인 검수 7개 차단 조건 (design-round3 §6)

| # | 차단 조건 | 확인 방법 |
|---|---|---|
| 1 | `calTodayBg = #0369A1` (WCAG 8.75:1 이상) | 시각적 검수 + 대비 체크 도구 |
| 2 | 모든 CTA 버튼이 화면 **하단 sticky** (헤더 우측 0건) | 화면별 PR 검수 |
| 3 | `minHeight: 56` 주요 CTA / `minHeight: 44` EmployeeChip | StyleSheet 수치 확인 |
| 4 | `raw hex #fff` 사용 0건 (`tokens.surface` 사용) | `grep -r "'#fff'" src/` 0건 |
| 5 | BottomSheet OS 네이티브 공유 시트 미사용 | PR 설명 확인 |
| 6 | Tab Bar 아이콘 filled/outlined 페어 적용 | 스크린샷 비교 |
| 7 | `@gorhom/bottom-sheet` 3단 snap 표준 준수 | 종류별 snapPoints 확인 |

#### 부분 합의 / 잔여 이슈 — **U-5 (Dark Mode 활성화 시점)**

- 매장 모드 토글 UI 자체 → **v1.3** (Yellow Line Y-4) — 베타 사용자 1명+ 요청 시 v1.2.1 hot-fix
- 다크 모드 라이트 고정 vs 다크 옵션 → **UX 권고: 라이트 고정** + 야간 직원 앱 시나리오만 v1.3 다크 (ux-round3 §5)

**책임 부서**: design (토큰·컴포넌트 스펙·디자인 자료 갱신) / frontend (RN tokens.ts·BottomSheet·Tab Bar·CTA 구현)

---

### 2.4 토픽 4 — 한 손 조작 (최기준 페르소나)

#### 합의 사항 (책임: ux / frontend / pm)

| # | 결정 | 근거 |
|---|---|---|
| T4-1 | **페르소나 통합 교체**: PM Round 1(45세/지하철/15분) → **UX 정의(38세/매장 카운터/30~90초 자투리/형광등 직사광/70~80dB)** | ux-round1 §0 / ux-round2 §0 / pm-round2 §4.1 / pm-round3 M4 |
| T4-2 | **합격 시나리오 2종 병행**: A(출근길 06:30~06:45 15분, PM 직접 시연) + B(점심 피크 11~14시 누적 30분, 진행 상태 자동 저장) | ux-round2 §1-3 / pm-round3 M5 |
| T4-3 | 드래그 fallback (**Red Line R-2**): | pm-round2 §2.2 / design-round2 §4.1 / ux-round3 §4 T4 / **U-2 결정** |
| | - **MUST**: 칩 short-press(탭) → "어디로 옮길까요?" 모드 → 달력 셀 1탭 → 이동 | |
| | - **SHOULD**: 칩 long-press(300ms) → 드래그 시작 (고급) | |
| | - 인터랙션 매핑은 **PM Round 2 §2.2 안 채택** (frontend Round 2 §4-1 안 폐기) | |
| T4-4 | 첫 진입 시 1회 코치마크 ("칩을 탭하거나 ⋮ 메뉴를 눌러 날짜를 바꿀 수 있어요") | frontend-round2 §3-3 / design-round3 §4.3 |
| T4-5 | Critical Path Tap Count P95 시나리오별 상한 | pm-round3 §2.1 / **신규 KPI** |
| | - 휴무 신청 ≤ 3탭 / 스케줄 생성 ≤ 7+1 / 미연동 일괄 ≤ 4+다중 / 직원등록·교환 ≤ 5탭 | |
| T4-6 | Misfire Rate ≤ 8% (Undo 트리거·재진입 비율) | ux-round1 §4 / pm-round3 §4 KPI 13 |
| T4-7 | **진행 상태 자동 저장** (시나리오 B 전제) | pm-round3 §5.4 신규 요구사항 |
| T4-8 | 좌·우손잡이 토글 → SHOULD/v1.3 (Yellow Line Y-5) | ux-round1 §1.4 / ux-round2 §1-4 / frontend-round2 §3-6 / frontend-round3 §0 답변 3 |
| T4-9 | 코치마크 PP-3 (U-1): frontend가 `onboarding-status.role` + 직원 연동 0명 시 자동 노출 결정 | ux-round1 PP-3 / **U-1** |

#### 부분 합의 / 잔여 이슈

- **U-1 PP-3 코치마크 구현 책임** → frontend가 v1.2 출시 시 휴무 수집 뷰 첫 진입 1회 노출 결정 (ux-round3 §6)
- **U-2 인터랙션 매핑** → ux-round3 §4 T4 권고 = PM 안(short=선택, long=드래그) 채택. frontend가 코드에서 채택 명시
- **Y-5 좌·우손잡이 토글** → 베타 NPS 인터뷰에 좌손 1~2명 포함 후 v1.3 결정

**책임 부서**: ux (시연 프로토콜·페르소나 검증·NPS 인터뷰) / frontend (코치마크·인터랙션 매핑·진행 상태 저장 구현) / pm (시연 합격 판정)

---

## 3. UX Red Line 8건 (양보 불가)

> ux-round3 §2 인용 — "이 8개 중 하나라도 흔들리면 v1.2 출시 거부."

| # | 항목 | 출시 차단? | 책임 부서 | 근거 |
|---|---|---|---|---|
| **R-1** | 달력 today 배경 `#0369A1` (8.75:1) | **🚫 출시 차단** | design + frontend | design-round2 §4.5 자기 확정 / pm-round2 §3.2 |
| **R-2** | 드래그 fallback (long-press → 메뉴 → 셀 1탭) 표준 | **🚫 출시 차단** | design + frontend | ux-round1 §1 시나리오 A 4·7번 / design-round2 §4.1 |
| **R-3** | 드래그 후 5초 Undo 토스트 + 햅틱 | **🚫 출시 차단** | frontend | ux-round1 PP-1 / design-round2 §1.3 |
| **R-4** | JWT → Keychain/Keystore (MMKV 평문 금지) | 보안+매출 리스크 | frontend | backend-round1 §3 / frontend-round2 §3-2 자기수정 |
| **R-5** | 영업시간 silent push + 권한 요청 = 첫 휴무 신청 후 | 보안+매출 리스크 | frontend + backend | pm-round2 §4.3 / ux-round1 §3 |
| **R-6** | "생성 확정" 헤더 → 하단 sticky CTA (full-width, ≥ 56dp) | **🚫 출시 차단** | design (자료 갱신) + frontend | design·pm·frontend 만장일치 |
| **R-7** | 매장 모드 토큰 분기 v1.2 코드 골격 박힘 (UI 진입은 v1.3) | 출시 가능, 골격 필수 | design + frontend | design-round2 §4.3 |
| **R-8** | EmployeeChip minHeight **44pt+** (매장 모드 53pt+) | 출시 가능, 골격 필수 | design + frontend | ux-round2 §4-6 / design-round3 §3 |

→ **출시 차단 4건**: **R-1 / R-2 / R-3 / R-6** (CI/PR 머지 가드 자동화 권고 — ux-round3 §8)

---

## 4. UX Yellow Line 7건 (조건부 양보)

> ux-round3 §3 인용 — "받아들인다. 단 조건이 붙는다."

| # | 항목 | 양보 조건 |
|---|---|---|
| **Y-1** | TTI **cold 1.5s / warm 0.8s** 두 단 KPI | warm 측정·공시가 KPI에 반드시 포함. cold는 첫 1회만 허용, 이후 진입은 warm 기준 |
| **Y-2** | PNG 멀티 이미지 **v1.2 fast-follow** | 출시일 + 4주 내 베타 5건 인터뷰. 결과 무관 백엔드 `?mode=weekly` API는 출시일에 enable 가능 |
| **Y-3** | Daily Digest 알림 → **v1.3 SHOULD** | 카테고리 on/off + silent hours가 v1.2에 들어가는 조건. 알림 끄기율 ≤ 15% 모니터로 트리거 |
| **Y-4** | 매장 모드 **토글 UI** → v1.3 | 토큰 분기 골격(R-7)은 v1.2 박힘. 베타 1명+ 요청 시 v1.2.1 hot-fix |
| **Y-5** | 좌·우손잡이 토글 → **v1.3** | 베타 NPS 인터뷰에 좌손 점장 1~2명 포함 + 의견 채집 후 v1.3 결정 |
| **Y-6** | RN v7 + Reanimated 3 안정성 | 갤럭시 A 시리즈(RAM 4GB) 또는 동급 1종 베타 합격선 추가 약속 시 양보 |
| **Y-7** | 오프라인 큐 X-Idempotency-Key | v1.2 출시일에 휴무 신청·교환·재배치 3종 모두 적용. frontend는 미리 클라이언트 UUID 코드 박음 |

---

## 5. 미해결 이슈 (U-1 ~ U-5)

> ux-round3 §6 + pm-round3 §6 통합. 본 회의 라운드 내 결정되지 않은 항목.

| # | 미해결 항목 | 보류 사유 | 결정 시점 / 권고 | 책임 |
|---|---|---|---|---|
| **U-1** | PP-3 무료/스탠다드 티어 코치마크 | 어느 팀도 명시적 채택 없음 | ux-round3 권고: frontend가 휴무 수집 뷰 첫 진입 시 1회 코치마크 + 티어 분기(`onboarding-status.role` + 연동 직원 0명) 구현 결정 | frontend |
| **U-2** | 인터랙션 매핑 short-press vs long-press | frontend R2 §4-1과 PM R2 §2.2 충돌 | ux-round3 §4 T4 권고: **PM 안 채택** (short=선택 모드 / long=드래그 보조) | frontend (코드 채택) |
| **U-3** | CommonResponse unwrap (A/B/C) | backend R2 §질문 3 → frontend R2 §1-2 (A) 채택 / backend 명시 미게시 | frontend-round3 §0 답변 3에서 (A) 확정. backend-round3 §5에서 (A) 묵시적 수용 | backend (명시 확정), frontend (구현) |
| **U-4** | FCM 실연동 v1.2 출시일 일정 확약 | backend Round 1·2·3 모두 일정 명시 없음. PM B-1 답변 미수신 | **킥오프 직후 backend 책임자 1:1 합의** — 일정 확약 불가 시 PM이 팀 티어 베타 50% 할인으로 비즈니스 모델 변경 | backend (확약), pm (B/M 변경) |
| **U-5** | 매장 모드 라이트 고정 vs 다크 옵션 / Dark Mode v1.2 활성화 | design §6 ux 검토 요청 / pm v1.3 이월 / ux 매장 라이트 고정 | UX 권고: **토큰 v1.2 박힘 + 활성화 v1.3 + 직원 앱 야간 시나리오만 우선**. 매장 모드는 라이트 고대비로 고정 | design + pm (v1.3 진입 시점 협의) |

---

## 6. 실행 로드맵

### 6.1 v1.2 MVP — MUST 11개 (출시 합격선)

| # | 기능 | 책임 팀 | 비고 |
|---|---|---|---|
| 1 | 직원 앱 카카오 OAuth + 케이스 3 환영 | frontend, backend | 진입 깔때기 |
| 2 | 직원 앱 캘린더 + 휴무 신청 BottomSheet | frontend, design | LeaveRequestSheet `['50%','92%']` |
| 3 | FCM 푸시 3종 실연동 (쉬기 전날·관리자 당일·휴무 재배치) | backend, frontend | **U-4: 일정 확약 요구** |
| 4 | 휴무 수집 뷰 + 하단 sticky CTA + 2탭 이동 fallback + 코치마크 | frontend, design | R-2/R-6/U-1/U-2 통합 |
| 5 | 매장 등록 온보딩 (케이스 1) | frontend, design | 진입 깔때기 |
| 6 | 직원 초대 BottomSheet (Kakao Share SDK) | frontend | 팀 티어 모객 경로 |
| 7 | BFF `GET /me/home-summary` 또는 client-side aggregation | backend (또는 frontend fallback) | TTI KPI 책임 |
| 8 | Phase 999: 관리자 API JWT 인가 + DEV 백도어 제거 + CI 빌드 가드 | backend | 보안·출시 차단 조건 |
| 9 | 알림 그룹화 + 영업시간 silent + 권한 요청 타이밍 | backend, frontend | R-5 |
| 10 | 달력 today 배경 `#0369A1` 변경 + 디자인 자료 갱신 | design + frontend | R-1 출시 차단 |
| 11 | JWT Keychain/Keystore 격리 (MMKV 평문 금지) | frontend | R-4 |

### 6.2 v1.2 SHOULD — 출시 후 4주 fast-follow (10건)

| # | 기능 | 사유 |
|---|---|---|
| S1 | 근무 교환 BottomSheet (`['60%','92%']`) | 빈도 낮음, 베타 검증 후 확장 |
| S2 | 딥링크 (Universal Links/App Links) + `GET /invite/{token}/preview` | 도메인 발급 일정 의존 |
| S3 | DiceBear 30종 SVG **lazy fetch** (첫 번들 4~6종) | frontend-round2 §3-5 무료티어 진입 부담 |
| S4 | BottomSheet 3단 snap 표준화 (`Invite/LeaveRequest/Conflict/Swap`) | design-round2 §1.1 / ux-round2 §3-2 토큰화 |
| S5 | 좌·우손잡이 토글 (FAB·CTA 좌우 반전) | Y-5 / ux-round2 §1-4 |
| S6 | 다크모드 토큰 파일 박힘 (UI 토글은 v1.3) | design-round2 §3.1 / U-5 |
| S7 | `?includeNext=true` 다음 달 스케줄 합산 | backend-round2 §1-2 부분 수용 |
| S8 | ETag (스케줄 조회·연간 통계·entries) | ux-round2 §2-4 / backend-round3 §3 |
| S9 | 오프라인 큐 확장 (휴무 재배치 PATCH 포함) + `X-Idempotency-Key` | Y-7 / backend-round2 §2-5 |
| S10 | 스케줄 생성 로딩 UX (10초 타임아웃 + 진행 안내) | backend-round2 §6-1 / design-round2 §2 |

### 6.3 v1.3 fast-follow / 백로그 (COULD/이월) — 5+1건

| # | 기능 | 비고 |
|---|---|---|
| C1 | 잉여 휴무 옵션 UI 라벨 변경 ("몰아서/골고루") + 미리보기 | ux-round1 PP-7 |
| C2 | PNG 주간 슬라이스 (`?mode=weekly`) | ux-round1 PP-4 / Y-2 베타 인터뷰 후 |
| C3 | 매장 모드 토글 UI (고대비·폰트 +2sp·hit area +20%) | Y-4 / design-round2 §4.3 |
| C4 | Daily Digest 알림 모드 | Y-3 / FCM 연동 후 |
| C5 | 직원→관리자 메시지 | 기획서 §4.3 검토중 |
| 추가 | 다크 모드 진입 UI 활성화 | U-5 |

### 6.4 v2.0 백로그 (WON'T) — 5건

| # | 기능 | 사유 |
|---|---|---|
| N1 | 출퇴근 버튼 | 기획서 §4.3 v2.0 로드맵 |
| N2 | 비즈니스 모델 티어 게이팅 (무료 5명·월 2회 한도) | 결제 도입 시점에 동시 활성화 |
| N3 | cursor 페이지네이션 | backend-round2 §1-6 거부 / v2.0 재논의 |
| N4 | PNG CDN 절대 경로 | backend-round2 §1-3 거부 / S3 인프라 선행 |
| N5 | 스케줄 생성 비동기 잡 + 푸시 결과 모델 | 동기 + 안내로 합의 / 직원 15명+ 매장 v1.3 검토 |

---

## 7. KPI 합격선 (15종)

| # | KPI | 목표 | 측정 방법 |
|---|---|---|---|
| 1 | **Cold-start TTI (cache miss)** | ≤ 1.5s P95 (4G) | RN trace + Sentry |
| 2 | **Warm-start TTI (cache hit)** | ≤ 0.8s P95 | RN trace |
| 3 | 스케줄 생성 깔때기 **일 단위 완수율** | ≥ 85% (24h 윈도우, 동일 점장) | 이벤트 깔때기 |
| 4 | 휴무 신청 성공률 | ≥ 95% | API 로그 |
| 5 | **스케줄 생성 API SLA** | 응답 P95 ≤ 5s, 클라 타임아웃 10s | API 로그 |
| 6 | 푸시 오픈율 (쉬기 전날) | ≥ 35% | FCM Analytics |
| 7 | 캐시 적중률 (첫 화면) | ≥ 70% | 클라이언트 telemetry |
| 8 | 팀 티어 전환율 (베타 4주) | ≥ 5% | 결제 로그 |
| 9 | 한 손 시나리오 합격 (A·B 병행) | A 15분 / B 누적 30분 | QA + 베타 ≥15명 |
| 10 | **알림 끄기율 (첫 7일)** | ≤ 15% | 시스템 권한 변경 이벤트 |
| 11 | 로그인 후 첫 휴무 신청 도달률 | ≥ 60% | 깔때기 분석 |
| 12 | **CPTC P95** (Critical Path Tap Count) | 시나리오별 상한 (§2.4 T4-5) | 탭 카운터 (UX 신규) |
| 13 | **Misfire Rate** | ≤ 8% | Undo 트리거·재진입 비율 (UX 신규) |
| 14 | NPS (보조 지표) | ≥ 7.0 (참고용) | 설문 (베타 ≥15명) |
| 15 | **저사양 기기 60fps 시연** | 갤럭시 A24/A34 (4GB RAM) 통과 | 베타 디바이스 매트릭스 |

---

## 8. 다음 액션 아이템

| # | 액션 | 책임자 | 기한 | 의존성 |
|---|---|---|---|---|
| **A1** | FCM 실연동 v1.2 출시일 일정 확약 1:1 (U-4) | backend 책임자 ↔ pm | 킥오프 +1주 | — |
| **A2** | FCM 일정 불가 시 비즈니스 모델 변경 결정 (팀 티어 베타 50% 할인) | pm | A1 결과 +3일 | A1 |
| **A3** | `docs/WorKey - 디자인.md` `--ts-cal-today-bg` `#0369A1` 갱신 PR | design (작성), pm (머지) | 킥오프 +3일 | — |
| **A4** | `docs/WorKey - 디자인.md` 휴무 수집 뷰 ASCII 레이아웃 갱신 ("생성 확정" 하단 sticky) | design (작성), pm (머지) | 킥오프 +3일 | — |
| **A5** | Phase 999 작업 일정 + CI `/dev/**` 라우트 빌드 가드 자동화 | backend | 킥오프 +1주 | — |
| **A6** | `tokens.ts` v1.2 라이트 + 다크 + storeModeOverrides 골격 (R-7) | frontend | 킥오프 +1주 | A3 |
| **A7** | EmployeeChip 44pt / CTA 56dp / Tab 3중 인코딩 / BottomSheet 3단 snap 적용 | frontend | 킥오프 +2주 | A6 |
| **A8** | 베타 사용자 ≥15명 모집 (좌손 1~2명 포함) | pm + ux | 킥오프 +2주 | — |
| **A9** | UX 시나리오 B (점심 피크 11~14시) 시연 프로토콜 작성 | ux | 킥오프 +2주 | A8 |
| **A10** | 진행 상태 자동 저장 (MMKV persist) 설계 | frontend | 킥오프 +1주 | — |
| **A11** | `GET /invite/{token}/preview` 신설 + AASA/assetlinks.json 서빙 | backend | v1.2 SHOULD | — |
| **A12** | `ScheduleDetailResponse.entries` Map → 배열 전환 | backend | v1.2 | — |
| **A13** | 출시 차단 PR 머지 가드 (R-1·R-2·R-3·R-6 자동 검사) | frontend + backend | v1.2 출시 1주 전 | A6, A7 |
| **A14** | UX Red Line 8건 차단 룰을 코드/CI에 명문화 (ux-round3 §8 권고) | team-lead 주관 4팀 협의 | 킥오프 +2주 | — |

---

## 9. 출시 합격 체크리스트 (v1.2 MVP DoD)

### 9.1 기능 합격선
- [ ] §6.1 MUST 11개 기능 모두 작동
- [ ] FCM 푸시 3종 실발송 검증 (또는 U-4 비즈니스 모델 변경 적용)
- [ ] Phase 999 관리자 API JWT 인가 + DEV 백도어 삭제 + CI 빌드 가드 통과
- [ ] BottomSheet 4종 디자인 토큰 1:1 일치 (design 검수 7개 차단 조건 통과)
- [ ] JWT Keychain/Keystore 격리 코드 적용 (MMKV 평문 0건)
- [ ] 달력 today 배경 `#0369A1` 변경 + 디자인 자료 본문 갱신 + PM 머지
- [ ] 휴무 수집 뷰 하단 sticky CTA + 2탭 이동 fallback + 코치마크 작동
- [ ] Red Line 8건 차단 룰을 코드/CI에 명문화

### 9.2 KPI 합격선
- [ ] Cold TTI P95 ≤ 1.5s (4G, 갤럭시 A24/A34)
- [ ] Warm TTI P95 ≤ 0.8s
- [ ] 스케줄 생성 API P95 ≤ 5s (타임아웃 10s)
- [ ] CPTC P95 시나리오별 상한 준수
- [ ] Misfire Rate ≤ 8%
- [ ] iOS / Android 양 플랫폼 베타 빌드 배포

### 9.3 페르소나 시연 합격선
- [ ] **시나리오 A**: 출근길 06:30 ~ 06:45 (15분) 단일 세션 스케줄 생성 완료 — PM 직접 시연
- [ ] **시나리오 B**: 점심 피크 11~14시 5세션 누적 30분 내 완료 (진행 상태 자동 저장 검증) — 베타 사용자 ≥ 15명 매장 시연 + UX 동행 관찰
- [ ] 일 단위 완수율 ≥ 85% (24h 윈도우)
- [ ] 알림 끄기율 ≤ 15% (첫 7일)

---

## 10. 결론 (한 줄 요약)

> **"v1.2 MVP는 MUST 11개 + SHOULD 10개로 확정한다. 페르소나는 UX의 38세 매장 카운터 점장으로 통합되며, 합격 시나리오는 출근길(A) + 점심 피크(B) 병행이다. KPI는 Cold/Warm TTI 두 단 + CPTC + Misfire + 일 단위 완수율 + 저사양 기기 시연을 추가하여 15종으로 확장한다. UX Red Line 8건(출시 차단 4건) + Yellow Line 7건은 코드/CI에 차단 룰로 박아 'sticky CTA 임시 복귀 PR' 같은 사고를 사전에 차단한다. 미해결 5건(U-1 코치마크 / U-2 인터랙션 / U-3 unwrap / U-4 FCM 일정 / U-5 Dark Mode)은 명시적 리스트로 남기며, 킥오프 직후 1:1 후속 합의로 결정한다. 카톡으로 돌아가지 않는 워키 — 이 한 줄이 이번 회의의 단일 목적이다."**
