# Round 2 — GraphQL queries & mutations that don't check roles

Scope: every `Query`/`Mutation` resolver exposed by the ~32 GraphQL schemas in
`backend-packages/`. Round 1 covered FHIR (`api_fhir_r4`) and row-security
scoping (the `scoped` commits). This round is **RBAC only**: does a role check
actually fire before the resolver touches data?

Method: AST walk of every resolver and every mutation class reachable from a
`Mutation` ObjectType, resolving each mutation's inheritance chain across files
and following the permission-helper wrappers (`PermissionValidation.validate_perms`,
`_check_permissions`, service-layer `has_perms`, …). Comments were stripped before
matching — a commented-out `has_perms` is not a check. Every finding below was
then read in the source and confirmed by hand.

**No global auth gate exists.** `OpenIMISGraphQLView` (`openIMIS/openIMIS/views.py:192`)
adds only Sentry reporting, and the configured graphene middleware
(`settings/base.py:271-275`) *resolves* the JWT user but never requires one. So a
resolver with no check at all is reachable **unauthenticated**, not merely by any
logged-in user. This distinction drives the severities below.

Baseline for the "vacuous check" class: `has_perms` returns `True` for an empty
permission list, by design — `core/core/models/user.py:809-810`:
`if not perm_list and not access_requirements: return True`.

Counts: 232 exposed mutations, 191 root-query resolvers scanned.

---

## CRITICAL — no check of any kind, reachable unauthenticated

- [x] **`paymentGatewayConfig` returns a live credential to anyone.** *(fixed 2026-09-30 as C2, payroll 1.0.1)*
  `payroll/payroll/schema.py:267` — no role check, no auth check; returns
  `PayrollConfig.payment_gateway_api_key` verbatim.
  *(= C2 in `access_control_audit.md`, confirmed still open.)*

