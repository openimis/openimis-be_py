# Declaration des droits : feuille de travail

But : donner a chaque droit un **nom django durable** (`app_label.codename`),
regroupe par **entite** puis **action**, comme `core.apps.DJANGO_PERMS`.

Ce nom devient une ligne `auth_permission` dont la cle primaire EST l'identifiant
du droit, donc il est durable : mieux vaut un blanc qu'un nom approximatif.

## Comment remplir

Une ligne par cle de config. Colonnes :

| colonne | quoi |
|---|---|
| `id` | identifiant openIMIS actuel — **ne pas changer** sauf intention explicite |
| `entite` | l'objet metier, en camelCase (`paymentPoint`, `benefitPlan`) |
| `action` | `query`/`create`/`update`/`delete` si ca correspond, sinon le verbe metier (`makePayment`, `close`) |
| `nom django` | `app_label.verbe_modele` — laisser vide si tu veux que je le derive de entite+action |
| `?` | `OK` si ma proposition convient, sinon corrige les colonnes |

Les colonnes `id`, `usages` et `partage avec` sont **informatives** : ne les modifie pas,
elles sont la pour decider.

- **usages** : nombre de sites d'appel dans le code (hors `apps.py`). Un `0` signale
  un droit declare que rien ne verifie — dis-moi si on le garde ou le supprime.
- **partage avec** : autres cles portant le meme identifiant. C'est **la** decision
  importante : meme entite/action differente (un alias voulu), ou collision a corriger ?

---

## policyholder  (37 cles)

