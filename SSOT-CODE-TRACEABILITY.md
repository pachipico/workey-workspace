# SSOT - 소스 추적성 인덱스 (요구사항 ID 중심)

목적: Obsidian WorKey 볼트(SSOT)의 요구사항을 실제 소스(workey-api / workeyApp)에 양방향 연결해,
"이거 됐는지 확인해" / "이 코드 고치면 어디 영향가" 류 작업을 빠르게 검증·관리하기 위한 파생 인덱스.

주축 = `WorKey - 전체 진척도`의 요구사항 ID (MVP-BE/FE, EMP-BE/FE). 이 인덱스는 SSOT를 대체하지 않고 가리킨다.
완료 처리 원칙(SSOT 5절): 문서만 보고 체크하지 않는다. 코드 + live OpenAPI + 실행 evidence 조합으로 확인한다.

## 표기 범례

상태 마커
- 완료    : SSOT에서 완료로 체크됨
- 미완    : SSOT에서 미완료
- 드리프트 : 계약 불일치 / 코드와 OpenAPI 불일치

앵커 신뢰도
- [코드확인]  : 이번 세션에 코드 grep으로 존재·호출 확인됨 (신뢰)
- [SSOT인용]  : SSOT 인용 anchor — 코드 재확인 미실시 (확장 시 검증 대상)

## 검증 출처

- SSOT: `WorKey - 전체 진척도`(2026-06-02 기준), `WorKey - 백엔드`, `specs/MVP_ADMIN_SCREEN_API_MATRIX`, `specs/MVP_EMPLOYEE_APP_API_MATRIX`
- 백엔드 [코드확인]: `workey-api/src/main/java/com/devwelllab/workeyapi/presentation/*Controller.java` (17개 컨트롤러 전부 method->UseCase grep 확인 2026-06-08, 부록 B 참조)
- 프론트 [코드확인]: `workeyApp/src/**` 실제 코드 grep 확인 2026-06-08 (MVP-FE 전 항목 + EMP-FE placeholder/drift). 경로는 `workeyApp/src/` 기준.
- 프론트 단일 API 경로 소스: `workeyApp/src/shared/api/endpoints.ts` (ENDPOINTS 객체)
- live OpenAPI: `http://localhost:9090/v3/api-docs` (62 paths, SSOT 기준 시점)

---

# 1. MVP 백엔드 (MVP-BE)

| ID | 상태 | 요구사항 | 구현/근거 코드 앵커 | 관련 API | 의존성 |
|---|---|---|---|---|---|
| MVP-BE-001 | 완료 | FCM 실연동 (Firebase Admin SDK + 알림 3종) Phase 998 | [코드확인] `FcmNotificationAdapter`, `FirebaseConfig`, `FcmNotificationEventListener` / [SSOT인용] `998-VERIFICATION.md`(12/13) | `PATCH /me/fcm-token` (`MeController.updateFcmToken` -> `UpdateFcmTokenUseCase` [코드확인]) | - |
| MVP-BE-002 | 미완 | 실제 푸시 수신 evidence (iOS>=1, Android advisory>=1) | (런타임 evidence - 코드 아님) [SSOT인용] launch evidence 문서 | - | BE-001, FE-002 |
| MVP-BE-003 | 미완 | release-target `/dev/**` 백도어 제거 증명 | [코드확인] `DevTokenController` 제거됨(source 확인) / [SSOT인용] release-target runtime proof 남음 | (없어야 함) `/dev/**` | - |
| MVP-BE-004 | 미완 | `/dev/**` 재등장 방지 guard CI 실행 evidence | [코드확인] `DevBackdoorSourceGuardTest` / [SSOT인용] `.github/workflows/deploy-main.yml` (test 미실행) | - | - |
| MVP-BE-005 | 완료 | `DELETE /me` 회원 탈퇴 API 불일치 해소 (live OpenAPI 노출) | [코드확인] `MeWithdrawalController` `@DeleteMapping("/me")` → `DeleteMemberUseCaseImpl` / [계약확인] 2026-06-15 live OpenAPI `/me` DELETE 노출 | `DELETE /me` (`MeWithdrawalController`) | FE-001 |
| MVP-BE-006 | 미완 | API 인증 실패 응답 계약 고정 (401/403 JSON) | [SSOT인용] `authenticationEntryPoint`/`accessDeniedHandler` 신설 필요 (Phase 49 scoped) | 무인증 보호 API 전반 | - |
| MVP-BE-007 | 완료 | Phase 46.1 store-scoped BOLA 감사·적용 | [SSOT인용] `46.1-VERIFICATION.md`(19/19), `46.1-HUMAN-UAT.md`(13/13) | wrong-store `/stores`,`/employees`,`/schedules` ... 403 | - |
| MVP-BE-008 | 완료 | 4xx/5xx ErrorResponse ETag/캐시 헤더 누수 차단 | [코드확인] `ErrorResponseCacheHeaderAdvice`(신규), `common/web/ETagConditional` / [SSOT인용] ETag endpoint 8종 회귀 | ETag endpoint 8종 (`ScheduleController`,`MeController`) | - |
| MVP-BE-009 | 미완 | `scheduleId` 기반 full detail API gap | [코드확인] `ScheduleController`에 `GET /schedules/{scheduleId}` 메서드 없음 확인. 존재: `GET /schedules/{scheduleId}/entries`->GetScheduleEntriesUseCase (entries만) | `GET /schedules/{scheduleId}` | - |
| MVP-BE-010 | 완료 | dev access token 24h 백도어 편의 설정 cleanup | [SSOT인용] `application-dev.yml`(override 제거), `application.yml`(30분만) | - | - |
| MVP-BE-011 | 미완 | 직원 조회 응답에 관리자 본인 식별 필드(`isAdmin`) | [SSOT인용] `EmployeeResponse` 확장 필요 (Phase 49 scoped) | `GET /stores/{storeId}/employees`, `GET /me/employee` | FE-012 |

