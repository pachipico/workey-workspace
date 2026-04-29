# [R2-FRONTEND] React Native 앱 구조 — Round 2 반론 및 통합 검토

> **작성자**: frontend-agent  
> **일시**: 2026-04-29  
> **참조**: backend-round1.md / design-round1.md / pm-round1.md / ux-round1.md

---

## 0. Round 1 자기 수정 사항 (타 에이전트 피드백 반영)

Round 1 에서 잘못 기재한 항목을 먼저 수정한다.

| 항목 | Round 1 기재 | 수정 내용 | 출처 |
|---|---|---|---|
| FCM 토큰 등록 엔드포인트 | `POST /me/push-token` | **`PATCH /me/fcm-token`** | backend-round1 §1.2 |
| 토큰 저장 방식 | MMKV AES-256으로 충분 | **JWT → iOS Keychain / Android Keystore** 필수 (MMKV는 일반 캐시용) | backend-round1 §3, pm-round1 §3.3 |
| 푸시 권한 요청 타이밍 | 앱 최초 실행 시 등록 | **첫 휴무 신청 완료 직후** (컨텍스트 있는 시점) | pm-round1 §3.3, ux-round1 §3 |
| CommonResponse 처리 | 미언급 | **단건 응답도 `result[0]`** 으로 접근 필요 (배열 고정) | backend-round1 §4 |

---

## 1. backend-round1 검토 및 반론

### 1-1. ✅ 동의 — BFF 합산 엔드포인트

backend-round1이 `GET /me/home-summary` 를 v1.2 검토 항목으로 올린 것은 전적으로 지지한다.  
**단, v1.2 도입 전까지 RN 클라이언트는 다음 전략을 즉시 적용**한다.

```ts
// SplashScreen에서 병렬 호출 (Promise.all 활용)
const [onboarding, schedule, store] = await Promise.all([
  api.getOnboardingStatus(),           // GET /me/onboarding-status
  api.getMySchedule(year, month),      // GET /me/schedules?year=&month=
  api.getStore(storeId),               // GET /stores/{storeId}
]);

// TanStack Query prefetch — 대시보드 진입 전 미리 캐시에 적재
await queryClient.prefetchQuery({
  queryKey: ['mySchedule', year, month],
  queryFn: () => api.getMySchedule(year, month),
  staleTime: 5 * 60 * 1000,
});
```

`Promise.all`로 병렬화하면 LTE 환경에서 직렬 호출 대비 약 60% 시간 단축.  
v1.2 BFF 엔드포인트 도입 시 교체 포인트를 `api/bootstrap.ts` 단일 파일로 격리해 두면 교체 비용이 최소화된다.

### 1-2. ✅ 동의 — CommonResponse 래퍼 처리

`result`가 항상 배열이므로 API 클라이언트 레이어에서 일괄 언래핑한다.

```ts
// api/client.ts — Axios 인터셉터로 result[0] 자동 언래핑
axiosInstance.interceptors.response.use((response) => {
  const data = response.data;
  if (data?.success && Array.isArray(data.result)) {
    // 단건 리소스: result[0] 반환, 목록은 result 그대로
    response.data = data.result.length === 1 ? data.result[0] : data.result;
  }
  return response;
});
```

### 1-3. ✅ 동의 — 스케줄 생성 API 지연 처리

backend-round1 §2.3에서 "1~5초 가능"으로 명시.  
RN 클라이언트에서는 다음 UX를 적용한다.

```tsx
// 스케줄 생성 뮤테이션 — 낙관적 UI + 타임아웃
const generateMutation = useMutation({
  mutationFn: api.generateSchedule,
  onMutate: () => setLoadingState('generating'),   // 스피너 + "AI가 스케줄을 만들고 있어요..." 문구
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['schedule'] });
    setLoadingState('done');
  },
  onError: (err) => {
    if (err.code === 'ECONNABORTED') {
      showToast('시간이 걸리고 있어요. 잠시 후 다시 확인해주세요.', 'warning');
    }
  },
  // 직원 수 × 일수 비례이므로 10초 타임아웃 기본
  timeout: 10_000,
});
```

### 1-4. ⚠️ 보완 요청 — ETag 지원 필요성

