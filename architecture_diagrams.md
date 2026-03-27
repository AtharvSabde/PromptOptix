# PromptOptimizer Pro — Architecture Diagrams

> Mermaid diagrams for research paper inclusion.
> Requires Mermaid v10+ for `direction` inside subgraphs.

---

## Figure 1: High-Level System Architecture

```mermaid
flowchart LR
    USER(["User"])

    subgraph FE["Frontend  ·  React 19 · TypeScript · Vite · Tailwind CSS"]
        FE_P["5 Pages\nAnalyze · Optimize\nHistory · Techniques · Home"]
        FE_H["Custom Hooks\nuseAnalysis · useOptimization\nuseHistory · useTechniques"]
        FE_S["API Client\nAxios · SSE Streaming"]
        FE_P --> FE_H --> FE_S
    end

    USER -->|"prompt + context"| FE_P

    FE_S -->|"HTTP REST / SSE"| BE_R

    subgraph BE["Backend  ·  FastAPI · Python 3.11+"]
        BE_R["API Routes\n/analyze  /optimize\n/optimize/advanced  /history"]
        BE_V["Validation & Sanitization"]
        BE_R --> BE_V
    end

    BE_V --> OR

    subgraph MAS["Multi-Agent Orchestration System"]
        OR["Agent Orchestrator\nasyncio.gather — parallel execution"]
        A1["Clarity Agent\nD001–D004"]
        A2["Structure Agent\nD005–D009"]
        A3["Context Agent\nD010–D014"]
        A4["Security Agent\nD023–D028"]
        CV["Consensus Voting\nConfidence-weighted · τ = 0.70\nPriority boosting: task-type · domain"]
        OR --> A1 & A2 & A3 & A4
        A1 & A2 & A3 & A4 --> CV
    end

    CV --> OPT_S & OPT_D & OPT_H & OPT_C

    subgraph OE["Optimization Engine"]
        direction LR
        OPT_S["Standard\nSingle-pass LLM\n~30 s"]
        OPT_D["DGEO\nDefect-Guided\nEvolutionary\n~2 min"]
        OPT_H["SHDT\nScored History\n+ Trajectories\n~1 min"]
        OPT_C["CDRAF\nCritic-Driven\nRefinement\n~1 min"]
    end

    OPT_S & OPT_D & OPT_H & OPT_C --> LLMSVC["LLM Service\nAnthropic Claude  ·  Groq Llama\nOpenAI GPT-4o  ·  Google Gemini"]
    OPT_S & OPT_D & OPT_H & OPT_C <-->|"persist / query"| DB[("SQLite\nDatabase\n3 tables")]

    LLMSVC --> OUT(["Optimized Prompt\n+ Analysis Report"])
    OUT -->|"JSON / SSE"| FE_S
```

---

## Figure 2: Comprehensive System Architecture & Data Flow