# 2. MVP 프론트엔드 (MVP-FE) — 전 항목 2026-06-08 코드 검증 완료

| ID | 상태 | 요구사항 | 구현/근거 코드 앵커 ([코드확인] = workeyApp/src 코드 확인) | 관련 API | 의존성 |
|---|---|---|---|---|---|
| MVP-FE-001 | 드리프트·미완 | `SettingsScreen` 회원 탈퇴 처리 정리 | [코드확인] `settings/screens/SettingsScreen.tsx:101` `apiClient.delete(ENDPOINTS.me.account)` (account='/me'), `WithdrawSheet`(:399). 드리프트 실재 확인 - OpenAPI에 `DELETE /me` 없음 -> 런타임 404 위험 | `DELETE /me` (계약 없음) | BE-005 |
| MVP-FE-002 | 미완 | FCM 실기기 검증 | [코드확인] 코드존재 `notifications/components/FcmMessagingBridge.tsx`, `notifications/api/fcmToken.ts` / 실기기 receipt = 런타임 evidence(미완) | `PATCH /me/fcm-token` | BE-001 |
| MVP-FE-003 | 완료 | iOS TTI 실측 evidence (hit<=800ms, miss<=1500ms) | [실행확인] Measurement 빌드 실측: cache-hit 540ms(≤800) / cache-miss 999·1072ms(≤1500), 인증 재실행 기준. cache-hit=`homeSummary.ts` MMKV persist(staleTime 60s)로 마운트 시 fetch 생략. evidence: `MVP-FE-003-ios-tti/MEASUREMENT.md`([TTI] 원문 3건). 커밋 `de9293e`·`786d804`·`01b6df1`. 측정환경 iPhone 17 Pro 시뮬/iOS 26.4/backend 9090 | - | - |
| MVP-FE-004 | 완료 | GitHub Actions 첫 PR guard 실행 evidence | [실행확인] `pr-guards.yml` push:[main] 트리거(commit `d35818d`) → Actions run #1 `release-guards` success(59s), `npm ci`+`guard:release`(R-1/R-2/R-3/R-6) green. evidence: `MVP-FE-004-ci-guard-run/run1-pr-guards-green.png` + run 28008900059 | - | - |
| MVP-FE-005 | 완료 | 알림 설정 화면 서버 GET/PATCH 연동 | [코드확인] `settings/screens/NotificationSettingsScreen.tsx:74-75` -> `notifications/api/notificationSettings.ts:81,94` (`useNotificationSettingsQuery`/`useUpdateNotificationCategorySetting`) -> `me.notificationSettings` | `GET/PATCH /me/notification-settings` | - |
| MVP-FE-006 | 완료 | 서버 logout 연동 | [코드확인] `settings/screens/SettingsScreen.tsx:82` `apiClient.post(ENDPOINTS.auth.logout, {refreshToken})` | `POST /auth/logout` (`AuthController.logout` [코드확인]) | - |
| MVP-FE-007 | 완료 | 서버 export API 연결 결정·반영 | [코드확인] `schedule/api/scheduleExport.ts:21-31` (exportPng/Xlsx/Ics) | `GET /schedules/{scheduleId}/export/{png,xlsx,ics}` | - |
| MVP-FE-008 | 완료 | schedule membership API 연결 | [코드확인] `roster/screens/RosterScreen.tsx:101-102` -> `roster/api/rosterQueries.ts:307,330` (`useAddScheduleMember`/`useRemoveScheduleMember`) -> `schedules.members` | `POST/DELETE /schedules/{scheduleId}/members` | - |
| MVP-FE-009 | 완료 | VC collection toggle 연결 (생성 직전 next-month lock) | [코드확인] `schedule/api/scheduleQueries.ts:642` `ENDPOINTS.stores.vcCollection(...)` PATCH + `schedule/screens/VacationCollectScreen.tsx` + `schedule/lib/scheduleGenerateContext.ts` + `home/api/homeSummary.ts` | `PATCH /stores/{storeId}/vc-collection` | - (주의: workeyApp 미커밋) |
| MVP-FE-010 | 완료 | FCM 프론트 live path wiring | [코드확인] `notifications/components/FcmMessagingBridge.tsx`, `notifications/api/fcmToken.ts:21` `apiClient.patch(me.fcmToken,...)` | `PATCH /me/fcm-token` | BE-001 |
| MVP-FE-011 | 완료 | 월별 스케줄 stale 404 클라이언트 방어 | [코드확인] `schedule/api/scheduleQueries.ts`, `shared/query/queryClient.ts`, 401 interceptor=`shared/api/client.ts` | `GET /stores/{storeId}/schedules?year=&month=` | BE-008 |
| MVP-FE-012 | 완료 | 팀 현황 관리자 본인 식별값 기반 UI 분기 | [코드확인] `roster/api/rosterQueries.ts`가 `EmployeeResponse.isCurrentAdmin`을 `Employee`로 정규화, `home/screens/HomeScreen.tsx` 팀 현황 self chip, `roster/screens/RosterScreen.tsx` 본인 chip/카카오·삭제 숨김/제외 self 분기가 `isCurrentAdmin` 우선 사용. Tests: `HomeScreen.test.tsx`, `RosterScreen.test.tsx` | `GET /stores/{storeId}/employees` | BE-011 |

