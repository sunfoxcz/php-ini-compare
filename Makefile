NAME = sunfoxcz/php-ini-diff

#.PHONY: all php56 php70 php71 php72 php73

all: ubuntu16-native-php70 ubuntu16-sury-php56 ubuntu16-sury-php70 ubuntu16-sury-php71 ubuntu16-sury-php72 ubuntu16-sury-php73

ubuntu16-native-php70:
	docker build -t $(NAME):$@ --rm -f docker/ubuntu-16.04/native-7.0/Dockerfile .
	docker run -it -v $(PWD):/app --user $(UID):$(GID) $(NAME):$@ runuser -u app -- php -n /app/src/save-ini-settings.php $@

ubuntu16-sury-php56:
	docker build -t $(NAME):$@ --rm -f docker/ubuntu-16.04/sury-5.6/Dockerfile .
	docker run -it -v $(PWD):/app --user $(UID):$(GID) $(NAME):$@ runuser -u app -- php -n /app/src/save-ini-settings.php $@

ubuntu16-sury-php70:
	docker build -t $(NAME):$@ --rm -f docker/ubuntu-16.04/sury-7.0/Dockerfile .
	docker run -it -v $(PWD):/app --user $(UID):$(GID) $(NAME):$@ runuser -u app -- php -n /app/src/save-ini-settings.php $@

ubuntu16-sury-php71:
	docker build -t $(NAME):$@ --rm -f docker/ubuntu-16.04/sury-7.1/Dockerfile .
	docker run -it -v $(PWD):/app --user $(UID):$(GID) $(NAME):$@ runuser -u app -- php -n /app/src/save-ini-settings.php $@

ubuntu16-sury-php72:
	docker build -t $(NAME):$@ --rm -f docker/ubuntu-16.04/sury-7.2/Dockerfile .
	docker run -it -v $(PWD):/app --user $(UID):$(GID) $(NAME):$@ runuser -u app -- php -n /app/src/save-ini-settings.php $@

ubuntu16-sury-php73:
	docker build -t $(NAME):$@ --rm -f docker/ubuntu-16.04/sury-7.3/Dockerfile .
	docker run -it -v $(PWD):/app --user $(UID):$(GID) $(NAME):$@ runuser -u app -- php -n /app/src/save-ini-settings.php $@
