# [R3-FRONTEND] React Native 앱 구조 — Round 3 최종 종합

> **작성자**: frontend-agent  
> **일시**: 2026-04-29  
> **입력**: backend-round1/2 · design-round1/2 · pm-round1/2 · ux-round1/2 · frontend-round1/2 + 수신 질문 3건

---

## 0. 수신 질문 공식 답변

### [backend → frontend] 질문 3건 답변

#### 답변 1 — FCM 토큰 등록 API 스펙 불일치 → **(A) 프론트가 맞춤**

백엔드 스펙 `PATCH /me/fcm-token { "fcmToken": "..." }` 을 따른다.  
`platform` 필드는 제거한다. FCM 토큰 자체에 플랫폼 정보가 내장되어 있으므로 불필요하다.

```ts
// 수정된 FCM 토큰 등록 코드 (Round 1 오류 수정)
const registerToken = async () => {
  const fcmToken = await messaging().getToken();
  await axiosInstance.patch('/me/fcm-token', { fcmToken }); // { token, platform } → { fcmToken }
};
```

#### 답변 2 — BFF aggregation TanStack Query 캐시 키 전략 → **전략 B (normalize) 채택**

backend-round2 §8 Q2의 권고대로 **전략 B**를 채택한다.  
BFF 응답 수신 시 `queryClient.setQueryData`로 도메인별 캐시 키에 즉시 분배한다.  
이렇게 하면 `schedule` 뮤테이션은 `['schedule']` 키만 무효화하면 되어 불필요한 re-fetch가 없다.

```ts
// hooks/useHomeSummary.ts — BFF + normalize 전략
export const useHomeSummary = () => {
  const queryClient = useQueryClient();
  const storeId = useAuthStore((s) => s.storeId);

  return useQuery({
    queryKey: ['home-summary'],
    queryFn: async () => {
      const data = await api.getHomeSummary(); // GET /me/home-summary

      // normalize: 수신 즉시 개별 도메인 캐시에 분배
      if (data.employees) {
        queryClient.setQueryData(['employees', storeId], data.employees);
      }
      if (data.thisMonthSchedule) {
        queryClient.setQueryData(
          ['schedule', storeId, data.thisMonthSchedule.year, data.thisMonthSchedule.month],
          data.thisMonthSchedule
        );
      }
      if (data.onboardingStatus) {
        useAuthStore.getState().setStatus(data.onboardingStatus);
      }
      return data;
    },
    staleTime: 60 * 1000,    // 1분 (onboarding-status는 no-cache, home-summary는 1분)
    gcTime: 5 * 60 * 1000,
  });
};

// 이후 각 화면은 개별 도메인 캐시만 구독 — BFF 재요청 없이 사용
const { data: employees } = useQuery({ queryKey: ['employees', storeId] });
const { data: schedule }  = useQuery({ queryKey: ['schedule', storeId, year, month] });
```

**BFF 필드 구성 요청사항** (backend-agent에 전달):  
normalize가 용이하도록 응답 필드를 도메인별로 명확히 분리해 달라:  
```json
{
  "role": "ADMIN",
  "onboardingStatus": "COMPLETE",
  "storeId": 42,
  "storeName": "워키 카페",
  "employees": [...],              // ADMIN only, 없으면 null
  "thisMonthSchedule": {...},      // 생성된 경우, 없으면 null
  "pendingDayOffCount": 3,
  "upcomingOff": ["2026-05-10"]    // EMPLOYEE only
}
```

#### 답변 3 — CommonResponse 래퍼 처리 → **(A) Axios interceptor 자동 unwrap**

```ts
// api/client.ts — 자동 unwrap + 단건/복수 자동 감지
axiosInstance.interceptors.response.use((response) => {
  const { success, result } = response.data ?? {};
  if (typeof success === 'boolean' && Array.isArray(result)) {
    // 단건 리소스 (result 길이 1) → 객체로, 목록 → 배열로
    response.data = result.length === 1 ? result[0] : result;
  }
  return response;
}, (error) => {
  // 401 → 토큰 갱신 후 재시도
  if (error.response?.status === 401) return refreshAndRetry(error);
  return Promise.reject(error);
});
```

