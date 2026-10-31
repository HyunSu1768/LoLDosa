# Toss (비바리퍼블리카) product and UX design principles: sourced notes

How these were collected (2026-10-31): WebFetch could not reach toss.im, toss.tech, maily.so or ditoday.com because of a DNS/allowlist failure. So the primary Toss pages were downloaded with curl through the proxy and their HTML text was extracted locally. Everything marked "(verified full text)" was read in full. Items marked "(search snippet only)" come from search-engine summaries and were **not** read in full.

---

## 1. Toss's stated product and design principles (exact wording)

### Takeaway
Toss has a written document of product principles, "토스 제품 원칙 / Toss Product Principle (PP)". Toss describes it as the "Winning Strategy" of its products. Its top value is **Simplicity**: learning nothing and understanding by instinct. Below that sit product-strategy rules and UX rules. The one directly relevant here is **One thing per One page**. Easy to answer, Value first / Cost later, Tap & Scroll, Context-based and No more loading follow the same idea. Toss officially confirms the PP's existence, the Simplicity definition and "Easy to answer". The full list of PP items comes from a secondary source, a Brunch summary of a Toss book.

### Cited Findings

**Where the PP came from and what it is for (official)**
- 2018 interview with PO 남영철. Toss defines simplicity as: "토스가 생각하는 단순함은 서비스를 사용하기 위해 알아야할 것이나 배워야할 것이 없고 본능적으로 이해할 수 있는 상태인데요. 별다른 설명 없이도 원하는 일을 끝낼 수 있는 매끄럽고 빠른 경험을 만드는 게 궁극적인 사용자 경험의 목표입니다." (Simplicity = nothing to know or learn, understood by instinct. The goal is a smooth, fast experience where you finish what you came for with no explanation.) — [토스피드, "토스는 왜 단순함에 집착할까?", 2018-06-19](https://toss.im/tossfeed/article/importance-simplicity) (verified full text; older than the preferred window, but it is the origin story)
- Same interview, on how the principles were written down. A failed home-screen experiment led the team to codify them: "‘단순함’이라는 제품의 철학이 더 확고해졌고, 이를 ‘토스 제품 원칙’이라는 문서로 정리하고 전파하기 시작했어요." (The philosophy became firmer and was written up and spread as the "Toss Product Principles" document.) — [토스피드 2018](https://toss.im/tossfeed/article/importance-simplicity)
- Tactics from the same interview:
  - "고객이 해야 할 일을 단 하나로 제약하다" (limit what the customer must do to exactly one thing): "다음 단계로 넘어가기 위해 눌러야 할 버튼은 꼭 하나씩만 있고" (only one button to proceed).
  - "경고 문구를 화면에 채워 넣기 보다는 고객이 실수를 했을 때만 무엇이 잘못되었는지 알려주고, 쉽게 다시 시도할 수 있도록" (don't fill the screen with warnings; tell the user what went wrong only when they make a mistake, and make retry easy).
  - "사용자에게 인증을 요구하는 것은 마지막까지 미루고" (defer asking for authentication until the very end; this is the seed of "Value first, cost later").
  - "‘이건 꼭 필요한 과정인가? 이 과정을 없앨 수 없을까?’" (constantly ask whether each step is necessary and whether it can be removed).
  - "로딩은 거의 없도록" (almost no loading in the transfer flow).
  — [토스피드 2018](https://toss.im/tossfeed/article/importance-simplicity)
- Toss Bank career article (content dated around 2023-07). It confirms the PP officially: "Toss Product Principle(이하 PP)은 그동안 시장을 바꿔온 토스 제품의 Winning Strategy를 담고 있는 원칙인데요. 토스팀이 제품을 만들고 개선할 때 PP를 좋고 나쁨을 판단하는 기준으로 두고…" (the PP holds the winning strategy of products that changed the market, and teams use it as the yardstick for good versus bad when building and improving). Also: "그중 가장 중요한 원칙인 Simplicity는 고객이 토스 제품을 이해하는 데 있어서 배움 없이 본능적으로 이해할 수 있음을 의미해요." (The most important principle, Simplicity, means understanding without learning, by instinct.) — [토스 채용, "단순하지만 큰 가치를 주는 제품의 힘을 믿어요" (토스뱅크 프로덕트 비전)](https://toss.im/career/article/tossbank-product-vision) (verified full text, extracted from the page JSON)
- Toss Tech, 2022-12-14, by 김재현, Design Strategy Lead: "토스에는 제품 디자인 원칙인 product principles가 있어요. 토스 제품의 winning strategy 를 담고 있고, 좋은 제품의 기준이 되는 원칙들인데요. 이 기준을 가지고 더 활발하게 피드백하기도 하고…" (the principles are the standard for good products and the basis for design feedback). — [Toss Tech, "토스 디자인 원칙, Easy to answer"](https://toss.tech/article/insurance-claim-process) (verified full text)
- Toss career page (search snippet only): designers "하나의 디자인 원칙을 함께 공유하고, 이를 바탕으로 서로의 작업을 리뷰" (share one set of design principles and review each other's work against them). — [Toss Product Designer job page](https://toss.im/career/job-detail?job_id=4326315003)

**Full PP item list (secondary; source says it is based on the book "토스의 위대한 도전")**
- 피그마스터 (Brunch, 2023-09-18) describes the PP as one top value, Simplicity, split into "제품 전략" (product strategy) and "UX 원칙/전략" (UX principles). The items and their Korean glosses:
  - **Product strategy**
    - **Casual Concept**: "전문적인 금융 용어와 개념 말고, 친숙하고 이해하기 쉬운 개념으로 접근" (use familiar, easy concepts rather than expert finance terms and concepts).
    - **Minimum feature**: "이 기능 없이는 절대 목표를 달성할 수 없는지 고려 / 기능이 추가될수록 제품은 어려워진다" (ask whether the goal is truly impossible without this feature; every added feature makes the product harder).
    - **Less Policy**: "단순한 제품의 시작은 단순한 정책! 사용자가 서비스를 이용하기 위해 알아야 하는 것을 최소화 한다" (a simple product starts with simple policy; minimise what users must know).
  - **UX principles**
    - **One thing per One page**: "하나의 화면은 하나의 메시지만 표현한다. 한 화면에 너무 많은 정보를 전달하지 않도록 지우고, 제외하고, 제거한다." (one screen expresses one message; erase, exclude and remove so a screen doesn't carry too much).
    - **Tap & Scroll**: "핵심 플로우를 누르기(Tap)과 스크롤(Scroll)만으로 구성한다." (build core flows from tap and vertical scroll only). The blogger adds that, in their own reading, few users swipe or scroll sideways. That remark is the blogger's, not Toss's.
    - **Easy to Answer**: "사용자가 마주치는 모든 질문에 3초 안에 대답할 수 있도록 한다. 기억하기 힘든 정보는 알아서 찾아준다" (every question can be answered within 3 seconds; information that is hard to remember is found for the user).
    - **Value First, Cost Later**: "사용자에게 제품의 가치를 먼저 전달한다. 정보를 입력하는 등 비용을 부과하는 행동은 그 다음의 일이다." (deliver value first; costly actions like data entry come after).
    - **No Ads Patterns**: "광고가 아닌 기능으로 소구한다. 광고 스타일을 사용하지 않을 때 오히려 사용자가 집중하기 쉽다" (appeal through function, not ad styling; users focus better without ad patterns).
    - **Context-based**: "사용자가 서비스를 이용하는 맥락을 고려해 플로우를 만든다. 맥락 없이 이어지는 플로우는 사용자의 이탈을 부른다." (design flows around the user's context; flows without context cause drop-off).
    - **No More Loading**: "사용자를 기다리게 하지 않는다. 이를 위해 정책, UX 플로우, 새로운 기술 등 모든 방법을 동원한다." (don't make users wait; use policy, flow and technology to avoid it).
    - **Sleek Experience**: "사용자가 의식하지 못할 정도로 매끈한 경험을 설계한다. 모든 시선과 손짓에 어색함이 없도록 배려한다." (an experience so smooth users don't notice it; no awkwardness in any glance or gesture).
  — [피그마스터, "토스 디자이너들의 프로덕트 원칙", Brunch, 2023-09-18](https://brunch.co.kr/@figmaster/8) (verified full text; secondary source)
- Corroboration (search snippet only): a newsletter titled "토스의 제품 원칙, 제품 전략 그리고 UX 원칙" gives the same structure, including "하나의 화면은 하나의 메시지" — [maily.so/eddy](https://maily.so/eddy/posts/78c6ef2d). A DI Today article describes "One Thing per Screen" as limiting each screen to one decision. It says information that older bank apps crammed together (account number, certificate, password) was split across separate screens to reduce cognitive load — [DI Today, "토스 10년 쉬운 금융이 만든 혁신과 그늘"](https://ditoday.com/?p=151644) (could not fetch; snippet only).

**UX writing principles (official, Toss Tech, 2022-11-15, by 김자유, UX Writer)**
- The writing system is a pyramid: core values → principles → guidelines → templates → system.
- **5 writing core values**:
  - **Clear 명확한**: "메이커가 아닌 사용자가 이해할 수 있는 문장" (sentences the user, not the maker, can understand).
  - **Concise 간결한**: "사용자는 쏟아지는 정보를 모두 읽지 않아요. 원하는 정보를 빠르게 스캔할 수 있도록 꼭 필요한 내용만 필요한만큼" (users don't read everything; give only what's needed so they can scan quickly).
  - **Casual 친근한**.
  - **Respect 존중하는**: "코스트를 숨기거나 혜택을 더 크게 보이게 만들고 싶을 때가 있어요… 당장의 이익을 조금 포기하더라도, 진실되고 사용자를 존중하는 커뮤니케이션" (don't hide costs or inflate benefits, even at some short-term cost).
  - **Emotional 공감하는**.
- **8 writing principles**, each phrased as a check question:
  - Predictable hint: "다음 화면을 예상할 수 있는 힌트가 있는가?" (is there a hint that lets the user predict the next screen?)
  - Weed cutting: "의미 없는 단어를 모두 제거했는가?" (all meaningless words removed?)
  - Remove empty sentences: "의미 없는 문장을 모두 제거했는가?" (all meaningless sentences removed?) The article adds: "공간이 비어보인다거나, 뭔가 허전한 느낌이 든다는 이유로 의미 없는 문구를 쓰는 것도 피해야" (don't add filler copy just because the space looks empty).
  - Focus on key message: "정말 중요한 메시지만 전달하고 있는가?" (only the truly important message?)
  - Easy to speak: "이해하기 어려운 용어나 표현을 사용하지 않았는가?" (no hard terms or expressions?) with "한 문장 안에는 가능하면 하나의 메시지만" (one message per sentence where possible).
  - Suggest over force: "특정 행동을 강요하거나 공포감을 주고 있지 않은가?" (not forcing an action or using fear?)
  - Universal words: "모두가 이해할 수 있고 모두에게 무해한가?" (understandable by and harmless to everyone?)
  - Find hidden emotion: "단순히 정보를 전달하는 것을 넘어 사용자의 감정에 공감했는가?" (beyond conveying information, did it empathise with the user's feelings?)
  — [Toss Tech, "토스의 8가지 라이팅 원칙들", 2022-11-15](https://toss.tech/article/8-writing-principles-of-toss) (verified full text)

**Affiliate-level product principles: 토스증권 (Toss Securities)**
- Chosun 쫌아는기자들 interview with 토스증권 PO 고동완 (2024-09-20). The reporters summarise the team's principles as:
  1. "무조건 쉽게 만들자. 쉽게 만들어서 생략하는 것이 있어도 좋다. 어려운 기능은 천천히 붙이자." (make it easy no matter what; it's fine to omit things; add hard features slowly)
  2. "일단 유저와의 접점을 늘려야한다." (first, increase touchpoints with users)
  3. "유저에게 선택권을 많이 주는 것보다 줄이는 것이 나을지도 모른다." (fewer choices may beat more choices)
  4. "이름은 매우 중요하다. ‘주식모으기’ 기능 이름 하나로 2주를 토론했다." (names matter a lot; the team debated the name "주식 모으기" for two weeks)
  — [네이트/조선일보, "[쫌아는기자들] 토스증권이 제품을 만드는 몇가지 원칙들", 2024-09-20](https://news.nate.com/view/20240920n08662) (verified full text)
- 토스증권 mission: "투자의 힘을 모두에게 / To provide better access to global capital markets for all investors" — [Toss Tech, "투자를 모르는데 어떻게 증권 UX 리서처를 해요?", 2024-10-14](https://toss.tech/article/30663)

**Design system principles (official)**
- Toss Tech, 2024-03-05, by 박수현, Platform Designer. The three elements for improving a component:
  - "다양한 케이스를 패턴화 해요" (pattern the many cases)
  - "심미적인 경험을 설계해요" (design an aesthetic experience)
  - "모든 유저의 사용성을 지켜요" (protect usability for all users)
- The motivation for this work, quoted: "서비스를 만들기에도 바쁜 디자이너는 다시 하나하나 다크모드, 텍스트가 길어질 때의 정책, 접근성 및 voice over 대응 등을 직접 결정해야 했죠" (busy designers had to decide dark mode, long-text policy, accessibility and VoiceOver handling one by one). Toss's response was to absorb these concerns into TDS components.
  — [Toss Tech, "토스 디자이너가 제품에만 집중할 수 있는 방법"](https://toss.tech/article/toss-design-system) (verified full text)

### Inferences
- *Inferred:* The PP behaves as a review checklist ("좋고 나쁨을 판단하는 기준"), not a set of slogans. A coaching app could adopt a short PP-style checklist for its own screen reviews in the same way.
- *Inferred:* Tap & Scroll, and its stated reason that horizontal gestures are under-used, is mobile-specific. On a desktop app the transferable part is to put core flows on a single vertical reading path and avoid hidden horizontal carousels.

### Gaps
- I did not get the original book "토스의 위대한 도전" or an official Toss page that lists every PP item. The item list rests on secondary blog sources, which agree with each other.
- I could not confirm whether the PP was revised after 2023.

---

## 2. What Toss presented at Simplicity conferences (and related Toss Tech posts) about UX

### Takeaway
Simplicity is mostly told through case stories. Session listings are available, but the session transcripts and videos were not accessible as text. Topics relevant here: A/B testing and data-driven decisions (토스모바일 MVP, 증권 guerrilla testing), redesigning complex products, sign-up flow improvement, "꼭 넣어야 해요?" (must we add this?), product ethics principles, screen-reader universal UX (Season 4 / 2025), and quantifying experience in research.

### Cited Findings
- Simplicity 21 (Aug 30 – Sep 2, 2021). The page groups sessions into four themes:
  - "사용자를 위해서라면" (for the user's sake): "문제의 본질을 속속들이 꿰뚫어 보고, 근본적인 해결에 도달한 이야기" (stories of seeing to the core of a problem and reaching a root fix)
  - "신은 디테일에 있다" (God is in the details): "숨결 하나, 여백 하나조차 허투루 생각하지 않는" (not taking even a breath or a margin lightly)
  - "아무도 가지 않은 길" (the road no one took)
  - "상식에 도전하다" (challenging common sense)
  — [toss.im/simplicity-21](https://toss.im/simplicity-21) (page text verified)
- Search summary (snippet only): Simplicity 21 included a session on redesigning stock-investing UX for 토스증권. — [토스피드, Simplicity 21 announcement](https://toss.im/tossfeed/article/toss-simplicity21)
- Simplicity 23 (2023-05-22) session list, verified from the page. Tags and titles of relevance, with speakers:
  - "토스모바일 ・ MVP ・ AB테스트 — 데이터로 내린 의사결정" (data-driven decisions; 정나림)
  - "증권 ・ AB테스트 — 프로덕트 디자이너가 게릴라 테스트에 진심인 이유" (why product designers are serious about guerrilla testing; 서은해)
  - "토스 주민센터 — 크고 복잡한 제품 과감하게 갈아엎기" (boldly tearing down a big, complex product; 이지윤)
  - "인터랙션 디자인 ・ 시스템 설계 — 꼭 넣어야 해요?" (do we really have to add it?; 김지혜, 박연주)
  - "제품 윤리 원칙 탄생기" (birth of the product ethics principles; 김명지)
  - "토스 가입 과정 — 완성 없는 이야기, 가입 과정 개선" (sign-up improvement as a never-finished story; 윤지영, 임경우)
  - "B2B ・ 사장님 ・ 유저리서치 — 사용자에게 질문을 멈춰야할 때" (when to stop asking users questions; 박지희)
  - "토스페이먼츠 ・ 결제창 — 복잡한 B2B 제품, 정답으로 향하는 길" (complex B2B product, path to the answer; 이영민)
  - "초등학생도 쓸 수 있는…" (a teen product usable even by elementary students; 성소연)
  — [toss.im/simplicity-23](https://toss.im/simplicity-23)
- Simplicity Season 4 / "Simplicity 25" (2025-04). Theme: "Vision Driven Design", 14 sessions. Topics include:
  - a graphic-design journey for "Pull To Refresh"
  - interaction design for foreign-user onboarding
  - universal UX improvements for screen-reader users
  - "경험을 수치화하는 새로운 리서치 방법론" (a new research method that quantifies experience)
  - AI and UX writers
  - the in-house design tool "데우스"
  - AI user-test bots
  - research to improve usability for blind users
  - fixing the "아무도 쓰지 않는 디자인 시스템" (design system nobody uses) problem
  — [디자인 나침반, "토스 심플리시티 25", 2025-04-28](https://designcompass.org/2025/04/28/toss-simplicity/) (verified full text)
- Simplicity 24 page: the response was compressed or binary and could not be parsed. Not covered.

### Inferences
- *Inferred:* The Simplicity material that bears most directly on data-heavy screens (complex-product teardown, "꼭 넣어야 해요?") would need the videos themselves. The titles alone signal a consistent stance: remove before you add.

### Gaps
- I found no Simplicity transcript specifically about information density, chart or number display, empty states or skeleton loading. The session videos are on toss.im/simplicity and YouTube, but they were not accessible as text in this session.
- I found no session-level detail on 자산 홈 or 소비 리포트 design.

---

## 3. How Toss handles data-heavy screens: what to show first, summarising, hierarchy, comparison, personalisation

### Takeaway
Across the cases the pattern is consistent:
- Show the **result the user cares about**, not the internal process. In the remittance case, 9 statuses became 3.
- **Separate the user's own data from Toss's suggestions** structurally, on different layers, rather than through louder styling.
- **Shrink choice sets to the user's own context**: show only my insurers, recommend only the single best card.
- **Start simple and add advanced density as users mature**: 토스증권 started with line charts only and added candlesticks and the order book later.

### Cited Findings
- **Show the outcome, not the pipeline (토스뱅크 해외송금, 2026-09-21, by 서자영, Product Designer).**
  - Internally a transfer goes through customer verification, FX-rule checks, AML and sanctions screening, receiving-bank checks, deposit and post-monitoring. The designer wrote: "이 과정을 사용자에게 모두 보여주는 게 답은 아니라고 생각했어요. 내부에서 어떤 일이 일어나는지 전부 보여주면 오히려 더 불안해질 수도 있으니까요." (showing everything could make users more anxious, not less).
  - The filter question the team used: "‘이건 사용자가 알아야 하는 정보인가, 아니면 우리만 알고 있으면 되는 정보인가?’" (does the user need to know this, or only we?)
  - The result: "아홉 개였던 송금 상태를 세 개로 줄였어요. 송금 처리 중 → 해외 은행 도착 → 완료" (nine states cut to three: processing → arrived at foreign bank → done), with the goal "지금 내 돈이 어디까지 갔는지 알 수 있는 정보만 남긴 거예요" (keep only what tells me where my money is now). Tagline: "보내면 보이는 해외송금" (send it and you can see it).
  - Before the redesign, the old screen said "정상 송금" (transfer normal) for three days straight, which was ambiguous. The PM's verdict: "걱정하지 말라고 했는데, 걱정은 그대로였어요." (they told me not to worry, but the worry stayed).
  - Instant validation feedback: entering a SWIFT code such as CHASUS33XXX immediately shows "JP Morgan Chase". This is a feature not needed for the transfer itself, added to give confidence that the input is correct. Address entry uses map-API autocomplete.
  - The team's yardstick shifted from "‘얼마나 싼가’에서 ‘얼마나 불안하지 않은가’로" (from how cheap to how un-anxious).
  — [Toss Tech, "도메인 지식 없는 디자이너가 팀의 기준을 바꾼 방법", 2026-09-21](https://toss.tech/article/remittance_transfer) (verified full text)
- **Separate "your data" from "our suggestion" by layer (토스뱅크 자산관리 리포트, 2026-09-22, by 김현지, Visual Designer).**
  - The report banner under the account area had a 2% CTR. Diagnosis: "토스뱅크 홈에는 정보가 많다 보니 주변 정보와 충분히 구분되지 않아" (the home has so much information the banner didn't stand apart).
  - Key insight: "계좌는 사용자의 정보이고, 리포트는 저희가 새롭게 건네는 제안이에요. 역할이 다른 둘이 한데 섞여 있다 보니…" (the account is the user's information; the report is a new suggestion from us; mixing the two roles hurt both). Simply emphasising the report wouldn't work either: "계좌를 확인하려는 사람에게 리포트가 먼저 보이면, 정작 필요한 정보가 잘 보이지 않을 수 있었어요" (if someone checking their account sees the report first, the info they need gets buried).
  - Solution: a tooltip-inspired floating card on a separate layer above the unchanged account screen. Details:
    - Strip graphics and colour so it reads as a function, not an ad. Toss's comparison: "광고는 큼직한 그래픽과 눈에 띄는 컬러로… 기능은 텍스트와 버튼을 중심으로 정보의 위계로 내용을 전하고" (ads use big graphics and loud colour; functions use text, buttons and information hierarchy).
    - The card shrinks when the user scrolls, staying as a re-entry point.
    - It opens after the screen appears, so it feels like a remark addressed to the user.
    - Easing that starts fast, decelerates smoothly and ends with a slight bounce; translate and scale are offset so the motion curves.
  - A/B test of three variants: the expression-change ("interactive") variant got only 1.1x CTR, while the structural floating variant got **3x CTR and 3x CVR**.
  - Lesson: "표현을 바꾸는 것만으로 해결되지 않는다면, 문제가 생기는 구조 자체를 다시 볼 필요가 있어요" (if changing expression doesn't solve it, re-examine the structure).
  — [Toss Tech, "방해하지 않고, 눈에 띌 수 있을까", 2026-09-22](https://toss.tech/article/asset_management) (verified full text)
- **Personalise to shrink the option set.** In 병원비 돌려받기 (hospital bill refund), showing all insurers caused heavy drop-off. Fix: "보험 정보가 토스에 연동되어있는 사용자라면, 가입된 보험사 목록만 보이게" (users with linked insurance see only their own insurers), and drop-off improved (no number given). — [Toss Tech, Easy to answer, 2022-12-14](https://toss.tech/article/insurance-claim-process)
- **Recommend one, not a ranking.** The 카드혜택추천 (card benefit recommendation) team expected a ranked list (variant A) to win. Showing only the #1 card (variant B) had the better application conversion: "결국 핵심은 선택지를 한 가지만 주는 것" (the key was offering only one choice). The author admits variables weren't well controlled.
  - A banner copy test: "1등 카드 확인하기" (check the #1 card) got **+20%p CTR**.
  - Suggested framings for "best option": social proof ("토스 회원들이 가장 많이 구매한 상품이에요", the product Toss members bought most) and the user's own data ("매일 카페를 가는 김토스님, 카페 할인되는 카드를 만들어보세요", "Kim Toss, you go to cafés every day; get a card with café discounts").
  — [Toss Tech, "추천할 때는 제일 좋은 것 하나면 된다", 2023-03-23, 박다롱](https://toss.tech/article/recommend-just-one) (verified full text)
- **Progressive density on securities screens (토스증권).** PO 고동완:
  - "처음에는 UI를 매우 단순하게 만들어서 초보 유저들만을 타겟으로" (at first the UI was very simple and targeted beginners only).
  - "초기 실제로 봉차트도 없고 선차트만 제공했으며, 추세선이나 이동평균선 같은 기능도 없었어요" (early on there were no candlestick charts, only line charts, and no trendlines or moving averages).
  - USD prices were shown in KRW. The team even designed hiding USD entirely, but chose to show both because hiding it risked misunderstanding.
  - "아무것도 모르는 사람에게 ‘20분 지연’을 설명하기도 어려우니, 그냥 ‘시장가로 주문하세요’고 안내했죠" (rather than explain "20-minute delay" to novices, they simply said "order at market price").
  - The team added charts, the real-time order book and quotes over time, "유저들의 성장에 맞춰" (in step with users' growth). Novice users later grew their invested amounts and trade frequency.
  — [네이트/조선일보, 2024-09-20](https://news.nate.com/view/20240920n08662) (verified full text)
- 토스증권 PC/WTS (search snippet only; I did not read the articles in full):
  - The October 2025 update reportedly centred on "직관적인 정보, 빠른 주문, 맞춤형 인터페이스" (intuitive information, fast ordering, customised interface), with PIP side panels.
  - A June 2026 update reportedly added up to 4 simultaneous charts and user-reorderable tabs combining chart, order book, quotes and investor flows.
  — [헤럴드경제, 2026-06-03](https://www.heraldk.com/article/2026060316513470589); [디자인 나침반, "토스 증권 PC 출시", 2024-07-19](https://designcompass.org/2024/07/19/toss-invest-pc/)
- **One clear action on the first screen.** In the 2018 home-screen experiment, listing many services on the first screen did not change users or revenue: "화면에 무언가를 더 많이 넣어도 고객이 인지하지 않는다" (putting more on screen doesn't mean customers notice it). The team made the home simpler instead, keeping only the amount input, and switched to context-based recommendation: "서비스가 다양해지고 복잡해진 만큼, 첫 화면은 오히려 더 단순해야 한다" (the more varied and complex the services, the simpler the first screen must be). — [토스피드 2018](https://toss.im/tossfeed/article/importance-simplicity)
- **Long lists and scannability in components.** The TDS menu component adds top and bottom blur when a list overflows, so users realise more items exist (prompted by senior-user VoC). It guarantees width for labels of 5 or more characters (over half of real usage). Check icons moved to the left for recognisability (about 50% of uses were check-type). — [Toss Tech, 2024-03-05](https://toss.tech/article/toss-design-system)

### Inferences
These are inferred applications to a dark-theme desktop coaching app, not Toss's statements:
- Each review or dashboard screen should lead with the one outcome the player cares about (the remittance "where is my money now" logic), and push process and internal metrics behind a disclosure.
- Use 3 coarse states rather than many fine ones for statuses such as analysis progress.
- Keep the user's own stats and the app's coaching suggestions on visually different layers. Don't put them in the same card grid.
- Recommend a single top "fix this next" item instead of a ranked top-10.
- Ship a simple chart first and add advanced views as the user's level rises.
- Toss's "ads look like big graphics and colour; functions look like text + hierarchy" heuristic argues for low-chroma, text-led insight cards on a dark theme.

### Gaps
- I found no official Toss source on 소비 리포트 (spending report) or 자산 홈 (asset home) information hierarchy, on number formatting rules (for example 억/만원 rounding), or on chart colour conventions (for example red-up/blue-down in 토스증권).
- I found no official Toss writing on empty states or skeleton loading beyond "No more loading" (secondary) and "로딩은 거의 없도록" (2018).

---

## 4. Experimentation and A/B testing, with measured results

### Takeaway
Toss publishes many small, honest case studies with numbers, including ones where the designer's own hypothesis lost. The recurring lessons:
- Simpler questions and fewer options win.
- Structural changes beat cosmetic ones.
- Prototype and usability-test before building.

### Cited Findings
- **Easy to answer, insurance claim (2022-12-14).**
  - Replacing the question "전문가 도움받을래 직접 할래?" (expert help or do it yourself?) with "서류 있나요?" (do you have the documents?) cut drop-off.
  - The article states two figures. First: "기존 화면에 비해 이탈하는 사용자가 50% 감소했어요" (drop-off fell 50% versus the old screen), for the question step. Later: "화면을 개선한 뒤 실제로 이탈하는 사용자가 60%로 대폭 감소했어요" (after the redesign, drop-off fell sharply, to/by 60%), apparently for the overall flow. The article does not reconcile the two numbers; treat 50% as the step-level figure and 60% as flow-level, ambiguously worded.
  - Yes/no split on documents: 5:4.
  - The problem was found by a usability test (UT) with 5 users, after the team had believed the "expert help" option solved it.
  - The rule of thumb: "3초 안에 답이 안나오면 어려운 질문이에요" (if no answer comes within 3 seconds, it's a hard question), with the example "저녁 뭐 먹을래?" (what do you want for dinner?) versus "저녁에 피자 먹을까?" (pizza for dinner?).
  — [Toss Tech](https://toss.tech/article/insurance-claim-process)
- **Card recommendation (2023-03-23).** Showing one card beat a ranked list on application conversion, and the "1등 카드 확인하기" banner got +20%p CTR. The author's own caveat: "실험의 변수가 잘 통제되어있진 않았어요" (the experiment's variables weren't well controlled). — [Toss Tech](https://toss.tech/article/recommend-just-one)
- **Asset report (2026-09-22).** In a 3-way A/B test, expression change gave 1.1x CTR; structural change (floating layer) gave 3x CTR and 3x CVR from a 2% CTR baseline. The author's point about CVR: "클릭만 늘었다면 리포트가 눈에 잘 띄어서 눌린 것일 수 있어요. 하지만 클릭 이후의 행동까지 함께 늘었다는 건…" (if only clicks rose, it might just be visibility; CVR rising too means the downstream experience improved). — [Toss Tech](https://toss.tech/article/asset_management)
- **"내 아이디어를 너무 믿지 마세요" (don't trust your own idea too much; 2023-03-28, 강효정).**
  - A voice-résumé concept, "3가지 질문에 답하면 저절로 완성되는 이력서" (a résumé that completes itself when you answer 3 questions), failed internal prototype UTs. Testers felt it was "간편한게 아니라 오히려 더 어렵고 부담스러운 방식" (not easier but harder and more burdensome).
  - It was pivoted to "3가지 질문에 답하면 합격 확률 높은 포지션을 알려줄게요" (answer 3 questions and we'll show positions you're likely to pass), with "이건 입사 지원이 아니다" (this isn't a job application) stated explicitly.
  - The UT method: define "검증하고 싶은 것" (what to validate), then "확인해야 할 것" (what to observe), then a scenario.
  — [Toss Tech](https://toss.tech/article/dont-trust-your-gut) (verified full text)
- **2018 home screen.** Adding more services to the first screen produced "사용자 수나 매출에 변화가 없었습니다" (no change in users or revenue). Simplifying the screen and adding contextual recommendations grew non-transfer services (no number given). — [토스피드 2018](https://toss.im/tossfeed/article/importance-simplicity)
- **TDS component work.** Before redesigning, the team audited actual usage with a component-collection tool. Findings:
  - check icons were used in about 50% of cases
  - more than half of labels were 5 or more characters
  - menus with 7 or more items occurred
  — [Toss Tech, 2024-03-05](https://toss.tech/article/toss-design-system)
- **토스증권 prioritisation.** Impact-size principle; 6-month OKRs per silo; "PON 리스트 (Problem, Opportunity, Needs)"; growth and business modelling with explicit assumptions (for example "거래액이 20% 증가할 것", trading value will rise 20%). When results differ, "가정이 틀렸다는 것을 인정하고, 무엇이 잘못되었는지 깊게 분석" (admit the assumption was wrong and analyse deeply). — [네이트/조선일보, 2024-09-20](https://news.nate.com/view/20240920n08662)
- Simplicity 23 had dedicated sessions on A/B tests and MVP decisions (토스모바일) and guerrilla testing (증권). Content not retrieved. — [toss.im/simplicity-23](https://toss.im/simplicity-23)

### Inferences
- *Inferred:* For a coaching app, track a downstream metric, not just click-through. For example: did the player actually practise the recommended concept? This mirrors Toss's emphasis on CVR over CTR.
- *Inferred:* Cheap internal UTs (5 users) caught problems that metrics alone had masked.

### Gaps
- I found no published Toss figure for the often-repeated claim that "reducing screens or steps increased conversion by X%" beyond the cases above.

---

## 5. Accessibility principles Toss has published

### Takeaway
Toss frames accessibility as part of "누구나 금융을 쉽게" (easy finance for everyone). It has published a developer-facing document, **A11y Fundamentals** (2025-08), and builds accessibility into TDS components. Simplicity 2025 had sessions on screen-reader and blind-user UX.

### Cited Findings
- **A11y Fundamentals (Toss Tech, 2025-08-13, by 강민우, Frontend Developer).**
  - Opening line: "토스는 ‘누구나 금융을 쉽게’ 사용할 수 있는 세상을 꿈꿔요. 그래서 제품을 만들 때도, 문서를 쓸 때도, 접근성을 고민합니다." (Toss dreams of a world where anyone can use finance easily, so it considers accessibility when building products and writing docs.)
  - It covers common mistakes: a button inside a button; a `<button>` inside an `<a>`; how screen readers read content; a `<div>` with only a click handler isn't recognised as a button; proper role, label and alt.
  - Benefits for everyone: correct `<a>` enables context menus ("open in new tab", "copy link"); a proper `<form>` and `<button type="submit">` enables Enter-to-submit; keyboard users navigate with Tab, Shift+Tab, Enter, Space and arrow keys and need correct roles and focus.
  - The article states accessibility helps disabled users, general users and developers (more robust, maintainable code).
  — [Toss Tech, "토스의 접근성 문서 A11y Fundamentals 을 소개합니다"](https://toss.tech/article/A11y_Fundamentals) (verified full text, first part)
- **TDS.** One of the three component principles is "모든 유저의 사용성을 지켜요" (protect usability for all users). Concrete outcomes:
  - menu overflow blur, added after senior-user VoC about unseen items
  - layouts that guarantee width under large OS text sizes
  - dark mode, long text and VoiceOver handled at the component level so product designers don't decide them per screen
  — [Toss Tech, 2024-03-05](https://toss.tech/article/toss-design-system)
- **Simplicity 2025** included "스크린 리더 사용자를 위한 유니버설 UX 개선" (universal UX improvements for screen-reader users) and research to raise usability for blind users. — [디자인 나침반, 2025-04-28](https://designcompass.org/2025/04/28/toss-simplicity/)
- **Writing.** The "Universal words" principle asks "모두가 이해할 수 있고 모두에게 무해한가?" (understandable by and harmless to everyone?). — [Toss Tech, 2022-11-15](https://toss.tech/article/8-writing-principles-of-toss)

### Inferences
- *Inferred:* For a desktop (likely web-tech) app, A11y Fundamentals maps directly:
  - use real `<button>` and `<a>`
  - support full keyboard navigation and visible focus
  - give charts text alternatives
  - put dark-mode tokens and large-text behaviour into shared components rather than per-screen decisions

### Gaps
- I did not read the full A11y Fundamentals document itself (the separate docs site), only the announcement article.
- I found no published Toss contrast ratios, dark-theme colour-token rules or chart-accessibility guidance.
