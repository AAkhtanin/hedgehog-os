# Sources and scope

Retrieved 24 September 2026. Primary literature and official documentation. No third-party figure or large table is reproduced.

## Project evidence

Accepted engineering: [fbb136f4](https://github.com/AAkhtanin/hedgehog-os/tree/fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a). Repository access is required.

The source identities and deduplicated storage paths are indexed in [SOURCE_MAP.json](evidence/SOURCE_MAP.json). The unchanged W5 portable package and supplementary W3/W2 sources have separate validation scopes. No source permission is reconstructed by reading this publication.

## External references

### L1. A Set Partitioning Problem

COIN-OR PuLP, Stuart Mitchell (example author). 2009. 

[Primary source](https://coin-or.github.io/pulp/CaseStudies/a_set_partitioning_problem.html)

Relevant sections: Opening explanation; wedding.py full example.

- Tables are subsets in a set-partitioning formulation, and each guest belongs to exactly one selected subset.

- The example explicitly enumerates possible subsets; the documentation notes scaling cost and mentions column generation.

- The supplied example contains 17 guests, at most five tables and at most four guests per table.

Scope: The prose says maximize happiness while the displayed script constructs LpMinimize. Describe the formulation without claiming the displayed objective direction is consistent.

Scope: This case study is not an evaluation of natural-language intent, authority or durable revision history.

Not supported by this source: PuLP cannot support changed inputs.; Radiolaria is faster than PuLP.



### L2. Finding an optimal seating chart

Meghan L. Bellows, J. D. Luc Peterson. 2012. 

[Primary source](https://improbable.com/news/2012/Optimal-seating-chart.pdf)

Relevant sections: Page 1: title, authors, affiliations and online publication date; Pages 1–2: Model; Page 5: Full Problem.

- The authors' affiliations were Princeton University units.

- The mathematical model uses mixed-integer linear optimization of prepared guest relationships.

- The full problem has 107 guests and 11 tables of capacity 10. The authors report their best-found seating after 36 hours, followed by human rearrangements.

Not supported by this source: A Princeton University standard.; A proven global optimum for the 107-person case.; A matched performance baseline for the 12-guest Radiolaria profile.



### L3. wedding_optimal_chart_sat.py

Google OR-Tools contributors. Undated documentation. 

[Primary source](https://github.com/google/or-tools/blob/100f66e6242ab8bf8d32feb8f3bf086db66ae2b5/examples/python/wedding_optimal_chart_sat.py)

Relevant sections: build_data; solve_with_discrete_model; WeddingChartPrinter.

- Official example imports ortools.sat.python.cp_model and builds a CP-SAT model.

- It adapts the Bellows/Peterson seating example, using a prepared connection matrix, table capacities and an objective.

- The provided data describe 17 named guests; this is a solver example, not an evaluated activity history platform.

Not supported by this source: Changing a wish necessarily requires rewriting OR-Tools code.; OR-Tools destroys previous history.; Google is defeated by this demonstration.



### L4. Entangled happily ever after: Wedding reception seating mapped to classical and quantum optimizers

Karie A. Nicholas, Vikram Khipple Mulligan. 2026. arXiv:2604.10497v2

[Primary source](https://arxiv.org/html/2604.10497v2)

DOI: 10.48550/arXiv.2604.10497

Relevant sections: II-A: Seating Optimization Masala Plugins; II-B: Encoding as a CFN; II-C5: 37-person wedding; III: Results; IV-A/B: plugins and limitations.

- Maps seating to cost function networks through Masala plugins and compares classical Monte Carlo, a hill-flattening variant and D-Wave Advantage 2 quantum annealing mappings.

- Includes a 37-person wedding case.

- Explicitly diagnoses invalid overlapping guest assignments; classical solutions were used for the authors' wedding.

- The plugin architecture supports interchangeable representations and optimizers.

Version: The unversioned abstract now resolves to v3 dated 2026-07-17. This catalogue deliberately evaluates the directive's v2 of 2026-04-22 and makes no claim to summarize v3 changes.

Not supported by this source: Researchers accepted invalid seating without checking it.; Masala is only a fixed linear chain.; The paper is Radiolaria's 12-person benchmark or D-Wave control run.; Its solver results establish Radiolaria superiority.



### L5. Masala Core library

Flatiron Institute, Vikram K. Mulligan (project initiator). Undated documentation. 

[Primary source](https://github.com/flatironinstitute/masala_public/blob/f45dfef9a3a7723663af1fee944fe90ef1c9c232/README.md)

Relevant sections: Description; Authors; Using Masala in other software.

- The core contains minimal infrastructure; most functionality lives in plugin libraries.

- External software can load plugins at runtime, including plugins not known at compile time.

Not supported by this source: Masala cannot replace numerical solvers or representations.; Radiolaria alone separates a core from extensible solver plugins.



### T1. From What Countries Can I Access D-Wave's Leap Quantum Cloud Service?

D-Wave Quantum Inc., Fiona H (displayed byline). 2020. 

[Primary source](https://support.dwavesys.com/hc/en-us/articles/360051869733-From-What-Countries-Can-I-Access-D-Wave-s-Leap-Quantum-Cloud-Service)

Relevant sections: Supported country lists and preceding contact route.

- Albania is absent from the published commercial/trial supported-country lists.

- The page directs people outside listed regions to contact D-Wave sales.

Not supported by this source: The page records a personal denial to the Radiolaria author.; Access is absolutely impossible by any route.; D-Wave execution occurred in this project.



### T2. Create and submit an example OpenQASM 3.0 quantum task

Amazon Web Services. Undated documentation. 

[Primary source](https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm-create-submit-task.html)

Relevant sections: Use the Python SDK; Use Boto3; Use the AWS CLI.

- Braket accepts OpenQASM 3.0 tasks through its Python SDK, Boto3 and AWS CLI.

- The documented Rigetti example currently names Ankaa-3.

Not supported by this source: This generic example verifies Radiolaria's actual device, task identity, shots or outcome.



### T3. Tracking quantum tasks from the Amazon Braket SDK

Amazon Web Services. Undated documentation. 

[Primary source](https://docs.aws.amazon.com/braket/latest/developerguide/braket-monitor-tasks-sdk.html)

Relevant sections: Retrieve a result; Retrieve a quantum task or result.

- Task submission is asynchronous and produces a unique task identity.

- A task object can be reconstructed from its ARN to retrieve an existing result after the original notebook or kernel closes.

Not supported by this source: This documentation establishes the project's no-resubmission history.; General distributed exactly-once execution.; Restoring an external task also restores project authority or currentness.



### T4. dimod local feasibility checking and sample construction

D-Wave. Undated documentation. Ocean SDK 9.5.0; dimod 0.12.22

[Primary source](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/generated/dimod.ConstrainedQuadraticModel.check_feasible.html)

Relevant sections: check_feasible return and tolerance definition; from_samples_cqm description.

- check_feasible evaluates whether a sample satisfies CQM constraints within specified tolerances.

- from_samples_cqm constructs a sample set from raw samples and a CQM, computing energies and feasibility.

Not supported by this source: Local feasibility checking was invented by Radiolaria.; D-Wave supplies only energies and no local constraint checking.; Assignment rejection measures or corrects a physical noise channel.



### M1. OSDI '26 Call for Artifacts

USENIX. 2026. 

[Primary source](https://www.usenix.org/conference/osdi26/call-for-artifacts)

Relevant sections: Process; Submitting an Artifact > Packaging Artifacts.

- Only Artifacts Available is evaluated.

- Availability does not establish functionality or correctness.

- README guidance includes Getting Started for a short basic check and Detailed Instructions for full replication.

- This call explicitly accepts GitHub and GitLab hosting.

Not supported by this source: Radiolaria has received an OSDI artifact badge.; OSDI '26 functionally validated the project.; OSDI '26 bans GitHub hosting.



### M2. USENIX Security '26 Call for Artifacts

USENIX. 2026. 

[Primary source](https://www.usenix.org/conference/usenixsecurity26/call-for-artifacts)

Relevant sections: Summary; Artifact Evaluation Information > Process.

- The call distinguishes availability, optional functionality assessment and optional result reproduction.

- Permanent archival access is required; development repositories such as GitHub are not accepted for permanent artifact availability. Zenodo is recommended.

Not supported by this source: A GitHub release alone satisfies this archival criterion.; Radiolaria has submitted or received any conference approval.; These hosting rules are identical to OSDI '26.



### M3. Assurance Cases and Confidence

Charles Weinstock. 2013. 

[Primary source](https://www.sei.cmu.edu/blog/assurance-cases-and-confidence/)

Relevant sections: Making a Sound Evaluation; Dependability-case formulation and environmental assumptions.

- An assurance case connects a claim to supporting evidence through an explicit argument.

- Evidence must be explained for relevance and sufficiency; environmental assumptions are also discussed.

Not supported by this source: Using a claim-evidence table certifies safety or correctness.



### M4. Measure

National Institute of Standards and Technology. Undated documentation. 

[Primary source](https://airc.nist.gov/airmf-resources/playbook/measure/)

Relevant sections: MEASURE 1.1; MEASURE 2.1; MEASURE 2.5.

- Document characteristics that cannot or will not be measured.

- Document test sets, metrics, tools and measurement details.

- Document assumptions, operating conditions, generalization limits, validity and variance.

Not supported by this source: This project is NIST certified or proven trustworthy because it uses the reporting practice.



### M5. Assertion-Evidence Approach: Rethinking Scientific and Technical Presentations

Assertion-Evidence Approach. Undated documentation. 

[Primary source](https://www.assertion-evidence.com/)

Relevant sections: One solution in technical talks is to adopt the assertion-evidence approach.

- Organize the presentation around succinct assertions supported by visual evidence.

Scope: The exact homepage does not explicitly prescribe a complete sentence; complete-sentence slide headings remain the user's editorial requirement, consistent with the approach.


