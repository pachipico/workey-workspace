# [PM] Round 3 — 최종 입장 정리

> 작성자: **PM**  
> 안건: WorKey 모바일 앱 React Native 킥오프  
> 종합 입력: round1 5종 + round2 5종 + UX의 R2 질문/PM 답변  
> 목적: **Round 1/2 입장 [유지/수정/철회] 확정 + 4대 토픽 최종 결론 + v1.2 MVP 합격선 확정**

---

## 0. Round 3 한 줄 요약

> **"4팀 Round 2에서 확정된 합의 21건 중 18건을 PM이 수용·MUST/SHOULD/COULD로 분류하여 v1.2 MVP 매트릭스를 MUST 11개로 최종화한다. 페르소나는 PM 1차안(45세/06:30) → UX 정의(38세/매장 카운터)로 교체하고 시나리오 2개 병행 합격을 채택한다. 미해결 3건은 R3 명시적 미해결 리스트로 남겨 향후 결정한다."**

---

## 1. Round 1 PM 입장 — 유지/수정/철회 최종 결정

### 1.1 유지 (Round 1 그대로)

| # | PM Round 1 항목 | 4팀 응답 | 결정 |
|---|---|---|---|
| U1 | `/me/onboarding-status` 단일 진입점 활용 | backend §1-1 ✅ 이미 완료 / frontend §3-1 SplashScreen 채택 | **유지** |
| U2 | 푸시 권한 요청 = 첫 휴무 신청 완료 직후 | frontend §0 자기수정 ✅ / ux §5 ✅ / design §4.4 ✅ | **유지** |
| U3 | OS 네이티브 공유 시트 미사용 (Kakao Share SDK 단독) | design §3.2 검수 항목으로 수용 | **유지** |
| U4 | AsyncStorage 평문 JWT 금지 | backend §3·frontend §0 자기수정·design 무관 ✅ | **유지** |
| U5 | 직원 초대 BottomSheet (Kakao Share) MUST | 4팀 모두 합의 | **유지** |
| U6 | 매장 등록 온보딩(케이스 1) MUST | 4팀 모두 합의 | **유지** |
| U7 | 직원 앱 카카오 OAuth + 케이스 3 MUST | 4팀 모두 합의 | **유지** |
| U8 | 휴무 수집 뷰 MUST | design·ux 모두 동의 + 하단 sticky CTA 만장일치 | **유지 + 하단 sticky 추가** |
| U9 | 한 손 조작 페르소나 검증 합격 시나리오 | ux §0 강력 보강 → 시나리오 2개 병행으로 확장 | **유지 + 보강 (§3 참조)** |
| U10 | KPI 7종 (TTI, 완료율, 신청 성공률 등) | frontend·ux 보강 요구 | **유지 + 5종 추가 (§4 참조)** |

### 1.2 수정 (입장 변경)

