# [R1-DESIGN] Design Round 1 Evidence
**작성자:** design-agent  
**날짜:** 2026-04-29  
**안건:** WorKey 모바일 앱(React Native) 개발 킥오프 — 디자인 이식 및 모바일 UI/UX 가이드라인

---

## 1. 디자인 시스템 현황 요약

### 1.1 Primary 컬러 토큰 (2026-04-25 갱신 기준)

| CSS 토큰 | HEX 값 | Tailwind 참조 | 용도 |
|---|---|---|---|
| `--ts-primary` | `#0EA5E9` | sky-500 | 주요 액션, CTA 버튼, 오늘 날짜 배경 |
| `--ts-primary-ink` | `#0369A1` | sky-700 | 텍스트 위 primary 색상 (대비 8.75:1 충족) |
| `--ts-primary-soft` | `#7DD3FC` | sky-300 | 소프트 강조, Blob 배경 |
| `--ts-primary-50` | `#F0F9FF` | sky-50 | 최소 배경 틴트 |
| `--ts-primary-100 / surface` | `#E0F2FE` | sky-100 | 카드 배경, 서피스 |
| `--ts-primary-ink-dark` | `#0369A1` | sky-700 | 진한 잉크 (= primary-ink) |
| `--ts-primary-ink-deep` | `#0C4A6E` | sky-900 | 최심층 잉크 (다크 배경용) |
| `--ts-cal-today-bg` | `#0EA5E9` | = primary | 달력 오늘 날짜 배경 |
| `--ts-cal-work-tint` | `#E0F9FF` | sky-50 정렬 | 근무일 틴트 |
| `--ts-blob-sky` | `#7DD3FC` | sky-300 | 배경 장식 Blob |

> ⚠️ **미결 사항:** `background: '#fff'` 카드 3~5곳이 아직 하드코딩 상태. `var(--ts-surface)`로 교체 필요.  
> ⚠️ 시연용 chrome의 raw hex도 토큰화 대기 중.

---

### 1.2 타이포그래피 토큰 (현황 및 모바일 이식 기준)

현재 `--ts-font-*-size` 토큰이 JSX 리터럴 fontSize(11, 15 등)로 혼용되고 있어 **모바일 이식 전 토큰 통일이 선행되어야 함**.

| 토큰 (권장) | 값 | 용도 |
|---|---|---|
| `--ts-font-xs-size` | 11px / 11sp | 보조 라벨, 캘린더 날짜 |
| `--ts-font-sm-size` | 13px / 13sp | 본문 보조 텍스트 |
| `--ts-font-base-size` | 15px / 15sp | 기본 본문 |
| `--ts-font-lg-size` | 17px / 17sp | 섹션 헤더 |
| `--ts-font-xl-size` | 20px / 20sp | 화면 제목 |

> RN에서는 `px` 대신 `sp` 단위 사용 (시스템 폰트 크기 설정 반영).  
> `StyleSheet` 내 `fontSize` 값은 위 토큰 대응 숫자로 고정하되, **접근성 설정을 허용**하려면 `PixelRatio.getFontScale()` 적용 고려.

---

## 2. 핵심 논의 사항 검토

### 2.1 디자인 이식 — 모바일 컴포넌트 표준 가이드

WorKey 디자인 시스템에서 정의된 핵심 컴포넌트의 RN 이식 규격입니다.

#### 2.1.1 BottomSheet

| 항목 | 규격 |
|---|---|
| 핸들 바 | 너비 32pt, 높이 4pt, 색상 `--ts-primary-soft(#7DD3FC)`, 상단 마진 8pt |
| 배경 | `--ts-surface (#fff → var(--ts-surface) 교체 대상)`, `borderRadius: 20` |
| 패딩 | 수평 20pt, 상단 12pt, 하단 safe-area + 16pt |
| 드래그 dismiss | `PanGestureHandler` 또는 `@gorhom/bottom-sheet` 라이브러리 |
| 반투명 배경 | `rgba(0,0,0,0.4)` |

**WorKey 사용 맥락:** 직원 초대 바텀시트, 휴무 신청 바텀시트(`LeaveRequestSheet`), 충돌 날짜 상세 바텀시트

#### 2.1.2 FAB (Floating Action Button)

