# [PM] Round 2 — 4팀 Round 1 반박/리뷰

> 작성자: **PM**  
> 안건: WorKey 모바일 앱 React Native 킥오프  
> 입력: `evidence/{backend,frontend,design,ux}-round1.md`  
> 관점: **비즈니스 우선순위 / MVP 범위 / KPI 측정성**

---

## 0. 총평 (한 문단 요약)

4팀의 Round 1을 PM 관점에서 검토한 결과, **단순한 합의 회의가 아니라 'MVP 범위 재정의 회의'가 되어야 한다**. 특히 **UX의 점장 1인칭 분석**이 PM이 작성한 Round 1의 페르소나(45세 최기준 / 06:30 출근길)를 더 가혹한 현실(**38세 / 영업 중 30초 자투리 / 한 손 + 형광등 + 70~80dB 소음**)로 재정의했고, 이를 받아들이면 **PM Round 1의 MUST 6개 중 최소 2개의 합격 기준이 흔들린다**. 본 문서는 4팀 입장을 PM이 정조준해 반박·수용하고, MVP 매트릭스·KPI를 어떻게 재조정할지 결정한다.

---

## 1. Backend Round 1 — PM 리뷰

### 1.1 PM이 동의하는 부분 ✅

- 핵심 API 6개군(Auth/Me/Employee/Schedule/Store/Export) 명세가 구체적이고 RN 즉시 연동 가능 — **Round 1에서 PM이 KPI로 잡은 "통합 엔드포인트로 첫 화면 결정"이 실제 `/me/onboarding-status`로 충족됨.**
- JWT 30분/Refresh 7일 Rotation + Keychain/Keystore 권장 — PM Round 1 §3.3 "AsyncStorage 평문 저장 금지" 결정과 정확히 일치.
- 스케줄 생성 API 응답 1~5초 가능성 명시 — **PM이 놓친 리스크**. KPI 보강 필요(§8 참조).

### 1.2 PM이 반박하는 부분 ❌

#### 반박 1: BFF 엔드포인트의 "v1.2에서 검토 권장" 톤다운에 **반대**

> 인용: backend §2.1 — *"현재 v1.1 범위 外. RN 앱은 Promise.all([api1, api2, api3]) 병렬 호출로 우선 구현하고, v1.2에서 BFF 도입 여부를 결정할 것을 권장한다."*

| 쟁점 | Backend 입장 | PM 반박 |
|---|---|---|
| 우선순위 | 병렬 호출로 우회 가능, BFF는 후순위 | **TTI 1.5s KPI(§6.1) 충족 책임은 PM이 진다. 병렬 호출 3건 + 4G 환경에서 1.5s 95p 달성 보장이 backend 책임이라면 OK, 아니면 BFF는 v1.2 MUST.** |
| 대시보드 페이로드 | `ScheduleDetailResponse.entries`가 직원 수 × 30일 = 큼, lazy loading 분리 권장 | **lazy loading은 첫 화면이 비어있는 시간을 만드는 안티패턴.** UX §6.T1 점장 인용 *"앱 켜고 0.8초 안에 이번 달 스케줄 보여라"*. → BFF + stale-while-revalidate 캐시가 정답. |

**PM 결정**: BFF (`GET /me/home-summary` 또는 `GET /stores/{id}/dashboard-summary`)는 **v1.2 MVP 출시 전 SHOULD → MUST로 승격**. 단, 일정상 백엔드 부담이라면 frontend가 client-side aggregation + MMKV 캐시로 임시 해결하는 fallback 인정.

#### 반박 2: FCM "v1.2 deferred" 그대로 두면 팀 티어 가치 0

> 인용: backend §6 미결 항목 — *"FCM 실제 발송: NoOp 어댑터 → Firebase Admin SDK 연동"* (구체 일정 없음)

PM Round 1 §1.2에서 "FCM 푸시 = MUST"라고 못 박았다. backend가 *일정 없이 deferred*로만 적은 것은 **팀 티어 매출(월 19,900원)의 정당화 근거를 v1.2에서 빼겠다는 의미**가 된다.

