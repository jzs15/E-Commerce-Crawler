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
    let sort_list = ['price', 'score', 'date', 'comment_num'];
    for (let i in sort_list) {
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
        url = location.pathname;
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

function searchChange(num, col) {
    let open_elem = document.getElementById("open_" + num);
    if (open_elem.innerText === "更多↓") {
        let hide_tables = document.getElementsByClassName("hide_table_" + num);
        for (let i = 0; i < hide_tables.length; i++) {
            hide_tables[i].removeAttribute("style");
        }
        document.getElementById("filter_name_" + num).setAttribute("rowspan", col);
        open_elem.innerText = "收缩↑";
    } else {
        let hide_tables = document.getElementsByClassName("hide_table_" + num);
        for (let i = 0; i < hide_tables.length; i++) {
            hide_tables[i].style.display = "none";
        }
        document.getElementById("filter_name_" + num).setAttribute("rowspan", 1);
        open_elem.innerText = "更多↓";
    }
    return false;
}

function change_select(val) {
    document.getElementById("search_form").setAttribute("action", '/products_filter/' + val)
}