Math & Algorithms Appendix v0.3
Hedgehog OS / Fractal Reflexive OS
0. Назначение документа
Этот документ фиксирует математическую и алгоритмическую основу ОС:
	1	время;
	2	DRS и memory-first reuse;
	3	фрактализация;
	4	AVF — поле жизнеспособности ветвей;
	5	Post V&V;
	6	GTValidator;
	7	GT-TTL;
	8	Marennya;
	9	UP!;
	10	Continuous / delta-runtime как будущий слой;
	11	базовые инварианты расчётов.
Цель документа — не философия, а операционная математика, которую можно постепенно переносить в код.

⸻

1. Базовые обозначения
Пусть:
I
— входной intent пользователя или события.
G
— каноническая цель.
W_t
— WorldState в момент t.
D
— локальный DRS.
D_{ext}
— внешний DRS / внешние указатели.
N
— множество установленных иголок.
V = \{v_1, v_2, ..., v_n\}
— множество CandidateVectors, то есть возможных направлений решения.
A_p
— AttractorPacket.
P
— PlanGraph.
R = \{r_1, r_2, ..., r_m\}
— множество ResultProposal от исполнителей.
Q
— множество Post V&V отчётов.
GT
— отчёт Game Theory Validator.
F
— FinalOutput, который имеет право создать только RootOrchestrator.
Общий pipeline:
I \rightarrow G \rightarrow W_t \rightarrow DRS\_retrieval \rightarrow V \rightarrow AVF \rightarrow A_p \rightarrow P \rightarrow R \rightarrow Q \rightarrow GT \rightarrow F \rightarrow DRS\_writeback

⸻

2. Время: TimeEnvelope, TemporalQuery, старение знания
2.1. Четыре оси времени
Каждая запись знания должна иметь TimeEnvelope.
TE = (PT, KT, ET, CT, TTL)
Где:
PT — Physical Time
PT = t_{created}
Физическое системное время создания записи.
KT — Knowledge Time
KT = t_{asof}
Время, “на которое” знание считается истинным или актуальным.
ET — Event Time
ET = t_{event}
Время события в предметной области.
CT — Context Time
CT = c_{session}
Временная координата внутри сессии, задачи, ветки фрактала или контекста.
TTL
TTL = \Delta t_{life}
Первичный срок жизни записи до пересмотра.

⸻

2.2. TimeEnvelope
Минимальный объект:
{
  "pt_created_at": "2026-05-21T12:00:00Z",
  "kt_asof": "2026-05-21T12:00:00Z",
  "et_observed_at": null,
  "ct_session_anchor": "sess_001",
  "ttl_seconds": 2592000,
  "freshness_class": "normal"
}
Инвариант:
\forall r \in DRS: TimeEnvelope(r) \neq \varnothing
То есть каждая DRS-запись обязана иметь TimeEnvelope.

⸻

2.3. TemporalQuery
Любой retrieval обязан иметь TemporalQuery:
TQ = (as\_of, range, freshness\_bias, max\_age)
Пример:
{
  "as_of": "2026-05-21T12:00:00Z",
  "time_range": {
    "from": null,
    "to": "2026-05-21T12:00:00Z"
  },
  "freshness_bias": "prefer_recent",
  "max_age_seconds": 2592000
}
Инвариант:
DRS.query(\cdot) \Rightarrow TemporalQuery \text{ required}

⸻

2.4. Возраст знания
Для записи r:
Age(r, t) = t - KT(r)
Если используется PT:
PhysicalAge(r, t) = t - PT(r)
Если событие важно по предметной области:
EventAge(r, t) = t - ET(r)
В retrieval надо явно решать, какая ось времени важнее:
Age_{effective}(r) =\omega_{PT} Age_{PT}+ \omega_{KT} Age_{KT}+ \omega_{ET} Age_{ET}
где:
\omega_{PT}+\omega_{KT}+\omega_{ET}=1

⸻

2.5. Экспоненциальное старение
Базовое старение знания:
W_t(r)=e^{-\lambda \Delta t}
где:
\lambda = \frac{\ln 2}{t_{1/2}}
t_{1/2} — half-life записи.
Тогда:
W_t(r)=2^{-\frac{\Delta t}{t_{1/2}}}
Если запись свежая:
\Delta t \approx 0 \Rightarrow W_t \approx 1
Если прошёл один half-life:
\Delta t = t_{1/2} \Rightarrow W_t = 0.5

⸻

2.6. FreshnessBoost
Записи разных типов стареют по-разному.
FreshnessBoost =f(freshness\_class, domain, mode)
Например:
static:        2.0
slow_changing: 1.3
normal:        1.0
fast_changing: 0.5
real_time:     0.1
Тогда эффективный half-life:
t_{1/2}^{effective} = t_{1/2}^{base} \cdot FreshnessBoost

⸻

2.7. Temporal validity
Запись валидна для запроса, если:
valid\_from(r) \leq as\_of(TQ) \leq valid\_to(r)
Если valid_to = null, то верхней границы нет.
Если запись протухла:
Age(r) > TTL(r)
то она не обязательно удаляется, но получает штраф:
FreshnessPenalty(r)=\min(1, \frac{Age(r)}{TTL(r)})

⸻

2.8. Temporal conflict
Две записи конфликтуют по времени, если:
content(r_i) \neq content(r_j)
и:
KT(r_i) < KT(r_j)
Тогда при prefer_recent:
priority(r_j) > priority(r_i)
Но при historical_as_of:
priority(r_i) \text{ может быть выше}
если:
KT(r_i) \leq as\_of < KT(r_j)
Это важно для случаев вроде профиля пользователя: старая запись может быть правильной “на тот момент”, но неправильной сейчас.

⸻

3. DRS и memory-first reuse
Ранний Genesis уже фиксировал принцип: перед тем как думать, система вспоминает; если задача уже решалась и качество выше порога — результат можно использовать повторно. Это прямо сформулировано как memory-first reuse в Genesis-документе проекта.  
3.1. Нормализованный ключ намерения
Для intent I:
K = Hash(Intent || NormalizedParams || Domain || Mode)
Где:
	•	Intent — канонизированная цель;
	•	NormalizedParams — очищенные параметры;
	•	Domain — предметная область;
	•	Mode — режим работы.
Пример:
goal:v25:sha256(canonical_goal + normalized_params + domain + mode)

⸻

