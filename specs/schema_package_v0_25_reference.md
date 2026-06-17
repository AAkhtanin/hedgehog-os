# JSON Schema Package v0.25 Reference

This document preserves the earlier full JSON Schema package draft for comparison.

It is not the active runtime schema directory.

Active schemas live in `schemas/*.schema.json`.

When this reference conflicts with the active schemas, the active schemas should not be overwritten blindly. Use this file only for audit and targeted patching.

## Current Status Warning

This file is a historical/reference schema package, not the source of truth for the current MVP runtime.

The active schema source of truth is `schemas/*.schema.json`.

The current architecture is defined by:

- `specs/human_passport_v0_25.md`
- `specs/math_appendix_v0_3.md`
- `specs/machine_manifest_v0_25.json`
- `specs/invariants.md`
- `specs/demo_baseline_v0_25.md`

Known reference drift:

- Architect must return `PlanGraph`, not `ResultProposal`.
- Executors / DAG runner return `ResultProposal`-shaped outputs.
- `AttractorPacket.architect_instructions.must_return_result_proposals_only` is obsolete and retired; active Architect-facing contracts use `must_return_plan_graph_only`.
- Architect-facing instructions must not mix Executor / DAG ResultProposal behavior into the Architect contract.
- Current runtime includes explicit Orchestrator-stage / Route Assembly.
- Current runtime includes Fractal DAG Executor after Architect PlanGraph.
- DRS hits do not imply direct reuse.
- Credential Vault / sealed secret slots are future production requirement for secrets.
- Marennya and UP are systemic/internal needles with quarantine-first behavior.

Phase 2 Executor / DAG ResultProposal contract note:

- Architect returns PlanGraph only.
- Architect does not return ResultProposal, execute plan nodes, create
  FinalOutput, or write DRS.
- Executor receives validated PlanGraph node(s) and returns schema-valid
  ResultProposal artifacts.
- Executor does not create FinalOutput, write DRS directly, bypass
  Post V&V / GT / Root, or execute real external actions unless a later
  explicit production/action layer authorizes that capability.
- Executor / DAG returns ResultProposal or ResultProposal-shaped boundary
  artifacts.
- Active `hedgehog/executor.py` output is schema-valid ResultProposal.
- Proof-level Fractal DAG / child-cell boundary outputs may be
  ResultProposal-shaped until a later normalization/runtime validation layer.
- ResultProposal-shaped boundary artifacts are not FinalOutput, not accepted
  evidence, not action authorization, and not DRS writeback.
- Post V&V / GT / Root remain required before any final answer or writeback.

EvidenceItem.kind alignment note:

- Active `$defs.EvidenceItem.properties.kind.enum` is:
  `drs_record`, `needle`, `schema`, `policy`, `trace`,
  `simulated_executor`, `fractal_dag_executor`, `audit`, and `manual`.
- `fractal_dag_executor` is a local ResultProposal evidence classification for
  Fractal DAG boundary evidence. It is not truth, authority,
  AcceptedEvidence, action permission, DRS writeback, or FinalOutput.
- `audit` is local ResultProposal evidence support/provenance. It does not
  mean truth, authority, AcceptedEvidence, action permission, DRS write, or
  FinalOutput.
- `needle_runtime` remains `trace_refs.kind` only.
- Do not copy `needle_runtime`, `executor_node`, `fractal_dag_executor_node`,
  `EvidenceCandidate`, `ValidationPacket`,
  `RootFinalOutput`, `GTReport`, `AuditEvent`, `ChildBoundarySnapshot`,
  `SemanticDraft`, `NeedleCandidate`, or `ManifestCandidate` into the active
  EvidenceItem.kind enum from this reference note.

artifact_type Mapping / Runtime Artifact Vocabulary v0.1 reference note:

- artifact_type is metadata/classification only.
- `result_payload.artifact_type` is an active runtime payload label when
  present. It is not formally declared in ResultProposal schema in this
  checkpoint.