```mermaid
flowchart TD
    USER(["User\nBrowser"])

    %% ─────────────────────────────────────────────
    %% FRONTEND LAYER
    %% ─────────────────────────────────────────────
    subgraph FE_LAYER["FRONTEND  ·  React 19 · TypeScript · Vite · Tailwind CSS · Recharts · Framer Motion"]
        direction LR
        FE_PAGES["Pages\nHomePage\nAnalyzePage\nOptimizePage\nHistoryPage\nTechniquesPage"]
        FE_HOOKS["Custom Hooks\nuseAnalysis\nuseOptimization\nuseAdvancedOptimization\nuseHistory\nuseTechniques"]
        FE_API["API Services\nanalysis.service.ts\noptimize.service.ts\nhistory.service.ts\ntechniques.service.ts\nAxios Client + SSE Streaming"]
        FE_PAGES --> FE_HOOKS --> FE_API
    end

    USER -->|"prompt input\n+ task type + domain"| FE_PAGES
    FE_API -->|"HTTP POST\nSSE events"| BE_ROUTES

    %% ─────────────────────────────────────────────
    %% BACKEND LAYER
    %% ─────────────────────────────────────────────
    subgraph BE_LAYER["BACKEND  ·  FastAPI · Python 3.11+ · Pydantic · Uvicorn"]
        direction LR
        BE_ROUTES["REST Endpoints\n/api/analyze  (+/stream)\n/api/optimize\n/api/optimize/advanced\n/api/history  (+/stats)\n/api/techniques\n/api/health"]
        BE_VALID["Validation & Sanitization\nInput validators\nToken counter (tiktoken)\nResponse parser\nCustom error handlers"]
        BE_ROUTES --> BE_VALID
    end

    %% ─────────────────────────────────────────────
    %% KNOWLEDGE BASE
    %% ─────────────────────────────────────────────
    subgraph KB_LAYER["KNOWLEDGE BASE  ·  Research Foundation: Tian et al. · Nagpure et al."]
        direction LR
        KB_DT["Defect Taxonomy\n28 Defects · 6 Categories\n──────────────────────\nSpec & Intent  D001–D004\n  Ambiguity · Underspecification\n  Conflicting Requirements\n  Intent Misalignment\n──────────────────────\nStructure  D005–D009\n  Role Separation · Disorganization\n  Syntax Errors · Format Issues\n  Information Overload\n──────────────────────\nContext & Memory  D010–D014\n  Context Overflow · Missing Context\n  Irrelevant Info · Misreferencing\n  Forgotten Instructions\n──────────────────────\nOutput Guidance  D015–D018\n  Output Constraints · Expectations\n  Success Criteria · Tone/Style\n──────────────────────\nExamples  D019–D022\n  Missing · Poor Quality\n  Insufficient Diversity\n  Example-Query Mismatch\n──────────────────────\nSecurity & Safety  D023–D028\n  Prompt Injection · Jailbreaking\n  Privacy · Harmful Content\n  Bias · IP Concerns"]
        KB_TR["Technique Registry\n41+ Techniques · 10 Categories\n──────────────────────\nZero-Shot · Few-Shot\nChain-of-Thought (CoT)\nRole-Based Prompting\nStructured Output\nDecomposition\nContext Enhancement\nIterative Refinement\nAdvanced Reasoning\n  (Self-Consistency,\n   Tree-of-Thought)\nMeta-Optimization\n──────────────────────\nEach technique maps to\none or more defect IDs\nwith effectiveness score"]
    end

    BE_VALID --> ORCH
    KB_DT -.->|"defect definitions\n& severity indicators"| ORCH

    %% ─────────────────────────────────────────────
    %% MULTI-AGENT ORCHESTRATION
    %% ─────────────────────────────────────────────
    subgraph MAS_LAYER["MULTI-AGENT ORCHESTRATION  ·  agent_orchestrator.py  (717 lines)"]
        ORCH["Agent Orchestrator\nasyncio.gather — all 4 agents run in parallel\nTolerates partial failures · SSE streaming support"]

        AG1["Clarity Agent\nFocus: Specification & Intent\n──────────────────\nD001 Ambiguity\nD002 Underspecification\nD003 Conflicting Requirements\nD004 Intent Misalignment"]
        AG2["Structure Agent\nFocus: Formatting & Layout\n──────────────────\nD005 Poor Role Separation\nD006 Disorganization\nD007 Syntax Errors\nD008 Format Issues\nD009 Information Overload"]
        AG3["Context Agent\nFocus: Context & Memory\n──────────────────\nD010 Context Overflow\nD011 Missing Context\nD012 Irrelevant Information\nD013 Misreferencing\nD014 Forgotten Instructions"]
        AG4["Security Agent\nFocus: Safety & Security\n──────────────────\nD023 Prompt Injection\nD024 Jailbreaking Attempts\nD025 Privacy Violations\nD026 Harmful Content\nD027 Bias & Discrimination\nD028 IP Concerns"]

        CONS["Consensus Voting & Aggregation\n──────────────────────────────────────────\nconsensus = detections / capable_agents\nConfidence-weighted averaging (squared weights)\nBoost factor: 1 + 0.1 × (detections − 1)\nThreshold filter: τ = 0.70\nDisagreements tracked separately\n──────────────────────────────────────────\nPriority Boosting\nTask-type: code_gen · reasoning · creative …\nDomain: healthcare · legal · software …\nUser-reported issues: mapped via issue_registry"]

        ORCH -->|"parallel LLM call"| AG1 & AG2 & AG3 & AG4
        AG1 & AG2 & AG3 & AG4 --> CONS
    end

    KB_DT -.->|"defect definitions\nper agent scope"| AG1 & AG2 & AG3 & AG4
    CONS --> OPT_STD & OPT_DGE & OPT_SHD & OPT_CDR

    %% ─────────────────────────────────────────────
    %% OPTIMIZATION ENGINE
    %% ─────────────────────────────────────────────
    subgraph OPT_LAYER["OPTIMIZATION ENGINE"]
        direction LR
        OPT_STD["Standard\noptimizer_service.py\n──────────────────\nTechnique selection\n  (greedy coverage)\nSingle-pass LLM rewrite\nBefore / after re-analysis\nImprovement verification\nLatency: ~30 seconds"]
        OPT_DGE["DGEO\ndgeo_optimizer.py\nDefect-Guided Evolutionary\nOptimization\n──────────────────\nPopulation size: 5\nGenerations: 3\nSelect top 50%\nLLM crossover\nMutation per defect\nFitness = agent score\nLatency: ~2 minutes"]
        OPT_SHD["SHDT\noptimizer_service.py\nScored History +\nDefect Trajectories\n──────────────────\nMax iterations: 4\nTarget score: 8.0\nMin improvement: 0.3\nTracks defects fixed /\nremaining / introduced\nCausal learning\nLatency: ~1 minute"]
        OPT_CDR["CDRAF\noptimizer_service.py\nCritic-Driven Refinement\n+ Agent Feedback\n──────────────────\nBaseline optimization\nCritique rounds: max 2\nEach agent critiques\noptimized prompt\nLLM refines per feedback\nLatency: ~1 minute"]
    end

    KB_TR -.->|"technique → defect\nmappings + effectiveness"| OPT_STD & OPT_DGE & OPT_SHD & OPT_CDR

    OPT_STD & OPT_DGE & OPT_SHD & OPT_CDR --> LLM_SVC

    %% ─────────────────────────────────────────────
    %% LLM SERVICE LAYER
    %% ─────────────────────────────────────────────
    subgraph LLM_LAYER["LLM SERVICE  ·  llm_service.py  ·  Multi-provider · Retry logic · Token tracking · Cost estimation"]
        direction LR
        LLM_A["Anthropic Claude\nPrimary Provider\n──────────────\nSonnet 4.6\nOpus 4.6\nHaiku 4.5\nContext: 200K tokens"]
        LLM_G["Groq Llama\nFallback Provider\n──────────────\nLlama 3.3 70B\nContext: 128K tokens\nFree tier available"]
        LLM_O["OpenAI\n──────────────\nGPT-4o\nGPT-4o Mini\nContext: 128K tokens"]
        LLM_M["Google Gemini\n──────────────\nGemini 2.0 Flash\nGemini 1.5 Pro\nContext: 1M–2M tokens"]
        LLM_SVC["call() · call_with_json_response()\nbatch_call() · streaming support\n3× retry with exponential backoff\nToken counting · Cost estimation"]
        LLM_SVC --> LLM_A & LLM_G & LLM_O & LLM_M
    end

    LLM_A & LLM_G & LLM_O & LLM_M -->|"model response"| LLM_SVC
    LLM_SVC -->|"parsed result"| OPT_STD & OPT_DGE & OPT_SHD & OPT_CDR

    OPT_STD & OPT_DGE & OPT_SHD & OPT_CDR -->|"save optimization run"| DB_H

    %% ─────────────────────────────────────────────
    %% PERSISTENCE LAYER
    %% ─────────────────────────────────────────────
    subgraph DB_LAYER["PERSISTENCE  ·  SQLite  ·  data/promptoptimizer.db"]
        direction LR
        DB_H["optimization_history\n──────────────────\noriginal_prompt\noptimized_prompt\nstrategy\nscore_before / score_after\nimprovement\ndefects_before / after  JSON\nevolution_history  JSON\ntrajectory_history  JSON\ncritique_history  JSON\nmetadata  JSON\ntask_type · domain\ncreated_at"]
        DB_T["technique_effectiveness\n──────────────────\ntechnique_id\ndefect_id\ntimes_applied\nsuccess_count\ntotal_improvement\navg_improvement\nlast_used\n(learned over time)"]
        DB_B["benchmark_results\n──────────────────\nbenchmark_id\nstrategy\nscore_before / after\nimprovement\ndefects_fixed\nprocessing_time_ms\ncost"]
    end

    OPT_STD & OPT_DGE & OPT_SHD & OPT_CDR -->|"record technique\neffectiveness"| DB_T
    DB_T -.->|"effectiveness scores\n(learned)"| KB_TR

    OPT_STD & OPT_DGE & OPT_SHD & OPT_CDR -->|"optimized prompt\n+ full analysis"| BE_ROUTES
    BE_ROUTES -->|"JSON response\n+ SSE event stream"| FE_API
    FE_API -->|"rendered result\n+ diff + charts"| USER
```

