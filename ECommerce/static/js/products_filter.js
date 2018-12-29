sort_list = ['price', 'score', 'date', 'comment_num']

function RemoveFilter(name) {
    let req = GetRequest();
    if (req.hasOwnProperty("page")) {
        delete req["page"];
    }
    for (let key in req) {
        if (key === name && req.hasOwnProperty(key)) {
            delete req[key];
            break;
        }
    }
    location.href = ToHref(req);
}

function AddFilter(name, value) {
    let req = GetRequest();
    if (req.hasOwnProperty("page")) {
        delete req["page"];
    }
    if (name === "common") {
        if (req.hasOwnProperty("price")) {
            delete req["price"];
        }
        if (req.hasOwnProperty("score")) {
            delete req["score"];
        }
        if (req.hasOwnProperty("date")) {
            delete req["date"];
        }
        if (req.hasOwnProperty("comment_num")) {
            delete req["comment_num"];
        }
    }
    for (var i in sort_list) {
        if (sort_list[i] === name) {
            if (req.hasOwnProperty("common")) {
                delete req["common"];
            }
        }
    }
    req[name] = value;

    location.href = ToHref(req);
}

function EditPage(value) {
    let req = GetRequest();
    req["page"] = value;
    location.href = ToHref(req);
}

function GetRequest() {
    let url = location.search;
    let theRequest = {};
    if (url.indexOf("?") !== -1) {
        let str = url.substr(1).split("&");
        for (let i = 0; i < str.length; i++) {
            theRequest[str[i].split("=")[0]] = decodeURI(str[i].split("=")[1]);
        }
    }
    return theRequest;
}

/**
 * @returns {string}
 */
function ToHref(req) {
    let url = {};
    if (Object.keys(req).length === 0) {
        url = "/products_filter";
    } else {
        url = "?";
        for (let key in req) {
            if (req.hasOwnProperty(key)) {
                url += key + "=" + req[key] + "&";
            }
        }
        url = url.substring(0, url.length - 1)
    }
    return url;
}