docsearch({
    appId: 'Y6L7HQ2HZO',
    apiKey: '9a1fd3379e6d318ef4f46aa36a3c5fe6',
    indexName: 'ploomber_jupysql',
    // Replace inputSelector with a CSS selector
    // matching your search input
    inputSelector: 'input[type=search]#search-input',
    // Set debug to true if you want to inspect the dropdown
    debug: false,
    searchParameters : {
      hitsPerPage: 10
    }
  });