**PM 결정**: 다음 둘 중 하나를 backend가 회의에서 확정해야 한다.
- (A) v1.2 출시일까지 **FCM 3종(쉬기 전날·관리자 당일·휴무 재배치) 실연동 보장**
- (B) FCM 미연동으로 출시 → **팀 티어 베타 가격 무료 또는 50% 할인 수정** (PM이 비즈니스 모델 변경 책임)

#### 반박 3: 관리자 API 인가 (`anyRequest().permitAll()`) 문제는 **MVP 출시 직전 차단 조건**

> 인용: backend §6 — *"관리자 API 인증: anyRequest().permitAll() / Phase 999"*

frontend round1 §8에서 *"prd 전 JWT 헤더 붙이는 interceptor 준비"*로 가볍게 처리했는데, **MVP 출시 = prd 배포**이므로 Phase 999는 v1.2 MUST다. 다른 매장 데이터 무인증 노출은 **개인정보보호법 위반 잠재 리스크**.

**PM 결정**: Phase 999 (관리자 API JWT 인가 + DEV 백도어 제거)를 **v1.2 MUST 추가** (PM Round 1 §1.2 매트릭스 보강).

### 1.3 Backend 결론

- **유지**: API 명세는 견고함. RN 작업 즉시 진행 가능.
- **승격 요구**: BFF·FCM·Phase 999 3건을 v1.2 MUST로.
- **명문화 요구**: 스케줄 생성 API 응답 SLA(상한 5초) + 클라이언트 타임아웃 정책.

---

## 2. Frontend Round 1 — PM 리뷰

### 2.1 PM이 동의하는 부분 ✅

- React Navigation 구조 (Stack/Tab/Modal) 명확. 케이스 1~5 분기 SplashScreen 로직 OK.
- TanStack Query + MMKV + Zustand 3-layer 아키텍처는 **PM의 KPI "AsyncStorage 캐시 적중률 ≥ 70%"** 달성에 충분.
- `@gorhom/bottom-sheet` 채택 — design round1 §2.1.1 규격(snap points, handle, backgroundColor)과 호환.
- 오프라인 큐 (휴무 신청 / 근무 교환) 설계 — PM Round 1 §3.2 "AsyncStorage 오프라인 큐" 요구사항 충족.

### 2.2 PM이 반박하는 부분 ❌

#### 반박 1: MMKV vs Keychain/Keystore — **JWT 저장은 frontend의 MMKV로 끝나면 안 됨**

> 인용: frontend §2.3 — *"결정: MMKV 채택 (주 저장소) → 토큰 저장 storage.set('accessToken', ...)"*  
> vs backend §3 — *"AsyncStorage 사용 시 위험: 루팅/탈옥 기기에서 평문 탈취 가능. 권장: expo-secure-store → Keychain/Keystore"*

MMKV는 AES-256 암호화가 가능하지만 **암호화 키가 코드 또는 ENV에 있으면 평문과 동등한 취약점**이다. 디바이스 hardware-backed 보안(Secure Enclave / TEE)을 쓰는 Keychain/Keystore와는 보안 등급이 다르다.

**PM 결정**:
- 일반 캐시·설정·온보딩 상태 → **MMKV** (frontend 안 그대로)
- **JWT(Access/Refresh) → Keychain/Keystore** (`expo-secure-store` 또는 `react-native-keychain`)
- frontend round1의 토큰 저장 코드 예시는 **수정 필수**

#### 반박 2: 드래그&드롭의 "한 손 fallback" 처리가 약함

> 인용: frontend §4.3 — *"DayOffChip ... onLongPress = startDrag, onPress = openRelocatePicker"*

