"""Pure five-feature pressure and lower-first capped dispatch-unit apportionment."""
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction

from hedgehog.outcome_calibration_v01 import round_half_even_rational_v01 as rhe
from hedgehog.gate4_reference_contracts_v01 import (
    W, TAU, G4_REFERENCE_NUMERIC_V01, ReferenceValueV01, bind_context, checked,
    digest, require, validate_supplied,
)


def evaluate_reference_pressure_v01(features, *, profile):
    require(type(profile) is str and profile == G4_REFERENCE_NUMERIC_V01, "numeric_profile")
    data = checked("pressure_input", features)
    ctx = bind_context(data["context"], data["context"])
    require(ctx["source_snapshot_hash"] == digest(data["branches"]), "pressure_snapshot")
    require(ctx["candidate_set_hash"] == digest([b["id"] for b in data["branches"]]), "pressure_candidates")
    missing = {d["source_ref"] for d in ctx["dispositions"] if d["state"] != "KNOWN"}
    survivors, excluded = [], []
    for b in data["branches"]:
        require(b["lower"] <= b["upper"], "quota_order")
        require(b["catalogue_revision"] == ctx["catalogue_revision"], "catalogue_binding")
        prior = b["prior"]
        require(prior["disposition"] not in ("TAMPERED", "UNVERIFIED"), "unverified_prior")
        require(prior["disposition"] == "USABLE" or prior["value"] == 0, "cold_prior_nonzero")
        reasons = [p["evidence_ref"] for p in b["hard"] if p["state"] == "FALSE"]
        if b["eligible"] == "FALSE" or b["available"] == "FALSE": reasons.append(b["material_ref"])
        if reasons:
            excluded.append({"id":b["id"],"reasons":sorted(set(reasons))})
            continue
        unknown = [p["evidence_ref"] for p in b["hard"] if p["state"] == "UNKNOWN"]
        if b["eligible"] == "UNKNOWN" or b["available"] == "UNKNOWN": unknown.append(b["material_ref"])
        if unknown:
            missing.update(unknown)
            continue
        contributions = [{"name":k, "numerator":n*b[k]["value"], "source_ref":b[k]["source_ref"],
                          "normalization":b[k]["normalization"], "interpretation":b[k]["interpretation"]}
                         for k,n in (("relevance",4),("lineage",2),("uncertainty",-2),("cost",-1),("prior",1))]
        numerator = sum(c["numerator"] for c in contributions)
        survivors.append({"id":b["id"],"lower":b["lower"],"upper":b["upper"],
            "z_fp":rhe(numerator,8),"contributions":contributions,"numerator":numerator,"denominator":8})
    return ReferenceValueV01("pressure_report", {"context":ctx, "input_id":ReferenceValueV01("pressure_input",data).identity,
        "inputs":data, "status":"NEEDS_MORE_EVIDENCE" if missing else "READY",
        "missing_refs":sorted(missing), "exclusions":excluded, "survivors":survivors,"authority":"NON_AUTHORITY"})


def _weights(z):
    if not z:
        return {}
    # Explicit parameters, including traps/flags/exponent range, isolate callers.
    context = Context(prec=80, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999,
                      capitals=1, clamp=0, flags=[], traps=[])
    with localcontext(context):
        maximum = max(z.values())
        values = {k:int((Decimal(W) * (Decimal(v-maximum)/Decimal(TAU)).exp()).to_integral_value(rounding=ROUND_HALF_EVEN))
                  for k,v in z.items()}
    require(all(0 < v <= W for v in values.values()), "weight_range")
    return values


def _rational(value):
    return {"numerator":value.numerator, "denominator":value.denominator}


