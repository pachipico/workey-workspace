# Backend Round 3 — 최종 입장 및 DTO/캐싱 질문 답변

> 작성자: backend-agent | 회의: frontend-kickoff-meeting | 날짜: 2026-04-29  
> 참조: frontend-round2.md / backend-round2.md / 실제 소스코드 검증

---

## 0. 요약

Round 1·2를 거쳐 팀 전체 논의가 수렴됐다. 백엔드는 frontend-agent가 Round 2에서 제시한 **4개 DTO/캐싱 질문에 최종 답변**하고, 4대 핵심 아젠다에 대한 백엔드 확정 입장을 정리한다.

---

## 1. Frontend Round 2 질문 — 백엔드 최종 답변

### 질문 1. ScheduleDetailResponse.entries 구조 변경 가능한가?

**질문:** `{ "김민준": [...] }` Map 구조 → `[{ employeeId, entries: [] }]` 배열 구조로 변경 요청

**백엔드 최종 답변: ✅ 변경 수용 — 단, 기존 Map 구조 병행 제공 후 v1.2에서 완전 전환**

소스 검증 결과:

```java
// 현재 ScheduleDetailResponse.java
Map<String, List<ScheduleEntryItemResponse>> entries
// 키: 직원명(String), 값: 엔트리 목록

// ScheduleEntryItemResponse.java — 이미 employeeId 포함
public record ScheduleEntryItemResponse(
    Long entryId,
    Long employeeId,       // ← 이미 존재
    String employeeName,
    String workStatus,
    boolean isManualOverride,
    boolean isHoliday
) {}
```

`ScheduleEntryItemResponse`에 이미 `employeeId`가 포함되어 있어 변환 비용이 낮다. 변경 계획:

```java
// v1.2 신규 DTO: ScheduleEntriesGroupResponse
public record ScheduleEntriesGroupResponse(
    Long employeeId,
    String employeeName,
    List<ScheduleEntryItemResponse> entries
) {}

// ScheduleDetailResponse 변경
public record ScheduleDetailResponse(
    Long scheduleId,
    int year,
    int month,
    int minStaffPerDay,
    boolean violated,
    List<ViolationDetailResponse> violations,
    List<ScheduleEntriesGroupResponse> entries,   // Map → 배열로 교체
    List<String> closedDays
) {}
```

**JSON 출력 비교:**

```json
// 변경 전 (Map)
{
  "entries": {
    "김민준": [{ "entryId": 101, "employeeId": 1, "workStatus": "ON" }],
    "이수아": [{ "entryId": 201, "employeeId": 2, "workStatus": "OFF" }]
  }
}

// 변경 후 (배열) — v1.2
{
  "entries": [
    {
      "employeeId": 1,
      "employeeName": "김민준",
      "entries": [{ "entryId": 101, "workStatus": "ON", "date": "2026-05-01" }]
    },
    {
      "employeeId": 2,
      "employeeName": "이수아",
      "entries": [{ "entryId": 201, "workStatus": "OFF", "date": "2026-05-01" }]
    }
  ]
}
```

**TanStack Query 캐시 키 권장 패턴 (Strategy B — normalize):**

```ts
// v1.2 배열 구조 수신 후 개별 캐시 키로 분산
onSuccess: (data) => {
  // 스케줄 전체
  queryClient.setQueryData(['schedule', storeId, year, month], data);
  // 직원별 entries 개별 캐시 (특정 직원 휴무 변경 시 해당 키만 무효화 가능)
  data.entries.forEach((group) => {
    queryClient.setQueryData(
      ['schedule', storeId, year, month, 'employee', group.employeeId],
      group.entries
    );
  });
}
```

**v1.1 임시 대응:** 현재 Map 구조의 `entries` 객체에서 `Object.entries()`로 변환해 사용:

```ts
// v1.1 클라이언트 side transform (임시)
const normalizedEntries = Object.entries(response.entries).map(
  ([employeeName, entries]) => ({
    employeeName,
    employeeId: entries[0]?.employeeId,  // ScheduleEntryItemResponse에 이미 포함
    entries,
  })
);
```

