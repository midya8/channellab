# ChannelLab method and limits

Original finite implementation and developed controls. Theorems are classical, not new. The order concerns supplied experiments, not estimated sensor quality.

## The experiment convention

An experiment E is a 2-by-m row-stochastic matrix. E[s][j] means P(signal j | state s). A and B may have different signal counts, each one to three. The supplied prior p=P(state 1) is strictly between zero and one. All decisions maximize expected payoff. Payoffs are a 2-by-k matrix, one to three actions. Signals are observed before choosing an action. No action changes the experiment or state.

Signal j has joint masses ((1-p)E[0][j],pE[1][j]), mass m_j and posterior q_j=pE[1][j]/m_j. A zero-mass signal retains its identity and a null posterior. Its joint action values are all zero. Choices there remain distinct in the complete policy family; they affect no expected value.

For a supplied payoff matrix U, an action a at signal j contributes:

```text
v(j,a) = (1-p) E[0][j] U[0][a] + p E[1][j] U[1][a]
V(E,U,p) = sum_j max_a v(j,a)
```

Every one of k**m deterministic signal-to-action policies is enumerated, including every tie. At most 27 per experiment. The selected action is the smallest maximizing index. The no-signal value is max_a((1-p)U[0][a]+pU[1][a]); information value is their difference. Randomization cannot raise the maximum of this finite linear expected-payoff objective. A policy's value is not a claim of how a real person would act.

## Order, not a single score

A dominates B when one state-independent row-stochastic kernel K maps A to B: A K = B in both state rows. This is Blackwell dominance. Every decision rule on B can then be replicated on A by first drawing a synthetic B signal from K. Raw channels form a preorder; modulo mutual dominance it is a partial order. Relabelled, split or pure-noise signals can differ as matrices yet be informationally equivalent.

For a binary state and a full-support prior, dominance is equivalent to convex order of the posterior laws. Both posterior laws have mean p. Define the call function:

```text
C_E(t) = sum_j m_j max(q_j-t,0)
       = sum_j max(p E[1][j] - t m_j,0).
```

A dominates B iff C_A(t)>=C_B(t) for every t in [0,1]. For finite laws, each function is piecewise affine, with slope changes only at supported posteriors. The difference is affine between successive knots of their union. A nonnegative value at both endpoints makes the whole segment nonnegative. ChannelLab checks every supported posterior plus 0 and 1, using exact rationals, not a sampled threshold grid. At most 8 distinct knots occur. Outside [0,1] common mass/mean make the comparison equal. The chart connects the exact knots; its pixel coordinates use floating point for display only. Tables and exports retain exact fractions.

Full support matters: a prior concentrating on one state cannot detect a difference in the other state's row. The implementation rejects p=0 and p=1, rather than claiming an order from a degenerate posterior comparison. The result's relation does not depend on which full-support prior is used, but numerical posterior positions and decision values do. The scalar call criterion is for two states. It is not a test for arbitrary multi-state experiments.

### Failure has a decision witness

If C_A(t)<C_B(t), choose two actions. Action 0 pays 0 in both states. Action 1 pays -t in state 0 and 1-t in state 1. Its posterior expected payoff is q-t; the optimal payoff is max(0,q-t). Thus V(B)-V(A)=C_B(t)-C_A(t)>0. The first failing sorted knot is selected. Both witness policy families, every signal action value/tie, and the strict exact gap are returned. Reversing the comparison constructs its own witness, not the same task with a changed sign.

Default A=[[1,0],[1/2,1/2]], B=[[1/2,1/2],[0,1]], p=1/2. Both have classification value 3/4. At t=1/3, B's call value 1/4 beats A's 1/6 by 1/12. At t=2/3, A's 1/12 beats B's 0 by 1/12. Neither dominates. Equal accuracy, alphabet size, entropy reduction or one task cannot establish the all-decision order.

### Success has a constructive kernel

For m source and n target signals, K has mn<=9 variables. Equalities are each source-row sum 1 and each reconstructed target cell in each state. Nonnegativity supplies bounds. The feasible set is bounded (every cell is in [0,1]) and closed. If it is nonempty, it has a vertex. Reduce the equality system exactly, obtaining rank r. Enumerate every r-column basis in lexicographic order, solve the square reduced system exactly, put other variables at zero, and keep the first nonnegative solution. A degenerate vertex has fewer than r positive variables but its independent positive-support columns extend to a basis. This is a small exhaustive basic-feasible-solution method, not a scalable LP solver.

The report includes K, every row sum, both reconstructed state laws and the prior-weighted source/target joint mass m_j K[j][i]. For every target signal it returns the total mass and state 1 joint mass. These equal the target's masses and its posterior-times-mass. Zero target mass is not divided by zero; zero source columns have arbitrary stochastic K rows that cannot change either state law. The returned vertex is one witness, not all feasible kernels. Signal-space K and a coupling over posterior beliefs are distinct objects.

## Independent replay and limitations