> **A trancher** : distinguer back-office et portail : deux entites ? un qualificatif d'action ?

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_mutation_create_policyholder_perms` | 150102 | 2 | - | policyholder | create | `policyholder.add_policyholder` | **?** |
| `gql_mutation_create_policyholdercontributionplan_perms` | 150402 | 1 | - | policyholdercontributionplan | create | `policyholder.add_policyholdercontributionplan` | **?** |
| `gql_mutation_create_policyholderinsuree_perms` | 150202 | 1 | - | policyholderinsuree | create | `policyholder.add_policyholderinsuree` | **?** |
| `gql_mutation_create_policyholderinsuree_portal_perms` | 154102 | 0 | - | policyholderinsureePortal | create | `policyholder.add_policyholderinsureeportal` | **?** |
| `gql_mutation_create_policyholderuser_perms` | 150302 | 1 | - | policyholderuser | create | `policyholder.add_policyholderuser` | **?** |
| `gql_mutation_create_policyholderuser_portal_perms` | 154402 | 0 | - | policyholderuserPortal | create | `policyholder.add_policyholderuserportal` | **?** |
| `gql_mutation_delete_policyholder_perms` | 150104 | 2 | - | policyholder | delete | `policyholder.delete_policyholder` | **?** |
| `gql_mutation_delete_policyholdercontributionplan_perms` | 150404 | 1 | - | policyholdercontributionplan | delete | `policyholder.delete_policyholdercontributionplan` | **?** |
| `gql_mutation_delete_policyholderinsuree_perms` | 150204 | 1 | - | policyholderinsuree | delete | `policyholder.delete_policyholderinsuree` | **?** |
| `gql_mutation_delete_policyholderinsuree_portal_perms` | 154104 | 0 | - | policyholderinsureePortal | delete | `policyholder.delete_policyholderinsureeportal` | **?** |
| `gql_mutation_delete_policyholderuser_perms` | 150304 | 1 | - | policyholderuser | delete | `policyholder.delete_policyholderuser` | **?** |
| `gql_mutation_delete_policyholderuser_portal_perms` | 154404 | 0 | - | policyholderuserPortal | delete | `policyholder.delete_policyholderuserportal` | **?** |
| `gql_mutation_replace_policyholdercontributionplan_perms` | 150406 | 1 | - | policyholdercontributionplan | replace | `policyholder.replace_policyholdercontributionplan` | **?** |
| `gql_mutation_replace_policyholderinsuree_perms` | 150206 | 1 | - | policyholderinsuree | replace | `policyholder.replace_policyholderinsuree` | **?** |
| `gql_mutation_replace_policyholderinsuree_portal_perms` | 154106 | 0 | - | policyholderinsureePortal | replace | `policyholder.replace_policyholderinsureeportal` | **?** |
| `gql_mutation_replace_policyholderuser_perms` | 150306 | 1 | - | policyholderuser | replace | `policyholder.replace_policyholderuser` | **?** |
| `gql_mutation_replace_policyholderuser_portal_perms` | 154406 | 0 | - | policyholderuserPortal | replace | `policyholder.replace_policyholderuserportal` | **?** |
| `gql_mutation_update_policyholder_perms` | 150103 | 2 | - | policyholder | update | `policyholder.change_policyholder` | **?** |
| `gql_mutation_update_policyholdercontributionplan_perms` | 150403 | 1 | - | policyholdercontributionplan | update | `policyholder.change_policyholdercontributionplan` | **?** |
| `gql_mutation_update_policyholderinsuree_perms` | 150203 | 1 | - | policyholderinsuree | update | `policyholder.change_policyholderinsuree` | **?** |
| `gql_mutation_update_policyholderinsuree_portal_perms` | 154103 | 0 | - | policyholderinsureePortal | update | `policyholder.change_policyholderinsureeportal` | **?** |
| `gql_mutation_update_policyholderuser_perms` | 150303 | 1 | - | policyholderuser | update | `policyholder.change_policyholderuser` | **?** |
| `gql_mutation_update_policyholderuser_portal_perms` | 154403 | 0 | - | policyholderuserPortal | update | `policyholder.change_policyholderuserportal` | **?** |
| `gql_query_insuree_policy_portal_perms` | 154901 | 1 | - | insureePolicyPortal | query | `policyholder.view_insureepolicyportal` | **?** |
| `gql_query_payment_portal_perms` | 154501 | 2 | - | paymentPortal | query | `policyholder.view_paymentportal` | **?** |
| `gql_query_policyholder_admins_perms` | 150105 | 0 | - | policyholderAdmins | query | `policyholder.view_policyholderadmin` | **?** |
| `gql_query_policyholder_perms` | 150101 | 3 | - | policyholder | query | `policyholder.view_policyholder` | **?** |
| `gql_query_policyholder_portal_perms` | 154001 | 1 | - | policyholderPortal | query | `policyholder.view_policyholderportal` | **?** |
| `gql_query_policyholdercontributionplanbundle_admins_perms` | 150405 | 0 | - | policyholdercontributionplanbundleAdmins | query | `policyholder.view_policyholdercontributionplanbundleadmin` | **?** |
| `gql_query_policyholdercontributionplanbundle_perms` | 150401 | 1 | - | policyholdercontributionplanbundle | query | `policyholder.view_policyholdercontributionplanbundle` | **?** |
| `gql_query_policyholdercontributionplanbundle_portal_perms` | 154601 | 1 | - | policyholdercontributionplanbundlePortal | query | `policyholder.view_policyholdercontributionplanbundleportal` | **?** |
| `gql_query_policyholderinsuree_admins_perms` | 150205 | 0 | - | policyholderinsureeAdmins | query | `policyholder.view_policyholderinsureeadmin` | **?** |
| `gql_query_policyholderinsuree_perms` | 150201 | 1 | - | policyholderinsuree | query | `policyholder.view_policyholderinsuree` | **?** |
| `gql_query_policyholderinsuree_portal_perms` | 154101 | 1 | - | policyholderinsureePortal | query | `policyholder.view_policyholderinsureeportal` | **?** |
| `gql_query_policyholderuser_admins_perms` | 150305 | 0 | - | policyholderuserAdmins | query | `policyholder.view_policyholderuseradmin` | **?** |
| `gql_query_policyholderuser_perms` | 150301 | 1 | - | policyholderuser | query | `policyholder.view_policyholderuser` | **?** |
| `gql_query_policyholderuser_portal_perms` | 154401 | 1 | - | policyholderuserPortal | query | `policyholder.view_policyholderuserportal` | **?** |

## invoice  (34 cles)

> **A trancher** : invoice / bill / paiement / evenement : combien d'entites ?

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_bill_amend_perms` | 156109 | 0 | - | bill | amend | `invoice.amend_bill` | **?** |
| `gql_bill_create_perms` | 156102 | 1 | - | bill | create | `invoice.add_bill` | **?** |
| `gql_bill_delete_perms` | 156104 | 2 | - | bill | delete | `invoice.delete_bill` | **?** |
| `gql_bill_event_create_message_perms` | 156306 | 1 | - | billEventCreateMessage | query | `invoice.view_billeventcreatemessage` | **?** |
| `gql_bill_event_create_perms` | 156302 | 0 | - | billEvent | create | `invoice.add_billevent` | **?** |
| `gql_bill_event_delete_all_message_perms` | 156308 | 0 | - | billEventDeleteAllMessage | query | `invoice.view_billeventdeleteallmessage` | **?** |
| `gql_bill_event_delete_my_message_perms` | 156307 | 1 | - | billEventDeleteMyMessage | query | `invoice.view_billeventdeletemymessage` | **?** |
| `gql_bill_event_delete_perms` | 156304 | 0 | - | billEvent | delete | `invoice.delete_billevent` | **?** |
| `gql_bill_event_search_perms` | 156301 | 1 | - | billEvent | query | `invoice.view_billevent` | **?** |
| `gql_bill_event_update_perms` | 156303 | 0 | - | billEvent | update | `invoice.change_billevent` | **?** |
| `gql_bill_payment_create_perms` | 156202 | 1 | - | billPayment | create | `invoice.add_billpayment` | **?** |
| `gql_bill_payment_delete_perms` | 156204 | 1 | - | billPayment | delete | `invoice.delete_billpayment` | **?** |
| `gql_bill_payment_refund_perms` | 156206 | 0 | - | billPaymentRefund | query | `invoice.view_billpaymentrefund` | **?** |
| `gql_bill_payment_search_perms` | 156201 | 1 | - | billPayment | query | `invoice.view_billpayment` | **?** |
| `gql_bill_payment_update_perms` | 156203 | 1 | - | billPayment | update | `invoice.change_billpayment` | **?** |
| `gql_bill_search_perms` | 156101 | 3 | - | bill | query | `invoice.view_bill` | **?** |
| `gql_bill_update_perms` | 156103 | 1 | - | bill | update | `invoice.change_bill` | **?** |
| `gql_invoice_amend_perms` | 155109 | 0 | - | invoice | amend | `invoice.amend_invoice` | **?** |
| `gql_invoice_create_perms` | 155102 | 3 | - | invoice | create | `invoice.add_invoice` | **?** |
| `gql_invoice_delete_perms` | 155104 | 3 | - | invoice | delete | `invoice.delete_invoice` | **?** |
| `gql_invoice_event_create_message_perms` | 155306 | 1 | - | invoiceEventCreateMessage | query | `invoice.view_invoiceeventcreatemessage` | **?** |
| `gql_invoice_event_create_perms` | 155302 | 0 | - | invoiceEvent | create | `invoice.add_invoiceevent` | **?** |
| `gql_invoice_event_delete_all_message_perms` | 155308 | 0 | - | invoiceEventDeleteAllMessage | query | `invoice.view_invoiceeventdeleteallmessage` | **?** |
| `gql_invoice_event_delete_my_message_perms` | 155307 | 1 | - | invoiceEventDeleteMyMessage | query | `invoice.view_invoiceeventdeletemymessage` | **?** |
| `gql_invoice_event_delete_perms` | 155304 | 0 | - | invoiceEvent | delete | `invoice.delete_invoiceevent` | **?** |
| `gql_invoice_event_search_perms` | 155301 | 1 | - | invoiceEvent | query | `invoice.view_invoiceevent` | **?** |
| `gql_invoice_event_update_perms` | 155303 | 0 | - | invoiceEvent | update | `invoice.change_invoiceevent` | **?** |
| `gql_invoice_payment_create_perms` | 155202 | 5 | - | invoicePayment | create | `invoice.add_invoicepayment` | **?** |
| `gql_invoice_payment_delete_perms` | 155204 | 3 | - | invoicePayment | delete | `invoice.delete_invoicepayment` | **?** |
| `gql_invoice_payment_refund_perms` | 155206 | 0 | - | invoicePaymentRefund | query | `invoice.view_invoicepaymentrefund` | **?** |
| `gql_invoice_payment_search_perms` | 155201 | 7 | - | invoicePayment | query | `invoice.view_invoicepayment` | **?** |
| `gql_invoice_payment_update_perms` | 155203 | 3 | - | invoicePayment | update | `invoice.change_invoicepayment` | **?** |
| `gql_invoice_search_perms` | 155101 | 3 | - | invoice | query | `invoice.view_invoice` | **?** |
| `gql_invoice_update_perms` | 155103 | 2 | - | invoice | update | `invoice.change_invoice` | **?** |

