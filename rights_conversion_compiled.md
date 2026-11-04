# Conversion à `DJANGO_PERMS` — synthèse des 18 modules

Un agent par module, contre `docs_rights_conversion_task.md`. Ce document compile leurs
rapports ; les rapports individuels sont dans le répertoire de travail de la session
(`scratchpad/rights_conversion/<module>.md`).

## 1. Résultat

**18 modules sur 18 convertis.** `DJANGO_PERMS` + `_PERM_CFG` + `RIGHTS` en place partout,
`get_rights` posé sur les modèles, `scope_parent` déclaré là où une sous-ressource a un
propriétaire identifiable.

| | |
|---|---|
| Modules convertis ce tour | 19 (18 + `calculation`) |
| Modules portant `DJANGO_PERMS` au total | **33 — tous les modules porteurs de droits** |
| Entités déclarées ce tour | 75 |
| Actions déclarées ce tour | 216 |
| Identifiants modifiés | **0** |
| Identifiants créés | **0** |
| Tests | **1753 OK** (18 modules + `core`, une seule exécution) |

**La carte des permissions régénérée est identique au bit près** — 352 entrées, aucune
clé ajoutée ou retirée, aucune valeur changée. C'est la preuve la plus forte disponible
que la conversion n'a touché ni un identifiant ni un nom de clé de config : la carte est
construite à partir des clés `*_perms`, donc le moindre renommage ou changement d'entier
l'aurait fait bouger.

| module | entités | actions | note |
|---|---:|---:|---|
| `api_etl` | 1 | 2 | action `execute` désormais distincte de `query` |
| `api_fhir_r4` | 1 | 4 | n'a qu'une entité propre : la souscription |
| `claim_sampling` | 1 | 4 | `approve` en action métier |
| `contribution_plan` | 3 | 18 | 3 blocs disjoints, `scope_parent` sur les détails de bundle |
| `controls` | 1 | 1 | |
| `deduplication` | 2 | 2 | deux entités, pas une à deux actions |
| `form_builder` | 3 | 5 | `design` / `submit` en actions métier |
| `grievance_social_protection` | 2 | 7 | statiques seuls ; génération dynamique intacte |
| `individual` | 2 | 9 | `individual` / `group` séparés |
| `invoice` | 6 | 34 | 6 blocs disjoints |
| `opensearch_reports` | 1 | 2 | |
| `payroll` | 4 | 13 | partage 202004 déclaré explicitement |
| `policyholder` | 4 | 37 | variantes back-office / portail en actions distinctes |
| `report` | 24 | 27 | une entité par état — décision de conception, §3 |
| `social_protection` | 5 | 20 | `close` / `enroll` / `timeEntry` en actions métier |
| `tasks_management` | 3 | 12 | |
| `tools` | 11 | 18 | option sans régression, décision ouverte, §3 |
| `workflow` | 1 | 1 | pas de modèle : `get_rights` sans objet |
| `calculation` | 1 | 2 | hors liste initiale ; pas de modèle non plus |

---

## 2. Ce que la conversion a mis au jour

### 2.1 La carte des permissions ne peut pas exprimer un identifiant empilé

Le point le plus important du lot, et il **corrige une question laissée ouverte par
l'audit**. `rights_audit_compiled.md` demandait, à propos de `tools` : « les 7
identifiants absents de la carte — la carte est-elle la cible, ou décrit-elle un état
incomplet ? » Ni l'un ni l'autre. Le générateur
(`core/management/commands/generate_permissions_map.py`) fait :

```python
if isinstance(perm_ids, list):
    for perm_id in perm_ids:
        permissions_map[key] = perm_id     # chaque passe ecrase la precedente
```

Une clé ne peut donc porter qu'**un** identifiant : le dernier de la pile. Les sept ne
sont pas morts, ils sont **inexprimables**.

Et ils sont bien vivants — trois preuves indépendantes, vérifiées :

