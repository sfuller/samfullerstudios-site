

(function(){
    var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;

    var CollapseController = function() {
        this.options = {
            subtree: false,
            attributes: true
        };

        this.observer = new MutationObserver(function(mutations) {
            mutations.forEach(this.attribute_changed.bind(this));
        }.bind(this));

    };

    CollapseController.prototype.observe = function(element) {
        this.observer.observe(element, this.options);

        var $element = $(element);
        if (!$element.hasClass('open')) {
            $element.children('.collapsible-body').css('display', 'none');
        }
    };


    CollapseController.prototype.attribute_changed = function(mutation) {
        if (mutation.attributeName != 'class') {
            return
        }

        var $element = $(mutation.target);
        if ($element.hasClass('open')) {
            $element.children('.collapsible-body').stop(true,false).slideDown({ duration: 350, easing: "easeOutQuart", queue: false, complete: function() {$(this).css('height', '');}});
        } else {
            $element.children('.collapsible-body').stop(true,false).slideUp({ duration: 350, easing: "easeOutQuart", queue: false, complete: function() {
                $(this).css('height', '');
            }});
        }
    };

    window.CollapseController = CollapseController
}());

(function(){
    var controller = new CollapseController();
    $('.collapsible').each(function(i, obj){
        controller.observe(obj);
    });
}());