# 3. 직원 앱 백엔드 (EMP-BE)

| ID | 상태 | 요구사항 | 구현/근거 코드 앵커 | 관련 API | 의존성 |
|---|---|---|---|---|---|
| EMP-BE-001 | 완료 | 직원 본인 휴무 신청 목록 API 추가 | [실행확인] `GET /me/day-off-requests` — `MeController` + `GetMyDayOffRequestsUseCase`(swap /me 거울) + out-port `loadByEmployeeId` + jooq adapter(param 바인딩). OpenAPI 노출+무인증 401 확인, 테스트 149 pass | `GET /me/day-off-requests` (본인 employeeId 격리, 전 status) | - |
| EMP-BE-002 | 완료 | 직원 휴무 신청 상세/취소 `/me` scope 정리 | [코드확인] 취소 `DELETE /day-off-requests/{id}` 이미 본인 전용(EMPLOYEE+self-ownership 가드+PENDING-only, 무변경). 조회=EMP-BE-001. 상세 endpoint 불필요(목록 item 전 필드 포함, YAGNI) | 조회=`GET /me/day-off-requests`, 취소=`DELETE /day-off-requests/{id}` | EMP-BE-001 |
| EMP-BE-003 | 완료(scope-out) | 근무 교환 상대 수락/거절 정책/API 확정 | [정책확정 2026-07-04] 상대 수락 단계 없음 — 당사자 사전 합의 전제, 관리자 승인만으로 확정. 현재 API(Create/Cancel + ADMIN Approve/Reject)가 정책과 정합 → 백엔드 무변경. 기획서 L252/L309 2단계로 수정 완료. 추후 '상대 수락' 추가 검토 예정. | (target-approve/reject 미도입 — 정책상 제외) | - |
| EMP-BE-004 | 완료 | 초대 링크 consume flow E2E 검증 | [검증완료 2026-07-05] create→preview→consume E2E(`InviteConsumeFlowEndToEndIntegrationTest`, TestContainers 실HTTP 3스텝 + 실DB 상태전이: role EMPLOYEE/member_id 링크/used_at 스탬프) + `POST /employees/*/invite` ADMIN authz 갭 픽스(SecurityConfig 매처 + 메소드 `@PreAuthorize`, 비-ADMIN 403 회귀) / gradle 1499 pass / 커밋 `56c67966` | `POST /employees/{id}/invite`, `GET /invite/{token}/preview`, `POST /auth/kakao/token-login` | - |
| EMP-BE-005 | 미완 | 직원 알림 실푸시 검증 | [코드확인] `NotificationController` / [SSOT인용] Phase 998/998.1 의존 | `GET /me/notifications` | BE-001 |
| EMP-BE-006 | 미완 | 복구 요청 lifecycle 검증 | [코드확인] `MeController.requestRestore` -> `RequestRestoreUseCase`, `RestoreActionController`, `RestorePreviewController` | `POST /me/request-restore`, `/restore/{token}/{preview,consume,reject}` | - |
| EMP-BE-007 | 미완 | 직원 store conflict/switch 정책 검증 | [코드확인] `MeController.confirmStoreSwitch` -> `ConfirmStoreSwitchUseCase` | `POST /me/confirm-store-switch` | - |