- `frontend-packages/ToolsModule/src/pages/RegistersPage.jsx:93` définit
  `hasRights = (list) => list.every(x => rights.includes(x))` — un **ET** — et l'applique
  à `RIGHT_REGISTERS_DIAGNOSES = [131002, 131001]`. Si les pairs n'étaient accordés nulle
  part, la page Registres serait vide pour tout le monde.
- La numérotation openIMIS : `01/02` diagnostics, `03/04` formations sanitaires, `05/06`
  localités, `07/08` articles, `09/10` actes — impair = lecture, pair = écriture, comme
  partout ailleurs.
- Les migrations `tools/0004` et `0005` accordent 131000, 131008 et 131010.

**Conséquence, et c'est la vraie forme du problème `tools`** : l'interface est plus
stricte que l'API. Le front exige les **deux** droits pour afficher un registre ; le
backend, qui évalue la pile en **OU**, en accepte **un seul** pour agir — y compris pour
réécrire le registre.

### 2.2 Un test qui dépendait de l'ordre d'exécution

`core.tests.test_rights_sync` a échoué à la première exécution combinée. Diagnostic :
`install()` appelle bien `sync_right_permissions()` depuis le `ready()` de core, mais à
ce moment le runner n'a pas encore basculé sur la base de test — cette synchro-là porte
sur la base de développement. Le relais prévu, `rerun_after_migrate`, ne se déclenche pas
sous `--keepdb` puisqu'il n'y a pas de migration. Ces tests ne passaient donc que si un
test antérieur du même run avait lui-même synchronisé.

Invisible tant qu'aucun droit nouveau n'était déclaré ; la conversion l'a révélé. Au
passage, `test_running_twice_changes_nothing` relevait ses compteurs **avant** toute
synchro — il mesurait autre chose que l'idempotence.

**Corrigé** : `setUp` synchronise. L'invariant vérifié devient « après synchronisation,
tout ce qui est déclaré est correspondu » au lieu de « la base se trouve être à jour ».
Rien à changer en production : `ready()` synchronise contre la vraie base à chaque
démarrage.

### 2.3 Deux bugs préexistants, trouvés en passant

- **`payroll/schema.py:274`** lit `PayrollConfig.payment_gateway_base_url`, alors que
  l'attribut s'appelle `gateway_base_url`. `resolve_payment_gateway_config` lève donc un
  `AttributeError` **même pour un utilisateur autorisé** : la lecture de la configuration
  de passerelle est cassée aujourd'hui. Non corrigé (hors lot).
- **`grievance` — l'allocation dynamique dépend de l'ordre.** `_get_next_available_id`
  part de `127100 + suffixe` et avance dans l'ordre de parcours de `grievance_types` :
  c'est la **position** qui décide de l'entier, pas l'identité de la catégorie. Or 127100
  et 127102 sont codés en dur à trois endroits. Un rôle exporté d'un déploiement et
  importé dans un autre peut accorder l'accès à la **mauvaise catégorie**. La stabilité
  est intra-déploiement, pas inter-déploiements.

---

## 3. Les trois décisions de conception

### `report` — une entité par état

24 entités (23 états + `report` pour le CRUD du gabarit), plutôt qu'une entité `report` à
24 actions. Le critère était de rendre visible le lien avec
`report_definitions[*]["permission"]`, aujourd'hui un entier nu : avec 24 actions la table
de correspondance aurait pointé `("report", <action>)`, couple dont la moitié est
constante, et aurait remis les 23 états et le CRUD du gabarit sous la même entité —
exactement la confusion qui a masqué le bug des 4 états insuree.

La pièce qui matérialise le lien : `CATALOGUE_STATES` (nom du rapport → entité) +
`catalogue_state_rights(name)`, l'équivalent de `get_rights` pour une entité sans modèle.
Deux tests l'épinglent, dont un qui fait échouer la suite si un état sort du catalogue en
silence.

### `tools` — option sans régression, décision laissée ouverte