`verify.py` imports strict validation/encoding, not the generator, its Gaussian elimination or its basis search. It recomputes signal masses, hinge knots and values directly from posterior calls; evaluates each complete policy state by state; and checks each feasible kernel's nonnegativity, row sums and exact matrix reconstruction. Failed directions require the full strict decision witness. Every derived field is sealed by exact, type-sensitive JSON comparison. Valid alternative feasible kernels are accepted when their coupling fields match. This is computational checking, not a proof assistant or a general formal certificate format. Shared schema and mathematical assumptions remain common failure modes.

The BigInt browser engine independently implements the same finite schema and output. Rational arithmetic/strict-JSON adapters were reused from the portfolio's RiskLab/BellmanLab; the experiment-order logic is new original implementation. Full comparison uses sorted lossless JSON, not ordinary `JSON.parse` as an exact-integer oracle. The `large_exact` control has output denominators beyond 2**53. Input components remain bounded by 1,000,000. Drawing the chart with Number does not feed into inference.

Strict input has exactly version/prior/a/b/payoffs. Version is integer 1. All rational values are non-boolean integers or [integer,positive denominator] pairs, absolute raw numerator<=1,000,000 and raw denominator<=1,000,000. Channels have nonnegative entries summing exactly to 1. Payoff magnitudes<=100. Combined normalized input-denominator LCM<=1,000,000. Unknown/duplicate keys, decimals, exponent numbers, nonfinite values, malformed dimensions and booleans fail. Input must be canonical UTF-8 JSON within 64 KiB for CLI/browser parsing; reports for CLI verification are capped at 8 MiB. Programmatic `compare` accepts a parsed object. Counts limit enumeration, not arbitrary integer bit complexity, output bytes, memory or wall time. The checker additionally caps each encoded report rational component at 10**100.

No dataset, external service, API, learned model, empirical sensor calibration, channel learning, sequential experiment design, finance, privacy guarantee, real-world decision recommendation, speed/scale benchmark, universal multi-state solver or new Blackwell theorem is claimed. Exact answers are conditional on supplied probabilities and payoffs.

## Developed controls and evidence provenance

Thirteen controls cover incomparability, perfect/noisy/blind chains, relabelling, split signals, null posteriors, nonunique pure-noise kernels, skew prior, task indifference, rectangular three-signal garbling, tiny prior and large exact fractions. Twelve were hand-constructed. `large_exact` is candidate 0 of the disclosed seed 17029 search in `tools/find_large.py`. It is a development example, not a held-out result.

The complete grid is all 25 two-output channels whose two Bernoulli rows use denominator 4, paired in all 625 ordered combinations, at prior 1/2 with the classification task. In addition, seed 17023 generates 72 rectangular channel pairs: eight for each of the nine 1..3 by 1..3 signal-count pairs, with three supplied actions. Together with 13 controls this makes 710 complete report comparisons. This grid checks a finite declared domain, not every rational channel. Numerical HiGHS compares feasibility in both directions for every problem; it is optional external evidence, not used to produce exact production outputs. Test counts, actual run totals and browser counts are in README, not inferred from algorithm bounds.

## Sources inspected November 10, 2026

1. [Sargent and Stachurski, QuantEcon, Blackwell's Theorem on Comparing Experiments](https://python.quantecon.org/blackwell_kihlstrom.html). Matrix garbling, full-support prior, posterior convex order and binary call criterion. We replace its illustrative sampled thresholds with complete finite knots.
2. [Tilman Borgers, Notes on Blackwell Dominance, December 3, 2023](https://websites.umich.edu/~tborgers/BlackwellDominance.pdf). Finite Markov matrix convention, risk-set equivalence, posterior criteria and integrated binary CDF proof. Our call function is the corresponding upper hinge; equal means connect put and call differences.
3. [Omer Tamuz, The Value and Cost of Information, April 9, 2025](https://www.tamuz.caltech.edu/teaching/info.pdf). Sections 1-3 on indirect expected utility, binary experiments, posterior means and Blackwell order. Later cost/asymptotic results are not implemented.
4. [Lones Smith, Blackwell's Theorem with the Original Wonderful Proof](https://www.lonessmith.com/wp-content/uploads/2025/04/1-Appendix-Blackwells-Theorem-with-the-Original-Wonderful-Proof.pdf). Finite state-independent garbling and decision-rule replication, displayed matrix equations. Its informal inclusion sentence has a direction typo; corroborating equations/sources determine the convention used here.
5. [Blackwell, Equivalent Comparisons of Experiments, 1953, bibliographic abstract](http://dml.mathdoc.fr/item/1177729032/). Historical attribution and dichotomy comparison; only abstract/bibliographic entry inspected, not full original paper. The archive's issue-number metadata differs from common bibliographies. DOI retrieval returned no content and is not presented as full-text review.
6. [SciPy official HiGHS linprog API](https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs.html). Equality/nonnegative feasibility and termination status for optional numerical reference. Online documentation version and installed SciPy may differ; actual installed version is printed by the check.
7. [Python official Fraction API](https://docs.python.org/3/library/fractions.html). Exact integer fractions and float-conversion caveats. Only Python 3.10-compatible common APIs are used.

Academic expositions, original-research bibliography and official software documentation are the available source types. No original theorem proof, third-party implementation, dataset or displayed figure was copied. Original implementation, controls and UI by Midya Rahmani, MIT.