- VVReport `artifact_type` is optional free-string metadata.
- GTReport uses `candidate_type`, not top-level artifact_type.
- FinalOutput has no artifact_type by design.
- DRSRecord uses `layer`, `type`, and `status`, not artifact_type.
- source_artifact_type is a proof/audit/lifecycle source label, not active
  runtime payload artifact_type unless explicitly mapped later.
- EvidenceItem.kind remains separate from artifact_type.
- Map first, constrain later, enum last if still needed.
- This reference note creates no runtime registry, no schema enum, and no
  authority semantics.

Use this file only as a comparison artifact. Do not overwrite active schemas from this file without checking the current passport and active tests.

common.schema.json
intent.schema.json
time_envelope.schema.json
temporal_query.schema.json
world_state.schema.json
candidate_vector.schema.json
attractor_packet.schema.json
plan_graph.schema.json
result_proposal.schema.json
vv_report.schema.json
gt_report.schema.json
drs_record.schema.json
marenna_record.schema.json
up_record.schema.json
final_output.schema.json

⸻

1. common.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/common.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Hedgehog OS Common Definitions v0.25",
  "type": "object",
  "$defs": {
    "id": {
      "type": "string",
      "minLength": 2,
      "maxLength": 256,
      "pattern": "^[a-zA-Z0-9_:\\-./]+$"
    },
    "iso_datetime": {
      "type": "string",
      "format": "date-time"
    },
    "non_empty_string": {
      "type": "string",
      "minLength": 1
    },
    "score_0_1": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "signed_score": {
      "type": "number",
      "minimum": -1,
      "maximum": 1
    },
    "positive_number": {
      "type": "number",
      "minimum": 0
    },
    "positive_integer": {
      "type": "integer",
      "minimum": 0
    },
    "layer": {
      "type": "string",
      "enum": ["work", "thoughts", "up", "quarantine", "deadends"]
    },
    "status": {
      "type": "string",
      "enum": ["active", "archived", "quarantine", "promoted", "rejected", "expired"]
    },
    "mode": {
      "type": "string",
      "enum": ["default", "strict", "explore"]
    },
    "source_type": {
      "type": "string",
      "enum": ["needle", "local_drs", "external_drs_pointer", "fallback", "system_template"]
    },
    "branching_mode": {
      "type": "string",
      "enum": ["horizontal", "vertical", "hybrid", "forbidden"]
    },
    "decision": {
      "type": "string",
      "enum": ["accept", "revise", "reject", "rerun", "fallback", "no_update"]
    },
    "validation_stage": {
      "type": "string",
      "enum": ["static", "dedup", "rag_support", "self_consistency", "utility", "safety"]
    },
    "time_envelope_ref": {
      "$ref": "https://hedgehog-os.local/schemas/time_envelope.schema.json"
    },
    "temporal_query_ref": {
      "$ref": "https://hedgehog-os.local/schemas/temporal_query.schema.json"
    }
  }
}

⸻

2. time_envelope.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/time_envelope.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "TimeEnvelope v0.25",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "pt_created_at",
    "kt_asof",
    "ct_session_anchor",
    "ttl_seconds"
  ],
  "properties": {
    "pt_created_at": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/iso_datetime"
    },
    "kt_asof": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/iso_datetime"
    },
    "et_observed_at": {
      "anyOf": [
        {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/iso_datetime"
        },
        {
          "type": "null"
        }
      ]
    },
    "ct_session_anchor": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "ttl_seconds": {
      "type": "integer",
      "minimum": 1
    },
    "valid_from": {
      "anyOf": [
        {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/iso_datetime"
        },
        {
          "type": "null"
        }
      ]
    },
    "valid_to": {
      "anyOf": [
        {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/iso_datetime"
        },
        {
          "type": "null"
        }
      ]
    },
    "freshness_class": {
      "type": "string",
      "enum": ["static", "slow_changing", "normal", "fast_changing", "real_time"]
    }
  }
}

