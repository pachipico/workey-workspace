# Backend Round 2 — 타 팀 Round 1 리뷰 및 반박

> 작성자: backend agent | 회의: frontend-kickoff-meeting | 날짜: 2026-04-29  
> 참조: pm-round1.md / frontend-round1.md / design-round1.md / ux-round1.md

---

## 0. 요약

4개 팀의 Round 1을 백엔드 구현 현실 기반으로 검토한다. 전반적으로 **요청 방향은 타당**하나, 실제 코드와 다른 API 스펙 가정, 과도한 서버 의존 설계, v1.2 일정 무시 요청이 혼재한다. 수용·부분 수용·거부로 분류해 정리한다.

---

## 1. PM Round 1 리뷰

### 1-1. ✅ 수용 — `/me/onboarding-status` 단일 진입점 (이미 완료)

> PM: "단일 진입 엔드포인트(`/me/onboarding-status`)로 케이스 1~5 분기 (백엔드 Phase 26 완료) → 프론트는 부가 호출 없이 첫 화면 결정"

**백엔드 확인:** Phase 26에서 `GET /me/onboarding-status` 완전 구현됨. PM 요구가 이미 충족된 상태다.

```json
// GET /me/onboarding-status → 5케이스 분기 가능
{
  "role": "ADMIN | EMPLOYEE",
  "status": "STORE_MISSING | INVITE_PENDING | STORE_CONFLICT | COMPLETE",
  "storeId": 42,
  "currentStore": { ... },
  "pendingStore": { ... }
}
```

---

### 1-2. 🟡 부분 수용 — `/me/schedules`에 이번달+다음달 합산 응답

> PM: "이번 달 + 다음 달 데이터를 한 번에 묶어달라 — 직원이 휴무 신청할 때 다음달이 항상 따라옴"

**백엔드 분석:**
- 현재 `GET /me/schedules?year=&month=` 는 단건(1개월) 응답 구조.
- 두 달 합산은 **쿼리 파라미터 확장** 방식으로 수용 가능:

```http
GET /me/schedules?year=2026&month=5&includeNext=true
```

```json
{
  "success": true,
  "result": [{
    "current": { "year": 2026, "month": 5, "entries": [...] },
    "next":    { "year": 2026, "month": 6, "entries": [...] }   // includeNext=true 시
  }]
}
```

**조건:** `month=6`이 이미 스케줄이 생성된 경우만 entries가 있음. 미생성 월은 `next: null`로 응답. v1.2 검토 항목으로 등록.

---

### 1-3. ❌ 거부 — PNG 이미지 CDN 절대 경로 응답

> PM: "PNG 이미지 URL은 CDN 절대 경로로 응답 (RN `<Image>`에서 바로 prefetch 가능)"

**백엔드 현실:**

현재 PNG는 **바이너리 스트리밍 응답**이다:

```java
// GET /schedules/{scheduleId}/export/png → byte[] 직접 반환
return ResponseEntity.ok()
    .contentType(MediaType.IMAGE_PNG)
    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; ...")
    .body(imageBytes);
```

CDN 절대 경로 응답을 위해선 **S3/CDN 인프라** 도입이 선행되어야 한다. 현재 문서에는 "S3 SDK 미사용 — 로컬 저장, 포트 인터페이스로 추후 교체"로 명시되어 있다.

**결론:** v1.2 MVS 범위가 아님. RN은 `GET /schedules/{scheduleId}/export/png`를 직접 호출하거나 `Blob` → `FileSystem`으로 저장하는 방식으로 대응할 것.

---

### 1-4. 🟡 부분 수용 — 푸시 토큰 idempotency key

> PM: "푸시 토큰 등록 API의 idempotency key 명시 (앱 재설치/재로그인 시 중복 등록 방지)"

**백엔드 분석:**

현재 `PATCH /me/fcm-token { fcmToken }` 은 PATCH 의미상 **멱등성을 보장**한다. 같은 memberId + 같은 fcmToken 재등록 시 `members.fcm_token` 컬럼을 덮어쓸 뿐이므로 실질적으로 중복이 없다.

단, 앱 재설치 시 새 토큰 발급 → 기존 토큰 무효 문제는 **FCM이 자체 처리**하므로 별도 idempotency key 불필요하다.

**결론:** 현재 PATCH 구조로 충분. 다만 FCM SDK 연동(v1.2) 시 `InvalidRegistrationToken` 오류 핸들링 코드 추가 필요.

