# auth_db on Postgres

FROM postgres:17.5

ENV POSTGRES_USER=rangiffler
ENV POSTGRES_PASSWORD=rangiffler
ENV POSTGRES_DB=auth_db

