# Frontend Round 1 - 킥오프 미팅 분석

> 작성일: 2026-04-28  
> 작성자: frontend-agent  
> 상태: 소스 파일 읽기 권한 거부로 인해 태스크 설명 기반 분석

---

## 0. 분석 제약 사항

`docs/WorKey - 프론트엔드.md` 및 `frontend/` 내 소스 파일(App.tsx, package.json 등)에 대한 읽기 접근이 차단되었습니다.  
현재 분석은 태스크 명세(`create-react-native-app` 초기화 상태)와 일반적인 RN 프로젝트 구조를 기반으로 작성되었으며, **파일 접근 권한 복구 후 반드시 재검토가 필요합니다.**

---

## 1. React Navigation 구조 설계

### 현황 가정
- `create-react-native-app` 기본 세팅 → React Navigation 미설치 또는 기본 스택만 존재
- 인증/비인증 분기가 없는 단순 구조일 가능성 높음

### 제안 네비게이션 아키텍처

```
RootNavigator
├── AuthStack (비인증 상태)
│   ├── LoginScreen
│   └── RegisterScreen
└── MainTabs (인증 상태 - BottomTabNavigator)
    ├── HomeStack
    │   ├── HomeScreen
    │   └── JobDetailScreen
    ├── SearchStack
    │   └── SearchScreen
    ├── ApplyStack
    │   ├── ApplicationListScreen
    │   └── ApplicationDetailScreen
    └── ProfileStack
        └── ProfileScreen
```

### 필요 패키지
- `@react-navigation/native` (core)
- `@react-navigation/native-stack` (iOS/Android 네이티브 스택)
- `@react-navigation/bottom-tabs` (메인 탭)
- `react-native-screens` + `react-native-safe-area-context` (필수 peer deps)

### 주요 고려사항
- **딥링크(Deep Link)**: 채용 공고 공유 시 앱 직접 진입 지원 필요 → `linking` 설정 필수
- **인증 상태 연동**: Navigation State는 Auth 토큰 유무로 분기 (Context or Zustand)
- **헤더 커스터마이징**: 각 Stack별 `screenOptions`로 플랫폼 통일된 헤더 적용

---

## 2. 상태 관리 전략

### 권장 구조: Zustand + React Query (TanStack Query)

| 관심사 | 도구 | 이유 |
|--------|------|------|
| 서버 데이터 (채용공고, 지원현황 등) | React Query | 캐싱, 백그라운드 리페치, 페이지네이션 |
| 클라이언트 상태 (인증, UI 상태) | Zustand | 가벼운 번들, 보일러플레이트 최소화 |
| 폼 상태 | React Hook Form | 유효성 검증, 비제어 컴포넌트 |

### 인증 상태 흐름
```
App 시작
  → AsyncStorage에서 토큰 로드
  → useAuthStore.setToken()
  → RootNavigator가 isAuthenticated 구독 → AuthStack / MainTabs 분기
```

### 오프라인 대응
- React Query `staleTime` / `cacheTime` 적극 활용
- 중요 데이터(지원 현황 등)는 `@react-native-async-storage/async-storage` 로컬 캐시 병행
- 네트워크 상태 감지: `@react-native-community/netinfo` → 오프라인 토스트 표시

---

## 3. 네이티브 모듈 검토

### 필수 네이티브 모듈 후보

| 기능 | 라이브러리 | 비고 |
|------|-----------|------|
| 알림 | `@notifee/react-native` 또는 `react-native-push-notification` | 채용 지원 결과 알림 |
| 이미지 업로드 | `react-native-image-picker` | 프로필/포트폴리오 사진 |
| 생체 인증 | `react-native-biometrics` | 간편 로그인 |
| 링크 열기 | `react-native-linking` (내장) | 채용 공고 외부 링크 |
| 키보드 처리 | `react-native-keyboard-aware-scroll-view` | 폼 화면 UX |

### 플랫폼 주의사항
- iOS: `Podfile` 업데이트 + `pod install` 필요 (CI에서 자동화 필수)
- Android: `gradle` 설정 충돌 위험 → `react-native-builder-bob` 기반 라이브러리 우선 선택

---

## 4. 디자인 시스템 이식 전략

### 현황 가정
- 디자인 파일(Figma 등) 존재, RN 컴포넌트 미구현 상태
- `design-agent`와 협의 필요

### 이식 전략

#### 4-1. 토큰 기반 Theme 시스템
```typescript
// theme/tokens.ts
export const colors = {
  primary: '#...',
  background: '#...',
  // ...
} as const;

export const spacing = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 } as const;
export const typography = { /* ... */ } as const;
```

#### 4-2. 컴포넌트 우선순위
1. **Atom**: Button, Text, Input, Icon, Badge
2. **Molecule**: Card (채용공고), ListItem, SearchBar
3. **Organism**: JobPostingCard, ApplicationStatusCard, BottomSheet

#### 4-3. 모바일 전용 UI 패턴
- **BottomSheet**: `@gorhom/bottom-sheet` — 필터, 옵션 선택
- **Modal**: RN 내장 Modal + 커스텀 애니메이션
- **터치 타겟**: 최소 44×44pt (iOS HIG 기준) / 48×48dp (Android Material 기준)

#### 4-4. design-agent에게 확인 필요한 항목
- Figma 컴포넌트와 RN StyleSheet 간 매핑 규칙
- 다크모드 지원 여부
- 아이콘 세트 (SVG vs. 폰트 아이콘)

---

## 5. API 호출 최적화

### backend-agent에게 요청할 사항
- **목록 API 경량화**: 채용공고 목록 조회 시 전체 필드가 아닌 카드 표시용 필드만 반환하는 `summary` DTO 요청
  - 예: `title`, `companyName`, `location`, `deadlineDate`, `thumbnailUrl` 등 최소 필드
- **페이지네이션**: offset 방식보다 cursor-based pagination 권장 (무한 스크롤 성능)
- **이미지 URL**: CDN URL + 사이즈 파라미터 지원 요청 (모바일 해상도 최적화)

---

## 6. iOS/Android 플랫폼 통일성

### 주요 차이점 및 대응 방안

| 항목 | iOS | Android | 대응 |
|------|-----|---------|------|
| 하단 안전 영역 | Safe Area (노치/홈바) | 네비게이션 바 | `useSafeAreaInsets()` |
| 뒤로가기 | 스와이프 제스처 | 하드웨어 버튼 | `BackHandler` 처리 |
| 폰트 | San Francisco | Roboto | `fontFamily` 통일 또는 커스텀 폰트 |
| 그림자 | `shadow*` props | `elevation` | 플랫폼별 조건부 스타일 |
| 키보드 | `KeyboardAvoidingView behavior="padding"` | `behavior="height"` | `Platform.OS` 분기 |

---

## 7. 다음 단계 (Round 2 준비)

- [ ] `docs/WorKey - 프론트엔드.md` 실제 내용 확인 후 분석 보완
- [ ] design-agent에게 RN 컴포넌트 이식성 질문 전달
- [ ] backend-agent에게 DTO 경량화 요청 전달
- [ ] 다른 팀원 Round 1 산출물 검토 후 리버틀 작성
