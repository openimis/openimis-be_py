# openIMIS backend — FHIR & GraphQL access-control audit checklist

Audit of `backend-packages/` covering the FHIR R4 REST API (`api_fhir_r4`) and
all GraphQL `schema.py` files across ~31 module packages. Two questions were
asked of every endpoint:

1. Does it fetch its primary data via a location/facility-scoped path
   (`Model.get_queryset(qs, user)` or equivalent), or via a raw
   `Model.objects.…` call that skips that restriction?
2. Is `user.has_perms(...)` checked, checked with the *right* constant, and
   checked *before* data is touched?

**Last re-verified against the code: 2026-09-28.** File:line references are
from that pass and are relative to `backend-packages/<pkg>/...`; re-check them
before editing, since the tree moves.

## How to use this list

- Every issue has a **stable ID** (`C2`, `H05`, `N01`, …). IDs are never
  renumbered or reused. A fixed issue keeps its ID and is ticked.
- Status: `[x]` **Fixed**, `[ ]` **Open**, or `[ ]` **Partial** (some of it fixed,
  the rest still open, as the item describes).
- Prefixes: `C` critical, `H` high, `M` medium, `L` low/informational,
  `S` systemic (fix once, not per instance), `N` new, found during the
  2026-09-28 re-verification.
- When you fix an issue, tick it, add *(fixed: …)* with the commit or PR and the
  test that pins it, and update the index row.

---

## Index

| ID | Sev | Module | Issue | Status |
|----|-----|--------|-------|--------|
| C1 | Critical | api_fhir_r4 | Contract/Coverage write endpoints had empty permissions | Fixed |
| C2 | Critical | payroll | `paymentGatewayConfig` returns the gateway API key with no check | Fixed |
| C3 | Critical | core | `claimAdmins` not location-scoped; empty-HF fallthrough | Fixed |
| C4 | Critical | tasks_management | `task` / `taskHistory` have no action-level permission check | Fixed |
| C5 | Critical | grievance_social_protection | Comment access not tied to the ticket | Fixed |
| C6 | Critical | claim | `claim` (singular) and `claimAttachments` are unscoped IDORs | Fixed |
| C7 | Critical | policyholder | Portal queries leak every policy holder's data | Fixed |
| C8 | Critical | contract | Contract queries leak every company's contracts | Fixed |
| C9 | Critical | invoice | Invoice/Bill row security was a no-op | Fixed |
| H01 | High | individual | `individualDataSourceUpload` unscoped | Fixed |
| H02 | High | insuree | Insuree/Family write mutations have no location authorization | Fixed |
| H03 | High | insuree | `UpdateInsureeMutation` checked the create right | Fixed |
| H04 | High | location | `healthFacilitiesStr`: no `has_perms`, `ignoreLocation` disables scoping | Open |
| H05 | High | claim, claim_sampling | Permission checks conditional on `settings.ROW_SECURITY` | Fixed |
| H06 | High | claim | `claimHistory` bypasses facility filtering | Fixed |
| H07 | High | claim | Claim workflow mutations act on unscoped UUIDs | Fixed |
| H08 | High | claim_sampling | `CreateClaimSamplingBatchMutation` permission check commented out | Fixed |
| H09 | High | policy | `policyRenewals` shares its right ID with the renew mutation | Partial |
| H10 | High | policy | `policyValues` unscoped `Policy`/`Family` lookups | Open |
| H11 | High | api_fhir_r4 | FHIR Group listing bypassed district scoping | Fixed |
| H12 | High | api_fhir_r4 | FHIR Communication listing bypassed district scoping | Fixed |
| H13 | High | api_fhir_r4 | FHIR ClaimAdmin listing: empty permission and unscoped | Fixed |
| H14 | High | api_fhir_r4 | FHIR Organisation listing unscoped | Fixed |
| H15 | High | api_fhir_r4 | FHIR Enrolment-officer listing: empty permission | Fixed |
| H16 | High | report | `report` / `definition` skip the per-report permission | Open |
| H17 | High | payer | `payer` (singular) unscoped | Open |
| H18 | High | payment | `payment` module has no location scoping | Open |
| H19 | High | form_builder | Viewer rights never checked | Fixed |
| H20 | High | payroll | Money-moving mutations gated by the wrong rights | Fixed |
| H21 | High | core | Shared update/delete mutation mixins look up targets unscoped | Fixed |
| M01 | Medium | api_fhir_r4 | `CoverageEligibilityRequest` POST lacked the eligibility right | Fixed |
| M02 | Medium | api_fhir_r4 | Invoice/Bill/PaymentNotice viewsets bypassed `get_queryset` | Fixed |
| M03 | Medium | contribution | `premiumsByPolicies` resolves client UUIDs unscoped | Open |
| M04 | Medium | product | `product` (singular, by uuid) unscoped | Open |
| M05 | Medium | calculation | `calculationParams` fetches any model by client-supplied name | Open |
| M06 | Medium | claim_sampling | Sampling batch / assignment unscoped | Open |
| M07 | Medium | claim_batch | `BatchRun` has no location scoping | Open |
| M08 | Medium | insuree | `insureeOfficers` right defaulted to `[]` | Fixed |
| M09 | Medium | insuree | `canAddInsuree` unscoped `Family.objects.get` | Open |
| M10 | Medium | social_protection | `resolve_awaiting_beneficiary` skips scoping (dead code) | Open |
| M11 | Medium | payroll, social_protection | `project` / `paymentPoint` scoped only when `parentLocation` given | Fixed |
| M12 | Medium | payer | `Payer.get_queryset` discards the incoming queryset | Open |
| L01 | Low | api_fhir_r4 | No-op `self.base_class` / incompatible `get_queryset` call | Fixed |
| L02 | Low | payment_cycle | `wait_for_mutation` runs before the permission check | Open |
| L03 | Low | location | `officerLocations` discloses any officer's locations | Open |
| L04 | Low | location | `locationsAll` bypasses district scoping | Fixed |
| L05 | Low | controls | `controlStr` has no permission check | Fixed |
| L06 | Low | tasks_management, payroll, claim_sampling | Dead / unimplemented resolvers | Partial |
| S1 | Systemic | all | Permission constants still at their `[]` default | Partial |
| S2 | Systemic | all | Scoped-list / unscoped-singular pairs | Open |
| S3 | Systemic | core | Thread row scoping through the shared mutation mixins | Fixed |
| S4 | Systemic | all | `has_perms(...) and settings.ROW_SECURITY` conditionals | Fixed |
| N01 | Critical | contract | GQL type `get_queryset` indented inside `class Meta`, never called | Fixed |
| N02 | High | policy | `Policy.get_queryset` only blocks anonymous users | Fixed |
| N03 | Medium | invoice | Invoice/Bill child models declare no `row_scope` | Open |
| N04 | Medium | form_builder | `FormSubmissionGQLType.get_queryset` discards the queryset | Open |
| N05 | Medium | claim_sampling | `samplingSummary` has no permission check | Fixed |
| N06 | Medium | core | `Officer.get_queryset` performs no location filtering | Open |
| N07 | Low | assembly | `script/scan_unscoped.py` undercounts | Open |

