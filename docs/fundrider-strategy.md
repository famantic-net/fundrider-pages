# Ride the Wave: How Fundrider Scores Funds by Momentum and Volatility

*A look under the hood of the Strategy page, the maths it runs, and the honest limits of what it can tell you.*

Picking funds in a system like the Swedish PPM has a peculiar property: switching is free. There is no transaction cost and no tax drag when you rotate from one fund to another. That removes the single biggest enemy of an active strategy and leaves one real question: which funds are growing strongly right now, and how do you spot the change in leadership in time?

The Strategy page in fundrider is built around one answer to that question, an approach often called momentum rotation, or more colloquially "riding the wave." This article explains exactly what it computes, why each piece is there, and what it deliberately does not promise.

## The raw material: normalized fund curves

Everything starts from the daily fund tables. Each fund's price history is normalized against its most recent value and then run through a base-10 logarithm. The effect is that the latest point of every fund sits at exactly zero, and earlier points sit above or below it.

This is more useful than it first sounds. Because the curves are logarithmic and share a common endpoint at zero, a fund that has climbed strongly has a deeply negative history, while a fund that has fallen has a positive one. Comparing funds becomes a matter of comparing shapes on the same scale, rather than juggling kronor and percentages across funds of wildly different sizes.

Two small hygiene steps run before any scoring. Funds with no fresh data for more than 10 days are treated as stale and dropped, so a fund that quietly stopped reporting does not pollute the ranking. And the log values are clipped to the range -2 to +2, which bounds the influence of a single freak data point.

## Momentum: the size of the wave

The first number the page computes for each fund is its momentum, and it uses what we call an integral score. The idea is to measure how much ground the fund has covered, not at a single horizon, but across several at once.

Write the fund's normalized log curve as $\ell_1, \ell_2, \dots, \ell_N$ from oldest to latest, where $\ell_t = \log_{10}\!\left(p_t / p_N\right)$ so that the latest value is $\ell_N = 0$. For a set of look-back windows $W$, the momentum score sums the last few log values in each window and negates the result:

$$M \;=\; \sum_{w \in W} \left( -\sum_{t = N - w + 1}^{N} \ell_t \right), \qquad W = \{5,\ 10,\ 21,\ 64,\ 129\}.$$

The windows are 5, 10, 21, 64 and 129 trading days, which correspond roughly to a week, a fortnight, a month, a quarter and half a year. They are weighted equally.

The negation is what makes higher mean better. A fund that rose has negative log history, so summing those values gives a negative number, and negating it produces a large positive score. A fund that fell produces a negative score.

There is a subtle and deliberate consequence of using nested windows that all end "now." The most recent five days appear in every one of the five windows, so they are effectively counted five times. The next stretch appears in four windows, and so on. Without any explicit weighting, recent performance ends up mattering far more than older performance. That is exactly the behaviour you want from a "what is working right now" signal, and it is the same integral score the daily email uses for its short-term list.

## Volatility: how bumpy the ride is

A big wave is only half the story. A fund can climb a long way through a series of violent lurches, or it can grind upward smoothly. Those are very different risks, and momentum alone cannot tell them apart.

So the page also measures each fund's volatility: the standard deviation of its daily log returns over the last 63 trading days, about three months. The daily log return is the day-to-day change in the curve,

$$r_t \;=\; \ell_t - \ell_{t-1} \;=\; \log_{10}\!\left(p_t / p_{t-1}\right),$$

and the volatility is the sample standard deviation over the last $n = 63$ returns,

$$\sigma \;=\; \sqrt{\frac{1}{n - 1} \sum_{t} \left( r_t - \bar{r} \right)^2 }.$$

The middle equality above is the reason volatility is unaffected by the latest-equals-zero normalization: subtracting consecutive log values cancels the shared $\log_{10} p_N$ term entirely. A fund needs at least 21 daily returns before a volatility figure is trusted.

For display the page converts this into an approximate annualized percentage, which is easier to read, but the ranking uses the raw daily figure:

$$\sigma_{\text{ann}} \;=\; \left( e^{\,\sigma \,\ln 10 \,\sqrt{252}} - 1 \right) \times 100\%.$$

## Combining the two: the general score

Here is where it gets interesting.

The obvious move is to rank funds by return divided by volatility, the classic Sharpe-like ratio. Steady climbers should beat jumpy ones. But when you try it across an entire fund universe, something perverse happens: money-market and bond funds shoot to the top. They barely grow, but their volatility is so tiny that dividing by it produces an enormous ratio. The "best" fund becomes a cash-like instrument that is going nowhere. That is the opposite of riding a wave.

**The fix is to make the strength of the volatility adjustment a dial rather than an absolute**. The page uses a general form, with $M$ the momentum and $\sigma$ the volatility from above:

$$\text{score} \;=\; \frac{M}{\sigma^{\,\alpha}}, \qquad \alpha \in [0,\ 1].$$

