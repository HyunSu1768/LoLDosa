# Toss (토스) UX Writing System — principles, rules, tools, before/after examples

> **Sourcing caveat (read first).** This session's network allowlist blocked direct fetches of toss.tech, toss.im, developers-apps-in-toss.toss.im, brunch, velog, oopy, i-boss and the-pr.co.kr (DNS ENOTFOUND). The findings below come from (a) search-engine snippets of those primary pages and (b) a public GitHub research summary ([vmc-inner-circle/k-style-ui-ux `docs/research/ux-writing/toss.md`](https://raw.githubusercontent.com/vmc-inner-circle/k-style-ui-ux/HEAD/docs/research/ux-writing/toss.md), hereafter **[KSU]**). KSU gives author, date and URL for each primary article, but it paraphrases and says most examples were read off images. Each item below names the primary article it points to. Treat exact Korean wording as **near-verbatim, not checked against the original page**. To check it, allow the domains toss.tech, toss.im and developers-apps-in-toss.toss.im.
>
> Primary articles referenced (dates are from KSU):
> - [8P] 김자유, 「토스의 8가지 라이팅 원칙들」, toss.tech, 2022-11-15 — https://toss.tech/article/8-writing-principles-of-toss
> - [ERR] 김자유, 「좋은 에러 메시지를 만드는 6가지 원칙」, toss.tech, 2022-09-21 — https://toss.tech/article/how-to-write-error-message
> - [SYS] 김자유, 「가이드라인을 시스템으로 만드는 법」, toss.tech, 2022-11-04 — https://toss.tech/article/introducing-toss-error-message-system
> - [1ST] 김자유, 「첫 UX writer는 무슨 일을 해야 할까」, toss.tech, 2023-04-14 — https://toss.tech/article/1st_uxwriter
> - [PPL] 「토스 피플 #2: UX 라이팅의 새로운 기준」, toss.tech (date not captured) — https://toss.tech/article/toss-people-2
> - [FEED] 토스피드 「토스가 금융을 더 쉽게 만드는 또 하나의 방법, UX Writing」, 2021-02-18 — https://toss.im/tossfeed/article/uxwriter-interview
> - [AIT] 앱인토스 개발자센터 「UX 라이팅」 (undated, live doc) — https://developers-apps-in-toss.toss.im/design/ux-writing.html
> - [MKT] 유아란, 「마케팅 문구 클릭률을 올리는 6가지 원칙」, toss.tech, 2026-01-30 — https://toss.tech/article/44737

## Q1. What are Toss's published UX writing principles (core values + 8 principles)?

### Takeaway
Toss has two layers. The top layer is **5 writing core values**: Clear, Concise, Casual, Respect, Emotional (명확한·간결한·친근한·존중하는·공감하는). Under them sit **8 practical principles**, each written so a writer can check it yes or no (Predictable hint, Weed cutting, Remove empty sentences, Focus on key message, Easy to speak, Suggest than force, Universal words, Find hidden emotion). Separately, the public Apps-in-Toss guide sets **style rules**: 해요체 everywhere, active voice, positive phrasing, and no excessive honorifics.

