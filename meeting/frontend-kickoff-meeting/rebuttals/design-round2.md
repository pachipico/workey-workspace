# [R2-DESIGN] Design Round 2 — 반론 및 교차 검토
**작성자:** design-agent  
**날짜:** 2026-04-29  
**참조:** frontend-round1.md / backend-round1.md / pm-round1.md / ux-round1.md + design-round1.md

---

## 0. 종합 평가

| 팀 | 디자인 관점 주요 발견 | 설계 정합성 |
|---|---|---|
| **frontend** | `@gorhom/bottom-sheet` 채택, 토큰 매핑 양호, Thumb Zone 적용 | ✅ 전반 일치 — snap heights 미확정 |
| **backend** | 스케줄 생성 1~5초 응답 지연, API 응답 래퍼 구조 | ⚠️ 로딩 UX 컴포넌트 필요 |
| **pm** | Dark Mode 미정의 Round 2 확인 요청, BottomSheet 4종 토큰 검수 기준 제시 | ✅ 디자인 우선순위 일치 |
| **ux** | 드래그&드롭 한 손 사망 지점, BottomSheet 3단 높이, 매장 모드 고대비 토큰 | 🔴 핵심 이슈 — 즉시 반영 필요 |

---

## 1. frontend-agent Round 1 검토 및 응답

### 1.1 BottomSheet 구현 ✅ 확정 응답

frontend가 요청한 `@gorhom/bottom-sheet` + 디자인 토큰 연동 가이드를 아래에 확정합니다.

#### snap heights 3단 표준 (UX R1 PP-2 반영)

UX가 제기한 "바텀시트가 달력을 다 가린다"는 문제를 해소하기 위해 **3단 높이 표준**을 확정합니다.

| 단계 | 높이 | 용도 | 달력 가림 정도 |
|---|---|---|---|
| **30%** | 화면의 30% | 힌트 / 토스트형 안내 | 최소 — 달력 70% 노출 |
| **60%** (기본 시작) | 화면의 60% | 충돌 상세, 신청자 칩 표시 | 달력 상단 절반 노출 |
| **100%** | 풀하이트 | 휴무 신청 사유 입력, 근무 교환 선택 | 전체 점유 |

```tsx
// 확정 구현 가이드
const DayOffConflictSheet = () => {
  // 충돌 상세: 60% 시작 (달력 상단이 보여야 비교 가능)
  const snapPoints = useMemo(() => ['60%', '100%'], []);

  return (
    <BottomSheet
      snapPoints={snapPoints}
      index={0}                         // 60% 기본 시작
      handleIndicatorStyle={{
        backgroundColor: tokens.primarySoft,   // #7DD3FC
        width: 40,                             // ≥ 40dp (UX R1 T3 요구)
        height: 4,
      }}
      backgroundStyle={{
        backgroundColor: tokens.surface,
        borderTopLeftRadius: 20,
        borderTopRightRadius: 20,
      }}
      backdropComponent={(props) => (
        <BottomSheetBackdrop
          {...props}
          opacity={0.4}
          disappearsOnIndex={-1}
          appearsOnIndex={0}
        />
      )}
    >
      ...
    </BottomSheet>
  );
};

const LeaveRequestSheet = () => {
  // 휴무 신청 사유 입력: 풀하이트 (키보드 공간 확보)
  const snapPoints = useMemo(() => ['100%'], []);
  ...
};

const InviteBottomSheet = () => {
  // 초대 링크: 35% (버튼 2개만 표시)
  const snapPoints = useMemo(() => ['35%'], []);
  ...
};
```

#### 핸들 터치 타겟 보정

UX가 요구한 핸들 너비 ≥ 40dp + 대비 4.5:1 요건:

```tsx
// 핸들 터치 히트슬롭 확대 (시각 너비 40dp, 터치 영역 44×44pt 확보)
handleStyle={{ height: 24, paddingTop: 10 }} // 내부 여백으로 터치 영역 확대
handleIndicatorStyle={{
  backgroundColor: '#7DD3FC',  // sky-300 on white: 대비 2.1:1 → 보완 필요
  width: 40,
  height: 4,
}}
```