---

### [design → frontend] 질문 답변

design-round2에서 확정된 스펙을 수용하고 구현에 반영한다.

#### BottomSheet 3단 snap 확정 수용

design-round2 §1.1 확정 스펙을 구현에 적용한다:

```tsx
// 화면별 BottomSheet snap 높이 최종 확정
const SNAP_POINTS = {
  DayOffConflict:  ['60%', '100%'],  // 충돌 상세: 60% 기본 (달력 40% 노출)
  LeaveRequest:    ['100%'],          // 휴무 신청 사유 입력: 풀하이트
  InviteEmployee:  ['35%'],           // 초대 링크: 버튼 2개만
  ShiftSwap:       ['60%', '100%'],   // 근무 교환: 직원 선택 포함
} as const;
```

#### 매장 모드 고대비 토큰 수용

design-round2 §4.3 확정값을 토큰 파일에 반영한다:

```ts
// theme/tokens.ts — design-round2 §4.3 storeModeOverrides 최종 확정
export const storeModeTokens = {
  primary:         '#0369A1',  // sky-700 (고대비, 기존 sky-500 → 대비 8.75:1)
  primarySurface:  '#BAE6FD',  // sky-200
  primary50:       '#E0F2FE',  // sky-100
  calWorkTint:     '#BAE6FD',  // ON/OFF 차이 명확화
  calTodayBg:      '#0369A1',  // 오늘 날짜 배경 (흰 텍스트 대비 8.75:1)
  textPrimary:     '#0C4A6E',  // sky-900
  hitAreaMultiplier: 1.2,
  fontSizeOffset:  2,           // sp 단위 +2
};
```

#### 다크 모드 토큰 확정 수용 (design-round2 §3.1)

```ts
// 앱 내 독립 설정 (시스템 다크 모드 따르지 않음)
export const darkTokens = {
  primary:       '#38BDF8',  // sky-400
  primaryInk:    '#7DD3FC',  // sky-300
  surface:       '#0F172A',  // slate-900
  surfaceCard:   '#1E293B',  // slate-800
  textPrimary:   '#F1F5F9',  // slate-100
  textSecondary: '#94A3B8',  // slate-400
  error:         '#F87171',  // red-400
  border:        '#334155',  // slate-700
  calTodayBg:    '#38BDF8',
};
```

---

### [ux → frontend] Thumb Zone 5문항 답변 (Round 2에서 구두 답변한 내용 공식화)

| # | 질문 | 최종 결정 |
|---|---|---|
| 1 | iOS 22pt + Android 제스처 회피 | `useSafeAreaInsets()` 자동 처리. Tab 콘텐츠 49pt + `insets.bottom` 추가. 별도 처리 불필요 |
| 2 | 매장 모드 59pt 탭 높이 보정 | 스크롤 down → 탭 auto-hide (Reanimated `withTiming`) + `contentContainerStyle.paddingBottom` 동적 조정 |
| 3 | 좌·우손잡이 FAB 반전 | Zustand `handedness: 'left'|'right'` + Reanimated `withSpring` 위치 전환. 온보딩에서 1회 선택 유도 |
| 4 | 활성/비활성 이중 인코딩 | **3중 인코딩 전면 채택**: 색(sky-500/slate-400) + 아이콘 형태(filled/outline) + 라벨 볼드(700/400) |
| 5 | Top Tab 대체 | 전역 네비는 Bottom Tab만. 화면 내 필터는 가로 스크롤 칩(FlatList). 월 전환은 하단 ‹/› + 스와이프 |

---

## 1. 핵심 토픽 1 최종 결론 — 모바일 최적화 API

