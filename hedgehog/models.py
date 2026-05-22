from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CandidateFeatures:
    rel: float
    p_success: float
    utility: float
    cost: float
    risk: float
    time_penalty: float
    policy_conflict: float
    gt_prior: float
    novelty: float

    def to_dict(self) -> dict:
        return {
            "rel": self.rel,
            "p_success": self.p_success,
            "utility": self.utility,
            "cost": self.cost,
            "risk": self.risk,
            "time_penalty": self.time_penalty,
            "policy_conflict": self.policy_conflict,
            "gt_prior": self.gt_prior,
            "novelty": self.novelty,
        }


@dataclass(frozen=True)
class CandidateVector:
    vector_id: str
    source: str
    domain: str
    branching_hint: str
    features: CandidateFeatures
    description: str | None = None
    capabilities_required: list[str] = field(default_factory=list)
    history_confidence: str | None = None
    requires_architect_creativity: bool = False
    hard_forbidden: bool = False
    forbidden_reason: str | None = None
    source_record_ref: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "CandidateVector":
        features = CandidateFeatures(**data["features"])
        return cls(
            vector_id=data["vector_id"],
            source=data["source"],
            domain=data["domain"],
            branching_hint=data["branching_hint"],
            features=features,
            description=data.get("description"),
            capabilities_required=list(data.get("capabilities_required", [])),
            history_confidence=data.get("history_confidence"),
            requires_architect_creativity=data.get(
                "requires_architect_creativity", False
            ),
            hard_forbidden=data.get("hard_forbidden", False),
            forbidden_reason=data.get("forbidden_reason"),
            source_record_ref=data.get("source_record_ref"),
        )

    def to_dict(self) -> dict:
        payload = {
            "vector_id": self.vector_id,
            "source": self.source,
            "domain": self.domain,
            "branching_hint": self.branching_hint,
            "features": self.features.to_dict(),
            "requires_architect_creativity": self.requires_architect_creativity,
            "hard_forbidden": self.hard_forbidden,
        }
        if self.description is not None:
            payload["description"] = self.description
        if self.capabilities_required:
            payload["capabilities_required"] = list(self.capabilities_required)
        if self.history_confidence is not None:
            payload["history_confidence"] = self.history_confidence
        if self.forbidden_reason is not None:
            payload["forbidden_reason"] = self.forbidden_reason
        if self.source_record_ref is not None:
            payload["source_record_ref"] = self.source_record_ref
        return payload