⸻

3. temporal_query.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/temporal_query.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "TemporalQuery v0.25",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "as_of",
    "freshness_bias"
  ],
  "properties": {
    "as_of": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/iso_datetime"
    },
    "time_range": {
      "type": "object",
      "additionalProperties": false,
      "required": ["from", "to"],
      "properties": {
        "from": {
          "anyOf": [
            {
              "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/iso_datetime"
            },
            {
              "type": "null"
            }
          ]
        },
        "to": {
          "anyOf": [
            {
              "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/iso_datetime"
            },
            {
              "type": "null"
            }
          ]
        }
      }
    },
    "freshness_bias": {
      "type": "string",
      "enum": ["prefer_recent", "prefer_stable", "historical_as_of", "ignore_time_for_static"]
    },
    "max_age_seconds": {
      "anyOf": [
        {
          "type": "integer",
          "minimum": 1
        },
        {
          "type": "null"
        }
      ]
    }
  }
}

⸻

4. intent.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/intent.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Intent v0.25",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "intent_id",
    "request_id",
    "raw_input",
    "canonical_goal",
    "domain",
    "created_at"
  ],
  "properties": {
    "intent_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "request_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "raw_input": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
    },
    "canonical_goal": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
    },
    "domain": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
    },
    "created_at": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/iso_datetime"
    },
    "user_constraints": {
      "type": "object",
      "additionalProperties": true
    },
    "system_constraints": {
      "type": "object",
      "additionalProperties": true
    },
    "source_of_hypothesis": {
      "type": "string",
      "enum": ["user", "system", "external", "consensus", "unknown"],
      "default": "user"
    }
  }
}

⸻

5. world_state.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/world_state.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "WorldState v0.25",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "world_state_id",
    "request_id",
    "intent_id",
    "time_context",
    "temporal_query",
    "user_context",
    "session_context",
    "local_drs_summary",
    "active_policy"
  ],
  "properties": {
    "world_state_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "request_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "intent_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "time_context": {
      "type": "object",
      "additionalProperties": false,
      "required": ["now_utc", "timezone", "freshness_required"],
      "properties": {
        "now_utc": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/iso_datetime"
        },
        "timezone": {
          "type": "string"
        },
        "freshness_required": {
          "type": "string",
          "enum": ["low", "medium", "high", "real_time"]
        }
      }
    },
    "temporal_query": {
      "$ref": "https://hedgehog-os.local/schemas/temporal_query.schema.json"
    },
    "user_context": {
      "type": "object",
      "additionalProperties": true,
      "required": ["user_id"],
      "properties": {
        "user_id": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
        },
        "preferences": {
          "type": "object",
          "additionalProperties": true
        },
        "constraints": {
          "type": "object",
          "additionalProperties": true
        }
      }
    },
    "session_context": {
      "type": "object",
      "additionalProperties": false,
      "required": ["session_id", "request_id"],
      "properties": {
        "session_id": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
        },
        "request_id": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
        }
      }
    },
    "local_drs_summary": {
      "type": "object",
      "additionalProperties": false,
      "required": ["matched_records", "dead_ends", "up_templates", "thoughts"],
      "properties": {
        "matched_records": {
          "type": "array",
          "items": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
          }
        },
        "dead_ends": {
          "type": "array",
          "items": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
          }
        },
        "up_templates": {
          "type": "array",
          "items": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
          }
        },
        "thoughts": {
          "type": "array",
          "items": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
          }
        }
      }
    },
    "active_policy": {
      "type": "object",
      "additionalProperties": false,
      "required": ["mode", "allow_external_drs", "allow_exploration"],
      "properties": {
        "mode": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/mode"
        },
        "allow_external_drs": {
          "type": "boolean"
        },
        "allow_exploration": {
          "type": "boolean"
        }
      }
    }
  }
}

⸻