### 확정 사항

| 항목 | 결론 |
|---|---|
| BFF 엔드포인트 | `GET /me/home-summary` v1.2 **MUST** (PM·UX 강력 요청, 병렬 호출 3건으로 1.5s 보장 불가) |
| 임시 전략 (BFF 완성 전) | `Promise.all` 병렬 호출 + MMKV 캐시 즉시 렌더(stale-while-revalidate) |
| TanStack Query 전략 | staleTime 5분 + normalize 분배(전략 B) |
| TTI KPI | **캐시 히트 ≤ 0.8s / 캐시 미스 ≤ 1.5s** (ux-round2 분리 요구 수용) |
| 스케줄 엔트리 lazy load | `GET /schedules/{id}/entries` 별도 lazy 호출 (entries는 직원 수 × 30일) |

### 구현 전략

```ts
// 1단계: SplashScreen — MMKV 캐시 즉시 렌더 (cold start ≤ 0.3s 목표)
const cachedRole  = storage.getString('userRole');
const cachedStore = storage.getString('lastStoreData');

if (cachedRole && cachedStore) {
  // 캐시 즉시 렌더 (stale 상태)
  navigation.replace(cachedRole === 'ADMIN' ? 'AdminTabs' : 'EmployeeTabs');
  queryClient.invalidateQueries({ queryKey: ['home-summary'] }); // 백그라운드 갱신
} else {
  // 캐시 없음 → 네트워크 대기
  await fetchAndNavigate();
}

// 2단계: home-summary 도착 후 normalize 분배 (위 useHomeSummary 구현 참조)
```

---

## 2. 핵심 토픽 2 최종 결론 — 네이티브 연동

### React Navigation 구조 최종 확정

```
RootNavigator (Stack)
├── SplashScreen            ← Keychain 토큰 확인 + MMKV 캐시 즉시 렌더
├── AuthStack (Stack)
│   ├── KakaoLoginScreen
│   └── OnboardingStack (Stack)
│       ├── RoleSelectScreen          (케이스 1·2 진입점)
│       ├── StoreRegisterScreen       (케이스 1 — MUST)
│       ├── LinkCheckScreen           (케이스 2)
│       ├── WelcomeScreen             (케이스 3 — MUST, 딥링크 진입)
│       ├── StoreSwitchScreen         (케이스 5)
│       └── DismissedScreen           (케이스 4)
└── MainStack (Stack)
    ├── AdminTabs (BottomTabNavigator)    ← 아이콘 3중 인코딩
    │   ├── DashboardScreen
    │   ├── EmployeeScreen
    │   ├── ScheduleScreen
    │   └── SettingsScreen
    ├── EmployeeTabs (BottomTabNavigator)
    │   ├── MyScheduleScreen
    │   ├── LeaveRequestScreen
    │   └── ShiftSwapScreen
    └── Modal Group (presentation: 'modal')
        ├── InviteBottomSheet        ← snap 35%
        ├── DayOffConflictSheet      ← snap 60%/100%
        ├── LeaveRequestSheet        ← snap 100%
        ├── ShiftSwapSheet           ← snap 60%/100%
        └── ExportModal
```

### 로컬 스토리지 최종 결정

```
민감 정보 (JWT)  → react-native-keychain   [iOS Keychain / Android Keystore]
비민감 캐시      → react-native-mmkv        [AES-256 암호화 옵션]
오프라인 큐      → react-native-mmkv
앱 설정/선호     → react-native-mmkv (persist)
```

```ts
// utils/secureStorage.ts — 최종 확정
import * as Keychain from 'react-native-keychain';
import { MMKV } from 'react-native-mmkv';

// JWT 전용
export const secureToken = {
  set: (access: string, refresh: string) =>
    Keychain.setInternetCredentials('workey.app', 'tokens',
      JSON.stringify({ access, refresh })),
  get: async () => {
    const c = await Keychain.getInternetCredentials('workey.app');
    return c ? JSON.parse(c.password) : null;
  },
  clear: () => Keychain.resetInternetCredentials('workey.app'),
};

// 캐시/설정 전용
export const storage = new MMKV({ id: 'workey-cache', encryptionKey: process.env.MMKV_KEY });
```

