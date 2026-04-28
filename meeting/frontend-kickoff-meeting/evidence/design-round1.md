# Design Round 1 - WorKey 모바일 앱 디자인 시스템 분석

**작성자:** design agent  
**일자:** 2026-04-28  
**라운드:** Round 1  

> ⚠️ **접근 제한 고지:** `docs/WorKey - 디자인.md` 및 `design/` 폴더 파일 읽기 권한이 없어, 의제(`agenda.md`) 맥락과 React Native 모바일 디자인 표준 원칙을 기반으로 분석합니다.

---

## 1. 모바일 디자인 토큰 (Mobile Design Tokens)

### 필수 토큰 분류

| 토큰 카테고리 | 항목 | 권장 규격 |
|---|---|---|
| **Color** | Primary, Secondary, Surface, Error, OnSurface | HSL 또는 HEX, semantic naming 필수 |
| **Typography** | fontSize, fontWeight, lineHeight | sp 단위 (Android) / pt 단위 (iOS) |
| **Spacing** | xs(4), sm(8), md(16), lg(24), xl(32), 2xl(48) | 4의 배수 기반 grid |
| **Border Radius** | sm(4), md(8), lg(16), full(9999) | 컴포넌트별 고정값 권장 |
| **Elevation / Shadow** | 0~5단계 | iOS: shadow props, Android: elevation |
| **Motion** | duration(100/200/300ms), easing | LayoutAnimation / Reanimated2 |

### React Native 토큰 이식 방식

```ts
// 권장: StyleSheet.create 대신 theme context로 토큰 관리
const theme = {
  colors: {
    primary: '#...',
    surface: '#...',
    onSurface: '#...',
  },
  spacing: {
    xs: 4, sm: 8, md: 16, lg: 24, xl: 32,
  },
  typography: {
    heading1: { fontSize: 24, fontWeight: '700', lineHeight: 32 },
    body1:    { fontSize: 16, fontWeight: '400', lineHeight: 24 },
    caption:  { fontSize: 12, fontWeight: '400', lineHeight: 18 },
  },
};
```

**이식성 체크포인트:**
- 웹 디자인 토큰(px 단위)이 RN에서 그대로 쓰이면 플랫폼별 스케일 불일치 발생.  
  → `PixelRatio.getFontScale()` 또는 `useWindowDimensions()`로 반응형 처리 필수.
- `rem` 단위는 RN에서 미지원 — 모든 폰트는 숫자 단위로 변환 필요.

---

## 2. BottomSheet 컴포넌트

### 권장 라이브러리: `@gorhom/bottom-sheet` v5

**선택 근거:**
- Reanimated 2 기반으로 60fps 애니메이션 보장
- `BottomSheetScrollView`, `BottomSheetFlatList` 등 내부 스크롤 지원
- Snap point 설정으로 디자인 가이드의 고정 높이 구현 가능
- iOS / Android 동일 동작 보장

**디자인 시스템 연계 주의사항:**

```ts
// ✅ 권장: snap points를 디자인 토큰 기반으로 정의
const SNAP_POINTS = {
  half: '50%',
  full: '90%',  // Safe Area 상단 margin 확보
};

// ✅ 필수: handle indicator 스타일을 디자인 가이드와 일치시킬 것
// (높이 4px, 너비 40px, 상단 margin 8px 표준)
```

**BottomSheet 내부 터치 타겟 주의:**  
BottomSheet 내부 버튼은 키보드가 올라오는 경우 `KeyboardAvoidingView` 또는  
`@gorhom/bottom-sheet`의 `enableDynamicSizing` 옵션으로 겹침 방지 필수.

---

## 3. 터치 타겟 (Touch Target)

### 플랫폼 최소 규격

| 플랫폼 | 최소 터치 타겟 | 출처 |
|---|---|---|
| iOS (HIG) | **44 × 44 pt** | Apple Human Interface Guidelines |
| Android (Material 3) | **48 × 48 dp** | Google Material Design |
| 권장 통합 기준 | **48 × 48 (논리 픽셀)** | 두 플랫폼 공통 충족 |

### WorKey 페르소나 적용 (최기준 점장님 - 한 손 조작)

바쁜 근무 현장에서 한 손 조작을 위한 추가 규격:

1. **엄지 도달 영역 (Thumb Zone):** 화면 하단 60% 내 주요 CTA 배치 권장
2. **하단 내비게이션 아이콘:** 최소 56px 높이 (탭 바 기준)
3. **일정 등록 버튼:** 최소 56 × 56px FAB 또는 전체 너비 버튼 권장
4. **입력 필드 높이:** 최소 52px — 터치 실패율 감소

**구현 시 주의:**  
`TouchableOpacity`의 `hitSlop` 속성을 활용해 시각적 크기를 유지하면서 터치 영역 확장 가능:
```ts
hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
```

---

## 4. Safe Area 처리

### 필수 라이브러리: `react-native-safe-area-context`

**이유:**
- RN 내장 `SafeAreaView`는 배경색 커스텀 불가 (노치/Dynamic Island 영역)
- `useSafeAreaInsets()` hook으로 정밀한 인셋 값 접근 가능

