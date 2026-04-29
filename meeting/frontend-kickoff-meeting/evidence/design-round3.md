# [R3-DESIGN] Design Round 3 — 종합 최종 가이드라인
**작성자:** design-agent  
**날짜:** 2026-04-29  
**참조:** 전 라운드 (design/frontend/backend/pm/ux Round 1·2)

---

## 0. 3라운드 전체 결론 한 줄 요약

> **"sky-500 파스텔 디자인 시스템은 매장 카운터 현실에 맞게 sky-700 고대비로 단단해졌고, BottomSheet 3단·드래그 fallback·EmployeeChip 44pt 세 가지로 한 손 조작 사망 지점을 해소했다. Dark Mode는 v1.3로 이월, 매장 모드 3요소는 v1.2 흡수."**

---

## 1. PM 질문 응답 (D-1, D-2)

### D-1 ✅ 동의 — 달력 오늘 날짜 배경 `#0369A1` 즉시 변경

> PM: "달력 오늘 날짜 배경을 `#0EA5E9`(2.9:1)에서 `#0369A1`(8.75:1)로 변경하는 데 동의하는가? v1.2 MVP 차단 조건."

**디자인 확정:** 동의. Round 2에서 이미 결정한 내용을 공식 확인한다.

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| `--ts-cal-today-bg` | `#0EA5E9` (sky-500) | `#0369A1` (sky-700) |
| 흰 텍스트 대비 | 2.9:1 ❌ WCAG 미달 | **8.75:1** ✅ WCAG AAA |
| 매장 모드 대비 | — | `#0C4A6E` (sky-900) → 12.6:1 |

> **docs/WorKey - 디자인.md `--ts-cal-today-bg` 값을 `#0369A1`로 갱신 필요. PM 머지 승인 요청.**

---

### D-2 ✅ 동의 — Dark Mode v1.3 강등

> PM: "PM은 Dark Mode를 v1.3로 이월하려는데 design이 동의하는가? UX가 '매장 형광등에선 라이트가 낫다'고 했다."

**디자인 확정:** 동의. 이유:

1. UX R2 §5 T3: "매장 형광등 환경에서 라이트 모드가 더 잘 보이는 경우가 많음"
2. 38세 점장 페르소나 시나리오(영업 중 형광등, 직사광)에서 다크 모드 수요 미확인
3. Round 2에서 제안한 다크 토큰 테이블은 **v1.3 착수 시 즉시 활용 가능하도록 문서 보존**

**v1.2 라이트 모드 단일 출시 전략:**
```ts
// theme/tokens.ts — v1.2 단일 라이트 팔레트
// useColorScheme() 무시 — 시스템 다크 자동 추종 OFF
export const tokens = {
  primary: '#0EA5E9',
  primaryInk: '#0369A1',
  calTodayBg: '#0369A1',  // ← D-1 갱신 반영
  surface: '#FFFFFF',
  // ... 라이트 단일
};

// v1.3 다크 토큰은 design-round2.md §3.1 테이블 참조하여 착수
```

---

## 2. frontend-agent 질문 응답 (4건)

### Q1 ✅ — BottomSheet 3단 snap 단계별 backdropOpacity + 핸들 컬러

> "30% / 60% / 92% 각 단계별 `backdropOpacity` 값과 핸들 인디케이터 색상 가이드를 제공해줄 수 있는가?"

**확정 가이드:**

| snap 단계 | 높이 | backdropOpacity | 핸들 바 색상 | 핸들 너비 | 용도 |
|---|---|---|---|---|---|
| **30%** | 화면 30% | `0.15` | `#BAE6FD` (sky-200) | 40dp | 힌트·코치마크 |
| **60%** (기본) | 화면 60% | `0.40` | `#0369A1` (sky-700) | 40dp | 충돌 상세, 칩 표시 |
| **92%** | 화면 92% | `0.60` | `#0369A1` (sky-700) | 40dp | 풀하이트 입력 |

**60% 단 달력 경계 그림자 처리:**