3.2. Memory-first reuse condition
Повторное использование разрешено, если существует запись:
\exists r \in DRS
такая что:
Key(r)=K
Quality(r) > \tau_{reuse}
Freshness(r) > \tau_{fresh}
PolicyOK(r)=true
GTTrust(r) > \tau_{gt}
Тогда:
Return(Rehydrate(r))
и тяжёлый фрактальный цикл не запускается.

⸻

3.3. Итоговый reuse score
ReuseScore(r)=a Q(r)+ b Freshness(r)+ c GTTrust(r)+ d SemanticSim(r, I)- e Risk(r)- f Conflict(r)
Где:
a+b+c+d+e+f = 1
Reuse разрешён, если:
ReuseScore(r) \geq \tau_{reuse}

⸻

3.4. Semantic similarity
Если точного ключа нет, используется semantic reuse:
Sim(q, r)=cos(Emb(q), Emb(r))
cos(a,b)=\frac{a \cdot b}{||a|| ||b||}
Дополнительно можно использовать Jaccard / MinHash:
J(A,B)=\frac{|A \cap B|}{|A \cup B|}
И объединить:
SemanticScore =\alpha cos(Emb(q), Emb(r))+ \beta J(tokens(q), tokens(r))

⸻

3.5. DRS layers
DRS = Work \cup Thoughts \cup UP \cup DeadEnds \cup Quarantine
Work
Факты и принятые результаты.
Thoughts
Внутридоменные уроки, Marennya, методологические патчи.
UP
Переносы между доменами, protocol templates, opportunities.
DeadEnds
Отрицательный опыт: куда не ходить.
Quarantine
Сырые черновики, ещё не допущенные в рабочие слои.
Инвариант:
Marennya, UP \nrightarrow Work
То есть Marennya и UP не могут напрямую мутировать Work.

⸻

3.6. DRS writeback
После каждого завершённого цикла система пишет:
DRSRecord = (layer, type, content, TimeEnvelope, provenance, GT?, status)
Минимально:
{
  "record_id": "drs_001",
  "layer": "work",
  "type": "task_outcome",
  "domain": "government_certificate",
  "content": {},
  "time_envelope": {},
  "provenance": {
    "request_id": "req_001",
    "plan_id": "plan_001",
    "trace_refs": []
  },
  "gt": {
    "elo": 1532,
    "regret": 0.04,
    "half_life_hours": 720,
    "decay_rate": 0.00096
  },
  "status": "active"
}

⸻

4. Фрактализация
В Genesis уже есть ранняя формализация: сложная задача дробится на подзадачи, формируя дерево или граф вычислений, а ячейка мышления имеет триаду Architect / Orchestrator / Executor.  
4.1. Задача и декомпозиция
Пусть есть задача:
T
Функция декомпозиции:
F(T, C, B) \rightarrow (G, \{t_1,t_2,...,t_n\})
Где:
	•	C — context / WorldState / AttractorPacket;
	•	B — budget;
	•	G — граф зависимостей;
	•	t_i — подзадачи.

⸻

4.2. DAG
План:
P = (N, E)
где:
	•	N — nodes;
	•	E — directed edges.
Ребро:
e_{ij} = (n_i \rightarrow n_j)
означает:
n_j \text{ depends on } output(n_i)

⸻

4.3. Ready set
В любой момент:
S_{ready} =\{ n \in N \mid deps(n) \subseteq S_{completed} \}
То есть узел можно запускать, если все его зависимости завершены.

⸻

4.4. Horizontal branching
Горизонтальное ветвление:
T \rightarrow \{t_1,t_2,t_3\}
где:
deps(t_i)=\varnothing
или независимы друг от друга.
Параллельность:
Parallelism = |\{t_i\}_{ready}|
Ограничение:
Parallelism \leq B_{parallel}

⸻

4.5. Vertical chain
Вертикальный long-chain:
t_1 \rightarrow t_2 \rightarrow t_3 \rightarrow ... \rightarrow t_k
где:
t_{i+1}=f_i(output(t_i))
Следующий шаг невозможен без предыдущего:
output(t_i) \text{ required for } t_{i+1}

⸻

4.6. Hybrid branching
Гибрид:
T \rightarrow \{a_1,a_2\}
потом:
a_1 \rightarrow b_1 \rightarrow c_1
а:
a_2 \rightarrow \{b_2,b_3\}
То есть дерево/граф может сужаться и расширяться.

⸻

4.7. Условие атомарности
Подзадача атомарна, если:
Atomic(t)=true
когда выполняется хотя бы одно:
CostEstimate(t) < \tau_{atomic\_cost}
Uncertainty(t) < \tau_{uncertainty}
Depth(t) \geq Depth_{max}
ToolAvailable(t)=true
NoUsefulDecomposition(t)=true
Если задача атомарна:
Executor(t) \rightarrow ResultProposal
Если нет:
Architect(t) \rightarrow SubPlan

⸻

4.8. Рекурсивная фрактальная ячейка
Каждая клетка:
Cell = (Orchestrator, Architect, Executor)
Рекурсия:
Cell(T) =\begin{cases}Executor(T), & Atomic(T)=true \\Orchestrator(Architect(T)), & Atomic(T)=false\end{cases}

⸻

4.9. Принцип “вассал моего вассала — не мой вассал”
Пусть Root вызывает Architect A_1.
Root \rightarrow A_1
Если A_1 создаёт дочерний кластер C_2:
A_1 \rightarrow C_2
Root не управляет внутренним состоянием C_2:
Root \not\rightarrow internal(C_2)
Root имеет право только:
Root \rightarrow boundary(C_2)
и:
Root \leftarrow snapshot(C_2)
То есть Root задаёт:
	•	goal;
	•	constraints;
	•	budget;
	•	forbidden regions;
	•	expected output schema.
Но не управляет внутренней траекторией внуков.

⸻

4.10. Budget propagation
Общий бюджет:
B = (tokens, time, depth, parallelism, money, risk)
При декомпозиции:
\sum_{i=1}^{n} B_i \leq B_{parent}
Если ветка получает слишком мало бюджета:
B_i < B_{min}\Rightarrow prune(t_i)

⸻

4.11. Branch expansion condition
Ветка расширяется, если:
ExpectedUtility(t_i) - ExpectedCost(t_i) > \tau_{expand}
или:
Uncertainty(t_i) > \tau_{uncertainty}\land ValueOfInformation(t_i) > \tau_{voi}

⸻

4.12. Branch pruning condition
Ветка гасится, если:
HardMask(t_i)=0
или:
Viability(t_i) < \tau_{prune}
или:
Budget(t_i)=0
или:
DeadEndMatch(t_i) > \tau_{deadend}

⸻