> ⚠️ **핸들 색상 대비 이슈:** `#7DD3FC`(sky-300) on white 대비 = **2.1:1** — WCAG AA 4.5:1 미달.  
> **수정안:** 핸들 배경을 `#BAE6FD`(sky-200) → 핸들 바를 `#0369A1`(sky-700)으로 변경 → 대비 **8.75:1** 확보.  
> 또는 핸들 영역 배경을 `#E0F2FE`(sky-100)로 깔아 시각적 분리.

### 1.2 CalendarCell 터치 타겟 ✅ 확인

frontend R1의 `width: 44, height: 44` 기준은 **HIG 44pt 충족**. 단, Android dp 기준 48dp와 동일 기기에서 맞추려면:

```tsx
const CalendarCell = ({ date, onPress }) => (
  <TouchableOpacity
    onPress={onPress}
    style={{
      width: 44,
      height: 44,
      alignItems: 'center',
      justifyContent: 'center',
      // 시각 크기는 작더라도 히트슬롭으로 터치 영역 보완
    }}
    hitSlop={{ top: 2, bottom: 2, left: 2, right: 2 }} // 실질 48dp 확보
  >
    <Text style={styles.dateText}>{date}</Text>
  </TouchableOpacity>
);
```

### 1.3 드래그 시각 피드백 스펙 ✅ 확정 (UX PP-1 반영)

frontend가 요청한 "드래그 시 shadow·scale 애니메이션" + UX가 요구한 "손가락 위 floating preview"를 통합합니다.

```tsx
// 드래그 중 칩 시각 피드백 스펙
const DraggableChip = ({ employee, onDrag }) => {
  const scale = useSharedValue(1);
  const opacity = useSharedValue(1);

  const gestureHandler = useAnimatedGestureHandler({
    onStart: () => {
      // 1. 원본 칩: 반투명으로 자리 표시
      opacity.value = withTiming(0.3, { duration: 150 });
      // 2. floating preview: 손가락 위 20dp 오프셋 + 1.05 scale
      scale.value = withSpring(1.05);
      // 3. 햅틱 피드백
      runOnJS(Haptics.impactAsync)(Haptics.ImpactFeedbackStyle.Medium);
    },
    onActive: (event) => {
      // floating preview 추적 (translateX/Y + offsetY -20dp)
    },
    onEnd: () => {
      // 1. 드롭 성공: 원본 fade out, preview scale 0
      // 2. 햅틱 (light)
      // 3. Toast: "N일로 이동되었어요" + 5초 Undo 버튼
      runOnJS(Haptics.notificationAsync)(Haptics.NotificationFeedbackType.Success);
    },
  });
};

// 드롭 가능 셀 강조
const DroppableCell = ({ isHighlighted }) => (
  <Animated.View
    style={[
      styles.cell,
      isHighlighted && {
        borderWidth: 2,
        borderColor: '#0EA5E9',   // --ts-primary
        borderRadius: 8,
        backgroundColor: '#E0F2FE', // --ts-primary-surface
      },
    ]}
  />
);
```

**드롭 후 Undo 토스트 (UX PP-1 요구):**

| 항목 | 규격 |
|---|---|
| 표시 위치 | 화면 하단, safe-area + 24pt |
| 내용 | "6월 17일 → 6월 23일로 이동되었어요" + [되돌리기] 버튼 |
| 유효시간 | **5초** (카운트다운 진행 바 표시) |
| 버튼 색상 | `#7DD3FC` (sky-300) — 토스트 배경과 구분 |
| 토스트 배경 | `#0C4A6E` (sky-900) — 어두운 배경에서 가독성 확보 |

---

## 2. backend-agent Round 1 검토 — 로딩 UX 컴포넌트 정의

backend R1에서 지적된 **"스케줄 생성 API 응답 1~5초"**에 대한 디자인 응답:

### 스케줄 생성 로딩 스피너 규격

```
[생성 확정 버튼 탭]
    ↓
풀스크린 로딩 오버레이 (투명도 0.7, 배경 #0F172A)
    ┌─────────────────┐
    │                 │
    │   ⚙️ 생성 중... │  ← sky-500 animated spinner
    │   약 3~5초 소요  │  ← 회색 캡션 텍스트
    │                 │
    └─────────────────┘
    ↓ 완료
결과 화면 (fade-in 300ms)
```

