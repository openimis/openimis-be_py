-- Remove duplicated rows in "tblRole", keeping the row that is actually
-- referenced by "tblUserRole" and re-pointing every other reference to it.
--
-- Keeper rule, per "RoleName": the live role (ValidityTo IS NULL) with the most
-- live tblUserRole assignments; ties broken by the lowest RoleID (the seeded one).
--
-- Runs inside a transaction and ends with ROLLBACK: inspect the reports, then
-- swap the last statement for COMMIT.

BEGIN;

CREATE TEMP TABLE role_dedup ON COMMIT DROP AS
WITH usage AS (
    SELECT r."RoleID",
           r."RoleName",
           count(ur."UserRoleID") AS n_users
    FROM "tblRole" r
    LEFT JOIN "tblUserRole" ur
           ON ur."RoleID" = r."RoleID"
          AND ur."ValidityTo" IS NULL
    WHERE r."ValidityTo" IS NULL
    GROUP BY r."RoleID", r."RoleName"
),
keeper AS (
    SELECT DISTINCT ON ("RoleName")
           "RoleName",
           "RoleID" AS keep_id
    FROM usage
    ORDER BY "RoleName", n_users DESC, "RoleID" ASC
)
SELECT r."RoleID" AS dup_id,
       k.keep_id,
       k."RoleName"
FROM "tblRole" r
JOIN keeper k ON k."RoleName" = r."RoleName"
WHERE r."RoleID" <> k.keep_id;

-- ---------------------------------------------------------------- reports --
-- What will be kept and how many rows disappear per role name.
SELECT "RoleName", keep_id, count(*) AS rows_removed
FROM role_dedup GROUP BY 1, 2 ORDER BY 1;

-- Rights held ONLY by a duplicate: these are dropped by the script below.
-- If any line shows up and matters, use the MERGE variant instead.
SELECT d."RoleName", d.keep_id, rr."RightID", count(*) AS on_n_duplicates
FROM role_dedup d
JOIN "tblRoleRight" rr ON rr."RoleID" = d.dup_id AND rr."ValidityTo" IS NULL
WHERE NOT EXISTS (
    SELECT 1 FROM "tblRoleRight" k
    WHERE k."RoleID" = d.keep_id AND k."RightID" = rr."RightID"
      AND k."ValidityTo" IS NULL)
GROUP BY 1, 2, 3 ORDER BY 1, 3;

-- ------------------------------------------------------- tblUserRole remap --
UPDATE "tblUserRole" ur
SET "RoleID" = d.keep_id
FROM role_dedup d
WHERE ur."RoleID" = d.dup_id;

-- collapse assignments that became identical, keeping the live one
DELETE FROM "tblUserRole"
WHERE "UserRoleID" IN (
    SELECT "UserRoleID" FROM (
        SELECT ur."UserRoleID",
               row_number() OVER (PARTITION BY ur."UserID", ur."RoleID"
                                  ORDER BY (ur."ValidityTo" IS NULL) DESC,
                                           ur."UserRoleID") AS rn
        FROM "tblUserRole" ur
        WHERE ur."RoleID" IN (SELECT keep_id FROM role_dedup)
    ) t WHERE t.rn > 1);

-- ------------------------------------------------------ tblRoleRight remap --
-- Default: the keeper's rights win, the duplicates' rights are dropped.
DELETE FROM "tblRoleRight" rr
USING role_dedup d
WHERE rr."RoleID" = d.dup_id;

-- MERGE variant (union of rights) -- replace the DELETE above with:
--   UPDATE "tblRoleRight" rr SET "RoleID" = d.keep_id
--     FROM role_dedup d WHERE rr."RoleID" = d.dup_id;
--   DELETE FROM "tblRoleRight" WHERE "RoleRightID" IN (
--       SELECT "RoleRightID" FROM (
--           SELECT rr."RoleRightID",
--                  row_number() OVER (PARTITION BY rr."RoleID", rr."RightID"
--                                     ORDER BY (rr."ValidityTo" IS NULL) DESC,
--                                              rr."RoleRightID") AS rn
--           FROM "tblRoleRight" rr
--           WHERE rr."RoleID" IN (SELECT keep_id FROM role_dedup)
--       ) t WHERE t.rn > 1);

-- ------------------------------------------- remaining (soft) references --
UPDATE "tblUsers" u
SET "RoleID" = d.keep_id
FROM role_dedup d WHERE u."RoleID" = d.dup_id;

UPDATE "core_historicalinteractiveuser" h
SET "RoleID" = d.keep_id
FROM role_dedup d WHERE h."RoleID" = d.dup_id;

UPDATE "core_RoleMutation" m
SET role_id = d.keep_id
FROM role_dedup d WHERE m.role_id = d.dup_id;

-- version chains pointing at a row about to vanish
UPDATE "tblRole" r
SET "LegacyID" = NULL
FROM role_dedup d WHERE r."LegacyID" = d.dup_id;

-- ------------------------------------------------------------- the delete --
DELETE FROM "tblRole" r
USING role_dedup d
WHERE r."RoleID" = d.dup_id;

-- ------------------------------------------------------------ verification --
SELECT count(*) AS still_duplicated FROM (
    SELECT "RoleName" FROM "tblRole" GROUP BY 1 HAVING count(*) > 1) t;

SELECT count(*) AS orphan_user_roles
FROM "tblUserRole" ur
WHERE NOT EXISTS (SELECT 1 FROM "tblRole" r WHERE r."RoleID" = ur."RoleID");

SELECT count(*) AS orphan_role_rights
FROM "tblRoleRight" rr
WHERE NOT EXISTS (SELECT 1 FROM "tblRole" r WHERE r."RoleID" = rr."RoleID");

ROLLBACK;  -- <- change to COMMIT once the reports look right

-- ---------------------------------------------------------------------------
-- Second line of defence, run AFTER the dedup above is committed.
--
-- core migration 0020 declares RoleUUID unique, but tblRole was still
-- managed = False at that point (0021_set_managed_to_true came later), so the
-- AlterField never reached the database and no unique index exists. That is why
-- re-running the fixtures could insert the very same UUIDs over and over.
--
-- Check first, then create:
--   SELECT "RoleUUID", count(*) FROM "tblRole" GROUP BY 1 HAVING count(*) > 1;
--
-- CREATE UNIQUE INDEX CONCURRENTLY "tblRole_RoleUUID_uniq" ON "tblRole" ("RoleUUID");
