# Testflix V09: результат для независимой проверки

Controlled P01-P06/N01-N20 и продолжение после renewal завершены. Настоящие
E700/E600, их supplied D/E consumers, новая Root review и native consumption
проверены на фактических возвратах. Live main и captured-handler завершены.
Live A/B: TWO_GOOGLE_504_THEN_READ_TIMEOUT; positive consumption NOT_COMPLETED.
Это внешний candidate, не owner landing и не самостоятельно присвоенная приёмка.

## Что исправлено

Чистые области существующего Host reuse теперь охватывают связанные D/E проверки
и чистое D4 cell execution. V08 Host, actual/saved origin, currentness, mutation
и exception cleanup сохранены. Нет общего scope вокруг handler, LLM или эффекта.
На каждом Bank E: 15342 обращения scope, 32 полные проверки material, 46 входов
registry core; unsupported=0. Счётчики вложенных функций не складываются как CPU-доли.

После ускорения обнаружены и исправлены конкретные domain consumers: сравнение
binding artifact ID с отличным context ID; неверное Root hard-failure vocabulary;
экспорт повторных stored bytes и executable admission callback. Все первичные
отказы/traceback сохранены. Historical bytes, actual work refs и обязательные
проверки не заменены общим PASS или заранее выбранным результатом.

## Фактическое исполнение

| Фаза | Секунды | Результат |
|---|---:|---|
| Bank E700 / E600 | 317.991 / 318.910 | Оба E PASS; Root700 отказ, Root600 ACCEPT |
| Canonical D700 / D600 | 16.792 / 16.876 | PASS на тех же живых возвратах |
| Supplied D700 / E700 | 14.620 / 17.005 | PASS |
| Supplied D600 / E600 | 14.697 / 17.108 | PASS |
| Controlled continuing: 10 тестов / 30 фаз | 3626.874 | Все SETUP/CALL/TEARDOWN PASS |
| Остальная scoped выборка: 57 тестов / 171 фаза | 1568.543 | Все фазы PASS |
| Live main / captured handler | 1174.812 / 1124.976 | PASS |
| Live A/B | 180.616 | Provider failure; no claimed action |
| Сумма latency всех model responses | 91.544 | Не время всего runtime |

Canonical E700: 19664988 bytes, SHA256
`9bb1508379324b80f3474c1c77b04eef697a2edc5aac5f0623822db8b2d3cd18`,
BYTE_IDENTICAL с source-bound recorded bank_story_03. Closed D schemas проверены
только локальными reference resources, включая unknown-key refusals.

Основная история сохраняет четыре Host и два mock-платежа. 500 и 600 positive
branches изолированы; 700 при consent650 не даёт дополнительного main payment.
N15 coherent mutations отказываются, правильные эквивалентные inputs проходят.

## Live и captured

Использована существующая `gemini-2.5-flash`, модель/аккаунт не менялись.
18 фактических попыток: main9, A/B9; ответов 15.
Транспортные незавершённые попытки: {'google.genai.errors.ServerError': 2, 'httpx.ReadTimeout': 1}.
Из ответов 13 принятых role outputs, один реальный missing-evidence refusal
и один A/B review refusal до D/effects. Первоначальная проекция
не называла предметный finite task и minor currency units. Она уточнена; старый
отказ остаётся отказом и отдельно воспроизведён тестом. Нет автоматического retry
или controlled fallback. Подробности: `live_input_contract_repair.md`.

Четыре разные роли потребляют предыдущие ответы и локальные capture refs.
Первый A/B закончился реальным разногласием ролей. Владелец разрешил дополнительные
запросы; уточнён общий QUALITY input contract, предикаты отказа не ослаблены.
Два новых ответа intent/terms сохранены, но selector получил два Google504,
затем httpx.ReadTimeout после увеличения server/client deadline до180с.
Проверены публичный input-bound resume и SDK server-deadline; результат не выдуман.
Положительное A/B-потребление НЕ завершено, точные транспортные ошибки сохранены.
Raw responses, usage, input projections и фактические Root inputs сохранены;
Bank/User private canaries не передавались в модель или чужую Root-проекцию.

Captured-handler использует новые настоящие Hosts, 0 model calls и выполняет
собственные mock effects. Все остальные поля/IDs/times истории совпадают точно;
различаются только четыре mode fields LIVE_CAPTURED -> CAPTURED_REEXECUTION.
Отдельный offline replay имеет 0 provider/effect calls и не выдаёт current permission.

## Граница покрытия и внесение

70 уникальных domain test IDs покрыты завершёнными выбранными receipts;
дополнительно четыре common scope/origin/mutation nodes. Изменённая distinct-role
граница проверена свежими 21 коротким тестом. Legacy controlled receipts
сохраняют собственные hashes; source-impact bridge не выдаётся за новый runtime.
Полный Living/Conformance/Gate и generic retained/granular приёмка на новых
common bytes не перезапускались. Нужен независимый cumulative review/admission.

Полная live история заняла около 19.6 минуты: native
history checks остаются существенной стоимостью. Это не мгновенная демонстрация
и не обещание универсального ускорения. Новый informational summary обновлённого
периода по-прежнему явно unsupported. Catalog/time controlled, эффекты mocks,
реальны model transport, локальные Root/contracts и evidence chain; это не OS
monitoring, external clock/provider attestation или production certification.

`demo/story.html` открывается офлайн; `demo/story.json` содержит actual story.
Desktop/mobile QA и раскрытие evidence проверены. `owner_apply/` содержит
35 cumulative postimages относительно L и 15 изменений V09
относительно V08, exact pins и read-only `git apply --check`. Ничего не применено.
Owner metadata/index/refs/status и сохранённые V08/original pins/barrier совпадают.

Неудачные/остановленные команды сохранены, не превращены в PASS:
`bank_story_01, bank_story_02, bank_story_03, bank_story_04, bank_story_05, observer_probe_03, live_main_01, semantic_scope_controls_02, live_AB_01, live_AB_02, live_AB_03, live_AB_04, live_AB_05`. Итоговые receipts/raw streams и точные node phases:
`coverage.json`, `commands/`; все test/runtime processes завершены и reap выполнен.

COMMIT=false; PUSH=false; FULL_TESTFLIX_ACCEPTANCE=NOT_SELF_AWARDED.
Следующий незакрытый шаг: получение завершённого provider suffix для live A/B и его actual consumption; разрешение владельца уже дано.
Затем окончательная независимая проверка/admission coverage и решение владельца о landing.