6. candidate_vector.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/candidate_vector.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CandidateVector v0.25",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "vector_id",
    "source",
    "domain",
    "description",
    "features",
    "branching_hint",
    "capabilities_required"
  ],
  "properties": {
    "vector_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "source": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/source_type"
    },
    "source_ref": {
      "anyOf": [
        {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
        },
        {
          "type": "null"
        }
      ]
    },
    "domain": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
    },
    "description": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
    },
    "features": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "rel",
        "p_success",
        "utility",
        "cost",
        "risk",
        "time_penalty",
        "policy_conflict",
        "gt_prior",
        "novelty"
      ],
      "properties": {
        "rel": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "p_success": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "utility": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "cost": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "risk": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "time_penalty": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "policy_conflict": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "gt_prior": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "novelty": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        }
      }
    },
    "branching_hint": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/branching_mode"
    },
    "capabilities_required": {
      "type": "array",
      "items": {
        "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
      }
    },
    "hard_forbidden": {
      "type": "boolean",
      "default": false
    },
    "forbidden_reason": {
      "type": ["string", "null"]
    },
    "requires_architect_creativity": {
      "type": "boolean",
      "default": false
    },
    "history_confidence": {
      "type": "string",
      "enum": ["none", "low", "medium", "high"],
      "default": "medium"
    }
  }
}

⸻

7. attractor_packet.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/attractor_packet.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "AttractorPacket v0.25",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "packet_id",
    "request_id",
    "intent_id",
    "world_state_ref",
    "goal",
    "time_context",
    "hard_forbidden_regions",
    "candidate_vectors",
    "exploration_budget",
    "architect_instructions"
  ],
  "properties": {
    "packet_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "request_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "intent_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "world_state_ref": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "goal": {
      "type": "object",
      "additionalProperties": false,
      "required": ["goal_id", "desired_state"],
      "properties": {
        "goal_id": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
        },
        "desired_state": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
        }
      }
    },
    "time_context": {
      "type": "object",
      "additionalProperties": false,
      "required": ["as_of", "freshness_required"],
      "properties": {
        "as_of": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/iso_datetime"
        },
        "freshness_required": {
          "type": "string",
          "enum": ["low", "medium", "high", "real_time"]
        }
      }
    },
    "hard_forbidden_regions": {
      "type": "array",
      "items": {
        "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
      }
    },
    "candidate_vectors": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "vector_id",
          "final_viability",
          "branching_mode",
          "branch_budget"
        ],
        "properties": {
          "vector_id": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
          },
          "final_viability": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
          },
          "branching_mode": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/branching_mode"
          },
          "branch_budget": {
            "type": "object",
            "additionalProperties": false,
            "required": ["max_fractals", "max_depth", "parallelism"],
            "properties": {
              "max_fractals": {
                "type": "integer",
                "minimum": 0
              },
              "max_depth": {
                "type": "integer",
                "minimum": 0
              },
              "parallelism": {
                "type": "integer",
                "minimum": 0
              }
            }
          }
        }
      }
    },
    "exploration_budget": {
      "type": "object",
      "additionalProperties": false,
      "required": ["enabled", "epsilon", "max_experimental_vectors"],
      "properties": {
        "enabled": {
          "type": "boolean"
        },
        "epsilon": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "max_experimental_vectors": {
          "type": "integer",
          "minimum": 0
        }
      }
    },
    "architect_instructions": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "do_not_expand_forbidden_regions",
        "must_return_time_assumptions",
        "must_return_plan_graph_only"
      ],
      "properties": {
        "do_not_expand_forbidden_regions": {
          "type": "boolean",
          "const": true
        },
        "must_return_time_assumptions": {
          "type": "boolean",
          "const": true
        },
        "must_return_plan_graph_only": {
          "type": "boolean",
          "const": true
        }
      }
    }
  }
}

⸻