backend-round1 §4에서 ETag/If-None-Match는 "v1.2 검토"로 남겼다.  
그러나 **스케줄 상세(`ScheduleDetailResponse`)는 직원 수 × 30일 크기의 페이로드**로 불필요한 재전송이 모바일 데이터 낭비로 직결된다.  
→ `GET /stores/{storeId}/schedules?year=&month=` 와 `GET /schedules/{id}/entries` 에 대해 **v1.2에서 ETag 우선 도입**을 backend-agent에 요청한다.

```ts
// ETag 클라이언트 구현 준비 (백엔드 지원 시 즉시 활성화)
const fetchScheduleWithETag = async (scheduleId: number) => {
  const cachedEtag = storage.getString(`etag:schedule:${scheduleId}`);
  const res = await api.get(`/schedules/${scheduleId}/entries`, {
    headers: cachedEtag ? { 'If-None-Match': cachedEtag } : {},
  });
  if (res.status === 304) return getCachedSchedule(scheduleId); // 캐시 그대로
  storage.set(`etag:schedule:${scheduleId}`, res.headers.etag);
  return res.data;
};
```

---

## 2. design-round1 검토 및 반론

### 2-1. ✅ 전면 수용 — BottomSheet 스펙 확정

design-round1 §2.1.1이 제시한 스펙을 RN 구현 표준으로 채택한다.

```tsx
// components/WorkeyBottomSheet.tsx — 디자인 토큰 완전 반영
import BottomSheet, {
  BottomSheetView,
  BottomSheetBackdrop,
} from '@gorhom/bottom-sheet';
import { tokens } from '../theme/tokens';

const WorkeyBottomSheet = ({ children, snapPoints = ['60%'], onClose }) => (
  <BottomSheet
    snapPoints={snapPoints}
    onClose={onClose}
    backdropComponent={(props) => (
      <BottomSheetBackdrop
        {...props}
        appearsOnIndex={0}
        disappearsOnIndex={-1}
        opacity={0.4}       // rgba(0,0,0,0.4) — design 스펙
      />
    )}
    handleIndicatorStyle={{
      width: 32,            // design §2.1.1: 너비 32pt
      height: 4,            // design §2.1.1: 높이 4pt
      backgroundColor: tokens.primarySoft,  // #7DD3FC
      marginTop: 8,         // 상단 마진 8pt
    }}
    backgroundStyle={{
      backgroundColor: tokens.surface,      // #FFFFFF
      borderRadius: 20,     // design §2.1.1
    }}
    style={{ paddingHorizontal: 20 }}       // 수평 20pt
  >
    <BottomSheetView style={{ paddingBottom: 16 }}>
      {children}
    </BottomSheetView>
  </BottomSheet>
);
```

### 2-2. ✅ 동의 + 즉시 반영 — `생성 확정` 버튼 하단 이동

design-round1 §5 "헤더 `생성 확정` 위치 — 🟠 높음" 이슈와 ux-round1 §1 시나리오 A 6번에서 모두 지적했다.  
휴무 수집 뷰에서 **헤더 우측 버튼을 제거하고 하단 sticky CTA로 이동**한다.

```tsx
// screens/DayOffCollectionScreen.tsx
const DayOffCollectionScreen = () => {
  const hasConflict = useConflictStore((s) => s.hasConflict);

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <Header title="2026년 6월 휴무 수집" />   {/* 헤더에서 생성 확정 버튼 제거 */}
      <EmployeeTabFilter />
      <DayOffCalendar />
      {/* 하단 고정 CTA */}
      <View style={styles.stickyBottom}>
        <TouchableOpacity
          style={[
            styles.confirmBtn,
            { backgroundColor: hasConflict ? tokens.primary100 : tokens.primary },
          ]}
          disabled={hasConflict}
          onPress={handleConfirm}
          accessibilityLabel={hasConflict ? '충돌 해소 후 생성 확정 가능' : '스케줄 생성 확정'}
        >
          <Text style={{ color: hasConflict ? tokens.primaryInk : '#fff', fontWeight: 'bold' }}>
            {hasConflict ? '⚠️ 충돌을 먼저 해소해주세요' : '생성 확정'}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};
```