# 4. 직원 앱 프론트엔드 (EMP-FE) — placeholder/drift 2026-06-08 코드 확인

핵심 확인 [코드확인]: `workeyApp/src/features/employee/`에는 `screens/_Placeholder.tsx` 단 1개 파일만 존재. 직원 탭(EmployeeTabs/MySchedule/ShiftSwap/Notifications/Settings) 전체가 미구현임을 코드로 확정.

| ID | 상태 | 요구사항 | 구현/근거 코드 앵커 | 관련 API | 의존성 |
|---|---|---|---|---|---|
| EMP-FE-001 | 미완 | 직원 앱 Release 2 화면/상태 흐름 | [코드확인] `features/employee/screens/_Placeholder.tsx` 만 존재 | - | - |
| EMP-FE-002 | 미완 | 초대 링크 deep link 처리 | [SSOT인용] invite URL -> token 보존 -> token-login `inviteToken` 미연결 | `POST /auth/kakao/token-login` | BE-004 |
| EMP-FE-003 | 미완 | 직원 MySchedule 화면 | [코드확인] employee=placeholder만 / [SSOT인용] hook `useMyScheduleHistory*` 준비됨 | `GET /me/schedules`, `/me/schedules/history{,/years}` | - |
| EMP-FE-004 | 완료 | 직원 휴무 신청/취소/내역 화면 | [구현확인 2026-07-05] 신청(`LeaveRequestFlow`) + 내역 화면(`EmployeeDayOffHistoryScreen`, status 클라이언트 필터) + 취소(`useCancelDayOffRequest`, DELETE 물리삭제 + Alert destructive). 공용 `DayOffRequestRow`. 커밋 466cfe0/077a1fd(신청·내역) + `e74be34`(내역화면·취소), origin push. tsc0/jest438, 스샷 evidence/emp-fe-004/09~12. | `POST /employees/{id}/day-off-requests`, `GET /me/day-off-requests`, `DELETE /day-off-requests/{id}` + EMP-BE-001 | EMP-BE-001 |
| EMP-FE-005 | 완료 | 직원 근무 교환 신청/내역 화면 | [구현확인 2026-07-05] 신청 3-step(`ShiftSwapFlow`) + 홈 "대기중" 카드 + 내역 화면(status 필터, `EmployeeSwapHistoryScreen`) + 취소(Alert destructive, `useCancelSwapRequest`). 공용 `SwapRequestRow`. 커밋 FE `401da6b`/`ffd4fda`/`5d1f2fc` + BE 2일 맞교대 `31c7290f`. tsc0/jest438, 스샷 evidence/emp-fe-005/01~12. TARGET 노출·전역 홈경고는 후속. | `POST /schedule-entries/swap-requests`, `GET /me/swap-requests`, `DELETE /swap-requests/{id}` | 31c7290f |
| EMP-FE-006 | 완료(scope-out) | 교환 상대 수락/거절 UI 또는 scope-out | [정책확정 2026-07-04] EMP-BE-003 = 상대 수락 없음 확정 → target 승인 UI 정책상 제외. 구현 없음. | (상대 수락 UI 정책상 제외) | EMP-BE-003 |
| EMP-FE-007 | 완료 | 직원 알림 인박스 | [구현확인 2026-07-05] 기존 `NotificationsScreen`을 `audience` param('admin'\|'employee')로 재사용(신규 화면 0) + 직원 홈 벨 onPress→인박스 + unread 개수 뱃지 + tap 읽음처리(딥링크는 EMP-FE-002 분리) + loading/error/pull-refresh + 상대시간. 커밋 `a0a3d95`, origin ↑1(미push). tsc0/eslint0/jest9(admin 무회귀), 시뮬 7항목. | `GET /me/notifications`, `PATCH /me/notifications/{id}/read` | - |
| EMP-FE-008 | 완료(코드검증) | 복구 요청 버튼 API 연결 | [구현확인 2026-07-05] 이전 "toast-only" 기록은 stale. `RemovedNoticeScreen.onRestoreRequest`(버튼 testID `removed-restore-request`)→POST /me/request-restore + onboarding-status invalidate + `RecoveryRequested` 이동; 409→"이미 복구 요청"→RecoveryRequested; error toast. `endpoints.me.requestRestore='/me/request-restore'`, `OnboardingStack case 'REMOVED'→RemovedNotice` 정합. 백엔드 POST /me/request-restore + preview/consume/reject 존재. ※ live E2E(removed 로그인 흐름) 미실시 — 코드+계약 검증으로 close. | `POST /me/request-restore` | - |
| EMP-FE-009 | 미완 | 관리자 Roster 초대 토큰 발급/공유 UI | [코드확인] `features/roster/`에 invite 발급 API 호출 0건 (로컬 sheet만) | `POST /employees/{id}/invite` | - |
| EMP-FE-010 | 미완 | 초대 preview 화면 연결 | [SSOT인용] `WelcomeScreen` storeStore fallback만 | `GET /invite/{token}/preview` | - |
| EMP-FE-011 | 완료 | 직원 설정 화면 | [구현확인 2026-07-05] 스켈레톤(로그아웃만)→풀 구성: 계정카드(아바타 편집=공용 `AvatarPickerSheet`+`useUpdateEmployeeAvatar` 재사용/이름 표시만) + 알림설정(`NotificationSettingsScreen` audience 파라미터화, 직원 4토글) + 이용약관·개인정보 modal + 로그아웃 + 탈퇴(`WithdrawSheet` 재사용). 신규 파일/컴포넌트/훅 0. 커밋 `90868a7`, origin ↑2(미push). tsc0/eslint0/jest 81suites·438(admin 무회귀), 시뮬 7항목. 제외(백엔드 근거): 근무패턴(self 403)·이름편집(name 차단)·schedGen(필드 없음)·workMute. | `GET/PATCH /me/notification-settings`, `PATCH /employees/{id}`(profileAvatar self), `DELETE /me` | - |
| EMP-FE-012 | 미완 | 직원 온보딩 상태별 화면 정리 | [SSOT인용] 일부 status 화면 미연결 | `GET /me/onboarding-status` (10 status) | - |