| # | PM Round 1 항목 | 변경 내용 | 사유 (4팀 응답 근거) |
|---|---|---|---|
| M1 | TTI ≤ 1.5s **단일** KPI | **Cold(cache miss) 1.5s + Warm(cache hit) 0.8s 두 단 분리** | ux §1-1 강한 반박 / frontend §3-3 RN cold start 800ms~1.2s 반박 / Round 2 PM 부분 수용 → R3 확정 |
| M2 | JWT는 "MMKV 평문 금지" | **JWT는 Keychain/Keystore 강제. MMKV는 비민감 캐시·오프라인 큐 전용** | backend §3 / frontend §0 자기수정·§5-1 명시 / Round 2 PM 반박 1 |
| M3 | MUST 6개 매트릭스 | **MUST 11개로 확장** (BFF, Phase 999, 알림 그룹화, 달력 색, JWT Keychain, BottomSheet 3단, 좌·우손 토글 추가) | Round 2 §7 매트릭스 + R2 4팀 응답 |
| M4 | 페르소나 = 45세/06:30 출근길 | **UX 정의로 교체: 38세/영업 중 30초/형광등/70~80dB** | ux §0 페르소나 충돌 + 모든 팀이 UX 시나리오를 더 가혹하게 평가 |
| M5 | "출근길 06:30 시연 단일" 합격 기준 | **시나리오 A(출근길 15분) + 시나리오 B(매장 카운터 점심 피크 11~14시) 병행** | ux §1-3 / Round 2 §4.4 PM 부분 동의 → R3 확정 |
| M6 | "한 손 조작 모드 자동 감지 불가 → 기본값 한 손 친화" | **좌·우손잡이 토글 도입** (UX 발견) | ux §1-4 / frontend §3-6 / FAB·CTA 좌우 반전 |
| M7 | 드래그&드롭 = MUST + 2탭 이동 = MUST 동격 | **2탭 이동(long-press → "다른 날로 옮기기") = MUST 기본 / 드래그 = SHOULD 옵션** + 코치마크 1회 | ux §3-3 mental model 부재 / design §4.1 컨텍스트 메뉴 fallback 표준 / frontend §4-1 채택 |
| M8 | 다크 모드 v1.3 이월 (PM Round 2 결정) | **앱 내 독립 라이트/다크 설정 v1.2 SHOULD 부분 흡수** (시스템 다크 추종은 OFF, 토큰만 확정해두고 UI 토글은 v1.3) | design §3.1 Dark Mode 토큰 확정 + ux §0 매장 형광등에선 라이트 권장 |
| M9 | "DiceBear 30종 SVG = COULD" | **lazy fetch 방식으로 SHOULD** (첫 번들에 4~6종, 나머지는 prefetch) | frontend §3-5 무료티어 진입 부담 우려 |
| M10 | 베타 사용자 5명 + NPS 7.0 | **베타 ≥15명 + 태스크 완수율(휴무 수집 뷰 진입 → 확정 일 단위 ≥85%)을 1차 합격선, NPS는 보조** | ux §1-2 통계적 의미 부족 + ux §1-5 일 단위 완수율 |

### 1.3 철회 (입장 취소)

| # | PM Round 1 항목 | 철회 사유 |
|---|---|---|
| W1 | "스케줄 이력 / 근무 교환 이력은 cursor 기반" KPI | backend §1-6 거부 (offset 방식 v1.2 출시) — PM 요구의 비즈니스 가치 < backend 작업 비용. **철회.** v2.0 이후 재논의. |
| W2 | "PNG 이미지 URL은 CDN 절대 경로" | backend §1-3 거부 (S3·CDN 인프라 선행 필요) — **철회.** RN이 binary 직접 호출. |

---

## 2. UX Round 2 질문 4건 — PM 공식 답변 (산출물 등록)

> 본 답변은 PM이 본 채널 회신으로 이미 발송한 내용을 R3 산출물에 정식 등록함.

### 2.1 답변 — 클릭 뎁스 시나리오별 P95 상한

| 시나리오 | 빈도 | 짜증 임계값 (P95) | 합격선 |
|---|---|---|---|
| **휴무 신청 (직원)** | 매월 1~3회 / 직원 8명 | 3탭 | **≤ 3탭** |
| **스케줄 생성 깔때기** | 매월 1회 | 7탭 + 인터랙션 1회 | **≤ 7+1** |
| **미연동 직원 휴무 5건 일괄** | 매월 1회 / 무료 매장 | 4탭 + 다중선택 | **≤ 4+다중** |
| **직원 등록 + 초대** | 분기 1~2회 | 5탭 | **≤ 5탭** |
| **근무 교환 요청** | 월 0~2회 | 5탭 | **≤ 5탭** |
| **설정 변경** | 1회성 | 10탭 | ≤ 10탭 |

### 2.2 답변 — §3.3 흐름 단축 우선순위

| 순위 | 단계 | 조치 |
|---|---|---|
| **1순위** | 휴무 수집 뷰 충돌 해소 (UX 시나리오 A 4번 = 사망 지점) | 2탭 이동 fallback MUST 승격 / 드래그 SHOULD 강등 |
| **2순위** | 조건 입력 (4필드 위→아래 위험) | 잉여 휴무 옵션 라벨 점장 언어("몰아서/골고루") + 미리보기 1줄 |
| **3순위** | 생성 확정 컨펌 (위치 문제만) | 헤더 → 하단 sticky CTA 만장일치 적용 |

### 2.3 답변 — KPI에 클릭 뎁스 추가 — **동의**

신규 KPI 2종 §4 KPI 표에 추가:
- **Critical Path Tap Count (CPTC) P95** — 시나리오별 권장값(§2.1)
- **Misfire Rate** — 작업 중 "되돌리기·잘못 누름" 발생률 ≤ 8%

### 2.4 답변 — 점심 피크 11~14시 시연 추가 — **부분 동의 (병행)**