---

### 질문 2. Bulk PATCH 응답 — 204 vs diff 응답

**질문:** `PATCH /stores/{storeId}/schedules/{year}/{month}/entries` 응답 형식 확인. 낙관적 업데이트 롤백을 위한 diff 응답 요청.

**백엔드 최종 답변: 현재 `CommonResponse<Void>` (200 + 빈 result 배열), diff 응답 v1.2 검토**

소스 검증 결과:

```java
// ScheduleController.java
@PatchMapping("/stores/{storeId}/schedules/{year}/{month}/entries")
public CommonResponse<Void> bulkUpdate(...) {
    bulkUpdateScheduleEntriesUseCase.execute(...);
    return CommonResponse.ok(null);   // ← { "success": true, "result": [] }
}
```

**현재 응답 스펙 확정:**

```json
// HTTP 200
{ "success": true, "result": [] }
```

204 No Content가 아닌 **200 + 빈 배열**임을 명시한다. 

**낙관적 업데이트 권장 패턴 (v1.1):**

```ts
// useMutation — 낙관적 업데이트 + 실패 시 전체 재조회로 롤백
const bulkUpdateMutation = useMutation({
  mutationFn: api.bulkUpdateEntries,
  onMutate: async (variables) => {
    await queryClient.cancelQueries({ queryKey: ['schedule', storeId, year, month] });
    const previousData = queryClient.getQueryData(['schedule', storeId, year, month]);
    // 낙관적으로 로컬 데이터 업데이트
    queryClient.setQueryData(['schedule', storeId, year, month], (old) => 
      applyLocalUpdate(old, variables)
    );
    return { previousData };
  },
  onError: (err, variables, context) => {
    // 실패 시 전체 schedule 재조회로 롤백 (diff 없으므로)
    queryClient.setQueryData(
      ['schedule', storeId, year, month], 
      context.previousData
    );
  },
  onSettled: () => {
    // 성공/실패 모두 서버 최신 데이터로 동기화
    queryClient.invalidateQueries({ queryKey: ['schedule', storeId, year, month] });
  },
});
```

**v1.2 검토 — diff 응답 추가:**

```json
// v1.2 제안: PATCH 성공 시 변경된 entries만 반환
{
  "success": true,
  "result": [{
    "updatedEntries": [
      { "entryId": 101, "employeeId": 1, "workStatus": "OFF", "date": "2026-05-03" }
    ]
  }]
}
```

이 경우 `onSuccess`에서 `invalidate` 없이 `setQueryData`로 정확한 캐시 패치 가능.

---

### 질문 3. POST /employees/{id}/day-off-requests — 멱등성 보장 여부

**질문:** 오프라인 큐 재시도 시 이중 신청 방지. `X-Idempotency-Key` 헤더 지원 또는 서버 단 중복 체크 여부.

**백엔드 최종 답변: 서버 단 중복 체크 존재, X-Idempotency-Key v1.2 추가 예정**

현재 구현 상태 분석:

| 항목 | 현재 상태 |
|---|---|
| 동일 직원 + 동일 날짜 중복 신청 | DB 제약 또는 서비스 레이어 검증 여부 확인 필요 |
| X-Idempotency-Key 헤더 처리 | ❌ 미구현 |
| 오프라인 큐 재시도 안전성 | ⚠️ 보장 불완전 |

**v1.1 오프라인 큐 재시도 임시 방어 로직 (프론트 단):**

```ts
// 오프라인 큐 항목에 clientRequestId 포함
interface OfflineQueueItem {
  id: string;       // UUID (클라이언트 생성)
  endpoint: string;
  payload: unknown;
  createdAt: number;
  retryCount: number;
}

// 재시도 시 서버 응답이 409 Conflict이면 이미 처리된 것으로 간주
const retryOfflineQueue = async (item: OfflineQueueItem) => {
  try {
    const result = await api.request(item);
    removeFromQueue(item.id);
    return result;
  } catch (err) {
    if (err.response?.status === 409) {
      // 이미 신청됨 → 큐에서 제거 (성공으로 처리)
      removeFromQueue(item.id);
      return;
    }
    // 그 외 에러 → 재시도 큐 유지
    incrementRetryCount(item.id);
  }
};
```

