# Mathematical Notation and Exact Forms

The following notation explains the recorded finite mechanisms. It introduces no new theorem, execution result or probability of safety. Exact implementation forms remain next to the numerical examples in chapters 05 and 08.

<a id="eq-rating"></a>
## M1. Fixed-Point Rating

R′ = clamp(R + RHE(α(O − E)/Q), 0, Q)

Q = 10⁹ and α = 125,000,000. R and E are integers in [0,Q]; O is 0 or Q. RHE rounds a signed rational to the nearest integer with ties to even. E is a prospective expectation, not the preceding rating. Only a current eligible comparable occurrence enters the bounded fold. Source: [E02](PAPER_SOURCE_KEY.md#e02).

<a id="eq-prior"></a>
## M2. Signed Advisory Prior

P′ = clamp(P + RHE(β((2O − Q) − P)/Q), −Q, Q)

β = 62,500,000. P is a dimensionless fixed-point integer in [−Q,Q]. One admitted negative occurrence starting from zero gives −62,500,000, labelled SPARSE. Source: [E05](PAPER_SOURCE_KEY.md#e05).

<a id="eq-pressure"></a>
## M3. Pressure and Weight

zᵢ = RHE((4rᵢ + 2lᵢ − 2uᵢ − cᵢ + pᵢ)/8)

wᵢ = RHE(10¹² exp((zᵢ − max(z))/250,000,000))

The first four features are in [0,Q], the signed prior in [−Q,Q]. The weight is an integer apportionment weight. Hard exclusion and unresolved required evidence precede allocation. Seven allocatable units change 4/3 to 3/4 inside a dispatch budget of nine, including one spent and one reserved unit. This changes expenditure, not total budget or measured speed. Source: [E05](PAPER_SOURCE_KEY.md#e05).

<a id="eq-decay"></a>
## M4. Decay After Time Admission

T = RHE(R × 2^(−a/h))

Age a and half-life h are integer seconds under the profile's time rules. Exact half-life multiples use rational division; the implementation returns zero at 64 half-lives. Usable trust gives pressure Q−T; otherwise maximum pressure recommends review. The recommendation threshold T<600,000,000 never suppresses mandatory policy. Source: [E02](PAPER_SOURCE_KEY.md#e02).

<a id="eq-wedding"></a>
## M5. Wedding Hard and Soft Costs

KEEP(x) = Σ_(g,h∈F) Σ_t (x[g,t] − x[h,t])²

MIX(x) = Σ_(g,h∈F) Σ_t x[g,t]x[h,t]

Q(x) = P H(x) + selected soft cost(x)

The 36 binary indicators assign twelve guests to three tables. H is a nonnegative integer hard penalty; H=0 means the original conditions hold. KEEP counts each separated familiar pair twice, MIX each co-seated pair once. P=25 and P=13 exceed their respective feasible soft bounds. The later ten-qubit pair representation contains up-to-four-local terms and is not a ten-variable QUBO. Source: [W-C3](PAPER_SOURCE_KEY.md#w-c3), [W-C5](PAPER_SOURCE_KEY.md#w-c5).

<a id="eq-measurement"></a>
## M6. Measurement Column Order

index = Σ_j z[j] 2^q[j]

q is measuredQubits and z is the same row's measurement vector. KEEP measurements[63] is zero-based and gives 1+4+512=517. Pair codes 0,1,2 are valid table indices; 3 is unseated and is not repaired. The original-condition checker and native consumer remain separate from save permission. Source: [W-Q2](PAPER_SOURCE_KEY.md#w-q2).

The same symbols can have different profile-local meanings: rating scale Q and Wedding objective Q(x) are not one runtime field. Integer counts, seconds, dimensionless fixed-point values and physical resource descriptions are never interchanged.
