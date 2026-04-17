FETCH_USER_DB_BY_USER_ID = """
SELECT  db.host, db.port, db.database_name,db.username,
db.dialect,db.password_encrypted
FROM db_connections db
JOIN workspace_members wm 
ON db.workspace_id = wm.workspace_id
WHERE wm.user_id = :id
"""