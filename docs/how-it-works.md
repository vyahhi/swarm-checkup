# How Agent QA Lab Works

Agent QA Lab is a deterministic demo of an agent reliability workflow. It starts with a deliberately flawed refund-support swarm, runs it against a stable stress-test suite, traces each agent and handoff in W&B Weave, scores the output and coordination, and compares improved prompt variants.

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
        D[Baseline refund swarm]
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

    J[Markdown report and CLI summary]

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
    D -. "agents and handoffs traced" .-> W
    E -. "agents and handoffs traced" .-> W
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
        S[Skill runner]
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

    subgraph AgentWorkflow[Refund support swarm]
        Coord[Coordinator]
        Triage[Triage Agent]
        Lookup[Policy Agent]
        Risk[Risk Agent]
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
    Agents --> Coord --> Triage --> Lookup --> Risk --> Decision --> Response
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
    class Coord,Triage,Lookup,Risk,Decision,Response workflow
    class Eval,Judge eval
    class Weave,Tables,Run wandb
```

PNG: [agent-qa-lab-architecture.png](diagrams/agent-qa-lab-architecture.png)

## What Happens During a Demo

1. The demo harness loads deterministic refund-support stress tests from `data/fallback_tests.json`.
2. The same cases run against the flawed baseline swarm and three improved prompt variants.
3. Each case moves through the support swarm: coordinator plan, triage, policy lookup, risk review, refund decision, response drafting, and evaluation.
4. `@weave.op` wraps the major agent and evaluator steps so W&B Weave can show a trace tree for each run.
5. The evaluator assigns pass/fail, numeric scores, coordination score, and a failure category.
6. The CLI and Markdown report show pass-rate improvement, fixed cases, remaining failures, and representative examples.
7. In online W&B mode, the harness logs evaluation tables and summaries to the `agent-qa-lab` W&B project.

## Why W&B Matters Here

W&B is not just a log sink in this demo. It is the evidence layer:

- **Weave traces** show where a bad answer came from.
- **Tables** compare baseline and variant outputs row by row, including participating agents and handoff counts.
- **Run summaries** show the best pass rate and variant-level metrics.
- **Project history** makes the demo reproducible across runs.