5. AVF — Attractor Viability Field
AVF — пред-фрактальный слой. Он не решает задачу, а решает, какие ветви имеют право родиться.
5.1. CandidateVector generation
V = CVG(W_t, G, N, DRS, Policy)
Источники:
V = V_{needles} \cup V_{localDRS} \cup V_{externalPointers} \cup V_{fallback}
Инвариант:
V \not\leftarrow freeLLMGeneration
То есть Root/AVF не выдумывает векторы свободной генерацией.

⸻

5.2. CandidateVector
v_i = (id, source, domain, features, branching\_hint, capabilities, history)
Признаки:
x_i =[rel_i,p_i,utility_i,cost_i,risk_i,time_i,conflict_i,gt_i,novelty_i]

⸻

5.3. Feature matrix
Для всех векторов:
X =\begin{bmatrix}x_1 \\x_2 \\... \\x_n\end{bmatrix}\in \mathbb{R}^{n \times d}
где d=9 в базовой версии.

⸻

5.4. Weight vector
w =[\alpha,\beta,\chi,-\delta,-\epsilon,-\zeta,-\eta,\lambda,\rho]
Где:
	•	\alpha — вес релевантности;
	•	\beta — вес вероятности успеха;
	•	\chi — вес полезности;
	•	\delta — штраф стоимости;
	•	\epsilon — штраф риска;
	•	\zeta — штраф времени;
	•	\eta — штраф конфликта;
	•	\lambda — вес GT-прошлого;
	•	\rho — вес новизны.

⸻

5.5. Базовый viability score
VS(v_i)=\alpha rel_i+ \beta p_i+ \chi utility_i- \delta cost_i- \epsilon risk_i- \zeta time_i- \eta conflict_i+ \lambda gt_i+ \rho novelty_i
Матрично:
S=Xw

⸻

5.6. HardMask
HM(v_i) \in \{0,1\}
Если:
v_i \in ForbiddenRegions
то:
HM(v_i)=0
и:
FV(v_i)=0
Пример: насилие, мошенничество, подмена личности, нарушение приватности.

⸻

5.7. SoftMask
SM(v_i) \in [0,1]
SoftMask снижает вес, но не убивает ветку:
SM(v_i)=1 - penalty(v_i)
Где:
penalty(v_i)=a costPenalty+ b riskPenalty+ c stalenessPenalty+ d uncertaintyPenalty

⸻

5.8. Final viability
FV(v_i)=HM(v_i) \cdot SM(v_i) \cdot VS(v_i)

⸻

5.9. Top-K selection
TopK = \operatorname{argtopk}_{v_i \in V}(FV(v_i), k)
Но с учётом exploration:
Selected = TopK_{exploit} \cup TopK_{explore}
Где:
|TopK_{explore}| \leq \epsilon_{explore} \cdot k

⸻

5.10. Exploration budget
\epsilon_{explore} \in [0,1]
Пример:
strict:  0.00
default: 0.05
explore: 0.20
research: 0.30+
creative: 0.40+
Инвариант:
Exploration \not\Rightarrow bypass(HardMask)

⸻

5.11. Cold start
Если:
History(v_i)=\varnothing
то:
history\_confidence = low
Исторический вес:
\lambda H(v_i) \approx 0
Новизна усиливается:
\rho' = \rho + \Delta_{cold}
Тогда:
VS_{cold}(v_i)=\alpha rel_i+ \beta p^{weak}_i+ \chi utility^{estimate}_i- \delta cost_i- \epsilon risk_i+ \rho' novelty_i
AttractorPacket должен включать:
{
  "history_confidence": "low",
  "fallback_to_architect_creativity": true,
  "requires_feedback_writeback": true
}

⸻

5.12. Branch budget allocation
Для каждого вектора:
BB(v_i)=f(FV(v_i), Mode, TotalBudget, ExplorationPolicy)
Пример:
max\_fractals_i =\left\lfloorB_{fractals}\cdot\frac{FV(v_i)}{\sum_j FV(v_j)}\right\rfloor
max\_depth_i =BaseDepth(Mode) + DepthBoost(FV(v_i))

⸻

5.13. AttractorPacket
A_p = (G, W_t, Forbidden, SelectedVectors, BranchBudgets, Time, Instructions)
Architect получает не raw goal, а AttractorPacket.
Инвариант:
ArchitectInput = AttractorPacket

⸻

6. Post V&V
Post V&V проверяет ResultProposal перед GT.
6.1. ResultProposal
r_i = (payload, evidence, cost, risks, time, trace)

⸻

6.2. VV scores
VV(r_i)=[schema_i,evidence_i,policy_i,time_i,safety_i,consistency_i]
Каждый score:
score \in [0,1]

⸻

6.3. Schema score
schema_i =\begin{cases}1, & JSONSchemaValid(r_i)=true \\0, & otherwise\end{cases}

⸻

6.4. Evidence score
evidence_i =\frac{claims\_supported}{claims\_total}
Если нет claims:
evidence_i = 0

⸻

6.5. Time score
time_i =Freshness(r_i) \cdot TimeEnvelopeValid(r_i)
Если нет TimeEnvelope:
time_i=0

⸻

6.6. Policy score
policy_i =1 - violations_i
где:
violations_i \in [0,1]
Если hard violation:
policy_i=0

⸻

6.7. Safety score
safety_i =1 - safety\_risk_i

⸻

6.8. Overall VV score
VVScore(r_i)=a schema_i+ b evidence_i+ c policy_i+ d time_i+ e safety_i+ f consistency_i
где:
a+b+c+d+e+f=1
Если:
schema_i=0
то proposal reject.
Если:
policy_i=0
то proposal reject.

⸻

7. GTValidator
GTValidator стоит после Post V&V и перед Root FinalOutput.
7.1. GT не доказывает истину
Инвариант:
GT \neq TruthProof
GT выбирает устойчивую стратегию по payoff-функции и обновляет рейтинги/TTL.

⸻

7.2. Candidates
C = \{c_1,c_2,...,c_m\}
где c_i — ResultProposal или memory record / patch / UP template.

⸻

7.3. Payoff function
Базовая формула:
Payoff(c_i)=w_1 U_i+ w_2 R_i- w_3 C_i- w_4 V_i+ w_5 Tr_i+ w_6 N_i
Где:
	•	U_i — utility;
	•	R_i — robustness;
	•	C_i — compute/cost;
	•	V_i — violations;
	•	Tr_i — transfer score;
	•	N_i — novelty guard.

⸻