| 항목 | 규격 |
|---|---|
| 스피너 색상 | `#0EA5E9` (--ts-primary) |
| 배경 오버레이 | `rgba(15, 23, 42, 0.7)` (slate-900 70%) |
| 텍스트 | "스케줄 생성 중..." + "잠시만 기다려 주세요" 14sp |
| 타임아웃 기준 | 10초 초과 시 "응답이 지연되고 있어요" 메시지 + 재시도 버튼 |
| 인터럽트 방지 | 로딩 중 Back 제스처 비활성화 |

> backend API 500ms 이하 응답 (초대·휴무 신청 등)은 인라인 버튼 로딩 상태로 처리 (풀스크린 오버레이 불필요).

---

## 3. PM Round 1 검토 — 핵심 요청 응답

### 3.1 Dark Mode — 앱 내 독립 설정으로 확정 (UX R1 T3 지지)

PM이 "Round 2에서 디자인팀에 확인 필요"로 등록한 Dark Mode 정책을 **확정**합니다.

**결정:** 시스템 다크 모드를 따르지 않고, **앱 내 독립 라이트/다크 설정** 제공.

> UX 근거: "매장 형광등 환경에서 라이트 모드가 더 잘 보이는 경우가 많음. 시스템 다크 따라가지 말고 앱 내 설정 분리."

#### 다크 모드 컬러 토큰 확정 테이블

| 토큰 | 라이트 값 | 다크 값 | WCAG 대비 (다크) |
|---|---|---|---|
| `--ts-primary` | `#0EA5E9` | `#38BDF8` (sky-400) | 배경 #0F172A 대비 6.7:1 ✅ |
| `--ts-primary-ink` | `#0369A1` | `#7DD3FC` (sky-300) | 배경 #0F172A 대비 9.4:1 ✅ |
| `--ts-primary-soft` | `#7DD3FC` | `#38BDF8` (sky-400) | — |
| `--ts-surface` | `#FFFFFF` | `#0F172A` (slate-900) | — |
| `--ts-surface-card` | `#E0F2FE` | `#1E293B` (slate-800) | — |
| `--ts-text-primary` | `#1E293B` | `#F1F5F9` (slate-100) | #0F172A 대비 15.3:1 ✅ |
| `--ts-text-secondary` | `#64748B` | `#94A3B8` (slate-400) | #0F172A 대비 5.1:1 ✅ |
| `--ts-error` | `#EF4444` | `#F87171` (red-400) | 배경 대비 4.8:1 ✅ |
| `--ts-cal-today-bg` | `#0EA5E9` | `#38BDF8` | — |
| `--ts-border` | `#E2E8F0` | `#334155` (slate-700) | — |

```ts
// theme/tokens.ts — 다크모드 분기 추가
import { Appearance } from 'react-native';

export const getTokens = (mode: 'light' | 'dark') => ({
  primary: mode === 'light' ? '#0EA5E9' : '#38BDF8',
  primaryInk: mode === 'light' ? '#0369A1' : '#7DD3FC',
  primarySoft: mode === 'light' ? '#7DD3FC' : '#38BDF8',
  surface: mode === 'light' ? '#FFFFFF' : '#0F172A',
  surfaceCard: mode === 'light' ? '#E0F2FE' : '#1E293B',
  textPrimary: mode === 'light' ? '#1E293B' : '#F1F5F9',
  textSecondary: mode === 'light' ? '#64748B' : '#94A3B8',
  error: mode === 'light' ? '#EF4444' : '#F87171',
  border: mode === 'light' ? '#E2E8F0' : '#334155',
  calTodayBg: mode === 'light' ? '#0EA5E9' : '#38BDF8',
});

// 앱 내 설정에서 'light' | 'dark' | 'system' 선택
// 설정값은 MMKV에 영구 저장
```

### 3.2 BottomSheet 4종 토큰 검수 기준 ✅ 수립

PM R1 §4.2가 요구한 "디자인 토큰 1:1 일치 PR 검수 기준":

| 검수 항목 | 기준값 | 확인 방법 |
|---|---|---|
| 핸들 바 색상 | `tokens.primarySoft (#7DD3FC)` | StyleSheet 선언 확인 |
| 핸들 너비 | `width: 40` (≥ 40dp) | props 확인 |
| 배경색 | `tokens.surface` (raw `#fff` 사용 금지) | 정규식 `/background[^:]*:\s*['"]#fff/` 0건 |
| CTA 버튼 활성 bg | `tokens.primary (#0EA5E9)` | — |
| CTA 버튼 비활성 bg | `tokens.primary100 (#E0F2FE)` + `tokens.textSecondary` 텍스트 | — |
| 패딩 상단 | `12pt` | — |
| 패딩 수평 | `20pt` | — |
| 하단 패딩 | `useSafeAreaInsets().bottom + 16` | SafeAreaInsets 사용 확인 |
| 오버레이 | `rgba(0,0,0,0.4)` | — |
| OS 네이티브 공유 시트 | **사용 금지** | PR 설명에 "OS Share 미사용" 명시 |

