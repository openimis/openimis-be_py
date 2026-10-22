# Tâche générique : conformité d'un module à la déclaration des droits

Vérifier qu'un module openIMIS respecte les règles ci-dessous, et **rapporter** les
écarts. Ne rien modifier : cette tâche produit un constat, pas un correctif.

Le module à vérifier est donné en paramètre. Son code est dans
`/mnt/data/Development/openimis-dev-tools/backend-packages/<module>/`.

## Contexte : pourquoi ces règles

Un droit openIMIS est un **entier** porté par les rôles (`RoleRight.right_id`) et
comparé par `core.models.user.User.has_perms`. Trois propriétés de ce mécanisme
expliquent toutes les règles :

1. **`has_perms([])` renvoie `True`.** Une liste de droits vide n'interdit rien : elle
   **accorde l'action à tout le monde**, authentifié ou non. C'est la cause de la
   majorité des failles trouvées dans l'audit.
2. **Les droits ne sont plus configurables.** `ModuleConfiguration.get_or_default`
   retire toute clé `_perms` stockée en base (y compris imbriquée). Un droit est une
   **constante** posée à la définition de la classe de config.
3. **Un identifiant est ce que portent les rôles.** Le changer casse l'accès de tous
   les rôles qui le détiennent. On ne le change que délibérément.

## Les règles

### R1 — Déclaration hiérarchique
`apps.py` définit `DJANGO_PERMS = {entité: {action: (nom_django, id_entier)}}`, où le
nom django suit la convention de django : `app_label.verbe_modele`
(`claim.view_claim`), avec `view/add/change/delete` pour query/create/update/delete.

### R2 — Table de correspondance des clés
`_PERM_CFG = {clé_de_config: (entité, action)}` couvre **exactement** les actions
déclarées dans `DJANGO_PERMS` — ni plus, ni moins.

### R3 — Déclaration branchée
`RIGHTS = RightsDeclaration(MODULE_NAME, DJANGO_PERMS, _PERM_CFG)`, avec les alias
`perms`, `django_perms`, `configured_perms`, `require`.

### R4 — Constantes, pas de config
Chaque clé de `_PERM_CFG` est un attribut de la classe de config valant
`RIGHTS.perms("entité", "action")`. **Aucune clé `_perms` ne subsiste dans
`DEFAULT_CFG`/`DEFAULT_CONFIG`**, ni au premier niveau ni imbriquée, et `ready()` ne
charge plus de droit depuis la config.

### R5 — Aucun droit vide
Aucune liste de droits vide. Une exception doit être **documentée sur place** avec sa
raison (cf. `medical.gql_query_diagnosis_perms`).

### R6 — Identifiants inchangés
Les identifiants sont ceux d'avant conversion. Tout changement doit être intentionnel
et expliqué. Comparer avec `backend/openIMIS/permissions_map.json`.

### R7 — Partages visibles
Quand plusieurs actions partagent un identifiant, la hiérarchie le rend lisible et un
commentaire dit pourquoi (même objet, même action vue de deux endroits ; ou
réutilisation du droit d'un autre module). Chaque action garde un **nom django
distinct** : plusieurs permissions peuvent pointer un même entier.

### R8 — Tout point d'entrée vérifie un droit
Chaque resolver de `Query` et chaque mutation exposée vérifie un droit — directement,
via un helper, ou via le service qu'elle appelle. Signaler :
- l'absence totale de contrôle ;
- un contrôle **commenté** (il ne compte pas) ;
- un contrôle conditionné à `settings.ROW_SECURITY` (le contrôle lui-même cesse alors
  de s'appliquer) ;
- un helper `_check_permissions` **défini mais jamais appelé**.

### R9 — Le droit vérifié correspond à l'action
Une lecture ne doit pas exiger un droit de mutation, une mise à jour ne doit pas
vérifier le droit de création. Les synonymes du module (`add`≡`create`,
`edit`≡`update`) sont acceptables ; une sous-ressource peut légitimement prendre le
droit de son parent (attacher une pièce à une réclamation = modifier la réclamation),
mais cela doit être dit.

### R10 — Accès par le modèle, si pertinent
Quand le module a des modèles, `Model.get_rights(action)` délègue à
`configured_perms(...)` et ne redéclare rien. Une sous-ressource déclare
`scope_parent = "<champ_fk>"` pour hériter des droits de son propriétaire.

## Ce qu'il faut rapporter

Pour chaque règle : **conforme**, **écart**, ou **sans objet**. Pour chaque écart,
donner `fichier:ligne`, ce qui est constaté, et pourquoi c'est un problème.

Distinguer nettement :
- ce qui est **cassé** (une faille : droit vide, contrôle absent ou commenté) ;
- ce qui est **non converti** (le module n'a pas encore `DJANGO_PERMS` — attendu, pas
  une faille) ;
- ce qui est **délibéré et documenté** (exemption OMT-281, alias voulu).

Ne pas signaler comme écart ce qu'un commentaire sur place justifie déjà.

## Méthode

Lire `apps.py`, les `schema.py` / `gql_queries.py` / `gql_mutations.py`, les
`services.py` et les `models.py` du module. Se référer à `core/core/apps.py`,
`core/core/rights_declaration.py` et `core/core/rights_sync.py` pour la forme de
référence, et à `claim/claim/apps.py` pour un module converti représentatif.

Un contrôle peut vivre dans le service appelé par la mutation : vérifier avant de
conclure à son absence. Retirer les commentaires avant de juger qu'un contrôle existe.