The exponent $\alpha$, labelled "volatility influence" on the page, runs from 0 to 1:

- At $\alpha = 0$, the denominator is 1 and volatility is ignored entirely, so you rank purely by wave momentum: the strongest growers regardless of how rough the ride.
- At $\alpha = 1$, you get the full risk-adjusted ratio $M / \sigma$, which strongly favours steadiness and, at the extreme, drags those cash-like funds back to the top.
- In between, you get growth-led ranking with a steadiness tilt. The default of $\alpha = 0.5$ turns out to be a sensible middle: the top of the list is dominated by genuine growth funds, and among funds of similar strength the steadier one wins.

This single knob unifies two philosophies that look like separate strategies. "Rank by momentum, use volatility as a tie-breaker" and "filter to growers, then rank by risk-adjusted return" are just two settings of the same formula.

For context the table also shows plain period returns over one, three and six months. These are read straight off the log curve and are not part of the score:

$$R_n \;=\; 10^{\,\ell_N - \ell_{N-n}} - 1 \;=\; \frac{p_N}{p_{N-n}} - 1.$$

### Reading momentum and volatility together

In practice it helps to think in four quadrants:

- High momentum, low volatility is the ideal ride: a strong, steady climber. These rise to the top as you increase alpha.
- High momentum, high volatility is strong but jumpy. Bigger potential upside, but prone to sharp reversals.
- Low momentum, low volatility is calm but barely growing, the cash-like case. Not a wave worth riding.
- Low momentum, high volatility is the worst of both: risky without reward.

## Beyond the score: reading the shape of the wave

A single score, however well constructed, throws away the *shape* of a fund's curve. Yet shape is exactly what one reads off the charts: is this trend accelerating or tiring, is it a clean climb or a jagged scramble, is it still making new highs or already fading? In practice that shape-reading, plus discretionary timing, has tended to do better than the purely mechanical ranking. So the page reports three shape-and-timing columns alongside the score. They are decision aids; they do not change the ranking.

Using the same normalized log curve $\ell_t = \log_{10}(p_t / p_N)$ as before:

**Acceleration** asks whether the trend is speeding up or rolling over. Fit a least-squares line to the last $W$ log values to get a recent daily slope $s_{\text{recent}}$, and another to the $W$ values before that to get a prior slope $s_{\text{prior}}$ (with $W = 21$, about a month). Convert each slope to a daily percentage and take the difference:

$$\text{Accel} \;=\; \left( 10^{\,s_{\text{recent}}} - 10^{\,s_{\text{prior}}} \right) \times 100 \quad \text{(percentage points per day).}$$

Positive means the recent pace is faster than the prior pace, the signature of catching a wave early; negative means it is decelerating or topping. A fund can have strong momentum yet negative acceleration, which is the quantified version of "still high, but losing steam."

**Trend quality** measures how clean the climb is: the coefficient of determination $R^2$ of a straight-line fit to the last $W = 63$ log values (about a quarter),

$$R^2 \;=\; 1 - \frac{\sum_t \left( \ell_t - \hat{\ell}_t \right)^2}{\sum_t \left( \ell_t - \bar{\ell} \right)^2},$$

where $\hat{\ell}_t$ is the fitted line and $\bar{\ell}$ the mean. Near 1 is a smooth, reliable trend; a low value is the same net move achieved through violent lurches. Read it together with momentum's direction: a high $R^2$ on a rising fund is a clean ride, on a falling fund it is a clean decline.

**Peak gap** captures whether the fund is breaking out or fading. Over the last $W = 126$ values (about six months) it compares the current level to the highest level reached:

$$\text{Peak gap} \;=\; \left( 10^{\,\ell_N - \max_{\tau} \ell_\tau} - 1 \right) \times 100\%.$$

Zero means the fund is at a new high (still breaking out); a negative value is how far below its recent peak it now sits (fading). Because the curve is normalized to the latest point, this is simply $10^{-\max \ell} - 1$ over the window.

Taken together these let you distinguish, among funds with similar scores, the fresh accelerating breakout from the tiring leader that is drifting off its highs.

## Market breadth: the regime gauge

The per-fund views cannot tell you what the *whole market* is doing, and the single best discretionary decision is usually a regime call: lighten up when everything is rolling over. So a banner at the top of the page reports breadth, the share of funds currently trending up, and the median momentum across all funds:

$$\text{breadth} \;=\; \frac{\#\{\, f : M_f > 0 \,\}}{\#\text{funds}}, \qquad \tilde{M} \;=\; \operatorname{median}_f \, M_f,$$

where $M_f$ is each fund's momentum. The banner is colour-coded: at least 60% up is a broad uptrend (rotation works well), 40 to 60% is mixed (be selective), and below 40% is broad weakness, a cue to lighten up or rotate defensive. Breadth typically turns down before any single fund's own trend gate trips, so it is an earlier warning of a regime change than the per-fund signals can give on their own.

## The trend gate: knowing when not to play

Relative ranking tells you the best fund. It does not tell you whether anything is worth holding at all. In a broad downturn, the "strongest" fund might still be falling, just falling less than the rest.

The trend gate is an absolute filter that sits in front of the ranking. Only funds whose momentum clears a threshold $g$ are scored at all,

$$\text{eligible} \;=\; \{\, f : M(f) > g \,\}, \qquad g = 0 \text{ by default,}$$

so with the default only funds that are actually trending up appear. Raise $g$ to be stricter, lower it into negative territory to include funds that are sliding, though that is not advisable for a hold list.

## The defensive fallback: where to hide

When the gate filters out most of the universe, that is itself a signal. Broad weakness means the right move is to rotate to safety, not to chase the least-bad loser.

The page classifies fixed-income and cash-like funds by name, matching tokens such as ränta, obligation, FRN, likviditet and penningmarknad, and flags them as defensive. It then suggests one to hold when breadth is poor, defaulting to the defensive fund with the strongest momentum, and lets you override the choice. When five or fewer funds pass the trend gate, the panel turns amber as a deliberate "consider going defensive" cue.

## Hysteresis: trading less, not more

Even with a clean ranking, a naive rule of "always hold the top five" produces constant churn. Funds hover near the boundary and get bought and sold on noise. Because PPM switching is free this costs no money, but it still exposes you to whipsaw, where you sell just before a fund recovers and buy just before it stumbles.

Hysteresis fixes this with two different thresholds instead of one:

- Buy a fund only once it climbs into the top $N$ by score, default 5.
- Sell a fund you already hold only once it falls out of the top $M$, default 10, where $M \ge N$.

Writing $H$ for your current holdings and $\text{rank}(f)$ for a fund's position by score (with an unranked fund, one that failed the gate or went stale, treated as $\text{rank}(f) = \infty$), the three action sets are:

$$
\begin{aligned}
\text{Buy}  &= \{\, f : \text{rank}(f) \le N,\ f \notin H \,\} \\
\text{Sell} &= \{\, f \in H : \text{rank}(f) > M \,\} \\
\text{Hold} &= \{\, f \in H : \text{rank}(f) \le M \,\}
\end{aligned}
$$

The gap between $N$ and $M$ is a dead band. A fund sitting at rank 7 is not in your buy zone, but if you already own it, it is not yet in your sell zone either, so you simply keep it. Funds have to move decisively before you act, which is exactly the point: you ride the wave through its middle rather than reacting to every ripple. A fund you hold that fails the trend gate or goes stale has $\text{rank}(f) = \infty > M$, so it falls into the Sell set.

The page turns this into a concrete Buy, Sell and Hold list, and shows which funds you currently hold directly in the ranking table.

## Connecting it to your actual portfolio

The rebalance suggestions are only meaningful against something. The page offers two sources.

In "My portfolio" mode it reads your real holdings, the ones you entered in the Portfolio widget on the charts page, which live in the browser's local storage. Funds you own that have dropped out of the top M are listed as "sell these." Recommended funds you do not own are listed as "add these." Funds you own that are still within the buffer are held.

Crucially, the Strategy page never edits your portfolio. Your holdings carry purchase dates and amounts, which a ranking page has no business inventing. Instead you make the actual changes in the Portfolio widget, then press "Re-check portfolio" and the page re-reads it: funds you sold drop off the list, and funds you added move into the Hold column. It reconciles itself against reality rather than trying to drive it.

In "Strategy set" mode the page instead maintains its own hypothetical holding set, useful for experimenting without touching your real portfolio. There, applying a rebalance commits the suggested holds and buys as the new set.

## What this is, and what it is not

It is worth being blunt about the limits, because the easiest way to misuse a tool like this is to mistake it for something it is not.

This is a ranking of current strength. It is not a forecast. It cannot catch tops or bottoms, and it never claims to. The entire design accepts that turning points are lagged: you will enter a little late and exit a little late. The money, if there is any, is in capturing the long middle of sustained trends and stepping aside during sustained declines.

Every tuning choice on the page is really a single trade-off in disguise: responsiveness versus stability, or lag versus whipsaw. A shorter look-back, a tighter gate, a smaller dead band, all make the page react faster and churn more. The opposite settings make it calmer and slower. There is no setting that removes both problems, and the honest way to find your preferred point on that dial is to test it against history rather than to tune it by eye.

That history-based validation, a proper walk-forward backtest, is the natural next chapter for fundrider. The Strategy page tells you what looks strong today. A backtest is what tells you whether acting on that signal would actually have paid off. Until then, the Strategy page is best read as a disciplined, transparent screen for spotting which funds are riding a wave right now, with the rules of engagement written down rather than left to gut feeling.