**Totals (59 issues):** 23 fixed, 5 partial, 31 open (of which 7 are the new `N` items).

---

## CRITICAL

- [x] **C1 — FHIR `Contract`/`Coverage` write endpoints have empty permissions.** *(fixed in `backend-packages/api_fhir_r4`)*
  `api_fhir_r4/api_fhir_r4/permissions.py` (`FHIRApiCoverageRequestPermissions`)
  set `permissions_post/put/patch/delete = []`, used by `views/fhir/contract.py`
  and `views/fhir/coverage_request.py`. Both viewsets write real policies.
  *Fix:* `permissions_post/put/patch/delete` now use `gql_mutation_create/edit/edit/delete_policies_perms`.

- [x] **C2 — `payroll.paymentGatewayConfig` returns a live API key with no auth check.** *(fixed 2026-09-30, payroll 1.0.1)*
  `resolve_payment_gateway_config` (`payroll/payroll/schema.py`) had no
  `has_perms` and no `is_authenticated` check, and returned
  `PayrollConfig.payment_gateway_api_key` verbatim. (It also crashed, because it
  read the nonexistent `PayrollConfig.payment_gateway_base_url`.)
  *Fix:* payroll's rights are declared with `RightsDeclaration`
  (`payroll/payroll/apps.py`), with the ids unchanged; the declaration in place is
  the one from `feature/security`, merged into `release/26.10` on 2026-10-01, which
  superseded the first version of this fix (`e6c0f47`). The action
  `paymentGatewayConfig.query` is right 202005, under the config key
  `gql_payment_gateway_config_perms`. The resolver refuses anonymous users and
  anything failing `require(user, "paymentGatewayConfig", "query")` (`9e0b861`),
  and it reads `gateway_base_url`. By decision, `apiKey` is still returned to users
  who hold the right. No other payroll right grants it.
  *Grant:* `backend/fixtures/demo/core/rights-system-admin.json` (LOCAL
  Administrator). No migration.
  *Test:* `payroll/payroll/tests/test_payment_gateway_config.py`: a user holding
  every payroll right except this one is refused; a user holding it gets
  `baseUrl`/`apiKey`/`timeout`.

- [x] **C3 — `claimAdmins` is not location-scoped.** *(fixed 2026-09-30)*
  *Fixed earlier:* gated by `gql_query_claim_administrator_perms =
  RIGHTS.perms("claimAdministrator", "query")` (no longer `[]`). A user without
  that right sees only their own ClaimAdmin.
  *Fixed in this change:*
  - `ClaimAdmin.row_scope = ParentScope("health_facility", allow_null=True)`
    (`core/core/models/user.py`) replaces the hand-written location filter.
    `ClaimAdmin.get_queryset` keeps only the validity filter and the `None` →
    all-rows convention used by FHIR, then hands on to `super()`.
    HealthFacility scopes itself in code, so this restricts through
    `HealthFacility.get_queryset`.
  - `ClaimAdminGQLType` uses `ScopedQuerysetMixin` instead of a validity-only
    hook.
  - `resolve_claim_admins` (`core/core/schema.py`) returns
    `ClaimAdmin.get_queryset(...)`. `districtUuid`/`regionUuid` now only narrow
    that result. The `try/except Exception`, and the `if user_health_facility:`
    fallthrough that gave **every** claim admin to a user whose districts hold no
    health facility, are gone.
  - FHIR `Practitioner`/`PractitionerRole` (H13) inherit the same scope through
    `ClaimAdmin.get_queryset`.
  *Behaviour note:* an administrator with no health facility stays visible to
  holders of the right (`allow_null=True`), as with the previous model filter.
  *Test:* `core/core/tests/test_claim_admin_row_security.py` (model and
  GraphQL, own district only; a district with no health facility sees none).
  The core and api_fhir_r4 suites pass (743 tests).