| 항목 | 규격 |
|---|---|
| 크기 | 최소 56×56dp (Material 48dp 기준 초과) |
| 색상 | bg: `--ts-primary(#0EA5E9)`, icon: `#fff` |
| 위치 | right: 16pt, bottom: safe-area + 16pt |
| 그림자 | `elevation: 6` (Android) / `shadow*` (iOS) |
| 아이콘 | 현재 이모지 → 추후 브랜드 SVG 아이콘으로 교체 예정 |

**WorKey 사용 맥락:** 스케줄 생성 진입점, 직원 추가 버튼

#### 2.1.3 Tab Bar (Bottom Navigation)

| 항목 | 규격 |
|---|---|
| 높이 | 49pt (iOS HIG) + safe-area bottom inset |
| 탭 아이템 크기 | 최소 44×44pt 터치 타겟 |
| 활성 색상 | `--ts-primary(#0EA5E9)` |
| 비활성 색상 | `#94A3B8` (slate-400) |
| 배경 | `#FFFFFF` with `borderTopColor: #E2E8F0` |
| 폰트 크기 | 10pt (라벨), 볼드 활성 |

**WorKey 사용 맥락:** 관리자 탭(홈/직원/설정), 직원 탭(스케줄/휴무신청)

#### 2.1.4 Modal

| 항목 | 규격 |
|---|---|
| 배경 오버레이 | `rgba(0,0,0,0.5)` |
| 컨테이너 | 너비 90%, 최대 380pt, `borderRadius: 16` |
| 패딩 | 24pt |
| CTA 버튼 | full-width, height 48pt, `--ts-primary` 배경 |
| 취소 | 텍스트 버튼, `--ts-primary-ink` 색상 |
| 애니메이션 | `fade + scale(0.95 → 1.0)`, 200ms |

**WorKey 사용 맥락:** 매장 변경 확인, 스케줄 생성 확정, 생성 실패 알림

#### 2.1.5 Toast / Snackbar

| 항목 | 규격 |
|---|---|
| 위치 | 화면 하단, safe-area + 24pt |
| 크기 | 최소 높이 48pt, 수평 패딩 16pt |
| 색상 (성공) | bg: `#0EA5E9`, text: `#fff` |
| 색상 (에러) | bg: `#EF4444`, text: `#fff` |
| 색상 (경고) | bg: `#F59E0B`, text: `#fff` |
| 지속 시간 | 2,000ms (기본), 4,000ms (에러) |
| 애니메이션 | bottom slide-in 150ms, fade-out 300ms |

**WorKey 사용 맥락:** 휴무 재배치 성공 "N일로 이동됨", 스케줄 생성 오류 안내

---

### 2.2 터치 타겟 최소 크기 기준

| 기준 | 최소 크기 | 비고 |
|---|---|---|
| Apple HIG | 44×44pt | iOS 권장 |
| Material Design | 48×48dp | Android 권장 |
| **WorKey 적용 기준** | **48×48dp (44pt 이상)** | 두 기준 중 더 큰 값 적용 |
| 캘린더 날짜 셀 | 최소 44×44pt | 드래그 & 드롭 대상 포함 |
| 휴무 신청자 칩 | 최소 44×32pt (너비 가변) | 드래그 소스 |
| 탭 바 아이템 | 전체 탭 영역 / n 탭 수 | 실질 터치 영역 보장 |
| FAB | 56×56dp | 핵심 액션, 여유 크기 |
| 바텀시트 버튼 | 48×48dp 이상, full-width 권장 | 단일 CTA |

> **중요:** 현재 `+ 팀원 추가` 등 버튼이 너무 밝아 비활성화처럼 보이는 문제가 `--ts-primary-ink(sky-700)` 교체로 수정됨. RN에서도 동일 색상값 적용 필수.

---

### 2.3 Thumb Zone 매핑 — 한 손 조작 최적화

**대상 페르소나:** 최기준 (카페 점장, 바쁜 근무 현장에서 한 손으로 일정 등록)

```
┌─────────────────────────────┐
│  ← 뒤로  [헤더 제목]  [액션] │  ← ⚠️ 도달 어려움 (Dead Zone)
├─────────────────────────────┤
│                             │
│  [콘텐츠 영역 — 달력/목록]   │  ← 자연스러운 스크롤 구역
│                             │
│                             │
├─────────────────────────────┤
│  [핵심 CTA: 생성 확정]       │  ← ✅ Thumb Zone (쉽게 닿음)
│  [탭 바]                    │  ← ✅ Thumb Zone 하단
└─────────────────────────────┘
```

