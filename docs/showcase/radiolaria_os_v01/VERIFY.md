# Verify Saved Evidence Before Running Anything

## Credential-free first encounter: INSPECT_SAVED

Open [the episode](episode/FOOTBALL.md), [source inventory](references/episode_sources.json) and [FOCUS Reader](reader/M2_FOCUS.md). These are inert local files. No account, network, source installation or runtime is needed. This return contains new data-only consistency checks, not a rerun of the original exam.

On accepted A, the existing public verifier provides a separate inspection route:

```sh
python3 -B demo/verify_gate6_reference_v01.py --output /tmp/g6-inspection
```

Requirements: ordinary accepted checkout, standard-library Python, unused writable output path. Writes an inspection result outside the checkout; no provider credentials or network. Expected successful label: `PASS_FINITE_MIXED_BASIS_REFERENCE_PACKAGE`. Without a separately accepted `--manifest-sha256` trust input, internal consistency is not independent admission. Source: [accepted package README](https://github.com/AAkhtanin/hedgehog-os/blob/2e965ecb18e545e428380eb8e9aa5a7037a388be/docs/gate6_reference_v01/README.md). Not executed here.

## VERIFY_SAVED

The supplied verification mode is distinct from generating fresh domain work:

```sh
python3 -B demo/verify_gate6_reference_v01.py --mode supplied --output /tmp/g6-supplied
```

Requires the declared installed dependencies and the accepted **detached bounded operator with a 600-second ceiling**, as stated in the package README. Do not launch it as an unbounded terminal foreground job. It writes a new result directory, starts 13 pure workers and two historical G5 children, and consumes saved data. The accepted installed proof took **126.26431604102254 seconds**; that is retained evidence, not a timing promise or fresh measurement here. Installed canonical result: 4762744 bytes, SHA-256 `55d17fd2c22f2860b4250ae7d795395b60407ae952b9d66d82b334c110758c01`.

## RUN_DETERMINISTIC_REFERENCE

To generate a fresh deterministic profile, use the documented composition entrypoint, with separately prepared current inputs, not a invented convenience command:

```sh
"$PYTHON" -B -m demo.run_gate6_reference_v01 execute \
  --profile G51 --inputs "$INPUTS" --output "$FRESH_OUTPUT"
```

`INPUTS` is JSON keyed by profile; G51 needs an absolute `scenario_dir`. This is actual native work, not a free inspection. It requires dependencies and bounded local resources; writes receipts/artifacts outside checkout; no LLM is implicit. Football additionally requires its reviewed image, Docker endpoint and operator configuration. The public [execution document](https://github.com/AAkhtanin/hedgehog-os/blob/2e965ecb18e545e428380eb8e9aa5a7037a388be/docs/gate6_reference_execution_v01.md) specifies those prerequisites. All commands are documentation only in this B3 review.

## RUN_LIVE_OPTIONAL

Live evidence requires separately authorized provider/network credentials, a reviewed model and explicit budget; it must not silently fall back to controlled output. The accepted [model budget note](https://github.com/AAkhtanin/hedgehog-os/blob/2e965ecb18e545e428380eb8e9aa5a7037a388be/docs/gate6_reference_execution_v01.md) and [technical handoff](https://github.com/AAkhtanin/hedgehog-os/blob/2e965ecb18e545e428380eb8e9aa5a7037a388be/docs/gate6_reference_v01/PUBLICATION_HANDOFF.md) preserve the bounded Gemini contrast and honest source origins. This review provides **no ready-to-run live generation command**: absent current credentials, manifest paths and owner budget would make such a command misleading. Preparation and saved replay are not live execution. No model or countTokens call is made here.

## Trust and reproducibility

Use the accepted A commit and detached technical manifest SHA-256 `9b5f6b856522c97dc1722f0edb4461d0e9cec2c0ac483d9cecf85ae1ab39efd4` as independently supplied provenance, not merely a digest asserted by the packet. The outer return manifest proves packaging consistency. The independent examiner remains a separate historical source; the new finite checks compare parent-held inputs, observed wire bytes, Work invocation values and source readback. They do not import the candidate or revalidate signatures today.