- [x] **C4 — `tasks_management` Task queries have no action-level permission check.** *(fixed 2026-10-01, tasks_management `e62725a`)*
  *Fixed earlier:* `resolve_task_group` calls `_check_permissions`, and
  `ResolveTaskMutation._validate_mutation` exists (executor/triage/admin).
  *Fixed in this change:*
  - `resolve_task` / `resolve_task_history` (`tasks_management/schema.py`) first
    require `task.query` (191001, `tasks_management.view_task`) via
    `require(user, "task", "query")`, before `wait_for_mutation`. The false
    comment saying `get_queryset` filtered by user is gone.
  - The executor/triage rule moved from the two GraphQL types to
    `Task.get_queryset` (`tasks_management/models.py`). `TaskGQLType` uses
    `ScopedQuerysetMixin`, and `TaskHistoryGQLType` delegates to
    `Task.get_queryset`, because the historical model does not inherit it.
  - The resolvers apply that scope **before** the `entityString__Icontains`
    filter, which loads rows in Python and used to walk every task.
  - Executor membership now ignores removed executors
    (`taskexecutor__is_deleted=False`, as `TaskDecisionGQLType` already did) and
    goes through a subquery, so tasks are no longer duplicated.
  - Anonymous users get nothing.
  *Grants:* 191001 is already held by every demo role that holds a task right,
  and the frontend menu is gated on it (`RIGHT_TASKS_MANAGEMENT_SEARCH`).
  Superusers pass `has_perms`. No fixture change.
  *Test:* `tasks_management/tests/test_task_row_security.py`.

- [x] **C5 — Grievance ticket comments: access check isn't ticket-scoped.** *(fixed 2026-10-05)*
  Before: `resolve_comments` passed if the user was `attending_staff` on **any**
  ticket, or held the comment right, then returned `Comment.objects.all()`.
  `Comment.get_queryset` (the category/flag ticket filter) never ran, because
  `CommentGQLType` had no hook. `CreateCommentMutation` and the commenter
  name/DOB fields used the same any-ticket check.
  *Fix* (`grievance_social_protection/grievance_social_protection/`):
  - **The right is always required.** Attending a ticket grants nothing by
    itself. `resolve_comments`, the commenter field checks (`check_comment_perms`)
    and `CreateCommentMutation` require 127004 / 127005. The any-ticket helper
    `user_associated_with_ticket` is removed.
  - **Rows are the model's.** `Comment.get_queryset` (`models.py`) returns
    comments on tickets visible under the category/flag rules, or attended by the
    user. `CommentGQLType` uses `ScopedQuerysetMixin`, and `resolve_comments`
    returns `Comment.get_queryset(...)`.
  - **Writing follows reading.** `CreateCommentMutation` requires the create
    right **and** a ticket whose thread the user may read (visible, or attended).
  *Grants:* deployments where attending staff commented without holding
  127004 / 127005 must now grant those rights to their role (fixtures, no
  migration).
  *Test:* `tests/test_comment_row_security.py`. The grievance suite passes (149 tests).
  *Not in scope, waiting for UBA:* "right **and** relationship" (only the creator
  or assignee of a grievance may comment or update it, with a broader right for
  supervisors). This needs a relationship-based grant; the `link_types` argument
  of the row-security layer is reserved for it.

- [x] **C6 — Claim `claim` (singular) and `claimAttachments` are unscoped IDORs.** *(fixed 2026-10-06, claim `4c9d27c`)*
  Before: `resolve_claim` did a raw `Claim.objects.get(id=…/uuid=…)` with a right
  check gated on `ROW_SECURITY`; `resolve_claim_attachments` checked the right
  only; `ClaimAttachment` had no `row_scope`.
  *Fix* (`claim/claim/`):
  - `ClaimAttachment.row_scope = ParentScope("claim")`: an attachment is as
    visible as its claim (through `Claim.get_queryset`, which scopes in code).
    `ClaimAttachmentGQLType` uses `ScopedQuerysetMixin`.
  - `resolve_claim` always requires the right and looks up through
    `Claim.get_queryset`; out of scope resolves to `null`, like a missing claim.
  - The REST download (`views.attach`) and the create/update/delete attachment
    mutations use the model scope. **Found while fixing:** the download and the
    delete filtered `ClaimAttachment` on `health_facility__location`, a field it
    does not have, so both failed for every non-superuser; the update/delete
    error handlers crashed when the attachment was not found.
  *Test:* `claim/tests/test_claim_row_security.py`. The claim suite passes.