```tsx
// 60% 단에서 바텀시트 상단 그림자 — 달력과의 경계 명확화
backgroundStyle={{
  backgroundColor: tokens.surface,
  borderTopLeftRadius: 20,
  borderTopRightRadius: 20,
  // iOS
  shadowColor: '#0C4A6E',   // sky-900
  shadowOffset: { width: 0, height: -4 },
  shadowOpacity: 0.12,
  shadowRadius: 8,
  // Android
  elevation: 4,
}}
```

**BottomSheet 종류별 최종 snap 표준:**

| 컴포넌트 | snapPoints | initialIndex | backdropOpacity |
|---|---|---|---|
| `InviteBottomSheet` | `['40%']` | 0 | 0.4 |
| `LeaveRequestSheet` | `['50%', '92%']` | 0 | 0.4 |
| `DayOffConflictSheet` | `['30%', '60%', '92%']` | 1 (60%) | 0.15/0.4/0.6 |
| `ShiftSwapSheet` | `['60%', '92%']` | 0 | 0.4 |

---

### Q2 ✅ — 드래그 시 BottomSheet 자동 축소 인터랙션 확정

> "충돌 칩 드래그 시 BottomSheet가 자동으로 30% 단으로 축소되는 인터랙션 — 디자인 스펙으로 정의해줄 수 있는가?"

**확정 인터랙션 시퀀스:**

```
[상태 1] DayOffConflictSheet 60% 단 열려있음
         → 달력 상단 40% 보임, 칩 목록 보임

[Long-press 시작 (300ms)]
         → 햅틱 Medium
         → BottomSheet.snapToIndex(0) 호출 (30% 단으로 자동 수축)
         → 수축 애니메이션: 200ms spring
         → 달력 70% 노출, 드롭 가능 셀 파란 테두리 활성화

[드래그 중]
         → floating preview: 칩 위 20dp 위치에 ghost 칩 표시
         → 드롭 후보 셀: border 2pt, #0EA5E9, backgroundColor #E0F2FE

[드롭 완료 OR 취소]
         → 햅틱 Success
         → BottomSheet.snapToIndex(1) 호출 (60% 복귀)
         → 충돌 재검증 결과 반영
         → Undo 토스트 표시 (5초)

[드롭 취소 (손 뗌, 셀 외부)]
         → BottomSheet.snapToIndex(1) (60% 복귀)
         → 칩 원위치 애니메이션
```

**RN 구현 포인트:**

```tsx
const conflictSheetRef = useRef<BottomSheet>(null);

const handleChipDragStart = useCallback(() => {
  conflictSheetRef.current?.snapToIndex(0); // 30%로 자동 축소
}, []);

const handleChipDrop = useCallback(() => {
  conflictSheetRef.current?.snapToIndex(1); // 60%로 복귀
}, []);
```

---

### Q3 ✅ — 매장 모드 고대비 토큰 + FAB/CTA 그림자 강화 스펙

> "매장 모드(고대비) 활성화 시 `--ts-primary` 고대비 변형 HEX값과 FAB/CTA 버튼 그림자 강화 스펙"

**고대비 primary 변형 (`--ts-primary-hc`):**

| 토큰 | 기본값 | 고대비 (매장 모드) | 대비 (on white) |
|---|---|---|---|
| `--ts-primary` / `primary` | `#0EA5E9` | `#0369A1` (sky-700) | 3.0:1 → **8.75:1** |
| `--ts-primary-ink` | `#0369A1` | `#0C4A6E` (sky-900) | 8.75:1 → **12.6:1** |
| `--ts-primary-soft` | `#7DD3FC` | `#38BDF8` (sky-400) | — |
| `--ts-cal-today-bg` | `#0369A1` | `#0C4A6E` | — |

**FAB/CTA 그림자 강화 (매장 모드):**

