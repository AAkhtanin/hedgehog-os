"""Finite source-bound advisory ranking, never a Root decision or permission."""
from hedgehog.outcome_calibration_v01 import round_half_even_rational_v01 as rhe
from hedgehog.gate4_reference_contracts_v01 import (
    Q, ReferenceValueV01, bind_context, checked, digest, require, validate_supplied,
)


def evaluate_reference_strategy_v01(input, *, independently_bound_context):
    data = checked("strategy_input", input)
    context = bind_context(data["context"], independently_bound_context)
    candidates, disagreements = data["candidates"], data["disagreements"]
    require(context["candidate_set_hash"] == digest(candidates), "candidate_set_binding")
    require(context["source_snapshot_hash"] == digest({"candidates":candidates, "disagreements":disagreements}), "snapshot_binding")
    roots = context["participants"]
    require([d["root_id"] for d in disagreements] == roots, "disagreement_participants")
    ds = {d["root_id"]:d for d in disagreements}
    for d in disagreements:
        require((d["validity"] == "CURRENT") == (d["value"] is not None), "disagreement_disposition")
    # Source and shape checks apply even to hard-excluded candidates.
    for c in candidates:
        require(c["source_hash"] == digest({k:v for k,v in c.items() if k != "source_hash"}), "candidate_source")
        require(c["participants"] == roots and set(c["required_roots"]) <= set(roots), "candidate_participants")
        require(c["policy_ref"] == context["policy_ref"] and c["time_envelope_ref"] == context["time_envelope_ref"], "candidate_context")
        for u in c["utilities"]:
            require(u["root_id"] in roots and u["candidate_id"] == c["id"], "utility_participant")
            require(len({t["id"] for t in u["terms"]}) == len(u["terms"]), "duplicate_term")
            require(not u["terms"] or sum(t["weight_fp"] for t in u["terms"]) == Q, "weight_sum")
            require(all(t["source_ref"] in c["feature_refs"] for t in u["terms"]), "feature_source")
    missing = {d["source_ref"] for d in context["dispositions"] if d["state"] != "KNOWN"}
    exclusions, feasible, ir, witnesses, traces, failed = [], [], [], [], [], []
    vectors = {}
    for c in candidates:
        false = [p["evidence_ref"] for p in c["hard"] if p["state"] == "FALSE"]
        if false:
            exclusions.append({"id":c["id"], "reasons":sorted({p["evidence_ref"] for p in c["hard"] if p["state"] != "TRUE"})})
            continue
        unknown = [p["evidence_ref"] for p in c["hard"] if p["state"] == "UNKNOWN"]
        if unknown:
            missing.update(unknown)
            continue
        feasible.append(c["id"])
        utilities = {u["root_id"]:u for u in c["utilities"]}
        vector = {}
        for root in roots:
            u, d = utilities.get(root), ds[root]
            if d["value"] is None:
                missing.add(d["source_ref"])
            if u is None:
                missing.add(c["source_ref"])
                continue
            if u["validity"] != "CURRENT" or u["uncertainty"] != "DISCLOSED" or not u["terms"]:
                missing.add(u["source_ref"])
                continue
            numerators = [t["weight_fp"] * t["feature_fp"] for t in u["terms"]]
            subtotal = rhe(sum(numerators), Q)
            value = subtotal - sum(u["penalties"].values())
            require(-4 * Q <= value <= Q, "utility_range")
            vector[root] = value
            gain = None if d["value"] is None else value - d["value"]
            traces.append({"candidate_id":c["id"], "root_id":root, "source_ref":u["source_ref"],
                "terms":[{"id":t["id"], "source_ref":t["source_ref"], "numerator":n,
                          "interpretation":t["interpretation"]} for t,n in zip(u["terms"],numerators)],
                "weighted":subtotal, "penalties":u["penalties"], "utility":value,
                "disagreement":d["value"], "gain":gain,
                "factor":max(gain,1) if gain is not None and gain >= 0 else None,
                "epsilon_used":gain == 0})
            if gain is not None and gain < 0:
                failed.append({"candidate_id":c["id"], "root_id":root, "utility":value, "disagreement":d["value"]})
        if len(vector) == len(roots) and all(ds[r]["value"] is not None for r in roots):
            vectors[c["id"]] = vector
            if all(vector[r] >= ds[r]["value"] for r in roots):
                ir.append(c["id"])
    pareto = []
    for b in ir:
        dominators = [a for a in ir if all(vectors[a][r] >= vectors[b][r] for r in roots)
                      and any(vectors[a][r] > vectors[b][r] for r in roots)]
        if dominators:
            a = min(dominators)
            witnesses.append({"id":b, "dominator":a,
                "differences":[{"root_id":r, "delta":vectors[a][r]-vectors[b][r]} for r in roots]})
        else:
            pareto.append(b)
    scores = {}
    for s in ir:
        product = 1
        for r in roots:
            product *= max(vectors[s][r] - ds[r]["value"], 1)
        require(len(str(product)) <= 80, "product_limit")
        scores[s] = product
    ranking = sorted(pareto, key=lambda s:(-scores[s],s))
    status = "RECOMMENDATION"
    if missing: status = "NEEDS_MORE_EVIDENCE"
    elif not feasible: status = "NO_DEAL_NO_FEASIBLE"
    elif not ir: status = "NO_DEAL_BELOW_DISAGREEMENT"
    elif all(vectors[s][r] == ds[r]["value"] for s in ir for r in roots): status = "NO_DEAL_ALL_ZERO_GAIN"
    selected = ranking[0] if status == "RECOMMENDATION" else None
    return ReferenceValueV01("strategy_report", {
        "context":context, "input_id":ReferenceValueV01("strategy_input",data).identity,
        "status":status, "recommendation":selected, "feasible":feasible, "ir":ir, "pareto":pareto,
        "exclusions":exclusions, "missing_refs":sorted(missing), "utilities":traces,
        "failed_comparisons":failed, "witnesses":witnesses,
        "scores":[{"id":s,"product":str(scores[s])} for s in ir], "ranking":ranking,
        "tie_rule":"DESCENDING_PRODUCT_THEN_STABLE_ID",
        "weak_ir":selected is not None and any(vectors[selected][r] == ds[r]["value"] for r in roots),
        "root_review_required":True, "creates_permission":False, "requests_effect":False,
        "deferred":{k:{"status":"NOT_IMPLEMENTED", "disposition":"DEFERRED_AFTER_GATE6_PUBLICATION"}
                    for k in ("regret","stability","robustness","CVaR","sensitivity")}})


def validate_reference_strategy_report_v01(supplied, *, inputs, source_basis):
    expected = evaluate_reference_strategy_v01(inputs, independently_bound_context=source_basis)
    return validate_supplied("strategy_report", supplied, expected)