### 2-3. ⚠️ 추가 요구 — BottomSheet 3단 높이 (UX 요구 반영)

design-round1은 단일 snap point를 제시했지만, ux-round1 §3이 "30% / 60% / 풀하이트 3단" 필요성을 강하게 주장했다.  
충돌 해소 바텀시트는 달력을 가리지 않도록 **60% 기본 → 풀하이트로 확장** 가능한 구조가 필요하다.

```tsx
// 3단 snap point 구조
const conflictSheetSnapPoints = useMemo(() => ['30%', '60%', '92%'], []);
// 초기 index=1 (60%에서 시작 — 달력 상단 절반 보임)
<WorkeyBottomSheet snapPoints={conflictSheetSnapPoints} initialSnapIndex={1}>
  <ConflictDetail />
</WorkeyBottomSheet>
```

→ **design-agent에 질문**: 3단 snap (30/60/92%) 에서 각 단계의 배경 dimming 강도와 핸들 가시성 스펙을 확정해 달라. 특히 60% 단에서 달력 영역과 바텀시트 경계의 그림자 처리 방식이 필요하다.

### 2-4. ⚠️ Dark Mode — RN 구현 전 토큰 확정 요청

design-round1 §4에서 다크 팔레트를 제안했지만 "미정의 상태"로 남아있다.  
RN `useColorScheme()` 훅이 시스템 모드를 즉시 반영하기 때문에, **토큰 확정 없이 구현 착수 시 전면 수정이 발생**한다.

```ts
// theme/tokens.ts — 다크 모드 대응 준비 구조 (토큰 확정 대기)
import { useColorScheme } from 'react-native';

export const useTokens = () => {
  const scheme = useColorScheme();
  const isDark = scheme === 'dark';
  return {
    primary:    isDark ? '#38BDF8' : '#0EA5E9',   // design §4 다크 제안값
    surface:    isDark ? '#0F172A' : '#FFFFFF',
    background: isDark ? '#1E293B' : '#F0F9FF',
    primaryInk: isDark ? '#7DD3FC' : '#0369A1',
    // ... design-agent 확정 후 채움
  };
};
```

---

## 3. pm-round1 검토 및 반론

### 3-1. ✅ 동의 — MVP MUST 6개 기준 Navigation 우선순위 재조정

pm-round1 §1.2의 MUST 6개를 기준으로 Navigation 구현 우선순위를 재정렬한다.

| 우선순위 | 기능 | Navigation 화면 |
|---|---|---|
| 1 | 직원 앱 초대 링크 진입 (케이스 3) | `OnboardingStack > WelcomeScreen` |
| 2 | 직원 내 스케줄 + 휴무 신청 BottomSheet | `EmployeeTabs > MyScheduleScreen` + `LeaveRequestSheet` |
| 3 | FCM 푸시 통합 | `usePushNotification` 훅 전역 적용 |
| 4 | 관리자 휴무 수집 뷰 | `AdminTabs > ScheduleScreen > DayOffCollectionScreen` |
| 5 | 매장 등록 온보딩 (케이스 1) | `OnboardingStack > StoreRegisterScreen` |
| 6 | 직원 초대 BottomSheet (Kakao Share SDK) | `InviteBottomSheet` |

### 3-2. ✅ 수용 — JWT 토큰 저장 방식 변경

pm-round1 §3.3과 backend-round1 §3 모두 AsyncStorage/MMKV 평문 저장을 경고했다.  
**Access/Refresh Token은 Keychain/Keystore로 격리**하고, MMKV는 민감도 낮은 캐시용으로만 사용한다.

```ts
// utils/secureStorage.ts
import * as Keychain from 'react-native-keychain';
import { MMKV } from 'react-native-mmkv';

export const storage = new MMKV({ id: 'workey-cache' }); // 비민감 캐시용

// JWT 전용 — Keychain (iOS: Keychain Services, Android: Keystore)
export const secureToken = {
  setTokens: async (access: string, refresh: string) => {
    await Keychain.setInternetCredentials(
      'workey.app',
      'tokens',
      JSON.stringify({ access, refresh })
    );
  },
  getTokens: async () => {
    const creds = await Keychain.getInternetCredentials('workey.app');
    if (!creds) return null;
    return JSON.parse(creds.password) as { access: string; refresh: string };
  },
  clearTokens: async () => {
    await Keychain.resetInternetCredentials('workey.app');
  },
};
```