### Cited Findings
**Core values → principles structure**
- The five core values are abstract, and the principles turn them into rules a writer can act on. The article's example: the core value *concise* becomes the principle 「의미 없는 단어를 없애자」 ("let's remove meaningless words"). Quote: 「토스에는 다섯 가지 라이팅 코어밸류가 있어요」 ("Toss has five writing core values") — [8P via search snippet](https://toss.tech/article/8-writing-principles-of-toss); [GPTers summary](https://www.gpters.org/ai-writing/post/everyone-likes-toss-creating-EJy7lIT7oDsoxkR) (written by a non-Toss author who says it was built from Toss materials).
- Core values: **Clear, Concise, Casual, Respect, Emotional** — [KSU](https://raw.githubusercontent.com/vmc-inner-circle/k-style-ui-ux/HEAD/docs/research/ux-writing/toss.md) citing [8P](https://toss.tech/article/8-writing-principles-of-toss).

**The 8 principles, with the examples Toss gives** (all from [8P](https://toss.tech/article/8-writing-principles-of-toss), via [KSU](https://raw.githubusercontent.com/vmc-inner-circle/k-style-ui-ux/HEAD/docs/research/ux-writing/toss.md) and search snippets)
1. **Predictable hint**: a reader should be able to predict the next screen from the button or sentence alone. Before 「다른 곳에서 후불결제 하기」 ("do buy-now-pay-later elsewhere") → after 「내가 쓰는 브랜드 신청하기」 ("apply for the brand I use").
2. **Weed cutting** (잡초 뽑기): remove words that don't change the meaning. The article stresses that the goal is not a lower character count: 「단순히 글자수를 줄이는 것 (X) / 소소한 잡초들을 뽑아 간결히 하는 일 (O)」 ("merely cutting characters (X) / pulling small weeds to make it concise (O)"). Example: 「앞으로 받을 배당금」 → 「받을 배당금」 ("dividends you'll receive *in the future*" → "dividends you'll receive"). A secondary summary gives another example: 「이미 보유하고 계신」 → 「보유 중인」 ("that you already hold [honorific]" → "held") — [styleseed UX-WRITING.md](https://raw.githubusercontent.com/bitjaru/styleseed/HEAD/engine/UX-WRITING.md).
3. **Remove empty sentences**: cut sentences that repeat what the screen already says or only fill space. This works at the screen level, while weed cutting works at the word level.
4. **Focus on key message**: leave out what the user already knows. Write options as action labels in the 「~하기」 form, not as descriptions.
5. **Easy to speak**: the text should sound natural read aloud. Avoid 한자어 (Sino-Korean words), written-style Korean (문어체) and long sentences. One message per sentence. Patterns to avoid: 「~로 인한」 ("due to"), 「~을 통해」 ("through"), 「~이 가능하며」 ("is possible and").
6. **Suggest than force**: recommend, but don't pressure the user or make them afraid. Always give a way out, e.g. 「다음에 할까요?」 ("Shall we do it next time?").
7. **Universal words**: avoid trendy slang, memes and jargon. Use words everyone understands and nobody finds off-putting.
8. **Find hidden emotion**: go beyond information and acknowledge how the user feels. Example: a push notification when a loan is fully repaid, 「드디어 대출 끝🎉」 ("Finally, loan done 🎉"). Another empathetic line from the same set: 「갚느라 고생 많으셨어요」 ("You worked hard paying it off") — [styleseed](https://raw.githubusercontent.com/bitjaru/styleseed/HEAD/engine/UX-WRITING.md).

**Style rules from the public Apps-in-Toss guide** ([AIT](https://developers-apps-in-toss.toss.im/design/ux-writing.html), via search snippet and [KSU](https://raw.githubusercontent.com/vmc-inner-circle/k-style-ui-ux/HEAD/docs/research/ux-writing/toss.md))
- **해요체**: 「제품 안의 모든 문구는 '해요체'로 써요. 일관성 있는 사용자 경험을 만들 수 있도록 상황, 맥락을 불문하고 모든 문구에 해요체를 적용해주세요.」 ("All copy in the product is written in 해요체. Apply 해요체 to every string, regardless of situation or context, so the experience is consistent.") Example: 「김토스님에게 1원을 보낼게요」 ("I'll send 1 won to Kim Toss").
- **능동형 (active voice)**: 「제품 안에서 최대한 능동형 문장을 써주세요. 수동형 문장은 특정 상황에서만 쓰는 게 좋아요.」 ("Use active sentences as much as possible. Passive is best only in specific situations.") The passive exceptions are: service ended or period expired, reporting the result of something the user did, and reassuring the user. Example: 「알림을 설정했어요.」 ("I set the notification"). The guide's list also includes 「됐어요 → 했어요」 ("it got done → I did it").
- **「~되어요」 → 「~돼요」**: always use the contracted form, to save screen space.
- **No 한자어 noun stacking**: don't write {명사}+{명사} chains. Unpack them into verbs or a 「{명사}가 {명사}해서」 clause. Example: 「잔액이 부족해서 구매하지 못했어요」 ("Couldn't buy because the balance was short"), instead of something like 잔액 부족으로 구매 불가 (inferred "before" form).
- **No excessive honorifics**: avoid 「~시겠어요?」, 「계시다」 and 「~께」. Example: 「카드를 해지할까요?」 ("Shall I cancel the card?"). Exception: when you need the user's goodwill, as in a survey, polite honorifics are fine.
- **긍정형 (positive phrasing)**: 「안 돼요, 없어요 (X) → ~하면 할 수 있어요 (O)」 ("can't / there isn't (X) → you can if you … (O)"). Exceptions where a negative is clearer: policy makes the service unavailable, some features are restricted, or the screen explains collection of sensitive information. In these cases 「쓸 수 없는 이유를 함께 안내해주세요」 ("explain why it can't be used").
- **Perspective**: say 「내 계좌」 ("my account"), not 「고객님의 계좌」 ("the customer's account"). Never mix 해요체 and 합쇼체 — [styleseed](https://raw.githubusercontent.com/bitjaru/styleseed/HEAD/engine/UX-WRITING.md) (secondary).
- **Early voice chart**: 「어투: 문장형(명사형X), 청유형 문장(강요나 지시X)」 ("Tone: sentence form, not noun form; suggestive 'let's' sentences, no forcing or commanding") — [FEED/1ST via search snippet](https://toss.tech/article/1st_uxwriter). Per [1ST](https://toss.tech/article/1st_uxwriter), the principles actually in use were then built from collected real cases (via KSU).
- **Consistency goal**: Toss runs 40+ services and wants them to sound 「한 사람이 말하는 것 같은 라이팅 톤」 ("as if one person is speaking") — [FEED](https://toss.im/tossfeed/article/uxwriter-interview) (search snippet). An early published principle was to pull the 잡초 (filler expressions) out of text — [DIGITAL iNSIGHT](https://ditoday.com/?p=141579).

### Inferences
- The 8 principles appear to work as a review checklist, each one a yes/no question ("Is there a hint for the next screen?", "Did I remove meaningless words?"). Both GPTers and styleseed present them that way. The app can use the same 8 questions as a copy-review rubric.
- For a game-coaching app, "Find hidden emotion" maps to post-loss feedback (acknowledge tilt before giving instructions). "Suggest than force" maps to coaching tips: 「~해보세요」 or 「~할 수 있어요」, not 「~해야 합니다」.

### Gaps
- I could not retrieve the full original text of [8P], so explanatory sentences are paraphrased. No source gave an official rationale for choosing 해요체 over 합니다체, beyond consistency and casualness.
- Whether the AIT guide is word-for-word identical to Toss's internal guide is unverified. It is the public version aimed at mini-app partners.

## Q2. Concrete rules: register, 명사형, 한자어, buttons, errors/empty/loading, numbers/dates

### Takeaway
The rules found are explicit for register, noun-ending avoidance, buttons and error messages. They are **thin to absent** for empty states, loading states and number/date formatting: no published Toss number-formatting rule was found. Error messages follow a 6-principle framework and come out of a template system.

### Cited Findings
**명사형 종결 → 문장형 (noun endings → full sentences)**
- 「카드 연결 완료」 / 「카드 연결을 완료했습니다」 → 「카드를 연결했어요」 ("card connection complete" → "I connected your card") — [KSU citing FEED/1ST](https://raw.githubusercontent.com/vmc-inner-circle/k-style-ui-ux/HEAD/docs/research/ux-writing/toss.md); the same example is reported in press coverage (search snippet of [longblack](https://longblack.co/note/985) / [etnews 2021-04-02](https://www.etnews.com/20210402000166) result set).
- For suggestions, use 「~할 수 있어요」 ("you can …") or 「~해보세요」 ("try …") instead of 「~해야 해요」 ("you must …") — [KSU citing ERR/1ST](https://raw.githubusercontent.com/vmc-inner-circle/k-style-ui-ux/HEAD/docs/research/ux-writing/toss.md).

**Buttons** ([KSU](https://raw.githubusercontent.com/vmc-inner-circle/k-style-ui-ux/HEAD/docs/research/ux-writing/toss.md) citing FEED/AIT/8P; [styleseed](https://raw.githubusercontent.com/bitjaru/styleseed/HEAD/engine/UX-WRITING.md))
- A single CTA uses the 「~하기」 form (verb + 하기), e.g. 「이동하기」 ("go"), 「동의하기」 ("agree"), 「가입하기」 ("sign up"). Avoid generic 「확인」/「제출」 ("OK"/"submit") for actions.
- A button that only moves between screens may use 「확인」 or 「다음」 ("OK" / "next").
- With two buttons, the secondary one is 「닫기」 ("close") or 「다음에」 ("next time"), **never 「취소」** ("cancel"), because 「취소」 can read as cancelling the task in progress. AIT says the dialog's left button is 「닫기」.
- A CTA must say what happens when you tap it and must not repeat the screen's value pitch. Before 「4,000원 받고 금리 3%받는 통장 만들기」 ("get ₩4,000 and open a 3%-interest account") → after 「이동하기」 ("go"). Toss classed the "before" as a critical usability error.
- Conflict noted: in TDS Mobile dev docs, ConfirmDialog's cancel button defaults to 「취소」, which contradicts the writing rule 「닫기」 — [KSU](https://raw.githubusercontent.com/vmc-inner-circle/k-style-ui-ux/HEAD/docs/research/ux-writing/toss.md).

**Error messages** ([ERR](https://toss.tech/article/how-to-write-error-message), 2022-09-21; [SYS](https://toss.tech/article/introducing-toss-error-message-system), 2022-11-04, via KSU and search snippets)
- The most important value is telling the user what to do next. Structure: situation → cause → solution.
- The 6 principles: (1) design so the error doesn't happen; (2) use the component that fits (toasts stay short); (3) tell users how to fix it themselves; (4) use the user's words, not developer terms; (5) give a button that fixes it in one tap; (6) reduce negative phrasing and say what the user *can* do.
- At minimum, 「적어도 이게 사용자가 스스로 해결할 수 있는 문제인지 아닌지 정도는 알려주어야 해요」 ("At least tell users whether it's a problem they can solve themselves") — [ERR search snippet](https://toss.tech/article/how-to-write-error-message).
- Before 「비밀번호를 틀렸어요」 ("You got the password wrong") → after 「김토스님의 정보가 아니에요」 ("This isn't Kim Toss's information") — [ERR via search snippet](https://toss.tech/article/how-to-write-error-message). This is the user-language rule.
- 해요체 applies to errors too: 「"(우리 잘못인데) 에러 메시지에도 해요체를 적용해야 할까요?"」 ("(It's our fault) — should error messages also use 해요체?"). Toss's answer today is an obvious 「네!」 ("Yes!") — search snippet ([toss.tech](https://toss.tech/article/how-to-write-error-message) result set).
- Input-error template: 「집 주소를 확인해주세요.」 ("Please check your home address"), 「계좌번호를 다시 확인해주세요.」 ("Please check your account number again"). Avoid literal-translation patterns such as 「입력이 필요합니다」 ("input is required") and 「유효하지 않은」 ("invalid") — [SYS via KSU](https://raw.githubusercontent.com/vmc-inner-circle/k-style-ui-ux/HEAD/docs/research/ux-writing/toss.md).
- Maintenance/update template: title and body are written separately, and forced updates are distinguished from recommended ones — [SYS via KSU](https://raw.githubusercontent.com/vmc-inner-circle/k-style-ui-ux/HEAD/docs/research/ux-writing/toss.md).

**Third-party application of the AIT guide** (for illustration only, not Toss-authored) — [GitHub PR Park3min/run #29](https://github.com/Park3min/run/pull/29)
- 「~합니다/~하세요」 → 「~해요/~해 주세요」; 「되어요」 → 「돼요」; 「불러옴」 → 「불러왔어요」 ("loaded" as a noun ending → full sentence)
- Empty state: 「활동이 없습니다」 ("there are no activities") → 「아직 가민에 기록된 활동이 없어요. 러닝을 마치고 다시 불러와 보세요」 ("No activities recorded in Garmin yet. Finish a run and try loading again")
- Buttons named for their result: 「기록 표시하기」 → 「기록 보기」 ("display records" → "see records"); 「수정하기」 → 「기록 고치기」 ("modify" → "fix the record"); 「위치 초기화」 → 「처음 위치로」 ("reset location" → "back to start"); 「연동 해제」 → 「연결 끊기」 ("release link" → "disconnect"; this swaps 한자어 for a native verb)
- Error: 「이메일 또는 비밀번호가 올바르지 않습니다」 → 「이메일이나 비밀번호를 다시 확인해 주세요」 ("Email or password is incorrect" → "Please check your email or password again")

**Numbers / amounts / dates / units**
- No Toss writing source found sets formatting rules for numbers. KSU states this explicitly ("토스 라이팅 자료에 숫자 표기 규칙은 없습니다", i.e. Toss writing materials have no number-formatting rule). Patterns seen in Toss examples: amounts as 「4,000원」 (comma separators + 원), percentages as 「연 1%」 ("1% per year"), dates as 「2021년 10월 5일」, ages as 「만 19세 이상」 — [KSU](https://raw.githubusercontent.com/vmc-inner-circle/k-style-ui-ux/HEAD/docs/research/ux-writing/toss.md).
- A PR article headline, 「3min 대신 3분, UX라이팅에서 중요한 것은」 ("'3분' instead of '3min' — what matters in UX writing"), suggests Toss prefers Korean units over English abbreviations. I could only see the headline — [The PR (더피알)](https://www.the-pr.co.kr/news/articleView.html?idxno=48406).

### Inferences
- **Application to the coaching app** (inferred from the rules above, not Toss-stated):
  - Labels: 「승률 52.3%」 can stay as a compact label. In feedback sentences, use verb forms: 「첫 갱 성공률 낮음」 → 「첫 갱이 자주 실패했어요」.
  - Errors: 「API 키가 유효하지 않습니다」 → 「API 키를 다시 확인해 주세요」 + a 「키 입력하기」 button.
  - Empty states: 「데이터 없음」 → 「아직 분석할 경기가 없어요. 한 판 하고 다시 열어보세요」.
  - Units: 「3min」/「CS/min」 → 「3분」/「분당 CS」.
  - Secondary dialog buttons: 「닫기」 or 「다음에」, not 「취소」.
- The rule 「{명사}+{명사} 쓰지 않기」 ("don't stack nouns") strongly argues against dashboard-style noun chains in sentences (e.g. 「오브젝트 관여율 저조」, "objective participation rate low"). Short metric labels on charts are probably fine, since Toss's own UI uses noun labels (e.g. 「받을 배당금」, "dividends to receive").
- Toss gives no official rounding or decimal policy. A consistent rule (e.g. one decimal place for percentages, none in prose) would be the app's own decision.

### Gaps
- No Toss-published rules were found for empty states or loading states specifically.
- No Toss rule was found for rounding, decimals, 만/억 abbreviations, relative dates (「3일 전」, "3 days ago"), or number spacing (「35만 원」 vs 「35만원」).
- The full text of "3min 대신 3분" was not retrievable.

## Q3. Tools, processes, and measured effects

### Takeaway
Toss built its writing guidelines into tools. These include a Figma-side 「잡초 제거기」 (weed remover) that applies the voice-tone automatically, error-message templates used like design components, and an internal tool reported as "보이스톤 메이커" (Voice-tone Maker) with 8,000+ rules. Later the team moved its focus from automated correction to **writing education**. The only published metrics are from a 2026 marketing-copy article.

### Cited Findings
- The UX writing team lead (김자유) unifies the voice-tone of every message in the app, push notifications included. Their flagship project is 「잡초 제거기」, a tool in the design tool that 「토스의 보이스톤을 자동으로 적용해주는」 ("automatically applies Toss's voice-tone"). They also built error-message templates that are used like components — [PPL via search snippet](https://toss.tech/article/toss-people-2).
- The limits of automation: 「문장 하나만 보면 괜찮은데 전체 화면을 읽어봤을 때 흐름이 끊긴다든지」 ("each sentence is fine alone, but read as a whole screen the flow breaks"), plus repetition across a screen. Machines struggle with these. So: 「이미 써진 문구를 시스템으로 잘 교정하는 것보다, 팀원분들이 처음부터 문구를 잘 쓰게 만들고 싶었죠. 라이팅 교육으로 초점을 맞춘 거예요.」 ("Rather than correcting already-written copy with a system, we wanted teammates to write well from the start, so we focused on writing education.") — [PPL via search snippet](https://toss.tech/article/toss-people-2).
- "보이스톤 메이커" is described as a system version of Toss's writing guidelines with 「8,000개가 넘는 룰」 ("over 8,000 rules") — [GPTers "토스의 보이스톤 메이커를 GPTs로 만들기"](https://www.gpters.org/marketing/post/converting-toss-voice-stone-Sx4k3fHwbrSietx) and [brunch @thinkaboutlove/396](https://brunch.co.kr/@thinkaboutlove/396), as seen in search snippets. These are secondary sources. KSU notes that this tool name does not appear in the primary articles it reviewed, so treat the name and the 8,000 figure as unverified.
- 「가이드라인을 시스템으로 만드는 법」 (2022-11-04) describes turning the error guidelines into templates (input-error and maintenance/update templates) — [SYS](https://toss.tech/article/introducing-toss-error-message-system) via [KSU](https://raw.githubusercontent.com/vmc-inner-circle/k-style-ui-ux/HEAD/docs/research/ux-writing/toss.md).
- Process history: the first UX writer at first did a bit of everything (sentence correction, website, recruiting content), then chose to focus on the product based on internal interviews — [1ST search snippet](https://toss.tech/article/1st_uxwriter). Toss recruited UX writers to replace difficult financial terms — [etnews 2021-04-02](https://www.etnews.com/20210402000166). Per the 토스증권 UX Writer job post, the role sets rules for all of Toss's writing and helps teammates write well — [inthiswork](https://inthiswork.com/?p=313197).
- **Measured effects** ([MKT](https://toss.tech/article/44737), 2026-01-30, via [KSU](https://raw.githubusercontent.com/vmc-inner-circle/k-style-ui-ux/HEAD/docs/research/ux-writing/toss.md)): principle "promise a certain reward" → **20x impressions**; "deliver only one key point" → **10x+ impressions and CTR**; "say what kind of information it is" → **6x CTR**; "write conditions concretely" → **4x conversion, 2x CTR**. Two more principles had no numbers: "make the action feel light", e.g. 「가입」 ("sign up") → 「준비」 ("get ready"), and 「보기」 ("view") → 「찍기」 ("snap"/"take").
- On 해요체 metrics, one Toss article snippet says applying 해요체 doesn't move metrics much but has branding impact (「브랜딩 적으로 임팩트 있는 해요체 적용」, "applying 해요체 has branding impact") — search snippet (toss.tech result set; exact article unconfirmed).
- Criticism: the "easy finance" UX has been accused of omitting information on high-risk products or oversimplifying risk — [DIGITAL iNSIGHT, "토스 10년"](https://ditoday.com/토스-10년-쉬운-금융이-만든-혁신과-그늘/).

### Inferences
- A lightweight version of the 「잡초 제거기」 idea could work in this app: a lint script over UI strings that flags 「~습니다」, 「~되어요」, noun endings such as 「~완료/~불가/~없음」, 「취소」 on secondary buttons, and English unit abbreviations. This is inferred and not a Toss tool spec.
- Toss's own pivot shows that string-level linting misses screen-level problems (repetition, broken flow). So a full-screen read-through ("Remove empty sentences") is still needed.

### Gaps
- No A/B results were found for product (non-marketing) copy changes such as buttons or errors.
- Simplicity conference writing talks were not found in the searches.
- The date of 토스 피플 #2 and the exact implementation of 잡초 제거기 (plugin name, rule count) were not confirmed from primary text.