---

## Component Summary

| Layer | Components | Key Detail |
|---|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind | 5 pages · 5 hooks · 4 API services · SSE streaming |
| **Backend** | FastAPI, Python 3.11+, Pydantic | 6 routes · Input validation · Token counting |
| **Knowledge Base** | Defect Taxonomy, Technique Registry | 28 defects (6 categories) · 41+ techniques (10 categories) |
| **Multi-Agent** | 4 Specialized Agents + Orchestrator | Parallel via `asyncio.gather` · Consensus τ = 0.70 |
| **Optimization** | Standard, DGEO, SHDT, CDRAF | Single-pass · Evolutionary · Trajectory · Critic-driven |
| **LLM Service** | Anthropic, Groq, OpenAI, Gemini | Primary/fallback · Retry · Token tracking · Cost estimation |
| **Persistence** | SQLite (3 tables) | Optimization history · Technique effectiveness (learned) · Benchmarks |

### Optimization Strategy Parameters

| Strategy | Algorithm | Parameters | Latency |
|---|---|---|---|
| **Standard** | Technique selection → single-pass LLM rewrite → re-analysis | max 10 techniques | ~30 s |
| **DGEO** | Defect-Guided Evolutionary: Generate → Evaluate → Select → Crossover → Mutate | population = 5, generations = 3 | ~2 min |
| **SHDT** | Iterative improvement with defect trajectory tracking | max iterations = 4, target score = 8.0 | ~1 min |
| **CDRAF** | Baseline pass + agent-specific critique rounds | max critique rounds = 2 | ~1 min |

