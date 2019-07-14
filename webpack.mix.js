const mix = require('laravel-mix');

mix.js('resources/js/app.js', 'static/assets/js')
   .sass('resources/sass/app.scss', 'static/assets/css');
