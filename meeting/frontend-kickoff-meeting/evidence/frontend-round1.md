# [R1-FRONTEND] React Native 앱 구조 설계 — Round 1

> **작성자**: frontend-agent  
> **일시**: 2026-04-29  
> **참조**: `docs/WorKey - 프론트엔드.md`, `docs/WorKey - 기획서.md`, `docs/WorKey - 디자인.md`, `docs/WorKey - 백엔드.md`

---

## 0. 요약

WorKey 모바일 앱은 **관리자 / 직원** 두 역할이 동일 앱 안에서 분기되는 구조다.  
백엔드 v1.1이 완료된 상태에서 화면(프론트엔드)만 남아있으므로, 이번 라운드에서는 **React Navigation 구조 / 상태 관리 / 네이티브 연동 / 디자인 이식 / 오프라인 대응** 5개 축을 중심으로 구현 전략을 제시한다.

---

## 1. 핵심 토픽 1 — 모바일 최적화 API 전략

### 1-1. 초기 로딩 최소화 — 온보딩 상태 단일 엔드포인트

앱 최초 진입 시 `GET /me/onboarding-status` **한 번의 호출**로 케이스 1~5를 분기한다.  
이 응답값(`STORE_MISSING | INVITE_PENDING | STORE_CONFLICT | COMPLETE`)을 Zustand 전역 스토어에 캐싱해 Navigation 라우터가 읽도록 구성한다.

```ts
// store/authStore.ts
import { create } from 'zustand';

type OnboardingStatus =
  | 'STORE_MISSING'
  | 'INVITE_PENDING'
  | 'STORE_CONFLICT'
  | 'COMPLETE';

interface AuthState {
  status: OnboardingStatus | null;
  role: 'ADMIN' | 'EMPLOYEE' | null;
  setStatus: (s: OnboardingStatus) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  status: null,
  role: null,
  setStatus: (status) => set({ status }),
}));
```

### 1-2. 대시보드 합산 API 요청 — 백엔드에 요구 사항 전달 예정

현재 관리자 대시보드는 다음 API를 개별 호출한다.

| 화면 요소 | 현재 API |
|---|---|
| 이번 달 스케줄 요약 | `GET /stores/{id}/schedules/{year}/{month}` |
| 직원 목록 | `GET /stores/{id}/employees` |
| StoreHoliday | `GET /stores/{id}/closed-days` |

> **backend-agent에 요청 예정**: 대시보드 초기 진입 시 세 API를 하나로 묶은 `GET /stores/{id}/dashboard-summary` (또는 `?include=schedule,employees,holidays` 쿼리 파라미터) 방식을 검토해달라. 모바일 네트워크 비용 절감 목적.

### 1-3. TanStack Query 캐시 전략

```ts
// 직원 목록: 5분 캐시, 백그라운드 자동 갱신
useQuery({
  queryKey: ['employees', storeId],
  queryFn: () => api.getEmployees(storeId),
  staleTime: 5 * 60 * 1000,
  gcTime: 10 * 60 * 1000,
});

// 스케줄: 생성/수정 뮤테이션 후 즉시 무효화
useMutation({
  mutationFn: api.generateSchedule,
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['schedule'] }),
});
```

---

## 2. 핵심 토픽 2 — 네이티브 연동 전략

### 2-1. React Navigation 구조 (Stack / Tab / Modal)

```
RootNavigator (Stack)
├── SplashScreen          ← MMKV 토큰 확인 → 분기
├── AuthStack (Stack)
│   ├── KakaoLoginScreen
│   └── OnboardingStack (Stack)
│       ├── RoleSelectScreen          (케이스 1·2 진입점)
│       ├── StoreRegisterScreen       (케이스 1)
│       ├── LinkCheckScreen           (케이스 2)
│       ├── WelcomeScreen             (케이스 3)
│       ├── StoreSwitchScreen         (케이스 5)
│       └── DismissedScreen           (케이스 4)
└── MainStack (Stack)
    ├── AdminTabs (BottomTabNavigator)
    │   ├── DashboardScreen
    │   ├── EmployeeScreen
    │   ├── ScheduleScreen
    │   └── SettingsScreen
    ├── EmployeeTabs (BottomTabNavigator)
    │   ├── MyScheduleScreen
    │   ├── LeaveRequestScreen
    │   └── ShiftSwapScreen
    └── Modal Group (presentation: 'modal')
        ├── EmployeeDetailModal
        ├── InviteBottomSheet        ← gorhom/bottom-sheet
        ├── LeaveRequestSheet
        ├── DayOffConflictSheet      ← 휴무 수집 뷰 충돌 바텀시트
        └── ExportModal
```

**분기 로직 (SplashScreen)**

