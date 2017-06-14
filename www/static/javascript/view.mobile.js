"use strict";

class CMangaView
{
    constructor()
    {
        let article = $("#article");

        this.mhash = article.data("mangaid");
        this.covers = parseInt(article.find("div.cover").data("covers"));
        this.current = {};
    }

    run()
    {
        $("#article").on("click", "div.chaptlist > div", (e) => {
            this.showChapter($(e.target).data("chaptid"));
        });

        $(document).on("fullscreenchange", function() {
            let mangaPage = $("#manga-page");
            let chapterView = $("#chapter-view");

            let fullscreen = "<div data-action='fullscreen' class='fa fa-expand'></div>";
            
            let pageControls = mangaPage.find(".page-controls");
            let chapterControls = chapterView.find(".chapter-controls");

            if (!$.fullscreen.isFullScreen()) {
                pageControls.append(fullscreen);
                chapterControls.append(fullscreen);
            } else {
                pageControls.find("div[data-action='fullscreen']").remove();
                chapterControls.find("div[data-action='fullscreen']").remove();
            }
        });
    }

    showChapter(chash, page)
    {
        $("body").fullscreen();

        let request = $.post(`/manga/${this.mhash}`, {
            "action": "get.thumbnails", "chash": chash
        });

        if (!$("#chapter-view").length) {
            $("body").append(aux.template("tt-chapter"));
        }

        let chapterView = $("#chapter-view");
        
        chapterView.on("click", "div.chapt-thumb", (e) => {
            this.showPage(chash, parseInt($(e.target).data("image")));
        });

        chapterView.find(".chapter-controls")
            .on("click", "div[data-action=close]", () => {
                chapterView.off("click");
                $.fullscreen.exit();
                chapterView.remove();
            })
            .on("click", "div[data-action='fullscreen']", () => {
                $("body").fullscreen();
            });

        chapterView.find("div.chapt-blur").css({
            "background-image": `url(/r/${this.mhash}/${chash})`
        });

        let chapterFlexbox = chapterView.find("div.chapt-flexbox");

        let pageLoaders = {
            first: data => this.showPage(data.chash, 1),
            last: data => this.showPage(data.chash, data.pages)
        };

        request.done((data) => {
            chapterView.find(".chapt-nav-current-title").text(data.chapter);

            this.current.index = data.index;
            this.current.pages = data.pages;

            if (page && page in pageLoaders)
            {
                pageLoaders[page](data);
            }

            chapterFlexbox.empty();

            for (let imageId = 1; imageId <= data.pages; ++imageId) {
                chapterFlexbox.append(aux.template("tt-thumbnail", {
                    mhash: this.mhash,
                    chash: data.chash,
                    image: imageId
                }));
            }

            if (data.readed && data.readed instanceof Array) {
                data.readed.forEach((imageId) => {
                    $(`div.chapt-thumb[data-image='${imageId}']`).attr("data-readed", 1);
                });
            }
        });
    }

    showPage(chash, imageId)
    {
        const MIN_SWIPELENGTH = 200;
        const MAX_SWIPE_TIME_DELTA = 500;
        const DEFAULT_CSS = {
            height: "auto",
            width: $(document).width()
        };

        this.current.imageId = imageId;

        let imageSource = `/t/${this.mhash}/${chash}/${imageId}`;

        if (!$("#manga-page").length) {
            $("body").append(aux.template("tt-page"));
        }

        let mangaPage = $("#manga-page");

        mangaPage.find(".page-controls")
            .on("click", "div[data-action=close]", () => {
                mangaPage.off("click");
                mangaPage.remove();
            }).on("click", "div[data-action=fullscreen]", () => {
                $("body").fullscreen();
            });

        let mangaPageImage = mangaPage.find("img");

        mangaPageImage.attr("src", imageSource);
        mangaPageImage.css(DEFAULT_CSS);

        $(window).off("resize");
        $(window).on("resize", () => {
            mangaPageImage.css({width: $(document).width()});
        });

        let proxySwipeLeft = () => {
            let newid = imageId + 1;

            if ($(`div.chapt-thumb[data-image=${newid}]`).length) {
                this.showPage(chash, newid);
                return;
            }

            let chapterList =  $("body div.chaptlist");
            let index = parseInt(
                chapterList.find(`div[data-chaptid=${chash}]`).data("index")
            );
    
            let chapter = chapterList.find(`div[data-index=${index + 1}]`);
    
            if (chapter.length) {
                this.showChapter(chapter.data("chaptid"), "first");
            }
        };

        let proxySwipeRight = () => {
            let newid = imageId - 1;
            if ($(`div.chapt-thumb[data-image=${newid}]`).length) {
                this.showPage(chash, newid);
                return;
            }
    
            let chapterList =  $("body div.chaptlist");
            let index = parseInt(
                chapterList.find(`div[data-chaptid=${chash}]`).data("index")
            );
    
            let chapter = chapterList.find(`div[data-index=${index - 1}]`);
    
            if (chapter.length) {
                let prevChash = chapter.data("chaptid");
                this.showChapter(prevChash, "last");
            }
        };

        mangaPage.off("touchend");
        mangaPage.off("touchmove");
        mangaPage.off("touchstart");

        mangaPage.on("touchstart", function (startEvent) {
            let firstTouch = startEvent.targetTouches[0];
            let previousTouch = startEvent.targetTouches[0];

            $(this).on("touchmove", function(e) {
                let currentTouch = e.targetTouches[0];
                let offset = $(mangaPageImage).offset();

                let deltaY = currentTouch.pageY - previousTouch.pageY;
                let deltaX = currentTouch.pageX - previousTouch.pageX;
                
                if (Math.abs(deltaY) > Math.abs(deltaX))
                {
                    offset.top += deltaY;
                    mangaPageImage.offset(offset);
                }
    
                previousTouch = currentTouch;
            }).on("touchend", function (endEvent) {
                $(this).off("touchmove");
                $(this).off("touchend");

                let delta = previousTouch.pageX - firstTouch.pageX;
                let timeDelta = endEvent.timeStamp - startEvent.timeStamp;

                if (timeDelta < MAX_SWIPE_TIME_DELTA)
                {
                    if (delta > 0 && delta > MIN_SWIPELENGTH)
                    {
                        proxySwipeRight();
                    }
                    else if (delta < 0 && delta < (-MIN_SWIPELENGTH))
                    {
                        proxySwipeLeft();
                    }
                }
            });
        });

        let image = new Image();
        image.src = `/p/${this.mhash}/${chash}/${imageId}`;

        image.onload = () => {
            mangaPageImage.attr("src", image.src);
            mangaPageImage.css(DEFAULT_CSS);
        };
    }
}

$(function () {
    let app = new CMangaView();
    app.run();
});
