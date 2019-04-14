['//code.jquery.com/jquery-1.11.0.min.js',
    typeaheadLink,
    schoolsLink
].forEach(function(item, index) {
    let script = document.createElement('script');
    script.src = item;
    script.async = false;
    
    document.head.appendChild(script);
});