8. plan_graph.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/plan_graph.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PlanGraph v0.25",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "plan_id",
    "request_id",
    "source_packet_id",
    "time_assumptions",
    "nodes",
    "edges",
    "executor_assignments"
  ],
  "properties": {
    "plan_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "request_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "source_packet_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "time_assumptions": {
      "type": "object",
      "additionalProperties": false,
      "required": ["as_of", "freshness_required", "unknowns"],
      "properties": {
        "as_of": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/iso_datetime"
        },
        "freshness_required": {
          "type": "string",
          "enum": ["low", "medium", "high", "real_time"]
        },
        "unknowns": {
          "type": "array",
          "items": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
          }
        }
      }
    },
    "nodes": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["node_id", "vector_id", "kind", "description", "depends_on"],
        "properties": {
          "node_id": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
          },
          "vector_id": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
          },
          "kind": {
            "type": "string",
            "enum": ["tool_or_simulated_action", "reasoning_stub", "retrieval", "validation", "human_clarification"]
          },
          "description": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
          },
          "depends_on": {
            "type": "array",
            "items": {
              "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
            }
          }
        }
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["from", "to"],
        "properties": {
          "from": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
          },
          "to": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
          }
        }
      }
    },
    "executor_assignments": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["executor_id", "node_id"],
        "properties": {
          "executor_id": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
          },
          "node_id": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
          }
        }
      }
    }
  }
}

⸻

9. result_proposal.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/result_proposal.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ResultProposal v0.25",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "proposal_id",
    "request_id",
    "producer",
    "vector_id",
    "plan_id",
    "result_payload",
    "evidence",
    "cost",
    "risks",
    "time_envelope",
    "trace_refs"
  ],
  "properties": {
    "proposal_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "request_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "producer": {
      "type": "object",
      "additionalProperties": false,
      "required": ["executor_id", "needle_id", "model_id"],
      "properties": {
        "executor_id": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
        },
        "needle_id": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
        },
        "model_id": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
        }
      }
    },
    "vector_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "plan_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "result_payload": {
      "type": "object",
      "additionalProperties": true
    },
    "evidence": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": true,
        "required": ["type", "ref"],
        "properties": {
          "type": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
          },
          "ref": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
          }
        }
      }
    },
    "cost": {
      "type": "object",
      "additionalProperties": false,
      "required": ["tokens", "wall_ms", "tool_calls"],
      "properties": {
        "tokens": {
          "type": "integer",
          "minimum": 0
        },
        "wall_ms": {
          "type": "integer",
          "minimum": 0
        },
        "tool_calls": {
          "type": "integer",
          "minimum": 0
        }
      }
    },
    "risks": {
      "type": "array",
      "items": {
        "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
      }
    },
    "time_envelope": {
      "$ref": "https://hedgehog-os.local/schemas/time_envelope.schema.json"
    },
    "trace_refs": {
      "type": "array",
      "items": {
        "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
      }
    }
  },
  "not": {
    "required": ["final_output"]
  }
}

⸻

10. vv_report.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/vv_report.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "VVReport v0.25",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "vv_id",
    "request_id",
    "proposal_id",
    "status",
    "scores",
    "normalized_features"
  ],
  "properties": {
    "vv_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "request_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "proposal_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "status": {
      "type": "string",
      "enum": ["accept", "revise", "reject"]
    },
    "scores": {
      "type": "object",
      "additionalProperties": false,
      "required": ["schema", "evidence", "policy", "time", "safety"],
      "properties": {
        "schema": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "evidence": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "policy": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "time": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "safety": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        }
      }
    },
    "normalized_features": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "utility",
        "robustness",
        "compute_cost",
        "violations",
        "transfer",
        "novelty_guard"
      ],
      "properties": {
        "utility": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "robustness": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "compute_cost": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "violations": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "transfer": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "novelty_guard": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        }
      }
    },
    "issues": {
      "type": "array",
      "items": {
        "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
      }
    }
  }
}

⸻