### 3-3. ⚠️ 반론 — TTI 1.5s 목표의 현실성

pm-round1 §2.1에서 첫 화면 TTI ≤ 1.5s를 측정 KPI로 설정했다.  
그러나 **RN cold start(JS Bundle 로드 + Native Bridge 초기화)**만으로 미드레인지 Android에서 800ms~1.2s가 소요된다.  
네트워크 1콜을 더하면 1.5s 달성이 빠듯하다.

**프론트엔드 제안:**
1. **Hermes 엔진** 기본 활성화 (JS 실행 30~40% 개선)
2. **SplashScreen에서 토큰 + 캐시 스케줄을 동시에 표시** → 네트워크 응답 전에 캐시 데이터 먼저 렌더 (stale-while-revalidate)
3. **TTI 기준을 "네트워크 포함 첫 의미있는 콘텐츠 렌더"로 정의** — 단순 Spinner는 TTI 측정에서 제외

```ts
// SplashScreen — 캐시 우선 렌더 (stale-while-revalidate 구현)
const SplashScreen = () => {
  const cachedSchedule = storage.getString('lastScheduleData'); // MMKV 캐시

  useEffect(() => {
    // 캐시 있으면 즉시 MainStack으로 이동 (stale 상태)
    if (cachedSchedule) {
      navigation.replace('AdminTabs');
      // 백그라운드에서 신선한 데이터 재검증
      queryClient.invalidateQueries({ queryKey: ['schedule'] });
    } else {
      // 캐시 없으면 API 기다림
      fetchAndNavigate();
    }
  }, []);
};
```

---

## 4. ux-round1 검토 및 반론

### 4-1. ✅ 전면 동의 — 드래그 Fallback 2탭 이동 모드

ux-round1 §1 시나리오 A 4번이 "한 손 시나리오의 사망 지점"으로 지목했다.  
**드래그&드롭과 2탭 이동 모드를 병행 구현**하고, 기본값은 **2탭 이동 모드**로 한다.

```tsx
// 드래그 fallback — long-press → ActionSheet → 날짜 선택
const DayOffChip = ({ employee, date }) => {
  const [mode, setMode] = useState<'idle' | 'selecting'>('idle');

  const handleLongPress = () => {
    // 2탭 이동 모드 진입
    setMode('selecting');
    // 달력 셀에 "이동 가능" 파란 테두리 표시
    setSelectableMode(employee.id);
  };

  return (
    <Animated.View style={[styles.chip, dragStyle]}>
      <TouchableOpacity
        onLongPress={handleLongPress}    // 2탭 이동 모드 진입
        delayLongPress={300}
        // 드래그 제스처 (선택적)
        onPress={mode === 'selecting' ? undefined : undefined}
        accessibilityLabel={`${employee.name} 휴무. 길게 눌러 날짜 변경`}
      >
        <Text>{employee.name}</Text>
      </TouchableOpacity>
      {mode === 'selecting' && (
        <Text style={styles.hint}>이동할 날짜를 탭하세요</Text>
      )}
    </Animated.View>
  );
};
```

드래그 중 floating preview + 햅틱도 구현한다.

```ts
import ReactNativeHapticFeedback from 'react-native-haptic-feedback';

const onChipDrop = (targetDate: string) => {
  ReactNativeHapticFeedback.trigger('impactMedium'); // 드롭 시 햅틱
  showUndoToast(`${employee.name}의 휴무가 ${targetDate}로 이동됨`, 5000);
};
```

### 4-2. ✅ 동의 — 알림 카테고리별 on/off + Daily Digest

ux-round1 §3이 하루 5~7개 푸시로 인한 "알림 끔" 시나리오를 정확히 짚었다.

```ts
// store/notificationStore.ts
interface NotificationPreferences {
  dailyDigest: boolean;           // true 시 하루 1번 모아서
  categories: {
    dayOffReminder: boolean;      // 쉬기 전날 알림
    dailyWorkSummary: boolean;    // 관리자 당일 근무 현황
    swapRequest: boolean;         // 근무 교환 요청
    dayOffRelocated: boolean;     // 휴무 재배치 결과
  };
  silentHours: {                  // 영업 중 무음
    enabled: boolean;
    start: string;                // "11:00"
    end: string;                  // "14:00"
  };
}
```