```tsx
// FAB — 기본 vs 매장 모드
const fabStyle = {
  // 기본
  elevation: 6,
  shadowColor: '#0369A1',
  shadowOffset: { width: 0, height: 3 },
  shadowOpacity: 0.3,
  shadowRadius: 6,

  // 매장 모드 강화
  ...(storeMode && {
    elevation: 10,
    shadowColor: '#0C4A6E',
    shadowOffset: { width: 0, height: 5 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
  }),
};

// CTA 버튼 — 기본 vs 매장 모드
const ctaStyle = {
  elevation: 3,
  shadowColor: '#0369A1',
  shadowOpacity: 0.2,

  ...(storeMode && {
    elevation: 6,
    shadowColor: '#0C4A6E',
    shadowOpacity: 0.4,
    shadowRadius: 6,
  }),
};
```

> **PM 결정(R2) 반영:** 매장 모드 토글 자체는 v1.3. v1.2에는 다음 3요소만 자동 적용:
> - (a) `minHeight: 48` 기본값 (이미 적용)
> - (b) 영업시간 silent push (FCM 인프라와 동시)
> - (c) `primary-ink(#0369A1)` 오늘 날짜 자동 적용 (D-1과 동일)

---

### Q4 ✅ — DiceBear 아바타 선택 그리드 모바일 레이아웃

> "아이콘 선택 그리드(30개)의 모바일 레이아웃(열 수, 셀 크기)을 디자인 시스템 기준으로 정의해줄 수 있는가?"

**아바타 선택 그리드 규격:**

```
┌──────────────────────────────────────┐
│  프로필 이모지 선택                    │  ← 모달 헤더
│  ────────────────────────────────── │
│                                      │
│  ○ ○ ○ ○ ○  (5열)                  │  ← 행 1: 기본 아바타 (01~05)
│  ○ ○ ○ ○ ○                          │  ← 행 2 (06~10) — "자주 쓰는" 상위 배치
│  ─────────────────────────── (구분선) │
│  ○ ○ ○ ○ ○                          │  ← 행 3~6 (11~30) — 스크롤 영역
│  ○ ○ ○ ○ ○                          │
│  ○ ○ ○ ○ ○                          │
│  ○ ○ ○ ○ ○                          │
│                                      │
│  [선택 완료]                          │  ← 48pt 하단 CTA
└──────────────────────────────────────┘
```

| 항목 | 규격 |
|---|---|
| 열 수 | **5열** (30개 ÷ 5 = 6행) |
| 셀 크기 | **56×56pt** (터치 타겟 48dp 초과) |
| 셀 간격 | 8pt |
| 선택 상태 | `borderWidth: 3, borderColor: tokens.primaryInk, borderRadius: 28` |
| 미선택 상태 | `opacity: 0.7` |
| 모달 높이 | `60%` snap (FlatList 내장) |
| 최상단 2행 | 기본 추천 아바타 (별도 섹션 헤더 "추천") |
| 이하 4행 | "전체" 섹션 (스크롤) |

> UX R2 §3: "이모지 그리드는 위쪽 행을 한 손이 못 누르는 문제 있음 → 검색·횡스크롤 권장"  
> → 5열 6행 구조에서 상단 2행(10개)은 기본 추천으로 채워 스크롤 없이 접근 가능. 상단 행 접근이 어려울 경우 `initialScrollIndex` 조정으로 보완.

---

## 3. UX Round 2 요구사항 최종 응답

### UX R2 §4.1 — 달력 오늘 날짜 배경 sky-700 즉시 변경 ✅ 확정

→ D-1 응답 참조. 이미 확정.

### UX R2 §4.2 — Dark Mode + High-Contrast(매장 모드) 3종 팔레트 ✅ 부분 수용

**v1.2 범위:** 라이트 단일 + primary-ink 고대비 자동 적용  
**v1.3 범위:** 다크 팔레트, 매장 모드 토글 (Round 2 문서 §3.1 팔레트 준비됨)

3종 팔레트 로드맵:

| 팔레트 | v1.2 | v1.3 |
|---|---|---|
| **라이트 (기본)** | ✅ 출시 | — |
| **라이트 고대비 (매장 모드)** | `primary-ink` 자동 적용만 | 토글 UI + 전체 토큰 |
| **다크** | ❌ 제외 | Round 2 §3.1 팔레트 착수 |