def _apportion(available, lower, upper, weights):
    """Private arithmetic only. Public entry first binds pressure and budget."""
    ids = sorted(lower)
    require(type(available) is int and 0 <= available <= 4096, "available_range")
    require(set(lower) == set(upper) == set(weights), "quota_keys")
    require(all(type(lower[k]) is int and type(upper[k]) is int and 0 <= lower[k] <= upper[k] <= 4096
                and type(weights[k]) is int and 0 < weights[k] <= W for k in ids), "quota_range")
    require(sum(lower.values()) <= available, "infeasible_minima")
    target = min(available, sum(upper.values()))
    remaining = target - sum(lower.values())
    caps = {k:upper[k]-lower[k] for k in ids}
    active = [k for k in ids if caps[k]]
    extras = {k:Fraction(0) for k in ids}
    rounds = []
    while remaining > 0 and active:
        total_weight = sum(weights[k] for k in active)
        tentative = {k:Fraction(remaining*weights[k],total_weight) for k in active}
        saturated = [k for k in active if tentative[k] >= caps[k]]
        rounds.append({"remaining":remaining,"active":list(active),"saturated":saturated,
            "tentative":[{"id":k,"value":_rational(tentative[k])} for k in active]})
        if not saturated:
            extras.update(tentative)
            break
        for k in saturated:
            extras[k] = Fraction(caps[k])
            remaining -= caps[k]
        active = [k for k in active if k not in saturated]
    floors = {k:extras[k].numerator//extras[k].denominator for k in ids}
    remainder = {k:extras[k]-floors[k] for k in ids}
    allocation = {k:lower[k]+floors[k] for k in ids}
    order = sorted((k for k in ids if allocation[k] < upper[k]),key=lambda k:(-remainder[k],k))
    awards = order[:target-sum(allocation.values())]
    for k in awards: allocation[k] += 1
    require(sum(allocation.values()) == target and all(lower[k] <= allocation[k] <= upper[k] for k in ids), "conservation")
    return {"target":target,"unallocated":available-target,"extras":extras,"floors":floors,
            "remainders":remainder,"allocations":allocation,"rounds":rounds,"order":order,"awards":awards}


def allocate_reference_work_budget_v01(pressure, *, current_budget_context):
    budget = checked("budget", current_budget_context)
    ctx = bind_context(budget["context"], budget["pressure_inputs"]["context"])
    require(budget["original_policy_ref"] == ctx["policy_ref"], "original_policy_ref")
    original = {"total":budget["total"],"policy_ref":budget["original_policy_ref"],
                "owner_root_id":ctx["owner_root_id"],"task_id":ctx["task_id"]}
    require(budget["original_policy_hash"] == digest(original) == ctx["policy_hash"], "original_policy_hash")
    require(budget["spending_snapshot_hash"] == digest({"spent":budget["spent"],"host_revision":budget["host_revision"],
        "owner_root_id":ctx["owner_root_id"],"task_id":ctx["task_id"],"transaction_id":ctx["transaction_id"]}), "spending_binding")
    require(budget["spent"] <= budget["total"], "spent_exceeds_original")
    branches = {b["id"]:b for b in budget["pressure_inputs"]["branches"]}
    for m in budget["mandatory"]:
        if "kind" in m:
            require(ctx["origin"] == "NATIVE_SOURCE_BOUND_G42_V01", "mandatory_native_origin")
            require(m["catalogue_revision"] == ctx["catalogue_revision"], "mandatory_catalogue")
        else:
            require(m["branch_ref"] in branches, "mandatory_branch")
            require(m["catalogue_revision"] == ctx["catalogue_revision"] and m["material_ref"] == branches[m["branch_ref"]]["material_ref"], "mandatory_material")
    expected = evaluate_reference_pressure_v01(budget["pressure_inputs"],profile=G4_REFERENCE_NUMERIC_V01)
    p = validate_supplied("pressure_report",pressure,expected).plain()
    mandatory = sum(m["count"] for m in budget["mandatory"])
    available = budget["total"]-budget["spent"]-mandatory
    rows = p["survivors"]
    status = ("BUDGET_INSUFFICIENT" if available < 0 else
              "NEEDS_MORE_EVIDENCE" if p["status"] != "READY" else
              "INFEASIBLE_MINIMA" if sum(r["lower"] for r in rows) > available else "ALLOCATED")
    report = {"context":ctx,"input_id":p["input_id"],"budget_id":ReferenceValueV01("budget",budget).identity,
        "budget":budget,"pressure_id":expected.identity,"status":status,"mandatory_units":mandatory,
        "available":available,"target":0,"unallocated":available if available >= 0 else None,
        "exclusions":p["exclusions"],"missing_refs":p["missing_refs"],"rows":[],"rounds":[],
        "remainder_order":[],"remainder_awards":[],"unit":"ONE_NATIVE_WORK_DISPATCH_UNIT","authority":"NON_AUTHORITY"}
    if status == "ALLOCATED":
        weights = _weights({r["id"]:r["z_fp"] for r in rows})
        result = _apportion(available, {r["id"]:r["lower"] for r in rows}, {r["id"]:r["upper"] for r in rows}, weights)
        report.update(target=result["target"],unallocated=result["unallocated"],rounds=result["rounds"],
                      remainder_order=result["order"],remainder_awards=result["awards"])
        report["rows"] = [{"id":r["id"],"lower":r["lower"],"upper":r["upper"],"z_fp":r["z_fp"],
            "weight":weights[r["id"]],"extra":_rational(result["extras"][r["id"]]),"floor":result["floors"][r["id"]],
            "remainder":_rational(result["remainders"][r["id"]]),"allocation":result["allocations"][r["id"]]} for r in rows]
        require(budget["spent"]+mandatory+sum(r["allocation"] for r in report["rows"]) <= budget["total"], "original_cap")
    return ReferenceValueV01("allocation_report",report)


def validate_reference_allocation_v01(supplied, *, inputs, current_budget_context):
    budget = checked("budget",current_budget_context)
    require(checked("pressure_input",inputs) == budget["pressure_inputs"], "independent_pressure_input")
    pressure = evaluate_reference_pressure_v01(inputs,profile=G4_REFERENCE_NUMERIC_V01)
    expected = allocate_reference_work_budget_v01(pressure,current_budget_context=budget)
    return validate_supplied("allocation_report",supplied,expected)