§3 합격 시나리오 표 참조. 시나리오 A(출근길) + 시나리오 B(점심 피크) 병행. 전제: 진행 상태 자동 저장 + 베타 5세션 누적 30분 내 완료.

---

## 3. v1.2 MVP 매트릭스 — Round 3 최종본

### 3.1 MUST (출시 차단 조건)

| # | 기능 | 책임 팀 | Round 1 → 3 |
|---|---|---|---|
| 1 | 직원 앱 카카오 OAuth + 케이스 3 환영 | frontend, backend | MUST 유지 |
| 2 | 직원 앱 캘린더 + 휴무 신청 BottomSheet | frontend, design | MUST 유지 |
| 3 | FCM 푸시 3종 실연동 (쉬기 전날·관리자 당일·휴무 재배치) | backend, frontend | MUST 유지 — backend 일정 확약 요구 |
| 4 | 휴무 수집 뷰 + **하단 sticky CTA + 2탭 이동 fallback + 코치마크** | frontend, design | MUST 보강 |
| 5 | 매장 등록 온보딩 (케이스 1) | frontend, design | MUST 유지 |
| 6 | 직원 초대 BottomSheet (Kakao Share) | frontend | MUST 유지 |
| 7 | **BFF `/me/home-summary` v1.2 도입** (또는 frontend client-side aggregation + Promise.all + stale-while-revalidate) | backend (또는 frontend fallback) | **신규 MUST** |
| 8 | **Phase 999: 관리자 API JWT 인가 + DEV 백도어 제거 + CI 빌드 가드** | backend | **신규 MUST** |
| 9 | **알림 그룹화(Android channel/iOS thread-id) + 영업시간 silent push + 권한 요청 타이밍** | backend, frontend | **신규 MUST** |
| 10 | **달력 오늘 날짜 배경 `#0369A1` 변경 (8.75:1 대비)** | design 갱신 + frontend 적용 | **신규 MUST** |
| 11 | **JWT Keychain/Keystore 격리 (MMKV 평문 금지)** | frontend | **신규 MUST** |

### 3.2 SHOULD (출시 후 4주 fast-follow)

| # | 기능 | 사유 |
|---|---|---|
| S1 | 근무 교환 BottomSheet | 빈도 낮음. 베타 검증 후 |
| S2 | 딥링크 (Universal Links / App Links) + `/invite/{token}/preview` 미리보기 API | 도메인 발급 일정 의존 |
| S3 | DiceBear 30종 SVG **lazy fetch** (첫 번들 4~6종) | 무료티어 진입 부담 우려 (frontend §3-5) |
| S4 | BottomSheet 3단 snap 표준화 (`Invite 35% / LeaveRequest 100% / Conflict 30·60·92% / Swap 60%`) | design §1.1 / ux §3-2 토큰화 |
| S5 | 좌·우손잡이 토글 (FAB·CTA 좌우 반전) | ux §1-4 / frontend §3-6 |
| S6 | 다크모드 토큰 확정 (UI 토글은 v1.3) | design §3.1 / 앱 내 독립 설정, 시스템 추종 OFF |
| S7 | `?includeNext=true` 다음 달 스케줄 합산 | backend §1-2 부분 수용 |
| S8 | ETag (스케줄 조회·연간 통계) | ux §2-4 모바일 페이로드 절감 |
| S9 | 오프라인 큐 확장 (휴무 재배치 PATCH 포함) + `X-Idempotency-Key` | backend §2-5 / ux §3-4 |
| S10 | 스케줄 생성 로딩 UX (10초 타임아웃 + 진행 안내) | backend §6-1 / design §2 풀스크린 오버레이 |

### 3.3 COULD (검토)

| # | 기능 | 비고 |
|---|---|---|
| C1 | 잉여 휴무 옵션 UI 라벨 변경 ("몰아서/골고루") + 미리보기 | ux PP-7 |
| C2 | PNG 주간 슬라이스 (`?mode=weekly`) | ux PP-4 / 베타 인터뷰 후 |
| C3 | 매장 모드 토글 (고대비·폰트 +2sp·hit area +20%) | design §4.3 토큰 신설 / **v1.3 우선** |
| C4 | Daily Digest 알림 모드 | backend FCM 연동 후 v1.3 |
| C5 | 직원→관리자 메시지 | 기획서 §4.3 검토중 |

