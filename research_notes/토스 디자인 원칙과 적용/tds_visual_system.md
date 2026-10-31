# Toss Design System (TDS): visual and component system, with concrete values for a dark web desktop app

Research date: 2026-10-31.

**Method note.** In this cloud session, tossmini-docs.toss.im, developers-apps-in-toss.toss.im and toss.tech could not be fetched (their DNS was blocked by the session network allowlist). To get past that, the most authoritative values below were **read directly from Toss's own published npm packages**, which `toss-public`, `raon0211@toss.im` and `kiwi.jang@toss.im` maintain:
- `@toss/tds-colors@0.1.0`, published 2025-09-25: colors.light.css, colors.dark.css, colors.scss.
- `@toss/tds-typography@0.0.3`.
- `@toss/tds-mobile@2.5.1`. The package was created 2025-09-25 and last modified 2026-07-29.

These are compiled production builds, so their values are "sourced" in the strongest sense: they are the shipped code. Source links:
- [npm @toss/tds-colors](https://www.npmjs.com/package/@toss/tds-colors)
- [npm @toss/tds-typography](https://www.npmjs.com/package/@toss/tds-typography)
- [npm @toss/tds-mobile](https://www.npmjs.com/package/@toss/tds-mobile)

The official docs pages that surfaced in search were:
- [TDS Mobile Colors](https://tossmini-docs.toss.im/tds-mobile/foundation/colors/)
- [TDS React Native Colors](https://tossmini-docs.toss.im/tds-react-native/foundation/colors/)

## 1. What Toss has published about TDS (docs, packages, articles, font)

### Takeaway
Toss now publishes TDS publicly for its Apps-in-Toss mini-app platform: docs at tossmini-docs.toss.im and npm packages for colors, typography and the React Mobile/RN components. Its main design writing covers a 2025 color system rebuild (OKLCH, semantic tokens) and the custom typeface Toss Product Sans, which Toss built for numbers and financial symbols.

### Cited Findings
- TDS docs for Mobile (React web) and React Native live at tossmini-docs.toss.im. Colors are consumed from the `colors` object of `@toss/tds-colors`, or from `@toss/tds-react-native` for RN — [TDS Mobile Colors](https://tossmini-docs.toss.im/tds-mobile/foundation/colors/); [TDS RN Colors](https://tossmini-docs.toss.im/tds-react-native/foundation/colors/)
- npm packages on the registry (checked 2026-10-31):
  - `@toss/tds-colors` 0.1.0, published 2025-09-25.
  - `@toss/tds-typography` 0.0.3.
  - `@toss/tds-mobile` 2.5.1, modified 2026-07-29.
  - `@toss/tds-react-native` 2.0.5.
  - `@toss/tds-mobile-ait` 2.5.1.
  - Source: [npm registry @toss/tds-mobile](https://registry.npmjs.org/@toss/tds-mobile)
- The components `@toss/tds-mobile` 2.5.1 exports include: AlertDialog, ConfirmDialog, Badge, BarChart, DoughnutChart, BoardRow, BottomCTA, FixedBottomCTA, BottomInfo, BottomSheet, Bubble, Button, CTAButton, IconButton, TextButton, Checkbox, Chip, DatePicker, FadeIn, FullScreenLoader, GridList, HighlightUI, List, ListHeader, ListFooter, ListRow, ListRowLoader, Loader, LoadingCompleteView, Menu, Modal, Navigation/TopNavigation, NumericSpinner, Paragraph, PointToast, ProgressBar, ProgressStepper, Rating, Result, SearchField, SegmentedControl, Selector, Skeleton, Slider, Spacing, Stepper/StepperRow, Switch, Tab, TableRow, TextField/TextArea, Toast, Tooltip, Top, and ThemeProvider/ColorSchemeArea — [npm @toss/tds-mobile](https://www.npmjs.com/package/@toss/tds-mobile) (taken from index.d.ts)
- toss.tech article "달리는 기차 바퀴 칠하기: 7년만의 컬러 시스템 업데이트" (painting the wheels of a running train: the first color system update in 7 years):
  - TDS rebuilt its color system and token system from scratch for the first time in 7 years.
  - A summary describes the rebuild as OKLCH plus semantic tokens plus auto-generated code.
  - The work included reimplementing token references for themes, modes and variants.
  - Sources: [toss.tech](https://toss.tech/article/tds-color-system-update) (full text not fetchable here); summary via [Velopers](https://velopers.kr/post/5984)
- Toss Product Sans (TPS) is a custom typeface built with Sandoll:
  - Hangul is based on Sandoll 고딕neo1 (Gothic neo1) with only minor changes. Latin, numerals and punctuation were newly designed.
  - The project ran for about 9 months, from July 2020 to March 2021.
  - It ships in 3 builds: general, Toss-app (with altered punctuation), and a lightweight web version.
  - Source: [Sandoll TPS page](https://www.sandoll.co.kr/TossProductSans)
- TPS rationale (Toss Feed blog): financial UIs depend on numbers and symbols.
  - The font has **tabular (fixed-width) numerals** for live-changing values such as real-time stock quotes ("이 화면에서 숫자가 고정폭이 아니라면 어지럽겠죠", roughly "if the numbers on this screen weren't fixed-width, it would be dizzying").
  - It has **proportional numerals** for big, prominent amounts.
  - %, comma, +, - and arrows were resized and given more spacing for legibility.
  - Source: [blog.toss.im – 토스 프로덕트 산스 제작기](https://blog.toss.im/article/beginning-of-tps)
- Shipped font stack in tds-mobile CSS: `font-family: 'Toss Product Sans', 'Tossface', 'SF Pro KR', 'SF Pro Display', 'SF Pro Icons', -apple-system, …`. Tossface is Toss's emoji font. Code uses `SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, Courier New, monospace` — [npm @toss/tds-mobile](https://www.npmjs.com/package/@toss/tds-mobile)
- Third-party site oppadu lists the Toss blue as #0064FF. That is the **brand/logo** blue, not the TDS UI primary. A GitHub PR on ko-design-md explicitly corrected a catalog to the TDS published value #3182F6, citing `@toss/tds-colors` — [oppadu](https://www.oppadu.com/tools/design-systems-site/brand/toss.html); [ko-design-md PR #418](https://github.com/CaesiumY/ko-design-md/pull/418)

### Inferences
- For a web app, TPS is not openly licensed. Sandoll and Toss offer it for Toss products, and one blog reports there are no public release plans. The practical substitute is **Pretendard**, which is open-source and has a similar neo-gothic Hangul with good Latin and digits. Use `font-variant-numeric: tabular-nums` wherever numbers update live; that reproduces TPS's fixed-width-digit intent.

### Gaps
- I could not read toss.tech or tds docs prose directly: the hosts were blocked in this session, so they must be allowed in network settings to verify the docs' usage guidance text.
- The Simplicity talks on TDS were not reviewed.
- The icon system (Toss icons and Tossface) was not researched.

## 2. Concrete tokens (colors, typography, radius, spacing)

### Takeaway
All values below were read from Toss's shipped packages:
- Grey runs #F9FAFB to #191F28 in light and is remapped to #202027 to #FFFFFF in dark.
- Primary is blue500: #3182F6 in light, #3485FA in dark.
- Dark mode backgrounds are #17171C (base), #101013 (grey/sunken), #202027 (layer 1) and #2C2C35 (layer 2/float).
- Typography has 20 levels (t1–t7 plus st1–st13), running from 30px down to 11px.

### Cited Findings: color (from `@toss/tds-colors@0.1.0`, colors.light.css / colors.dark.css) — [npm](https://www.npmjs.com/package/@toss/tds-colors)

The token names are CSS variables `--adaptive*`, which switch between light and dark. The scss also exposes fixed `darkTheme*` and `inverseGrey*` sets.

**Grey**

| step | light | dark |
|---|---|---|
| 50 | #f9fafb | #202027 |
| 100 | #f2f4f6 | #2c2c35 |
| 200 | #e5e8eb | #3c3c47 |
| 300 | #d1d6db | #4d4d59 |
| 400 | #b0b8c1 | #62626d |
| 500 | #8b95a1 | #7e7e87 |
| 600 | #6b7684 | #9e9ea4 |
| 700 | #4e5968 | #c3c3c6 |
| 800 | #333d4b | #e4e4e5 |
| 900 | #191f28 | #ffffff |

- The light greys are blue-tinted. The dark greys are neutral with a slight violet cast (#17171c family).
- Dark grey is **inverted**: grey900 is the primary text color in both themes, and it is white in dark.

**Blue (primary)**

| step | light | dark |
|---|---|---|
| 50 | #e8f3ff | #202c4d |
| 100 | #c9e2ff | #23386a |
| 200 | #90c2ff | #25478c |
| 300 | #64a8ff | #265ab3 |
| 400 | #4593fc | #2970d9 |
| 500 | #3182f6 | #3485fa |
| 600 | #2272eb | #449bff |
| 700 | #1b64da | #61b0ff |
| 800 | #1957c2 | #8fcdff |
| 900 | #194aa6 | #c8e7ff |

- `disabledBlue500` is #c9e2ff in light and rgba(49,130,246,0.2) in dark.

**Red**

| step | light | dark |
|---|---|---|
| 50 | #ffeeee | #3c2020 |
| 100 | #ffd4d6 | #562025 |
| 200 | #feafb4 | #7a242d |
| 300 | #fb8890 | #9e2733 |
| 400 | #f66570 | #ca2f3d |
| 500 | #f04452 | #f04251 |
| 600 | #e42939 | #fa616d |
| 700 | #d22030 | #fe818b |
| 800 | #bc1b2a | #ffa8ad |
| 900 | #a51926 | #ffd1d3 |

**Green, orange, yellow (steps 50/500/700/900 only)**

| hue | 50 | 500 | 700 | 900 |
|---|---|---|---|---|
| Green, light | #f0faf6 | #03b26c | #029359 | #027648 |
| Green, dark | #153729 | #16bb76 | #4ee4a6 | #ccffea |
| Orange, light | #fff3e0 | #fe9800 | #f57800 | #e45600 |
| Orange, dark | #3d2500 | #f18600 | #ffa861 | #ffe4d6 |
| Yellow, light | #fff9e7 | #ffc342 | #faa131 | #dd7d02 |
| Yellow, dark | #3d2d1a | #ffb134 | #ffd68a | #fff1d4 |

- Yellow 300 is #ffdd78 (light) and #eb8b1e (dark).

**Teal and purple (step 500 only)**

| hue | light | dark |
|---|---|---|
| Teal500 | #18a5a5 | #2eaab2 |
| Purple500 | #a234c7 | #ae3dd1 |

- Teal and purple also have full 50–900 scales, but they are not reproduced here.

**Backgrounds**

| token | light | dark |
|---|---|---|
| background | #ffffff | **#17171c** |
| greyBackground / backgroundLevelB01 | #f2f4f6 | **#101013** |
| layeredBackground / backgroundLevel01 | #ffffff | **#202027** |
| floatBackground / backgroundLevel02 | #ffffff | **#2c2c35** |
| hairlineBorder | #e5e8eb | #3c3c47 |
| dimmed (modal scrim) | rgba(0,0,0,0.2) | rgba(0,0,0,0.56) |
| pcScreenBg | #f6f7f9 | #202027 |

**Opacity greys (overlays on any surface)**

| step | light | dark |
|---|---|---|
| greyOpacity50 | rgba(0,23,51,0.02) | rgba(209,209,253,0.05) |
| greyOpacity100 | rgba(2,32,71,0.05) | rgba(217,217,255,0.11) |
| greyOpacity200 | rgba(0,27,55,0.1) | rgba(222,222,255,0.19) |
| greyOpacity300 | rgba(0,29,58,0.18) | rgba(224,224,255,0.27) |
| greyOpacity500 | rgba(3,24,50,0.46) | rgba(242,242,255,0.47) |
| greyOpacity700 | rgba(3,18,40,0.7) | rgba(253,253,255,0.75) |
| greyOpacity900 | rgba(2,9,19,0.91) | #ffffff |

- Dark opacity greys use a faint blue-violet white rather than pure white.

### Cited Findings: typography (from `@toss/tds-typography@0.0.3`) — [npm](https://www.npmjs.com/package/@toss/tds-typography)
- Level order is `t1, st1, st2, st3, t2, st4, st5, st6, t3, st7, t4, st8, st9, t5, st10, t6, st11, t7, st12, st13`. The "t" levels are primary steps; the "st" levels are in-between sub-steps.
- `defaultTypographyRule` = [30,29,28,27,26,25,24,23,22,21,20,19,18,17,16,15,14,13,12,11]. That gives these primary levels at default size:

| level | font size | line height |
|---|---|---|
| t1 | 30px | 40 |
| t2 | 26px | 35 |
| t3 | 22px | 31 |
| t4 | 20px | 29 |
| t5 | 17px | 25.5 |
| t6 | 15px | 22.5 |
| t7 | 13px | 19.5 |

- Sub-steps include st13 = 11/16.5, st12 = 12/18 and st11 = 14/21.
- Line-height rule from the size map:
  - 11–18px use 1.5×.
  - Above that, line height is size + 9 up to 29px (e.g. 20→29, 24→33).
  - From 30px it is size + 10 (30→40, 42→52).
- Each fixed size also defines:
  - icon height (e.g. 17→19px, 15→17px).
  - Badge font, padding and radius (e.g. text 17 → badge 10px font, padding 3px 7px, radius 9px; text 30 → 14px, 4px 8px, radius 13px).
- iOS Dynamic Type (Large…A11y_xxxLarge) and Android fontScale rules rescale the whole scale, so TDS treats accessibility font scaling as a first-class concern.

### Cited Findings: radius, sizes, spacing (from `@toss/tds-mobile@2.5.1` compiled styles) — [npm](https://www.npmjs.com/package/@toss/tds-mobile)

**Button sizes**

| size | min height | radius | font | padding | min width |
|---|---|---|---|---|---|
| xlarge | 56px | 16px | t5 (17px) | 2px 28px (15px 28px when inline) | 96px |
| large | 48px | 14px | t5 (17px) | 2px 16px | 80px |
| medium | 38px | 10px | t6 (15px) | 2px 16px | 64px |
| small | 32px | 8px | t7 (13px) | 2px 10px | 52px |

- Button font weight is 600.
- Display options: `inline` (auto width), `block` (100%), `full` (100% and radius 0).
- Button API types:
  - `color: 'primary' | 'danger' | 'light' | 'dark'`
  - `variant: 'fill' | 'weak'`
  - `size: 'small' | 'medium' | 'large' | 'xlarge'`
  - `display: 'inline' | 'block' | 'full'`
- Most frequent `borderRadius` literals in the components are 8, 12, 13, 10, 14, 16, 18 and 20px, plus 50%/100% for circles.
- Some top-edge sheet/header surfaces use `borderTopLeftRadius/RightRadius: 20px`.
- One size map (variable names minified, so the component is unidentified) uses spacing small 8 / medium 12 / large 16 / xlarge 24px. Another uses tiny/small 12px and medium/large 16px.
- ListRowLoader `verticalPadding` options are extraSmall, small, medium (default) and large.

### Inferences
- Use the dark surface ladder #101013 < #17171c < #202027 < #2c2c35 for elevation. In dark mode, lighter means higher: no shadows, just tone steps. For a desktop app:
  - #101013 for the window or sidebar background.
  - #17171c for the main canvas.
  - #202027 for cards.
  - #2c2c35 for popovers and sheets.
- The text hierarchy in dark is roughly:
  - grey900 #fff for titles.
  - grey800 #e4e4e5 or grey700 #c3c3c6 for body.
  - grey600 #9e9ea4 for secondary text.
  - grey500 #7e7e87 for captions and disabled.
- Spacing is not a published token scale. Observed values cluster on a 4/8 rhythm (4, 8, 12, 16, 20, 24) with 20px horizontal screen padding (button 'medium/large' content variants use "2px 20px" / "4px 20px").

### Gaps
- No standalone spacing or radius token set was found. Values are per-component.
- Exact ListRow heights, BottomSheet radius and Toast metrics were not isolated because the build's variable names are minified.
- OKLCH generation parameters from the toss.tech article were not read.

## 3. Component patterns and usage guidance

### Takeaway
TDS centers screens on:
- **Top**: a large title and subtitle block at the top of the screen.
- **ListRow**: rows with left asset, text stack and right accessory.
- A sticky bottom CTA (**BottomCTA/FixedBottomCTA**) using fill or weak Buttons.
- BottomSheet, Toast, Skeleton and Loader for feedback.

### Cited Findings
- Components with clear roles (from export names and JSDoc in [@toss/tds-mobile](https://www.npmjs.com/package/@toss/tds-mobile)):
  - **Top** (with lower button/CTA props): the page title area.
  - **ListHeader/ListRow/ListFooter**: list structure. ListRow has icon, texts and icon-button sub-parts, a divider style option and a ListRowLoader skeleton variant (square, circle or bar).
  - **BottomCTA / FixedBottomCTA (TypeB)**: the main action pinned at the bottom.
  - **BottomSheet**: has single and double CTA variants.
  - **AlertDialog / ConfirmDialog**: dialogs.
  - **Toast / PointToast**: transient messages.
  - **Badge**: sized relative to the adjacent text size, via the typography package's badge map.
  - **Tab / SegmentedControl / Chip**: switching and filtering.
  - **Skeleton**: placeholder loading.
  - **Result / LoadingCompleteView**: completion states.
  - **BarChart / DoughnutChart**: data display.
  - **TableRow / BoardRow**: tables and boards.
- Button hierarchy is expressed as color × variant:
  - `fill` (solid) is the primary action.
  - `weak` (tinted, low-emphasis background) is secondary.
  - `danger` is for destructive actions.
  - `light/dark` are neutral.
  - Disabled and loading states use opacity:
    - Loading dots pulse to 0.7 opacity (fill) or 0.24 (weak).
    - Over a disabled button they pulse to 0.2 (fill) or 0.14 (weak).
    - Each pulse runs 0.6s with ease-out and repeats in reverse.
  - Source: [npm @toss/tds-mobile](https://www.npmjs.com/package/@toss/tds-mobile)
- Hover only applies on fine pointers: `@media (hover: hover) and (pointer: fine) { &:hover { background: greyOpacity200 } }`. Pressed/active rows use greyOpacity200 or grey100 backgrounds with `transition: background-color 0.2s ease` — [npm @toss/tds-mobile](https://www.npmjs.com/package/@toss/tds-mobile)

### Inferences
- A "weak" button is likely blue50 background with blue500/600 text (dark: #202c4d bg, #449bff-ish text). This was **estimated**: the exact mapping was not isolated.
- For a desktop app:
  - Use ListRow-style rows (about 56–64px tall, 20–24px side padding) instead of bordered tables.
  - Use one primary fill button per view.
  - Use the weak variant for secondary actions.
  - Use the Skeleton/ListRowLoader approach instead of spinners for list loading.

### Gaps
- Official prose guidance ("when to use each") from the docs was not retrievable. The roles above are inferred from API names and JSDoc.

## 4. Dark mode, charts and number emphasis

### Takeaway
TDS handles dark mode through "adaptive" tokens. The same semantic name remaps per theme:
- Greys invert.
- Accents get lighter in dark: blue500 #3182f6→#3485fa, and higher steps move toward pastel.
- Low steps become dark tinted fills: blue50 →#202c4d, red50 →#3c2020.

Numbers are a typographic priority: TPS has tabular figures for live data and redesigned +/−/%/arrow glyphs.

### Cited Findings
- The adaptive light/dark pairs listed in section 2 come from separate colors.light.css and colors.dark.css. `ColorSchemeArea`, `ColorPreference` and `ThemeProvider` exports handle theme switching — [npm @toss/tds-colors](https://www.npmjs.com/package/@toss/tds-colors); [npm @toss/tds-mobile](https://www.npmjs.com/package/@toss/tds-mobile)
- In dark mode, the 50–100 steps of every hue become **dark tinted surfaces**: blue50 #202c4d, green50 #153729, red50 #3c2020, yellow50 #3d2d1a. The 600–900 steps become **lighter** text and accent tones. This keeps "tinted badge background + strong text" pairs working in both themes — [npm @toss/tds-colors](https://www.npmjs.com/package/@toss/tds-colors)
- The modal scrim is stronger in dark: 0.56 black vs 0.2 in light — same source.
- TPS ships tabular numerals for real-time quote screens and proportional numerals for big hero amounts, and its UI symbols were redesigned — [blog.toss.im](https://blog.toss.im/article/beginning-of-tps); [Sandoll](https://www.sandoll.co.kr/TossProductSans)
- Charts: tds-mobile ships `BarChart` and `DoughnutChart` (with DoughnutLabel) — [npm @toss/tds-mobile](https://www.npmjs.com/package/@toss/tds-mobile)
- The Toss App Builder article notes its design guide is optimized for light mode, with dark mode "on the roadmap" for that tool — [brunch @uibowl](https://brunch.co.kr/@uibowl/379)

### Inferences
- Korean market convention, which Toss Securities follows (**observed**, not sourced here): rises are shown in red, falls in blue. With TDS tokens that is red500 #f04452 (dark #f04251) for up and blue500 #3182f6 (dark #3485fa) for down.
  - For non-finance metrics in a game app (win rate, etc.), consider using green500/red500 or blue/red deliberately, and state which convention applies so it doesn't conflict with users' finance intuition.
- For big-number emphasis:
  - Use t1–t2 (26–30px), bold, grey900.
  - Put a smaller st/t5 delta line beneath, colored for the sign.
  - Use tabular-nums for any updating value.

### Gaps
- No Toss-authored source was found on chart styling (axis, gridline, color order) or on the red-up/blue-down rule. The toss.tech color article may cover dark-mode rationale but was unreadable here.

## 5. Motion and interaction feedback

### Takeaway
TDS motion is spring-based, with named presets. Tactile press feedback is a quick scale-down to 0.96 that springs back on release.

### Cited Findings (from `@toss/tds-mobile@2.5.1`) — [npm](https://www.npmjs.com/package/@toss/tds-mobile)
- Spring presets (stiffness/damping/mass):

| preset | stiffness | damping | mass |
|---|---|---|---|
| basic | 200 | 30 | 1 |
| small | 480 | 50 | 1 |
| quick | 800 | 55 | 1 |
| medium | 270 | 25 | 1 |
| large | 100 | 15 | 1 |
| slow | 70 | 20 | 1 |
| rapid | 1000 | 55 | 1 |
| bounce | 300 | 15 | 1 |

- Cubic-bezier easings:

| name | cubic-bezier |
|---|---|
| linear | 0,0,1,1 |
| ease | .6,0,0,.6 |
| out | .25,.1,.25,1 |
| expo | .16,1,.3,1 |
| back | .34,1.56,.64,1 |

- Touch effect: `touchStart → scale .96` with the rapid spring, then `touchEnd → scale 1` with the quick spring. A PRESSED state also scales to .96.
- A "shine/bounce" variant animates scale [1, 1.02, 1] over 0.2s plus the slow-spring duration.
- Selectable items return to scale 1 with the quick spring.
- Other transitions: background-color 0.2s ease for pressed rows, and a `FadeIn` component exists.

### Inferences
- CSS approximation for desktop:
  - `:active { transform: scale(.96) }` with `transition: transform 120ms cubic-bezier(.16,1,.3,1)`.
  - Hover: an overlay of greyOpacity100–200, shown only under `@media (hover:hover)`.
  - Sheet and modal entry: translateY plus fade with expo-out (~300ms).
  - These durations are **estimated** from the spring stiffness values.

### Gaps
- Toss-authored written motion principles (e.g. a toss.tech or Simplicity motion talk) were not retrieved, so the principles are inferred from the code.
