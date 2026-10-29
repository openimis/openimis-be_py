# Tâche générique : convertir un module à `DJANGO_PERMS`

Pendant : `docs_rights_module_checklist.md` **constate** (règles R1→R10) ; cette
tâche-ci **corrige**. Le module à convertir est donné en paramètre ; son code est dans
`/mnt/data/Development/openimis-dev-tools/backend-packages/<module>/`.

## Ce qui est déjà vrai, et ce qui ne l'est pas

Les modules cités ont **déjà** passé l'étape « droits déconfigurés » : leurs droits sont
des constantes de classe, `DEFAULT_CFG` n'en contient plus, `ready()` n'en charge plus.
Vérifie-le et ne le refais pas. Ce qui manque est la **déclaration hiérarchique** :
`DJANGO_PERMS`, `_PERM_CFG`, `RIGHTS`, et l'accès par le modèle (`get_rights`).

## Pourquoi, en trois faits

1. **`has_perms([])` renvoie `True`.** Une liste vide n'interdit rien, elle **accorde à
   tout le monde**. C'est la cause de la majorité des failles de l'audit.
2. **Un identifiant est ce que portent les rôles** (`RoleRight.right_id`, un entier).
   Le changer retire l'accès à tous les rôles qui le détiennent.
3. **Le nom django est déclaratif.** C'est l'entier qui est appliqué aujourd'hui ; le
   nom est posé à côté, prêt pour le jour où les droits passeront dans les tables de
   django. Les deux vivent ensemble pour ne pas pouvoir diverger.

## La cible

Référence canonique : `backend-packages/product/product/apps.py`. Reproduis cette forme.

```python
from core.rights_declaration import RightsDeclaration

MODULE_NAME = "product"

# Droits, par entite puis par action. <une phrase par choix non evident>
DJANGO_PERMS = {
    "product": {
        "query":  ("product.view_product",      121001),
        "create": ("product.add_product",       121002),
        "update": ("product.change_product",    121003),
        "delete": ("product.delete_product",    121004),
        "duplicate": ("product.duplicate_product", 121005),
    },
}

_PERM_CFG = {
    "gql_query_products_perms":           ("product", "query"),
    "gql_mutation_products_add_perms":    ("product", "create"),
    ...
}

RIGHTS = RightsDeclaration(MODULE_NAME, DJANGO_PERMS, _PERM_CFG)

perms = RIGHTS.perms
django_perms = RIGHTS.django_perm_names
configured_perms = RIGHTS.configured
require = RIGHTS.require


class ProductConfig(AppConfig):
    name = MODULE_NAME

    # Droits: constantes, plus surchargeables.
    gql_query_products_perms = RIGHTS.perms("product", "query")
    ...
```

`RightsDeclaration` **refuse au chargement** une clé de `_PERM_CFG` qui pointe une
action non déclarée : une erreur de frappe casse le démarrage plutôt que d'ouvrir un
droit. C'est voulu.

## Étapes

### 1. Inventorier l'existant — ne rien inventer
Liste les clés `*_perms` de la classe de config et leur valeur actuelle. Pour chacune,
trouve **tous** ses sites d'appel (`grep -rn "<clé>" backend-packages/`). Une clé que
personne ne lit est une **déclaration dormante** : conserve-la, et annote-la (voir 6).

### 2. Nommer les entités et les actions
Une entité = un objet métier, en `camelCase` (`paymentPlan`, `benefitPlan`). Les actions
canoniques sont `query` / `create` / `update` / `delete` — le vocabulaire de django. Tout
le reste est une action métier, nommée par ce qu'elle fait (`submit`, `approve`,
`duplicate`, `replace`, `execute`). **Ne force pas** une action métier dans un verbe
canonique : `execute` n'est pas `update`.