### FCM/APNs 최종 통합

```ts
// hooks/usePushNotification.ts — 최종 확정
export const usePushNotification = () => {
  // 타이밍: 첫 휴무 신청 완료 직후 (pm·ux 공통 동의)
  const requestPermissionOnFirstLeave = useCallback(async () => {
    const status = await messaging().requestPermission();
    if (status === messaging.AuthorizationStatus.AUTHORIZED) {
      const fcmToken = await messaging().getToken();
      await axiosInstance.patch('/me/fcm-token', { fcmToken }); // 확정 스펙
    }
  }, []);

  // 포그라운드 메시지 → 인앱 토스트 (design-round2 §T2 스펙 적용)
  useEffect(() => {
    const unsubscribe = messaging().onMessage(async (msg) => {
      const type = msg.data?.type as string;
      showInAppToast(msg.notification, type);
    });

    // 토큰 갱신 이벤트
    const unsubRefresh = messaging().onTokenRefresh(async (newToken) => {
      await axiosInstance.patch('/me/fcm-token', { fcmToken: newToken });
    });

    return () => { unsubscribe(); unsubRefresh(); };
  }, []);

  return { requestPermissionOnFirstLeave };
};

// 알림 카테고리별 설정 (ux-round2 알림 피로도 반영)
const notificationPrefs: NotificationPrefs = {
  dailyDigest: false,
  categories: {
    dayOffReminder: true,
    dailyWorkSummary: true,
    swapRequest: true,
    dayOffRelocated: true,
  },
  silentHours: { enabled: false, start: '11:00', end: '14:00' },
};
```

---

## 3. 핵심 토픽 3 최종 결론 — 디자인 이식

### BottomSheet 최종 구현

```tsx
// components/WorkeyBottomSheet.tsx — Round 3 최종 확정
import BottomSheet, { BottomSheetView, BottomSheetBackdrop } from '@gorhom/bottom-sheet';

const WorkeyBottomSheet = ({ children, snapPoints, initialIndex = 0, onClose }) => (
  <BottomSheet
    snapPoints={snapPoints}
    index={initialIndex}
    onClose={onClose}
    backdropComponent={(props) => (
      <BottomSheetBackdrop
        {...props}
        appearsOnIndex={0}
        disappearsOnIndex={-1}
        opacity={0.4}               // design-round2 확정값
      />
    )}
    handleStyle={{ height: 24, paddingTop: 10 }}   // 터치 영역 44pt 확보
    handleIndicatorStyle={{
      width: 40,                    // design-round2: ≥40dp (대비 문제로 #0369A1 사용)
      height: 4,
      backgroundColor: '#0369A1',  // sky-700 on white: 8.75:1 ✅ (sky-300 2.1:1 수정)
    }}
    backgroundStyle={{
      backgroundColor: tokens.surface,
      borderTopLeftRadius: 20,
      borderTopRightRadius: 20,
    }}
    style={{ paddingHorizontal: 20 }}
  >
    <BottomSheetView style={{ paddingBottom: insets.bottom + 16 }}>
      {children}
    </BottomSheetView>
  </BottomSheet>
);
```

### 드래그 Fallback — Long-press 2탭 이동 모드 (기본값)

ux-round1 PP-1 + design-round2 §4.1 통합 구현:

```tsx
// components/DayOffChip.tsx — 드래그 + 2탭 fallback 병행
const DayOffChip = ({ employee, date, onRelocate }) => {
  const [selecting, setSelecting] = useState(false);

  return (
    <>
      <TouchableOpacity
        onLongPress={() => {
          setSelecting(true);
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
        }}
        delayLongPress={300}
        style={[styles.chip, selecting && styles.chipSelected]}
        accessibilityLabel={`${employee.name} 휴무 ${date}. 길게 눌러 날짜 변경`}
      >
        <Text>{employee.name}</Text>
      </TouchableOpacity>

      {/* Long-press 후 컨텍스트 메뉴 */}
      {selecting && (
        <ContextMenu onSelect={(action) => {
          if (action === 'relocate') {
            // 달력 셀 선택 모드 진입
            setSelectableMode(employee.id);
          }
          setSelecting(false);
        }}>
          <MenuItem icon="📅" label="다른 날로 옮기기" value="relocate" />
          <MenuItem icon="✕" label="취소" value="cancel" />
        </ContextMenu>
      )}
    </>
  );
};

// 드롭 완료 후 Undo 토스트 (design-round2 §1.3 스펙)
const showUndoToast = (from: string, to: string) => {
  toast.show(`${from} → ${to}로 이동되었어요`, {
    duration: 5000,
    action: { label: '되돌리기', onPress: undoLastRelocate },
    backgroundColor: '#0C4A6E',   // sky-900
  });
  Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
};
```

### 디자인 토큰 최종 파일

```ts
// theme/tokens.ts — Round 3 최종 (라이트 / 다크 / 매장 모드 3종)
export const lightTokens = {
  primary:       '#0EA5E9',   // sky-500
  primaryInk:    '#0369A1',   // sky-700
  primarySoft:   '#7DD3FC',   // sky-300
  primary50:     '#F0F9FF',   // sky-50
  primary100:    '#E0F2FE',   // sky-100
  primarySurface:'#E0F2FE',
  surface:       '#FFFFFF',
  surfaceCard:   '#E0F2FE',
  textPrimary:   '#1E293B',
  textSecondary: '#64748B',
  error:         '#EF4444',
  border:        '#E2E8F0',
  calTodayBg:    '#0369A1',   // sky-700 (design-round2 §4.5 수정: 2.9→8.75:1)
  calWorkTint:   '#E0F9FF',
  minTouchTarget: 48,
};

// 다크 모드 (앱 내 독립 설정)
export const darkTokens = { ...lightTokens,
  primary:       '#38BDF8',
  primaryInk:    '#7DD3FC',
  surface:       '#0F172A',
  surfaceCard:   '#1E293B',
  textPrimary:   '#F1F5F9',
  textSecondary: '#94A3B8',
  error:         '#F87171',
  border:        '#334155',
  calTodayBg:    '#38BDF8',
};

// 매장 모드 (고대비 + 큰 글씨 + 큰 터치)
export const storeModeTokens = { ...lightTokens,
  primary:       '#0369A1',   // sky-700 (직사광 대비 8.75:1)
  primarySurface:'#BAE6FD',   // sky-200
  primary50:     '#E0F2FE',
  calWorkTint:   '#BAE6FD',
  textPrimary:   '#0C4A6E',   // sky-900
  minTouchTarget: 58,          // 48 × 1.2
};

// 사용
export const useTokens = () => {
  const { colorMode, isStoreMode } = useAppStore();
  if (isStoreMode) return storeModeTokens;
  return colorMode === 'dark' ? darkTokens : lightTokens;
};
```

---

## 4. 핵심 토픽 4 최종 결론 — 사용자 환경 (최기준 페르소나)

### ux-round2가 추가한 두 번째 시나리오 공식 채택

PM의 "출근길 06:30 지하철 15분"과 UX의 "매장 영업 중 30초 자투리" 두 시나리오 **모두** 합격 기준으로 채택한다.

| 시나리오 | 환경 | 합격 기준 |
|---|---|---|
| A (출근길 지하철) | 한 손 음료, 지하철, 15분 | 스케줄 생성 완전 완료 ≤ 15분 |
| B (매장 영업 중) | 카운터, 형광등, 30초 자투리, 손 젖음 | TTI ≤ 0.8s + 단일 액션(휴무 신청 등) 3탭 이내 |

