# Backend Round 1 — 백엔드 입장 정리

> 작성자: backend agent | 회의: frontend-kickoff-meeting | 날짜: 2026-04-29

---

## 0. 요약

v1.1 백엔드는 **핵심 기능 API 전체 완성** 상태. FCM 발송 인프라(NoOp)·관리자 API 인가·딥링크 파일 서빙만 v1.2 항목으로 남아있다. 본 문서는 React Native 모바일 앱 연동 관점에서 **4대 핵심 토픽 각각에 대한 백엔드 입장**을 정리한다.

---

## 1. 실제 구현된 API 엔드포인트 목록

> 서버 포트: **9090** | 공통 응답 래퍼: `CommonResponse<T> { success: bool, result: T[] }`

### 1.1 인증 (Auth)

```
POST /auth/kakao/callback    # 카카오 OAuth code → JWT 발급
POST /auth/refresh           # Refresh Token → 새 Token 쌍
POST /auth/logout            # Refresh Token 무효화
```

#### Request/Response 상세

```json
// POST /auth/kakao/callback
// Request
{
  "code": "kakao_auth_code",
  "redirectUri": "http://...",
  "inviteToken": "optional_invite_token"
}

// Response (CommonResponse)
{
  "success": true,
  "result": [{
    "accessToken": "eyJ...",
    "refreshToken": "eyJ...",
    "expiresIn": 1800
  }]
}
```

### 1.2 나의 정보 (Me)

```
GET    /me/onboarding-status            # 온보딩 상태 (STORE_MISSING / INVITE_PENDING / STORE_CONFLICT / COMPLETE)
POST   /me/confirm-store-switch         # 매장 전환 확인/취소
GET    /me/schedules?year=&month=       # 내 월별 스케줄 조회
PATCH  /me/fcm-token                    # FCM 푸시 토큰 등록 ✅ (API 존재, NoOp 어댑터)
GET    /me/swap-requests                # 근무 교환 이력 (paging)
```

#### OnboardingStatusResponse

```json
{
  "success": true,
  "result": [{
    "role": "EMPLOYEE",
    "status": "STORE_CONFLICT",
    "storeId": 42,
    "currentStore": { "id": 42, "name": "현재 매장" },
    "pendingStore":  { "id": 99, "name": "초대된 새 매장" }
  }]
}
```

#### MyScheduleResponse

```json
{
  "success": true,
  "result": [{
    "year": 2026,
    "month": 5,
    "entries": [
      { "entryId": 101, "date": "2026-05-01", "status": "ON" },
      { "entryId": 102, "date": "2026-05-02", "status": "OFF" }
    ]
  }]
}
```

#### FCM 토큰 등록

```json
// PATCH /me/fcm-token
// Request
{ "fcmToken": "firebase_registration_token_string" }
// Response
{ "success": true, "result": [] }
```

### 1.3 직원 (Employee)

```
POST   /stores/{storeId}/employees                        # 직원 등록 (201)
GET    /stores/{storeId}/employees                        # 직원 목록
PATCH  /employees/{employeeId}                            # 직원 수정
DELETE /employees/{employeeId}                            # 직원 삭제
PATCH  /stores/{storeId}/employees/day-off-per-month      # dayOffPerMonth 일괄 수정
POST   /employees/{id}/invite                             # 초대 링크 생성
POST   /employees/{id}/day-off-requests                   # 휴무 신청
```

#### EmployeeResponse

```json
{
  "id": 1,
  "storeId": 42,
  "name": "김민준",
  "dayOffPerMonth": 8,
  "surplusDayOffOption": "SPREAD",
  "profileAvatar": "AVATAR_03"
}
```

### 1.4 스케줄 (Schedule)

```
POST  /stores/{storeId}/schedules/generate                 # 스케줄 자동 생성
GET   /stores/{storeId}/schedules?year=&month=             # 월별 스케줄 조회
GET   /schedules/{scheduleId}/entries                      # 엔트리 목록
GET   /schedules/{scheduleId}/export/png                   # PNG (binary)
GET   /schedules/{scheduleId}/export/xlsx                  # Excel (binary)
GET   /schedules/{scheduleId}/export/ics                   # iCal (binary)
GET   /stores/{storeId}/schedules/annual?year=             # 연간 근무 통계
PATCH /stores/{storeId}/schedules/{year}/{month}/entries   # 수동 Bulk 수정
```

#### ScheduleDetailResponse