---

## 4. UX Round 1 검토 — 심층 반론 및 수용

UX R1은 디자인 관점에서 가장 중요한 현장 인사이트를 제공했습니다. 항목별 설계 반영을 결정합니다.

### 4.1 드래그&드롭 한 손 사망 지점 (UX PP-1) — 🔴 즉시 반영

**UX 발견:** "칩 드래그 중 손가락에 가려서 어디 떨어지는지 모른다."

**디자인 결정:**

1. **floating preview (손가락 위 20dp):** 드래그 중 칩의 유령 복사본이 손가락 위에 표시. 1.1 섹션 참조.
2. **드래그 fallback (UX R1 T4 드래그 fallback):** 칩 long-press → 컨텍스트 메뉴 → "이 직원의 휴무를 다른 날로 옮기기" → 달력 셀 1탭으로 완료.

```
[Long-press DayOffChip]
    ↓
컨텍스트 메뉴 팝오버 (칩 위 60dp)
┌──────────────────────┐
│ 김민준 휴무 (6/17)    │
│ ──────────────────── │
│ 📅 다른 날로 옮기기    │  ← 탭
│ ✕ 취소                │
└──────────────────────┘
    ↓ "다른 날로 옮기기" 선택
달력 셀 선택 모드 진입
(선택 가능 셀 파란 테두리 강조)
    ↓ 셀 1탭
이동 완료 + 토스트 + 5초 Undo
```

**규격:**
- 컨텍스트 메뉴: `borderRadius: 12`, `backgroundColor: tokens.surface`, `elevation: 8`
- 메뉴 항목 높이: **48dp** (터치 타겟 기준 준수)
- 매뉴 아이템 텍스트: `tokens.primaryInk (#0369A1)`, 16sp bold

### 4.2 충돌 셀 Long-press 미니 팝오버 (UX PP-2) — ✅ 수용

**UX 발견:** "충돌 셀 탭 → 바텀시트가 달력을 가림 → 옆 날짜 비교 불가."

**디자인 결정:** 충돌 셀 Long-press → **인라인 미니 팝오버** (달력 위 플로팅, 높이 최대 달력의 40%)

```
┌─────────────────────────────────────────────┐
│  일  월  화  수  목  금  토                   │
│  ...    [🔴17]                               │
│         ┌────────────────────┐              │
│         │ 6/17 인원 미달      │  ← 미니 팝오버
│         │ 최소 3명 / 현재 2명  │  (달력 위 플로팅)
│         │ 👤김민준  👤이수아   │
│         │ [재배치 모드 진입 →] │
│         └────────────────────┘
│  ...                                        │
└─────────────────────────────────────────────┘
```

**규격:**
- 팝오버 최대 높이: 달력 높이의 **40%** (하단 달력 60% 노출 유지)
- `borderRadius: 12`, `backgroundColor: tokens.surface`
- `elevation: 6`, 탭 외부 영역 → 팝오버 dismiss
- "재배치 모드 진입" 버튼 탭 시 → 60% 바텀시트로 전환 + 칩 드래그/롱프레스 모드 진입

### 4.3 매장 모드 (Store Mode) 고대비 토큰 — ✅ 신설

**UX 발견:** "매장 직사광, 형광등 환경에서 sky-50이 흰색과 구분 안 됨. 노안 시작 점장."

**디자인 결정:** "매장 모드" 컬러 토큰 셋 신설