### 3. Les noms django
`app_label.verbe_modele` en minuscules : `view_`/`add_`/`change_`/`delete_` pour les
quatre canoniques, le nom de l'action pour les autres (`api_etl.execute_apietlrule`).
L'`app_label` est celui du modèle dans **cet assemblage**, pas le nom du paquet pip.
Vérifie-le sur le modèle (`Meta.app_label`, sinon le nom de l'app). Les actions non
canoniques ne deviennent des droits django accordables que si le modèle les déclare dans
`Meta.permissions` — on ne le fait **pas** maintenant ; le nom reste déclaratif.

### 4. Les identifiants : **inchangés**
Reprends exactement l'entier actuel. Contrôle-le contre
`backend/openIMIS/permissions_map.json`. Si tu dois en créer un (droit manquant, clé
sans identifiant) :
- reste dans le bloc du module, prends le premier libre ;
- vérifie qu'il est libre dans **tout** `permissions_map.json` ;
- écris sur place, en commentaire, *pourquoi* il est neuf.

Si un identifiant est **partagé** entre deux actions, ce n'est pas une erreur en soi :
plusieurs noms django peuvent pointer le même entier (c'est ce que permet
`RightPermission`, dont le `right_id` est indexé mais **non unique**). Mais le partage
doit être **écrit** sur place — sinon on ne peut pas distinguer un alias voulu d'un
copier-coller.

### 5. Accès par le modèle (`get_rights`)
Sur le modèle principal de chaque entité :

```python
@classmethod
def get_rights(cls, action):
    from <module>.apps import configured_perms
    return configured_perms("<entite>", action)
```

**Lis la config dans la méthode, jamais à l'import** : les attributs `_perms` ne
valent leur valeur qu'après `ready()`, et un instantané pris à l'import capture le
placeholder — donc une liste vide, donc un droit accordé à tous.

Une sous-ressource déclare le FK qui la possède plutôt que ses propres droits :

```python
class ContractDetails(HistoryModel):
    contract = models.ForeignKey(Contract, ...)
    scope_parent = "contract"
```

Le parent est **déclaré et non déduit** : `ContractDetails` a trois FK et un seul est le
propriétaire. Ne déclare un `scope_parent` que si tu peux dire lequel, et pourquoi.

### 6. Commenter ce qui n'est pas évident
Sur place, pas dans le rapport : un identifiant partagé, une action métier, un droit
dormant, un identifiant neuf, un emprunt au droit d'un autre module. Une phrase suffit,
mais elle doit dire **pourquoi**, pas répéter le code.

### 7. Un test de non-régression
`<module>/tests/test_permission_declarations.py`, sur le modèle de
`claim/tests/test_permission_declarations.py` : il épingle chaque identifiant et la
correspondance avec `permissions_map.json`. C'est ce qui rend un changement d'entier
visible en revue.

## Interdits

- **Ne touche pas à `core/`** ni à un autre module que le tien.
- **Ne régénère pas `permissions_map.json`** — plusieurs agents travaillent en
  parallèle, la carte sera régénérée une fois à la fin.
- **Ne change aucun identifiant existant** sans le dire explicitement dans ton rapport.
- **Ne corrige pas les failles d'autorisation** relevées par l'audit (droit manquant sur
  un resolver, `ROW_SECURITY` couplé au contrôle, etc.) : c'est un autre lot, et les
  mélanger rend la revue impossible. Signale-les, ne les touche pas.
- Ne renomme pas les clés `*_perms` : d'autres modules et les tests les importent.

## Vérifier

```bash
cd /mnt/data/Development/openimis-dev-tools/backend/openIMIS
python manage.py test <module> --keepdb
python manage.py test core.tests.test_rights_not_configurable core.tests.test_rights_declaration --keepdb
```

Les deux doivent passer. Si un test échoue **avant** ta modification, dis-le et ne le
compte pas pour toi.

## Rapport

Écris `<répertoire scratchpad>/rights_conversion/<module>.md` :

1. **Verdict** — converti / partiellement / bloqué, en une phrase.
2. **Tableau des entités** : entité | action | nom django | identifiant | clé de config |
   inchangé ?
3. **Décisions** — action métier plutôt que canonique, identifiant partagé, identifiant
   neuf, `scope_parent` retenu ou écarté, et pourquoi.
4. **Non fait** — ce que tu n'as pas pu convertir, et ce qui manque pour le faire.
5. **Tests** — la commande et son résultat.

Sois franc sur ce qui reste incertain : un « je n'ai pas su trancher » est utile, une
conversion inventée ne l'est pas.