Android: `NotificationChannel` 카테고리별 분리  
iOS: `thread-id` + `summary-argument`로 그룹화

```ts
// Android 채널 설정
import PushNotification from 'react-native-push-notification';

PushNotification.createChannel({ 
  channelId: 'day-off-reminder', 
  channelName: '쉬는 날 알림',
  importance: 3
});
PushNotification.createChannel({ 
  channelId: 'swap-request', 
  channelName: '근무 교환',
  importance: 4
});
```

### 4-3. ✅ 동의 — 클라이언트 단 충돌 검증

ux-round1 §6 T1에서 "드래그 도중 매번 API 호출 금지, 클라이언트 단 즉시 계산"을 강하게 요청했다.  
이는 데이터 소모와 UX 모두에서 맞다.

```ts
// hooks/useConflictCheck.ts — 클라이언트 단 충돌 검증
export const useConflictCheck = (minStaff: number, totalEmployees: number) => {
  const checkConflict = useCallback(
    (offMap: Map<string, string[]>) => {
      const conflicts: string[] = [];
      offMap.forEach((employees, date) => {
        const onCount = totalEmployees - employees.length;
        if (onCount < minStaff) conflicts.push(date);
      });
      return conflicts;
    },
    [minStaff, totalEmployees]
  );

  // 서버는 최종 확정 시에만 호출
  const confirmWithServer = useMutation({
    mutationFn: (payload: GenerateScheduleRequest) =>
      api.generateSchedule(payload),
  });

  return { checkConflict, confirmWithServer };
};
```

---

## 5. 크로스-에이전트 통합 이슈

### 5-1. 공통 쟁점: Keychain vs MMKV

- **backend**: Keychain 권장
- **pm**: Keychain 명시
- **frontend (Round 1)**: MMKV로 충분하다고 했지만 → **수정: JWT는 Keychain, 캐시는 MMKV로 분리**

**최종 결정:**
```
JWT (Access/Refresh)  → react-native-keychain (iOS Keychain / Android Keystore)
캐시 (schedule, store, preferences) → react-native-mmkv
오프라인 큐 → react-native-mmkv
```

### 5-2. 공통 쟁점: 매장 모드 (Store Mode) 토글

ux-round1 §5에서 "매장 모드" 개념을 제안했다 (폰트 +1단계, hit area +20%, contrast 강화).  
이를 RN `StyleSheet`에서 구현하려면 토큰 레이어가 필요하다.

```ts
// theme/useAppTheme.ts
export const useAppTheme = () => {
  const isStoreMode = useAppStore((s) => s.isStoreMode);
  const scheme = useColorScheme();

  return {
    ...baseTokens,
    fontSize: {
      xs: isStoreMode ? 13 : 11,
      sm: isStoreMode ? 15 : 13,
      base: isStoreMode ? 17 : 15,
      lg: isStoreMode ? 19 : 17,
      xl: isStoreMode ? 22 : 20,
    },
    minTouchTarget: isStoreMode ? 58 : 48,  // hit area +20%
  };
};
```

→ **design-agent에 질문**: 매장 모드 활성화 시 primary 색상의 고대비 변형 토큰(`--ts-primary-hc`)이 필요하다. sky-500 `#0EA5E9` 기준으로 직사광(야외 3000 lux+) 환경에서 WCAG AA(4.5:1)를 충족하는 고대비 버전 값을 확정해줄 수 있는가?

---

## 6. design-agent에게 공식 질문 (SendMessage 대상)

**질문 내용:**