### Tab Bar 최종 결정

```tsx
// navigation/AdminTabNavigator.tsx — 3중 인코딩 최종 구현
<Tab.Navigator
  tabBar={(props) => <WorkeyTabBar {...props} />}
  screenOptions={({ route }) => ({
    tabBarIcon: ({ focused, color }) => {
      const icons = {
        Dashboard: focused ? DashboardFilled : DashboardOutline,
        Employees: focused ? TeamFilled    : TeamOutline,
        Schedule:  focused ? CalFilled     : CalOutline,
        Settings:  focused ? GearFilled    : GearOutline,
      };
      const Icon = icons[route.name];
      return <Icon size={24} color={color} />;
    },
    tabBarLabel: ({ focused, children }) => (
      <Text style={{
        fontSize: 10,
        color: focused ? tokens.primary : '#94A3B8',
        fontWeight: focused ? '700' : '400',   // 3중: 라벨 볼드
      }}>
        {children}
      </Text>
    ),
    tabBarActiveTintColor:   '#0EA5E9',   // sky-500
    tabBarInactiveTintColor: '#94A3B8',   // slate-400
    tabBarStyle: {
      height: 49 + insets.bottom,
      paddingBottom: insets.bottom,
    },
  })}
/>
```

### FAB + 손잡이 토글

```tsx
// components/FAB.tsx — 최종 구현
const FAB = ({ onPress, icon, style }) => {
  const handedness = useAppStore((s) => s.handedness);
  const isStoreMode = useAppStore((s) => s.isStoreMode);
  const insets = useSafeAreaInsets();

  const SIZE = isStoreMode ? 67 : 56;  // 매장 모드 +20%
  const BOTTOM = insets.bottom + 72;   // 탭 바 위

  const positionStyle = handedness === 'right'
    ? { right: 16 }
    : { left: 16 };

  return (
    <Animated.View style={[{
      position: 'absolute',
      bottom: BOTTOM,
      width: SIZE, height: SIZE, borderRadius: SIZE / 2,
      backgroundColor: tokens.primary,
      elevation: 6,
      shadowColor: '#000', shadowOffset: { width: 0, height: 3 },
      shadowOpacity: 0.3, shadowRadius: 4,
    }, positionStyle, style]}>
      <TouchableOpacity
        onPress={onPress}
        style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}
        hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
        accessibilityRole="button"
      >
        {icon}
      </TouchableOpacity>
    </Animated.View>
  );
};
```

---

## 5. 오프라인 큐 최종 전략

```ts
// utils/offlineQueue.ts — idempotency key 포함 (backend-round2 §2.5 반영)
import { v4 as uuidv4 } from 'uuid';

interface QueuedMutation {
  id: string;                         // idempotency key
  endpoint: string;
  method: 'POST' | 'PATCH' | 'DELETE';
  body: unknown;
  createdAt: number;
}

export const offlineQueue = {
  enqueue: (mutation: Omit<QueuedMutation, 'id'>) => {
    const queue = getQueue();
    const item = { ...mutation, id: uuidv4() };  // UUID idempotency key
    storage.set('offlineQueue', JSON.stringify([...queue, item]));
  },
  flush: async () => {
    const queue = getQueue();
    const failed: QueuedMutation[] = [];
    for (const item of queue) {
      try {
        await axiosInstance.request({
          url: item.endpoint,
          method: item.method,
          data: item.body,
          headers: { 'X-Idempotency-Key': item.id }, // 중복 방지
        });
      } catch {
        failed.push(item);
      }
    }
    storage.set('offlineQueue', JSON.stringify(failed));
  },
};

// 오프라인 대응 범위 (최종 결정)
// ✅ 큐 적재: 휴무 신청, 근무 교환 요청
// ❌ 오프라인 차단 + 토스트: 스케줄 생성, 스케줄 수동 조정 (서버 연산 필수)
```

