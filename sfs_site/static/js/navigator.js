
// Hack until MaterializeCss provides an api to know if fixed sidebar is will always be visible at the current screen size.
const FIXED_SIDENAV_ALWAYS_ON_WIDTH = 992;

Item = function(element, index) {
    this.element = element;
    this.index = index;
};


Navigator = function() {
    this.request = null;
    this.items_by_href = {};
    this.on_page_loaded = function(){};
    this.loading_view = null;
    this.content = null;
    this.active_item = null;
    this.previous_active_item = null;
    this.close_sidenav_after_choice = false;
};

Navigator.prototype.handle_click = function(event) {
    event.preventDefault();
    const item = event.target.closest('li').dataItem;
    this.load_page(event.target.href, item);

    // Hide side-menu, See Hack note above.
    if (window.innerWidth <= FIXED_SIDENAV_ALWAYS_ON_WIDTH) {
        const sidenav = M.Sidenav.getInstance(document.querySelector('.sidenav'));
        sidenav.close();
    }
};

Navigator.prototype.setup = function() {
    this.loading_view = document.querySelector('.progress');
    this.content = document.querySelector('#content');
    this.active_item = null;

    window.onpopstate = this.handle_popstate.bind(this);

    const addItemFromElement = (element, sectionIndex) => {
        const item = new Item(element, sectionIndex);
        element.dataItem = item;
        const anchor = element.querySelector('a');
        this.items_by_href[anchor.href] = item;
        if (element.classList.contains('current-page')) {
            this.active_item = item;
        }
    }

    const collapsibleElement = document.querySelector('nav .collapsible');
    let sectionIndex = 0;
    Array.from(collapsibleElement.children).forEach(section => {
        if (!section.matches('li')) {
            return;
        }
        addItemFromElement(section, sectionIndex);
        section.querySelectorAll('li').forEach(child => addItemFromElement(child, sectionIndex));
        ++sectionIndex;
    });

    if (this.active_item !== null) {
        collapsibleElement.children[this.active_item.index].classList.add('active');
    }

    // Need sepearate event handlers per anchor due to the inablility of materialize
    // to turn off auto opening/closing of collapsibles on click.
    // Separate event handler at the anchor level allows us to stop propagation.
    // https://github.com/Dogfalo/materialize/issues/1996
    document.querySelectorAll('nav .collapsible li a').forEach(el => {
        el.addEventListener('click', event => {
            this.handle_click(event);
            event.preventDefault();
            event.stopPropagation();
        });
    });
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

    this.previous_active_item = this.active_item;
    this.active_item = item;

    this.show_loading_view();

    if (!from_pop) {
        history.pushState({url: url}, '', url);
    }

    const result = SFSUtil.promiseHttp('GET', url + '?fragment=true');
    this.request = result.request;
    result.promise.catch(() => this.load_error())
        .then(response => this.load_success(item, url, response));
};

Navigator.prototype.load_success = function(item, url, response) {
    this.request = null;

    // TODO: This isn't amazing, success should be determined outside of the 'on success' method.
    if (response.status !== 200) {
        this.load_error();
        return;
    }

    const response_object = JSON.parse(response.responseText);
    this.set_content(response_object.content);
    document.title = response_object.title;
    this.hide_loading_view();

    if (this.previous_active_item === null || this.previous_active_item.index !== item.index) {
        if (this.previous_active_item !== null) {
            const previous_collapsible = M.Collapsible.getInstance(this.previous_active_item.element.closest('.collapsible'));
            if (this.can_toggle_collapsible_section(this.previous_active_item)) {
                previous_collapsible.close(this.previous_active_item.index);
            }
        }

        const new_collapsible = M.Collapsible.getInstance(item.element.closest('.collapsible'));
        if (this.can_toggle_collapsible_section(item)) {
            new_collapsible.open(item.index);
        }
    }

    if (this.previous_active_item !== null) {
        this.previous_active_item.element.classList.remove('current-page');
    }
    item.element.classList.add('current-page')

    this.on_page_loaded(response_object.title, url);
};

Navigator.prototype.load_error = function() {
    this.request = null;
    this.hide_loading_view();
    // TODO: Need to surface this in a more user friendly way.
    //alert('There was an issue loading the requested page. Please refresh to try again.');
};

Navigator.prototype.can_toggle_collapsible_section = function(item) {
    const section = item.element.closest('.collapsible').children[item.index];
    const header = section.querySelector('.collapsible-header');
    const body = section.querySelector('.collapsible-body');
    return header !== null && body !== null;
};

Navigator.prototype.set_content = function(content) {
    this.content.innerHTML = content;
};

Navigator.prototype.handle_popstate = function(event) {
    if (!event.state) {
        window.location.href = document.URL;
        return;
    }
    const url = event.state.url;
    const item = this.items_by_href[url];
    this.load_page(url, item, true);
};
