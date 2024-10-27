#!/bin/bash

if ! [ -f db.db ]; then
  alembic revision --autogenerate -m "New revision"
  alembic upgrade head
fi