---

## 6. 전체 3라운드 기술 결정 최종 확정표

| 항목 | Round 1 | Round 2 수정 | Round 3 최종 |
|---|---|---|---|
| **JWT 저장** | MMKV | react-native-keychain | **Keychain/Keystore 확정** |
| **캐시 저장** | MMKV | MMKV 유지 | MMKV (비민감 데이터) |
| **FCM 토큰 API** | `POST /me/push-token { token, platform }` | `PATCH /me/fcm-token` | **`PATCH /me/fcm-token { fcmToken }` 확정** |
| **푸시 권한 시점** | 앱 최초 | 첫 휴무 신청 후 | **첫 휴무 신청 완료 직후 확정** |
| **BFF 엔드포인트** | 미확정 | v1.2 SHOULD | **v1.2 MUST (PM 승격)** |
| **TanStack Query** | 캐시 전략 미정 | normalize 전략 B | **전략 B(normalize 분배) 확정** |
| **CommonResponse** | 미처리 | interceptor 언래핑 | **Axios interceptor (A안) 확정** |
| **BottomSheet snap** | 미확정 | 3단 제안 | **30%→35% / 60% / 100% 화면별 확정** |
| **핸들 바 색상** | `#7DD3FC` (2.1:1 ❌) | 문제 인식 | **`#0369A1` (8.75:1) ✅ 확정** |
| **오늘 날짜 배경** | `#0EA5E9` (2.9:1 ❌) | 수정 권고 | **`#0369A1` (8.75:1) ✅ 확정** |
| **Dark Mode** | 미대응 | 토큰 제안 | **앱 내 독립 설정 확정, 토큰 확정** |
| **매장 모드** | 미구현 | 고대비 토큰 신설 | **3종 토큰셋(라이트/다크/매장) 확정** |
| **생성 확정 위치** | 헤더 우측 | 하단 이동 권고 | **하단 full-width sticky 확정** |
| **드래그 fallback** | 미구현 | 2탭 이동 모드 | **long-press → 컨텍스트 메뉴 → 달력 1탭 확정** |
| **충돌 검증 위치** | 미확정 | 클라이언트 권고 | **클라이언트 즉시 계산, 서버 최종만 확정** |
| **Tab Bar 인코딩** | 색 단독 | 이중 인코딩 제안 | **3중(색+형태+라벨볼드) 확정** |
| **좌우손잡이** | 미구현 | FAB 반전 패턴 | **Zustand handedness + Reanimated 확정** |
| **TTI KPI** | 단일 1.5s | 분리 요구 | **캐시hit ≤0.8s / 캐시miss ≤1.5s 확정** |
| **오프라인 큐 idempotency** | UUID 미포함 | X-Idempotency-Key 요청 | **UUID v4 `X-Idempotency-Key` 헤더 확정** |
| **알림 설정** | 카테고리 on/off | 묶음 설계 | **카테고리별 + dailyDigest + silentHours 확정** |

---

## 7. 라이브러리 최종 목록