코드 자체는 fallback 의도가 보이는데, **UX round1 §1 시나리오 A의 4·7번 "한 손 거의 불가"** 진단을 충족하기에는 약하다. UX는 *"드래그 fallback: 칩 long-press → 메뉴 → '이 직원의 휴무를 다른 날로 옮기기' → 달력 셀 1탭 — 드래그 없이도 동일 결과"*를 요구한다. frontend는 long-press를 드래그 시작으로, short-press를 RelocatePicker로 매핑했는데 이는 **점장 멘탈 모델과 반대**(점장은 long-press를 컨텍스트 메뉴로 이해).

**PM 결정**: 인터랙션 매핑을 **반대로** 변경하라.
- short-press(탭) → 칩 선택 + "어디로 옮길까요?" 모드로 전환 → 셀 1탭으로 이동 완료
- long-press → 드래그 시작 (고급 사용자용)
- 드래그&드롭 자체는 SHOULD, 2탭 이동이 MUST

#### 반박 3: BFF에 대해 backend에 떠넘기는 톤

> 인용: frontend §1-2 — *"backend-agent에 요청 예정: GET /stores/{id}/dashboard-summary ... 검토해달라"*

PM도 BFF 도입에 찬성하지만 backend가 *"v1.2 검토 권장"*으로 답한 상태다. **frontend가 client-side aggregation + MMKV 캐시 + stale-while-revalidate로 first-paint TTI 1.5s를 임시 충족할 수 있는지** 답해야 한다. 이것이 안 되면 backend BFF가 MUST가 되어야 하고, PM은 backend에 일정을 요구할 명분을 frontend로부터 받아야 한다.

### 2.3 Frontend 결론

- **유지**: 라이브러리 선택·아키텍처·오프라인 큐 설계.
- **수정 요구**: JWT는 Keychain/Keystore. 드래그/탭 인터랙션 우선순위 반대로.
- **답변 요구**: client-side aggregation으로 TTI 1.5s 충족 가능 여부 — Round 2 질문으로 발사 (§9).

---

## 3. Design Round 1 — PM 리뷰

### 3.1 PM이 동의하는 부분 ✅

- 컬러 토큰 sky-500 매핑 명확. RN `colors.ts` 분리 권고 + `minHeight: 48` 강제 적용 결정 — **PM Round 1 §4.2 "토큰 사용률 raw hex 0건" KPI** 충족 가능.
- BottomSheet/FAB/TabBar/Modal/Toast 5종 컴포넌트 RN 규격 표 — frontend의 `@gorhom/bottom-sheet` 채택과 호환.
- WCAG AA 대비 검증 (primary-ink on white = 8.75:1) — **PM의 야외 시인성 요구를 일부 충족**.

### 3.2 PM이 반박하는 부분 ❌

#### 반박 1: Dark Mode 우선순위 — **PM은 v1.2 MVP에서 빼고 싶다**

> 인용: design §5 — *"Dark Mode 팔레트 미정의 / 심각도 🟠 높음 / RN 구현 전 다크 팔레트 확정 필요"*  
> vs UX §6.T3 — *"매장 형광등 환경에서 라이트 모드가 더 잘 보이는 경우가 많음 — 시스템 다크 따라가지 말고 앱 내 설정 분리"*

design은 다크모드를 v1.2 진입 조건으로 격상시키려 하지만, **UX 페르소나가 "매장 형광등 환경에선 라이트가 더 좋다"라고 했고**, 점장 1인칭으로 다크모드를 요구한 흔적이 없다. PM 입장에선 다크모드 토큰 정의 = MVP 외부 작업이다.

**PM 결정**:
- v1.2 MVP는 **라이트 모드 단일 출시**
- 시스템 다크모드 자동 추종 OFF (`useColorScheme` 무시)
- 다크모드는 **v1.3 SHOULD**
- design round1 §5 "심각도 🟠 높음" → 🟡 중간으로 재분류

#### 반박 2: "생성 확정" 버튼 위치 변경 — **PM 동의, 단 backend·UX 검수 필요**

> 인용: design §2.3 권고사항 — *"휴무 수집 뷰의 생성 확정 버튼은 반드시 화면 하단 고정 (sticky bottom) 배치"*