## report  (27 cles)

> **A trancher** : chaque etat est-il une entite, ou une action 'query' sur une entite `report` ?

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_mutation_report_add_perms` | 131224 | 1 | - | reportAdd | None | `report.None_reportadd` | **?** |
| `gql_mutation_report_delete_perms` | 131226 | 0 | - | reportDelete | None | `report.None_reportdelete` | **?** |
| `gql_mutation_report_edit_perms` | 131225 | 1 | - | reportEdit | None | `report.None_reportedit` | **?** |
| `gql_query_report_perms` | 131200 | 6 | - | report | query | `report.view_report` | **?** |
| `gql_reports_capitation_payment_perms` | 131218 | 0 | - | reportsCapitationPayment | query | `report.view_reportscapitationpayment` | **?** |
| `gql_reports_claim_history_report_perms` | 131223 | 0 | - | reportsClaimHistoryReport | query | `report.view_reportsclaimhistoryreport` | **?** |
| `gql_reports_claim_overview_report_perms` | 131213 | 0 | - | reportsClaimOverviewReport | query | `report.view_reportsclaimoverviewreport` | **?** |
| `gql_reports_contribution_collection_perms` | 131204 | 0 | - | reportsContributionCollection | query | `report.view_reportscontributioncollection` | **?** |
| `gql_reports_contribution_distribution_perms` | 131206 | 0 | - | reportsContributionDistribution | query | `report.view_reportscontributiondistribution` | **?** |
| `gql_reports_contribution_payment_perms` | 131220 | 0 | - | reportsContributionPayment | query | `report.view_reportscontributionpayment` | **?** |
| `gql_reports_control_number_assignment_perms` | 131221 | 0 | - | reportsControlNumberAssignment | query | `report.view_reportscontrolnumberassignment` | **?** |
| `gql_reports_derived_operational_indicators_perms` | 131203 | 0 | - | reportsDerivedOperationalIndicators | query | `report.view_reportsderivedoperationalindicator` | **?** |
| `gql_reports_enrolment_performance_indicators_perms` | 131208 | 0 | - | reportsEnrolmentPerformanceIndicators | query | `report.view_reportsenrolmentperformanceindicator` | **?** |
| `gql_reports_families_insurees_overview_perms` | 131215 | 0 | - | reportsFamiliesInsureesOverview | query | `report.view_reportsfamiliesinsureesoverview` | **?** |
| `gql_reports_insuree_without_photos_perms` | 131210 | 0 | - | reportsInsureeWithoutPhotos | query | `report.view_reportsinsureewithoutphoto` | **?** |
| `gql_reports_matching_funds_perms` | 131212 | 0 | - | reportsMatchingFunds | query | `report.view_reportsmatchingfund` | **?** |
| `gql_reports_overview_of_commissions_perms` | 131222 | 0 | - | reportsOverviewOfCommissions | query | `report.view_reportsoverviewofcommission` | **?** |
| `gql_reports_payment_category_overview_perms` | 131211 | 0 | - | reportsPaymentCategoryOverview | query | `report.view_reportspaymentcategoryoverview` | **?** |
| `gql_reports_pending_insurees_perms` | 131216 | 0 | - | reportsPendingInsurees | query | `report.view_reportspendinginsuree` | **?** |
| `gql_reports_percentage_referrals_perms` | 131214 | 0 | - | reportsPercentageReferrals | query | `report.view_reportspercentagereferral` | **?** |
| `gql_reports_primary_operational_indicator_policies_perms` | 131201 | 0 | - | reportsPrimaryOperationalIndicatorPolicies | query | `report.view_reportsprimaryoperationalindicatorpolicy` | **?** |
| `gql_reports_primary_operational_indicators_claims_perms` | 131202 | 0 | - | reportsPrimaryOperationalIndicatorsClaims | query | `report.view_reportsprimaryoperationalindicatorsclaim` | **?** |
| `gql_reports_product_sales_perms` | 131205 | 0 | - | reportsProductSales | query | `report.view_reportsproductsale` | **?** |
| `gql_reports_rejected_photo_perms` | 131219 | 0 | - | reportsRejectedPhoto | query | `report.view_reportsrejectedphoto` | **?** |
| `gql_reports_renewals_perms` | 131217 | 0 | - | reportsRenewals | query | `report.view_reportsrenewal` | **?** |
| `gql_reports_status_of_register_perms` | 131209 | 0 | - | reportsStatusOfRegister | query | `report.view_reportsstatusofregister` | **?** |
| `gql_reports_user_activity_perms` | 131207 | 0 | - | reportsUserActivity | query | `report.view_reportsuseractivity` | **?** |

## social_protection  (20 cles)

> **A trancher** : benefit plan / beneficiary / group beneficiary / project : decoupage

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_activity_search_perms` | 208001 | 1 | - | activity | query | `social_protection.view_activity` | **?** |
| `gql_beneficiary_create_perms` | 170002 | 3 | - | beneficiary | create | `social_protection.add_beneficiary` | **?** |
| `gql_beneficiary_delete_perms` | 170004 | 2 | - | beneficiary | delete | `social_protection.delete_beneficiary` | **?** |
| `gql_beneficiary_search_perms` | 170001 | 6 | - | beneficiary | query | `social_protection.view_beneficiary` | **?** |
| `gql_beneficiary_update_perms` | 170003 | 2 | - | beneficiary | update | `social_protection.change_beneficiary` | **?** |
| `gql_benefit_plan_close_perms` | 160005 | 1 | - | benefitPlan | close | `social_protection.close_benefitplan` | **?** |
| `gql_benefit_plan_create_perms` | 160002 | 1 | - | benefitPlan | create | `social_protection.add_benefitplan` | **?** |
| `gql_benefit_plan_delete_perms` | 160004 | 2 | - | benefitPlan | delete | `social_protection.delete_benefitplan` | **?** |
| `gql_benefit_plan_search_perms` | 160001 | 5 | - | benefitPlan | query | `social_protection.view_benefitplan` | **?** |
| `gql_benefit_plan_update_perms` | 160003 | 1 | - | benefitPlan | update | `social_protection.change_benefitplan` | **?** |
| `gql_project_beneficiary_enroll_perms` | 209005 | 2 | - | projectBeneficiaryEnroll | query | `social_protection.view_projectbeneficiaryenroll` | **?** |
| `gql_project_beneficiary_time_entry_perms` | 209006 | 2 | - | projectBeneficiaryTimeEntry | query | `social_protection.view_projectbeneficiarytimeentry` | **?** |
| `gql_project_create_perms` | 209002 | 1 | - | project | create | `social_protection.add_project` | **?** |
| `gql_project_delete_perms` | 209004 | 2 | - | project | delete | `social_protection.delete_project` | **?** |
| `gql_project_search_perms` | 209001 | 3 | - | project | query | `social_protection.view_project` | **?** |
| `gql_project_update_perms` | 209003 | 1 | - | project | update | `social_protection.change_project` | **?** |
| `gql_schema_create_perms` | 171002 | 4 | - | schema | create | `social_protection.add_schema` | **?** |
| `gql_schema_delete_perms` | 171004 | 0 | - | schema | delete | `social_protection.delete_schema` | **?** |
| `gql_schema_search_perms` | 171001 | 4 | - | schema | query | `social_protection.view_schema` | **?** |
| `gql_schema_update_perms` | 171003 | 4 | - | schema | update | `social_protection.change_schema` | **?** |

