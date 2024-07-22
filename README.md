### Парсинг страницы

* Бренды собираются по `<div class='brands'>`, в нем содержатся все ссылки на бренды. 
* Страницы собираются по `<ul class='page-number'>`, в нем содержатся все ссылки на страницы. 
* Товары собираются по `<div class='products products-catalog'>`. 

### Парсинг товара 

* Сам продукт содержится в `<div class='product-item'>`, в нем есть ссылка на сам товар.
* Все характеристики содержатся в `<div class='sidebar-content__info'>`.
* Описание содержится `<div class='woocommerce-Tabs-panel woocommerce-Tabs-panel--description panel entry-content wc-tab'>`.
* Все картинки товара содержатся в `<ol class='flex-control-nav flex-control-thumbs'>`
