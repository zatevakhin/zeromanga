"use strict";


function MangaView() {
    this.mangaid = $("#article").data("mangaid");
    this.chash = undefined;
}


MangaView.prototype.run = function () {
    let self = this;

    $("#article").on('click', 'div.chaptlist > div', function (e) {
        self.chash = e.target.getAttribute("data-chaptid");
        self.show_thumbnails(self.chash);
    });

    $("body").on('click', 'div.chapt-thumb', function (e) {
        self.show_page(parseInt(e.target.getAttribute("data-image")));
    });

    let cover = $("div.cover");
    let current_n = parseInt(cover.data('current'));
    let covers_n = parseInt(cover.data('covers'));

    cover.append(aux.template("template-coverlist", {text: `${current_n} / ${covers_n}`}));

    let coverslist = cover.children("div.covers-list");

    coverslist.on("click", "div.covers-arrow-left", function (e) {
        current_n = parseInt(cover.data('current')) - 1;
        if (current_n > 0 && current_n <= covers_n) {
            cover.css("background-image", `url('/m/${self.mangaid}/c/${current_n}')`);
            cover.data("current", current_n);
            $('div.covers-text').text(`${current_n} / ${covers_n}`);
        }
    });

    coverslist.on("click", "div.covers-arrow-right", function (e) {
        current_n = parseInt(cover.data('current')) + 1;
        if (current_n > 0 && current_n <= covers_n) {
            cover.css("background-image", `url('/m/${self.mangaid}/c/${current_n}')`);
            cover.data("current", current_n);
            $('div.covers-text').text(`${current_n} / ${covers_n}`);
        }
    });
};


MangaView.prototype.show_page = function (imageid) {
    let self = this;

    if (!this.chash || (typeof this.chash) !== "string") {
        console.error("Var `chash` is undefined or not string: ", this.chash);
        return;
    }

    let image = new Image();
    image.src = `/p/${this.mangaid}/${this.chash}/${imageid}`;

    let mangapage = $('.manga-page');
    let mpimage = mangapage.children("img");

    if (!mangapage.length) {
        $("body").append(aux.template("template-page", {src: image.src}));
        mangapage = $('.manga-page');
        mpimage = mangapage.children("img");
    } else {
        mpimage.attr("src", image.src);
    }

    if (cookie.get("dfsid")) {
        $(`div.chapt-thumb[data-image='${imageid}']`).attr("data-readed", 1);

        let all = $("div.chapt-flexbox div.chapt-thumb").length;
        let readed = $("div.chapt-flexbox div.chapt-thumb[data-readed]").length;

        $(`div[data-chaptid=${this.chash}] span.viewer_chapts_reading`).text(`${readed} / ${all}`);
    }

    mangapage.on('click', 'div.manga-page-close', function (evt) {
        mangapage.off('click', 'div.manga-page-close');
        mangapage.remove();
    });

    mpimage.swipe({
        swipeLeft: function(event, direction, distance, duration, fingerCount) {
            console.log(arguments);

            if (fingerCount > 1) {
                return false;
            }

            let newid = imageid + 1;

            if ($(`div.chapt-thumb[data-image=${newid}]`).length) {
                self.show_page(newid);
                return;
            }

            let index = $(`div.chaptlist div[data-chaptid=${self.chash}]`).data("index");

            index = parseInt(index);

            let chapter = $(`div.chaptlist div[data-index=${index + 1}]`);

            if (chapter.length) {
                self.chash = chapter.data("chaptid");
                self.show_thumbnails(self.chash);
                self.show_page(1);
            }
        },
        swipeRight: function(event, direction, distance, duration, fingerCount) {
            console.log(arguments);

            if (fingerCount > 1) {
                return false;
            }

            let newid = imageid - 1;
            if ($(`div.chapt-thumb[data-image=${newid}]`).length) {
                self.show_page(newid);
                return;
            }

            let index = $(`div.chaptlist div[data-chaptid=${self.chash}]`).data("index");

            index = parseInt(index);

            let chapter = $(`div.chaptlist div[data-index=${index - 1}]`);

            if (chapter.length) {
                self.chash = chapter.data("chaptid");
                self.show_thumbnails(self.chash);

                setTimeout(function () {

                    let last = $("div.chapt-thumb[data-image]").last().data("image");

                    last = parseInt(last);

                    self.show_page(last);

                }, 500);
            }
        },
        swipeUp: function(event, direction, distance, duration, fingerCount) {
            let tpx = parseInt(mpimage.css("top"));
            if (tpx != tpx) {
                tpx = mpimage[0].offsetTop;
            }

            mpimage.animate({ "top": `${tpx - 100}px`}, 50, "linear");
        },
        swipeDown: function(event, direction, distance, duration, fingerCount) {
            let tpx = parseInt(mpimage.css("top"));
            if (tpx != tpx) {
                tpx = mpimage[0].offsetTop;
            }

            mpimage.animate({ "top": `${tpx + 100}px`}, 50, "linear");
        }
    });

    mpimage.swipe("option", {fingers: 1, allowPageScroll: 'none'});

    let x = { height: "auto", width: `${$(document).width() - 10}px`};
    mpimage.css(x);


};


MangaView.prototype.show_thumbnails = function (chash) {
    let self = this;

    let index = $(`div.chaptlist div[data-chaptid=${chash}]`).data("index");

    let jqxhr = $.post(`/manga/${this.mangaid}`, {"action": "get.thumbnails", "chash": chash});

    jqxhr.done(function (data) {

        let chapter_view = $("#chapter-view");

        if (!chapter_view.length) {
            $("body").append(aux.template("template-chapter", {
                mhash: self.mangaid,
                chash: data.chash
            }));

            chapter_view = $("#chapter-view");
        } else {
            chapter_view.children("div.chapt-blur").css({
                "background-image": `url('/r/${self.mangaid}/${data.chash}')`
            })
        }

        let chapt_flexbox = $("div.chapt-flexbox");

        chapt_flexbox.empty();
        for (let i = 1; i <= data.pages; ++i) {
            chapt_flexbox.append(aux.template("template-thumbnail", {
                mhash: self.mangaid,
                chash: data.chash,
                image: i
            }));
        }

        if (data["readed"] && typeof data["readed"] == 'object') {
            data["readed"].forEach(function (item) {
                $(`div.chapt-thumb[data-image='${item}']`).attr("data-readed", 1);
            });
        }

        $(".chapter-controls").on('click', 'span[data-action=close]', function (evt) {
            $(".chapter-controls").off('click', 'span[data-action=close]');
            $("#chapter-view").remove();
        });

    });
};

$(function () {
    let app = new MangaView();
    app.run();
});