### 3.4 WON'T (이번 MVP 제외)

| # | 기능 | 사유 |
|---|---|---|
| N1 | 출퇴근 버튼 | 기획서 §4.3 v2.0 로드맵 |
| N2 | 비즈니스 모델 티어 게이팅 (무료 5명·월 2회 한도) | 결제 도입 시점에 동시 활성화 |
| N3 | cursor 페이지네이션 | backend §1-6 거부 / v2.0 재논의 |
| N4 | PNG CDN 절대 경로 | backend §1-3 거부 / S3·CDN 인프라 선행 |
| N5 | 스케줄 생성 비동기 잡 + 푸시 결과 모델 | backend §6-1 동기 유지 / v2.0 검토 (ux §2-2 제안 보류) |

---

## 4. KPI — Round 3 최종본

| # | KPI | 목표 | 측정 |
|---|---|---|---|
| 1 | **Cold-start TTI (cache miss)** | ≤ 1.5s P95 (4G) | RN trace + Sentry |
| 2 | **Warm-start TTI (cache hit)** | ≤ 0.8s P95 | RN trace |
| 3 | **스케줄 생성 깔때기 일 단위 완수율** | ≥ 85% (24h 윈도우, 동일 점장) | 이벤트 깔때기 |
| 4 | 휴무 신청 성공률 | ≥ 95% | API 로그 |
| 5 | **스케줄 생성 API SLA** | 응답 P95 ≤ 5s, 클라 타임아웃 10s | API 로그 (backend §6-1) |
| 6 | 푸시 오픈율 (쉬기 전날) | ≥ 35% | FCM Analytics |
| 7 | 캐시 적중률 (첫 화면) | ≥ 70% | 클라 telemetry |
| 8 | 팀 티어 전환율 (베타 4주) | ≥ 5% | 결제 로그 |
| 9 | 한 손 시나리오 합격 (A·B 병행) | A 15분 / B 누적 30분 | QA + 베타 ≥15명 |
| 10 | 알림 끄기율 (첫 7일) | ≤ 15% | 시스템 권한 변경 이벤트 |
| 11 | 로그인 후 첫 휴무 신청 도달률 | ≥ 60% | 깔때기 |
| 12 | **Critical Path Tap Count (CPTC) P95** | §2.1 시나리오별 상한 준수 | 탭 카운터 (UX 신규) |
| 13 | **Misfire Rate** | ≤ 8% | Undo 트리거·재진입 비율 (UX 신규) |
| 14 | NPS (보조 지표) | ≥ 7.0 (참고용) | 설문 |
| 15 | **저사양 기기(갤럭시 A24/A34, 4GB RAM) 60fps 시연 합격** | 통과 / 실패 | 베타 디바이스 매트릭스 (frontend §3-7) |

---

## 5. 4대 핵심 토픽 — PM 최종 결론

### 5.1 토픽 1 — 모바일 최적화 API

| 결정 항목 | 결론 |
|---|---|
| BFF | `/me/home-summary` **v1.2 MUST** (backend §2-2 수용 + ux §2-1 강력 요구). 일정 5일 이상 시 frontend client-side aggregation으로 fallback 인정. |
| 두 단 TTI | Cold 1.5s / Warm 0.8s P95 — 두 KPI 모두 합격선. |
| stale-while-revalidate | MMKV 캐시 + TanStack Query staleTime 5분. SplashScreen에서 캐시 hit 시 즉시 라우팅. |
| 다음 달 합산 | `?includeNext=true` SHOULD (backend §1-2). |
| ETag | 스케줄 조회·연간 통계 SHOULD (backend §6-2). |
| 시간대 | `X-Timezone: Asia/Seoul` 헤더 + contract 명문화 (backend §1-5). |
| Cache-Control | backend §6-2 제안값 그대로 적용 (employees 5분 / schedule 1분 / annual 1시간). |

### 5.2 토픽 2 — RN 네이티브 연동 (푸시 / AsyncStorage)

