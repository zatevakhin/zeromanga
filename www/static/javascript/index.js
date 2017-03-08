"use strict";

function MangaClient() {
    this.count = cookie.get("manga-cnt") || 0;
    cookie.del("manga-cnt");
    this.articles = 20;
}

MangaClient.prototype.run = function () {
    let self = this;
    this.showLoading();

    this.load();

    this.bindLinks();

    this.displayPagination();

    let offset = parseInt(Hash.get("O")) || 0;

    $('div.pagination').find(`a[href="#O:${offset}"]`).addClass('current');

    $("#articles").on('click', 'div.article-info', function (evt) {
        evt.stopPropagation();
    });

    $(window).on("hashchange", function () {
        self.showLoading();
        $("#articles").empty();
        self.load();
    });
};


MangaClient.prototype.showLoading = function () {
    $("#loading").remove();
    $("body").append(aux.template("template-loading"));
};

MangaClient.prototype.load = function () {
    let self = this;
    let offset = parseInt(Hash.get("O")) || 0;
    offset = ((offset && offset >= 0 && offset <= this.count) ? offset : 0 );

    let jqxhr = $.post("/", {action:"load", articles: 20, offset: offset});
    jqxhr.done(function (data) {
        self.displayPage(data);
    });

    jqxhr.fail = this.loadingEnd;
    jqxhr.always = this.loadingEnd;
};

MangaClient.prototype.genPagination = function () {
    let pagin = [];
    for (let i = 0, j = 0; i < this.count; i += this.articles, j++) {
        pagin.push({"page": j, "offset": i});
    }
    return pagin;
};

MangaClient.prototype.displayPagination = function () {
    let pagination = this.genPagination();

    for (let i = 0; i < pagination.length; i++) {
        let obj = pagination[i];
        $("<a/>", {
            "href": `#O:${obj.offset}`,
            "data-page": obj.page,
            "text": obj.page
        }).appendTo('div.pagination');
    }

    $("div.pagination").on("click", "a", function () {
        $('div.pagination a').removeClass('current');
        $(this).addClass("current")
    })
};

MangaClient.prototype.bindLinks = function () {
    $("#articles").on('click', 'div.article', function (evt) {
        if (!(evt.target.className == "article")) {
            return;
        }

        let mangaid = $(this).data("mangaid");
        window.location.href = `/manga/${mangaid}`;
    });
};

MangaClient.prototype.loadingEnd = function () {
    $("#loading").fadeOut(500, function () {
        $(this).remove();
    });
};

MangaClient.prototype.displayPage = function (data) {
    if (data && JSON.isjson(data)) {
        let mangalist = JSON.parse(data);

        for (let i in mangalist) {
            if (mangalist.hasOwnProperty(i)) {
                let manga = mangalist[i];
                let coverrange = aux.range(1, manga["covers"] + 1);
                let cover = `/m/${manga.mhash}/c/${coverrange.rand()}`;

                $("#articles").append(aux.template("template-article", {
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
    let mcApp = new MangaClient();
    mcApp.run();
});
