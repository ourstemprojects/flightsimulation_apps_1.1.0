
CREATE TABLE IF NOT EXISTS avatardata (
      rownum            INTEGER  PRIMARY KEY  AUTO_INCREMENT  UNIQUE  NOT NULL
    , datecreated       DATETIME
    , name              VARCHAR(35)
    , queueposition     INTEGER
    , status            VARCHAR(20)
    , gamehighscore     FLOAT
    , colour            VARCHAR(15)
    , animal            VARCHAR(15)
    , number            VARCHAR(2)
    , email             VARCHAR(50)
    , phone             VARCHAR(20)
    , avatar            BLOB
    , completiontime    INTEGER
)