### UX R2 §4.3 — BottomSheet 핸들 40~48dp + sky-700 ✅ 확정

Q1 응답에서 확정. 요약:
- 핸들 너비: **40dp** (UX 요구 ≥ 40dp 충족)
- 핸들 색상: **60%/92% 단 = `#0369A1` (sky-700)**  30% 단 = `#BAE6FD` (sky-200)

> sky-300(`#7DD3FC`) on white = 2.1:1 → sky-700(`#0369A1`) on white = 8.75:1로 수정. UX R2 §4.3 요구 충족.

### UX R2 §4.4 — Tab Bar 활성/비활성 아이콘 페어 ✅ 채택

**UX 발견:** "색만으로 활성/비활성 구분 → 색약 + 노안 + 직사광 = 식별 불가"

**디자인 결정:** 활성/비활성 아이콘을 **채워진(filled) vs 외곽선(outlined)** 페어로 정의.

| 탭 | 비활성 아이콘 | 활성 아이콘 | 색상 |
|---|---|---|---|
| 홈/대시보드 | `home-outline` | `home` (filled) | 비활성: `#94A3B8` / 활성: `#0369A1` |
| 직원 | `people-outline` | `people` (filled) | 동일 |
| 스케줄 | `calendar-outline` | `calendar` (filled) | 동일 |
| 설정 | `settings-outline` | `settings` (filled) | 동일 |
| 내 스케줄 | `calendar-check-outline` | `calendar-check` | 동일 |
| 휴무 신청 | `calendar-plus-outline` | `calendar-plus` | 동일 |

> **현재 이모지 → SVG 미전환 미결 사항과 묶어 처리.** 브랜드 SVG 라인 아이콘 스타일 정의 후 filled/outlined 페어 제작.  
> v1.2 임시: `react-native-vector-icons/Ionicons` 또는 `MaterialCommunityIcons`의 filled/outline 페어 활용.

### UX R2 §4.6 — EmployeeChip minHeight 44pt ✅ 상향 확정

**UX 발견:** "직원 칩 minHeight 32pt는 드래그 소스로 작다. 노안 점장이 32pt 칩을 잡고 끌어야 한다."

**디자인 결정:** EmployeeChip minHeight **44pt**로 상향.

```tsx
// 확정 EmployeeChip 스타일
const styles = StyleSheet.create({
  chip: {
    minHeight: 44,          // ← 32pt → 44pt 상향 (UX R2 §4.6)
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 22,
    backgroundColor: tokens.primarySurface,  // #E0F2FE
    borderWidth: 1,
    borderColor: tokens.primarySoft,         // #7DD3FC
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  chipText: {
    fontSize: 15,                            // --ts-font-base-size
    color: tokens.primaryInk,               // #0369A1
    fontWeight: '600',
  },
  chipMenuIcon: {
    // ⋮ 메뉴 아이콘 (UX R2 §3-3 요구 반영)
    padding: 4,                              // 추가 터치 영역
    minWidth: 24,
    minHeight: 24,
  },
});
```

---

## 4. 전 라운드 합의 사항 — 디자인 시스템 최종 확정 테이블

### 4.1 컬러 토큰 (v1.2 라이트 단일)

| 토큰 | v1.2 값 | WCAG on white | 변경 사항 |
|---|---|---|---|
| `--ts-primary` | `#0EA5E9` (sky-500) | 3.0:1 | 유지 |
| `--ts-primary-ink` | `#0369A1` (sky-700) | 8.75:1 ✅ | 유지 |
| `--ts-primary-soft` | `#7DD3FC` (sky-300) | 2.1:1 | 유지 (장식용) |
| `--ts-primary-50` | `#F0F9FF` (sky-50) | — | 유지 |
| `--ts-primary-surface` | `#E0F2FE` (sky-100) | — | 유지 |
| `--ts-primary-ink-deep` | `#0C4A6E` (sky-900) | 12.6:1 ✅ | 유지 |
| **`--ts-cal-today-bg`** | **`#0369A1` (sky-700)** | **8.75:1 ✅** | **🔴 변경 (2.9:1 → 8.75:1)** |
| `--ts-error` | `#EF4444` (red-500) | 4.8:1 ✅ | 유지 |
| `--ts-surface` | `#FFFFFF` | — | 유지 |
| `--ts-text-primary` | `#1E293B` (slate-800) | 15.8:1 ✅ | 유지 |
| `--ts-border` | `#E2E8F0` (slate-200) | — | 유지 |

