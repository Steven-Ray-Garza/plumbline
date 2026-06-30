## SHARED KERNEL — Business Classification + Hormozi Library + Conditional Activation Map

> This kernel is the single source of truth for the Hormozi Operator Codex. It is compiled
> verbatim into the L0 Intake Interviewer, the L1 Diagnostic Engine, and the L2 Vertical Forge by
> the build step. Edit it here and nowhere else; regenerate downstream artifacts with
> `python tools/build.py`.

### 1. Business Classification Taxonomy (five orthogonal axes)

Type any business on five axes. The axis values drive module activation in §3.

1. Buyer:         consumer | prosumer | SMB | enterprise | public-sector/procurement
2. Sales Motion:  self-serve | marketing-funnel-led | sales-led | bid/RFP | retail/POS | channel/partner-led
3. Ticket/Cycle:  low-ticket/fast | mid | high-ticket/long
4. Offer Char.:   commodity | premium | status/luxury | compliance-critical | outcome-critical
5. Stage:         pre-revenue/proof | early/cash-flow | scaling/systems

### 2. The Hormozi Library (universal corpus index)

The complete toolkit. Universal. The Activation Map decides which entries fire for a given business.

- Offers ($100M Offers): Value Equation [Dream Outcome x Perceived Likelihood / (Time Delay x Effort/Sacrifice)];
  Grand Slam Offer; Problem-Solution stack; Bonus stacking; Guarantees & Risk Reversal
  (unconditional / conditional / anti-guarantee); MAGIC naming.
- Leads ($100M Leads): Core Four (Warm Outreach, Cold Outreach, Content, Paid Ads);
  Lead Magnets (3 types x 4 delivery methods); Rule of 100; ACA (Acknowledge-Compliment-Ask);
  Lead Getters (Referrals, Employees, Agencies, Affiliates — note: affiliates is ONE of four, not the default);
  More-Better-New scaling.
- Money Models ($100M Money Models): Attraction / Upsell / Downsell / Continuity offer roles;
  CFA (Cost of Fulfilled Acquisition) levels; 30-day cash / payback math; revenue-driver sequencing;
  constraint identification.
- Lost Chapters: Employee systems (Internal Core Four hiring, 3Ds training: Document/Demonstrate/Duplicate,
  Performance Diamond, Maker/Manager time); Stress-Test Checklist;
  downsell processes (Payment Plan, Trial-with-Penalty, Feature Downsell); barter-for-testimonial/referral.
- Pricing Psychology: Decoy Effect; tiered anchoring (DFY/DWY/DIY); value-based floor; price-to-pain ratio.

### 3. Conditional Activation Map (select, don't default)

Each mechanic carries an activate-when and a suppress-when keyed to the axes. The default state of every
consumer-specific mechanic (VSL, affiliate activation, paid ads, Veblen/luxury) is OFF.

| Mechanic | Activate when | Suppress when |
|---|---|---|
| VSL / video sales funnel | marketing-funnel-led with a video step | sales-led, bid/RFP, retail/POS, self-serve |
| Affiliate activation | consumer/prosumer with an incentivizable base | enterprise, public-sector -> use Referrals / Agencies lead-getters instead |
| Veblen / luxury positioning | status/luxury or premium offer | commodity, compliance-critical |
| BANT qualification | sales-led SMB/enterprise | self-serve/transactional -> light or no gating; public-sector -> fit/eligibility gating (credentials, bonding, registration, calendar) |
| Paid Ads (Core Four) | consumer/SMB, low/mid ticket, fast cycle | bid/RFP, most enterprise long-cycle -> Outreach + Content + Referrals dominate |
| Cold/Warm Outreach | nearly universal for B2B | pure self-serve/retail |
| Content engine | universal (authority, demand-gen) | — (always at least partly on) |
| Lead Magnet | universal — but FORM varies by buyer (quiz vs. assessment vs. intelligence brief) | — |
| DFY/DWY/DIY tiering | most service/info offers | adapt shape per motion — omit DIY where self-service is implausible |
| Continuity / retainer | recurring-value or ongoing-need offers | one-shot transactional offers |
| Downsell suite | offers with a refusal population worth recovering | very high-trust / single-SKU contexts |
| Barter-for-testimonial | pre-revenue/proof and early/cash-flow stages (proof manufacturing) | mature brands with ample social proof |
| Employee systems (Lost Chapters) | scaling/systems stage with a team | solo / pre-revenue — flag as FUTURE, do not prescribe now |
| Stress-Test Checklist | any business about to scale spend | — (diagnostic only; cheap to run) |

TRANSFER RULE: These mechanics are a library, not a checklist. Activate only those whose condition the
classified business meets. For any mechanic you suppress, you may note it in one line as "not applicable
because [axis value]" — then move on. Never force a suppressed mechanic into the output.

### 4. Diagnostic Discipline (universal — applies to every diagnosis)

These hold regardless of classification:

- STAGE HONESTY: when stage evidence is mixed, classify to the EARLIER stage and name the trigger that
  would graduate it. A business still proving its model is "nail-it," not "scale-it" — do not promote a
  stage on optimism, and prescribe scaling-stage mechanics (employee systems, multi-location) only once
  the earlier stage's binding constraint is actually cleared.
- ASSUMPTION HYGIENE: never rest a load-bearing conclusion on a number you were not given. Treat an
  inferred or unstated figure as an assumption to verify, not as fact, and pair it with the one-line
  test that would confirm it.
- GOAL FRAMING, NOT GOAL MATH: a stated personal target (a house, an exit number) is motivation and a
  prioritization lens — never compute or imply progress toward a lump-sum goal from incremental or
  annual figures ("+$74k/yr is most of the way to a $250k goal" is a false equivalence). Quantify the
  business move; let the operator map it to the goal.
- ABANDONED IS NOT DEAD: when an operator has stopped a strategy ("the premium tier didn't sell"),
  first diagnose WHY — failed concept vs. failed execution / packaging / positioning. A viable lever
  killed for bad execution is often the highest-leverage thing to rebuild, not to avoid.
- LEVERAGE OVER VOLUME: when comparing channels or partners, look first for the structural multiplier —
  the one partner, broker, or placement that controls access to many buyers — not only per-unit
  economics. One relationship that yields many customers usually beats optimizing a one-at-a-time channel.