---

# 부록 A. 도메인별 미해결 / 드리프트 (검증 우선 항목)

- 드리프트 `DELETE /me` (BE-005 / FE-001): 프론트는 호출하나 OpenAPI에 없음 -> 런타임 404 위험. BE 추가 또는 FE 제거 결정 필요.
- 드리프트 `PATCH /day-off-relocations`: `StoreModeSimulator` offline DEV sample에만 존재, OpenAPI에 없음 -> replay 시 실패.
- scheduleId full detail gap (BE-009): `ScheduleAdjustScreen`/`ScheduleHistoryDetailScreen`이 scheduleId만으로 full detail 조회 불가, 월별 조회 + scheduleId 일치 검증으로 우회 중.
- ~~근무 교환 상대 수락 단계 (EMP-BE-003 / EMP-FE-006)~~ **해소(2026-07-04)**: 상대 수락 없음 확정(당사자 사전 합의 전제, 관리자 승인만). 기획서 L252/L309 2단계로 수정, 현재 API 정합. 추후 '상대 수락' 추가 검토 예정.
- FCM 실수신 (BE-002 / FE-002 / EMP-BE-005): 코드/배선 완료, 실기기 receipt evidence 미확보.

# 부록 B. 엔드포인트 - 백엔드 컨트롤러/UseCase 맵 (전 컨트롤러 method->UseCase grep 확인 2026-06-08, 모두 [코드확인])