---

### 1-5. ✅ 수용 — 시간대 Asia/Seoul 고정

> PM: "시간대(Asia/Seoul) 고정 정책을 응답 헤더 또는 contract에 명문화"

**백엔드 확인:** 현재 스케줄 date 필드는 모두 `yyyy-MM-dd` ISO 형식 문자열로 반환된다. 서버는 Asia/Seoul 기준으로 동작한다. 이를 API contract 문서(springdoc-openapi)에 명시하고, 응답 헤더에 `X-Timezone: Asia/Seoul`을 추가하는 것을 수용한다.

---

### 1-6. ❌ 거부 — cursor 기반 페이지네이션

> PM: "스케줄 이력 / 근무 교환 이력은 cursor 기반. 첫 페이지 ≤ 20건"

**백엔드 현실:**

현재 `/me/swap-requests`는 `PageResponse<T> { content, page, size, totalElements, totalPages }` offset 방식으로 구현됨. cursor 방식으로 재구현은 v1.2 일정에 영향을 준다.

```java
// 현재 구현: page/size offset
@RequestParam(defaultValue = "0") int page,
@RequestParam(defaultValue = "20") int size
```

**결론:** 교환 이력은 실시간성보다 정확성이 중요하고 데이터 볼륨이 크지 않으므로 **offset 방식으로 v1.2 출시**한다. cursor 방식은 v2.0에서 고려.

---

## 2. Frontend Round 1 리뷰

### 2-1. ❌ 스펙 불일치 발견 — FCM 토큰 등록 API 필드명

> Frontend: `api.registerPushToken({ token: fcmToken, platform: Platform.OS })`

**백엔드 실제 스펙:**

```java
// UpdateFcmTokenRequest.java
public record UpdateFcmTokenRequest(
    @NotBlank String fcmToken   // ← "fcmToken" 필드명
) {}

// MeController.java
@PatchMapping("/me/fcm-token")  // ← POST가 아닌 PATCH
```

**불일치 2가지:**
1. **엔드포인트**: Frontend는 `POST /me/push-token` 가정 → 실제는 `PATCH /me/fcm-token`
2. **필드명**: Frontend는 `{ token, platform }` → 실제는 `{ fcmToken }` 단일 필드

또한 `platform` 필드는 **현재 스펙에 없음**. FCM 토큰 자체가 플랫폼 구분 가능(FCM은 iOS APNs도 통합 처리)하므로 별도 platform 필드가 필요한지 검토 필요.

**⚠ 즉시 조율 필요.** 아래 frontend-agent 질문 섹션에서 확인 예정.

---

### 2-2. ✅ 수용 — 대시보드 합산 API 요청

> Frontend: "대시보드 초기 진입 시 세 API를 하나로 묶은 `GET /stores/{id}/dashboard-summary` (또는 `?include=` 쿼리 파라미터) 방식 검토 요청"

**백엔드 제안:**

Round 1에서 `GET /me/home-summary`를 이미 제안했다. Frontend 요청과 방향이 일치한다. v1.2에서 아래 구조로 확정 가능:

```http
GET /me/home-summary
```

```json
{
  "success": true,
  "result": [{
    "role": "ADMIN",
    "onboardingStatus": "COMPLETE",
    "currentStore": {
      "id": 42, "name": "워키 카페"
    },
    "employees": [...],          // ADMIN 전용
    "thisMonthSchedule": {
      "year": 2026, "month": 5,
      "violated": false,
      "scheduleId": 10
    },
    "pendingDayOffCount": 3,     // ADMIN: 미처리 휴무 신청 수
    "upcomingOff": ["2026-05-03"] // EMPLOYEE: 나의 다음 휴무
  }]
}
```

**일정:** v1.2 백엔드 작업 항목으로 공식 등록. v1.1 API `Promise.all` 병렬 호출로 임시 대응.

---

### 2-3. ✅ 확인 — TanStack Query 캐시 전략

> Frontend: `staleTime: 5분 / gcTime: 10분 + 뮤테이션 후 즉시 무효화`

**백엔드 관점:** 합리적인 전략. 단, 스케줄 `generate` 성공 후 반드시 `['schedule', storeId, year, month]` 캐시를 즉시 무효화해야 한다. 서버 응답에 `scheduleId`가 포함되므로 이를 즉시 사용 가능.

---