| UI 요소 | 배치 위치 | Thumb Zone 적합성 |
|---|---|---|
| 스케줄 생성 확정 버튼 | 화면 하단 full-width | ✅ 최적 |
| FAB (직원 추가) | 우하단 | ✅ 적합 |
| 탭 바 네비게이션 | 최하단 | ✅ 최적 |
| 날짜 칩 드래그 대상 | 달력 중앙부 | ⚠️ 상단 날짜는 도달 어려움 → 스크롤 유도 |
| 직원 탭 필터 | 달력 상단 | ⚠️ 가로 스크롤로 보완 |
| 뒤로가기 / 헤더 우측 액션 | 최상단 | ❌ Dead Zone → NavigationBar 기본 제스처로 대체 |

**권고사항:**
- 휴무 수집 뷰의 `생성 확정` 버튼은 반드시 화면 **하단 고정 (sticky bottom)** 배치
- 헤더 우측의 "생성 확정" 배치 안 됨 (디자인 문서 레이아웃 현재 그렇게 되어 있으나, RN 구현 시 하단 이동 권장)
- 충돌 바텀시트 내 칩 드래그는 손가락 중간 위치(중단부)에 배치 — 바텀시트가 절반 높이로 올라왔을 때 달력 상단 절반만 보이는 구조로 상단 날짜 드롭 영역 접근성 개선

---

### 2.4 컬러/타이포 토큰 모바일 대응

#### Dark Mode 대응

| 라이트 모드 토큰 | 다크 모드 대응값 | 비고 |
|---|---|---|
| `--ts-primary (#0EA5E9)` | `#38BDF8` (sky-400) | 다크 배경 대비 확보 |
| `--ts-primary-ink (#0369A1)` | `#7DD3FC` (sky-300) | 다크 배경 위 텍스트 |
| `--ts-surface (#fff)` | `#0F172A` (slate-900) | 카드 배경 |
| `--ts-surface-card` | `#1E293B` (slate-800) | 중첩 카드 |
| 텍스트 기본 | `#1E293B` | `#F1F5F9` (slate-100) |
| 달력 오늘 `--ts-cal-today-bg` | `#0EA5E9` → `#38BDF8` | 대비 유지 |

> ⚠️ 현재 디자인 문서에 Dark Mode 토큰이 미정의 상태. **RN 구현 전 다크 팔레트 확정 필요.**  
> RN에서는 `useColorScheme()` 훅 + `Appearance` API로 시스템 설정 감지.

#### 야외/매장 환경 시인성 (고조도 환경)

| 대응 | 상세 |
|---|---|
| 최소 WCAG AA 대비 4.5:1 | `--ts-primary-ink(#0369A1)` on white: 8.75:1 ✅ |
| 충돌 빨간 배지 | `#EF4444` on white: 4.8:1 ✅ (명확한 경고 시인) |
| 달력 오늘 날짜 배경 | `#0EA5E9` + 흰 텍스트: 2.9:1 ⚠️ → 흰 텍스트 볼드 처리 또는 `#0369A1` 배경으로 대체 고려 |
| 버튼 텍스트 | 흰 텍스트 on `#0EA5E9`: 볼드 16pt 이상 권장 (대형 텍스트 기준 3:1 충족) |

---

## 3. 디자인 시스템 → RN 컴포넌트 매핑표