```ts
// screens/SplashScreen.tsx
const SplashScreen = () => {
  const token = useMMKVString('accessToken');
  const navigation = useNavigation<RootNavigationProp>();

  useEffect(() => {
    (async () => {
      if (!token) {
        navigation.replace('AuthStack');
        return;
      }
      const { status, role } = await api.getOnboardingStatus();
      useAuthStore.getState().setStatus(status);
      if (status !== 'COMPLETE') {
        navigation.replace('OnboardingStack', { status });
      } else {
        navigation.replace(role === 'ADMIN' ? 'AdminTabs' : 'EmployeeTabs');
      }
    })();
  }, []);

  return <ActivityIndicator />;
};
```

### 2-2. FCM / APNs 푸시 알림 통합

백엔드 `NoOpNotificationAdapter` → v1.2에서 Firebase SDK 연동 예정.  
프론트엔드는 **지금부터 FCM 토큰 등록 흐름을 구현**해 두어야 백엔드 연동 시 추가 작업이 최소화된다.

```ts
// hooks/usePushNotification.ts
import messaging from '@react-native-firebase/messaging';
import { api } from '../api';

export const usePushNotification = () => {
  useEffect(() => {
    const registerToken = async () => {
      const authStatus = await messaging().requestPermission();
      if (authStatus === messaging.AuthorizationStatus.AUTHORIZED) {
        const fcmToken = await messaging().getToken();
        await api.registerPushToken({ token: fcmToken, platform: Platform.OS });
      }
    };
    registerToken();

    // 포그라운드 메시지 핸들러
    const unsubscribe = messaging().onMessage(async (remoteMessage) => {
      // 인앱 알림 토스트 표시
      showInAppNotification(remoteMessage.notification);
    });
    return unsubscribe;
  }, []);
};
```

**알림 종류 (v1.2 준비)**

| 알림 | 트리거 | 수신자 |
|---|---|---|
| 쉬기 전날 알림 | 저녁 20:00 스케줄러 | 직원 |
| 관리자 당일 근무 현황 | 오전 7:00 스케줄러 | 관리자 |
| 휴무 재배치 결과 | 드래그&드롭 확정 시 | 직원 |
| 근무 교환 요청/승인/거절 | 각 액션 시 | 요청자·수락자 |

### 2-3. 로컬 스토리지 — AsyncStorage vs MMKV 비교

| 항목 | AsyncStorage | MMKV |
|---|---|---|
| 성능 | 비동기 I/O, 느림 | 동기 가능, 10~100배 빠름 |
| 암호화 | ❌ | ✅ (AES-256) |
| RN 공식 지원 | ✅ | react-native-mmkv |
| 주 용도 | 대용량 JSON 저장 | 토큰·설정·작은 상태 |

**결정: MMKV 채택 (주 저장소)**

```ts
import { MMKV } from 'react-native-mmkv';
export const storage = new MMKV({ id: 'workey-store', encryptionKey: 'ENV_KEY' });

// 토큰 저장
storage.set('accessToken', token);
storage.set('refreshToken', refreshToken);

// Zustand 영속화 (zustand/middleware의 persist)
import { persist, createJSONStorage } from 'zustand/middleware';

const mmkvStorage = {
  getItem: (name: string) => storage.getString(name) ?? null,
  setItem: (name: string, value: string) => storage.set(name, value),
  removeItem: (name: string) => storage.delete(name),
};
```

---

## 3. 핵심 토픽 3 — 디자인 이식 (모바일 컴포넌트 & 디자인 토큰)

### 3-1. BottomSheet 라이브러리 선택 — `@gorhom/bottom-sheet`

| 후보 | 장점 | 단점 |
|---|---|---|
| `@gorhom/bottom-sheet` v5 | Reanimated 3 기반, 성능 최상, snap points 유연 | 약간의 setup 복잡도 |
| `react-native-bottom-sheet` (별도 패키지들) | 간단 | 성능·유지보수 열위 |
| `@gorhom/bottom-sheet` | **채택** | — |

**직원 초대 바텀시트 구현 예시**

```tsx
// components/InviteBottomSheet.tsx
import BottomSheet, { BottomSheetView } from '@gorhom/bottom-sheet';

const InviteBottomSheet = ({ employeeId, onClose }) => {
  const snapPoints = useMemo(() => ['35%'], []);

  return (
    <BottomSheet
      snapPoints={snapPoints}
      onClose={onClose}
      backgroundStyle={{ backgroundColor: tokens.surface }}
      handleIndicatorStyle={{ backgroundColor: tokens.border }}
    >
      <BottomSheetView style={styles.container}>
        <TouchableOpacity
          style={[styles.primaryBtn, { backgroundColor: tokens.primary }]}
          onPress={handleKakaoShare}
          accessibilityLabel="카카오톡으로 초대 링크 보내기"
        >
          <Text style={{ color: '#fff' }}>💬 카카오톡으로 보내기</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.secondaryBtn, { borderColor: tokens.primaryInk }]}
          onPress={handleCopyLink}
        >
          <Text style={{ color: tokens.primaryInk }}>🔗 링크 복사</Text>
        </TouchableOpacity>
      </BottomSheetView>
    </BottomSheet>
  );
};
```

