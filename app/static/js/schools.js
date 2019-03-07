// constructs the suggestion engine
var schools = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: schoolsJson
});

$('#search .schools-search').typeahead({
    hint: true,
    highlight: true,
    minLength: 3
    },
    {
    name: 'schools',
    display: 'name',
    source: schools,
    limit: 4,
    templates: {
        empty: [
            '<div class="school-result">',
                '<p>',
                    'Unable to find that school in NACCS',
                '</p>',
            '</div>'
          ].join('\n'),
        suggestion: function(school) {
                let html = [
                    '<div class="school-result">',
                        '<img class="school-logo">',
                        '<div class="school-info">',
                            '<div class="school-name">',
                                '' + school.name,
                            '</div>',
                            '<div class="school-location">',
                                'Placeholder',
                            '</div>',
                        '</div>',
                    '</div>'
                ].join('\n');
                return [
                    '<div class="school-result">',
                        '<img class="school-logo">',
                        '<div class="school-info">',
                            '<div class="school-name">',
                                school.name,
                            '</div>',
                            '<div class="school-location">',
                                'Placeholder',
                            '</div>',
                        '</div>',
                    '</div>'
                ].join('\n');
            }
        }
    }
);