## contribution_plan  (18 cles)

> **A trancher** : bundle / plan / payment plan : trois entites, plus les *_admins

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_mutation_create_contributionplan_perms` | 151202 | 1 | - | contributionplan | create | `contribution_plan.add_contributionplan` | **?** |
| `gql_mutation_create_contributionplanbundle_perms` | 151102 | 2 | - | contributionplanbundle | create | `contribution_plan.add_contributionplanbundle` | **?** |
| `gql_mutation_create_paymentplan_perms` | 157102 | 1 | - | paymentplan | create | `contribution_plan.add_paymentplan` | **?** |
| `gql_mutation_delete_contributionplan_perms` | 151204 | 1 | - | contributionplan | delete | `contribution_plan.delete_contributionplan` | **?** |
| `gql_mutation_delete_contributionplanbundle_perms` | 151104 | 2 | - | contributionplanbundle | delete | `contribution_plan.delete_contributionplanbundle` | **?** |
| `gql_mutation_delete_paymentplan_perms` | 157104 | 1 | - | paymentplan | delete | `contribution_plan.delete_paymentplan` | **?** |
| `gql_mutation_replace_contributionplan_perms` | 151206 | 1 | - | contributionplan | replace | `contribution_plan.replace_contributionplan` | **?** |
| `gql_mutation_replace_contributionplanbundle_perms` | 151106 | 2 | - | contributionplanbundle | replace | `contribution_plan.replace_contributionplanbundle` | **?** |
| `gql_mutation_replace_paymentplan_perms` | 157106 | 1 | - | paymentplan | replace | `contribution_plan.replace_paymentplan` | **?** |
| `gql_mutation_update_contributionplan_perms` | 151203 | 1 | - | contributionplan | update | `contribution_plan.change_contributionplan` | **?** |
| `gql_mutation_update_contributionplanbundle_perms` | 151103 | 2 | - | contributionplanbundle | update | `contribution_plan.change_contributionplanbundle` | **?** |
| `gql_mutation_update_paymentplan_perms` | 157103 | 1 | - | paymentplan | update | `contribution_plan.change_paymentplan` | **?** |
| `gql_query_contributionplan_admins_perms` | 151205 | 0 | - | contributionplanAdmins | query | `contribution_plan.view_contributionplanadmin` | **?** |
| `gql_query_contributionplan_perms` | 151201 | 9 | - | contributionplan | query | `contribution_plan.view_contributionplan` | **?** |
| `gql_query_contributionplanbundle_admins_perms` | 151105 | 0 | - | contributionplanbundleAdmins | query | `contribution_plan.view_contributionplanbundleadmin` | **?** |
| `gql_query_contributionplanbundle_perms` | 151101 | 3 | - | contributionplanbundle | query | `contribution_plan.view_contributionplanbundle` | **?** |
| `gql_query_paymentplan_admins_perms` | 157105 | 0 | - | paymentplanAdmins | query | `contribution_plan.view_paymentplanadmin` | **?** |
| `gql_query_paymentplan_perms` | 157101 | 3 | - | paymentplan | query | `contribution_plan.view_paymentplan` | **?** |

## payroll  (13 cles)

> **A trancher** : `make_payment` est un decaissement ; close/reject sont des transitions d'etat

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_csv_reconciliation_create_perms` | 206002 | 1 | - | csvReconciliation | create | `payroll.add_csvreconciliation` | **?** |
| `gql_csv_reconciliation_search_perms` | 206001 | 1 | - | csvReconciliation | query | `payroll.view_csvreconciliation` | **?** |
| `gql_payment_gateway_config_perms` | 202005 | 2 | - | paymentGatewayConfig | query | `payroll.view_paymentgatewayconfig` | **?** |
| `gql_payment_point_create_perms` | 201002 | 1 | - | paymentPoint | create | `payroll.add_paymentpoint` | **?** |
| `gql_payment_point_delete_perms` | 201004 | 1 | - | paymentPoint | delete | `payroll.delete_paymentpoint` | **?** |
| `gql_payment_point_search_perms` | 201001 | 1 | - | paymentPoint | query | `payroll.view_paymentpoint` | **?** |
| `gql_payment_point_update_perms` | 201003 | 1 | - | paymentPoint | update | `payroll.change_paymentpoint` | **?** |
| `gql_payroll_close_perms` | 202004 | 2 | payroll.gql_payroll_delete_perms, payroll.gql_payroll_reject_perms | payroll | close | `payroll.close_payroll` | **?** |
| `gql_payroll_create_perms` | 202002 | 4 | payroll.gql_payroll_make_payment_perms | payroll | create | `payroll.add_payroll` | **?** |
| `gql_payroll_delete_perms` | 202004 | 4 | payroll.gql_payroll_close_perms, payroll.gql_payroll_reject_perms | payroll | delete | `payroll.delete_payroll` | **?** |
| `gql_payroll_make_payment_perms` | 202002 | 2 | payroll.gql_payroll_create_perms | payrollMakePayment | query | `payroll.view_payrollmakepayment` | **?** |
| `gql_payroll_reject_perms` | 202004 | 2 | payroll.gql_payroll_close_perms, payroll.gql_payroll_delete_perms | payroll | reject | `payroll.reject_payroll` | **?** |
| `gql_payroll_search_perms` | 202001 | 8 | - | payroll | query | `payroll.view_payroll` | **?** |

