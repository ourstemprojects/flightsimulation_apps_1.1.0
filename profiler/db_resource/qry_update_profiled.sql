
-- QUERY USED TO UPDATE A PLAYER'S PROFILED FLAG
UPDATE
    gamedata
SET
    profiled = 1
WHERE
    name = %s