- [x] **C7 — PolicyHolder portal queries leaked every company's data.** *(fixed 2026-10-06, policyholder `74ec39e`)*
  Before: `resolve_policy_holder_insuree` / `_user` / `_contribution_plan_bundle`
  never restricted to the caller's own `PolicyHolderUser` link, and the model
  `get_queryset` of the three link models was `if settings.ROW_SECURITY: pass`.
  *Fix* (`policyholder/policyholder/`):
  - `PolicyHolder.get_queryset`: policy holders in the user's districts **or**
    the ones the user is currently attached to. Membership widens rows only;
    the right is always required (same shape as C5's "visible or attended").
  - The three link models declare `ParentScope("policy_holder")`.
  - Holding only a portal right restricts every query to the user's own
    policy holders, through `PolicyHolder.filter_membership(user, prefix)`.
  *Behaviour change:* a portal user with no membership now gets an empty list
  from `policyHolder` instead of an "unauthorized" error.
  *Test:* `tests/test_policy_holder_row_security.py`.

- [x] **C8 — `contract`/`contractDetails`/`contractContributionPlanDetails` leaked all companies' contracts.** *(fixed 2026-10-06, contract `0e4097a`, with N01)*
  `ContractDetails` declares `ParentScope("contract")`,
  `ContractContributionPlanDetails` `ParentScope("contract_details")`; the three
  GQL types use `ScopedQuerysetMixin`; holding only the portal right restricts
  to the user's own policy holders (`PolicyHolder.filter_membership`).
  *Test:* `contract/tests/test_contract_row_security.py`. policyholder, contract,
  both contribution calcrules and api_fhir_r4 pass (377 tests).

- [x] **C9 — Invoice/Bill: row security was a documented no-op for the whole module.** *(fixed)*
  `invoice/invoice/mixins.py:17-32` now hands on to `super().get_queryset(...)`,
  so Invoice/Bill's `GenericScope("subject")` (`models.py:146,219`) applies;
  `resolve_bill_payment` (`gql/bill_payment/query.py:27`) now calls
  `_check_permissions`. The FHIR viewsets were already routed through
  `get_queryset` (M02). Remaining gap on the child models: **N03**.

---

## HIGH

- [x] **H01** — `individualDataSourceUpload` was unscoped. *(fixed 2026-10-08, individual `fb321de`)* An upload has no location until its rows are imported, so it is visible to its uploader, to whoever may see its review task (`Task.get_queryset`), and to whoever may see an individual created from it. Rows not yet imported follow the uploader and reviewers (before: visible to nobody but superusers, so reviewers saw nothing to accept); imported rows follow their individual. `IndividualDataUploadRecords` declare `ParentScope("data_upload")`; resolvers and the invalid-items download go through these scopes. *Test:* `individual/tests/test_upload_row_security.py`. See also the opt-in Python import pipeline (`ba47e65`), which resolves each row's village at validation.
- [x] **H02** — Insuree/Family write mutations had no location authorization. *(fixed 2026-10-06, insuree `fca9f12`)* Delete/Remove/SetFamilyHead/ChangeInsureeFamily/MoveFamilyToParent/DeleteFamiliesFromParent look targets up through `Family/Insuree.get_queryset` (out of scope reads as "does not exist"). `InsureeService.create_or_update` and `FamilyService` refuse to update an out-of-scope insuree or family (by uuid or CHFID), to attach an insuree to one, and to place either in a location the user is not granted (`LocationManager.is_allowed`). Also fixed: `RemoveInsurees` extended its error list with a dict's keys. *Test:* `insuree/tests/test_insuree_write_row_security.py`; full suite 2161 tests green.
- [x] **H03** — `UpdateInsureeMutation` checked the CREATE permission. *(fixed: `insuree/insuree/gql_mutations.py:271` now checks `gql_mutation_update_insurees_perms`)*
- [ ] **H04** — `healthFacilitiesStr`: only `is_authenticated`, no `has_perms`; client-controlled `ignoreLocation: true` skips the `LocationManager` filter and `HealthFacilityGQLType` (`location/location/gql_queries.py:164`) has no `get_queryset` backstop. (`location/location/schema.py:152-177`) — **Open**
- [x] **H05** — Claim permission checks gated by `and settings.ROW_SECURITY`. *(fixed 2026-10-06: claim `4c9d27c` (`claim`), `c75eaa9` (`claims`, `claimHistory`); claim_sampling `9701565` (`claimSamplingBatch`, `claimSamplingBatchAssignment`, `samplingBatchClaims`). Test: `test_claim_row_security.py`)* The claim_sampling singular lookups are still unscoped (raw `.objects.get`), see **S2**.
- [x] **H06** — `claimHistory` bypassed facility filtering. *(fixed 2026-10-06, claim `c75eaa9`: the resolver scopes the current claim through `Claim.get_queryset` and follows `legacy_id`; `ClaimGQLType.get_queryset` still skips this field because the rows are superseded versions. Test: `test_history_keeps_own_district`)*
- [x] **H07** — Claim workflow mutations acted on unscoped UUIDs. *(fixed 2026-10-06, claim `c75eaa9`)*
  Submit (explicit uuids), Process, Delete, DeliverFeedback, SaveReview, the
  feedback/review status mutations (`set_claims_status`, now scoped to the
  `user` it is given), DeliverReview's `update_claims_dedrems`, UpdateClaim
  (`update_or_create_claim` and `validate_claim_data`, including the restore
  source) and the print report (`ClaimReportService.fetch`) start from
  `Claim.get_queryset`. Out-of-scope claims are reported as not found. Also
  fixed: Process/Delete appended errors with `errors += {...}` (adding the
  dict's keys), and `set_claim_deleted` returned a dict instead of a list.
  *Test:* `test_claim_row_security.py` (delete, process, status change, save
  review, update). Claim sampling still calls `set_claims_status` without a
  user (system workflow, unscoped by design).
- [x] **H08** — `CreateClaimSamplingBatchMutation` permission check was commented out; only an anonymous-user check was live. *(fixed, merged from `feature/security` into `release/26.10` on 2026-10-01: `claim_sampling/claim_sampling/gql_mutations.py` checks `gql_mutation_create_claim_batch_samplings_perms` again)*
- [ ] **H09** — `policyRenewals` right. — **Partial**
  Now reads a query-named key, `gql_query_policy_renewals_perms`
  (`policy/policy/schema.py:117`), and `PolicyRenewalGQLType` is scoped
  (`gql_queries.py:63`, `models.py:132` `ParentScope("policy")`). But in
  `policy/policy/apps.py:51-52`, `"queryRenewals"` maps to the same right ID
  (101205) as `"renew"`, so viewing renewals still requires the renew right.
  Its scoping also inherits **N02**.
- [ ] **H10** — `policyValues` does an unscoped `Policy.objects.get(uuid=prev_uuid)` (`policy/policy/schema.py:180`) and an unscoped `Family.objects…get(id=family_id)` (`:175-177`) on client-supplied ids. — **Open**
- [x] **H11** — FHIR Family/Group listing bypassed district scoping (`views/fhir/group.py` used `Family.objects.all()`). *(fixed)*
- [x] **H12** — FHIR claim-feedback (`Communication`) listing bypassed district scoping (`views/fhir/communication.py`). *(fixed)*
- [x] **H13** — FHIR ClaimAdmin listing: empty permission and unscoped. *(fixed: permission now `CoreConfig.gql_query_claim_administrator_perms`; `_ca_queryset()` routes through `ClaimAdmin.get_queryset`. Scoped by `ClaimAdmin.row_scope` since C3.)*
- [x] **H14** — FHIR HealthFacility/PolicyHolder org listing unscoped (`views/fhir/organisation.py`). *(fixed)*
- [x] **H15** — FHIR Enrolment-officer listing had an empty permission. *(fixed: permission now `CoreConfig.gql_query_enrolment_officers_perms`; querysets routed through `Officer.get_queryset`. That classmethod does no location filtering itself; see **N06**.)*
- [ ] **H16** — `report`/`ReportGQLType.definition` check only the generic `gql_query_report_perms` (`report/report/schema.py:49-51`, `:24-26`), skipping the per-report `report["permission"]` filter that `reports` applies (`:46`). — **Open**
- [ ] **H17** — `resolve_payer` (singular) returns a raw `Payer.objects.get(uuid=uuid)` (`payer/payer/schema.py:71`), skipping the scoping `resolve_payers` applies. See also M12. — **Open**
- [ ] **H18** — `payment` module has no location/facility scoping. `Payment` (`payment/payment/models.py:10`) and `PaymentDetail` declare no `row_scope`/`get_queryset`; `PaymentGQLType` (`gql_queries.py:14`) has no hook; `schema.py:74,88` use raw `Payment.objects.filter`. — **Open**
- [x] **H19** — `form_builder` viewer rights were never checked. *(fixed: `openimis-be-form_builder_py/form_builder/schema.py:52-55,64-67` now check `gql_form_definition_viewer_perms`/`gql_form_submission_viewer_perms`. Related remaining gap: **N04**.)*
- [x] **H20** — `payroll` permission mismatches on money-moving mutations: `MakePaymentForPayrollMutation` checked `gql_payroll_create_perms`; `ClosePayrollMutation`/`RejectPayrollMutation` checked `gql_payroll_delete_perms`. *(fixed, merged from `feature/security` into `release/26.10` on 2026-10-01: dedicated actions `payroll.close` / `payroll.reject` (aliased onto 202004) and `payroll.makePayment` (aliased onto 202002), checked through `gql_payroll_close_perms` / `gql_payroll_reject_perms` / `gql_payroll_make_payment_perms`. No role change.)*
- [x] **H21** — Mutation object lookups were never location-scoped. *(fixed 2026-10-06 with S3: core `1c1c5cc`, contribution_plan `ec52087`, policyholder `fabc311`)* The shared mixins and `BaseService.update/delete` now look targets up through `core.models.target_queryset` (= `Model.get_queryset`), so payer, payment, invoice/bill, grievance, payroll, tasks_management, individual and social_protection writes that go through them are covered. The remaining `X.objects.get(id=…)` in those modules' mutations are post-write bookkeeping (linking the MutationLog to the object the service just wrote), not target lookups. *Test:* `core/tests/test_mutation_target_scope.py`, `policyholder/tests/test_policy_holder_row_security.py` (`PolicyHolderWriteRowSecurityTests`).

---

## MEDIUM

- [x] **M01** — FHIR `CoverageEligibilityRequest` POST performed a real eligibility lookup without the GET-equivalent permission. *(fixed: `permissions_post` now also requires `PolicyConfig.gql_query_eligibilities_perms`)*
- [x] **M02** — FHIR Invoice/Bill/PaymentNotice viewsets bypassed their model's `get_queryset`. *(fixed: `invoice.py`/`payment_notice.py` call `Invoice/Bill/PaymentInvoice.get_queryset`; effective since C9. `PaymentInvoice` itself has no `row_scope`, see **N03**.)*
- [ ] **M03** — `resolve_premiums_by_policies` (`contribution/contribution/schema.py:127-131`) filters raw `Policy.objects` by client-supplied UUIDs and returns `Premium.objects.filter(...)`. `Premium.row_scope = ParentScope("policy")` (`contribution/models.py:21`) exists but is not called, and would not help until **N02** is fixed. — **Open**
- [ ] **M04** — `resolve_product` (singular) with `uuid` returns raw `Product.objects.get(uuid=…)` (`product/product/schema.py:305-313`), ignoring `Product.row_scope = LocationScope("location")`. The `id` path goes through the node lookup and the scoped `ProductGQLType`. — **Open**
- [ ] **M05** — `resolve_calculation_params` (`calculation/calculation/schema.py:167-186`) does `ContentType.objects.get(model__iexact=<client class name>).model_class().objects.get(id=<client id>)`, gated only by `gql_query_calculation_rule_perms`: it reads an instance of *any* installed model. — **Open**
- [ ] **M06** — `ClaimSamplingBatch`/`ClaimSamplingBatchAssignment` (`claim_sampling/claim_sampling/models.py:6,21`) declare no `row_scope`; `schema.py:49,60,69-70` fetch by int id / uuid unscoped. — **Open**
- [ ] **M07** — `BatchRun` (`claim_batch/claim_batch/models.py:13`) has no `row_scope`/`get_queryset`; `BatchRunGQLType` (`schema.py:18`) has no hook; `resolve_batch_runs_summaries` is raw SQL with no location restriction. — **Open**
- [x] **M08** — `resolve_insuree_officers` was gated by a `[]` default. *(fixed: `insuree/insuree/apps.py:34,48,112` — `RIGHTS.perms("insuree", "queryOfficers")`, i.e. `insuree.view_insuree_officer` / 101101; same fix in `policy/apps.py`)*
- [ ] **M09** — `resolve_can_add_insuree` does an unscoped `Family.objects.get(id=family_id)` by raw sequential integer (`insuree/insuree/schema.py:171-174`), then discloses policy/product/member-count warnings. — **Open**
- [ ] **M10** — `social_protection.resolve_awaiting_beneficiary` (`schema.py:510-525`) returns `GroupBeneficiary.objects.filter(...)` without the `GroupBeneficiary.get_queryset` its sibling applies (`:482`). No `awaiting_beneficiary` field is declared, so it is unreachable dead code: scope it or delete it. — **Open**
- [x] **M11** — Location filtering only when the client supplies `parentLocation`. *(fixed)*
  `social_protection` `project`: `Project.row_scope = LocationScope("location")` and `ProjectGQLType` uses `ScopedQuerysetMixin`.
  `payroll` `paymentPoint` (merged from `feature/security` into `release/26.10` on 2026-10-01): `PaymentPoint.row_scope = LocationScope("location")` (`payroll/payroll/models.py`) and `PaymentPointGQLType` uses `ScopedQuerysetMixin`. `parentLocation` now only narrows the result.
- [ ] **M12** — `Payer.get_queryset` (`payer/payer/models.py:69-71`) filters the incoming queryset, then discards it and rebuilds from `Payer.objects` via `build_user_location_filter_query`. — **Open**

---

## LOW / informational

- [x] **L01** — FHIR `permissions.py`: no-op `self.base_class` statement; `multiserializer/mixins.py` called `base_class.get_queryset()` with an incompatible signature. *(fixed: the statement was removed and the call now passes `(None, request.user)`; still effectively unreachable)*
- [ ] **L02** — `payment_cycle.resolve_payment_cycle` runs `wait_for_mutation` (`payment_cycle/payment_cycle/schema.py:51`) *before* `_check_permissions` (`:54`). — **Open**
- [ ] **L03** — `resolve_officer_locations` (`location/location/schema.py:201-211`) does `Officer.objects.get(code=officer_code)` and returns that officer's allowed locations to anyone holding `gql_query_locations_perms`. — **Open**
- [x] **L04** — `locationsAll` bypasses district scoping. *(confirmed intentional and documented: `location/location/gql_queries.py:94-98,143`; pinned by `location/tests/test_location_walk_row_security.py:93`)*
- [x] **L05** — `controls.resolve_control_str` had no auth/permission check (nor did `control`, which had no resolver at all). *(fixed, merged from `feature/security` into `release/26.10` on 2026-10-01: both `resolve_control` and `resolve_control_str` (`controls/controls/schema.py`) require authentication and `gql_query_controls_perms`)*
- [ ] **L06** — Dead/unimplemented resolvers. — **Partial**
  *Removed:* `resolve_task_relative_indexes`, `resolve_payment_details`.
  *Still open:* `ApproveClaimSamplingBatchMutation` (`claim_sampling/claim_sampling/gql_mutations.py:144-160`, exposed at `schema.py:116`) checks the right and returns `[]`. Finish it or remove it.

---

## Systemic patterns (fix once, not per-instance)

- [ ] **S1** — Permission constants still at their `[]` default (`has_perms([])` returns `True` by design). — **Partial**
  Remaining: `medical/medical/apps.py` `gql_query_diagnosis_perms = []`. Since the medical rework (merged from `feature/security` into `release/26.10` on 2026-10-01), `resolve_diagnoses` and `resolve_diagnoses_str` refuse anonymous callers explicitly, but any authenticated user still passes. The comment in `apps.py` records the open product decision: give `diagnosis.query` its own right id, or declare diagnoses open reference data like items and services (OMT-281).
- [ ] **S2** — Scoped-list / unscoped-singular pairs. Known instances: C6 (fixed), H10, H17, M04, M09, L03. `scan_unscoped.py` reports 28 unscoped reads (12 connection fields whose type has no hook, 14 plain fields/lists, 2 nested resolvers), which is an undercount (see N07). — **Open**
- [x] **S3** — Scoping threaded through the shared mutation mixins *(fixed 2026-10-06, core `1c1c5cc`)*: `TargetLookupMixin._target_queryset(user)` in the mixins, `BaseService._get_target` in services. `_validate_mutation` keeps a plain existence check because subclasses call it **before** their own permission check (which must answer first); the scoped lookup is in `_mutate`. Out of scope reads as "does not exist". H02 (insuree/family mutations) does not use these mixins and stays open.
- [x] **S4** — `has_perms(...) and settings.ROW_SECURITY` conditionals: the 6 listed in H05 are removed *(fixed with H05)*. `location/location/models.py:427` looks similar but is not a permission gate: it lifts the scope for region creators (OMT-280).

---

## NEW — found during the 2026-09-28 re-verification

- [x] **N01** — **Contract GQL types' `get_queryset` was indented inside `class Meta`**, so graphene never called it and Contract's `ParentScope("policy_holder")` never applied through GraphQL. *(fixed 2026-10-06, contract `0e4097a`: the three types use `ScopedQuerysetMixin`; see C8)*
- [x] **N02** — **`Policy.get_queryset` only blocked anonymous users.** *(fixed 2026-10-06: policy `dfe3b5f`, insuree `c582c6e`, location `2413852`)* `Policy.row_scope = ParentScope("family")`; `PolicyGQLType` and `policiesByFamily` apply it (`policiesByInsuree` stays the nationwide enquiry). `Premium`, `PolicyRenewal`, `ClaimDedRem` now inherit a real restriction (M03, H09 scoping). **Found while fixing:** `Family`/`Insuree` compared at district level, so enrolment officers (granted villages) saw no family, insuree or policy at all; `LocationManager.build_user_village_filter_query` matches each granted location at its own level (TODO(UBA): grants will come from business accesses). *Tests:* `policy/tests/test_policy_row_security.py`, `insuree/tests/test_officer_row_security.py`, `policy/tests/test_roles_gql_eo_user.py` (previously asserted the unscoped behaviour).
- [ ] **N03** — **Invoice/Bill child models declare no `row_scope`**: `InvoicePayment`, `BillPayment`, `InvoiceEvent`, `BillEvent`, `PaymentInvoice` (`invoice/invoice/models.py:188,203,271,285,372`). Each should get `ParentScope("invoice"/"bill")` (or the equivalent) so they compose onto C9's `GenericScope`. — **Open**
- [ ] **N04** — **`FormSubmissionGQLType.get_queryset` ignores the incoming queryset** and returns a fresh `FormSubmission.objects.filter(...)` with no row scoping (`openimis-be-form_builder_py/form_builder/gql_queries.py:62-63`). — **Open**
- [x] **N05** — **`claim_sampling.resolve_sampling_summary` had no permission check.** *(fixed, merged from `feature/security` into `release/26.10` on 2026-10-01: it checks `gql_query_claim_batch_samplings_perms`)*
- [ ] **N06** — **`Officer.get_queryset` performs no location filtering**; it only blocks anonymous users. H15 routes FHIR through it, so the enrolment-officer listing is still effectively unscoped. — **Open**
- [ ] **N07** — **`backend/script/scan_unscoped.py` undercounts.** `secured_models()` only counts models that define `get_queryset` in their own class body, so models scoped through `row_scope` alone (Product, Premium, …) are missed, as are models with no scoping at all (M06, M07). It also treats any `get_queryset` call as scoped, even when the implementation does nothing useful (N02, N06). — **Open**

---

## Suggested triage order

1. ~~**C2** (payment gateway key)~~: fixed 2026-09-30.
2. ~~**N01**~~: fixed 2026-10-06.
3. ~~**H05 / S4**, **H08**~~: fixed.
4. ~~**C6**~~ (with H06, H07): fixed 2026-10-06.
5. ~~**C7, C8**~~: fixed 2026-10-06.
6. **N02, N06**: the model-level scopes other items depend on.
7. ~~**S3**, **H21**, **N02**~~: fixed 2026-10-06.
8. The rest of HIGH, then MEDIUM, in ID order.

---

## History: FHIR (`api_fhir_r4`) fix pass

All `api_fhir_r4` (FHIR) findings (C1, H11–H15, M01, M02, L01) are fixed in `backend-packages/api_fhir_r4`. Fixes were sanity-checked with `py_compile` on every edited file and by confirming that the existing FHIR test suite (`api_fhir_r4/tests/`) uses superuser/imis_admin test users, which bypass permission-list and location-filter checks entirely. Tightening the permission lists and routing querysets through each model's `get_queryset` should therefore not change existing test behaviour. New tests (`api_fhir_r4/tests/test_api_rights_enforcement.py`) use genuinely restricted (non-superuser) users to verify the fixed endpoints both ways (403 without the right, allowed with it). The full 217-test suite plus the 12 new tests pass under both `manage.py test` and `pytest` (see "Pytest wiring" below).

### Follow-up: `permissions.py` rewritten against verified ground truth, not name-guessing

The original fix assigned FHIR permission classes by picking the Config attribute that "sounded right" for each HTTP verb. That is the same failure mode that caused the bugs in the first place. A second pass traced every one of the ~19 permission classes in `api_fhir_r4/permissions.py` down through its serializer to whatever the code actually enforces (the underlying service's own `has_perms` check when one exists, otherwise the equivalent GraphQL query/mutation), and rewrote the file against that ground truth.

**New file: `api_fhir_r4/rights.py`**: named constants (Django-style `<MODEL>_<VIEW|ADD|CHANGE|DELETE>`) that alias the existing dynamic `SomeConfig.gql_..._perms` attributes. The raw right-ID numbers are never hardcoded, so rights that admins configure via `ModuleConfiguration` still work. `permissions.py` now reads as `rights.POLICY_ADD` etc. instead of a wall of near-identical `SomeConfig.gql_mutation_...` lines. Each constant's inline comment records what was actually verified, including known gaps that were not fixed.

#### Fixes applied in this pass
- [x] **`Product` (InsurancePlan) GET had no permission at all** (`permissions_get = []`). `Item`/`Service` have a documented, intentional OMT-281 open-read exemption, both in their `get_queryset` and in GraphQL. `Product` has no such exemption anywhere, and its GraphQL equivalent (`resolve_products`) enforces `gql_query_products_perms`. Fixed: now requires `ProductConfig.gql_query_products_perms` (`rights.PRODUCT_VIEW`).
- [x] **`Claim` POST was missing a required permission.** The real code path (`serializers/claimSerializer.py::_create_claim_from_validated_data`) checks `create_claims_perms OR submit_claims_perms`, but the DRF gate only recognized `create_claims_perms`. A user with only the submit right was blocked at the REST gate before reaching the more permissive real check. Fixed: `rights.CLAIM_ADD` now concatenates both.
- [x] **`Communication`/`CommunicationRequest` GET was gated by a mutation-only permission** (`gql_mutation_select_claim_feedback_perms`). Elsewhere that right is used only to flip a status field on write, and it has no read role in the schema. Fixed: now uses `ClaimConfig.gql_query_claims_perms` (`rights.CLAIM_FEEDBACK_VIEW`), the real read-path permission.
- [x] **`Contract`/`Coverage` GET used the wrong Config attribute** (`gql_query_policies_by_insuree_perms` for a queryset that lists ALL policies, not policies "by insuree"). Fixed: now uses `PolicyConfig.gql_query_policies_perms` (`rights.POLICY_VIEW`).

#### Deliberately NOT changed (documented instead, as a maintainer decision)
- **`ClaimAdmin`/`Officer` create/update/delete rights** (`CLAIM_ADMINISTRATOR_*`, `ENROLMENT_OFFICER_*`) are dedicated, purpose-built rights that no GraphQL mutation currently checks. Via GraphQL, ClaimAdmin/Officer CRUD only happens as a side effect of the generic `CreateUserMutation`/`UpdateUserMutation`/`DeleteUserMutation`, gated by the unrelated `gql_mutation_*_users_perms`. Unifying them is a product decision, not a mechanical fix.
- **`ClaimAdmin`/`Officer` GET** kept the dedicated `gql_query_claim_administrator_perms`/`gql_query_enrolment_officers_perms`. (The GraphQL `claimAdmins` resolver has since moved to the same right; see C3.)
- **`Insuree` PUT/PATCH** kept the semantically correct `gql_mutation_update_insurees_perms` (GraphQL now matches, see H03).
- **`Location` PUT/PATCH**: GraphQL's `UpdateLocationMutation` additionally requires `gql_mutation_create_region_locations_perms` to edit Region/District rows (via `LocationService._check_users_locations_rights`). The FHIR `LocationSerializer` writes directly to the model and never calls `LocationService`. That would need the serializer to call the service. Documented, not fixed.
- **`Group` (Family) POST/PUT**: `GroupSerializer` also upserts non-head member `Insuree` records, gated only on the Family permission. GraphQL's closest analog requires an Insuree permission too. Documented, not fixed.
- **`Invoice`/`Bill` POST/PUT/PATCH**: both serializers' `create()`/`update()` are `pass` stubs, and no GraphQL equivalent exists. The assignments are naming-consistent placeholders. `InvoiceViewSet` has no destroy route at all.
- **`ActivityDefinition` and `Product` write verbs**: correct right IDs, but unreachable (`ActivityDefinitionViewSet` is list/retrieve-only, `ProductViewSet` is a `ReadOnlyModelViewSet`).
- **`Claim`/`Communication` DELETE ("skip")**: permission IDs are correct, but REST hard-deletes the row via `DestroyModelMixin`, whereas GraphQL (`DeleteClaimsMutation`/`SkipClaimsFeedbackMutation`) only flips a status. A behavioural gap, not a naming issue.

#### Verification
- `python manage.py test api_fhir_r4 --keepdb` → 217 tests, all pass.
- `python -m pytest --pyargs api_fhir_r4.tests.test_api_rights_enforcement` → 12/12 pass.

### Test coverage & pytest wiring (api_fhir_r4 only)

- `backend-packages/api_fhir_r4/api_fhir_r4/tests/test_api_rights_enforcement.py`: regression tests for the fixed endpoints. Each asserts BOTH directions with a genuinely restricted (non-superuser) test user: 403 without the right, allowed with exactly that right. Covers Contract POST (C1), CoverageEligibilityRequest POST (M01), and Practitioner GET (H13, H15).
- `backend-packages/api_fhir_r4/api_fhir_r4/tests/utils.py`: fixed an eager DB call at module-import time (a `create_admin_role()` call used as a function-default value), which broke test collection under `pytest-django`. Made lazy; no behaviour change.
- `backend/openIMIS/pytest.ini` + `backend/openIMIS/conftest.py`: pytest-django wiring. Run with `cd backend/openIMIS && pytest --pyargs api_fhir_r4.tests.test_api_rights_enforcement -v`. `conftest.py` disables password validators after Django configures, because the shared fixtures' password (`"admin123"`) does not satisfy this project's policy.
- **Known gap**: ~14 other pre-existing test files in this module (`test_api_claim.py`, `test_api_contract.py`, `test_api_group.py`, etc.) still hit the DB at import time (via `LogInMixin` or module-level `create_admin_role()` calls) and fail to collect under pytest. The other ~140 pytest-compatible tests run cleanly once those files are excluded.
