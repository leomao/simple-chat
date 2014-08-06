'use strict';

var wsuri;
var ws;
var iden;
var users;
var now;
var now_dom;
var convs = {};
var name;
var keepalive;

function show_conv() {
    var c = $("#conversation");
    c.html(convs[now]);
    c.scrollTop(c.height());
}

function change_conv() {
    if (now_dom != undefined)
        now_dom.toggleClass("active");
    now_dom = $(this);
    now_dom.toggleClass("active");
    now = now_dom.children(".name").text()
    show_conv();
    now_dom.children(".badge").text("");
}

function update(from) {
    if (from == now) {
        show_conv();
    }
    else {
        var count = parseInt($("#conv-" + from).children(".badge").text());
        if (count)
            count++;
        else
            count = 1;
        $("#conv-" + from).children(".badge").text(count);
    }
}

function send_message() {
    var mes = $("#message").val();
    $("#message").val("");
    if (ws == undefined) {
        console.log("doesn't connect");
        return;
    }
    convs[now] += name + ": " + mes + "<br>";
    show_conv();

    var data = {'to': now, 'message':mes, 'iden':iden};
    try {
        ws.send(JSON.stringify(data));
    }
    catch (err) {
        console.log("connection broken");
        console.log("error message:", err.message);
    }
}

function get_message(from, mes) {
    console.log("get from", from, ":", mes);
    if (convs[from] == undefined) {
        convs[from] = "";
        add_conv(from);
    }
    convs[from] += from + ": " + mes + "<br>";
    update(from);
}

function add_conv(username) {
    var conv_list = $("#conv_list");
    conv_list.append($('<a id="conv-' + username +
                       '" href="#" class="list-group-item">' +
                       '<span class="glyphicon glyphicon-remove"></span>' +
                       '<span class="name">' + username + '</span>' +
                       '<span class="badge"></span>' + '</a>'));
}

function update_convs() {
    var conv_list = $("#conv_list");
    conv_list.empty();
    convs.forEach(function(conv){
        conv_list.append($('<a id="conv-' + username +
                           '" href="#" class="list-group-item">' +
                           '<span class="glyphicon glyphicon-remove"></span>' +
                           '<span class="name">' + username + '</span>' +
                           '<span class="badge"></span>' + '</a>'));
    });
}

function update_users() {
    var user_list = $("#user_list tbody");
    user_list.empty();
    users.forEach(function(username){
        console.log(username);
        user_list.append($('<tr><td class="user">' + username + '</td></tr>'));
    });
}

function pong() {
    if (ws != undefined) {
        try {
            ws.send("pong");
        }
        catch (err) {
            console.log("connection broken");
            console.log("error message:", err.message);
        }
    }
}

function connect() {
    wsuri = "ws://" + location.host + '/ws/';
    name = $("#name").val();
    try {
        ws = new WebSocket(wsuri);
        ws.onopen = function(){
            console.log("connected to", wsuri);
            ws.send(name);
            keepalive = setInterval(pong, 30000);
        }
        ws.onmessage = function(evt){
            console.log(evt.data);
            var data = JSON.parse(evt.data);
            if (data.iden)
                iden = data.iden;
            if (data.message)
                get_message(data.from, data.message);
            if (data.user_list) {
                users = data.user_list;
                console.log(users);
                update_users();
            }
        }
        ws.onclose = function(){
            clearInterval(keepalive);
            console.log("closed");
        }
    }
    catch (err) {
        console.log("can't connect to", wsuri);
        console.log("error message:", err.message);
    }
}

$(function(){
    $("#send").click(send_message);
    $("#connect").click(connect);
    $("#message").keypress(function(e){
        var keycode = (e.keyCode ? e.keyCode : e.which);
        if(keycode == '13'){
            $("#send").click();
        };
    });

    $("#user_list").on("click", ".user", function(){
        var username = $(this).text();
        if (convs[username] == undefined) {
            convs[username] = "";
            add_conv(username);
        }
        $("#conv-" + username).click();
        $("#message").focus();
    });

    $("#conv_list").on("click", ".glyphicon", function(){
        var convsname = $(this).parent().children(".name").text();
        $(this).parent().remove();
        delete convs[convsname];
    });

    $("#conv_list").on("click", "a", change_conv);
});