- [x] **`billPayment` — permission helper defined but never called.** *(fixed: `resolve_bill_payment` calls `_check_permissions`, right 156201; verified 2026-10-06. Row scoping is C9 / N03 in `access_control_audit.md`.)*
  `invoice/invoice/gql/bill_payment/query.py:23`. `_check_permissions` exists at
  `:40` and nothing calls it; its sibling `invoiceLineItem`
  (`invoice/.../invoice_line_item/query.py:24`) *does* call its own. Compounded:
  `InvoiceConfig.bill_user_filter` defaults to `None`, and
  `BillPaymentGQLType.get_queryset` is dead code (see Systemic #1) — so this query
  has no role check, no scoping and no auth on financial records.

- [x] **`workflow` — permission helper defined but never called.** *(fixed: `resolve_workflow` calls `_check_permissions` with `gql_workflow_search_perms`, right 210001; verified 2026-10-06)*
  `workflow/workflow/schema.py:17`; `_check_permissions` at `:28` is unreferenced.
  Exposes the workflow inventory (names/groups) to anonymous callers.

- [x] **`taskGroup` has no check and no scoping.** *(right fixed: `resolve_task_group` checks `gql_task_group_search_perms`, right 190001; verified 2026-10-06. `TaskGroupGQLType` still has no row scope.)*
  `tasks_management/tasks_management/schema.py:135`. `TaskGroupGQLType`
  (`gql_queries.py:163`) is the only task GQLType with neither a `get_queryset`
  nor `ScopedQuerysetMixin`, while the sibling `taskExecutor` resolver *does*
  check `gql_task_group_search_perms` (`schema.py:166`).
  *(C4 partially: `resolve_task`/`resolve_task_history`/`ResolveTaskMutation` are
  now genuinely fixed — see "Already fixed" below. `taskGroup` was missed.)*

## HIGH — the check runs but is vacuous (`has_perms([])` → `True`)

Each of these calls `has_perms` with a constant whose `DEFAULT_CFG` value is `[]`,
so it passes for every caller, authenticated or not, unless a deployment happens
to have configured that right via `ModuleConfiguration`.

- [ ] **`claimOfficers`, `fspFromClaim`, `claimWithSameDiagnosis`** —
  `claim/claim/schema.py:234`, `:248`, `:261` — all three use
  `ClaimConfig.gql_query_claim_officers_perms`, `[]` at `claim/claim/apps.py:8`.
  Leaks enrolment-officer PII, and `claimWithSameDiagnosis`/`fspFromClaim` take a
  CHFID + ICD code and return that insuree's claim history / facility.
- [ ] **`insureeOfficers`** — `insuree/insuree/schema.py:347`;
  `gql_query_insuree_officers_perms` `[]` at `insuree/insuree/apps.py:13`.
- [ ] **`policyOfficers`** — `policy/policy/schema.py:351`;
  `gql_query_policy_officers_perms` `[]` at `policy/policy/apps.py:17`.
- [ ] **`diagnosesStr`** — `medical/medical/schema.py:91`;
  `gql_query_diagnosis_perms` `[]` at `medical/medical/apps.py:6`.
- [ ] **`relativeIndexes`** — `claim_batch/claim_batch/schema.py:210`;
  `gql_query_relative_indexes_perms` `[]` at `claim_batch/claim_batch/apps.py:7`.

## HIGH — the check is commented out or conditionally disabled

- [ ] **`createClaimSamplingBatch` — role check commented out.**
  `claim_sampling/claim_sampling/gql_mutations.py:93-94`; only the
  anonymous-user check at `:91-92` is live.
- [ ] **RBAC coupled to `ROW_SECURITY` — the check itself stops firing.**
  Pattern is `if not user.has_perms(...) and settings.ROW_SECURITY: raise`, so on a
  deployment with `ROW_SECURITY=False` the permission denial never happens:
  - `claim/claim/schema.py:137-141` (`claim`), `:154-158` (`claims`), `:277-281`
  - `claim_sampling/claim_sampling/schema.py:41-45`, `:52-56`, `:63-67`
    (`claimSamplingBatch`, `claimSamplingBatchAssignment`, `samplingBatchClaims`)

## HIGH — write mutations gated on authentication only

These inherit a base mixin whose `_validate_mutation` checks *only* that the user
is not anonymous (`core/core/gql/gql_mutations/base_mutation.py:189-191`, `:219-221`,
`:254-260`) and never override it with a role check.

- [ ] **`moveFamiliesToParentMutation`** — `insuree/insuree/gql_mutations.py:327`.
  Re-parents any family by client-supplied UUID (`Family.objects.filter(uuid=…)`,
  unscoped) and can cancel that family's policies via `cancel_policies`. Note
  `insuree/insuree/services.py` contains **zero** `has_perms` — there is no
  service-layer backstop.
- [ ] **`deleteFamiliesFromParentMutation`** — `insuree/insuree/gql_mutations.py:390`. Same.
- [ ] **`createContractDetails` / `updateContractDetails` / `deleteContractDetails`** —
  `contract/contract/gql/gql_mutations/contract_details_mutations.py:20`, `:42`, `:51`.
  No `_validate_mutation` override. Contrast the main contract mutations, which
  *are* checked inside `contract/contract/services.py`
  (`Contract.create/update/submit/approve/counter/amend/renew/delete`).
- [ ] **`createContractDetailsByPhInsuree`** —
  `contract/contract/gql/gql_mutations/mutations.py:280`
  (`ContractDetailsFromPHInsureeMutationMixin`, auth-only at `:287-289`); its
  service method `ContractDetails.get_details_from_ph_insuree`
  (`services.py:747`) has no check either.
- [ ] **`createContractInvoiceBulk`** —
  `contract/contract/gql/gql_mutations/mutations.py:347`
  (`ContractCreateInvoiceMutationMixin`, auth-only at `:354-356`);
  `ContractToInvoiceService.create_invoice` (`services.py:1034`) has no check.

## MEDIUM — authenticated, but any role

- [ ] **form_builder: `formDefinition`, `formSubmission`, `formControlsSchema`** —
  `openimis-be-form_builder_py/form_builder/schema.py:42`, `:50`, `:55`. Auth only.
  The module *defines* `gql_form_definition_viewer_perms` (151002) and
  `gql_form_submission_viewer_perms` (151004) at `apps.py:12`,`:18` and never uses
  them. `FormSubmission.data` is the raw submitted answers.
- [ ] **`healthFacilitiesStr`** — `location/location/schema.py:152`. Auth only, and
  the client-supplied `ignoreLocation: true` disables district scoping outright
  (`:170`), with no role required to pass it.
- [ ] **`customFilters`** — `core/core/schema.py:1451`. Auth only; takes
  client-supplied `module_name` / `object_type_name` / `uuid_of_object`.
- [ ] **`paymentMethods`** — `payroll/payroll/schema.py:258`. Auth only.

## LOW — no check; confirm whether intentional

- [ ] `passwordPolicy` `core/core/schema.py:1078` and `maxLengthConstraints` `:1101`
  — no check at all. Plausibly needed pre-login, but `passwordPolicy` discloses the
  exact password rules to an anonymous caller.
- [ ] `moduleConfigurations` `core/core/schema.py:1506` — no check; the only guard
  is the `is_exposed=True` data flag and a code comment warning not to store
  credentials in exposed config. Relies entirely on data hygiene.
- [ ] `validateContributionPlanCode` / `validateContributionPlanBundleCode` /
  `validatePaymentPlanCode` — `contribution_plan/contribution_plan/schema.py:178`,
  `:182`, `:186`. No auth; a code-existence oracle. The equivalent validators in
  core and claim (`core/core/schema.py:1087`, `claim/claim/schema.py:131`) do
  require a query right — these are the inconsistent ones.
- [ ] `controlStr` / `control` — `controls/controls/schema.py:17`.
- [ ] `globalSchema` — `individual/individual/schema.py:463` (returns the configured
  individual schema; `_check_permissions` exists in the same class and isn't used here).
- [ ] `userDistricts` `location/location/schema.py:179`,
  `healthFacilityLegalForms` `:191`, `healthFacilitySubLevels` `:196` — auth only,
  reference data / caller's own districts.

## Verified intentional — no action, listed so they aren't re-flagged

- `locations`, `locationsAll`, `locationsStr` — `location/location/schema.py:128`,
  `:134`, `:139`: permission check deliberately commented with an **OMT-281**
  reference ("allow querying to anyone, with limitations in the get_queryset").
  `locationsStr` does route through `Location.get_queryset`; `locationsAll` does not.
- `medicalItemsStr`, `medicalItems`, `medicalServicesStr`, `medicalServices` —
  `medical/medical/schema.py:102`, `:116`, `:144`, `:160`: same OMT-281 exemption.
- Core auth/self-service mutations — `tokenAuth`, `logout`, `getCsrfToken`,
  `resetPassword` (`schema.py:2257`), `setPassword` (`:2284`, gated by an emailed
  token + `check_lockout`), `changeUserLanguage`, `changeUserDefaultRowsPerPage`,
  and `changePassword` (`:2213`) — the last is properly checked in
  `core/core/services/userServices.py:261-266`, which requires
  `gql_mutation_update_users_perms` to change *another* user's password.

## Systemic

1. [ ] **13 GQLTypes define `get_queryset` nested inside `class Meta`, where
   graphene never calls it** — dead scoping code, and it makes these types *look*
   protected in review. All of `invoice` (10) and `contract` (3):
   `invoice/invoice/gql/gql_types/invoice_types.py:15,82,122,138`,
   `bill_types.py:15,80,120,136`, `payment_types.py:17,33`,
   `contract/contract/gql/gql_types.py:22,85,111`.
   This is the concrete root cause behind audit finding C9's "row security is a
   documented no-op for the whole module".
2. [ ] **9 more permission constants default to `[]` but are currently referenced
   nowhere** — harmless today, a trap the moment someone wires them up:
   `medical_pricelist.gql_query_pricelists_perms`,
   `contract.gql_query_contract_admins_perms`,
   `policyholder.gql_query_policyholder{,insuree,user,contributionplanbundle}_admins_perms`,
   `contribution_plan.gql_query_{contributionplan,contributionplanbundle,paymentplan}_admins_perms`.
   Consider making `has_perms([])` fail closed, or asserting non-empty at config load.
3. [ ] **Helper-defined-but-never-called is a recurring shape** (`billPayment`,
   `workflow`, and `globalSchema` in its class). Cheap lint: a `_check_permissions`
   / `_have_permissions` staticmethod in a Query class with zero call sites.

---

## Already fixed — audit items that are now stale

Re-verified against current source; `access_control_audit.md` still lists these as open:

- **C3 `claimAdmins`** — now checks `CoreConfig.gql_query_claim_administrator_perms`
  (default `["121601"]`) at `core/core/schema.py:1017`, with a documented
  self-link fallback so a claim admin can still resolve their own record. The
  broken `from locations.models import` typo and the bare `except` are gone.
- **C4, partly** — `TaskGQLType.get_queryset` / `TaskHistoryGQLType.get_queryset`
  (`tasks_management/tasks_management/gql_queries.py:88`, `:152`) now really do
  scope to the caller's task groups, so the "not checking perms because
  get_queryset filters" comments at `schema.py:91`,`:117` are now accurate.
  `ResolveTaskMutation` (`gql_mutations.py:339`) now has a real
  `_validate_mutation` requiring executor membership or triage rights.
  `taskDecision` is scoped via `TaskDecisionGQLType.get_queryset` (`:330`).
  **Still open from C4: `taskGroup`** (see CRITICAL above).
- **`invoiceLineItem`** — does call `_check_invoice_permissions`
  (`invoice/.../invoice_line_item/query.py:24`). Only `billPayment` forgets.

## Suggested fix order

1. `paymentGatewayConfig` — credential exposure, one-line fix.
2. `billPayment`, `workflow` — call the helper that is already written.
3. `taskGroup` — add the check its sibling `taskExecutor` already has.
4. The five vacuous `[]` constants — assign real right IDs in each `apps.py`.
5. `createClaimSamplingBatch` (uncomment) and the `ROW_SECURITY` conditionals
   (split the RBAC check out of the row-security condition).
6. The insuree family-move and contract-details write mutations.
7. form_builder — wire up the viewer perms it already defines.
8. Systemic #1 (move `get_queryset` out of `Meta`) — overlaps round 1's scoping work.