7.4. Utility
U_i =GoalSatisfaction(c_i)
Например:
U_i =\frac{completed\_requirements}{total\_requirements}

⸻

7.5. Robustness
R_i =a evidence_i+ b consistency_i+ c repeatability_i+ d fallback\_support_i

⸻

7.6. Cost
C_i =a tokens_i+ b walltime_i+ c toolcalls_i+ d money_i
Нормализуется в [0,1].

⸻

7.7. Violations
V_i =HardViolation_i+ SoftViolationPenalty_i
Если HardViolation:
V_i=1
и candidate может быть reject независимо от payoff.

⸻

7.8. Transfer score
Tr_i =PotentialCrossDomainUsefulness(c_i)
Для обычного result_selection может быть низкий вес.
Для UP game — высокий.

⸻

7.9. Novelty guard
Novelty полезна только если не нарушает безопасность.
N_i =Novelty_i \cdot (1 - Risk_i)

⸻

7.10. Expected outcome для Elo
Если есть два кандидата i и j:
E_i =\frac{1}{1 + 10^{(R_j - R_i)/400}}
E_j = 1 - E_i

⸻

7.11. Elo update
R'_i = R_i + K(S_i - E_i)
Где:
	•	R_i — рейтинг;
	•	K — коэффициент чувствительности;
	•	S_i — фактический результат;
	•	E_i — ожидаемый результат.
Для победителя:
S_i=1
Для проигравшего:
S_i=0
Для ничьей:
S_i=0.5

⸻

7.12. Regret
Для выбранного кандидата:
Regret(c_i)=Payoff(c^*) - Payoff(c_i)
где:
c^* = \operatorname{argmax}_{c \in C} Payoff(c)
Нормализованный regret:
Regret_{norm} =\frac{Regret}{|Payoff(c^*)| + \epsilon}

⸻

7.13. Dominance
Кандидат a строго доминирует b, если:
\forall k: metric_k(a) \geq metric_k(b)
и:
\exists k: metric_k(a) > metric_k(b)
Если strict dominance найден:
b \rightarrow reject/archive

⸻

7.14. Mixed strategy
Если несколько кандидатов близки:
mix_i =\frac{e^{\tau Payoff_i}}{\sum_j e^{\tau Payoff_j}}
где \tau — sharpness.
При большом \tau почти winner-take-all.
При малом \tau распределение мягкое.

⸻

7.15. Early stopping
Если один кандидат уверенно доминирует:
Payoff(c_1) - Payoff(c_2) > \Delta
и confidence:
Conf(c_1) > \tau_{conf}
то турнир можно остановить.

⸻

8. GT-TTL и эволюция памяти
8.1. Half-life через рейтинг
t_{1/2}(r)=base \cdot\sigma\left(\frac{Elo(r)-\mu}{s}\right)\cdot(1-Regret_{norm}(r))\cdotFreshnessBoost(r)
где:
\sigma(x)=\frac{1}{1+e^{-x}}

⸻

8.2. Decay rate
decay\_rate(r)=\frac{\ln 2}{t_{1/2}(r)}

⸻

8.3. Memory survival score
Survival(r,t)=GTTrust(r)\cdot Freshness(r,t)\cdot ReuseFrequency(r)\cdot UtilityHistory(r)

⸻

8.4. Garbage collection
Запись архивируется, если:
Survival(r,t)<\tau_{archive}
или:
Regret(r)>\tau_{regret}
или:
ConflictWithWork(r)=true
и новый Work имеет более высокий temporal priority.

⸻

8.5. Smart TTL
Полезное знание живёт дольше:
TTL'(r)=TTL(r)\cdot (1+\alpha Utility(r)+\beta Reuse(r)+\gamma EloBoost(r))
Мусор умирает быстрее:
TTL'(r)=TTL(r)\cdot (1-\delta Regret(r)-\epsilon FailureRate(r))

⸻

9. Marennya
Marennya — внутридоменная рефлексия.
9.1. Trigger
Trigger_{M} =Idle\lor AfterTask\lor Staleness\lor FailurePattern\lor GTRegretHigh

⸻

9.2. Input bundle
B_M =Work_{recent}\cup Thoughts_{related}\cup DeadEnds\cup GTFeedback\cup TraceRefs

⸻

9.3. Patch candidate
p = Marennya(B_M)
Типы:
reflection
protocol_patch
validator_patch
dead_end_candidate
heuristic_adjustment

⸻

9.4. Patch utility
U(p)=ExpectedImprovement(p)- Risk(p)- Cost(p)+ Robustness(p)

⸻

