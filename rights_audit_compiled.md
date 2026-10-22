# Audit des droits — synthèse consolidée

Un agent par module, instruit par `docs_rights_module_checklist.md` (règles R1→R10),
sur les 44 modules de l'assemblage `backend/openIMIS/openimis-dev.json`. Chaque agent a
produit un rapport détaillé ; ce document en est la compilation. Les rapports
individuels restent disponibles dans le répertoire de travail de la session
(`scratchpad/rights_audit/<module>.md`).

Tous les modules cités ici sont **dans l'assemblage** : les écarts décrits sont
atteignables sur un déploiement de développement standard, ils ne portent pas sur du
code dormant.

Couverture des 44 modules : **34 audités** — 29 par agent, et les 5 derniers
(`contribution`, `claim_batch`, `claim_sampling`, `workflow`, `controls`) par moi-même,
l'agent s'étant interrompu en cours d'écriture ; **10 sans aucun droit déclaré** —
`dhis2_etl` et les 9 `calcrule_*`, dont l'`apps.py` ne contient aucune clé `_perms`
(vérifié), donc hors périmètre de R1-R9. **Le périmètre est couvert en entier.**

Trois catégories, telles que définies dans la consigne :

- **CASSÉ** — un droit qui ne protège pas ce qu'il prétend protéger, ou qui manque.
- **NON CONVERTI** — `DJANGO_PERMS` / `_PERM_CFG` / `RightsDeclaration` / `get_rights`
  pas encore en place. Attendu à ce stade, ce n'est pas une faille : le mécanisme
  `has_model_right` échoue **fermé** quand rien n'est déclaré.
- **DÉLIBÉRÉ** — décision assumée. Elle ne compte comme écart que si elle n'est pas
  écrite sur place.

---

## 1. Verdict d'ensemble

La déconfiguration des droits (R4/R5/R6) a **tenu partout** : sur les 34 modules audités,
aucun ne réintroduit un droit par la configuration, aucun n'a de liste vide non
justifiée, et aucun identifiant n'a bougé — hors les changements décidés et documentés.
C'est le résultat le plus important : le chantier « plus de config des droits » est
étanche.

Ce que l'audit a mis au jour est d'une autre nature : **les droits existent, ils sont
juste mal branchés.** Presque toutes les failles trouvées sont des points d'entrée qui
ne lisent pas le droit prévu pour eux — et dans plusieurs cas le droit prévu n'est lu
nulle part du tout. Le catalogue est bon ; le câblage ne l'est pas.

| | modules |
|---|---|
| Audités | 34 — périmètre complet |
| Convertis (`DJANGO_PERMS`) | 14 — core, claim, insuree, contract, policy, location, medical, medical_pricelist, payer, payment, payment_cycle, product, claim_batch, contribution |
| Déconfigurés mais non convertis | 19 — attendu |
| Sans faille ouverte | 12 — api_fhir_r4, calculation, opensearch_reports, im_export, payment, payment_cycle, product, payroll, contribution, claim_batch, workflow, tasks_management (R1-R9) |
| Failles corrigées pendant l'audit | 3 |
| Constats d'agent périmés, vérifiés et écartés | 2 |

---

## 2. Ce qui est déjà corrigé

Trois failles trouvées en cours d'audit (§2.1-2.3), le **lot A** dans son entier
(§2.4), et les secrets en clair dans le journal des mutations et les réponses (§2.5). **705 tests sur les 8 modules touchés, aucun échec** — y compris les deux échecs
de `form_builder` qui préexistaient au lot A.

Les deux cartes de permissions sont réalignées : `solution-builder/solution/permissions_map.json`
portait encore l'ancien schéma de noms (318 entrées, `api_etl.query_api_etl_rule` au lieu de
`api_etl.api_etl_rule`). Regénérée par `generate_permissions_map --output`, donc par le même
générateur que la carte du backend et non à la main : les deux fichiers sont désormais
identiques, 352 entrées. La seule valeur qui disparaît est `191005`
(`tasks_management.task_search_all`), retirée volontairement par la migration
`0012_remove_task_search_all_right` — « never enforced server-side ».

### 2.1 Escalade de privilèges par l'API REST `core` — **corrigé**

`core/core/views.py`, `core/core/serializers.py`. `UserViewSet` était un `ModelViewSet`
complet sur `core.User` avec pour seul contrôle `IsAuthenticated`, et aucun
`DEFAULT_PERMISSION_CLASSES` dans l'assemblage. Reproduit avant correction, avec un
compte sans aucun droit :

```
GET   /api/core/users/     → 200   (liste de tous les comptes, champ `rights` inclus)
PATCH is_superuser=true    → 200
is_superuser après         → True
```

C'est l'exact inverse de la protection GraphQL : `update_or_create_user`
(`schema.py:2032`) refuse de positionner `is_superuser` sans `is_imis_admin`.
Correctif : table `_ACTION_RIGHTS` + `get_permissions()` par action, et
`read_only_fields = ("is_superuser", "is_imis_admin")` sur le sérialiseur.
`current_user` reste sous `IsAuthenticated`.

### 2.2 Le verrou anti-configuration était contournable — **corrigé**

`core/core/models/base.py`. Le filtre qui retire les clés `_perms` vivait dans
`get_or_default`, mais `_reload_module_config` (appelé par `transaction.on_commit` à
chaque enregistrement de config) faisait son propre `json.loads` et court-circuitait le
filtre. Une ligne `ModuleConfiguration` avec `"gql_beneficiary_search_perms": []` était
donc ignorée au démarrage mais **appliquée au premier enregistrement** — et
`has_perms([])` renvoie `True`. Le filtre a été déplacé dans `_cfg`, le seul endroit où
le JSON est décodé ; `social_protection/apps.py` passe désormais par `instance._cfg`.

### 2.3 Facturation de contrat sans aucun droit — **corrigé**

`contract/.../contract_mutations.py`. `ContractCreateInvoiceBulkMutation` redéfinissait
`async_mutate`, seul appelant de `_validate_mutation` : le contrôle
`gql_invoice_create_perms` n'était jamais exécuté, et rien en aval ne compensait
(`tasks.py`, `ContractToInvoiceService.create_invoice` au corps `pass`). Tout utilisateur
connecté pouvait générer les factures de n'importe quel contrat. Correctif : appel
explicite de `cls._validate_mutation(user, **data)` en tête.

Note : `ApproveContractBulkMutation` et `CounterContractBulkMutation` contournent aussi
`_validate_mutation`, mais restent couvertes par `ContractService.approve`/`.counter`.

