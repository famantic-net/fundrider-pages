# Does Riding the Wave Actually Pay? The Fundrider Backtest

*What the Backtest page does, how it avoids fooling itself, and the sobering thing it reveals about beating the default fund.*

The Strategy page answers "what looks strong right now." It is a ranking, not a promise. The obvious next question is the honest one: if you had actually followed that ranking, would you have come out ahead? The Backtest page exists to answer exactly that, by replaying the strategy day by day over several years of real fund prices and comparing the result against the benchmark that actually matters.

## The benchmark that matters: AP7 Aktiefond

In the Swedish premium pension, if you make no choice at all your money goes into AP7 Aktiefond, the state default fund. So the only benchmark worth measuring against is AP7 itself. Beating a generic index is irrelevant; the real test is whether all this rotation does better than simply doing nothing and leaving the money in the default. Every result on the page is shown as excess return over AP7.

## Avoiding the cardinal sin: look-ahead

A backtest is only worth anything if, at every past moment, it uses only information that was actually available then. This is where it would have been easy to cheat by accident.

The Strategy page works off the sliced tables, which are each fund's price normalized to its most recent value. That normalization divides by the latest price, and the momentum score is a sum of those normalized values. Because it is a sum, the latest-price constant does not cancel out, so feeding those tables into a backtest would quietly leak the future into every past decision.

To avoid this, the backtest does not use the sliced tables at all. It reads the raw daily snapshots that are fetched and committed every day, which contain the actual buy and sell prices for every fund on that date. From these it builds a clean price history with three properties that keep it honest:

- **Stable identity.** Each fund is keyed by its fund number, not its name, so a fund that is renamed stays a single continuous series instead of splitting in two.
- **Survivorship safety.** Each day's snapshot only contains the funds that existed that day, so funds that were later discontinued are present for exactly the period they really existed, and no longer.
- **As-of-date normalization.** At each rebalance date the strategy is recomputed by normalizing each fund to its price on that date. The signal at any past day therefore sees only that day's history, never the future.

A freshness filter discards stale quotes (a price more than ten days old relative to the snapshot), which both removes dead funds and keeps the timeline to genuine trading days. The price used is the mid of the buy and sell quote, which for normal fund units are effectively the same.

## The simulation

The backtest reuses the very same signal code as the live Strategy page, so the two can never drift apart: the integral momentum score, the volatility, the combined score, the trend gate, the defensive fallback and the hysteresis buffer are all imported directly. On top of that it runs a simple, mechanical portfolio:

- Rebalance on a fixed cadence (monthly by default).
- Hold the selected funds equally weighted.
- Carry holdings across rebalances through the hysteresis buffer, so a held fund is only sold once it falls well out of the top ranks, not the moment it slips.
- When breadth is poor (few funds pass the trend gate) rotate fully into the best defensive fund.
- Compound returns daily between rebalances.
- Apply no transaction costs, because switching funds within the premium pension is free.

The output is an equity curve of the strategy against AP7, plus the statistics that matter: total return, compound annual growth rate (CAGR), annualized volatility, Sharpe ratio, maximum drawdown, the hit rate (share of periods that were positive), how often it beat the benchmark, and the average turnover per rebalance.

## The parameter heatmaps

A single backtest only tells you about one set of choices. The interesting question is how sensitive the result is to those choices, which is what the sweep answers. It runs a full backtest for every combination on a grid of two parameters and colours each cell by its excess CAGR over AP7: green beats the default fund, red trails it. The cell label is the strategy's own CAGR.

The page shows two of these heatmaps over the same grid, because the right answer depends on where you invest:

- **PPM portfolio (max 5 funds).** The premium pension lets you hold at most five funds, so this heatmap caps holdings at five. This is the realistic picture for a PPM account.
- **Unrestricted (for example Avanza).** Most premium-pension funds are also available through a broker such as Avanza, which does not cap the number of funds (though it does charge fees the pension does not). With the cap removed, the strategy can hold a wider basket, so this heatmap shows what broader diversification would have achieved.

Comparing the two side by side is the most instructive part of the page.

## The sobering finding

Putting realism first changes the story. With no cap, the strategy looks genuinely strong: holding a wider basket of eight to twelve funds and rebalancing roughly every two months beats AP7 by a wide margin over the test period. The diversification smooths out the whipsaw of betting on a few volatile momentum leaders.

But none of that is reachable inside a premium-pension account, because you cannot hold more than five funds. Cap the portfolio at five and the edge largely evaporates: above five funds the result simply stops improving (there is nothing to add), and the only configuration that beats AP7 does so by a thin margin, at one specific rebalance cadence, with both neighbouring cadences underperforming. A lone good cell flanked by worse ones on either side is the classic fingerprint of in-sample luck rather than a durable effect.

The honest conclusion is that, constrained to the five funds a premium-pension portfolio allows, this mechanical ride-the-wave rule has, over this period, roughly matched the default fund at best and trailed it at most settings. That is a genuinely useful thing to know before trusting any single backtested configuration, and it is exactly why the page enforces the cap rather than quietly reporting the flattering uncapped numbers.

## What the backtest does not capture

It is worth being clear about the gap between this mechanical test and how the tools are actually used well. The backtest mechanizes only half of the real process: it ranks by the score and rebalances on a calendar. It does not read the *shape* of the curves (acceleration, trend quality, distance from the peak) and it does not exercise discretionary timing or step aside ahead of a market turn. Those are precisely the things a person watching the Strategy page and the charts can add, and they are where the real edge has tended to come from. The shape-and-timing columns and the breadth banner on the Strategy page exist to make more of that judgement explicit.

So read the backtest for what it is: a rigorous, no-look-ahead validation of the *mechanical* rule, and a reminder that the rule alone is not the strategy. It tells you the floor, not the ceiling.