```json
{
  "scheduleId": 10,
  "year": 2026, "month": 5,
  "minStaffPerDay": 2,
  "violated": false,
  "violations": [],
  "entries": {
    "김민준": [
      { "entryId": 101, "date": "2026-05-01", "status": "ON" }
    ],
    "이수아": [
      { "entryId": 201, "date": "2026-05-01", "status": "OFF" }
    ]
  },
  "closedDays": ["2026-05-05"]
}
```

### 1.5 매장 (Store)

```
POST   /stores              # 매장 등록 (201)
GET    /stores/{storeId}    # 매장 조회
PATCH  /stores/{storeId}    # 매장 수정
DELETE /stores/{storeId}    # 매장 삭제 (연쇄 삭제 포함)
```

---

## 2. 4대 핵심 토픽 — 백엔드 입장

### 2.1 모바일 최적화 API (앱 초기 로딩 데이터 최소화)

**현재 상태:** 모바일 전용 BFF/aggregation 엔드포인트 **없음**. 앱 홈화면 초기화 시 최소 3건의 병렬 API 호출이 필요하다.

| 화면 초기화 시 필요한 호출 | 엔드포인트 |
|---|---|
| 온보딩 분기 판단 | `GET /me/onboarding-status` |
| 내 이번달 스케줄 | `GET /me/schedules?year=&month=` |
| 매장 정보 (관리자) | `GET /stores/{storeId}` + `GET /stores/{storeId}/employees` |

**백엔드 제안 — v1.2 BFF 엔드포인트:**

```http
GET /me/home-summary
```

```json
// 제안 Response
{
  "success": true,
  "result": [{
    "onboardingStatus": "COMPLETE",
    "role": "EMPLOYEE",
    "currentStore": { "id": 42, "name": "워키 카페" },
    "thisMonth": {
      "year": 2026, "month": 5,
      "workDays": 22, "offDays": 9,
      "entries": [ ... ]
    },
    "upcomingOff": ["2026-05-03", "2026-05-10"]
  }]
}
```

> **현재 v1.1 범위 外.** RN 앱은 `Promise.all([api1, api2, api3])` 병렬 호출로 우선 구현하고, v1.2에서 BFF 도입 여부를 결정할 것을 권장한다.

---

### 2.2 네이티브 연동 — FCM 푸시 알림

**현재 구현 상태:**

| 항목 | 상태 |
|---|---|
| FCM 토큰 등록 API (`PATCH /me/fcm-token`) | ✅ 구현 완료 |
| `SendNotificationPort` 인터페이스 | ✅ 정의 완료 |
| 알림 발송 어댑터 | ❌ `NoOpNotificationAdapter` (로그만 출력) |
| 알림 스케줄러 로직 (3종) | ✅ 완성 (쉬기 전날 20:00, 관리자 07:00, 미확인 독촉) |

**앱 → 서버 FCM 토큰 등록 흐름:**

```
RN 앱 최초 실행
  → FirebaseMessaging.getToken() 호출
  → 로그인 완료 후 PATCH /me/fcm-token { "fcmToken": "..." }
  → 서버: members 테이블 fcm_token 컬럼 저장

토큰 갱신 이벤트 (onTokenRefresh)
  → PATCH /me/fcm-token 재호출
```

**푸시 페이로드 스펙 (v1.2 연동 시 예상 구조):**

```json
// 쉬기 전날 알림 (직원용)
{
  "notification": { "title": "내일은 휴무예요 🌙", "body": "5월 10일(일)이 휴무예요." },
  "data": { "type": "DAY_OFF_REMINDER", "date": "2026-05-10", "storeId": "42" }
}

// 당일 근무 현황 (관리자용)
{
  "notification": { "title": "오늘의 근무 현황", "body": "근무: 김민준, 이수아 / 휴무: 박지호" },
  "data": { "type": "DAILY_WORK_SUMMARY", "date": "2026-05-01", "storeId": "42" }
}

// 근무 교환 요청 (상대 직원용)
{
  "notification": { "title": "근무 교환 요청", "body": "김민준님이 5/3↔5/10 교환을 요청했어요." },
  "data": { "type": "SWAP_REQUEST", "swapRequestId": "123" }
}
```

---

### 2.3 디자인 이식 — 바텀시트 API 연동 타이밍

바텀시트 등 컴포넌트 자체는 백엔드와 무관하나, **UX 흐름별 API 호출 타이밍**을 정리한다:

| UX 액션 | 필요 API | 응답 속도 기대 |
|---|---|---|
| 초대 바텀시트 열기 | `POST /employees/{id}/invite` | < 500ms |
| 휴무 신청 바텀시트 제출 | `POST /employees/{id}/day-off-requests` | < 500ms |
| 매장 전환 확인 바텀시트 | `POST /me/confirm-store-switch` | < 500ms |
| 스케줄 생성 확정 버튼 | `POST /stores/{storeId}/schedules/generate` | **1~5초 가능** (알고리즘 실행) |

> **스케줄 생성 API 응답 지연 주의:** 직원 수 × 일수 비례. 앱 측에서 로딩 스피너와 타임아웃 처리 필수.

---

### 2.4 사용자 환경 — 한 손 조작 (최기준 페르소나 검증)

관리자가 모바일에서 스케줄을 생성하는 최소 API 호출 경로:

```
1회: POST /stores/{storeId}/schedules/generate
     Body: { year, month, minStaffPerDay, confirmedDayOffs: [...] }
     → 단 1번의 API 호출로 스케줄 생성

1회: GET  /stores/{storeId}/schedules?year=&month=
     → 결과 확인 (캐시로 대체 가능)
```

최소 2번의 API 호출로 "조건 입력 → 스케줄 완성" 플로우 완결 가능. 한 손 조작에 무리 없는 수준.

---

## 3. JWT / Refresh Token 흐름 (RN 보안 고려)

### 현재 스펙

| 항목 | 값 |
|---|---|
| Access Token 유효기간 | 30분 (`expiresIn: 1800`) |
| Refresh Token 유효기간 | 7일 |
| Rotation | Refresh 시 새 Refresh Token 발급 + 기존 무효화 |
| 서버 저장 위치 | MySQL `refresh_tokens` 테이블 |

### RN 보안 권고

```
현재 AsyncStorage 사용 시 위험:
  → 루팅/탈옥 기기에서 평문 탈취 가능

권장:
  iOS:     expo-secure-store → Keychain Services
  Android: expo-secure-store → Android Keystore
```

### 토큰 재발급 흐름

```
API 호출 → 401 Unauthorized
  ↓
POST /auth/refresh { "refreshToken": "..." }
  ↓ 성공: 새 토큰 저장 → 원래 요청 재시도
  ↓ 실패(만료/무효): 카카오 OAuth 재인증 시작
```

---

## 4. 페이로드 경량화 전략

### 공통 응답 래퍼 주의사항

```json
// CommonResponse 구조
{ "success": true, "result": [ <데이터> ] }

// 단건 조회도 항상 배열 → RN에서 result[0] 으로 꺼내야 함
const employee = response.data.result[0];
```

### 경량화 전략 현황

| 전략 | 현재 지원 | 비고 |
|---|---|---|
| gzip 압축 | ✅ (Spring Boot 기본) | 자동 적용 |
| Sparse fieldset (`?fields=`) | ❌ | v1.2 검토 |
| ETag / If-None-Match | ❌ | 스케줄 캐싱에 효과적, v1.2 검토 |
| GraphQL | ❌ | 도입 비용 대비 효과 재검토 필요 |

**실용적 권장사항:**
- `ScheduleDetailResponse.entries` 는 직원 수 × 30일 크기 → lazy loading 분리 (`GET /schedules/{id}/entries`)
- 앱에서 월 단위 로컬 캐시 구현으로 리렌더 최소화

---

## 5. 딥링크 — 백엔드 서빙 필요 파일 (v1.2)

```
https://workey.app/.well-known/apple-app-site-association   # iOS Universal Links
https://workey.app/.well-known/assetlinks.json              # Android App Links
```

현재 미서빙. 앱 스토어 출시 전 v1.2에서 처리. 비즈니스 로직과 무관한 정적 파일 서빙.

---

## 6. v1.2 미결 항목 요약

| 항목 | 현재 상태 | 필요 작업 |
|---|---|---|
| FCM 실제 발송 | NoOp 어댑터 | Firebase Admin SDK 연동 |
| 관리자 API 인증 | `anyRequest().permitAll()` | JWT 인증 적용 (Phase 999) |
| DEV 백도어 | `/dev/**` 존재 | prd 배포 전 삭제 필수 |
| 딥링크 정적 파일 | 미서빙 | AASA / assetlinks.json |
| BFF 홈 요약 | 없음 | 검토 필요 (v1.2) |
| 프로필 아바타 UI | AVATAR_01~30 enum 완성 | SVG 번들·selector UI (프론트) |