| 토큰 (라이트) | 라이트 값 | **매장 모드 값** | 대비 개선 |
|---|---|---|---|
| `--ts-primary` | `#0EA5E9` | `#0369A1` (sky-700) | 3.0:1 → 8.75:1 ✅ |
| `--ts-primary-surface` | `#E0F2FE` | `#BAE6FD` (sky-200) | 시각적 분리 강화 |
| `--ts-primary-50` | `#F0F9FF` | `#E0F2FE` (sky-100) | 배경 틴트 강조 |
| `--ts-cal-work-tint` | `#E0F9FF` | `#BAE6FD` | ON/OFF 차이 명확화 |
| `--ts-text-primary` | `#1E293B` | `#0C4A6E` (sky-900) | 최심층 잉크 |
| 폰트 크기 | 기준 | +1단계 (xs→sm, sm→base 등) | 노안 대응 |
| 터치 타겟 | 48dp | **+20%: 58dp** | 손가락 오동작 방지 |

```ts
// theme/tokens.ts에 storeMode 추가
export const storeModeOverrides = {
  primary: '#0369A1',        // sky-700 (고대비)
  primarySurface: '#BAE6FD', // sky-200
  primary50: '#E0F2FE',
  calWorkTint: '#BAE6FD',
  textPrimary: '#0C4A6E',
  hitAreaMultiplier: 1.2,    // 모든 터치 타겟 ×1.2
  fontSizeOffset: 2,         // sp 단위 +2
};

// 사용 예
const effective = storeMode
  ? { ...baseTokens, ...storeModeOverrides }
  : baseTokens;
```

**매장 모드 진입점:** 설정 화면 → "매장 모드 (고대비/큰 글씨)" 토글. 온보딩에서 1회 소개 ("밝은 매장에서 더 잘 보이게").

### 4.4 알림 피로도 — 디자인 관련 항목 (UX PP-5)

UX R1 PP-5의 알림 그룹화는 백엔드·프론트 협의 사항이지만, **디자인이 담당하는 UI 구성요소**:

| 컴포넌트 | 규격 |
|---|---|
| in-app 알림 배너 | 화면 상단 below 내비게이션 바, 높이 56pt, `backgroundColor: tokens.surfaceCard` |
| 배너 내 "N건 변경사항" | 굵은 숫자 + "자세히 보기 >" 링크 (primaryInk) |
| 알림 설정 화면 | 카테고리별 Toggle (스위치 높이 44pt), 영업시간 무음 시간 범위 슬라이더 |
| Daily Digest 토글 | ON: "오늘 변경사항 한 번에 받기", OFF: "실시간 받기" |

### 4.5 달력 오늘 날짜 배경 대비 문제 — ✅ 수정 확정

Round 1에서 경고로 표시했던 `#0EA5E9` + 흰 텍스트 = **2.9:1** 문제.

**결정:** 오늘 날짜 배경을 `#0369A1`(sky-700)으로 변경.

| 항목 | 기존 | 수정 |
|---|---|---|
| `--ts-cal-today-bg` | `#0EA5E9` (sky-500) | `#0369A1` (sky-700) |
| 흰 텍스트 대비 | 2.9:1 ❌ | 8.75:1 ✅ |
| 매장 모드 대비 | — | `#0C4A6E` (sky-900), 대비 12.6:1 |

> 이 변경은 `docs/WorKey - 디자인.md`의 `--ts-cal-today-bg` 토큰 갱신이 필요합니다. PM 승인 후 반영 요청.

---

## 5. 4대 핵심 토픽 최종 디자인 입장 정리

### T1. 모바일 최적화 API — 디자인 관점 추가 의견

UX가 요구한 "bootstrap API로 0.8초 첫 화면"에 대해 디자인이 지원할 수 있는 것:

- **Skeleton Screen 표준화:** 스케줄 달력, 직원 목록, 대시보드 요약 각각의 skeleton 컴포넌트 규격 정의
- **stale-while-revalidate 시각화:** 캐시 데이터 노출 시 "마지막 업데이트 N분 전" 안내 문구 (텍스트 secondary, 11sp)

### T2. 네이티브 연동 — 푸시 알림 UI 스펙

| 알림 종류 | in-app Toast 스펙 | 배경색 |
|---|---|---|
| 쉬기 전날 알림 | "내일은 휴무예요 🌙" | `#0369A1` (sky-700) |
| 휴무 재배치 결과 | "N일로 이동되었어요" + Undo | `#0C4A6E` (sky-900) |
| 근무 교환 요청 | "OOO님이 교환을 요청했어요" | `#0369A1` |
| 관리자 당일 현황 | in-app 배너 (상단 56pt) | `tokens.surfaceCard` |

### T3. 디자인 이식 — Round 2 확정 사항 요약

