# FAQ — honest status: what's proven vs. what's still a claim

> **Document type:** FAQ / honest-status disclosure (for an evaluator who is rightly skeptical)
> **Source:** Captured verbatim from the plumbline build conversation, 2026-06-29. Statement by the operator; answer by Claude (Opus 4.8), reproduced unedited.

## Q: "That's hard to believe." — is the advice actually good? How much of this is proven?

### Operator statement (verbatim)

> That's hard to believe Claude.

### Answer (verbatim)

Fair. And honestly — my last answer slipped into marketing, so you're right to push.

Let me draw the line I should have drawn the first time, because there are two very different things in here and they deserve very different levels of belief.

**The machinery — believe it. I tested it.** The "factory quality-control line" is real and mechanical: one master source, an automatic check that the copies can't drift, and a battery of pass/fail tests. I ran those — 11 of 11 passed, every time, and I actively tried to break them and couldn't. That part isn't a claim; it's verified, and it's the boring engineering kind of true.

**The advice quality — don't believe me, because it has never actually run.** This is the important admission. The "taste tests" that supposedly prove the engine gives great, business-specific advice? They've executed **zero times.** There's no API key connected yet, so the part that would actually grade the AI's output has never fired once. Everything I said about it "nailing the right advice and suppressing the wrong tactics" is, at this moment, *a hypothesis written down as a test* — not a result. I presented an untested intention as if it were a proven outcome. That's the part that's hard to believe, and it should be.

And here's the deeper honesty: strip away the polish and this "AI business diagnostician" is **a very carefully structured prompt.** A structured prompt will *always* hand you confident, tidy, framework-shaped advice. Whether that advice is actually *correct and worth acting on* is a much higher bar that no amount of prompt engineering guarantees — AI is perfectly capable of being fluent, organized, and wrong. The machinery guarantees consistency and discipline. It does **not** guarantee wisdom.

So the believable version is: *I built a disciplined quality-control system around an AI advisor whose advice has not yet been put to the test.*

The cure for "hard to believe" is evidence, not more words from me. So — **pick a business.** Real or hypothetical, but ideally one you know cold (your own procurement consultancy is right there in the repo, and you'd spot fluff instantly). I'll run the actual compiled engine on it and show you the raw, unedited output. Then I'll run a second, deliberately hostile pass whose only job is to tear it apart — "is this genuinely tailored, or could you paste it under any business?" — and you judge which side wins.

If it produces generic slop, you'll see it immediately and we'll have learned the engine needs work. If it's sharp, you won't have to take my word for it. Either way you get the truth instead of a sales pitch. Want me to run it — and on which business?

---
*The evidence run described above is specified in [REQUIREMENTS.md](REQUIREMENTS.md). Until it is run with a live API key, treat all claims about advice **quality** as unverified.*