1. `@gorhom/bottom-sheet` 에서 WorKey BottomSheet 3단 snap (30% / 60% / 92%) 구현 시 각 단계별 `backdropOpacity` 값과 핸들 인디케이터 색상 가이드를 제공해줄 수 있는가?
2. 충돌 칩 드래그 시 BottomSheet가 자동으로 30% 단으로 축소되는 인터랙션 — 이 동작을 디자인 스펙으로 정의해줄 수 있는가? (예: 드래그 시작 이벤트 → `snapToIndex(0)` 자동 호출 여부)
3. **매장 모드(고대비)** 활성화 시 `--ts-primary` 의 고대비 변형 HEX 값과, FAB/CTA 버튼의 그림자(`elevation`, `shadowColor`) 강화 스펙을 제공해줄 수 있는가?
4. DiceBear Lorelei Neutral SVG 30종을 `react-native-svg`로 렌더링하는 `EmployeeAvatar` 컴포넌트 — 아이콘 선택 그리드(30개)의 모바일 레이아웃(열 수, 셀 크기)을 디자인 시스템 기준으로 정의해줄 수 있는가?

---

## 7. backend-agent에게 공식 질문 (SendMessage 대상)

**질문 내용:**

1. **DTO 구조와 React Query 캐싱 호환성**: `ScheduleDetailResponse.entries`가 직원명을 키로 하는 Map 구조 (`{ "김민준": [...], "이수아": [...] }`)인데, React Query의 `queryKey`는 배열 기반이다. 직원 개별 캐시 무효화(예: 특정 직원 휴무만 변경 시)를 지원하려면 entries를 **배열 구조** (`[{ employeeId, entries: [...] }]`)로 변경하거나 별도 엔드포인트(`GET /schedules/{id}/entries?employeeId=`)를 추가하는 것이 가능한가?
2. **Bulk PATCH와 낙관적 업데이트**: `PATCH /stores/{storeId}/schedules/{year}/{month}/entries` 에서 부분 업데이트 후 응답으로 변경된 entries 전체를 다시 반환하는가? 아니면 204 No Content인가? React Query의 낙관적 업데이트(`onMutate`) 후 롤백 처리를 위해 **변경된 entries만 담은 diff 응답**이 필요하다.
3. **휴무 신청 오프라인 큐 idempotency**: `POST /employees/{id}/day-off-requests` 가 같은 직원, 같은 날짜로 중복 요청 시 멱등성을 보장하는가? 오프라인 큐에서 네트워크 복구 후 재시도할 때 중복 신청이 생성되는 리스크를 방지하려면 `Idempotency-Key` 헤더 지원 또는 서버 단 중복 체크가 필요하다.
4. **onboarding-status 응답에 storeId 포함 여부**: 현재 응답에 `storeId`가 포함되어 있어(backend-round1 §1.2) SplashScreen에서 추가 API 없이 매장 정보 fetching이 가능하다 — 이 스펙이 확정인가? STORE_MISSING 상태에서는 `storeId`가 null인가?

---

## 8. Round 2 결론 및 Round 3 준비

### 확정된 기술 결정 사항

| 항목 | Round 1 | Round 2 확정 |
|---|---|---|
| JWT 저장 | MMKV | **react-native-keychain** (Keychain/Keystore) |
| 캐시 저장 | MMKV | MMKV 유지 (비민감 데이터) |
| 오프라인 큐 | MMKV | MMKV 유지 |
| 푸시 권한 요청 | 앱 최초 | **첫 휴무 신청 완료 직후** |
| BottomSheet snap | 단일 % | **30% / 60% / 92% 3단** |
| 생성 확정 위치 | 미확정 | **하단 sticky CTA (헤더 제거)** |
| 드래그 fallback | 미구현 | **long-press → 2탭 이동 모드 (기본값)** |
| FCM 토큰 등록 | POST /me/push-token (오류) | **PATCH /me/fcm-token** |
| 충돌 검증 위치 | 서버 | **클라이언트 단 (서버는 최종 확정만)** |
| CommonResponse | 미처리 | **result[0] 인터셉터 언래핑** |

### Round 3에서 다룰 항목

1. backend-agent의 DTO 구조 변경 응답 수용 여부 결정
2. design-agent의 Dark Mode + 매장 모드 토큰 확정 후 `useAppTheme.ts` 완성
3. FCM NoOp → 실제 발송 일정 확정 후 `usePushNotification` 훅 활성화 전략
4. 딥링크(Universal Links/App Links) 구현 순서 — 도메인 발급 일정과 동기화

---

*Round 2 완료 — design-agent, backend-agent에게 질문 발송 후 Round 3 통합 작성 예정.*