이 변경은 **디자인 자료(`docs/WorKey - 디자인.md` §휴무 수집 뷰)의 ASCII 레이아웃과 모순**된다. design이 이를 자체 수정 권고로 적은 것은 좋은데, 기획서/디자인 자료 두 문서를 갱신해야 한다.

**PM 결정**: 디자인팀이 v1.2 RN 구현 착수 전에 디자인 자료 본문을 수정하고 PR로 공유. **PM이 머지 승인.**

#### 반박 3: "달력 오늘 날짜 sky-500 + 흰 텍스트 = 2.9:1" 대비 부족 — **MVP 차단 조건**

> 인용: design §2.4 — *"#0EA5E9 + 흰 텍스트: 2.9:1 ⚠️"*

WCAG AA(4.5:1)·AAA(7:1) 기준 모두 미달. 달력은 앱의 가장 자주 보는 표면. 점장이 "오늘 어디지" 못 찾으면 모든 KPI가 무너진다.

**PM 결정**: design은 둘 중 하나를 v1.2 MVP 진입 전 선택해야 한다.
- (A) 오늘 날짜 배경을 `#0369A1` (primary-ink, 8.75:1)로 변경
- (B) 텍스트를 흰색 볼드 + 외곽선 추가 (대형 텍스트 기준 3:1 충족)

→ PM은 **(A) 권장**. design `--ts-primary-ink-dark`가 이미 정의되어 있어 토큰 추가 비용 0.

### 3.3 Design 결론

- **유지**: 컴포넌트 5종 규격, 토큰 RN 매핑, Thumb Zone 가이드.
- **승격**: "오늘 날짜 대비 부족"을 v1.2 차단 조건으로 격상.
- **강등**: Dark Mode를 v1.3로 이월.
- **수정 요구**: 디자인 자료 본문의 "생성 확정" 버튼 위치 갱신 + PM 머지.

---

## 4. UX Round 1 — PM 리뷰 (가장 무겁게)

### 4.1 PM이 강하게 동의하는 부분 ✅✅

- **페르소나 재정의**: PM Round 1의 "45세 / 06:30 출근길" 시나리오를 UX가 "38세 / 영업 중 30초 자투리 / 한 손 / 70~80dB / 형광등"으로 더 가혹하게 재정의 → **PM 수용**. PM Round 1 §5.1 페르소나는 본 라운드부터 UX 정의로 통합한다.
- **PP-1 ~ PP-7 페인포인트** 모두 실재 위험. 특히 PP-5 "알림 피로도", PP-7 "균등/연속 옵션 라벨" 두 개는 PM이 Round 1에서 못 잡았던 사각지대.
- **시나리오 A 4·7번 한 손 거의 불가** — frontend round1 §4.3 fallback이 약하다는 PM의 §2.2 반박과 정확히 같은 결론.

### 4.2 PM이 반박하는 부분 ❌

#### 반박 1: "TTI 0.8초 안에 이번 달 스케줄" — **불가능. 1.5초로 합의 요청**

> 인용: ux §6.T1 — *"앱 켜고 0.8초 안에 이번 달 스케줄 보여라. 그 이상 걸리면 앱 닫고 카톡 본다."*

점장 1인칭의 강조는 이해하지만, **4G 환경 + 스케줄 응답 페이로드(직원 8명 × 30일 = 240 entries) + RN cold start**의 물리적 합산은 0.8초가 불가능하다. **stale-while-revalidate 캐시가 있는 warm start에서만 0.8초가 가능**하고, 첫 진입은 1.5초가 현실선이다.

**PM 결정**: KPI를 두 단으로 분리.
- **Cold start TTI ≤ 1.5s 95p** (4G, 미드레인지 안드로이드)
- **Warm start (캐시 hit) TTI ≤ 0.8s 95p** ← UX 요구 충족 지점
- 두 KPI 모두 §8에서 측정 명세화

#### 반박 2: "매장 모드(Store Mode) 토글" — **MVP 외부**

> 인용: ux §5 — *"매장 모드(Store Mode) 토글 / 폰트 +1단계 / hit area +20% / contrast 강화 / silent push / 한 손 모드 우측 정렬"*

