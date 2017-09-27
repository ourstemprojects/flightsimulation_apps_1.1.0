
-- QUERY USED TO PLOT THE PLAYER'S PROFILE GRAPH
SELECT
      name
    , actualprofiledata
    , targetprofiledata
    , gamehighscore
FROM
    gamedata
WHERE
    completiontime = (SELECT MAX(completiontime) FROM gamedata WHERE profiled = 0)