| 결정 항목 | 결론 |
|---|---|
| FCM 토큰 등록 | **`PATCH /me/fcm-token { fcmToken }`** (frontend §0 자기수정 / backend §2-1). `platform` 필드 불필요. |
| FCM 실연동 | v1.2 MUST. backend 일정 확약 요구 (§6 미해결). |
| 알림 카테고리 | Android `NotificationChannel` 4종 / iOS `thread-id` 4종 + 영업시간 silent push (members.notification_preferences) |
| 권한 요청 타이밍 | 첫 휴무 신청 완료 직후 (4팀 만장일치) |
| Daily Digest | v1.3 SHOULD (FCM 연동 후) |
| JWT 저장 | **react-native-keychain** (Keychain/Keystore). MMKV는 비민감 캐시·오프라인 큐 전용 |
| 오프라인 큐 | 휴무 신청·근무 교환·**휴무 재배치 PATCH** 포함 (ux §3-4) + `X-Idempotency-Key` 헤더 (backend §2-5) |
| Splash 라우팅 | MMKV onboarding-status 캐시 hit 시 즉시 라우팅 + 백그라운드 재검증 (ux §3-1) |
| 딥링크 | SHOULD + `/invite/{token}/preview` 미리보기 API (backend §5 / ux PP-6) |

### 5.3 토픽 3 — 디자인 이식 (BottomSheet 등)

| 결정 항목 | 결론 |
|---|---|
| BottomSheet snap 표준 | `Invite 35% / LeaveRequest 100% / Conflict 30·60·92% / Swap 60%` 토큰화 (design §1.1 + ux §3-2) |
| 핸들 | 너비 40dp / 색 `#0369A1` (대비 8.75:1) — design §1.1 자체 수정 |
| 생성 확정 위치 | **하단 full-width sticky 56dp** (4팀 만장일치) |
| 드래그 fallback | long-press → 컨텍스트 메뉴 → 달력 셀 1탭 (design §4.1 표준 + 첫 진입 코치마크 1회) |
| 충돌 셀 | Long-press → 미니 팝오버 (달력 60% 노출) + "재배치 모드" 버튼 (design §4.2) |
| Floating preview + 햅틱 | 드래그 시 손가락 위 20dp + Medium impact + 5초 Undo 토스트 (design §1.3) |
| 달력 오늘 색 | `#0369A1` 변경 — `docs/WorKey - 디자인.md` `--ts-cal-today-bg` 갱신 + PM 머지 |
| Tab Bar | 색 + 아이콘 형태(채워짐/외곽선) **이중 인코딩** (ux §4-4) |
| EmployeeChip | minHeight **44pt**로 확장 (ux §4-6 / 디자인 32pt → 44pt) |
| Dark Mode | 토큰 확정 (design §3.1) but UI 토글은 **v1.3**. 시스템 추종 OFF. |
| 매장 모드 토글 | **v1.3 COULD**로 이월. 단, 3개 요소만 v1.2 흡수: (a) hit area 48dp 기본 (b) 영업시간 silent push (c) 달력 오늘 색 자동 적용 |

### 5.4 토픽 4 — 사용자 환경 (한 손 조작 페르소나)

| 결정 항목 | 결론 |
|---|---|
| 페르소나 | **UX 정의로 통합 교체** — 38세 / 분식+카페 / 직원 8명(연동4·미연동4) / 매장 카운터 / 영업 중 / 형광등 + 직사광 / 70~80dB / 30~90초 자투리 |
| 합격 시나리오 | **A 출근길 06:30 (15분)** + **B 점심 피크 11~14시 (5세션 누적 30분)** 병행 |
| 좌·우손잡이 토글 | SHOULD — FAB·CTA 좌우 반전 + 첫 온보딩에서 묻기 (ux §1-4 / frontend §3-6) |
| Thumb Zone CTA | 핵심 액션 = bottom-fixed full-width hit area ≥ 48dp |
| 드래그 fallback | 2탭 이동 = MUST 기본값 / 드래그 = SHOULD 옵션 (mental model 통일) |
| EmployeeChip 크기 | minHeight 44pt (노안 점장 손가락 가림 방지) |
| 코치마크 | 휴무 수집 뷰 첫 진입 시 1회 (티어 분기 안내 + 칩 조작 안내) |
| 진행 상태 자동 저장 | **MVP 신규 요구사항** — 영업 중 30초 자투리 다회 시나리오 B의 전제조건 |

---

## 6. 명시적 미해결 (R3에서도 결정 안 된 항목)

> ux §7 인용 *"R3에선 합의 후보 21건 중 최소 15건을 합의로 굳히고, 합의 안 된 것은 명시적 미해결 리스트로 남겨라."*  
> PM Round 3에서 18건 합의. 미해결 3건 등록.