11. gt_report.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/gt_report.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "GTReport v0.25",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "gt_report_id",
    "request_id",
    "game_mode",
    "winner",
    "mix",
    "ratings",
    "regret",
    "half_life_hours",
    "decision",
    "audit"
  ],
  "properties": {
    "gt_report_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "request_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "game_mode": {
      "type": "string",
      "enum": ["result_selection", "marenna_game", "up_game", "memory_evo"]
    },
    "winner": {
      "anyOf": [
        {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
        },
        {
          "type": "null"
        }
      ]
    },
    "mix": {
      "type": "object",
      "additionalProperties": {
        "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
      }
    },
    "ratings": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "additionalProperties": false,
        "required": ["elo"],
        "properties": {
          "elo": {
            "type": "number"
          },
          "delta": {
            "type": "number"
          },
          "stdev": {
            "type": "number",
            "minimum": 0
          }
        }
      }
    },
    "regret": {
      "type": "object",
      "additionalProperties": {
        "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
      }
    },
    "half_life_hours": {
      "type": "object",
      "additionalProperties": {
        "type": "number",
        "minimum": 0
      }
    },
    "decay_rate": {
      "type": "object",
      "additionalProperties": {
        "type": "number",
        "minimum": 0
      }
    },
    "dominance": {
      "type": "string",
      "enum": ["none", "weak", "strict"]
    },
    "decision": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/decision"
    },
    "audit": {
      "type": "object",
      "additionalProperties": true,
      "required": ["method"],
      "properties": {
        "method": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
        },
        "early_stop": {
          "type": ["string", "null"]
        }
      }
    }
  }
}

⸻

12. drs_record.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/drs_record.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DRSRecord v0.25",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "record_id",
    "layer",
    "type",
    "domain",
    "content",
    "time_envelope",
    "provenance",
    "status"
  ],
  "properties": {
    "record_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "layer": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/layer"
    },
    "type": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
    },
    "domain": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
    },
    "content": {
      "type": "object",
      "additionalProperties": true
    },
    "time_envelope": {
      "$ref": "https://hedgehog-os.local/schemas/time_envelope.schema.json"
    },
    "provenance": {
      "type": "object",
      "additionalProperties": false,
      "required": ["request_id"],
      "properties": {
        "request_id": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
        },
        "plan_id": {
          "type": ["string", "null"]
        },
        "trace_refs": {
          "type": "array",
          "items": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
          }
        }
      }
    },
    "gt": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "elo": {
          "type": "number"
        },
        "regret": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "half_life_hours": {
          "type": "number",
          "minimum": 0
        },
        "decay_rate": {
          "type": "number",
          "minimum": 0
        },
        "gt_report_ref": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
        }
      }
    },
    "validation": {
      "type": "object",
      "additionalProperties": true
    },
    "status": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/status"
    }
  }
}

⸻

13. marenna_record.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/marenna_record.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MarennyaRecord v0.25",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "record_id",
    "layer",
    "type",
    "domain",
    "content",
    "validation",
    "time_envelope"
  ],
  "properties": {
    "record_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "layer": {
      "type": "string",
      "enum": ["quarantine", "thoughts"]
    },
    "type": {
      "type": "string",
      "enum": [
        "marenna_reflection",
        "marenna_patch",
        "validator_patch",
        "dead_end_candidate",
        "heuristic_adjustment"
      ]
    },
    "domain": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
    },
    "content": {
      "type": "object",
      "additionalProperties": true
    },
    "input_refs": {
      "type": "array",
      "items": {
        "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
      }
    },
    "validation": {
      "type": "object",
      "additionalProperties": false,
      "required": ["status", "pipeline"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["quarantine", "promoted", "rejected"]
        },
        "pipeline": {
          "type": "array",
          "items": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/validation_stage"
          }
        },
        "passed": {
          "type": "boolean"
        }
      }
    },
    "time_envelope": {
      "$ref": "https://hedgehog-os.local/schemas/time_envelope.schema.json"
    }
  }
}