## tasks_management  (12 cles)

> **A trancher** : task / task group / task flow / executor : decoupage

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_task_create_perms` | 191002 | 0 | - | task | create | `tasks_management.add_task` | **?** |
| `gql_task_delete_perms` | 191004 | 0 | - | task | delete | `tasks_management.delete_task` | **?** |
| `gql_task_flow_create_perms` | 192002 | 1 | - | taskFlow | create | `tasks_management.add_taskflow` | **?** |
| `gql_task_flow_delete_perms` | 192004 | 1 | - | taskFlow | delete | `tasks_management.delete_taskflow` | **?** |
| `gql_task_flow_search_perms` | 192001 | 2 | - | taskFlow | query | `tasks_management.view_taskflow` | **?** |
| `gql_task_flow_update_perms` | 192003 | 2 | - | taskFlow | update | `tasks_management.change_taskflow` | **?** |
| `gql_task_group_create_perms` | 190002 | 2 | - | taskGroup | create | `tasks_management.add_taskgroup` | **?** |
| `gql_task_group_delete_perms` | 190004 | 2 | - | taskGroup | delete | `tasks_management.delete_taskgroup` | **?** |
| `gql_task_group_search_perms` | 190001 | 3 | - | taskGroup | query | `tasks_management.view_taskgroup` | **?** |
| `gql_task_group_update_perms` | 190003 | 2 | - | taskGroup | update | `tasks_management.change_taskgroup` | **?** |
| `gql_task_search_perms` | 191001 | 1 | - | task | query | `tasks_management.view_task` | **?** |
| `gql_task_update_perms` | 191003 | 1 | - | task | update | `tasks_management.change_task` | **?** |

## tools  (11 cles)

> **A trancher** : « registers » et « extracts » sont des ACTIONS (import / export), pas des entites a 'voir'

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `extracts_master_data_perms` | 131101 | 1 | - | extractsMasterData | query | `tools.view_extractsmasterdata` | **?** |
| `extracts_officer_feedbacks_perms` | 131106 | 1 | - | extractsOfficerFeedbacks | query | `tools.view_extractsofficerfeedback` | **?** |
| `extracts_officer_renewals_perms` | 131105 | 1 | - | extractsOfficerRenewals | query | `tools.view_extractsofficerrenewal` | **?** |
| `extracts_phone_extract_perms` | 131102,131103 | 1 | - | extractsPhoneExtract | query | `tools.view_extractsphoneextract` | **?** |
| `extracts_upload_claims_perms` | 131104 | 4 | - | extractsUploadClaims | query | `tools.view_extractsuploadclaim` | **?** |
| `registers_diagnoses_perms` | 131000,131002,131001 | 2 | tools.registers_health_facilities_perms, tools.registers_items_perms, tools.registers_locations_perms, tools.registers_perms, tools.registers_services_perms | registersDiagnoses | query | `tools.view_registersdiagnose` | **?** |
| `registers_health_facilities_perms` | 131000,131004,131003 | 2 | tools.registers_diagnoses_perms, tools.registers_items_perms, tools.registers_locations_perms, tools.registers_perms, tools.registers_services_perms | registersHealthFacilities | query | `tools.view_registershealthfacility` | **?** |
| `registers_items_perms` | 131000,131008,131007 | 4 | tools.registers_diagnoses_perms, tools.registers_health_facilities_perms, tools.registers_locations_perms, tools.registers_perms, tools.registers_services_perms | registersItems | query | `tools.view_registersitem` | **?** |
| `registers_locations_perms` | 131000,131006,131005 | 5 | tools.registers_diagnoses_perms, tools.registers_health_facilities_perms, tools.registers_items_perms, tools.registers_perms, tools.registers_services_perms | registersLocations | query | `tools.view_registerslocation` | **?** |
| `registers_perms` | 131000,131100 | 0 | tools.registers_diagnoses_perms, tools.registers_health_facilities_perms, tools.registers_items_perms, tools.registers_locations_perms, tools.registers_services_perms | registers | query | `tools.view_register` | **?** |
| `registers_services_perms` | 131000,131010,131009 | 4 | tools.registers_diagnoses_perms, tools.registers_health_facilities_perms, tools.registers_items_perms, tools.registers_locations_perms, tools.registers_perms | registersServices | query | `tools.view_registersservice` | **?** |

## individual  (9 cles)

> **A trancher** : individual / group / data source / upload : decoupage

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_group_create_perms` | 180002 | 6 | - | group | create | `individual.add_group` | **?** |
| `gql_group_delete_perms` | 180004 | 2 | - | group | delete | `individual.delete_group` | **?** |
| `gql_group_search_perms` | 180001 | 5 | - | group | query | `individual.view_group` | **?** |
| `gql_group_update_perms` | 180003 | 3 | - | group | update | `individual.change_group` | **?** |
| `gql_individual_create_perms` | 159002 | 7 | - | individual | create | `individual.add_individual` | **?** |
| `gql_individual_delete_perms` | 159004 | 1 | - | individual | delete | `individual.delete_individual` | **?** |
| `gql_individual_search_perms` | 159001 | 13 | - | individual | query | `individual.view_individual` | **?** |
| `gql_individual_undo_delete_perms` | 159005 | 1 | - | individualUndo | delete | `individual.delete_individualundo` | **?** |
| `gql_individual_update_perms` | 159003 | 1 | - | individual | update | `individual.change_individual` | **?** |

