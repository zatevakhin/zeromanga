"use strict";

class MangaIndex {

    constructor() {
        zk.listen();

        zk.set("paging::next", "arrowright", () => {
            let offset = this.offset + this.page_articles;
            Hash.set({"O": (offset >= this.count ? this.offset : offset)});
        });

        zk.set("paging::prev", "arrowleft", () => {
            let offset = this.offset - this.page_articles;
            Hash.set({"O": (offset > 0 ? offset : 0)});
        });

        this.count = cookie.get("manga-cnt") || 0;
        cookie.remove("manga-cnt");

        this.page_articles = 20;

        this.st_title = ["Выпуск манги продолжается", "Манга завершена"];
        this.tr_title = ["Перевод манги продолжается", "Перевод манги завершен"];
    }

    static showLoading() {
        $("body > .loading").remove();
        $("body").append(aux.template("tt-loading"));
    }

    static hideLoading() {
        $("body > .loading").fadeOut(500, function () {
            $(this).remove();
        });
    }

    get offset() {
        let offset = parseInt(Hash.get("O")) || 0;
        return ((offset && offset >= 0 && offset <= this.count) ? offset : 0);
    }

    loadArticles() {
        $.post("/", {action: "load", articles: this.page_articles, offset: this.offset})
            .always(MangaIndex.hideLoading)
            .fail(MangaIndex.hideLoading)
            .done((data) => {
                if (JSON.isjson(data)) {
                    this.renderArticles(JSON.parse(data));
                }
            });
    }

    renderArticles(data) {
        $("body > .articles").empty()
            .append(data.map((manga) => {
                return aux.template("tt-article", {
                    cover: aux.rand(1, manga.covers + 1),
                    tr_title: this.tr_title[ +manga.translation ],
                    st_title: this.st_title[ +manga.state ],
                    translation: manga.translation,
                    short: manga.title.cut(50),
                    state: manga.state,
                    mhash: manga.mhash,
                    title: manga.title
                });
            }));
    }

    * generatePagination() {
        for (let i = 0, j = 0; i < this.count; i += this.page_articles, j++) {
            yield {"page": j, "offset": i};
        }
    }

    renderPagination() {
        let pagination = $("body .nav__pagination");
        pagination.empty();

        for (let item of this.generatePagination()) {
            pagination.append(
                aux.template(item.offset === this.offset ? "tt-paging-span" : "tt-paging-link", item)
            );
        }
    }

    displayAll() {
        MangaIndex.showLoading();
        this.renderPagination();
        this.loadArticles();
    }

    run() {
        this.displayAll();
        $(window).on("hashchange", () => {
            this.displayAll();
        });

        zk.bind("paging::next", "paging::prev");
    }
}

$(() => {
    let app = new MangaIndex();
    app.run();
});