Les onze piles sont déclarées telles quelles, décomposées en actions nommées mais
recomposées à l'identique sur la classe de config : aucun rôle ne perd d'accès. L'option
« un identifiant par action » reste recommandée mais **non appliquée** — c'est une
migration de droits, pas une conversion. Ce qu'elle casserait, précisément : le rôle 32
(qui ne porte que 131000) perd les 12 routes registres/export ; tout rôle ne portant que
l'identifiant pair perd le téléchargement ; deux rôles de test de `core/test_helpers.py`
perdent l'écriture en silence ; les 3 routes hybrides et les 4 export/import Excel
demandent le même découpage ; la carte doit être régénérée et les rôles déployés
re-semés ; et le **ET** du front doit changer en même temps.

### `grievance` — frontière statique / dynamique

Les 7 droits statiques (127000-127006) sont déclarés ; la plage 127100-127999 reste à la
génération dynamique, intacte. La frontière est écrite en commentaire et **verrouillée par
deux tests** : aucun entier déclaré ne tombe dans la plage dynamique, et 127100/127102
restent hors de `_PERM_CFG`.

---

## 4. Ce que les agents ont refusé de faire, à raison

Trois refus valent d'être connus, parce qu'ils corrigent des suggestions que je leur avais
faites ou qu'un lecteur pressé aurait appliquées :

- **`payroll` a refusé `scope_parent = "payroll"` sur `BenefitConsumption`** — je le lui
  avais suggéré. Il l'a démontré faux : ce modèle n'a aucune relation `payroll` (sa seule
  FK est `individual`, le lien passe par la table de jonction `PayrollBenefitConsumption`).
  `scope_parent_of` aurait journalisé une erreur et renvoyé `None`, donc `has_model_right`
  aurait **tout refusé**. Remplacé par un `get_rights` explicite.
- **`social_protection` a écarté `scope_parent` partout** : il hérite l'action *de même
  nom*, donc `scope_parent = "project"` sur les inscriptions ferait passer la création par
  `project.create` (209002) là où le site d'appel exige `project.enroll` (209005).
- **`form_builder` a écarté `scope_parent` sur `FormSubmission`** : l'hériter de
  `FormDefinition` ferait de tout lecteur de formulaire un lecteur des réponses.

Deux autres jugements notables : `deduplication` a **prouvé** que
`Query.module_name = "tasks_management"` est sans effet sur l'ancrage des droits plutôt
que de « nettoyer » la ligne ; et `opensearch_reports` a refusé d'aligner un message
d'erreur au motif que `mutation.authentication_required` est une clé de traduction
partagée par 124 sites — la diverger dans un seul module aurait créé une exception, pas
une amélioration.

---

## 5. Ce qui reste

### Plus aucun module porteur de droits n'est hors déclaration
**`calculation`** — absent de la liste initiale — a été converti à la suite : 2 droits
(153001 lecture, 153003 dormant, le module n'expose aucune mutation), pas de modèle donc
pas de `get_rights`, test de non-régression ajouté. `im_export` et `dhis2_etl` ne
déclarent aucun droit propre : rien à convertir. **Le chantier de déclaration est
complet.**

### Décisions en attente
`tools` (option (a) ou (b) définitivement), `report` (recâbler le catalogue sur
`catalogue_state_rights`, ce qui remettrait 131210 et 131216 en service),
`policyholder` (154501 / 154901 rattachés à `policyHolder` faute de mieux — leur place
juste serait dans `payment` et `insuree`), `grievance` (figer une sous-plage pour la
catégorie par défaut, ce qui permettrait de déclarer 127100/127102 sans risque).

### Le lot suivant
Les failles d'autorisation relevées par l'audit restent **toutes** ouvertes : les agents
avaient consigne de les signaler sans y toucher, pour que la revue de conversion ne soit
pas mêlée à des changements de comportement. `rights_audit_compiled.md` les classe par
gravité ; le lot A y est fait, les lots B à E restent.

### Droits dormants
Recensés et annotés module par module plutôt que supprimés : ils servent de registre
nom → identifiant pour le semis des rôles. Les plus notables : `report` 9, `policyholder`
4 + 8 portail, `invoice` 12, `contribution_plan` 3, `tasks_management` 2 (accordées par
migration et lues par le front, donc à conserver), `form_builder` 1, `api_etl` 1,
`social_protection` 1.