## grievance_social_protection  (9 cles)

> **A trancher** : en plus, droits GENERES par categorie - voir question 2

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_mutation_create_comment_perms` | 127005 | 3 | - | comment | create | `grievance_social_protection.add_comment` | **?** |
| `gql_mutation_create_tickets_perms` | 127001 | 1 | - | tickets | create | `grievance_social_protection.add_ticket` | **?** |
| `gql_mutation_delete_tickets_perms` | 127003 | 2 | - | tickets | delete | `grievance_social_protection.delete_ticket` | **?** |
| `gql_mutation_resolve_grievance_perms` | 127006 | 1 | - | grievance | resolve | `grievance_social_protection.resolve_grievance` | **?** |
| `gql_mutation_update_tickets_perms` | 127002 | 4 | - | tickets | update | `grievance_social_protection.change_ticket` | **?** |
| `gql_mutation_update_uncategorized_category_tickets_perms` | 127102 | 0 | - | uncategorizedCategoryTickets | update | `grievance_social_protection.change_uncategorizedcategoryticket` | **?** |
| `gql_query_comments_perms` | 127004 | 2 | - | comments | query | `grievance_social_protection.view_comment` | **?** |
| `gql_query_tickets_perms` | 127000 | 6 | - | tickets | query | `grievance_social_protection.view_ticket` | **?** |
| `gql_query_uncategorized_category_tickets_perms` | 127100 | 0 | - | uncategorizedCategoryTickets | query | `grievance_social_protection.view_uncategorizedcategoryticket` | **?** |

## form_builder  (5 cles)

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_form_definition_viewer_perms` | 151002 | 0 | - | formDefinitionViewer | query | `form_builder.view_formdefinitionviewer` |  |
| `gql_form_designer_perms` | 151001 | 8 | - | formDesigner | query | `form_builder.view_formdesigner` |  |
| `gql_form_extension_write_perms` | 151005 | 0 | - | formExtensionWrite | query | `form_builder.view_formextensionwrite` |  |
| `gql_form_submission_viewer_perms` | 151004 | 0 | - | formSubmissionViewer | query | `form_builder.view_formsubmissionviewer` |  |
| `gql_form_submit_perms` | 151003 | 6 | - | form | submit | `form_builder.submit_form` |  |