### 2-4. ✅ 수용 — MMKV 암호화 토큰 저장

> Frontend: `react-native-mmkv + AES-256 encryptionKey`로 토큰 저장

**백엔드 관점:** AsyncStorage 평문 저장보다 훨씬 안전하다. Refresh Token 7일 Rotation 정책과 잘 맞는다.

**추가 권고:** `encryptionKey`를 환경변수 하드코딩보다 `expo-secure-store` 또는 iOS Keychain에서 동적으로 가져오는 방식 권장.

---

### 2-5. 🟡 부분 수용 — 오프라인 큐 idempotency

> Frontend: "뮤테이션 실패 시 MMKV 큐에 적재 후 네트워크 복구 시 재시도"

**백엔드 관점:**

휴무 신청(`POST /employees/{id}/day-off-requests`)의 **이중 제출 위험**:

```
오프라인 큐 적재 → 네트워크 복구 → 재시도 → 이미 서버에 반영된 경우 중복 신청
```

현재 백엔드에 idempotency key 처리 로직이 없다. 해결 방법:

```http
POST /employees/{id}/day-off-requests
X-Idempotency-Key: {uuid}   // RN에서 클라이언트 생성 UUID 전송
```

서버에서 동일 key 재수신 시 기존 응답을 그대로 반환. v1.2 항목으로 검토.

---

## 3. Design Round 1 리뷰

### 3-1. ✅ 수용 — 디자인 토큰 RN 이식 (백엔드 무관)

컴포넌트 규격(BottomSheet, FAB, Toast, Modal)과 색상 토큰은 백엔드 연관성이 낮다. Frontend와 Design의 합의 사항이다.

---

### 3-2. 🟡 주목 — 달력 오늘 날짜 대비 부족 이슈

> Design: `#0EA5E9` + 흰 텍스트: 2.9:1 ⚠ → 흰 텍스트 볼드 처리 or `#0369A1` 배경 전환 고려

백엔드 응답의 `status: "ON"/"OFF"` 데이터와 직결되는 렌더링 이슈는 아니나, **공휴일 컬러 헤더**(PNG 출력)는 백엔드에서 계산해 제공하는 데이터다. 대비 기준을 맞추려면 PNG 렌더링 코드도 함께 수정이 필요할 수 있음.

---

### 3-3. ❌ 거부 — 다크모드 서버 응답 변경 필요성

다크모드는 **클라이언트 렌더링 문제**이며, 서버 응답 구조와 무관하다. 백엔드 변경 불필요.

---

## 4. UX Round 1 리뷰

### 4-1. ✅ 수용 — 휴무 수집 뷰 충돌 검증 분리 모델

> UX: "휴무 수집 뷰 충돌 검증은 클라이언트 단에서 즉시 계산하고, 서버는 최종 확정 시점에만 검증 (드래그 도중 매번 API 호출 금지)"

**백엔드 완전 동의.** 현재도 `POST /stores/{storeId}/schedules/generate` 요청 시에만 서버 검증(사전 검증 3가지 + violation 기록)이 이루어진다. 드래그 중간 실시간 API 호출 설계는 **애초에 없다**. 충돌 로직(minStaffPerDay 미달 체크)은 클라이언트에서 구현해야 한다.

**클라이언트 충돌 계산에 필요한 데이터:**
- `confirmedDayOffs`: 직원별 OFF 날짜 목록
- `minStaffPerDay`: 스케줄 생성 요청 시 프론트가 이미 알고 있음
- `totalEmployees`: `GET /stores/{id}/employees` 응답의 직원 수

---

### 4-2. 🟡 부분 수용 — 대시보드 bootstrap aggregation endpoint

> UX: "`/me/dashboard?storeId=...` — 위 5건을 1콜에 합쳐 응답"

PM·Frontend·UX 3팀 모두 동일한 요청을 했다. **`GET /me/home-summary`로 통일**해 v1.2에서 구현한다. 단, UX가 요구하는 "5건 전체 합산"은 응답 크기가 커질 수 있으므로 **필수 필드 + lazy 필드** 구분이 필요하다:

```json
// /me/home-summary: 즉시 렌더에 필요한 최소 필드만
{
  "role": "ADMIN",
  "storeName": "워키 카페",
  "storeId": 42,
  "onboardingStatus": "COMPLETE",
  "thisMonthScheduleId": 10,
  "violated": false,
  "employeeCount": 6,
  "pendingDayOffCount": 3,
  "upcomingHolidays": ["2026-05-05"]
}
// 직원 목록 entries 같은 대용량 데이터는 별도 lazy 호출
```