### 3-2. 디자인 토큰 RN 매핑

디자인 문서의 CSS 변수를 RN StyleSheet 상수로 1:1 매핑한다.

```ts
// theme/tokens.ts
export const tokens = {
  // Primary (sky-500 계열)
  primary: '#0EA5E9',        // --ts-primary
  primaryInk: '#0369A1',     // --ts-primary-ink
  primarySoft: '#7DD3FC',    // --ts-primary-soft
  primary50: '#F0F9FF',      // --ts-primary-50
  primary100: '#E0F2FE',     // --ts-primary-100 / surface
  primaryInkDark: '#0369A1', // --ts-primary-ink-dark
  primaryInkDeep: '#0C4A6E', // --ts-primary-ink-deep

  // 캘린더 전용
  calTodayBg: '#0EA5E9',     // --ts-cal-today-bg
  calWorkTint: '#E0F9FF',    // --ts-cal-work-tint
  blobSky: '#7DD3FC',        // --ts-blob-sky

  // 공통 시맨틱
  surface: '#FFFFFF',
  background: '#F0F9FF',
  border: '#E0F2FE',
  error: '#EF4444',          // 충돌 날짜 빨간 강조
  warning: '#F59E0B',
};
```

### 3-3. 터치 타겟 크기 기준 (iOS HIG / Android MD3)

- **최소 터치 타겟**: 44×44pt (iOS) / 48×48dp (Android) — 둘 다 충족 시 `minHeight: 48` 적용
- 캘린더 날짜 셀: `width: 44, height: 44` 보장
- 직원 칩 (드래그 대상): `paddingHorizontal: 12, paddingVertical: 10` → 실 타겟 ≥ 44pt

---

## 4. 핵심 토픽 4 — 사용자 환경 (최기준 페르소나: 한 손 사용성)

> "바쁜 근무 현장에서 점장님이 한 손으로 일정 등록을 마칠 수 있는가?"

### 4-1. 엄지 존 (Thumb Zone) 설계 원칙

```
┌──────────────┐
│   위험 구역   │  ← 네비게이션 탭, 뒤로가기만 배치
│              │
│   보통 구역   │  ← 캘린더, 직원 목록
│              │
│  편한 구역 ▼  │  ← 주요 액션 버튼 (FAB, 생성 확정)
└──────────────┘
```

- **FAB(Floating Action Button)**: `position: 'absolute', bottom: 24, right: 24` — 오른손 엄지 도달 구역
- **생성 확정 버튼**: 하단 고정 바 (`SafeAreaView` 안쪽), 전체 너비 버튼

### 4-2. 스케줄 생성 최소 탭 수 목표

| 작업 | 목표 탭 수 | 구현 방법 |
|---|---|---|
| 스케줄 생성 진입 | 2탭 | 대시보드 FAB → 조건 확인 |
| 직원 추가 | 3탭 | 직원탭 → + → 이름 입력 완료 |
| 휴무 수동 추가 | 4탭 | 휴무수집 → + 수동추가 → 직원선택 → 날짜선택 |
| 초대 링크 전송 | 3탭 | 직원상세 → 초대하기 → 카카오톡 전송 |

### 4-3. 접근성 (한 손 모드 대응)

```tsx
// 드래그 불가 환경 대비: 충돌 날짜에 탭으로 날짜 이동 가능한 대체 UI 제공
const DayOffChip = ({ employee, date, onRelocate }) => (
  <TouchableOpacity
    onPress={() => openRelocatePicker(employee, date)}
    onLongPress={() => startDrag(employee, date)}
    accessibilityLabel={`${employee.name} 휴무 날짜 변경`}
    accessibilityHint="길게 누르면 드래그, 짧게 누르면 날짜 선택"
    style={styles.chip}
  >
    <Text>{employee.emoji} {employee.name}</Text>
  </TouchableOpacity>
);
```

---

## 5. 오프라인 큐잉 & 네트워크 회복

### 5-1. NetInfo 기반 네트워크 상태 감지

```ts
// hooks/useNetworkStatus.ts
import NetInfo from '@react-native-community/netinfo';

export const useNetworkStatus = () => {
  const [isConnected, setConnected] = useState(true);

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state) => {
      setConnected(!!state.isConnected && !!state.isInternetReachable);
    });
    return unsubscribe;
  }, []);

  return { isConnected };
};
```

### 5-2. 오프라인 큐 — TanStack Query + MMKV