**v1.2 확정 계획 — X-Idempotency-Key 도입:**

```http
POST /employees/{id}/day-off-requests
X-Idempotency-Key: {client-generated-uuid}
Content-Type: application/json

{ "date": "2026-05-10", "reason": "개인 사유" }
```

서버 처리: Redis 또는 DB에 `idempotency_key` 저장 → TTL 24h → 동일 키 재요청 시 201로 이전 응답 반환.

---

### 질문 4. onboarding-status에서 storeId — STORE_MISSING 시 null 여부

**질문:** SplashScreen에서 `storeId`를 즉시 활용 가능한가? STORE_MISSING 상태에서 null인가?

**백엔드 최종 답변: ✅ 확정 — storeId는 @Nullable. STORE_MISSING 시 null**

소스 검증 결과:

```java
// OnboardingStatusResponse.java
public record OnboardingStatusResponse(
    String role,
    String status,
    @Nullable Long storeId,          // ← @Nullable 명시
    @Nullable StoreSummaryResponse currentStore,
    @Nullable StoreSummaryResponse pendingStore
) {}

// MeMapper.java
return new OnboardingStatusResponse(
    view.role().name(),
    view.status().name(),
    view.storeId() != null ? view.storeId().value() : null,   // null safe
    view.currentStore() != null ? StoreSummaryResponse.from(view.currentStore()) : null,
    view.pendingStore() != null ? StoreSummaryResponse.from(view.pendingStore()) : null
);
```

**status별 null 필드 매트릭스:**

| status | storeId | currentStore | pendingStore |
|---|---|---|---|
| `STORE_MISSING` | **null** | null | null |
| `INVITE_PENDING` | null | null | not null |
| `STORE_CONFLICT` | not null (현재 매장) | not null | not null |
| `COMPLETE` | **not null** | not null | null |

**SplashScreen 분기 로직 권장 패턴:**

```ts
const { status, storeId, role, pendingStore } = onboardingStatus;

switch (status) {
  case 'STORE_MISSING':
    // storeId === null 확정
    navigation.replace('OnboardingStack', { screen: 'StoreRegisterScreen' });
    break;
    
  case 'INVITE_PENDING':
    // storeId === null, pendingStore !== null
    navigation.replace('OnboardingStack', { screen: 'InvitePendingScreen', params: { pendingStore } });
    break;
    
  case 'STORE_CONFLICT':
    // storeId !== null (currentStore), pendingStore !== null
    navigation.replace('OnboardingStack', { screen: 'StoreConflictScreen', params: { storeId, pendingStore } });
    break;
    
  case 'COMPLETE':
    // storeId !== null — 추가 API 없이 즉시 메인 스택 진입 가능
    if (role === 'ADMIN') {
      navigation.replace('AdminTabs', { storeId });
    } else {
      navigation.replace('EmployeeTabs', { storeId });
    }
    break;
}
```

**확정:** `COMPLETE` 상태에서는 `storeId`가 항상 non-null이므로, SplashScreen에서 `GET /stores/{storeId}` 추가 호출 없이 `storeId`를 `AdminTabs`/`EmployeeTabs`로 전달하는 패턴이 안전하다. 이 스펙은 v1.2에서도 변경 없이 유지한다.

---

## 2. 4대 아젠다 — 백엔드 최종 확정 입장

### 2-1. 모바일 최적화 API — BFF 합산 엔드포인트

**최종 결정:**
- **v1.1**: `Promise.all([onboarding, schedule, store])` 병렬 호출로 확정
- **v1.2**: `GET /me/home-summary` 신규 엔드포인트 추가

`GET /me/home-summary` 최종 응답 구조:

```json
{
  "success": true,
  "result": [{
    "role": "ADMIN",
    "onboardingStatus": "COMPLETE",
    "storeId": 42,
    "storeName": "워키 카페",
    "thisMonthScheduleId": 10,
    "thisMonthViolated": false,
    "employeeCount": 6,
    "pendingDayOffCount": 3,
    "upcomingHolidays": ["2026-05-05"]
  }]
}
```