---

### 4-3. ✅ 수용 원칙 / 구현은 v1.2 — 알림 묶음(daily digest) + 영업시간 silent push

> UX: "daily digest 모드 / 영업시간 무음 / 카테고리별 on/off"

**백엔드 구현 현황:**

알림 스케줄러는 완성됐으나 FCM 인프라가 NoOp 상태다. daily digest나 silent push는 **FCM 연동(v1.2) 이후**에 구현 가능하다.

**백엔드 설계 필요 사항 (v1.2 이후):**

```
1. members 테이블에 notification_preferences 컬럼 추가
   {
     "dailyDigest": true,
     "silentStart": "11:00",
     "silentEnd": "14:00",
     "categories": { "dayOff": true, "swap": false }
   }

2. PATCH /me/notification-preferences 엔드포인트 추가
3. 스케줄러에서 silent 시간대 체크 로직 추가
```

v1.2 기간에 FCM 연동과 함께 설계. v1.1에서는 모든 알림이 NoOp이므로 영향 없음.

---

### 4-4. 🟡 논의 필요 — PNG 멀티 이미지 (1주씩 4장 + 전체 1장)

> UX: "PNG 출력 시 '1주씩 4장 + 전체 1장' 멀티 이미지 옵션"

**백엔드 현실:**

현재 `GET /schedules/{scheduleId}/export/png`는 전체 월 단일 이미지를 반환한다. 1주 단위 슬라이스는 렌더링 로직 추가가 필요하다.

```http
// 제안 확장 스펙 (v1.2 검토)
GET /schedules/{scheduleId}/export/png?mode=weekly   // 4개 파일 zip 또는 multipart
GET /schedules/{scheduleId}/export/png?mode=full     // 현재 방식 (기본값)
```

ZIP 응답 또는 multipart 방식 중 프론트와 협의 필요. 현재 v1.1 우선순위는 아니다.

---

## 5. UX PP-1~PP-7 — 백엔드 영향 항목 응답

UX Round 1의 7개 페인 포인트 중 백엔드 변경이 필요하거나 관련 있는 항목만 정리한다.

| PP # | 내용 요약 | 백엔드 영향 | 대응 |
|---|---|---|---|
| PP-1 | 드래그 오드롭 → 손가락에 가려 어디 떨어졌는지 모름 | ❌ 없음 | 순수 클라이언트 UX 문제. 드롭 후 서버 저장은 `confirmedDayOffs` 확정 시 1회만 발생 |
| PP-2 | 충돌 빨간 표시 이유가 화면에서 안 보임 | ❌ 없음 | 서버는 `violations[]` 배열로 이유를 내려줌. 클라이언트 UI 표시 방식 문제 |
| PP-3 | "+ 수동 추가"가 유일 입력임을 모름 | ❌ 없음 | 코치마크는 클라이언트 로직. 다만 `GET /me/onboarding-status`의 `role`·`status` 조합으로 티어 분기 가능 |
| PP-4 | PNG가 카톡에서 잘림 | 🟡 백엔드 작업 필요 | `GET /schedules/{id}/export/png?mode=weekly` 주간 슬라이스 옵션 추가 (v1.2 검토) |
| PP-5 | 푸시 알림 피로도 | 🟡 백엔드 작업 필요 | FCM 연동 시 `PATCH /me/notification-preferences` + members 테이블 컬럼 추가 필요 (v1.2+) |
| PP-6 | 딥링크 진입 후 카카오 로그인 바로 뜸 | 🟡 관련 있음 | 초대 토큰 유효성 정보를 사전 조회하는 `GET /invite/{token}/preview` 추가 가능 — 환영 화면에서 매장명·점장 이름 표시용. v1.2 검토 |
| PP-7 | "균등 분산/연속 부여" 라벨이 점장 언어가 아님 | ❌ 없음 | `SurplusDayOffOption: SPREAD/CONSECUTIVE` enum은 백엔드 내부 값. 프론트에서 표시 라벨만 변경하면 됨 |

### PP-6 상세 — 딥링크 토큰 미리보기 API 제안

```http
GET /invite/{inviteToken}/preview
// 인증 불필요 (public endpoint)
```

