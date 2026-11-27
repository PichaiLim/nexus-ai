\getenv app_password NEXUS_DB_APP_PASSWORD
CREATE ROLE nexus_app LOGIN PASSWORD :'app_password';
GRANT CONNECT ON DATABASE nexus_ai TO nexus_app;
GRANT USAGE, CREATE ON SCHEMA public TO nexus_app;