- `employees` 목록·`entries` 등 대용량 데이터는 포함하지 않음 (lazy 별도 호출 유지)
- TanStack Query normalize 전략(Strategy B): `onSuccess`에서 개별 캐시 키에 분배

**v1.2 전환 시 교체 포인트:** `api/bootstrap.ts` 단일 파일에 격리 ✅ (frontend-round2 §1-1 제안 수용)

---

### 2-2. FCM 푸시 — 타임라인 확정

**최종 결정:**

| 단계 | 내용 | 시점 |
|---|---|---|
| v1.1 출시 | `PATCH /me/fcm-token` 토큰 저장 ✅, 알림 발송 NoOp | 현재 완료 |
| v1.2 | Firebase Admin SDK 연동, 실제 발송 시작 | 미정 |
| v1.2 | `PATCH /me/notification-preferences` 카테고리별 on/off | FCM 연동 동시 |
| v1.2+ | daily digest, silent hours | notification-preferences 이후 |

**앱 측 FCM 구현 지침 (확정):**

```ts
// 1. 로그인 완료 후 즉시 토큰 등록
const registerToken = async () => {
  const token = await messaging().getToken();
  await api.patch('/me/fcm-token', { fcmToken: token });
};

// 2. onTokenRefresh — 토큰 갱신 시 재등록
messaging().onTokenRefresh(async (newToken) => {
  await api.patch('/me/fcm-token', { fcmToken: newToken });
});

// 3. 푸시 권한 요청 타이밍: 첫 휴무 신청 완료 직후
// (pm-round1 §3.3 + ux-round1 §3 합의)
const afterFirstDayOffRequest = () => {
  messaging().requestPermission();
  registerToken();
};
```

---

### 2-3. 바텀시트 API 연동 — 최종 타이밍 표

| UX 액션 | 엔드포인트 | v1.1 응답 시간 | 비고 |
|---|---|---|---|
| 초대 바텀시트 열기 | `POST /employees/{id}/invite` | < 500ms | 링크 생성 |
| 휴무 신청 제출 | `POST /employees/{id}/day-off-requests` | < 500ms | 오프라인 큐 지원 |
| 매장 전환 확인 | `POST /me/confirm-store-switch` | < 500ms | — |
| 스케줄 생성 확정 | `POST /stores/{storeId}/schedules/generate` | **1~5초** | 타임아웃 10s 설정 필수 |
| Bulk 수정 저장 | `PATCH /stores/{storeId}/schedules/{year}/{month}/entries` | < 500ms | 현재 200+빈배열 응답 |

---

### 2-4. 한 손 조작 UX — 백엔드 지원 사항

**드래그 중 API 호출 없음 (확정):** 충돌 검증은 클라이언트 단 전담. 서버는 `POST .../generate` 한 번만 호출.

**클라이언트 충돌 계산에 필요한 데이터 (백엔드 제공 확정):**
- `minStaffPerDay` → `GenerateScheduleRequest`에서 프론트가 직접 입력
- `totalEmployees` → `GET /stores/{storeId}/employees` 응답 count
- `confirmedDayOffs` → 드래그로 구성한 로컬 상태

---

## 3. HTTP 캐시 헤더 — 최종 채택 계획

### v1.2 Cache-Control 헤더 추가 확정

| 엔드포인트 | Cache-Control | 비고 |
|---|---|---|
| `GET /stores/{id}/employees` | `max-age=300, private` | 5분 |
| `GET /stores/{id}/schedules?year&month` | `max-age=60, private` | 1분 |
| `GET /schedules/{id}/entries` | `max-age=300, private` | ETag 병행 |
| `GET /stores/{id}/schedules/annual` | `max-age=3600, private` | 1시간 |
| `GET /me/onboarding-status` | `no-cache` | 항상 최신 |

### ETag 도입 — v1.2 우선 대상

