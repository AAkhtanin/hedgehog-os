# Related Work and Public Context

Radiolaria combines mechanisms with substantial antecedents. Its contribution is the explicit organization of continuing, source-bound activity in the implemented profiles, not a claim of priority over policy engines, workflow systems, provenance models or numerical optimization. The following finite comparison uses primary sources rechecked on 28 September 2026; it is not a performance benchmark or survey of every alternative.

## Complementary Mechanisms

OR-Tools CP-SAT works with integer constraints and explicit feasible/optimal/infeasible/unknown statuses. It can be a numerical participant. Radiolaria's separate question is how a selected result is tied to the current task, actually consumed and considered by local owners. That does not make a solver responsible for authorization or imply that solver-based applications lack policies. [CP-SAT documentation](https://developers.google.com/optimization/cp/cp_solver). [RW01](../PAPER_SOURCE_KEY.md#rw01).

Temporal organizes durable workflow execution and replay of recorded activity results. The overlap is continuing work and useful history. Radiolaria's profiles additionally foreground source applicability and independent local Root decisions. These are comparisons of emphasis and interfaces, not a claim that durable workflow applications cannot implement such checks. [Temporal tasks](https://docs.temporal.io/tasks). [RW02](../PAPER_SOURCE_KEY.md#rw02).

Open Policy Agent separates policy decisions from enforcement and accepts structured input. This is a plausible integration boundary, not a demonstrated Radiolaria deployment. A policy decision still needs correct inputs and an enforcement point. Current action and evidence lifecycles remain an application responsibility. [OPA documentation](https://www.openpolicyagent.org/docs). [RW03](../PAPER_SOURCE_KEY.md#rw03).

seL4 capDL describes kernel objects and capability distributions for initialization and reasoning about access. It concerns concrete OS capability boundaries. Radiolaria's local Root and Work relationships are not a substitute for those kernel proofs, and reviewed Python code is not thereby isolated. [capDL](https://docs.sel4.systems/projects/capdl/). [RW04](../PAPER_SOURCE_KEY.md#rw04).

W3C PROV defines interoperable descriptions of entities, activities and agents. This is relevant to derived results and provenance, but recording derivation does not make the source true or its current use permitted. Radiolaria's E/B/C and causal consumption records can be compared at that conceptual level without claiming PROV conformance or replacing the accepted schemas. [PROV overview, Working Group Note, 30 April 2013](https://www.w3.org/TR/2013/NOTE-prov-overview-20130430/). [RW05](../PAPER_SOURCE_KEY.md#rw05).

## Incident Motivation Is Not Local Evidence

An Australian government press-conference transcript published 24 September 2026 described a June incident involving an OpenAI agent and a Medicare statistics portal, and said forensic investigation was continuing. This corpus treats that official account as motivation for checking boundaries. The bounded provider-source search did not establish a matching primary provider account. It therefore omits speculative attack details, cause and final findings. No Radiolaria test reproduced that incident, and it proves no local security claim. [Australian Prime Minister transcript](https://www.pm.gov.au/media/press-conference-new-york). [RW06](../PAPER_SOURCE_KEY.md#rw06).

## Regulatory and Management Context

The EU AI Act is binding legislation whose duties depend on actors, use and classification. The European Commission policy page, rechecked on 28 September 2026, states general application from 2 August 2026 and distinguishes Annex III high-risk application on 2 December 2027 from Annex I application on 2 August 2028. Its simplification section says the Omnibus entered into force on 27 July 2026. The fresh EUR-Lex retrieval returned a JavaScript challenge, so this edition attributes the dates to the Commission summary rather than claiming a fresh reading of the consolidated legislation. This is a dated editorial summary, not legal advice or a classification of Radiolaria. An integrator must determine its role, intended purpose, applicable duties and current law. Local review, logs and traceability may support engineering obligations; their existence does not establish conformity. [Commission AI Act overview, Application timeline and simplification sections](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai). [RW07](../PAPER_SOURCE_KEY.md#rw07).

NIST AI RMF is voluntary risk-management guidance. It can organize governance and assessment, but the recorded finite cases do not constitute a NIST certification. ISO/IEC 42001:2023 is an organizational AI management-system standard. Only its public official abstract was consulted; the paid full text was not inspected. Nothing in Root, a signature or an outcome envelope establishes organizational certification. Deployment teams retain risk, privacy, human-oversight and operational responsibilities. [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework). [RW08](../PAPER_SOURCE_KEY.md#rw08); [ISO/IEC 42001](https://www.iso.org/standard/42001). [RW09](../PAPER_SOURCE_KEY.md#rw09).

The comparison leaves a constructive role for common organization: applications can combine these mechanisms while preserving purpose, current material, actual use and attributable decisions. It does not turn references, regulatory vocabulary or private praise into an independent benchmark or permission to publish certification marks.

## Comparison Boundaries

| Object | Shared concern | Radiolaria emphasis | Not compared |
| --- | --- | --- | --- |
| CP-SAT | Explicit constraints and results | Binding a checked result to actual current Work | Solver speed, optimality advantage |
| Temporal | Continuing work and retained outcomes | Source applicability and independent local owners | Reliability or feature superiority |
| OPA | Policy decisions and enforcement | Current packet, effect and evidence lifecycle | Enterprise policy coverage |
| seL4 capDL | Access boundaries | Application-level reviewed Work and decisions | Kernel isolation or formal-proof strength |
| W3C PROV | Derivation and participants | Actual consumption plus separate authority checks | Standards conformance |

These are interface-level comparisons based on the cited official descriptions, not tests of the other systems.

## Information Flow and Local Computation

Microsoft's May 20, 2026 FIDES description separates integrity and confidentiality labels, propagates them through derived content and checks policy before sensitive tools run. It is experimental: source labels are opt-in, default labels can be too trusting, propagation is conservative and approvals coarse. Its June 16 IFC account extends the discussion to agents, MCP and access-list-aware derivation. These mechanisms overlap with the need to distinguish useful untrusted material from permitted action. Radiolaria emphasizes continuing Work, actual consumption and independent current owners. This is an interface comparison, not a benchmark, compatibility claim or endorsement. [Microsoft FIDES](https://devblogs.microsoft.com/agent-framework/fides/); [Microsoft IFC](https://commandline.microsoft.com/information-flow-control-moving-toward-secure-autonomous-agents/). [RW10](../PAPER_SOURCE_KEY.md#rw10)

Apple's French Newsroom announcement of August 25, 2026 describes M6/M5 Ultra and on-device AI computation using unified memory. It is manufacturer context for possible local participants, not a Radiolaria measurement. A future composition could combine a person's local model, an organization's local computation and a remote service, each behind its own source and authority boundary. Location does not decide permission: a local model is no more a Root than a cloud model. No parameter-count benchmark, measured adapter or installed Apple-based Sentinel is claimed. Wedding's recorded remote QPU and Sentinel's CLOUD_LLM provenance remain unchanged. [Apple announcement](https://www.apple.com/fr/newsroom/2026/08/apple-introduces-m6-and-m5-ultra-for-a-big-leap-in-performance-and-ai-compute/). [RW11](../PAPER_SOURCE_KEY.md#rw11)