이건 **별도 제품 모드를 신설하자는 제안**이라, design 토큰 분기 + frontend 컴포넌트 분기 + UX 가이드 + 점장 온보딩 1회 안내 = **최소 2주 추가 공수**. v1.2 MVP 일정에 들어가면 다른 MUST가 밀린다.

**PM 결정**:
- 매장 모드 자체는 v1.3 후보(SHOULD)로 이월
- 단, **3가지 핵심 요소만 v1.2 MVP에 흡수**:
  - (a) hit area 기본값을 `minHeight: 48` 적용 (design §5 이미 결정)
  - (b) 영업시간 silent push (FCM 페이로드 옵션) — UX §3 권고와 동일, FCM 인프라 작업에 같이 끼워 넣음
  - (c) primary-ink(`#0369A1`) 기반 high-contrast 모드는 §3.2 반박 3과 합쳐 자동 적용

#### 반박 3: "PNG 1주씩 4장 + 전체 1장" — **무료 티어 제공 비용 검토 필요**

> 인용: ux PP-4 — *"PNG 출력 시 '1주씩 4장 + 전체 1장' 멀티 이미지 옵션. 무료 티어에도 이 옵션은 줘야 한다."*

기획서 §6 출력 형식은 PNG 단일이고, §7 비즈니스 모델에서 PNG는 무료 티어다. UX 요구를 받으면 **무료 티어 출력 비용이 5배 늘어남** (서버 렌더링 5번). 점장 페르소나가 정말 필요로 한다면 받겠지만, **카톡 줌인이 정말 그렇게 큰 페인인지** 점장 5명 인터뷰로 검증한 후 결정하는 것이 PM의 입장.

**PM 결정**: 멀티 이미지 옵션은 **v1.2 fast-follow (출시 후 4주 내 베타 사용자 인터뷰 기반 판단)**. MVP 차단 조건 아님. 단, 알림에 *"카톡 공유 후 줌인이 필요하면 알려주세요"* 피드백 채널을 첨부.

### 4.3 PM이 부분 동의하는 부분 🟡

#### 부분 동의 1: 알림 피로도 → **Daily Digest는 v1.3, 영업시간 silent + 권한 요청 타이밍은 v1.2 MUST**

> 인용: ux §3 — Daily digest, 영업시간 silent, 권한 요청 타이밍 3종

| UX 권고 | PM 판단 | MVP? |
|---|---|---|
| 영업시간 자동 silent push | FCM 페이로드 옵션 1줄, 백엔드 추가 비용 적음 | **MUST** (FCM 작업과 동시) |
| 권한 요청 타이밍을 첫 휴무 신청 직전으로 | Frontend 단독 구현 가능 | **MUST** |
| Daily digest (변경사항 N건 모아서 1회) | 백엔드 알림 큐 + 묶음 로직 신규 | **SHOULD → v1.3** |
| 알림 그룹화 (Android channel + iOS thread-id) | OS 표준, frontend 반나절 | **MUST** |

#### 부분 동의 2: 무료 티어 한도 미경고 (PP-6) → **MVP 외부**

> 인용: ux PP-6 위험표 — *"생성 월 2회 무료 한도 초과 직전 무경고 → 분노"*

backend round1 §6 *"비즈니스 모델 티어 제한 로직: 결제 도입 시점에 처리"*. **결제 도입 자체가 v1.2 외부**이므로 한도 표시 UI도 같이 후순위. 단, **무료 티어 한도가 v1.2 출시일 시점에 어떻게 운영될지 PM이 명문화해야 한다** — "무제한 베타" 정책으로 v1.2 출시, 결제 도입 시점에 동시 활성화.

### 4.4 UX 결론

- **PM 페르소나 정의를 UX 정의로 교체** (PM Round 1 §5.1 → UX §0)
- **알림 그룹화·영업시간 silent·권한 요청 타이밍 3종을 v1.2 MUST로 수용**
- **TTI KPI 0.8s/1.5s 두 단 분리**
- **매장 모드·멀티 PNG·티어 한도 표시는 v1.3 이월**