⸻

14. up_record.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/up_record.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "UPRecord v0.25",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "record_id",
    "layer",
    "type",
    "domain",
    "content",
    "metrics",
    "validation",
    "time_envelope"
  ],
  "properties": {
    "record_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "layer": {
      "type": "string",
      "enum": ["quarantine", "up"]
    },
    "type": {
      "type": "string",
      "enum": [
        "up_opportunity",
        "up_protocol_template",
        "up_link"
      ]
    },
    "domain": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
    },
    "content": {
      "type": "object",
      "additionalProperties": true
    },
    "input_refs": {
      "type": "array",
      "items": {
        "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
      }
    },
    "metrics": {
      "type": "object",
      "additionalProperties": false,
      "required": ["novelty", "expected_utility", "risk"],
      "properties": {
        "novelty": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "expected_utility": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "risk": {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/score_0_1"
        },
        "energy": {
          "type": "number"
        }
      }
    },
    "validation": {
      "type": "object",
      "additionalProperties": false,
      "required": ["status", "pipeline"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["quarantine", "promoted", "rejected"]
        },
        "pipeline": {
          "type": "array",
          "items": {
            "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/validation_stage"
          }
        },
        "passed": {
          "type": "boolean"
        }
      }
    },
    "time_envelope": {
      "$ref": "https://hedgehog-os.local/schemas/time_envelope.schema.json"
    }
  }
}

⸻

15. final_output.schema.json

{
  "$id": "https://hedgehog-os.local/schemas/final_output.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "FinalOutput v0.25",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "final_output_id",
    "request_id",
    "created_by",
    "status",
    "answer",
    "used_proposals",
    "gt_report_ref",
    "drs_writes",
    "time_envelope"
  ],
  "properties": {
    "final_output_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "request_id": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
    },
    "created_by": {
      "type": "string",
      "const": "root_orchestrator"
    },
    "status": {
      "type": "string",
      "enum": ["ok", "partial", "failed", "needs_user"]
    },
    "answer": {
      "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
    },
    "used_proposals": {
      "type": "array",
      "items": {
        "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
      }
    },
    "gt_report_ref": {
      "anyOf": [
        {
          "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
        },
        {
          "type": "null"
        }
      ]
    },
    "drs_writes": {
      "type": "array",
      "items": {
        "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/id"
      }
    },
    "time_envelope": {
      "$ref": "https://hedgehog-os.local/schemas/time_envelope.schema.json"
    },
    "notes": {
      "type": "array",
      "items": {
        "$ref": "https://hedgehog-os.local/schemas/common.schema.json#/$defs/non_empty_string"
      }
    }
  }
}

⸻

16. Что эти схемы уже жёстко фиксируют

Они уже машинно закрепляют:

* Executor не может вернуть final_output.
* FinalOutput может создать только root_orchestrator.
* DRSRecord всегда требует TimeEnvelope.
* WorldState всегда требует TemporalQuery.
* AttractorPacket всегда требует candidate vectors и forbidden regions.
* Architect обязан вернуть time_assumptions через PlanGraph.
* Marennya и UP не могут писать сразу в Work.
* UP/Marennya сначала идут через quarantine.
* GTReport содержит winner/mix/ratings/regret/half_life.
* CandidateVector имеет источник, features и branching hint.

⸻

17. Что ещё нужно будет добавить уже при коде

Это не в JSON Schema, а в runtime-тестах:

1. Проверка, что сумма mix в GTReport ≈ 1.0.
2. Проверка, что candidate vectors не появились из свободного LLM.
3. Проверка, что forbidden vector не дошёл до Architect.
4. Проверка, что UP/Marennya не мутируют Work.
5. Проверка, что все DRS retrieval вызваны с TemporalQuery.
6. Проверка, что ResultProposal не содержит user-facing answer.
7. Проверка, что second run использует DRS-записи first run.