### Multi-Agent Consensus Algorithm

```
For each detected defect:
  consensus  = num_detections / num_capable_agents
  w_conf     = Σ(confidenceᵢ²) / Σ(confidenceᵢ)
  boost      = 1 + 0.1 × (num_detections − 1)
  final_conf = min(1.0, w_conf × boost × task_boost × domain_boost)
  if consensus ≥ τ (0.70) → include in final report
  else               → record as disagreement
```

---

## Figure 3: Backend Component Architecture

> Internal module structure of the FastAPI backend — all layers, their responsibilities, and inter-module dependencies.

```mermaid
flowchart TD
    subgraph ENTRY["Entry Point  ·  app.py"]
        APP["FastAPI Application\nCORS Middleware · Lifespan Manager\nHost 0.0.0.0 · Port 8000"]
    end

    subgraph ROUTES["Routes Layer"]
        direction LR
        R_AN["/api/analyze\n/api/analyze/stream\nanalyze.py"]
        R_OP["/api/optimize\n/api/techniques\noptimize.py"]
        R_HI["/api/optimize/advanced\n/api/history\n/api/history/stats\nhistory.py"]
        R_HE["/api/health\nhealth.py"]
    end

    subgraph SERVICES["Service Layer"]
        direction LR
        SVC_ORC["agent_orchestrator.py\nParallel orchestration\nConsensus voting\nPriority boosting\nSSE streaming\n717 lines"]
        SVC_OPT["optimizer_service.py\nStandard optimization\nSHDT trajectory\nCDRAF critique rounds\nTechnique selection"]
        SVC_DGE["dgeo_optimizer.py\nEvolutionary search\nPopulation management\nCrossover · Mutation\nFitness evaluation"]
        SVC_LLM["llm_service.py\nMulti-provider abstraction\ncall() · batch_call()\nRetry w/ backoff (3×)\nToken counting · Cost\n730+ lines"]
        SVC_DB["db_service.py\nSQLite persistence\nHistory · Effectiveness\nBenchmarks · Stats"]
        SVC_ANA["analyzer_service.py\nHigh-level wrapper\naround orchestrator"]
    end

    subgraph AGENTS["Agent Layer"]
        AG_BASE["base_agent.py\nAbstract analyze()\nMeta-prompt generation\nJSON response parsing\nTaxonomy enrichment"]
        AG_CL["clarity_agent.py\nD001–D004\nSpecification & Intent"]
        AG_ST["structure_agent.py\nD005–D009\nFormatting & Layout"]
        AG_CX["context_agent.py\nD010–D014\nContext & Memory"]
        AG_SC["security_agent.py\nD023–D028\nSafety & Security"]
        AG_BASE --> AG_CL & AG_ST & AG_CX & AG_SC
    end

    subgraph MODELS["Knowledge Models"]
        direction LR
        MOD_DT["defect_taxonomy.py\n28 Defects · 6 Categories\nSeverity · Indicators\nRemediation mapping\n684 lines"]
        MOD_TR["technique_registry.py\n41+ Techniques · 10 Categories\nEffectiveness scores\nDefect-to-technique map\n1588 lines"]
        MOD_IR["issue_registry.py\nUser issue → defect\nnatural language mapping\n553 lines"]
        MOD_RQ["request_models.py\nPydantic v2 DTOs\nAnalyzeRequest\nOptimizeRequest\nAdvancedOptimizeRequest"]
        MOD_RS["response_models.py\nAnalysisResponse\nOptimizationResponse\nAdvancedOptimizeResponse"]
    end

    subgraph UTILS["Utilities"]
        direction LR
        UT_VAL["validators.py\nInput sanitization\nEnum + range checks\nNull byte removal\n279 lines"]
        UT_TOK["token_counter.py\ntiktoken · LRU cache\nCost estimation\nContext limit guard\n262 lines"]
        UT_PAR["response_parser.py\nJSON extraction\nRequired field checks\nMalformed LLM output handling"]
        UT_ERR["error_handlers.py\nAPIKeyError\nRateLimitError\nTokenLimitError\nLLMServiceError"]
    end

    subgraph CONFIG["Configuration  ·  config.py  (476 lines)"]
        direction LR
        CFG_K["API Keys\nAnthropic · Groq\nOpenAI · Gemini"]
        CFG_M["Model Registry\nContext windows\nCost per 1K tokens\nStreaming support"]
        CFG_A["Agent Config\nNUM_AGENTS = 4\nCONSENSUS_THRESHOLD = 0.70\nTask-type priority boosts\nDomain priority boosts"]
        CFG_S["Strategy Params\nDGEO: pop=5 · gen=3\nSHDT: iter=4 · target=8.0\nCDRAF: rounds=2"]
    end

    subgraph DB["Persistence  ·  SQLite  ·  data/promptoptimizer.db"]
        direction LR
        DB_H["optimization_history\noriginal · optimized · strategy\nscores · improvement\nevolution/trajectory/critique JSON"]
        DB_T["technique_effectiveness\ntechnique_id · defect_id\ntimes_applied · avg_improvement\n(adaptive learning)"]
        DB_B["benchmark_results\nbenchmark_id · strategy\nscores · timing · cost"]
    end

    subgraph EXTERNAL["External  ·  LLM APIs"]
        direction LR
        EX_A["Anthropic\nClaude Sonnet 4.6\nClaude Opus 4.6\nClaude Haiku 4.5"]
        EX_G["Groq\nLlama 3.3 70B\n128K context"]
        EX_O["OpenAI\nGPT-4o\nGPT-4o Mini"]
        EX_M["Google\nGemini 2.0 Flash\nGemini 1.5 Pro\n1M–2M context"]
    end

    APP --> R_AN & R_OP & R_HI & R_HE

    R_AN --> SVC_ANA
    R_OP --> SVC_OPT
    R_HI --> SVC_OPT & SVC_DGE

    SVC_ANA --> SVC_ORC
    SVC_OPT --> SVC_ORC
    SVC_DGE --> SVC_ORC

    SVC_ORC --> AG_CL & AG_ST & AG_CX & AG_SC
    AG_CL & AG_ST & AG_CX & AG_SC --> SVC_LLM
    SVC_OPT --> SVC_LLM
    SVC_DGE --> SVC_LLM
    SVC_LLM --> EX_A & EX_G & EX_O & EX_M

    MOD_DT -.->|"defect definitions"| SVC_ORC
    MOD_DT -.->|"agent defect scope"| AG_CL & AG_ST & AG_CX & AG_SC
    MOD_TR -.->|"technique → defect map"| SVC_OPT
    MOD_IR -.->|"issue → defect map"| SVC_ORC
    CFG_A -.->|"consensus config"| SVC_ORC
    CFG_M -.->|"model selection"| SVC_LLM
    CFG_S -.->|"strategy params"| SVC_OPT & SVC_DGE

    R_AN & R_OP & R_HI --> UT_VAL
    SVC_LLM --> UT_TOK & UT_PAR

    SVC_OPT --> SVC_DB
    SVC_DGE --> SVC_DB
    SVC_DB --> DB_H & DB_T & DB_B
    DB_T -.->|"learned effectiveness\nfeedback"| MOD_TR
```

