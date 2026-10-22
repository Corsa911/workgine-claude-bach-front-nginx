#!/usr/bin/env sh
# Первый запуск на Linux-сервере: секреты, сертификат Let's Encrypt, старт.
# Перед запуском: DNS-запись домена указывает на сервер, порты 80 и 443 открыты.
# Использование: DOMAIN=workgine.kz LETSENCRYPT_EMAIL=admin@workgine.kz ./setup-prod.sh
set -eu
cd "$(dirname "$0")"

if [ ! -f .env ]; then
  : "${DOMAIN:?Укажите DOMAIN=ваш.домен}"
  : "${LETSENCRYPT_EMAIL:?Укажите LETSENCRYPT_EMAIL=почта}"
  umask 077
  {
    echo "SECRET_KEY=$(openssl rand -hex 48)"
    echo "POSTGRES_PASSWORD=$(openssl rand -hex 24)"
    echo "DOMAIN=$DOMAIN"
    echo "LETSENCRYPT_EMAIL=$LETSENCRYPT_EMAIL"
    echo "DOCS_ENABLED=false"
  } > .env
  echo "Создан .env"
fi
set -a; . ./.env; set +a
mkdir -p backups

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"

if ! $COMPOSE run --rm --entrypoint test certbot -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem"; then
  echo "Выпускаю сертификат для $DOMAIN..."
  $COMPOSE run --rm -p 80:80 --entrypoint certbot certbot certonly --standalone \
    -d "$DOMAIN" -m "$LETSENCRYPT_EMAIL" --agree-tos --no-eff-email --non-interactive
fi

$COMPOSE up --build -d
echo "Готово: https://$DOMAIN"