9.5. Patch comparison
Патч проходит, если:
U(p') > U(p_{baseline}) + \Delta
или:
RegretReduction(p') > \tau_{regret\_reduction}

⸻

9.6. Marennya quarantine
Инвариант:
MarennyaOutput \rightarrow Quarantine
а не Work.

⸻

9.7. Validation pipeline
Validate_M(p)=Static\land Dedup\land RAG\land SelfConsistency\land Utility\land Safety
Публикация разрешена, если:
Validate_M(p)=true
Тогда:
p \rightarrow Thoughts

⸻

9.8. Marennya GT game
Кандидаты:
C_M = \{baseline, patch_1, patch_2,...\}
Payoff:
Payoff_M(p)=w_1 Utility(p)+ w_2 Robustness(p)- w_3 Risk(p)- w_4 Cost(p)- w_5 HallucinationRisk(p)
Победитель может быть рекомендован к promotion.

⸻

10. UP!
UP! — слой переносов и обобщений.
10.1. Trigger
Trigger_{UP} =AfterTask\lor PatternRepetition\lor HighUtilityThought\lor Idle

⸻

10.2. Input bundle
B_{UP} =Work\cup Thoughts\cup UP_{related}\cup GTFeedback

⸻

10.3. UP candidate types
u \in \{opportunity,protocol\_template,link\}

⸻

10.4. UP energy function
E(u)=\frac{Novelty(u)\cdot ExpectedUtility(u)}{Risk(u)+CostTokens(u)+\epsilon}
где \epsilon защищает от деления на ноль.

⸻

10.5. Transfer score
Transfer(u)=DomainDistance^{-1}\cdot StructuralSimilarity\cdot UtilityEstimate
Можно записать:
Transfer(u)=\alpha Sim_{structure}+ \beta Sim_{constraints}+ \gamma Utility- \delta Risk

⸻

10.6. UP validation
Validate_{UP}(u)=Static\land Dedup\land RAGSupport\land SelfConsistency\land Utility\land Safety
Если:
Validate_{UP}(u)=true
то:
u \rightarrow DRS\_UP
Иначе остаётся в Quarantine или rejected.

⸻

10.7. UP GT game
Кандидаты:
C_{UP} = \{u_1,u_2,...,u_n\}
Payoff:
Payoff_{UP}(u)=w_1 Transfer(u)+ w_2 ExpectedUtility(u)+ w_3 Novelty(u)- w_4 Risk(u)- w_5 Cost(u)
UP по умолчанию non-actionable:
UP(u) \not\Rightarrow ExternalAction

⸻

11. AVF feedback / ViabilityFeedback
После выполнения ветка возвращает обратную связь:
VF(v_i)=(predicted, actual, delta, failure\_modes, gt\_update)

⸻

11.1. Prediction error
Error(v_i)=|PredictedViability(v_i)-ActualUtility(v_i)|

⸻

11.2. Feature correction
Если вектор переоценён:
FV_{future}(v_i) = FV(v_i) - \alpha Error(v_i)
Если недооценён:
FV_{future}(v_i) = FV(v_i) + \beta PositiveSurprise(v_i)

⸻

11.3. DeadEnd promotion
Если ветка провалилась устойчиво:
FailureRate(v_i) > \tau_{fail}
и:
ContextMatch(v_i) > \tau_{context}
то:
v_i \rightarrow DeadEnds

⸻

11.4. Successful protocol promotion
Если:
SuccessRate(v_i) > \tau_{success}
и:
Regret(v_i) < \tau_{regret}
то:
v_i \rightarrow Work/Thoughts
в зависимости от типа записи.

⸻

12. Anti-sycophancy math
12.1. User-origin hypothesis
Если гипотеза пришла от пользователя:
source(v_i)=user
то:
TrustBoost(v_i|source=user)=0
Пока нет внешнего evidence.

⸻

12.2. Evidence requirement
Trust(v_i)=BaseTrust(v_i)+ EvidenceSupport(v_i)+ GTPrior(v_i)- ConflictPenalty(v_i)
Но:
BaseTrust(user\_claim) \not> BaseTrust(system\_claim)

⸻

12.3. Counter-branch requirement
Для спорных гипотез:
If\ Risk(v_i)>\tau\Rightarrow GenerateCounterVector(v_i)
Но counter-vector тоже должен идти через разрешённый источник:
system_template / red_team_needle / DRS conflict record

⸻

13. Continuous / Delta Runtime — будущий слой
Это не MVP-core, но математически фиксируется.
13.1. Состояние мира как поток
W(t)
а не единичный snapshot.

⸻

13.2. Delta update
\Delta W_t = W_t - W_{t-1}
Но “минус” здесь структурный:
\Delta W_t =added \cup removed \cup changed \cup expired

⸻

13.3. Selective activation
Модуль активируется, если:
Relevance(module, \Delta W_t) > \tau_{wake}

⸻

13.4. ActiveNeedleSet
ANS_t =\{ n \in Needles \mid WakeScore(n,\Delta W_t)>\tau \}

⸻

13.5. Delta фрактал
Не пересчитывается весь фрактал:
F_t = Patch(F_{t-1}, \Delta W_t)

⸻

13.6. Scope of recomputation
Scope(\Delta W_t)=\{ nodes \in F \mid depends\_on(nodes, changed\_state)\}

⸻

13.7. Многочастотная модель
Разные контуры могут иметь разные частоты:
L0 reflex:       100 Hz
L1 hot state:    10 Hz
L2 root update:   1 Hz
L3 deep checks:   async / idle
L4 Marennya/UP:   idle / scheduled
Главный инвариант:
100Hz \neq full\_recompute
100 Гц — это частота возможных delta-активаций, а не полного размышления всей ОС.

⸻

14. Аудит и hash-chain
14.1. Content hash
H(r)=SHA256(canonical\_json(r))

⸻

14.2. Hash-chain
Для append-only журнала:
H_i = SHA256(R_i || H_{i-1})
где H_{i-1} — hash предыдущей записи.

⸻

14.3. Audit event
AuditEvent = (kind, payload, timestamp, hash)
Используется для:
	•	DRS append;
	•	registry append;
	•	GT report;
	•	FinalOutput;
	•	Marennya/UP promotion.

⸻

15. Формальный полный pipeline
I \xrightarrow{normalize} G
G \xrightarrow{WorldState} W_t
(W_t, TQ) \xrightarrow{DRS} M
(W_t, M, N) \xrightarrow{CVG} V
V \xrightarrow{AVF} A_p
A_p \xrightarrow{Architect} P
P \xrightarrow{Executors} R
R \xrightarrow{PostV\&V} Q
Q \xrightarrow{GTValidator} GT
(R,Q,GT) \xrightarrow{Root} F
(F,GT,Trace) \xrightarrow{Writeback} DRS
DRS \xrightarrow{Hooks} Marennya/UP

[ПАСПОРТ] [MATH-APPENDIX] [ПОЛНЫЙ-PIPELINE]
Да, похоже, там кусок съехал/не вставился. Вот полный пункт 15 — Формальный полный pipeline целиком.

⸻

15. Формальный полный pipeline
Полный pipeline описывает путь одной задачи от входа пользователя/события до финального ответа, записи опыта в DRS и возможного запуска Marennya / UP.
Главный инвариант:
FinalOutput создаёт только RootOrchestrator.

⸻

15.1. Общая формула pipeline
I \xrightarrow{normalize} G
G \xrightarrow{WorldState} W_t
(W_t, TQ) \xrightarrow{DRS} M
(W_t, M, N) \xrightarrow{CVG} V
V \xrightarrow{AVF} A_p
A_p \xrightarrow{Architect} P
P \xrightarrow{Executors} R
R \xrightarrow{PostV\&V} Q
Q \xrightarrow{GTValidator} GT
(R,Q,GT) \xrightarrow{Root} F
(F,GT,Trace) \xrightarrow{Writeback} DRS
DRS \xrightarrow{Hooks} Marennya/UP
Где:
I   = raw input / event
G   = canonical goal
W_t = WorldState at time t
TQ  = TemporalQuery
M   = memory bundle / DRS retrieval result
N   = installed needles
V   = CandidateVectors
A_p = AttractorPacket
P   = PlanGraph
R   = ResultProposals
Q   = Post V&V reports
GT  = GTValidator report
F   = FinalOutput

⸻

15.2. Step 1 — Input/Event
Входом может быть:
user message
system event
needle event
timer event
external DRS signal
scheduled task
Формально:
I_0 = Input(raw)
Пример:
{
  "raw_input": "Мне нужна справка X",
  "source": "user",
  "session_id": "sess_001"
}

⸻

15.3. Step 2 — Intent normalization
RootOrchestrator нормализует вход в Intent.
G = Normalize(I_0)
Intent содержит:
request_id
raw_input
canonical_goal
domain
constraints
source_of_hypothesis
created_at
Пример:
{
  "intent_id": "intent_001",
  "request_id": "req_001",
  "raw_input": "Мне нужна справка X",
  "canonical_goal": "obtain_certificate_x",
  "domain": "government_certificate",
  "source_of_hypothesis": "user",
  "created_at": "2026-05-21T12:00:00Z"
}
Инвариант:
На этом этапе Root ещё не отвечает пользователю.

⸻

15.4. Step 3 — TemporalQuery construction
Root строит TemporalQuery для любых последующих retrieval.
TQ = BuildTemporalQuery(G, now, mode)
Пример:
{
  "as_of": "2026-05-21T12:00:00Z",
  "time_range": {
    "from": null,
    "to": "2026-05-21T12:00:00Z"
  },
  "freshness_bias": "prefer_recent",
  "max_age_seconds": 2592000
}
Инвариант:
Любой DRS retrieval без TemporalQuery запрещён.

⸻

15.5. Step 4 — WorldState assembly
Root собирает состояние мира:
W_t = AssembleWorldState(G,TQ)
WorldState включает:
time_context
user_context
session_context
local_drs_summary
active_policy
available_needles
recent_trace_refs
Пример:
{
  "world_state_id": "ws_001",
  "request_id": "req_001",
  "intent_id": "intent_001",
  "time_context": {
    "now_utc": "2026-05-21T12:00:00Z",
    "timezone": "Europe/Tirane",
    "freshness_required": "high"
  },
  "temporal_query": {
    "as_of": "2026-05-21T12:00:00Z",
    "freshness_bias": "prefer_recent"
  },
  "active_policy": {
    "mode": "default",
    "allow_external_drs": false,
    "allow_exploration": true
  }
}
Инвариант:
WorldState не должен тащить нерелевантные иголки автоматически.
Например, weather не входит в WorldState, если задача не требует погоды.

⸻

15.6. Step 5 — DRS retrieval / memory-first reuse
Root обращается к Local DRS до генерации плана.
M = DRS.query(G,TQ,layers)
Проверяется возможность reuse:
ReuseScore(r)=aQ(r)+bFreshness(r)+cGTTrust(r)+dSemanticSim(r,G)-eRisk(r)-fConflict(r)
Если:
ReuseScore(r) \geq \tau_{reuse}
и:
PolicyOK(r)=true
тогда возможен reuse:
F = RootFinalFromReuse(r)
Но даже при reuse Root должен проверить свежесть:
validate_freshness = true
Если reuse невозможен, pipeline идёт дальше.
Инвариант:
Memory-first reuse происходит до Architect.

⸻

15.7. Step 6 — CandidateVectorGenerator
Если reuse не сработал, Root запускает генерацию CandidateVectors.
V = CVG(W_t, G, N, DRS, Policy)
Источники CandidateVectors строго ограничены:
installed_needles
local_drs
external_drs_pointers
fallback_exploration_templates
Запрещено:
free LLM hallucination of CandidateVectors
Пример CandidateVectors:
[
  {
    "vector_id": "official_online_request",
    "source": "needle",
    "domain": "government_certificate"
  },
  {
    "vector_id": "personal_visit",
    "source": "needle",
    "domain": "government_certificate"
  },
  {
    "vector_id": "fallback_exploration",
    "source": "fallback",
    "requires_architect_creativity": true
  }
]

⸻

15.8. Step 7 — AVF scoring
AVF оценивает CandidateVectors до Архитектора.
X = FeatureMatrix(V)
S = Xw
FV(v_i)=HardMask(v_i)\cdot SoftMask(v_i)\cdot S(v_i)
HardMask убивает запрещённые ветки:
HM(v_i)=0 \Rightarrow v_i \notin ArchitectInput
Пример:
illegal_coercion → HardMask=0 → не передаётся Архитектору
Выбирается:
Selected = TopK(FV) \cup ExplorationBudget
Инвариант:
AVF не строит план.
AVF строит поле допустимых направлений.

⸻

15.9. Step 8 — AttractorPacket creation
Root формирует AttractorPacket:
A_p = BuildAttractorPacket(G,W_t,SelectedVectors,Budgets,Forbidden,Time)
AttractorPacket содержит:
goal
world_state_ref
time_context
hard_forbidden_regions
candidate_vectors
branch_budget
exploration_budget
architect_instructions
Пример:
{
  "packet_id": "ap_001",
  "goal": {
    "goal_id": "goal_certificate",
    "desired_state": "certificate_obtained"
  },
  "hard_forbidden_regions": [
    "illegal_coercion",
    "fraud",
    "identity_abuse"
  ],
  "candidate_vectors": [
    {
      "vector_id": "official_online_request",
      "final_viability": 0.86,
      "branching_mode": "vertical",
      "branch_budget": {
        "max_fractals": 3,
        "max_depth": 4,
        "parallelism": 1
      }
    }
  ],
  "architect_instructions": {
    "do_not_expand_forbidden_regions": true,
    "must_return_time_assumptions": true,
    "must_return_result_proposals_only": true
  }
}
Инвариант:
Architect получает AttractorPacket, а не raw user text.

⸻

15.10. Step 9 — Architect planning
Architect получает AttractorPacket и строит PlanGraph.
P = Architect(A_p)
PlanGraph:
P=(Nodes,Edges)
Architect обязан вернуть:
plan_id
source_packet_id
time_assumptions
nodes
edges
executor_assignments
Инварианты:
Architect не создаёт FinalOutput.
Architect не отвечает пользователю.
Architect не расширяет forbidden regions.
Architect обязан вернуть time_assumptions.

⸻

15.11. Step 10 — Fractal / DAG execution
ExecutorRunner запускает PlanGraph.
Готовые к выполнению узлы:
Ready(P)=\{n \in Nodes \mid deps(n)\subseteq Completed\}
Параллельность ограничена:
Parallelism \leq branch\_budget.parallelism
Каждый узел исполняется Executor-ом:
r_i = Executor(n_i)
Executor возвращает только ResultProposal.
Инвариант:
Executor не имеет права создавать FinalOutput.

⸻

15.12. Step 11 — ResultProposals
Множество результатов:
R=\{r_1,r_2,\dots,r_m\}
Каждый ResultProposal содержит:
proposal_id
producer
vector_id
plan_id
result_payload
evidence
cost
risks
time_envelope
trace_refs
Пример:
{
  "proposal_id": "rp_001",
  "producer": {
    "executor_id": "exec_001",
    "needle_id": "needle_government_services",
    "model_id": "stub_executor_v1"
  },
  "vector_id": "official_online_request",
  "plan_id": "plan_001",
  "result_payload": {
    "status": "success"
  },
  "evidence": [],
  "cost": {
    "tokens": 0,
    "wall_ms": 12,
    "tool_calls": 1
  },
  "risks": [],
  "time_envelope": {},
  "trace_refs": []
}

⸻

15.13. Step 12 — Post V&V
Post V&V проверяет каждый ResultProposal.
Q = PostVV(R)
Для каждого r_i:
VV(r_i)=(schema_i,evidence_i,policy_i,time_i,safety_i,consistency_i)
И общий score:
VVScore(r_i)=a schema_i+b evidence_i+c policy_i+d time_i+e safety_i+f consistency_i
Если:
schema_i=0
или:
policy_i=0
то:
r_i \rightarrow reject
Инвариант:
Post V&V идёт до GTValidator.

⸻

15.14. Step 13 — GTValidator
GTValidator получает VVReports.
GT = GTValidator(Q)
Кандидаты:
C = \{q_i \in Q \mid q_i.status = accept\}
Payoff:
Payoff(c_i)=w_1 U_i+w_2 R_i-w_3 C_i-w_4 V_i+w_5 Tr_i+w_6 N_i
GT выбирает winner или mix:
winner = argmax(Payoff(c_i))
или:
mix_i =\frac{e^{\tau Payoff_i}}{\sum_j e^{\tau Payoff_j}}
GT обновляет:
Elo
regret
half_life
decay_rate
decision
Elo:
E_i =\frac{1}{1+10^{(R_j-R_i)/400}}
R'_i = R_i + K(S_i-E_i)
Half-life:
t_{1/2}(r)=base \cdot\sigma\left(\frac{Elo(r)-\mu}{s}\right)\cdot(1-Regret_{norm}(r))\cdotFreshnessBoost(r)
Decay:
decay\_rate=\frac{\ln 2}{t_{1/2}}
Инвариант:
GT не доказывает истину.
GT выбирает устойчивый результат по payoff и обновляет память.

⸻

15.15. Step 14 — Root Final Synthesis
Root получает:
(R,Q,GT)
и создаёт:
F = RootFinal(R,Q,GT)
FinalOutput содержит:
final_output_id
request_id
created_by = root_orchestrator
status
answer
used_proposals
gt_report_ref
drs_writes
time_envelope
Инвариант:
created_by == root_orchestrator
Executor / Architect / GTValidator не имеют права создавать FinalOutput.

⸻

15.16. Step 15 — DRS writeback
Root пишет результаты в DRS.
DRS.write(F,GT,Trace)
Создаются записи:
Work record
GT metadata
ViabilityFeedback
DeadEnd record if needed
Trace record if enabled
Каждая запись должна иметь:
TimeEnvelope
provenance
status
layer
type
domain
Если ветка провалилась:
FailureRate(v_i)>\tau\Rightarrow DeadEnd(v_i)
Если ветка успешна:
Success(v_i) \Rightarrow Work/ProtocolCandidate
Инвариант:
DRSRecord без TimeEnvelope запрещён.

⸻

15.17. Step 16 — Marennya hook
После DRS writeback Root может запустить Marennya.
MarennaTrigger =AfterTask\lor Idle\lor FailurePattern\lor HighRegret
Marennya берёт:
recent Work
deadends
gt_reports
trace_refs
viability_feedback
И создаёт:
marenna_reflection
marenna_patch
validator_patch
dead_end_candidate
heuristic_adjustment
Первичная запись:
MarennyaOutput \rightarrow Quarantine
После 6-stage validation:
Quarantine \rightarrow Thoughts
Инвариант:
Marennya не может мутировать Work напрямую.

⸻

15.18. Step 17 — UP hook
UP запускается после задачи или в idle.
UPTrigger =AfterTask\lor PatternRepetition\lor HighUtilityThought\lor Idle
UP берёт:
Work
Thoughts
related UP
GTFeedback
И создаёт:
up_opportunity
up_protocol_template
up_link
Energy:
E(u)=\frac{Novelty(u)\cdot ExpectedUtility(u)}{Risk(u)+CostTokens(u)+\epsilon}
Первичная запись:
UPOutput \rightarrow Quarantine
После validation:
Quarantine \rightarrow UP
Инвариант:
UP не может мутировать Work напрямую.
UP по умолчанию non-actionable.

⸻

15.19. Step 18 — Audit / trace
Каждый значимый переход может писать audit event.
H(r)=SHA256(canonical\_json(r))
Hash-chain:
H_i=SHA256(R_i || H_{i-1})
Audit используется для:
DRS append
registry append
GT report
FinalOutput
Marennya/UP promotion
external DRS pointer publication

⸻

15.20. Полный pipeline в псевдокоде
function process_request(raw_input):

    # 1. Root receives input
    intent = normalize_intent(raw_input)

    # 2. Time
    temporal_query = build_temporal_query(
        as_of = now(),
        intent = intent,
        freshness_bias = choose_freshness(intent)
    )

    # 3. WorldState
    world_state = assemble_world_state(
        intent = intent,
        temporal_query = temporal_query,
        active_policy = current_policy()
    )

    # 4. Memory-first reuse
    memory_bundle = drs.query(
        intent = intent,
        temporal_query = temporal_query,
        layer_filter = ["work", "thoughts", "up", "deadends"]
    )

    reuse_candidate = select_reuse_candidate(memory_bundle)

    if reuse_candidate.score >= TAU_REUSE:
        final_output = root_final_from_reuse(
            intent = intent,
            reuse_candidate = reuse_candidate,
            world_state = world_state
        )

        drs.write(
            layer = "work",
            type = "reuse_outcome",
            content = final_output,
            time_envelope = make_time_envelope()
        )

        return final_output

    # 5. Candidate vectors
    candidate_vectors = candidate_vector_generator(
        intent = intent,
        world_state = world_state,
        installed_needles = load_needles(),
        drs_memory = memory_bundle
    )

    # 6. AVF
    attractor_packet = avf_score_and_build_packet(
        intent = intent,
        world_state = world_state,
        candidate_vectors = candidate_vectors,
        policy = world_state.active_policy
    )

    # 7. Architect
    plan_graph = architect_make_plan(
        attractor_packet = attractor_packet
    )

    assert plan_graph.time_assumptions is not None

    # 8. Executors
    result_proposals = execute_plan_graph(
        plan_graph = plan_graph
    )

    assert all(is_result_proposal(r) for r in result_proposals)
    assert no_executor_final_output(result_proposals)

    # 9. Post V&V
    vv_reports = post_vv_validate(
        result_proposals = result_proposals,
        attractor_packet = attractor_packet
    )

    # 10. GT
    gt_report = gt_validate(
        vv_reports = vv_reports,
        mode = "result_selection"
    )

    # 11. Root final
    final_output = root_synthesize_final_output(
        intent = intent,
        world_state = world_state,
        result_proposals = result_proposals,
        vv_reports = vv_reports,
        gt_report = gt_report
    )

    assert final_output.created_by == "root_orchestrator"

    # 12. DRS writeback
    drs_records = drs_writeback(
        final_output = final_output,
        gt_report = gt_report,
        result_proposals = result_proposals,
        vv_reports = vv_reports,
        trace = collect_trace()
    )

    # 13. Marennya hook
    if policy_allows_marenna(world_state.active_policy):
        marenna_records = marenna_after_task(
            drs_records = drs_records,
            gt_report = gt_report
        )
        write_to_quarantine(marenna_records)

    # 14. UP hook
    if policy_allows_up(world_state.active_policy):
        up_records = up_after_task(
            drs_records = drs_records,
            gt_report = gt_report
        )
        write_to_quarantine(up_records)

    # 15. Return
    return final_output

⸻

15.21. Полный pipeline в компактной строке
Input
→ Intent
→ TemporalQuery
→ WorldState
→ DRS memory-first retrieval
→ reuse? yes → RootFinalFromReuse → DRS writeback
→ reuse? no
→ CandidateVectorGenerator
→ AVF hard/soft scoring
→ AttractorPacket
→ Architect PlanGraph
→ Executor ResultProposals
→ Post V&V
→ GTValidator
→ Root FinalOutput
→ DRS writeback
→ Marennya quarantine hook
→ UP quarantine hook
→ Audit/Trace

⸻
16. Минимальные алгоритмы в псевдокоде
16.1. Root pipeline
function process_request(raw_input):
    intent = normalize_intent(raw_input)

    temporal_query = build_temporal_query(now, intent)
    world_state = assemble_world_state(intent, temporal_query)

    reuse = drs.try_reuse(intent, temporal_query)
    if reuse.score >= tau_reuse:
        return root_final_from_reuse(reuse)

    candidate_vectors = generate_candidate_vectors(
        intent,
        world_state,
        installed_needles,
        drs
    )

    attractor_packet = avf_score(candidate_vectors, world_state.policy)

    plan_graph = architect.make_plan(attractor_packet)

    result_proposals = execute_plan(plan_graph)

    vv_reports = post_vv(result_proposals)

    gt_report = gt_validate(vv_reports)

    final_output = root_synthesize(result_proposals, vv_reports, gt_report)

    drs.write(final_output, gt_report, traces)

    marenna_hook_if_allowed()
    up_hook_if_allowed()

    return final_output

⸻

16.2. AVF algorithm
function avf_score(candidate_vectors, policy):
    X = feature_matrix(candidate_vectors)
    w = mode_weights(policy.mode)

    raw_scores = X @ w

    hard_mask = compute_hard_mask(candidate_vectors, policy)
    soft_mask = compute_soft_mask(candidate_vectors, policy)

    final_scores = raw_scores * hard_mask * soft_mask

    exploit = top_k(final_scores)
    explore = select_exploration(candidate_vectors, policy.epsilon)

    selected = exploit ∪ explore

    return build_attractor_packet(selected)

⸻

16.3. DRS retrieval
function drs_query(intent, temporal_query, layer_filter):
    assert temporal_query is not None

    candidates = load_records(layer_filter)

    candidates = filter_by_time(candidates, temporal_query)
    candidates = filter_by_domain(candidates, intent.domain)
    candidates = score_semantic_similarity(candidates, intent)

    candidates = apply_gt_ttl_decay(candidates)
    candidates = sort_by_reuse_score(candidates)

    return top(candidates)

⸻

16.4. GT validation
function gt_validate(vv_reports):
    candidates = accepted(vv_reports)

    if candidates empty:
        return decision="rerun" or "needs_user"

    for c in candidates:
        payoff[c] = compute_payoff(c)

    winner = argmax(payoff)

    ratings = update_elo(candidates, winner)
    regrets = compute_regret(candidates, payoff)
    half_life = compute_half_life(ratings, regrets)

    return GTReport(winner, ratings, regrets, half_life)

⸻

16.5. Marennya
function marenna_tick(trigger):
    bundle = collect_recent_work_thoughts_gt_deadends()

    drafts = generate_reflection_candidates(bundle)

    for draft in drafts:
        write_to_quarantine(draft)

    for draft in drafts:
        if validate_6_stage(draft):
            promote_to_thoughts(draft)

⸻

16.6. UP
function up_tick(trigger):
    bundle = collect_work_thoughts_up()

    candidates = generate_transfer_candidates(bundle)

    for u in candidates:
        u.energy = novelty * expected_utility / (risk + cost + eps)
        write_to_quarantine(u)

    for u in candidates:
        if validate_6_stage(u):
            promote_to_up(u)

⸻

17. Что обязательно перенести в новую ветку
Для Codex / Antigravity этот документ должен лечь как:
specs/math_appendix_v0_3.md
И рядом должны быть:
AGENTS.md
specs/machine_manifest_v0_25.json
schemas/*.schema.json
specs/legacy_mapping.md
В AGENTS.md не надо вставлять весь этот appendix целиком. Там достаточно ссылки:
For formulas and algorithms, read specs/math_appendix_v0_3.md.

⸻

18. Финальный статус
Теперь можно сказать:
v0.25
Инженерный паспорт MVP.
Machine Manifest v0.25
Машинная карта системы.
JSON Schemas v0.25
Контракты объектов.
Math Appendix v0.3-draft
Формулы и алгоритмы:
	•	Time;
	•	DRS;
	•	fractalization;
	•	AVF;
	•	Post V&V;
	•	GT;
	•	GT-TTL;
	•	Marennya;
	•	UP;
	•	continuous runtime;
	•	audit/hash-chain.
Это уже достаточно, чтобы в новой ветке не потерять математику проекта. ]