| 역할 | 라이브러리 | 버전 | 확정 근거 |
|---|---|---|---|
| 네비게이션 | `@react-navigation/native` + bottom-tabs + stack | v7 | RN 표준 |
| 서버 상태 | `@tanstack/react-query` | v5 | normalize 전략 B 적합 |
| 전역 상태 | `zustand` + `immer` | v5 | handedness, colorMode, storeMode |
| 안전한 토큰 저장 | `react-native-keychain` | v9 | Keychain/Keystore |
| 일반 캐시 | `react-native-mmkv` | v3 | 동기 I/O, 오프라인 큐 |
| 영역 처리 | `react-native-safe-area-context` | v4 | Tab + BottomSheet insets |
| BottomSheet | `@gorhom/bottom-sheet` | v5 | Reanimated 3 성능 |
| 제스처 | `react-native-gesture-handler` | v2 | 드래그&드롭 |
| 애니메이션 | `react-native-reanimated` | v3 | FAB 전환, 탭 auto-hide |
| 햅틱 | `expo-haptics` | latest | 드래그/드롭 피드백 |
| 푸시 알림 | `@react-native-firebase/messaging` | v21 | FCM + APNs 통합 |
| 네트워크 감지 | `@react-native-community/netinfo` | v11 | 오프라인 큐 trigger |
| 캘린더 | `react-native-calendars` | v1.13 | 달력 커스터마이징 |
| SVG 렌더 | `react-native-svg` | v15 | DiceBear 아바타 |
| 카카오 공유 | `@react-native-kakao/share` | 공식 | 초대 링크 Feed 템플릿 |
| UUID | `uuid` | v9 | idempotency key |

---

## 8. v1.2 MVP 출시 전 Frontend 체크리스트

### MUST (미완료 시 출시 차단)

- [ ] React Navigation 5레이어 구조 완성 + 온보딩 5케이스 분기
- [ ] `react-native-keychain` JWT 저장 (AsyncStorage 평문 사용 0건)
- [ ] `PATCH /me/fcm-token { fcmToken }` 연동 + 첫 휴무 신청 후 권한 요청
- [ ] BottomSheet 4종 (초대·충돌·휴무신청·근무교환) 디자인 토큰 1:1 검수 통과
- [ ] 생성 확정 버튼 하단 full-width sticky (헤더 버튼 0개)
- [ ] 드래그 fallback (long-press → 2탭 이동) 구현
- [ ] 3중 인코딩 Tab Bar (색+형태+볼드)
- [ ] 매장 모드 토큰셋 + 설정 화면 토글
- [ ] 오프라인 큐 (휴무 신청, 근무 교환) + `X-Idempotency-Key`
- [ ] TTI ≤ 0.8s (캐시 히트) / ≤ 1.5s (캐시 미스) 성능 달성
- [ ] Phase 999 완료 후 JWT Authorization 헤더 interceptor 활성화

### SHOULD (출시 4주 내 fast-follow)

- [ ] `GET /me/home-summary` BFF 연동 + normalize 전략 B 적용
- [ ] Dark Mode 독립 설정 화면
- [ ] 딥링크 Universal Links / App Links + deferred deep link
- [ ] DiceBear SVG 30종 번들 + EmployeeAvatar 선택 그리드
- [ ] 알림 카테고리별 on/off + dailyDigest + silentHours 설정 UI
- [ ] 스케줄 생성 로딩 (design-round2 §2 스펙: 풀스크린 오버레이 + 10초 타임아웃)

---

## 9. 미해결 의존성 (타 팀 액션 필요)

| 항목 | 담당 | 기다리는 것 |
|---|---|---|
| FCM NoOp → 실제 발송 | backend | v1.2 FCM Firebase SDK 연동 일정 확정 |
| `GET /me/home-summary` BFF | backend | 응답 스펙 확정 + 구현 |
| `GET /invite/{token}/preview` | backend | 딥링크 환영 화면용 공개 API |
| `PATCH /me/notification-preferences` | backend | 알림 설정 저장 API |
| 매장 모드 라이트 고대비 vs 다크 고대비 결정 | design + ux | ux-round2 §회신 대기 (시각 피로도 현장 검증) |
| Phase 999 (관리자 API JWT 인가) | backend | 완료 시점 확정 — 미완료 시 prd 배포 불가 |

---

*Round 3 완료. frontend-agent 최종 입장: 3라운드에 걸쳐 결정된 모든 기술 스펙은 위 §6 확정표에 따라 구현하며, 의존성 §9의 타 팀 액션 완료를 전제로 v1.2 MVP 출시를 진행한다.*