## claim_sampling  (4 cles)

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_mutation_approve_claim_batch_samplings_perms` | 126004 | 1 | - | claimBatchSamplings | approve | `claim_sampling.approve_claimbatchsampling` |  |
| `gql_mutation_create_claim_batch_samplings_perms` | 126002 | 1 | - | claimBatchSamplings | create | `claim_sampling.add_claimbatchsampling` |  |
| `gql_mutation_update_claim_batch_samplings_perms` | 126003 | 1 | - | claimBatchSamplings | update | `claim_sampling.change_claimbatchsampling` |  |
| `gql_query_claim_batch_samplings_perms` | 126001 | 5 | - | claimBatchSamplings | query | `claim_sampling.view_claimbatchsampling` |  |

## api_fhir_r4  (4 cles)

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `fhir_sub_create_perms` | 158002 | 0 | - | fhirSub | create | `api_fhir_r4.add_fhirsub` |  |
| `fhir_sub_delete_perms` | 158004 | 0 | - | fhirSub | delete | `api_fhir_r4.delete_fhirsub` |  |
| `fhir_sub_search_perms` | 158001 | 0 | - | fhirSub | query | `api_fhir_r4.view_fhirsub` |  |
| `fhir_sub_update_perms` | 158003 | 0 | - | fhirSub | update | `api_fhir_r4.change_fhirsub` |  |

## calculation  (2 cles)

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_mutation_update_calculation_rule_perms` | 153003 | 0 | - | calculationRule | update | `calculation.change_calculationrule` |  |
| `gql_query_calculation_rule_perms` | 153001 | 4 | - | calculationRule | query | `calculation.view_calculationrule` |  |

