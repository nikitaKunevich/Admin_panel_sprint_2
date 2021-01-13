set -a
. deploys/dev.env
set +a

case $1 in
  start)
    ./run.sh stop
    docker-compose up -d
    docker-compose exec movies /bin/sh -c 'echo "running ETL"; cd /etl; python load_data.py --from db.sqlite --to "dbname=${PG_DB} user=${PG_USER} host=${PG_HOST} password=${PG_PASS}" --init postgres_init.sql'
    docker-compose exec movies ./manage.py migrate
    docker-compose exec movies ./manage.py collectstatic --no-input
    docker-compose exec movies /bin/sh -c 'echo "creating admin user"'
    docker-compose exec movies ./manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('${ADMIN}', 'admin@example.com', '${ADMIN_PASS}')"
    docker-compose logs -f
  ;;
  stop)
    docker-compose down -v --remove-orphans
  ;;
  *)
    echo "Use 'start' command"
esac
