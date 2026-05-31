# How Agent QA Lab Works

Agent QA Lab is a deterministic demo of an agent reliability workflow. It starts with a deliberately flawed refund-support agent, runs it against a stable stress-test suite, traces each agent step in W&B Weave, scores the output, and compares improved prompt variants.

## End-to-End Flow

```mermaid
flowchart TB
    subgraph Inputs[Inputs]
        A[Seed support tickets]
        P[Refund policy fixture]
    end

    subgraph TestCreation[Test creation]
        B[Test generator]
        C[Stress-test suite]
    end

    subgraph Execution[Agent execution]
        D[Baseline refund agent]
        E[Prompt variants]
        F[Agent run records]
    end

    subgraph Evaluation[Evaluation]
        G[Evaluator]
        H[Failure taxonomy]
        I[Variant metrics]
    end

    subgraph Evidence[W&B evidence layer]
        W[W&B Weave traces]
        K[W&B Tables and run summary]
    end

    J[Streamlit dashboard]

    A --> B
    P --> B
    B --> C
    C --> D
    C --> E
    P --> D
    P --> E
    D --> F
    E --> F
    F --> G
    G --> H
    G --> I
    D -. "weave traced" .-> W
    E -. "weave traced" .-> W
    G -. "scores logged" .-> W
    H --> J
    I --> J
    W --> J
    I --> K
    H --> K

    classDef input fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:2px
    classDef generation fill:#fef3c7,stroke:#d97706,color:#0f172a,stroke-width:2px
    classDef execution fill:#ede9fe,stroke:#7c3aed,color:#0f172a,stroke-width:2px
    classDef evaluation fill:#fee2e2,stroke:#dc2626,color:#0f172a,stroke-width:2px
    classDef evidence fill:#dcfce7,stroke:#16a34a,color:#0f172a,stroke-width:2px
    classDef dashboard fill:#e5e7eb,stroke:#374151,color:#0f172a,stroke-width:2px

    class A,P input
    class B,C generation
    class D,E,F execution
    class G,H,I evaluation
    class W,K evidence
    class J dashboard
```

PNG: [agent-qa-lab-flow.png](diagrams/agent-qa-lab-flow.png)

## Runtime Architecture

```mermaid
flowchart TB
    subgraph UI[Local UI]
        S[Streamlit app]
        CLI[CLI smoke test]
    end

    subgraph Data[Demo fixtures]
        Policy[refund_policy.md]
        Seeds[seed_tickets.json]
        Tests[fallback_tests.json]
    end

    subgraph Core[Agent QA Lab package]
        TG[test_generator.py]
        Runner[runner.py]
        Agents[support_agents.py]
        Eval[evaluator.py]
        Prompts[prompts.py]
        Log[wandb_logging.py]
    end

    subgraph AgentWorkflow[Refund support workflow]
        Triage[Triage Agent]
        Lookup[Policy Lookup]
        Decision[Decision Agent]
        Response[Response Agent]
        Judge[QA Judge]
    end

    subgraph WB[Weights and Biases]
        Weave[Weave trace tree]
        Tables[W&B Tables]
        Run[Run summary]
    end

    S --> Runner
    CLI --> Runner
    Policy --> TG
    Seeds --> TG
    Tests --> TG
    TG --> Runner
    Prompts --> Runner
    Runner --> Agents
    Agents --> Triage --> Lookup --> Decision --> Response
    Response --> Eval
    Eval --> Judge
    Eval --> Runner
    Runner --> Log
    Log --> Weave
    Log --> Tables
    Log --> Run

    classDef ui fill:#e5e7eb,stroke:#374151,color:#0f172a,stroke-width:2px
    classDef data fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:2px
    classDef core fill:#fef3c7,stroke:#d97706,color:#0f172a,stroke-width:2px
    classDef workflow fill:#ede9fe,stroke:#7c3aed,color:#0f172a,stroke-width:2px
    classDef eval fill:#fee2e2,stroke:#dc2626,color:#0f172a,stroke-width:2px
    classDef wandb fill:#dcfce7,stroke:#16a34a,color:#0f172a,stroke-width:2px

    class S,CLI ui
    class Policy,Seeds,Tests data
    class TG,Runner,Agents,Prompts,Log core
    class Triage,Lookup,Decision,Response workflow
    class Eval,Judge eval
    class Weave,Tables,Run wandb
```

PNG: [agent-qa-lab-architecture.png](diagrams/agent-qa-lab-architecture.png)

## What Happens During a Demo

1. **Load Demo Suite** loads deterministic refund-support stress tests from `data/fallback_tests.json`.
2. **Run Baseline + Variants** runs the same cases against the flawed baseline and three improved prompt variants.
3. Each case moves through the support workflow: triage, policy lookup, refund decision, response drafting, and evaluation.
4. `@weave.op` wraps the major steps so W&B Weave can show a trace tree for each run.
5. The evaluator assigns pass/fail, numeric scores, and a failure category.
6. The dashboard shows pass-rate improvement, fixed cases, remaining failures, and representative examples.
7. In online W&B mode, the app logs evaluation tables and summaries to the `agent-qa-lab` W&B project.

## Why W&B Matters Here

W&B is not just a log sink in this demo. It is the evidence layer:

- **Weave traces** show where a bad answer came from.
- **Tables** compare baseline and variant outputs row by row.
- **Run summaries** show the best pass rate and variant-level metrics.
- **Project history** makes the demo reproducible across runs.
