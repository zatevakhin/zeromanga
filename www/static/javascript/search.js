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

    $("div.searchform").on('click', 'input[type=button]', function (evt) {
       self.find();
    });

    $("#found").on('click', 'div.article', function (evt) {
        if (!(evt.target.className === "article")) {
            return;
        }

        let mangaid = $(this).data("mangaid");
        window.location.href = `/manga/${mangaid}`;
    });
};

MSearch.prototype.find = function () {
    let search = { text: "", genres: {include: [], exclude: []}};

    search.text = $(".searchform .search input").val();

    $(".genres span[data-include]").each(function (i, e) {
        search.genres.include.push(parseInt(e.getAttribute("data-id")));
    });

    $(".genres span[data-exclude]").each(function (i, e) {
        search.genres.exclude.push(parseInt(e.getAttribute("data-id")));
    });

    $.post("/search", {data: JSON.stringify(search), action: 'search'})
        .done(this.display_found);
};

MSearch.prototype.display_found = function (data) {
    if (data) {
        let mangalist = data.result;
        let found = $("#found");

        found.empty();

        for (let i in mangalist) {
            if (mangalist.hasOwnProperty(i)) {
                let manga = mangalist[i];
                let coverrange = aux.range(1, manga["covers"] + 1);
                let cover = `/m/${manga.mhash}/c/${coverrange.rand()}`;

                found.append(aux.template("template-found", {
                    shorttitle: manga.title.cut(50),
                    mhash: manga.mhash,
                    title: manga.title,
                    cover: cover
                }));
            }
        }
    }
};

$(function () {
    let app = new MSearch();
    app.run();
});