---

### 2.4 Lot A — les points d'entrée sans aucun contrôle — **corrigé**

Sept resolvers et une vue REST étaient exposés sans qu'aucun droit ne soit évalué.
Aucun n'avait d'appelant légitime sans droit, d'où le traitement en premier.

| Module | Correctif | Tests |
|---|---|---|
| `payer` | `resolve_fundings` et `resolve_funding` ajoutés, sous `gql_query_payers_perms` — le droit qu'exigent déjà `PayerGQLType.resolve_fundings` et `FundingConnection.resolve_total_count` pour la même donnée. Renvoyer un queryset laisse `queryset_resolver` appliquer `get_queryset`, donc la portée ligne est préservée. | 10/10 |
| `medical` | `resolve_diagnoses` ajouté, aligné sur son jumeau `diagnoses_str` : droit + `filter_validity` (les lignes historisées étaient exposées). Le refus de l'anonyme est explicite sur les **deux**, `gql_query_diagnosis_perms` valant `[]` tant que la décision produit n'est pas prise — et `has_perms([])` renvoie `True`, y compris pour `AnonymousUser`. | 18/18 |
| `insuree` | `resolve_insuree_status_reasons` ajouté, sous le droit des autres nomenclatures d'assuré. | 32/32 |
| `claim` | `resolve_claim_attachment_type` ajouté, même droit et même forme que `resolve_claim_attachments` juste au-dessus. | 85/85 |
| `controls` | `resolve_control` ajouté, même contrôle que son jumeau `control_str`. **Les tests du module appelaient le champ sans aucun contexte** — ils ne passaient que grâce à l'absence de garde ; corrigés, plus un cas négatif. | 5/5 |
| `core` | `/api/core/scheduled_jobs` était en `AllowAny` : **nouveau droit 900201** (`core.view_scheduled_job`), dans le bloc 9002xx à côté de `maskedData` — le planificateur est une capacité, pas un modèle. `check_user_rights` accepte désormais un appelable, `CoreConfig` n'étant pas importable en tête de `views.py` (import circulaire) alors qu'un décorateur s'évalue à l'import. Carte des permissions régénérée : 352 entrées, une seule ajoutée. | 498/498 |
| `medical_pricelist` | `if hf and hf.x != id` → `if not (hf and hf.x == id)` : le refus ne se déclenchait jamais pour un compte sans formation sanitaire. `gql_query_pricelists_perms` (121200), déclaré et lu nulle part, devient le droit de lecture générale. **3 tests de non-régression ajoutés**, dont le cas qui échouait avant le correctif. | 6/6 |
| `form_builder` | 151002 et 151004 branchés sur les deux resolvers de lecture ; `formControlsSchema` sous 151001 **ou** 151002, le OU étant voulu et écrit sur place. Test négatif ajouté. Les 2 échecs préexistants sont corrigés eux aussi : ils attendaient qu'une mutation anonyme s'exécute et consigne son erreur dans un `MutationLog`, ce que la garde de `OpenIMISMutation.mutate_and_get_payload` rend volontairement impossible — le refus arrive **avant** l'écriture, pour qu'un anonyme ne puisse pas faire écrire une ligne dont il contrôle le contenu. Les tests vérifient désormais les deux moitiés : 401 `UNAUTHENTICATED`, et aucune ligne de journal créée. | 51/51 |

Une conséquence à assumer, sur `medical_pricelist` : un rôle qui lisait une liste de prix
sans détenir ni 121200 ni le droit du type concerné perd cet accès. C'est le trou qui se
ferme ; la voie de migration est de lui accorder 121200.

### 2.5 Secrets en clair dans le journal des mutations et dans la réponse — **corrigé**

Hors périmètre R1-R10, trouvé en marge : `OpenIMISMutation.mutate_and_get_payload` écrit
l'intégralité de l'input dans `MutationLog.json_content`, **et** le renvoie au front dans
`metadata`. Deux inputs journalisés portent un secret — `password` (`UserBase`, donc
`createUser` et `updateUser`) et `api_key` (`UpdatePaymentGatewayConfigInputType`).
Reproduit avant correction :

```
{"username": "MLS001", "email": "...", "password": "pS3cr3t!Never!Logged", ...}
```

en clair dans une table conservée sans limite de durée — et le même mot de passe rejoué
dans la réponse HTTP, qui traverse journaux d'accès, mandataires et rapporteurs d'erreur.

**Le secret n'atteint plus ni la base ni le courtier de messages.** Le journal n'est pas
qu'une trace : en mode asynchrone — `core.async_mutations`, **`True` par défaut en PROD**
(`core/apps.py:140-145`) — `core/tasks.py` **rejoue la mutation depuis `json_content`**.
La ligne *est* la charge utile, donc la masquer à la création créerait l'utilisateur avec
le mot de passe littéral `********`.

D'où la règle : **une mutation dont l'input porte un secret s'exécute en synchrone**,
quel que soit `core.async_mutations`. Le chemin synchrone construit sa charge utile depuis
le `data` en mémoire et non depuis le journal, la ligne peut donc être écrite **déjà
masquée**. C'est strictement meilleur que chiffrer la valeur : chiffrée, elle resterait
récupérable avec `SECRET_KEY` + la base, et il faudrait gérer une clé. Les mutations
concernées sont des actions d'administration unitaires, pas des traitements de masse :
les exécuter en synchrone ne coûte rien.

- `core/mutation_log_secrets.py` — `contains_secret` (décide du mode) et `scrub_secrets`
  (masque), par indice de nom de clé : `password`, `api_key`, `secret`, `token`… La
  **clé est conservée**, seule la valeur devient `********` : le journal garde sa valeur
  d'audit et montre qu'un mot de passe a bien transité.
- `core/schema.py` — ligne écrite déjà masquée, exécution forcée en synchrone, et les
  **deux** points de retour vers le front masqués (celui de l'erreur de validation
  renvoyait `data` brut).
- `MutationLog._secret_free_fields()` — masquage au passage en état terminal, conservé en
  **défense en profondeur** : il rattrape une clé sensible que `contains_secret` n'aurait
  pas reconnue à l'entrée, et couvre les lignes antérieures qui repasseraient par un état
  terminal. Plié dans le même `UPDATE` que le statut, donc atomique et sans aller-retour.