| Figma 컴포넌트/변수명 | RN 컴포넌트 | prop 매핑 |
|---|---|---|
| `PrimaryButton` | `<TouchableOpacity style={styles.primaryBtn}>` | `backgroundColor: '#0EA5E9'`, `minHeight: 48` |
| `PrimaryButton (ink)` | `<TouchableOpacity>` | `backgroundColor: '#0369A1'` |
| `TextButton` | `<TouchableOpacity>` | `color: '#0369A1'`, `minHeight: 44` |
| `BottomSheet` | `@gorhom/bottom-sheet <BottomSheet>` | `handleIndicatorStyle`, `backgroundStyle` |
| `CalendarCell` | `<TouchableOpacity style={styles.cell}>` | `minWidth: 44`, `minHeight: 44` |
| `EmployeeChip` | `<Animated.View>` (PanGesture) | `minHeight: 32`, `paddingHorizontal: 12` |
| `BadgeConflict (🔴)` | `<View style={styles.badge}>` | `backgroundColor: '#EF4444'`, `borderRadius: 10` |
| `TabBar` | `@react-navigation/bottom-tabs` | `tabBarActiveTintColor: '#0EA5E9'` |
| `FAB` | `<TouchableOpacity style={styles.fab}>` | `width: 56, height: 56, borderRadius: 28` |
| `Toast` | 커스텀 `ToastProvider` | `backgroundColor` 상황별 분기 |
| `Modal` (확인 다이얼로그) | `<Modal>` (RN core) | `transparent: true`, overlay `rgba(0,0,0,0.5)` |
| `--ts-primary` | `colors.primary` | `'#0EA5E9'` |
| `--ts-primary-ink` | `colors.primaryInk` | `'#0369A1'` |
| `--ts-primary-soft` | `colors.primarySoft` | `'#7DD3FC'` |
| `--ts-primary-surface` | `colors.surface` | `'#E0F2FE'` |

---

## 4. 화면별 모바일 디자인 체크리스트

### 4.1 휴무 수집 뷰 (핵심 화면)

- [x] 달력 날짜 셀 최소 44×44pt 확보
- [x] 충돌 날짜 빨간 배지 시인성 확인 (WCAG 4.5:1 이상)
- [ ] `생성 확정` 버튼 → 하단 sticky 배치로 변경 (현재 헤더 우측)
- [ ] 드래그 중 바텀시트 dismiss 애니메이션 (겹침 방지)
- [ ] 직원 탭 필터 가로 스크롤 시 터치 타겟 44pt 이상
- [ ] `+ 휴무 수동 추가` 버튼 최소 48pt 높이

### 4.2 직원 초대 바텀시트

- [x] 카카오톡 전송 버튼 full-width CTA (48pt)
- [x] 링크 복사 보조 버튼 (44pt 이상)
- [ ] 바텀시트 핸들 터치 영역 최소 44pt 확보
- [ ] safe-area bottom 반영

### 4.3 직원 스케줄 캘린더

- [x] 월별 달력 뷰 (파스텔 블루 계열 — 귀엽게)
- [x] 오늘 날짜 `--ts-primary` 배경
- [ ] 근무일/휴무일 색상 대비 야외 확인
- [ ] 달력 헤더 공휴일 컬러 적용

---

## 5. 미결 디자인 리스크 및 권고

| 이슈 | 심각도 | 권고 조치 |
|---|---|---|
| Dark Mode 팔레트 미정의 | 🟠 높음 | 다크 토큰 테이블 우선 정의 후 RN 구현 |
| 달력 오늘 날짜 `#0EA5E9` 대비 부족 | 🟡 중간 | 볼드 텍스트 or `#0369A1` 배경 전환 |
| JSX fontSize 리터럴 혼용 | 🟡 중간 | 토큰 치환 후 RN prop 매핑 |
| 헤더 `생성 확정` 위치 | 🟠 높음 | Thumb Zone 기준 하단 CTA 재배치 |
| 이모지 아이콘 → SVG 미전환 | 🟢 낮음 | v1.2 이후 진행 (우선순위 낮음) |
| `background: '#fff'` 하드코딩 | 🟡 중간 | `var(--ts-surface)` / `colors.surface` 치환 |

---

## 6. Round 1 결론

WorKey의 sky 계열 파스텔 디자인 시스템은 모바일 이식성이 높으나, 다음 3가지를 **RN 구현 착수 전** 확정해야 합니다:

1. **Dark Mode 컬러 토큰 정의** — 야외/매장 환경 야간 사용 시나리오 포함
2. **`생성 확정` CTA를 하단 sticky로 변경** — 한 손 조작 페르소나(최기준) 기준 Thumb Zone 최적화
3. **CSS 토큰 → RN `StyleSheet` 상수 파일 (`colors.ts`, `typography.ts`) 분리** — 토큰 일관성 보장

> frontend-agent에게: `colors.ts` 파일에 위 매핑표 기준으로 토큰 상수를 선언하고, `BottomSheet`, `FAB`, `Toast` 등 공통 컴포넌트는 반드시 위 규격을 준수해 주세요. 특히 `minHeight: 48` 강제 적용을 컴포넌트 기본값으로 설정할 것을 권고합니다.