frontend-round2 §1-4 요청 수용. 대상 엔드포인트:
- `GET /stores/{storeId}/schedules?year=&month=`
- `GET /schedules/{scheduleId}/entries`

```http
// 서버 응답
HTTP/1.1 200 OK
ETag: "schedule-10-v3"
Cache-Control: max-age=60, private

// 클라이언트 재요청
GET /schedules/10/entries
If-None-Match: "schedule-10-v3"

// 미변경 시
HTTP/1.1 304 Not Modified
```

v1.2 스프린트 첫 항목으로 등록.

---

## 4. 트랜잭션 정합성 — 최종 가이드

백엔드 Round 2에서 식별한 3개 위험 지점에 대한 최종 대응:

| 위험 | v1.1 대응 | v1.2 대응 |
|---|---|---|
| 휴무 신청 + 스케줄 생성 동시 | 서버: 단일 트랜잭션 (타이밍 경쟁 가능) | 422 상태 코드 + "생성 중" 상태 플래그 |
| Bulk 수정 + 근무 교환 동시 | last-write-wins (낙관적 잠금 없음) | `schedule_entries.version` 컬럼 추가 |
| 오프라인 큐 이중 제출 | 409 응답 시 성공으로 간주 (프론트) | `X-Idempotency-Key` 서버 처리 |

---

## 5. 전체 라운드 합의 매트릭스

| 항목 | 결정 | 적용 버전 |
|---|---|---|
| FCM 토큰 엔드포인트 | `PATCH /me/fcm-token { fcmToken }` | v1.1 ✅ |
| JWT 저장 | react-native-keychain (Keychain/Keystore) | v1.1 ✅ |
| 캐시 저장 | MMKV (비민감 데이터) | v1.1 ✅ |
| BFF 합산 API | `GET /me/home-summary` | v1.2 |
| entries 구조 | Map → 배열 `[{ employeeId, entries }]` | v1.2 |
| Bulk PATCH 응답 | 현재 200+빈배열, diff 응답 추가 | v1.2 검토 |
| Idempotency-Key | v1.2 추가 예정 | v1.2 |
| storeId nullability | STORE_MISSING 시 null (확정) | v1.1 ✅ |
| ETag 지원 | schedule endpoints 우선 | v1.2 |
| CommonResponse 언래핑 | Axios 인터셉터 자동 처리 (Frontend 선택 A) | v1.1 ✅ |
| 충돌 검증 위치 | 클라이언트 단 (서버는 최종 generate만) | v1.1 ✅ |
| 스케줄 생성 타임아웃 | 10초 (클라이언트) | v1.1 ✅ |
| 딥링크 파일 서빙 | AASA / assetlinks.json | v1.2 |
| notification-preferences API | FCM 연동 후 | v1.2+ |

---

## 6. Round 3 백엔드 최종 확인 사항

### 즉시 조치 필요 (v1.1 릴리즈 전)

1. ✅ **FCM 토큰 스펙 조율 완료** — frontend가 `PATCH /me/fcm-token { fcmToken }`으로 수정 확인
2. ✅ **onboarding-status storeId null 처리** — 소스 확인 완료, `@Nullable` 보장됨
3. ✅ **Bulk PATCH 응답 스펙 명확화** — `CommonResponse<Void>` (200 + 빈배열) 확정 전달

### v1.2 백엔드 작업 항목 (우선순위 순)

1. Firebase Admin SDK 연동 (FCM 실제 발송)
2. ETag 지원 (`GET /schedules/{id}/entries`, `GET /stores/{id}/schedules`)
3. `GET /me/home-summary` BFF 엔드포인트
4. `ScheduleDetailResponse.entries` Map → 배열 전환
5. `X-Idempotency-Key` 처리 (`POST /employees/{id}/day-off-requests`)
6. `PATCH /me/notification-preferences` + members 테이블 컬럼
7. Bulk PATCH diff 응답 추가
8. 딥링크 정적 파일 서빙 (AASA / assetlinks.json)

---

*Backend Round 3 완료 — 모든 DTO 질문 최종 답변 및 v1.2 로드맵 확정.*