- `scrub_mutation_log_secrets` — commande pour l'historique déjà en base. Par défaut
  **seules les lignes en état terminal** : une ligne encore en `RECEIVED` peut être en
  file d'attente, la masquer casserait la mutation. `--include-pending
  --older-than-hours` pour les lignes bloquées, `--dry-run` pour compter d'abord.

**Limite connue** : `contains_secret` reconnaît un secret à son *nom de clé*. Un champ
sensible nommé autrement passerait à travers — d'où la défense en profondeur. Dans
l'autre sens, un faux positif ne coûte qu'une exécution synchrone et du détail d'audit en
moins, jamais une perte de sécurité.

9 tests, dont deux qui tiennent la conception : un **mode asynchrone forcé** qui vérifie
que la mutation s'exécute quand même tout de suite et que la ligne n'a jamais porté le
secret, et un **rejeu asynchrone de bout en bout** qui prouve que la charge utile reste
utilisable (`check_password(secret)` vrai sur l'utilisateur créé). Le second échouerait
si le masquage arrivait trop tôt sur ce chemin.

## 3. Failles ouvertes, par gravité

Les constats ci-dessous viennent des rapports d'agents. **J'ai revérifié moi-même, dans
le code, les dix plus graves** — ils sont marqués ✓ : `tools` (même constante pour le
`GET` et le `POST`, `has_perms` en OU, `DeletableUploadSerializer` avec
`INSERT_UPDATE_DELETE`, zéro `has_perms` dans `services.py`), `form_builder`
(`is_anonymous` seul, `get_queryset` sans filtre, 151002/151004 absents hors `apps.py`),
`medical_pricelist` (`if hf and …` avec `get_health_facility()` à `None`), `location`
(`ignoreLocation` exposé comme argument GraphQL), `claim` (`and settings.ROW_SECURITY`
sur le `has_perms`), `invoice` (`PaymentInvoiceGQLType` sans `ScopedQuerysetMixin`,
`get_queryset` dans `Meta`, resolver sans filtre), `payer` (aucun resolver sur
`fundings`), `grievance` (`CommentGQLType` en `relay.Node` sans `get_queryset`,
`Comment.objects.all()`, `user_associated_with_ticket` sans argument ticket),
`claim_sampling` et `controls` (audités entièrement par moi-même), plus les trois déjà
corrigés au §2. Les autres reposent sur le rapport de l'agent seul et
méritent une relecture avant correction.


### Niveau 1 — lecture ou écriture atteignable sans le droit correspondant

| # | Module | Point d'entrée | Ce qui est atteignable |
|---|---|---|---|
| 1 | `tools` ✓ | `views.py` — les 5 registres | **Le droit de lire un registre donne celui de le réécrire.** Même constante pour le `GET download_*` et le `POST upload_*`, évaluée en **OU** sur 3 ids. Trois imports acceptent `INSERT_UPDATE_DELETE` : suppression en masse de diagnostics, articles, services. Ces écritures contournent en outre entièrement les droits de `medical` et `location` — `tools/services.py` ne contient aucun `has_perms`. |
| ~~2~~ | `form_builder` ✓ **corrigé** | `schema.py:42-53` | `resolve_formDefinition` et `resolve_formSubmission` ne testent que `is_anonymous`. Tout compte authentifié lit **toutes** les soumissions, `submission_data` compris, filtrable par `submitted_by`. Les droits 151002/151004 n'ont aucune occurrence hors `apps.py`. En prime, `UpdateFormSubmissionMutation` ne vérifie pas la propriété — on réécrit la soumission d'autrui (le `delete`, lui, vérifie). |
| 3 | `report` | `views.py:101-118` | `reportbro_previewer` accepte en `PUT` une **définition ReportBro arbitraire et l'exécute**, sous le seul droit de *lecture* 131200 — que tous les rôles semés portent. Les droits d'écriture de gabarit (131224/131225) existent et ne gardent que la mutation. |
| ~~4~~ | `medical_pricelist` ✓ **corrigé** | `schema.py:144-160` | Le refus est conditionné à `if hf and …`, or `get_health_facility()` renvoie `None` pour tout compte back-office : la branche n'est jamais prise, **aucune exception n'est levée**, et tout compte authentifié lit n'importe quelle liste de prix en énumérant des ids séquentiels. Le droit prévu (121200) n'est lu à aucun site d'appel. Le commentaire du resolver énonce l'intention inverse. |
| 5 | `location` ✓ | `schema.py:152-177` `healthFacilitiesStr` | Aucun droit vérifié, et le seul garde-fou restant — le filtre de district — est **désactivable par le client** : `healthFacilitiesStr(ignoreLocation: true)`. Liste nationale des formations sanitaires pour tout compte authentifié, sans dépendre d'aucune configuration serveur. |
| 6 | `location` | `schema.py:134-137` `locationsAll` | Trois garde-fous tombent ensemble : pas de droit, `get_queryset` explicitement court-circuité, marche d'arbre non filtrée. Arbre complet des localités pour tout compte authentifié. **Non couvert par l'exemption OMT-281**, qui repose précisément sur le `get_queryset` ici neutralisé. |
| ~~7~~ | `medical` **corrigé** | `schema.py:46` `diagnoses` | Aucun `resolve_diagnoses`, `DiagnosisGQLType` sans `ScopedQuerysetMixin` : `Diagnosis.get_queryset` est du code mort sur ce chemin, `filter_validity` non plus. Seul écart du module non couvert par un commentaire — l'asymétrie avec `diagnoses_str`, trois lignes plus loin, montre l'oubli. |
| 8 | `claim` ✓ | `schema.py:144,162,285` | `if not has_perms(...) and settings.ROW_SECURITY: raise`. **Avec `ROW_SECURITY=False` le contrôle de droit disparaît entièrement** — registre complet des réclamations lisible, y compris anonyme. Le réglage vaut `True` par défaut (`settings/security.py:25`), donc la faille est *latente* : elle s'ouvre le jour où un déploiement pose `ROW_SECURITY=False`, ce qui est une configuration supportée. Vérifié sur place. `claimHistory` est le pire : son `get_queryset` renvoie en plus le queryset non filtré. |
| 9 | `claim_sampling` ✓ | `schema.py:39-67` | **Le même `and settings.ROW_SECURITY` que `claim`, sur 3 resolvers sur 4** — dont `sampling_batch_claims`, qui renvoie des réclamations. Le quatrième (`resolve_sampling_summary`, `:86`) n'a pas la condition, ce qui montre l'incohérence. Latent comme pour `claim` : s'ouvre sur `ROW_SECURITY=False`. |
| 10 | `invoice` ✓ | `gql/payment_invoice/query.py:25-42` | `resolve_payment_invoice` n'a **aucun** filtrage de lignes : tout porteur de 155201 voit l'intégralité de `tblPaymentInvoice`, quelle que soit sa localisation. Cause : `get_queryset` écrit **dans `class Meta`** sur 10 GQLType — graphene ne l'appelle jamais (cf. §4.2). |
| 11 | `policyholder` | `schema.py:121-147` | Le droit « portail » de lecture, censé restreindre au policyholder de l'utilisateur, **n'ajoute aucun filtre** sur 3 resolvers : tous les assurés, tous les utilisateurs, tous les bundles de tous les employeurs. Fuite inter-employeurs sur un portail multi-tenant. `resolve_policy_holder`, lui, fait le travail correctement. |
| ~~12~~ | `payer` ✓ **corrigé** | `schema.py:24-33` | `Query.fundings` et `Query.funding` n'ont **aucun resolver**, donc aucun `has_perms` : graphene applique le resolver par défaut. `ScopedQuerysetMixin` + `ParentScope("payer")` bornent les *lignes*, pas le *droit* — montants et reçus de financement lisibles par tout appelant que la portée ligne n'exclut pas. La même donnée est correctement protégée quand on y accède par le payeur (`gql_queries.py:105`) : le contrôle manque uniquement à la racine. |
| 13 | `grievance` ✓ | `openIMIS/schema.py:54` + `gql_queries.py` | **Le texte de n'importe quel commentaire est lisible par `node(id: base64("CommentGQLType:N"))`**, sans détenir aucun droit du module — donc le contenu de griefs de catégories restreintes. Cause double : `resolve_comment` n'a pas de contrôle, et la row security des modèles (`get_queryset`, conditionnée à `ROW_SECURITY`) n'est reliée à aucun type GraphQL (pas de `ScopedQuerysetMixin`). |
| ~~14~~ | `core` **corrigé** | `views.py:88-91` | `get_scheduled_jobs` : `@api_view(["GET"])` sans `permission_classes` → `AllowAny`. Un **anonyme** obtient le nom, le déclencheur et le chemin d'import du handler de chaque tâche planifiée. Point de reconnaissance. |

### Niveau 2 — le droit vérifié n'est pas celui de l'action (séparation de droits cassée)

| Module | Localisation | Écart |
|---|---|---|
| `api_etl` | `gql_mutations.py:26-30` | L'**exécution** d'un pipeline ETL (tire une source HTTP externe et **écrit** des `Individual`) est gardée par le droit de **lecture** 953001. Le droit d'exécution 953002 n'est vérifié nulle part. Tout rôle pouvant lister les pipelines peut les déclencher. |
| `individual` | `views.py:96-111` + `signals/...:112-195` | L'import d'individus, gardé par 159002 seul, appelle `GroupService.create` **et** `.update` — qui ne vérifient aucun droit. Un rôle sans 180002/180003 crée des groupes et **modifie la composition de groupes existants** par fichier. Même chemin en maker-checker. |
| `social_protection` | `views.py:105-314` (6 routes) | Les imports de **bénéficiaires** sont gardés par les droits du module `individual` (159001/159002). Tout rôle autorisé à créer des individus enrôle en masse dans un benefit plan et télécharge les fichiers d'upload — ce que la mutation GraphQL équivalente lui refuse. Les droits 170001/170002 existent et ne sont pas lus. |
| `individual` | `gql_mutations.py:557-567` | `ConfirmIndividualEnrollmentMutation` exige le droit de créer un **groupe** (180002) pour enrôler des **individus**. Ni la bonne entité ni le bon module. |
| `deduplication` | `gql_mutations.py:71` | La mutation *payment* contrôle 172001 (droit bénéficiaire) ; 172002 est déclaré et jamais vérifié → inopérant. Un rôle portant le droit prévu ne peut pas agir ; un rôle portant l'autre le peut. |
| `tasks_management` | `gql_queries.py:18-22` | `is_task_triage` concatène 4 droits et les passe à `has_perms`, **qui évalue en OU**. L'écriture se lit « détient les quatre », elle signifie « au moins un ». Un rôle portant le seul 190001 (lecture de l'annuaire des groupes) obtient la visibilité sur toutes les tâches, tout l'historique, tout le registre de votes — et peut **voter sur n'importe quelle tâche** (`gql_mutations.py:357`). |
| `invoice` | `gql/invoice_payment/mutation.py:51,66` | `UpdateInvoicePaymentMutation` / `Delete...` exigent le droit *invoice* (155103/155104) au lieu du droit *paiement* (155203/155204) — alors que le frère `Create` et les trois équivalents côté bill prennent bien celui du paiement. Incohérent dans les deux sens. |
| `contribution_plan` | `gql_types.py:134,140` | Deux resolvers de `PaymentPlanGQLType` exigent 151201 (*contribution plan*) au lieu de 157101 (*payment plan*) — leur voisin immédiat, lui, est correct. Copier-coller manqué. |
| `location` | `services.py:127-139` | Mettre à jour une localité exige de fait `update ET (create OU createRegion)` : le service réclame le droit de **création** que la mutation d'update n'a pas demandé. |
| `api_fhir_r4` | `permissions.py:165-166` | `PUT`/`PATCH` sur une Region/District par REST écrit directement sur le modèle sans passer par `LocationService`, donc sans le contrôle `createRegion` que GraphQL impose. Le chemin REST est plus permissif que le chemin GraphQL. |
| `api_fhir_r4` | `permissions.py:232-237` | `Group` POST/PUT : `GroupSerializer` appelle `InsureeService.create_or_update` pour chaque membre sous le seul droit Family. L'analogue GraphQL exige un droit Insuree. |
| `policyholder` | `apps.py:106-113` | **8 droits « portail » de mutation ne sont lus nulle part.** Les cases existent à l'écran des rôles et n'accordent rien ; pour que le portail fonctionne il faut donner le droit back-office, non scopé — l'inverse de l'intention. Fonctionnalité morte qui pousse à sur-habiliter. |
| `report` | `insuree/report.py:12-45` | Les 4 états du module insuree déclarent tous `"permission": ["131215"]`, alors que 131210 et 131216 leur sont assignés dans le catalogue. Ces deux ids n'accordent donc rien, et 131215 en ouvre quatre. Seul endroit où le droit d'un état vit **hors** du module report. |
| `report` | `schema.py:49-52` vs `40-47` | `resolve_reports` filtre état par état ; `resolve_report(name)` ne filtre pas. Le filtre par droit d'état est contournable en demandant l'état par son nom. Idem `resolve_definition`, qui renvoie le gabarit complet sous le seul 131200. |
| `tools` | `views.py:477-519` | `upload_enrollments` / `renewals` / `feedbacks` sont gardés par le droit du **registre des localités** puis par celui du téléversement des **demandes de remboursement** (`# TODO` sur place). Le cumul ferme plus qu'il n'ouvre, mais aucun des deux droits ne nomme l'action. |
| `tools` | `views.py:392-398` | `extracts_phone_extract_perms = ["131102","131103"]` en OU, sur une route dont le paramètre `with_insuree` change la nature de l'export : le porteur du droit faible obtient le contenu large. |
| `claim` | `schema.py:256-271` | `resolve_fsp_from_claim` et `resolve_claim_with_same_diagnosis` (qui renvoie une **liste de réclamations**, sans filtre de localisation) vérifient le droit « agents de saisie ». Sans effet aujourd'hui — les deux ids valent 111001 — mais faille dès dissociation. |
| `insuree` | `apps.py:75,117` | `gql_query_insuree_family_members` **ne porte pas le suffixe `_perms`** : la clé échappe au filtre anti-configuration, reste dans `DEFAULT_CFG`, et l'attribut de classe vaut `[]`. Le canal de reconfiguration que R4 devait fermer est rouvert par un nom mal formé, sur exactement la requête que la conversion avait corrigée. |
| `grievance` | `services.py:91,188,221` | **`GrievanceAccessControl` n'est appelé que sur 3 mutations sur 6.** `reopen_ticket`, `CommentService.create` et `resolve_grievance_by_comment` ne vérifient que le droit **global** du module (127002/127006) — celui que possède n'importe quel agent de grief. Rouvrir, commenter et **clôturer** un ticket d'une catégorie interdite échappent donc entièrement à la segmentation par catégorie, qui *est* le modèle de sécurité du module. |
| `grievance` | `access_control.py:169` | **Le repli par défaut promeut un droit de mutation en droit de lecture intégrale.** Sur une catégorie configurée `['restricted_read', 'read']` avec `visible_fields`, `get_user_access_level` teste create/update/delete, ne les trouve pas générés, retombe sur le droit global — et la seule possession de **127002** (droit banal) rend `ACCESS_FULL`, donc `visible_fields = None`, donc **aucun masquage**. `restricted_read` et toute la configuration de champs visibles sont annulés. |
| `grievance` | `validations.py:123-127` | `user_associated_with_ticket(user)` ne prend **pas de ticket en argument** : elle répond « est attending_staff de *quelque* ticket », jamais « de *ce* ticket ». Utilisée comme substitut de droit en `OR` à trois endroits (`schema.py:55`, `gql_queries.py:129`, `gql_mutations.py:139`), donc toujours pour élargir. Un agent affecté à un seul ticket lit les commentaires de tous. |
| `grievance` | update/delete | Fail-open sur catégorie inconnue : une catégorie absente de la configuration n'entraîne pas de refus. |
| `controls` ✓ | `gql_mutations.py:48-57,77` | `MOBILE_ENROLLMENT_RIGHTS` aplatit **8 droits de 3 autres modules** (insuree, policy, contribution) et les passe à `has_perms` avec `list_evaluation_or=True` **écrit explicitement**. Un seul de ces 8 suffit donc pour `mobileEnrollment`, qui crée en une transaction atomique une famille, ses assurés, ses polices **et** ses cotisations. Un rôle n'ayant que `contribution.update_premiums` enrôle des familles et crée des polices. Rien ne documente ce choix. |
| `payroll` | `views.py:18-20`, `:59`, `gql_mutations.py:288` | Trois emprunts de droit non dits : l'acquittement de la passerelle sous le droit de *créer* un payroll ; le GET du CSV de rapprochement sous le droit *create* (plus strict, mais 206001 devient inutile) ; la suppression d'une prestation sous le droit de suppression du payroll (héritage plausible, non documenté — et `_model = Payroll` est faux). |