```json
{
  "success": true,
  "result": [{
    "storeName": "워키 카페",
    "ownerName": "최기준",
    "employeeName": "김민준",   // 미리 등록된 직원 이름
    "expiresAt": "2026-04-30T23:59:59"
  }]
}
```

앱 미설치 → 스토어 → 첫 실행 시 이 API로 환영 화면 데이터를 채운 뒤 카카오 OAuth 트리거. **카카오 로그인 전에 "어느 매장에 초대됐는지"를 사용자에게 먼저 보여주는 흐름** 지원 가능.

---

## 6. API 부하·캐싱·트랜잭션 정합성 관점

### 6-1. API 부하 — 스케줄 생성 엔드포인트 병목

`POST /stores/{storeId}/schedules/generate`는 알고리즘 실행 특성상 **동기 HTTP 응답**으로 1~5초가 소요될 수 있다.

| 직원 수 | 예상 응답 시간 |
|---|---|
| 3명 | ~300ms |
| 6명 | ~800ms |
| 10명 | ~2,000ms |
| 15명 | ~4,000ms+ |

**백엔드 권고:**
- RN 클라이언트는 타임아웃을 **10초**로 설정 (기본 5초 부족)
- 생성 중 로딩 스피너 + "생성 중입니다 (보통 1~5초)" 안내 문구 필수
- v1.2에서 비동기 처리(Job Queue) 검토 가능하나 현재는 동기 방식 유지

### 6-2. 캐싱 전략 — 백엔드 HTTP 캐시 헤더

현재 백엔드 응답에 `Cache-Control` 헤더가 없다. 모바일 네트워크 최적화를 위해 v1.2에서 추가 예정:

| 엔드포인트 | Cache-Control 제안 |
|---|---|
| `GET /stores/{id}/employees` | `max-age=300, private` (5분) |
| `GET /stores/{id}/schedules?year&month` | `max-age=60, private` (1분) |
| `GET /schedules/{id}/entries` | `max-age=300, private` |
| `GET /stores/{id}/schedules/annual` | `max-age=3600, private` (1시간) |
| `GET /me/onboarding-status` | `no-cache` (항상 최신) |

### 6-3. 트랜잭션 정합성 — 핵심 위험 지점

**위험 1: 휴무 신청 + 스케줄 생성 동시 발생**

```
직원 A: POST /employees/{id}/day-off-requests (APPROVED 처리)
관리자: POST /stores/{id}/schedules/generate (confirmedDayOffs: null)

→ confirmedDayOffs=null 이면 DB APPROVED 기준으로 생성
→ 직원 A 신청이 반영됨 (정상 동작)

위험: 생성 중(트랜잭션 열린 상태)에 또 신청 승인이 오면?
→ 현재: 스케줄 생성이 단일 트랜잭션이므로 타이밍 경쟁 발생 가능
→ 권고: 생성 중 "스케줄 생성 중에는 휴무 신청 불가" 상태를 서버에서 422로 반환 검토
```

**위험 2: Bulk 수정 중 근무 교환 동시 발생**

```
관리자: PATCH /stores/{id}/schedules/{year}/{month}/entries
직원:   POST /swap-requests (승인 대기 중 항목 수정)

→ 근무 교환 승인 시 schedule_entries 업데이트
→ Bulk PATCH와 동시 실행 시 last-write-wins 충돌 가능
→ 현재: 낙관적 잠금 없음. v1.2에서 schedule_entries에 version 컬럼 추가 검토
```

**위험 3: 오프라인 큐 휴무 신청 이중 제출**

이미 §2-5에서 언급. `X-Idempotency-Key` 헤더 도입으로 해결 가능.

---

## 7. 백엔드 관점 종합 반박 요약

### 수용/거부 매트릭스