| 컨트롤러 | 엔드포인트 -> UseCase |
|---|---|
| `AuthController` | `POST /auth/kakao/callback`->KakaoLogin, `POST /auth/kakao/token-login`->KakaoTokenLogin, `POST /auth/refresh`->RefreshToken, `POST /auth/logout`->Logout |
| `MeController` (`@RequestMapping /me`) | `/select-role`->SelectRole, `PATCH /name`->UpdateMemberName, `/schedules`->GetMySchedules, `PATCH /fcm-token`->UpdateFcmToken, `/onboarding-status`->GetOnboardingStatus, `/home-summary`->GetHomeSummary, `/employee`->GetMyEmployee, `/confirm-store-switch`->ConfirmStoreSwitch, `/confirm-employment-ended`->ConfirmEmploymentEnded, `/request-restore`->RequestRestore, `/swap-requests`->GetMySwapRequestHistory, `/schedules/history{,/years}`->GetMyScheduleHistory{Detail,Years} |
| `StoreController` (`@RequestMapping /stores`) | `POST`->CreateStore, `GET /{id}`->GetStore, `PATCH /{id}`->UpdateStore, `DELETE /{id}`->DeleteStore, `PATCH /{id}/vc-collection`->ToggleVcCollection |
| `ScheduleController` | `POST /stores/{id}/schedules/generate`->GenerateSchedule, `GET /stores/{id}/schedules`->GetSchedule, `GET /schedules/{sid}/entries`->GetScheduleEntries, `GET /schedules/{sid}/export/{png,xlsx,ics}`->ExportSchedule{Png,Xlsx,Ics}, `GET /stores/{id}/schedules/annual`->GetAnnualWorkSummary, `PATCH /stores/{id}/schedules/{y}/{m}/entries`->BulkUpdateScheduleEntries, `POST /schedules/{sid}/members`->AddScheduleMember, `DELETE /schedules/{sid}/members/{eid}`->RemoveScheduleMember, `GET /stores/{id}/schedules/{y}/{m}/matrix`->LoadStoreScheduleMatrix, `GET /stores/{id}/schedules/history{,/years}`->GetStoreScheduleHistory{Detail,Years}. 주의: `GET /schedules/{sid}` full detail 없음(MVP-BE-009 갭 코드 확정) |
| `StoreClosedDayController` | `POST /stores/{id}/closed-days`->RegisterStoreClosedDay, `DELETE /stores/{id}/closed-days/{date}`->DeleteStoreClosedDay, `GET /stores/{id}/closed-days`->GetStoreClosedDayList |
| `DayOffRequestController` | `POST /employees/{eid}/day-off-requests`->CreateDayOffRequest, `GET /stores/{id}/day-off-requests`->GetDayOffRequestList, `GET .../monthly`->GetMonthlyDayOffRequests, `PATCH /day-off-requests/{rid}/approve`->Approve, `.../reject`->Reject, `DELETE /day-off-requests/{rid}`->DeleteDayOffRequest |
| `SwapRequestController` | `POST /schedule-entries/swap-requests`->CreateSwapRequest, `DELETE /swap-requests/{id}`->CancelSwapRequest, `PATCH /swap-requests/{id}/approve`->Approve, `.../reject`->Reject. 주의: target-approve/reject 메서드 없음(EMP-BE-003 갭 코드 확정) |
| `SwapRequestHistoryController` | `GET /stores/{id}/swap-requests`->GetStoreSwapRequestHistory |
| `NotificationController` (`@RequestMapping /me/notifications`) | `GET`->ListMyNotifications, `PATCH /{nid}/read`->MarkNotificationRead |
| `NotificationSettingsController` (`@RequestMapping /me/notification-settings`) | `GET`->GetNotificationSettings, `PATCH`->UpdateNotificationSettings |
| `EmployeeController` | `POST /stores/{id}/employees`->CreateEmployee, `GET /stores/{id}/employees`->GetEmployeeList, `PATCH /employees/{eid}`->UpdateEmployee, `DELETE /employees/{eid}`->DeleteEmployee, `PATCH /stores/{id}/employees/day-off-per-month`->BulkUpdateEmployeeDayOffPerMonth |
| `InviteController` | `POST /employees/{eid}/invite`->IssueInviteToken |
| `InvitePreviewController` | `GET /invite/{token}/preview`->GetInvitePreview |
| `RestoreActionController` | `POST /restore/{token}/consume`->ConsumeRestoreToken, `.../reject`->RejectRestoreToken |
| `RestorePreviewController` | `GET /restore/{token}/preview`->GetRestoreTokenPreview |
| `WellKnownController` | `GET /.well-known/apple-app-site-association`, `GET /.well-known/assetlinks.json` (정적) |