---

## Figure 4: Backend Request Processing Pipeline

> End-to-end algorithmic flow of a single optimization request through the backend — from API receipt to persisted response.

```mermaid
flowchart TD
    REQ(["API Request\nPOST /api/optimize/advanced\n{ prompt, strategy, task_type, domain }"])

    REQ --> VALID

    VALID{"Input Validation\nvalidators.py"}
    VALID -->|"invalid"| ERR(["400 Bad Request\nValidation error details"])
    VALID -->|"valid"| P1_START

    subgraph PHASE1["Phase 1 — Multi-Agent Defect Detection"]
        P1_START["Agent Orchestrator\nasyncio.gather — spawn 4 parallel tasks"]

        subgraph PARALLEL["Parallel LLM Calls  ·  Independent Execution"]
            direction LR
            AG1["Clarity Agent\nGenerate detection prompt\n→ LLM API call\n→ Parse JSON\n→ Enrich w/ taxonomy\nD001–D004"]
            AG2["Structure Agent\nGenerate detection prompt\n→ LLM API call\n→ Parse JSON\n→ Enrich w/ taxonomy\nD005–D009"]
            AG3["Context Agent\nGenerate detection prompt\n→ LLM API call\n→ Parse JSON\n→ Enrich w/ taxonomy\nD010–D014"]
            AG4["Security Agent\nGenerate detection prompt\n→ LLM API call\n→ Parse JSON\n→ Enrich w/ taxonomy\nD023–D028"]
        end

        CONS["Consensus Aggregation\n① Group detections by defect_id\n② consensus = detections ÷ capable_agents\n③ w_conf = Σ(conf²) ÷ Σ(conf)\n④ boost = 1 + 0.1 × (detections − 1)\n⑤ Apply task-type priority multipliers\n⑥ Apply domain priority multipliers\n⑦ Apply user-issue priority boosts\n⑧ Filter: τ = 0.70  →  disagreements below\n⑨ Sort by severity × final_confidence"]

        P1_START --> AG1 & AG2 & AG3 & AG4 --> CONS
    end

    CONS --> SKIP_CHK

    SKIP_CHK{"Overall score\n≥ 9.0 ?"}
    SKIP_CHK -->|"yes — already excellent"| NOOP(["Return original prompt\nno optimization applied"])
    SKIP_CHK -->|"no — proceed"| STRAT_SEL

    STRAT_SEL{"Strategy\nSelector"}

    %% ── STANDARD ──────────────────────────────────────
    subgraph STD["Standard  ·  optimizer_service.py"]
        direction TB
        ST1["Select techniques\nGreedy defect coverage\nRank by effectiveness score\nRespect optimization_level"]
        ST2["Single-pass LLM rewrite\nApply up to 10 techniques\nAnti-template validation"]
        ST3["Re-analyze optimized prompt\nAgent orchestrator (2nd pass)"]
        ST4["Compute improvement\nscore_after − score_before"]
        ST1 --> ST2 --> ST3 --> ST4
    end

    %% ── DGEO ──────────────────────────────────────────
    subgraph DGEO["DGEO  ·  dgeo_optimizer.py  ·  Defect-Guided Evolutionary Optimization"]
        direction TB
        DG1["Generate initial population\n5 variants — each targets\ndifferent defect subsets"]
        DG2["Evaluate fitness\nRe-analyze each variant\nScore = agent consensus score"]
        DG3["Select survivors\nKeep top 50%"]
        DG4["LLM Crossover\nCombine strengths of\ntop-2 scoring variants"]
        DG5["LLM Mutation\nApply remaining\ndefect remediations"]
        DG6{"Generation\n≤ 3 ?"}
        DG7["Return best variant\n+ full evolution history"]
        DG1 --> DG2 --> DG3 --> DG4 --> DG5 --> DG6
        DG6 -->|"next generation"| DG2
        DG6 -->|"complete"| DG7
    end

    %% ── SHDT ──────────────────────────────────────────
    subgraph SHDT["SHDT  ·  optimizer_service.py  ·  Scored History + Defect Trajectories"]
        direction TB
        SH1["Apply targeted improvements\nfor current defect set"]
        SH2["Re-analyze result\nagent orchestrator pass"]
        SH3["Record trajectory entry\ndefects_fixed · defects_remaining\ndefects_introduced · Δscore"]
        SH4{"Score > 8.0\nor Δ < 0.3\nor iterations > 4 ?"}
        SH5["Return best prompt\n+ full trajectory history"]
        SH1 --> SH2 --> SH3 --> SH4
        SH4 -->|"continue"| SH1
        SH4 -->|"converged"| SH5
    end

    %% ── CDRAF ─────────────────────────────────────────
    subgraph CDRAF["CDRAF  ·  optimizer_service.py  ·  Critic-Driven Refinement + Agent Feedback"]
        direction TB
        CD1["Standard baseline pass\n(technique selection + rewrite)"]
        CD2["Re-analyze optimized prompt\nall 4 agents as critics"]
        CD3["Collect per-agent critiques\nClarity · Structure · Context · Security\nfocus-area specific issues + remediations"]
        CD4["LLM refinement pass\nIncorporate agent feedback\nper critique round"]
        CD5{"Round\n≤ 2 ?"}
        CD6["Return refined prompt\n+ all critique rounds"]
        CD1 --> CD2 --> CD3 --> CD4 --> CD5
        CD5 -->|"next round"| CD2
        CD5 -->|"complete"| CD6
    end

    STRAT_SEL -->|"standard"| STD
    STRAT_SEL -->|"dgeo"| DGEO
    STRAT_SEL -->|"shdt"| SHDT
    STRAT_SEL -->|"cdraf"| CDRAF

    ST4 & DG7 & SH5 & CD6 --> PERSIST

    subgraph PERSIST["Persistence & Response Assembly  ·  db_service.py"]
        direction LR
        PS1["optimization_history\nSave original · optimized · strategy\nscores · techniques · metadata\nevolution / trajectory / critique JSON"]
        PS2["technique_effectiveness\nUpdate technique_id × defect_id\ntimes_applied · avg_improvement\n(adaptive learning signal)"]
        PS3["Build AdvancedOptimizeResponse\noriginal_prompt · optimized_prompt\nstrategy · score_before · score_after\nimprovement · strategy-specific history\ntoken usage · cost · processing_time_ms"]
        PS1 & PS2 --> PS3
    end

    PS3 --> RESP(["HTTP 200 — JSON Response\n+ SSE event stream\nto Frontend"])
```