| 요청 팀 | 요청 사항 | 판정 | v1.2 일정 |
|---|---|---|---|
| PM | 온보딩 단일 진입점 | ✅ 이미 완료 | — |
| PM | /me/schedules 이달+다음달 합산 | 🟡 수용 (incl 파라미터 방식) | v1.2 검토 |
| PM | PNG CDN 경로 | ❌ 거부 (인프라 선행 필요) | v2.0+ |
| PM | cursor 페이지네이션 | ❌ 거부 (offset으로 v1.2 출시) | v2.0 |
| PM | 시간대 명문화 | ✅ 수용 | v1.2 헤더 추가 |
| Frontend | FCM 토큰 스펙 (`{ token, platform }`) | ❌ 스펙 불일치 — 즉시 조율 필요 | — |
| Frontend | 대시보드 합산 API | ✅ 수용 (`/me/home-summary`) | v1.2 |
| Frontend | 오프라인 큐 idempotency | 🟡 수용 (X-Idempotency-Key) | v1.2 |
| UX | 충돌 검증 클라이언트화 | ✅ 원래 설계 동일 | — |
| UX | bootstrap aggregation | ✅ 수용 (home-summary 통일) | v1.2 |
| UX | daily digest / silent push | 🟡 원칙 수용 / FCM 연동 후 | v1.2 이후 |
| UX | PNG 주간 슬라이스 | 🟡 검토 필요 | v1.2 검토 |

---

## 8. frontend-agent에게 질문 — DTO 편의성 및 BFF 캐시 키

> ⚠ 아래 내용을 SendMessage로 frontend-agent에게 직접 전달한다.

---

**[backend → frontend] API 응답 DTO 구조 편의성 + BFF 캐시 키 설계 + FCM 스펙 조율**

Round 1 코드 검토 결과 조율이 필요한 항목 3건을 공유합니다.

---

**질문 1 (즉시 필요) — FCM 토큰 등록 API 스펙 불일치**

Round 1 코드:
```ts
await api.registerPushToken({ token: fcmToken, platform: Platform.OS });
```

실제 백엔드 스펙:
```
PATCH /me/fcm-token        ← POST /me/push-token 아님
Body: { "fcmToken": "..." } ← { token, platform } 아님
```

선택해주세요:
- **(A)** 프론트가 `PATCH /me/fcm-token { "fcmToken": "..." }` 에 맞춰 수정 (권장)
- **(B)** 백엔드가 `{ token, platform }` 수용 + `platform` 컬럼 추가

`platform` 필드 용도를 알려주시면 B 검토 가능합니다. FCM 토큰은 플랫폼 구분이 이미 내장돼 있어 불필요해 보입니다.

---

**질문 2 (핵심) — BFF aggregation 응답에서 TanStack Query 캐시 키를 어떻게 잡을 계획인지**

v1.2에서 `GET /me/home-summary`를 추가하면, 응답 안에 employees·schedule·onboardingStatus 등 **여러 도메인 데이터가 혼합**됩니다. 

TanStack Query로 이를 캐싱할 때 두 가지 전략이 충돌합니다:

```ts
// 전략 A: BFF 응답을 통째로 하나의 캐시 키에 저장
useQuery({ queryKey: ['home-summary'] })
// → 직원 목록 뮤테이션 후 home-summary 전체를 invalidate 해야 함
// → 스케줄만 변경됐는데 직원 목록도 다시 fetch 됨 (낭비)

// 전략 B: BFF 응답 수신 후 normalize해 개별 캐시 키에 분배
onSuccess: (data) => {
  queryClient.setQueryData(['employees', storeId], data.employees);
  queryClient.setQueryData(['schedule', storeId, year, month], data.thisMonthSchedule);
}
// → 각 도메인 뮤테이션이 정확한 키만 invalidate 가능
// → 구현 복잡도 증가
```

백엔드 관점에선 **전략 B(normalize + 개별 캐시 키 분배)** 를 권장합니다. 스케줄 생성 성공 시 `['schedule', storeId, year, month]`만 무효화하면 되기 때문입니다.

프론트팀의 실제 구현 계획을 알려주세요. BFF 응답 필드 구성을 그에 맞게 조정하겠습니다 (예: normalize에 용이하도록 각 도메인 필드를 명확히 분리).

---

**질문 3 — CommonResponse 래퍼 unwrap 처리 방식**

모든 응답이 `{ "success": true, "result": [<데이터>] }` 배열로 래핑됩니다. 단건도 `result[0]` 접근이 필요합니다.

- **(A)** Axios interceptor에서 자동 unwrap → `response.data` 가 바로 데이터
- **(B)** 각 API 함수에서 수동 `result[0]`
- **(C)** 백엔드 스펙 변경 요청 (단건은 객체, 복수는 배열로 분리)

(C) 원하시면 `CommonResponse` 구조 변경 검토 가능하나 기존 파싱 코드 전체 수정 필요합니다. 팀 선호를 알려주세요.

---

> 답변을 backend-round3.md 최종 스펙 확정에 반영합니다.