---

# 부록 C. graphify 그래프 탐색 (보강 완료)

42개 요구사항 + 엔드포인트 + 검증된 FE 앵커를 `graphify-out/graph.json`에 노드로 추가하고 기존 백엔드 컨트롤러 노드에 연결했다 (재현 스크립트: `graphify-out/enrich_ssot.py`). 엣지: `req --specifies--> endpoint --served_by--> Controller`, `req --implemented_by--> FE앵커`, `req --depends_on--> req`.

`graphify query`(키워드 BFS)는 노이즈가 많으니 `graphify path`를 쓸 것 (시작/끝 노드를 정확히 앵커):

```
graphify path "MVP-BE-009" "ScheduleController"            # 요구사항 -> 엔드포인트 -> 컨트롤러
graphify path "MVP-FE-006" "AuthController"                # served_by [EXTRACTED] = grep 검증됨
graphify path "MVP-FE-005" "useNotificationSettingsQuery"  # 요구사항 -> 검증된 FE 호출부
graphify path "MVP-FE-002" "MVP-BE-001"                    # 의존성(depends_on)
```

- 드리프트 신호: `DELETE /me` 엔드포인트 노드는 `served_by` 엣지가 없다(백엔드 미구현) -> 그래프에서 고립으로 드러남.
- 그래프 엣지의 `[EXTRACTED]` = 컨트롤러 grep 검증(`/auth`·`/me`·`/stores`·`/terms`·notification). `[INFERRED]` = 도메인명 추정(나머지).

---

## 진행 상태

1. (완료) MVP-FE 전 항목 + EMP-FE placeholder/drift 코드 검증 — 2026-06-08, [SSOT인용] -> [코드확인] 승격.
2. (완료) graphify 그래프 보강 — 요구사항/엔드포인트/FE앵커 노드 + 코드 엣지. `graphify path`로 탐색.
3. (완료) 백엔드 17개 컨트롤러 전부 method->UseCase grep 확인 (부록 B). 부수 확인: MVP-BE-009(scheduleId full detail 없음)·EMP-BE-003(target-approve/reject 없음) 갭이 코드로 확정.

남은 [SSOT인용] 항목(코드 미재확인): MVP-BE의 evidence 문서류(BE-002/003/004/007/010), Phase 49 scoped 항목(BE-005/006/011), TTI/CI 런타임 evidence(FE-003/004). 이들은 코드가 아니라 런타임 evidence나 미실행 plan이라 grep 대상이 아님.