```ts
// 뮤테이션 실패 시 MMKV 큐에 적재 후 네트워크 복구 시 재시도
const offlineQueue = {
  enqueue: (mutation: QueuedMutation) => {
    const queue = JSON.parse(storage.getString('offlineQueue') ?? '[]');
    storage.set('offlineQueue', JSON.stringify([...queue, mutation]));
  },
  flush: async () => {
    const queue: QueuedMutation[] = JSON.parse(
      storage.getString('offlineQueue') ?? '[]'
    );
    for (const item of queue) {
      await api.replay(item);
    }
    storage.delete('offlineQueue');
  },
};

// NetInfo 복구 이벤트에서 flush 호출
NetInfo.addEventListener((state) => {
  if (state.isConnected) offlineQueue.flush();
});
```

> **오프라인 대응 범위**: 휴무 신청, 근무 교환 요청 — 네트워크 단절 시 큐에 적재.  
> 스케줄 자동 생성은 서버 연산이 필요하므로 오프라인 차단 + 토스트 안내.

---

## 6. 상태 관리 아키텍처 요약

```
┌────────────────────────────────────────────────┐
│             전역 상태 (Zustand)                  │
│  authStore: 토큰, 역할, 온보딩 상태               │
│  storeStore: 현재 매장 정보                      │
└─────────────────┬──────────────────────────────┘
                  │
┌─────────────────▼──────────────────────────────┐
│         서버 상태 (TanStack Query)               │
│  employees, schedules, dayOffRequests,          │
│  swapRequests, storeHolidays                    │
└─────────────────┬──────────────────────────────┘
                  │
┌─────────────────▼──────────────────────────────┐
│          영속 저장소 (MMKV)                      │
│  accessToken, refreshToken, settings,           │
│  offlineQueue, onboardingStatus                 │
└────────────────────────────────────────────────┘
```

---

## 7. 핵심 라이브러리 후보 목록

| 역할 | 라이브러리 | 버전 기준 | 선택 이유 |
|---|---|---|---|
| 네비게이션 | `@react-navigation/native` | v7 | RN 표준, Stack/Tab/Modal |
| 서버 상태 | `@tanstack/react-query` | v5 | 캐싱·무효화·재시도 |
| 전역 상태 | `zustand` | v5 | 보일러플레이트 최소 |
| 로컬 스토리지 | `react-native-mmkv` | v3 | 동기 I/O, AES 암호화 |
| BottomSheet | `@gorhom/bottom-sheet` | v5 | Reanimated 3, 성능 최상 |
| 푸시 알림 | `@react-native-firebase/messaging` | v21 | FCM + APNs 통합 |
| 네트워크 상태 | `@react-native-community/netinfo` | v11 | NetInfo 표준 |
| 캘린더 | `react-native-calendars` | v1.13 | 달력 커스터마이징 |
| 드래그&드롭 | `react-native-reanimated` + `react-native-gesture-handler` | v3 | 60fps 제스처 |
| 카카오 SDK | `@react-native-kakao/share` | 공식 SDK | Feed 템플릿 공유 |
| 딥링크 | `react-native-code-push` or `Branch.io` | — | Deferred deep link |

---

## 8. 리스크 및 미결 사항

| 항목 | 리스크 | 대응 |
|---|---|---|
| FCM NoOp 상태 | 백엔드 v1.2 전까지 푸시 테스트 불가 | 인앱 토스트로 알림 대체 구현 후 교체 |
| 드래그&드롭 (휴무 수집 뷰) | Reanimated + GestureHandler 설정 복잡도 | Worklet 기반 shared value 패턴 적용 |
| iOS Universal Links | `apple-app-site-association` 도메인 설정 필요 | 인프라팀 협의 (§10.1) |
| DiceBear SVG 아바타 | 30종 SVG 번들 → 앱 크기 증가 | react-native-svg + 아이콘 스프라이트 최적화 |
| 관리자 API 인증 없음 | 현재 `permitAll` 상태 | Phase 999 적용 전 개발 편의 활용, prd 전 JWT 헤더 붙이는 interceptor 준비 |

---

## 9. backend-agent / design-agent 협의 예정 사항

**backend-agent에 요청:**
- 대시보드 합산 API (`GET /stores/{id}/dashboard-summary`) 경량화 응답 설계
- FCM 토큰 등록 엔드포인트 (`POST /me/push-token`) 스펙 확인
- 오프라인 큐 재시도 시 idempotency key 처리 방식

**design-agent에 요청:**
- `@gorhom/bottom-sheet` + 디자인 토큰 연동 가이드 (snap height, 배경색, handle indicator)
- 캘린더 셀 터치 타겟 최소 44pt 준수 확인
- 직원 칩 드래그 시 시각적 피드백 (shadow, scale 애니메이션) 스펙

---

*Round 1 완료 — backend / design 에이전트 응답 대기 후 Round 2 에서 통합 반론 작성 예정.*
