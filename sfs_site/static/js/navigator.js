

Navigator = function() {
    this.request = null;
    this.items_by_href = {};
    this.on_page_loaded = function(){};
};

Navigator.prototype.handle_click = function(event) {
    event.preventDefault();
    var item = $(event.target).parents('li').get(0);
    this.load_page(event.target.href, item);

    // Hide side-menu
    $('.button-collapse').sideNav('hide');
};

Navigator.prototype.setup = function() {
    this.loading_view = $('.progress').get(0);
    this.content = $('#content').get(0);
    this.active_item = $('nav * li.active').get(0);

    window.onpopstate = this.handle_popstate.bind(this);

    var cb = this.handle_click.bind(this);
    $.each($('nav * li'), function(i, el) {
        var anchor = $('a', el).get(0);
        this.items_by_href[anchor.href] = el;
    }.bind(this));
    $('nav * li a').on('click', cb);
};

Navigator.prototype.show_loading_view = function() {
    this.loading_view.style.visibility = 'visible';
};

Navigator.prototype.hide_loading_view = function() {
    this.loading_view.style.visibility = 'hidden';
};

Navigator.prototype.load_page = function(url, item, from_pop) {
    if (this.request != null) {
        this.request.abort();
    }

    if (url.substr(url.length - 1, 1) !== '/') {
        url += '/';
    }

    var $active_item = $(this.active_item);
    $active_item.removeClass('active');
    this.previous_active_item = this.active_item;
    this.active_item = item;

    this.show_loading_view();

    if (!from_pop) {
        history.pushState({url: url}, '', url);
    }

    this.request = $.ajax({
        type: 'GET',
        url: url + '?fragment=true',
        success: this.load_success.bind(this, item, url),
        error: this.load_error.bind(this)
    });
};

Navigator.prototype.load_success = function(item, url, response) {
    this.request = null;
    this.set_content(response.content);
    document.title = response.title;
    this.hide_loading_view();

    var $item = $(item);
    var $previous_item = $(this.previous_active_item);
    var previous_closest = $previous_item.closest('.collapsible');
    var closest = $item.closest('.collapsible');
    if (previous_closest.get(0) !== closest.get(0)) {
        previous_closest.removeClass('open');
        closest.addClass('open');
    }
    $item.addClass('active');

    this.on_page_loaded(response.title, url);
};

Navigator.prototype.load_error = function() {
    this.request = null;
    this.hide_loading_view();
};

Navigator.prototype.set_content = function(content) {
    this.content.innerHTML = content;
};

Navigator.prototype.handle_popstate = function(event) {
    if (!event.state) {
        return;
    }
    var url = event.state.url;
    var item = this.items_by_href[url];
    this.load_page(url, item, true);
};