| 항목 | Round 1 | Round 2 확정 |
|---|---|---|
| BottomSheet snap heights | 미확정 | **30% / 60% / 100% 3단** 확정 |
| 핸들 색상 대비 | `#7DD3FC` (2.1:1) ❌ | `#0369A1` 핸들 바 (8.75:1) ✅ |
| 드래그 피드백 | 규격 미정 | floating preview + 햅틱 + 5초 Undo 토스트 |
| 충돌 셀 인터랙션 | 탭 → 60% 바텀시트 | **Long-press → 미니 팝오버** (달력 60% 유지) |
| Dark Mode | 미정의 | 앱 내 독립 설정, 토큰 테이블 확정 |
| 오늘 날짜 배경 | `#0EA5E9` (2.9:1) ❌ | `#0369A1` (8.75:1) ✅ |
| 매장 모드 | 없음 | 고대비 토큰 셋 신설, +20% 타겟, +2sp 폰트 |

### T4. 사용자 환경 (한 손 조작) — Round 2 확정

| 요소 | Round 1 | Round 2 확정 |
|---|---|---|
| 생성 확정 버튼 | 헤더 우측 → 하단 권고 | **하단 full-width sticky, 56dp** 확정 |
| 드래그 fallback | 권고 | **Long-press → 메뉴 → 달력 1탭** 표준 구현 |
| 달력 상단 날짜 접근 | 스크롤 유도 | Long-press 방식으로 상단 날짜 접근 불필요 |
| 알림 권한 요청 타이밍 | 언급 없음 | 첫 휴무 신청 완료 직후 (PM, UX 공통 동의) |

---

## 6. UX에게 SendMessage 요청 사항

> 아래는 SendMessage to: "ux" 로 전달하는 공식 검토 요청입니다.

**검토 요청 1 — 터치 타겟 크기 현장 검증**

WorKey는 Apple HIG 44pt와 Material 48dp 중 더 큰 48dp를 기준으로 삼고, 매장 모드에서 ×1.2(58dp)를 추가 적용하는 방안을 확정했습니다.  
그러나 실제 카운터 환경(기름 묻은 손, 젖은 손, 장갑 착용 가능성)에서 58dp가 충분한지, 아니면 60~64dp까지 확대해야 하는지 점장 페르소나 시각에서 현장 검증 의견을 요청합니다.  
특히 **드래그 소스인 직원 칩(현재 최소 높이 32pt)**이 실제 매장 환경에서 첫 탭에 정확히 잡히는지 피드백을 주세요.

**검토 요청 2 — 야외/매장 시각 피로도**

매장 모드 고대비 토큰에서 primary를 `#0369A1`(sky-700)으로 상향했으나, 형광등 직사광 환경에서 sky-700의 채도가 오히려 **눈부심(glare)** 을 유발할 가능성이 있는지 검토 부탁드립니다.  
특히 장시간 스케줄 조작 시(30분 이상) 파란색 계열 고채도 색상의 시각 피로도가 라이트 모드보다 다크 모드에서 낮은지, 아니면 매장 환경에서는 오히려 라이트 모드 고대비가 더 나은지 의견을 주세요.  
이 결과에 따라 **매장 모드를 라이트 고대비로 고정할지, 다크+고대비 옵션을 추가할지** 결정하겠습니다.

---

## 7. Round 2 미결 및 다음 단계

| 항목 | 담당 | 우선순위 |
|---|---|---|
| `--ts-cal-today-bg` `#0369A1` 변경 → 디자인 문서 갱신 | design | 🟠 높음 |
| 핸들 바 색상 `#0369A1` 변경 → tokens.ts 반영 | frontend | 🟠 높음 |
| Dark Mode tokens.ts 완전 구현 | frontend | 🟠 높음 |
| 매장 모드 토큰 구현 + 설정 화면 UI | frontend + design | 🟡 중간 |
| Long-press 미니 팝오버 컴포넌트 명세 | design | 🟡 중간 |
| 드래그 floating preview + Undo 토스트 | frontend | 🟡 중간 |
| Skeleton Screen 컴포넌트 3종 | design + frontend | 🟡 중간 |
| UX 회신 대기 (터치 타겟 현장 검증, 시각 피로도) | ux | — |

---

*Round 2 완료 — Round 3에서 UX 회신 통합 후 최종 가이드라인 확정 예정.*