---

## 5. 4팀 입장 충돌 매트릭스

| 쟁점 | Backend | Frontend | Design | UX | PM 최종 결정 |
|---|---|---|---|---|---|
| **TTI 목표** | (언급 없음) | 캐시 활용 | (언급 없음) | 0.8s 요구 | **Cold 1.5s / Warm 0.8s 두 단** |
| **JWT 저장** | Keychain/Keystore | MMKV | (언급 없음) | (언급 없음) | **Backend 입장 채택 — Keychain/Keystore** |
| **드래그&드롭** | (언급 없음) | long-press 드래그 | 드래그&드롭 가이드 | "거의 불가" | **2탭 이동 = MUST / 드래그 = SHOULD** |
| **Dark Mode** | (언급 없음) | (언급 없음) | v1.2 진입 조건 (🟠) | 라이트 권장 | **v1.3로 이월** |
| **BFF 엔드포인트** | v1.2 검토 | backend에 요청 | (언급 없음) | aggregation 요구 | **v1.2 MUST 승격 (또는 frontend client-side aggregation)** |
| **FCM 실연동** | NoOp / 일정 미정 | 토큰 등록 미리 구현 | (언급 없음) | 알림 피로도 우려 | **v1.2 MUST + 일정 확정 요구** |
| **Phase 999 (관리자 인가)** | v1.2 deferred | interceptor 준비 | (언급 없음) | (언급 없음) | **v1.2 MUST 승격** |
| **알림 daily digest** | (언급 없음) | (언급 없음) | (언급 없음) | 강하게 요구 | **v1.3 SHOULD** |
| **매장 모드 토글** | (언급 없음) | (언급 없음) | (언급 없음) | 강하게 요구 | **3개 요소만 흡수, 토글 자체는 v1.3** |
| **달력 오늘 색 대비** | (언급 없음) | (언급 없음) | 2.9:1 ⚠️ | (언급 없음) | **primary-ink(#0369A1)로 교체 — MVP MUST** |

---

## 6. PM Round 1 입장 변경/유지 결정

### 6.1 입장 유지 (3건)

| PM Round 1 항목 | 근거 |
|---|---|
| MUST 6개 우선순위 매트릭스 | UX·design·frontend 모두 동일 영역을 다룸. 변경 없음. |
| KPI 7종 측정 항목 | 각 팀 round1이 측정 가능 메커니즘 (Sentry, FCM Analytics, 클라이언트 telemetry) 모두 인지. |
| 출근길 15분 합격 시나리오 | UX가 "30초 자투리 다회"로 더 강하게 만들었지만, 점장 시연용 합격 기준은 여전히 15분 단일 시나리오로 유지. |

### 6.2 입장 변경 (5건)

| PM Round 1 항목 | 변경 내용 | 사유 |
|---|---|---|
| §3.2 JWT를 AsyncStorage 평문 금지 | **Keychain/Keystore + MMKV는 일반 캐시만**으로 명문화 | frontend MMKV 단독 사용 우려 |
| §6.1 TTI ≤ 1.5s 단일 KPI | **Cold 1.5s / Warm 0.8s 두 단으로 분리** | UX §6.T1 0.8s 요구 + 물리적 한계 |
| §1.2 매트릭스 MUST 6 | **MUST 9로 확장** (BFF + Phase 999 + 알림 그룹화 추가) | backend 일정 압박 + UX 알림 피로도 |
| §5.1 페르소나 (45세 / 06:30) | **UX 정의 (38세 / 영업 중 30초)로 교체** | UX 분석이 더 가혹한 현실 반영 |
| §4.2 BottomSheet 토큰 일치 체크리스트 | **달력 오늘 날짜 색 변경(primary-ink)을 추가 차단 조건으로** | design §2.4 WCAG 미달 |

### 6.3 입장 철회 (1건)

| PM Round 1 항목 | 철회 사유 |
|---|---|
| §1.2 매트릭스 SHOULD "DiceBear 30종 SVG" | UX·design 어느 팀도 우선순위 언급 없음 + 백엔드는 이미 enum만 노출. → **COULD로 강등**. |

---

## 7. v1.2 MVP 매트릭스 — Round 2 갱신본

| # | 기능 | Round 1 PM | Round 2 PM | 변경 사유 |
|---|---|---|---|---|
| 1 | 직원 앱 카카오 OAuth + 케이스 3 | MUST | **MUST** | 유지 |
| 2 | 직원 앱 캘린더 + 휴무 신청 시트 | MUST | **MUST** | 유지 |
| 3 | FCM 푸시 3종 실연동 | MUST | **MUST** | 유지 + backend 일정 확약 요구 |
| 4 | 휴무 수집 뷰 | MUST | **MUST** + 2탭 이동 fallback | UX §1 시나리오 A 4·7번 |
| 5 | 매장 등록 온보딩 (케이스 1) | MUST | **MUST** | 유지 |
| 6 | 직원 초대 BottomSheet (Kakao Share) | MUST | **MUST** | 유지 |
| 7 | 근무 교환 BottomSheet | SHOULD | **SHOULD** | 유지 |
| 8 | 딥링크 (Universal/App Links) | SHOULD | **SHOULD** | 유지 |
| 9 | DiceBear 30종 SVG | SHOULD | **COULD** | 4팀 어느 곳도 우선 언급 없음 |
| 10 | 잉여 휴무 옵션 UI | COULD | **COULD** + 라벨 변경 | UX PP-7 점장 언어로 |
| 11 | 출퇴근 버튼 | WON'T | **WON'T** | 유지 (v2.0) |
| **12 (신규)** | **BFF `/me/home-summary` 또는 client-side aggregation** | — | **MUST** | TTI KPI 책임 |
| **13 (신규)** | **Phase 999 관리자 API JWT 인가 + DEV 백도어 제거** | — | **MUST** | 보안 + 출시 차단 조건 |
| **14 (신규)** | **알림 그룹화 + 영업시간 silent + 권한 타이밍** | — | **MUST** | UX 알림 피로도 |
| **15 (신규)** | **달력 오늘 날짜 색 변경 (`#0369A1`)** | — | **MUST** | WCAG AA 차단 조건 |
| **16 (신규)** | **JWT Keychain/Keystore 강제** | — | **MUST** | Frontend MMKV 단독 우려 |

→ MUST **6개 → 10개**로 확장. 일정 부담은 §9 Round 2 질문으로 backend·frontend에 확인.

---

## 8. KPI 재정의 — Round 2 갱신본

| KPI | Round 1 | Round 2 갱신 | 측정 방법 |
|---|---|---|---|
| 첫 화면 TTI | ≤ 1.5s 95p | **Cold ≤ 1.5s 95p / Warm ≤ 0.8s 95p** | Sentry Performance + RN custom trace |
| 스케줄 생성 깔때기 완료율 | ≥ 85% | 유지 | 이벤트 깔때기 |
| 휴무 신청 성공률 | ≥ 95% | 유지 | API 로그 |
| **스케줄 생성 API SLA** | (없음) | **신규: 응답 ≤ 5s 95p, 타임아웃 10s** | API 로그 (backend round1 §2.3) |
| 푸시 오픈율 | ≥ 35% | 유지 | FCM Analytics |
| 캐시 적중률 | ≥ 70% | 유지 | 클라이언트 telemetry |
| 팀 티어 전환율 | 베타 4주 ≥ 5% | 유지 | 결제 로그 |
| 한 손 시나리오 합격 | 15분 내 | 유지 (UX 페르소나 적용) | 수동 QA + 베타 사용자 5명 |
| **알림 끄기율** | (없음) | **신규: 첫 7일 ≤ 15%** (UX §3 우려) | 시스템 권한 변경 이벤트 |
| **로그인 후 첫 휴무 신청 도달률** | (없음) | **신규: ≥ 60%** (직원 앱 onboarding 완수율) | 깔때기 분석 |

---

## 9. Round 2 발사 — 다른 팀에 던지는 질문

> ⚠️ SendMessage 도구가 제 환경에 노출되어 있지 않으므로, 본 문서를 통해 질문을 명문화하고 team-lead에 전달 위임. team-lead가 SendMessage 대행 또는 도구 노출 시 즉시 호출.

### 🔵 to: **backend** (필수, 1순위 — 기술 제약 vs 기획 의도 충돌)

> **질문 B-1 (MVP 차단)**: NoOp FCM 어댑터를 v1.2 출시일까지 **Firebase Admin SDK 실연동**으로 전환하는 작업 일정을 회의에서 확정해줄 수 있는가? 만약 일정 확약이 불가능하다면, PM은 비즈니스 모델 §7을 **"팀 티어 베타 가격 무료 또는 50% 할인"으로 변경**하여 매출 KPI를 v1.3로 이월할 책임을 지겠다. **확약 가능 / 불가능 중 명확히 답변 요청.**

> **질문 B-2 (BFF)**: `GET /me/home-summary` BFF 엔드포인트를 v1.2 MVP에 포함하는 비용을 백엔드 인력 일수로 견적 가능한가? 5일 이내라면 PM은 MUST로 확정. 그 이상이면 frontend client-side aggregation으로 우회한다. **5일 / 그 이상 중 답변 요청.**

> **질문 B-3 (Phase 999)**: Phase 999 (관리자 API JWT 인가 + DEV 백도어 제거)를 v1.2 출시 차단 조건으로 격상하는 데 동의하는가? 동의 시 일정과 작업 범위 확인 요청.

### 🟢 to: **frontend** (필수)

> **질문 F-1 (인터랙션 매핑)**: PM §2.2 반박 2 — 칩 short-press = "어디로 옮길까요?" 모드 / long-press = 드래그 시작으로 매핑을 **반대로** 변경하는 데 동의하는가? UX §1 시나리오 A 4번 한 손 fallback 핵심.

> **질문 F-2 (TTI 책임)**: client-side aggregation + MMKV stale-while-revalidate로 **Cold 1.5s / Warm 0.8s 95p** 충족이 가능한가? 가능하면 backend BFF는 backlog로 두고 frontend가 KPI 책임. 불가능하면 backend BFF v1.2 MUST.

### 🟣 to: **design** (필수)

> **질문 D-1 (대비)**: 달력 오늘 날짜 배경을 `#0EA5E9`(2.9:1)에서 `#0369A1`(8.75:1)로 변경하는 데 동의하는가? PM은 v1.2 MVP 차단 조건으로 보고 있다.

> **질문 D-2 (Dark Mode 강등)**: PM은 다크모드를 v1.3로 이월하려는데 design은 동의하는가? UX §6.T3 점장 의견("매장 형광등에선 라이트가 낫다")이 강한 근거.

### 🟡 to: **ux** (필수)

> **질문 U-1 (TTI 합의)**: PM이 KPI를 **Cold 1.5s / Warm 0.8s 95p** 두 단으로 분리하는 안에 동의하는가? UX §6.T1의 0.8s는 warm start로 충족된다.

> **질문 U-2 (매장 모드 강등)**: 매장 모드 토글 자체는 v1.3로 이월하되, **(a) hit area minHeight 48 (b) 영업시간 silent push (c) primary-ink 자동 적용** 3개 요소만 v1.2에 흡수하는 타협안에 동의하는가?

---

## 10. PM Round 2 입장 정리 (한 줄)

> "**Round 1의 MUST 6개를 MUST 10개로 확장하고, 페르소나는 UX 정의로 교체하며, KPI는 Cold/Warm 두 단으로 분리한다. backend FCM·BFF·Phase 999 3건 일정 확약, frontend 인터랙션 매핑 반대 변경, design 대비 차단 조건 수용, UX 매장 모드 강등 — 4팀 모두 회신해야 Round 3 합격선이 결정된다.**"