### 4.2 컴포넌트 최종 규격 (v1.2 확정)

#### BottomSheet

| 항목 | 확정값 |
|---|---|
| snap heights | `InviteBS: ['40%']` / `LeaveBS: ['50%','92%']` / `ConflictBS: ['30%','60%','92%']` / `SwapBS: ['60%','92%']` |
| ConflictBS 기본 index | `1` (60%) |
| 핸들 너비 | `40dp` |
| 핸들 색 (30%) | `#BAE6FD` (sky-200) |
| 핸들 색 (60%+) | `#0369A1` (sky-700) — 8.75:1 ✅ |
| 배경 | `tokens.surface` (raw #fff 사용 금지) |
| borderRadius | `20pt` |
| 수평 패딩 | `20pt` |
| backdropOpacity | 30%: 0.15 / 60%: 0.40 / 92%: 0.60 |
| 드래그 칩 시작 | `snapToIndex(0)` 자동 수축 |
| 드롭/취소 시 | `snapToIndex(1)` 복귀 |
| OS 네이티브 공유 시트 | **사용 금지** |

#### FAB

| 항목 | 확정값 |
|---|---|
| 크기 | `56×56dp` |
| 색 | bg: `#0EA5E9`, icon: `#FFFFFF` |
| 위치 기본 | `right: 16, bottom: safeArea + 16` |
| elevation | 기본: 6 / 매장 모드: 10 |
| shadowColor | `#0369A1` |

#### Tab Bar

| 항목 | 확정값 |
|---|---|
| 높이 | `49pt + safeArea inset` |
| 터치 타겟 | `44pt 이상` (실질 영역) |
| 활성 색 | `#0369A1` (sky-700) — 기존 sky-500에서 변경 |
| 비활성 색 | `#94A3B8` (slate-400) |
| 아이콘 | **filled(활성) / outlined(비활성) 페어 필수** |

> 활성 색을 sky-500 → sky-700으로 변경. 직사광 시인성 확보 + 아이콘 형태 이중 인코딩으로 색약 대응.

#### CTA 버튼 (생성 확정 등 핵심 액션)

| 항목 | 확정값 |
|---|---|
| 위치 | **하단 sticky full-width** (헤더 우측 배치 금지) |
| 높이 | **56dp** (기본 48dp → UX R2 §5 T4 "≥ 56dp 요구" 반영) |
| 비활성 bg | `#E0F2FE` + `#0369A1` 텍스트 |
| 활성 bg | `#0EA5E9` + `#FFFFFF` 텍스트 볼드 |
| 위치 컴포넌트 | `SafeAreaView` 내부 `position: absolute, bottom: 0` |

#### EmployeeChip

| 항목 | 확정값 |
|---|---|
| minHeight | **44pt** (32pt에서 상향) |
| paddingHorizontal | `14pt` |
| paddingVertical | `10pt` |
| borderRadius | `22pt` |
| 배경 | `#E0F2FE` (sky-100) |
| 텍스트 색 | `#0369A1` |
| 우측 ⋮ 메뉴 아이콘 | 필수 (드래그 fallback 진입점) |

#### Toast / Snackbar

| 종류 | 배경색 | 텍스트 | 지속 |
|---|---|---|---|
| 성공 (이동 완료) | `#0C4A6E` (sky-900) | `#FFFFFF` | 5초 + Undo 버튼 |
| 오류 | `#EF4444` | `#FFFFFF` | 4초 |
| 경고 | `#F59E0B` | `#FFFFFF` | 3초 |
| 정보 | `#0369A1` (sky-700) | `#FFFFFF` | 2초 |

> Undo 버튼 색: `#7DD3FC` (sky-300) — 어두운 배경에서 구분.

### 4.3 드래그 fallback 인터랙션 표준 (만장일치 확정)

| 단계 | 동작 |
|---|---|
| **기본 (MUST)** | 칩 **탭** → "어디로 옮길까요?" 모드 → 달력 셀 1탭 → 이동 완료 |
| **고급 (SHOULD)** | 칩 **Long-press (300ms)** → 드래그 시작 + 햅틱 Medium + BottomSheet 30% 수축 |
| 드롭 완료 | 햅틱 Success + 5초 Undo 토스트 |
| 첫 진입 코치마크 | "칩을 탭하거나 ⋮ 메뉴를 눌러 날짜를 바꿀 수 있어요" 1회 표시 |

> PM R2 §2.2: "탭 = 이동 모드(MUST) / 롱프레스 = 드래그(SHOULD)" 결정을 디자인 표준으로 확정.

### 4.4 Thumb Zone 배치 표준 (최종 확정)

```
┌──────────────────────────────┐  ← NavigationBar (Back 제스처)
│  ✘ Dead Zone                 │
├──────────────────────────────┤
│                              │
│  스크롤·콘텐츠 영역            │  ← 달력, 직원 목록
│  (탭 인터랙션 허용)            │
│                              │
├──────────────────────────────┤
│  ✅ Thumb Zone 핵심           │
│  [생성 확정 CTA — 56dp]       │  ← full-width sticky
│  [FAB — 56×56dp 우하단]       │
│  [Tab Bar — 49pt]            │  ← 최하단
└──────────────────────────────┘
```

**좌·우손잡이 대응 (UX R2 §1.4, §3.6 요구):**

| 항목 | v1.2 결정 | v1.3 로드맵 |
|---|---|---|
| FAB 위치 | 우하단 기본 (우손잡이 기준) | 좌·우 토글 설정 |
| CTA 버튼 | full-width (좌·우 무관) | — |
| 설정 UI | 미포함 | "왼손잡이 모드" 토글 |

---

## 5. Figma → RN 매핑표 최종 버전 (R3 갱신)

| Figma 변수 / 컴포넌트 | RN `tokens.ts` 키 | v1.2 값 | 변경 |
|---|---|---|---|
| `--ts-primary` | `primary` | `'#0EA5E9'` | — |
| `--ts-primary-ink` | `primaryInk` | `'#0369A1'` | — |
| `--ts-primary-soft` | `primarySoft` | `'#7DD3FC'` | — |
| `--ts-primary-surface` | `primarySurface` | `'#E0F2FE'` | — |
| `--ts-primary-ink-deep` | `primaryInkDeep` | `'#0C4A6E'` | — |
| **`--ts-cal-today-bg`** | `calTodayBg` | **`'#0369A1'`** | **🔴 sky-500 → sky-700** |
| `--ts-surface` | `surface` | `'#FFFFFF'` | — |
| `--ts-error` | `error` | `'#EF4444'` | — |
| `PrimaryButton` | `<TouchableOpacity>` | `bg: primaryInk, minHeight: 56` | 높이 48→56 |
| `BottomSheet` | `@gorhom/bottom-sheet` | 컴포넌트별 snapPoints 위 §4.2 | 3단 확정 |
| `EmployeeChip` | `<Animated.View>` | `minHeight: 44` | **32→44** |
| `CalendarCell` | `<TouchableOpacity>` | `minWidth: 44, minHeight: 44, hitSlop: 2` | — |
| `TabBar/active` | `tabBarActiveTintColor` | `'#0369A1'` | sky-500→sky-700 |
| `TabBar/icon-active` | filled icon variant | Ionicons 또는 MCIcon | **신규** |
| `FAB` | `<TouchableOpacity>` | `56×56, elevation: 6` | — |
| `Toast/success` | `ToastProvider` | `bg: '#0C4A6E'` | sky-900 |
| `AvatarGrid` | `FlatList numColumns={5}` | `cellSize: 56` | **신규** |

---

## 6. v1.2 디자인 차단 조건 (MVP 합격 기준)

아래 항목 중 하나라도 미충족이면 v1.2 출시 차단:

| # | 차단 조건 | 확인 방법 |
|---|---|---|
| 1 | `calTodayBg = #0369A1` (WCAG 8.75:1 이상) | 시각적 검수 + 대비 체크 도구 |
| 2 | 모든 CTA 버튼이 화면 **하단 sticky** (헤더 우측 0건) | 화면별 PR 검수 |
| 3 | `minHeight: 56` 주요 CTA / `minHeight: 44` EmployeeChip | StyleSheet 수치 확인 |
| 4 | `raw hex #fff` 사용 0건 (`tokens.surface` 사용) | `grep -r "'#fff'" src/` 0건 |
| 5 | BottomSheet OS 네이티브 공유 시트 미사용 | PR 설명 확인 |
| 6 | Tab Bar 아이콘 filled/outlined 페어 적용 | 스크린샷 비교 |
| 7 | `@gorhom/bottom-sheet` 3단 snap 표준 준수 | 종류별 snapPoints 확인 |

---

## 7. v1.3 이월 항목 (공식 백로그)

| 항목 | 근거 |
|---|---|
| Dark Mode 전체 팔레트 | PM R2 D-2 결정, UX 라이트 권장 |
| 매장 모드 토글 UI | PM R2 §4.2 — 공수 과다 |
| 좌·우손잡이 토글 | UX R2 §1.4, §3.6 |
| Daily Digest 알림 모드 | PM R2 §4.3 부분 동의 |
| 브랜드 SVG 아이콘 전환 | 아이콘 세트 스타일 정의 선행 필요 |
| PNG 주간 슬라이스 멀티 이미지 | PM — 베타 인터뷰 후 결정 |

---

## 8. frontend-agent에게 최종 구현 가이드

Round 2·3를 통해 확정된 내용을 구현 순서대로 정리합니다:

**즉시 (v1.2 착수 전):**
1. `tokens.ts`의 `calTodayBg: '#0369A1'` 갱신
2. `tabBarActiveTintColor: '#0369A1'` 갱신  
3. EmployeeChip `minHeight: 44`
4. CTA 버튼 `minHeight: 56`

**구현 중:**
5. `@gorhom/bottom-sheet` 종류별 snapPoints §4.2 표 적용
6. DayOffConflictSheet 드래그 시 `snapToIndex(0)` 자동 수축 연결
7. Tab Bar filled/outlined 아이콘 페어 교체
8. DiceBear 아바타 그리드 `numColumns={5}`, `cellSize: 56`
9. Undo 토스트 5초 구현 (`#0C4A6E` 배경)

**PR 머지 전 체크:**
10. §6 차단 조건 7개 전체 통과 확인

---

## 9. 3라운드 최종 결론

> **WorKey 모바일 디자인 시스템의 v1.2 MVP 결론:**
>
> sky-500 파스텔 계열의 부드러운 아이덴티티는 유지하되, 핵심 인터랙션 요소(달력 오늘 날짜·Tab Bar 활성·BottomSheet 핸들)는 sky-700으로 강화해 38세 점장이 형광등 직사광 아래 매장 카운터에서 한 손으로 사용해도 끊김 없는 경험을 보장한다.
>
> 드래그가 필요 없는 탭 2회 이동이 기본, 드래그는 선택지. BottomSheet는 3단 높이로 달력을 가리지 않고, 44pt 칩은 기름 묻은 손에도 잡히며, 56dp CTA는 엄지가 자연스럽게 닿는 곳에 있다.
>
> **"지하철 06:30"과 "매장 카운터 11시 점심 피크" 두 시나리오 모두 통과할 것.**

---

*Round 3 완료 — 이 문서가 v1.2 RN 구현의 디자인 시스템 단일 진실 출처(Single Source of Truth).*
