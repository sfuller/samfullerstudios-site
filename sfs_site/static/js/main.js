

(function(){
    var navigator = new Navigator();

    var on_load = function(title, url) {
        ga('set', { page: url, title: title});
        ga('send', 'pageview');
        $('.parallax').parallax();
        $('.materialboxed').materialbox();
    };
    navigator.on_page_loaded = on_load;

    $(function() {
        navigator.setup();
        ga('create', 'UA-9260053-4', 'auto');
        on_load();
        $('.button-collapse').sideNav();
    });
}());
