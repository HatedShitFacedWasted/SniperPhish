FROM php:8.1-apache

# Install mysqli and other required extensions
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Enable Apache mod_rewrite for .htaccess support
RUN a2enmod rewrite

WORKDIR /var/www/html
