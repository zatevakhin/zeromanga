"use strict";


function MSearch() {

}

MSearch.prototype.run = function () {
    let self = this;

    $("div.searchform div.genres").on('click', 'span', function (evt) {
        if (this.hasAttribute("data-include")) {
            this.removeAttribute("data-include");
            this.setAttribute("data-exclude", "");

        } else if (this.hasAttribute("data-exclude")) {
            this.removeAttribute("data-include");
            this.removeAttribute("data-exclude");

        } else {
            this.removeAttribute("data-exclude");
            this.setAttribute("data-include", "");
        }
    });

    $("div.searchform div.find").on('click', 'input[type=button]', function (evt) {
       self.find();
    });
};

MSearch.prototype.find = function () {
    let search = { text: "", genres: {include: [], exclude: []}};

    search.text = $(".searchform .search input").val();

    $(".genres span[data-include]").each(function (i, e) {
        search.genres.include.push(e.getAttribute("data-id"));
    });

    $(".genres span[data-exclude]").each(function (i, e) {
        search.genres.exclude.push(e.getAttribute("data-id"));
    });

    let jqxhr = $.post("/search", {
        data:  btoa(JSON.stringify(search)),
        action: 'search'
    });

    jqxhr.done(function () {
        console.log(arguments);
    });

    //
    // jqxhr.fail = this.loadingEnd;
    // jqxhr.always = this.loadingEnd;
};



$(function () {
    let app = new MSearch();
    app.run();
});