| # | 미해결 항목 | 보류 사유 | 결정 시점 |
|---|---|---|---|
| O1 | **FCM 실연동 v1.2 일정 확약** | backend §6에 일정 명시 없음. PM이 backend 책임자에 직접 요구해도 본 회의 라운드 내 확답 못 받음 | **킥오프 직후 backend 책임자와 1:1 합의** — 일정 확약 불가 시 PM이 비즈니스 모델 §7 변경(팀 티어 베타 50% 할인) 책임 |
| O2 | **CommonResponse 단건/다건 분리 vs Axios interceptor unwrap** | backend §8 질문 (A/B/C) 미결 / frontend §1-2는 (A) interceptor 자동 unwrap 채택 의지 | **frontend·backend 양자 합의** — PM은 frontend 안 (A) 권장 |
| O3 | **매장 모드 라이트 고정 vs 다크 옵션** | design §6 ux에 검토 요청 / ux 답변은 본 회의 라운드 내 미수신 | **v1.3 진입 시점 design + ux 협의** — PM은 v1.2에서 결정 안 함 (라이트 단일 출시) |

---

## 7. 출시 합격 체크리스트 — Round 3 최종본

### 7.1 기능 합격선

- [ ] §3.1 MUST 11개 기능 모두 작동
- [ ] FCM 푸시 3종 실발송 검증 (또는 §6 O1 비즈니스 모델 변경 적용)
- [ ] Phase 999 관리자 API JWT 인가 + DEV 백도어 삭제 + CI 빌드 가드 통과
- [ ] BottomSheet 4종 디자인 토큰 1:1 일치 (design §3.2 검수 기준)
- [ ] JWT Keychain/Keystore 격리 코드 적용
- [ ] 달력 오늘 날짜 `#0369A1` 변경 + 디자인 자료 본문 갱신 + PM 머지
- [ ] 휴무 수집 뷰 하단 sticky CTA + 2탭 이동 fallback + 코치마크 작동

### 7.2 KPI 합격선

- [ ] Cold TTI P95 ≤ 1.5s (4G, 갤럭시 A24/A34)
- [ ] Warm TTI P95 ≤ 0.8s
- [ ] 스케줄 생성 API P95 ≤ 5s
- [ ] CPTC P95 시나리오별 상한 준수 (§2.1)
- [ ] Misfire Rate ≤ 8%
- [ ] iOS / Android 양 플랫폼 베타 빌드 배포

### 7.3 페르소나 시연 합격선

- [ ] **시나리오 A**: 출근길 06:30 ~ 06:45 (15분) 단일 세션 스케줄 생성 완료 — PM 직접 시연
- [ ] **시나리오 B**: 점심 피크 11~14시 5세션 누적 30분 내 완료 (진행 상태 자동 저장 검증) — 베타 사용자 ≥ 15명 실제 매장 시연 + UX 동행 관찰
- [ ] 일 단위 완수율 ≥ 85% (24h 윈도우)
- [ ] 알림 끄기율 ≤ 15% (첫 7일)

---

## 8. PM Round 3 최종 입장 (한 줄)

> **"v1.2 MVP는 MUST 11개 + SHOULD 10개로 확정한다. 페르소나는 UX의 38세 매장 카운터 점장으로 통합되며, 합격 시나리오는 출근길 + 점심 피크 병행이다. KPI는 Cold/Warm TTI 두 단 + CPTC + Misfire + 일 단위 완수율 + 저사양 기기 시연을 추가하여 15종으로 확장한다. 미해결 3건(FCM 일정·CommonResponse 분리·매장 모드)은 명시적 리스트로 남기고, 킥오프 직후 1:1 후속 합의로 결정한다. PM은 그때까지 비즈니스 모델 변경(팀 티어 50% 할인)에 대한 의사결정 권한을 유보한다."**

---

## 9. team-lead 보고

> **"PM Round 3 작성 완료. 산출물: `meeting/frontend-kickoff-meeting/evidence/pm-round3.md`. Round 1 입장 유지 10건·수정 10건·철회 2건 / UX 4개 질문 공식 답변 등록 / 4대 토픽 최종 결론 / MVP 매트릭스(MUST 11/SHOULD 10/COULD 5/WON'T 5) / KPI 15종 / 미해결 3건 명시. SendMessage·TaskUpdate 도구 미노출 — team-lead 대행 요청."**
