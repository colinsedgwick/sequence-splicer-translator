PORT ?= 8050

filter:
	docker ps --filter "expose=${PORT}"  --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"

compose-down:
	docker compose down

compose-up:
	docker compose up --build -d

compose: compose-down compose-up
