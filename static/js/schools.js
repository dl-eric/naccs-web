// constructs the suggestion engine
var schools = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
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
source: schools
});