### Niveau 3 — filtrage de lignes absent ou neutralisable

| Module | Localisation | Écart |
|---|---|---|
| `tasks_management` | `gql_queries.py:89-97`, `153-161` | La jointure `task_group__taskexecutor` ne filtre pas `taskexecutor__is_deleted=False`. `TaskExecutor` est un `HistoryModel` : **retirer un membre d'un groupe ne lui retire pas l'accès** aux tâches du groupe, `business_data` compris. Ces deux resolvers ne vérifient volontairement aucun droit : le `get_queryset` est l'unique contrôle. Le module contient la version correcte 180 lignes plus loin (`:333-337`), avec le commentaire qui décrit ce problème — le durcissement n'a pas été reporté sur les deux types dont il est copié. |
| `core` | `openIMIS/schema.py:54` + `gql_queries.py:144-306` | `node(id:)` atteint `InteractiveUserGQLType`, `RoleGQLType`, `RoleRightGQLType`… sans passer par les resolvers gardés. Les champs sensibles ont été rattrapés, mais `lastName`, `email`, `phone`, `loginName` n'ont pas de resolver et ne dépendent que d'un `get_queryset` lui-même conditionné à `ROW_SECURITY`. Énumération de l'état civil et des identifiants de connexion par global ID. |
| `core` | `models/user.py:215,239,996` | `if settings.ROW_SECURITY: pass` dans `Role`, `RoleRight` et `User.get_queryset` : la règle de portée a été prévue puis jamais écrite, et le seul filtrage réel (l'anonyme) est conditionné au réglage. C'est ce qui rend le point précédent exploitable. |
| `policyholder` | `models.py:43-148` | Même motif ×4 : garde anonyme conditionnée à `ROW_SECURITY`, puis `if settings.ROW_SECURITY: pass` sur 3 modèles. Seul `PolicyHolder` filtre réellement — donc **le filtrage du parent est contournable en interrogeant l'enfant**. Ces `get_queryset` sont réutilisés hors du module via `prefix_filterset` par `contract`, `payment`, `contribution_plan`. |
| `contribution_plan` | `models.py:47-104`, `mixins.py:24-28` | Même `if settings.ROW_SECURITY: pass`, aucun `row_scope` déclaré. |
| `invoice` | 10 GQLType | `get_queryset` défini **dans `class Meta`** : jamais appelé. 5 types sont sauvés par `ScopedQuerysetMixin` (le `Meta` y est du code mort) ; 5 ne le sont pas, dont 4 avec un repli `*_user_filter` qui vaut `None` par défaut. Voir §4.2. |
| `grievance` | `schema.py:55-61`, modèles | `resolve_comments` renvoie `Comment.objects.all()` — aucun filtrage, quel que soit le chemin d'entrée. Et les `get_queryset` des modèles sont conditionnés à `ROW_SECURITY` **et** jamais branchés : aucun type GraphQL ne porte `ScopedQuerysetMixin`, donc la row security du module est intégralement du code mort. C'est ce qui rend le point 11 du niveau 1 atteignable. |
| `im_export` | `views.py:37` | `export_insurees` exporte tout le queryset des assurés valides, sans filtrage par district (`# TODO` sur place), alors que le même droit de lecture est assorti d'une restriction géographique côté GraphQL. |

### Niveau 4 — contrôles absents à faible enjeu, non documentés

`core` — `resolve_password_policy` et `resolve_max_length_constraints` sans aucun contrôle
(probablement voulu pour l'écran pré-authentification, mais rien ne le dit) ;
`resolve_custom_filters` accepte un `module_name`/`object_type_name` arbitraires sous la
seule authentification. ~~`claim` — `claimAttachmentType` sans resolver ni `get_queryset`.~~ **corrigé**
~~`insuree` — `insureeStatusReasons`, seul point d'entrée du module sans contrôle.~~ **corrigé**
`location` — `resolve_client_mutation_id` sur `LocationGQLType` (son homologue formation
sanitaire, lui, exige un droit), référentiels statiques, `userDistricts`.
`payroll` — `resolve_payment_methods`, seul resolver du module sans droit.
~~`controls`~~ **corrigé** — `Query.control` (`schema.py:14`) n'avait **aucun resolver** et `ControlGQLType`
n'a ni `get_queryset` ni `ScopedQuerysetMixin`, alors que le modèle `Control` définit un
`get_queryset` — donc du code mort, exactement comme `medical.diagnoses`. Le frère
`control_str` est correctement gardé. Donnée de référence (paramétrage de formulaires),
enjeu faible, mais contrôle nul et atteignable anonymement.
`policyholder` — `services.py` : toutes les classes de service ne vérifient que
l'authentification, aucun `has_perms` ; non atteignable par un point d'entrée actuel,
mais c'est une API publique importable par tout autre module.

---

## 4. Motifs récurrents

Ce sont eux qui comptent : chaque motif produit la même faille dans plusieurs modules,
et se corrige une fois pour toutes.

### 4.1 `if settings.ROW_SECURITY: pass` — la règle prévue, jamais écrite

Trouvé dans `core` (3×), `policyholder` (3×), `contribution_plan` (3×), et sous une
variante conditionnée dans `claim` (3×), `claim_sampling` (3×) et `location`. Deux problèmes distincts, toujours
ensemble :

- la branche de portée est vide — le filtrage annoncé n'existe pas ;
- la garde anonyme, elle, est **conditionnée** à `ROW_SECURITY`, un réglage de
  déploiement pilotable par variable d'environnement.

`ROW_SECURITY` choisit un *périmètre de lignes*. Il ne doit jamais décider *si* l'on
contrôle. Dans `claim`, le `and settings.ROW_SECURITY` porte directement sur le
`has_perms` : avec le réglage à faux, le registre des réclamations n'est plus protégé
du tout.

### 4.2 `get_queryset` au mauvais endroit — code mort silencieux

`invoice` : 10 GQLType déclarent `get_queryset` **dans `class Meta`**. graphene-django ne
l'appelle que sur la classe du type et ne lit de `Meta` que les options qu'il connaît :
le code ne s'exécute jamais, sans la moindre erreur. L'intention était bonne (les corps
appellent correctement `Model.get_queryset`) — c'est une erreur d'emplacement.
Symétriquement, `medical.DiagnosisGQLType` et `controls.ControlGQLType` ont chacun un
`get_queryset` de modèle correct que le type n'emprunte pas, faute de `ScopedQuerysetMixin`.

Un test générique « tout `DjangoObjectType` dont le modèle déclare `get_queryset`
l'appelle effectivement » attraperait les deux formes.

### 4.3 `node(id:)` contourne tous les resolvers gardés

`core` et `tasks_management` le signalent indépendamment, et c'est un motif global :
`graphene.relay.Node.Field()` passe par `cls.get_queryset` et **jamais** par le resolver
de `Query`. Tout type sans `get_queryset` ni `ScopedQuerysetMixin` dont la protection
vit dans le resolver racine est récupérable à l'unité par global ID. C'est l'argument
central de `scoped_object_type.py` : la règle appartient au modèle, pas au resolver.

### 4.4 `has_perms` évalue en OU — l'écriture par concaténation ment

`tasks_management.is_task_triage`, `controls.MOBILE_ENROLLMENT_RIGHTS` et les 11 clés de
`tools` concatènent plusieurs ids et
les passent à `has_perms`, qui évalue en **OU** (`user.py:809`, `list_evaluation_or=True`).
La lecture naturelle est « détient tous ces droits » ; la sémantique est « au moins un ».
Dans `tools`, c'est ce qui fait qu'un droit de lecture donne l'écriture ; dans
`tasks_management`, qu'un droit de lecture d'annuaire donne le vote sur toute tâche ;
dans `controls`, qu'un droit sur les cotisations donne l'enrôlement d'une famille
complète. `controls` est le seul des trois à écrire `list_evaluation_or=True`
explicitement — donc à l'avoir choisi, sans le justifier.
`has_perms([])` renvoyant `True` est la même famille de piège.

### 4.5 REST plus permissif que GraphQL, sur les mêmes données

`core` (`UserViewSet`, corrigé), `api_fhir_r4` (Location `PUT`, Group `POST`),
`social_protection` (6 routes sous les droits `individual`), `tools` (écriture sur
`medical`/`location` sans leurs droits), `report` (previewer), `im_export` (pas de
filtre géographique). Le chemin GraphQL a été durci ; les chemins REST, écrits plus
tard ou ailleurs, ne l'ont pas suivi. C'est exactement ce que `Model.get_rights(action)`
devait résoudre — et le mécanisme existe, il n'est branché que sur 3 modules.

### 4.6 Un droit déclaré que personne ne lit

Recensé dans presque tous les modules : `policyholder` 12/37, `report` 9/24,
`medical_pricelist` 3, `contribution_plan` 3, `form_builder` 3, `calculation` 1,
`api_etl` 1, `deduplication` 1, `claim` 1, `product` 1 (121005 `duplicate`, alors que la
mutation exige le droit de création), `payment_cycle` 1, `tools` 1 (131100, l'id
canonique de la carte).

Ce n'est pas une faille en soi, mais ce n'est pas neutre : la case existe à l'écran des
rôles, elle donne l'illusion d'habiliter, elle n'accorde rien — et pour faire marcher la
fonction il faut accorder le droit voisin, plus large. **L'inventaire des droits morts
pousse mécaniquement à la sur-habilitation.** Chacun doit être soit branché, soit annoté
comme dormant (le motif de `medical_pricelist` 121200 est le bon).

### 4.7 Un manque de droit rapporté comme un défaut d'authentification

`api_etl`, `opensearch_reports`, `contribution_plan` lèvent `ValidationError` ou
`PermissionError("mutation.authentication_required")` là où le contrôle est bien un
contrôle de droit. Le contrôle s'applique — ce n'est pas un écart R8 — mais le message
est faux et rend le diagnostic d'habilitation impossible côté exploitation.

---

## 5. Ce qui reste à faire

### 5.1 Conversion (R1/R2/R3/R10)

14 modules restent à convertir. Aucun n'est une urgence de sécurité : `has_model_right`
échoue fermé quand rien n'est déclaré. Mais `core` est aujourd'hui le seul module à
déclarer `DJANGO_PERMS` **sans câbler ses propres modèles** (`User`, `Role`, `Officer`,
`ClaimAdmin` n'ont pas de `get_rights`), ce que `api_fhir_r4/rights.py:68-88` compense à
la main — précisément le doublon que la conversion devait supprimer.

`scope_parent` manque partout où il serait naturel et où son absence coûte déjà quelque
chose : `policyholder` (3 modèles avec un FK `policy_holder`), `claim` (9 sous-ressources
qui déclarent pourtant `row_scope = ParentScope(...)` côté lignes),
`contribution_plan.ContributionPlanBundleDetails` (l'exemple même de `rights_scope.py`,
deux FK dont une seule est le propriétaire), `invoice`, `payroll`, `medical_pricelist`.

### 5.2 Décisions à trancher

- **`tools` — 7 ids hors de la carte** (131000, 131002, 131004, 131006, 131008, 131010,
  131102). **Question résolue depuis, par la conversion** (`rights_conversion_compiled.md`
  §2.1) : la carte ne peut pas *exprimer* un identifiant empilé — le générateur écrase
  `permissions_map[key]` à chaque passe, seul le dernier de la pile survit. Les sept ne
  sont pas morts, ils sont inexprimables, et ils sont bien accordés (le front exige la
  paire en **ET**, les migrations `tools/0004`-`0005` en accordent trois). La vraie forme
  du problème : **l'interface est plus stricte que l'API** — le front demande les deux
  droits, le backend en accepte un seul, y compris pour réécrire. Reste à trancher : un
  identifiant par action, ou l'empilement conservé.
- **`report` — granularité.** Une entité par état avec une action `query`, ou une entité
  `report` avec 24 actions ? Et le lien avec `report_definitions[*]["permission"]` doit
  devenir explicite, sinon l'écart des 4 états insuree se reproduira.
- **`medical.diagnosis`** — identifiant dédié, ou donnée de référence ouverte comme les
  articles et services sous OMT-281 ?
- **`location`** — `locationsAll` et `healthFacilitiesStr` : exiger le droit, ou inscrire
  la dérogation et son ticket sur le resolver. Aujourd'hui ni l'un ni l'autre.
- **`grievance` — allocation des ids par catégorie.** La génération dynamique 127100-127999
  est saine et explicitement reconnue par `core/rights_sync.py` — ce n'est pas l'anomalie.
  Mais 127100 et 127102 sont codés en dur ailleurs alors que l'allocation dépend de
  l'**ordre** des catégories dans la configuration : deux déploiements avec les mêmes
  catégories dans un ordre différent n'attribuent pas les mêmes ids. À figer.
- **`deduplication`** — `Query.module_name = "tasks_management"` : le module se déclare
  sous le nom d'un autre. Sans effet observé, mais `module_name` sert d'ancrage côté core.

### 5.3 Exemptions à écrire

Plusieurs décisions sont défendables mais muettes, ce qui les rend invérifiables :
`location` `locationsStr` (OMT-281 non cité ici alors qu'il l'est deux fois dans le même
fichier), `claim` `SaveClaimReviewMutation` sous le droit *deliver*, `contract` `update`
acceptant le droit d'approbation, `medical_pricelist` les deux actions `duplicate`
dormantes, `contribution_plan` et `payroll` les héritages de sous-ressource,
`deduplication` l'emprunt de 170001 — dont un sur des données `payroll`.

---

### 5.4 Deux constats d'agent vérifiés et écartés

Signalés pour que personne ne les re-ouvre.

- **`grievance` É-7 et le même constat sur `individual`** — « `_merge_with_defaults` lit
  `instance._cfg`, la configuration **brute**, et contourne le filtre `_without_rights`
  qui n'est appliqué que par `get_or_default` ». C'était vrai, ça ne l'est plus : le
  filtre a été déplacé **dans `_cfg`** pendant l'audit (§2.2), au seul endroit où le JSON
  est décodé, précisément parce que le chemin de rechargement à chaud l'évitait. Les
  trois modules abonnés au reloader (`grievance_social_protection`, `individual`,
  `social_protection`) passent tous par `instance._cfg` et sont donc filtrés. Vérifié et
  verrouillé par un test dédié :
  `core/tests/test_rights_not_configurable.py::test_the_hot_reload_path_also_drops_a_stored_override`
  (9/9 OK), qui couvre aussi la réaffectation de `config` en place — le cas de l'admin.

- **`grievance` — `get_all_permissions()` devenu code mort** : exact, mais c'est une
  conséquence voulue de la déconfiguration, pas un écart.

### 5.5 Ordre de correction proposé

Rangé par « ce que ça ferme » / « ce que ça coûte », pas par module.

**Lot A — FAIT (§2.4).** Quatre lignes de code chacun, ferme une lecture ouverte.
`payer` (ajouter `resolve_fundings`), `medical` (`resolve_diagnoses`), `insuree`
(`insureeStatusReasons`), `claim` (`claimAttachmentType`), `medical_pricelist`
(refuser quand `hf is None` et lire 121200), `core` (`get_scheduled_jobs`),
`form_builder` (brancher 151002/151004 sur les deux resolvers de lecture), `controls`
(`resolve_control`).
Aucun de ces points n'avait d'appelant légitime sans droit.

**Lot B — décrocher `ROW_SECURITY` du contrôle de droit.** Les `and
settings.ROW_SECURITY` de `claim` (3), `claim_sampling` (3) et `location`, et les huit `if settings.ROW_SECURITY:
pass` de `core`, `policyholder`, `contribution_plan`. Mécanique, uniforme, testable
d'un coup par un test générique « aucun `has_perms` n'est conjoint à `settings.ROW_SECURITY` ».

**Lot C — les droits qui existent et que personne ne lit.** `controls`
(`MOBILE_ENROLLMENT_RIGHTS` : exiger les droits **de chaque objet créé**, en ET),
`api_etl` 953002,
`deduplication` 172002, `social_protection` 170001/170002 sur les 6 routes REST,
`invoice` 155203/155204, `contribution_plan` 157101, `product` 121005,
`policyholder` les 8 droits portail. Chacun est une ligne, mais **chacun change qui
peut faire quoi** : c'est le lot qui demande des fixtures de rôles à jour, donc à
grouper avec la migration opérationnelle déjà prévue.

**Lot D — les deux motifs structurels.** `get_queryset` dans `class Meta` (`invoice`,
10 types) et la non-couverture de `node(id:)` (`core`, `tasks_management`, `grievance`).
Ils se corrigent une fois et se verrouillent par un test générique sur le schéma —
c'est le meilleur rapport effort/couverture du lot.

**Lot E — `tools` et `report`.** Les deux demandent une décision avant du code
(§5.2) : séparation lecture/écriture des registres et des 7 ids empilés pour `tools`,
granularité par état pour `report`. À ne pas traiter au fil de l'eau.

## 6. Annexe — conformité par règle

`CONF` conforme · `ÉCART` écart · `NC` non converti (attendu) · `SO` sans objet

| module | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 |
|---|---|---|---|---|---|---|---|---|---|---|
| api_etl | NC | NC | NC | CONF | CONF | CONF | ÉCART | ÉCART | **ÉCART** | SO |
| api_fhir_r4 | NC | NC | NC | CONF | CONF | CONF | CONF | CONF | CONF | NC |
| calculation | NC | NC | NC | CONF | CONF | CONF | SO | CONF | CONF | SO |
| claim_batch | CONF | CONF | CONF | CONF | CONF | CONF | ÉCART | CONF | CONF | ÉCART |
| claim_sampling | NC | NC | NC | CONF | CONF | CONF | SO | **ÉCART** | CONF | NC |
| claim | CONF | CONF | CONF | CONF | CONF | CONF | CONF | **ÉCART** | **ÉCART** | ÉCART |
| contribution | CONF | CONF | CONF | CONF | CONF | CONF | SO | CONF | CONF | ÉCART |
| controls | NC | NC | NC | CONF | CONF | CONF | ÉCART | **ÉCART** | **ÉCART** | NC |
| contract | CONF | CONF | CONF | CONF | CONF | CONF | CONF | **ÉCART** | ÉCART | ÉCART |
| contribution_plan | NC | NC | NC | CONF | CONF | CONF | ÉCART | CONF | **ÉCART** | ÉCART |
| core | CONF | CONF | CONF | CONF | CONF | CONF | SO | **ÉCART** | CONF | ÉCART |
| deduplication | NC | NC | NC | CONF | CONF | CONF | ÉCART | **ÉCART** | ÉCART | SO |
| form_builder | NC | NC | NC | CONF | CONF | CONF | ÉCART | **ÉCART** | ÉCART | NC |
| grievance | NC | NC | NC | CONF | CONF | CONF | ÉCART | **ÉCART** | **ÉCART** | NC |
| im_export | SO | SO | SO | ÉCART | CONF | CONF | ÉCART | CONF | CONF | SO |
| individual | NC | NC | NC | CONF | CONF | CONF | ÉCART | CONF | **ÉCART** | NC |
| insuree | CONF | CONF | CONF | **ÉCART** | **ÉCART** | CONF | CONF | ÉCART | CONF | ÉCART |
| invoice | NC | NC | NC | CONF | CONF | CONF | ÉCART | CONF | **ÉCART** | **ÉCART** |
| location | CONF | CONF | CONF | CONF | CONF | CONF | SO | **ÉCART** | ÉCART | ÉCART |
| medical | CONF | CONF | CONF | CONF | ÉCART | CONF | SO | **ÉCART** | CONF | ÉCART |
| medical_pricelist | CONF | CONF | CONF | CONF | CONF | CONF | SO | **ÉCART** | CONF | ÉCART |
| opensearch_reports | NC | NC | NC | CONF | CONF | CONF | SO | CONF | CONF | NC |
| payroll | NC | NC | NC | CONF | CONF | ÉCART | ÉCART | ÉCART | ÉCART | NC |
| payer | CONF | CONF | CONF | CONF | CONF | CONF | CONF | **ÉCART** | ÉCART | ÉCART |
| payment | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | CONF | ÉCART |
| payment_cycle | CONF | CONF | CONF | CONF | CONF | CONF | SO | CONF | CONF | ÉCART |
| policy | CONF | CONF | CONF | CONF | CONF | CONF | ÉCART | CONF | CONF | ÉCART |
| policyholder | NC | NC | NC | CONF | CONF | CONF | SO | **ÉCART** | **ÉCART** | NC |
| product | CONF | CONF | CONF | CONF | CONF | CONF | SO | CONF | ÉCART | ÉCART |
| report | NC | NC | NC | CONF | CONF | CONF | ÉCART | **ÉCART** | ÉCART | NC |
| workflow | NC | NC | NC | CONF | CONF | CONF | SO | CONF | CONF | NC |
| social_protection | NC | NC | NC | ÉCART* | CONF | CONF | ÉCART | CONF | **ÉCART** | NC |
| tasks_management | NC | NC | NC | CONF | CONF | CONF | CONF | CONF | CONF | NC |
| tools | NC | NC | NC | CONF | CONF | ÉCART | ÉCART | **ÉCART** | **ÉCART** | NC |

\* corrigé pendant l'audit (§2.2).

R4, R5 et R6 sont conformes partout sauf trois cas nommés : `insuree` (une clé sans
suffixe `_perms`), `im_export` (deux clés mortes dans `DEFAULT_CFG`), `tools` et
`payroll` (ids empilés / partagés, décidés). **Le chantier de déconfiguration est tenu.**
