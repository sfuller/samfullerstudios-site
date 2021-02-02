(function(){
    const navigator = new Navigator();

    const on_load = function(title, url) {
        ga('set', { page: url, title: title});
        ga('send', 'pageview');
        M.Parallax.init(document.querySelectorAll('.parallax'), {});
        M.Materialbox.init(document.querySelectorAll('.materialboxed'), {});
    };
    navigator.on_page_loaded = on_load;

    document.addEventListener('DOMContentLoaded', function() {
        navigator.setup();
        ga('create', 'UA-9260053-4', 'auto');
        on_load();

        M.Sidenav.init(document.querySelectorAll('.sidenav'), {});
        M.Collapsible.init(document.querySelectorAll('.collapsible'));
    });
}());
