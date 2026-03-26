(function() {
    var scripts = {{ scripts | tojson | safe }};
    scripts.forEach(function(src) {
        var s = document.createElement('script');
        s.src = src;
        s.async = false; // Preserves execution order
        document.head.appendChild(s);
    });
})();