## opensearch_reports  (2 cles)

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_opensearch_dashboard_search_perms` | 199001 | 2 | - | opensearchDashboard | query | `opensearch_reports.view_opensearchdashboard` |  |
| `gql_opensearch_dashboard_update_perms` | 199003 | 1 | - | opensearchDashboard | update | `opensearch_reports.change_opensearchdashboard` |  |

## deduplication  (2 cles)

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_create_deduplication_payment_review_perms` | 172002 | 0 | - | deduplicationPaymentReview | create | `deduplication.add_deduplicationpaymentreview` |  |
| `gql_create_deduplication_review_perms` | 172001 | 2 | - | deduplicationReview | create | `deduplication.add_deduplicationreview` |  |

## api_etl  (2 cles)

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_mutation_execute_api_etl_rule_perms` | 953002 | 0 | - | executeApiEtlRule | None | `api_etl.None_executeapietlrule` |  |
| `gql_query_api_etl_rule_perms` | 953001 | 2 | - | apiEtlRule | query | `api_etl.view_apietlrule` |  |

## workflow  (1 cles)

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_workflow_search_perms` | 210001 | 2 | - | workflow | query | `workflow.view_workflow` |  |

## controls  (1 cles)

| cle de config | id | usages | partage avec | entite | action | nom django | ? |
|---|---|---|---|---|---|---|---|
| `gql_query_controls_perms` | 211001 | 2 | - | controls | query | `controls.view_control` |  |

---

## Questions transverses

**1. `medical.gql_query_diagnosis_perms` est vide** (= accorde a tout le monde).
Pas de droit de lecture voisin sur lequel l'aliaser : un diagnostic n'est ni un
article ni un acte. Deux issues coherentes :
- lui donner un identifiant propre (122105 est libre) — les roles devront le recevoir ;
- le declarer donnee de reference ouverte, comme les articles et actes le sont deja
  a dessein (exemption OMT-281), et le documenter comme tel.

Reponse : 

**2. `grievance_social_protection` genere un droit par categorie de ticket configuree**
(plage 127100-127999, l'identifiant etant la cle primaire d'une ligne `auth_permission`).
C'est le dernier endroit ou de la donnee de configuration produit des droits.
Consequences : le catalogue depend du deploiement, et deux instances peuvent donner
des identifiants differents a « la meme » categorie — donc les fixtures de roles ne
sont pas portables entre instances.
- garder tel quel ;
- ou un jeu FIXE de droits par type de permission, la granularite par categorie
  passant au scoping des lignes plutot qu'a un droit par categorie (changement
  fonctionnel, pas un nettoyage).

Reponse : 

**3. `odk_integration`** n'est pas dans `openimis.json` (donc pas installe ici, non
testable). Ses droits `import_flow_*` valent **180001-04**, qui sont les droits
`group_*` du module `individual` : accorder « gerer les flux ODK » accorde aussi
creer/modifier/supprimer des groupes du registre client. Et son bloc propre
181001-04 n'a aucune entree au catalogue, donc ces 4 droits ne peuvent etre
accordes a personne. On corrige a l'aveugle, ou on laisse ?

Reponse : 

**4. Droits a 0 usage.** Plusieurs droits ne sont verifies nulle part (colonne
`usages`). Les garder revient a afficher dans l'ecran des roles des cases qui ne
protegent rien. A supprimer, ou a cabler ?

Reponse : 