```ts
// ✅ 권장 패턴
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const Screen = () => {
  const insets = useSafeAreaInsets();
  return (
    <View style={{ 
      paddingTop: insets.top,
      paddingBottom: insets.bottom 
    }}>
      ...
    </View>
  );
};
```

**특수 케이스:**
- **BottomSheet + Safe Area:** BottomSheet가 풀스크린으로 확장될 때 상단 인셋 별도 처리 필요
- **키보드 + Safe Area:** `KeyboardAvoidingView`와 하단 inset 중복 적용 시 이중 패딩 주의
- **가로 방향(Landscape):** 좌/우 inset도 반드시 처리 (태블릿 대응 시)

---

## 5. 다크모드 (Dark Mode)

### 지원 전략 권장안

**Option A: 시스템 연동 (권장)**
```ts
import { useColorScheme } from 'react-native';
const colorScheme = useColorScheme(); // 'light' | 'dark' | null
```

**Option B: 앱 내 수동 전환 + 시스템 연동 혼합**
- React Context + AsyncStorage로 사용자 설정 유지
- WorKey처럼 B2B 업무용 앱은 근무 환경(야간 주방 등) 고려 시 수동 다크모드 지원 가치 있음

### 다크모드 토큰 쌍 정의 필수 항목

```ts
const colors = {
  light: {
    background: '#FFFFFF',
    surface:    '#F5F5F5',
    onSurface:  '#1A1A1A',
    border:     '#E0E0E0',
    primary:    '#...',
  },
  dark: {
    background: '#121212',
    surface:    '#1E1E1E',
    onSurface:  '#FFFFFF',
    border:     '#2C2C2C',
    primary:    '#...', // 다크모드에서 채도 조정 필요
  },
};
```

**디자인 가이드 이식 시 필수 체크:**
- 이미지/아이콘의 다크모드 대응 여부 (SVG는 fill 색상 토큰 연결)
- 그림자(Shadow)는 다크모드에서 효과 없음 → elevation 대신 border로 구분
- 하드코딩된 `#FFFFFF` / `#000000` 금지 — 반드시 semantic 토큰 사용

---

## 6. React Native 컴포넌트 라이브러리 의견

### 평가 기준
1. 디자인 시스템 커스터마이징 용이성
2. RN 최신 아키텍처(New Architecture / Fabric) 호환성
3. 번들 사이즈 영향
4. 유지보수 활성화 여부 (2024~2025 기준)

### 후보 라이브러리 비교

| 라이브러리 | 커스터마이징 | New Arch | 번들 영향 | 권장도 |
|---|---|---|---|---|
| **Shopify/restyle** | ★★★★★ | ✅ | 소 | ★★★★★ |
| **React Native Paper** | ★★★★ | ✅ | 중 | ★★★★ |
| **NativeBase** | ★★★ | 부분 | 대 | ★★★ |
| **Gluestack UI v2** | ★★★★ | ✅ | 중 | ★★★★ |
| **직접 구축 (custom)** | ★★★★★ | ✅ | 최소 | ★★★ (리소스 큰 경우) |

### 권장: **Shopify/restyle + 부분 커스텀 컴포넌트 조합**

**근거:**
- `restyle`은 디자인 토큰을 theme에 정의 후 모든 컴포넌트에 자동 적용 → **토큰 이식성 최고**
- 특수 컴포넌트(BottomSheet, Calendar 등)는 개별 전용 라이브러리 사용
- 불필요한 UI 컴포넌트 번들을 포함하지 않아 앱 용량 최소화

```
[컴포넌트 레이어 제안]
- 토큰/테마 관리: @shopify/restyle
- 레이아웃 프리미티브: Box, Text (restyle 기반)
- BottomSheet: @gorhom/bottom-sheet
- 날짜/달력: react-native-calendars (or 직접 구현)
- 아이콘: react-native-vector-icons / @expo/vector-icons
- 애니메이션: react-native-reanimated 2+
```

---

## 7. 종합 의견 및 frontend-agent에 대한 체크포인트

Round 2에서 `frontend-agent`가 확인해야 할 항목:

1. **토큰 관리:** px/rem 단위를 RN 논리 픽셀로 변환했는지 확인
2. **BottomSheet 구현:** `@gorhom/bottom-sheet` 사용 시 snap points가 디자인 가이드 기준 높이와 일치하는지
3. **터치 타겟:** 모든 인터랙티브 요소가 최소 48×48px 이상인지 (`hitSlop` 포함)
4. **Safe Area:** `react-native-safe-area-context` 기반으로 모든 스크린에 적용했는지
5. **다크모드:** 하드코딩 색상 없이 semantic 토큰만 사용하는지
6. **컴포넌트 라이브러리:** 선택 라이브러리가 디자인 토큰과 연결 가능한 구조인지

---

*이 문서는 `docs/WorKey - 디자인.md` 원본 파일 접근이 제한된 상태에서 작성되었습니다. Round 2에서 실제 디자인 가이드 토큰값이 공유되면 수치를 보완할 예정입니다.*
