$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the shopcart form with data from the response
    function update_form_data(res) {
        $("#shopcart_id").val(res.id);
        $("#shopcart_name").val(res.name);
        $("#shopcart_userid").val(res.userid);
        $("#shopcart_status").val(res.status);
    }

    // Clears all shopcart form fields
    function clear_form_data() {
        $("#shopcart_id").val("");
        $("#shopcart_name").val("");
        $("#shopcart_userid").val("");
        $("#shopcart_status").val("");
    }

    // Updates the item form with data from the response
    function update_item_form_data(res) {
        $("#item_id").val(res.id);
        $("#item_shopcart_id").val(res.shopcart_id);
        $("#item_product_id").val(res.product_id);
        $("#item_name").val(res.name);
        $("#item_quantity").val(res.quantity);
        $("#item_price").val(res.price);
    }

    // Clears all item form fields
    function clear_item_form_data() {
        $("#item_id").val("");
        $("#item_shopcart_id").val("");
        $("#item_product_id").val("");
        $("#item_name").val("");
        $("#item_quantity").val("");
        $("#item_price").val("");
    }

    // Shows a flash message to the user
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    //  S H O P C A R T   A C T I O N S
    // ****************************************

    // -------- Create a Shopcart --------
    $("#create-btn").click(function () {
        var name = $("#shopcart_name").val();
        var userid = $("#shopcart_userid").val();
        var cart_status = $("#shopcart_status").val();

        var data = {
            "name": name,
            "userid": userid,
            "status": cart_status
        };

        $("#flash_message").empty();

        var ajax = $.ajax({
            type: "POST",
            url: "/shopcarts",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    // -------- Update a Shopcart --------
    $("#update-btn").click(function () {
        var shopcart_id = $("#shopcart_id").val();
        var name = $("#shopcart_name").val();
        var userid = $("#shopcart_userid").val();
        var cart_status = $("#shopcart_status").val();

        $("#flash_message").empty();

        if (!shopcart_id) {
            flash_message("Error: Shopcart ID is required to update");
            return;
        }

        var data = {
            "name": name,
            "userid": userid,
            "status": cart_status
        };

        var ajax = $.ajax({
            type: "PUT",
            url: "/shopcarts/" + shopcart_id,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    // -------- Checkout a Shopcart --------
    $("#checkout-btn").click(function () {
        var shopcart_id = $("#shopcart_id").val();

        $("#flash_message").empty();

        if (!shopcart_id) {
            flash_message("Error: Shopcart ID is required to checkout");
            return;
        }

        var ajax = $.ajax({
            type: "PUT",
            url: "/shopcarts/" + shopcart_id + "/checkout",
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    // -------- Search Shopcarts by Status --------
    $("#search-btn").click(function () {
        var status = $("#shopcart_status").val();

        var queryString = "";
        if (status) {
            queryString = "?status=" + status;
        }

        $("#flash_message").empty();

        var ajax = $.ajax({
            type: "GET",
            url: "/shopcarts" + queryString,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            $("#search_results_body").empty();
            if (res.length === 0) {
                flash_message("No Shopcarts found");
            } else {
                for(var i = 0; i < res.length; i++) {
                    var shopcart = res[i];
                    var row = "<tr id='row_" + i + "'>" +
                        "<td>" + shopcart.id + "</td>" +
                        "<td>" + shopcart.name + "</td>" +
                        "<td>" + shopcart.userid + "</td>" +
                        "<td>" + shopcart.status + "</td>" +
                        "<td>" + shopcart.items.length + "</td>" +
                        "<td>" + shopcart.total_price.toFixed(2) + "</td>" +
                        "</tr>";
                    $("#search_results_body").append(row);
                }
                flash_message("Success");
            }
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    // -------- List All Shopcarts --------
    $("#list-btn").click(function () {
        var shopcart_id = $("#shopcart_id").val();
        var status = $("#shopcart_status").val();

        $("#flash_message").empty();

        // If ID is provided, retrieve that specific shopcart
        if (shopcart_id) {
            var ajax = $.ajax({
                type: "GET",
                url: "/shopcarts/" + shopcart_id,
                contentType: "application/json",
                data: ''
            });

            ajax.done(function(res){
                $("#search_results_body").empty();
                var shopcart = res;
                var row = "<tr id='row_0'>" +
                    "<td>" + shopcart.id + "</td>" +
                    "<td>" + shopcart.name + "</td>" +
                    "<td>" + shopcart.userid + "</td>" +
                    "<td>" + shopcart.status + "</td>" +
                    "<td>" + shopcart.items.length + "</td>" +
                    "<td>" + shopcart.total_price.toFixed(2) + "</td>" +
                    "</tr>";
                $("#search_results_body").append(row);
                flash_message("Success");
            });

            ajax.fail(function(res){
                $("#search_results_body").empty();
                flash_message(res.responseJSON.message);
            });
        } else {
            // No ID: list all, optionally filtered by status
            var queryString = "";
            if (status) {
                queryString = "?status=" + status;
            }

            var ajax = $.ajax({
                type: "GET",
                url: "/shopcarts" + queryString,
                contentType: "application/json",
                data: ''
            });

            ajax.done(function(res){
                $("#search_results_body").empty();
                if (res.length === 0) {
                    flash_message("No Shopcarts found");
                } else {
                    for(var i = 0; i < res.length; i++) {
                        var shopcart = res[i];
                        var row = "<tr id='row_" + i + "'>" +
                            "<td>" + shopcart.id + "</td>" +
                            "<td>" + shopcart.name + "</td>" +
                            "<td>" + shopcart.userid + "</td>" +
                            "<td>" + shopcart.status + "</td>" +
                            "<td>" + shopcart.items.length + "</td>" +
                            "<td>" + shopcart.total_price.toFixed(2) + "</td>" +
                            "</tr>";
                        $("#search_results_body").append(row);
                    }
                    flash_message("Success");
                }
            });

            ajax.fail(function(res){
                flash_message(res.responseJSON.message);
            });
        }
    });

    // -------- Delete a Shopcart --------
    $("#delete-btn").click(function () {
        var shopcart_id = $("#shopcart_id").val();

        $("#flash_message").empty();

        if (!shopcart_id) {
            flash_message("Error: Shopcart ID is required to delete");
            return;
        }

        var ajax = $.ajax({
            type: "DELETE",
            url: "/shopcarts/" + shopcart_id,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            clear_form_data();
            $("#shopcart_id").val("");
            flash_message("Shopcart has been Deleted!");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    // -------- Clear Shopcart Form --------
    $("#clear-btn").click(function () {
        $("#shopcart_id").val("");
        $("#flash_message").empty();
        clear_form_data();
    });

    // ****************************************
    //  I T E M   A C T I O N S
    // ****************************************

    // -------- Create an Item in a Shopcart --------
    $("#create-item-btn").click(function () {
        var shopcart_id = $("#item_shopcart_id").val();
        var product_id = $("#item_product_id").val();
        var name = $("#item_name").val();
        var quantity = $("#item_quantity").val();
        var price = $("#item_price").val();

        $("#flash_message").empty();

        if (!shopcart_id) {
            flash_message("Error: Shopcart ID is required to create an item");
            return;
        }

        var data = {
            "product_id": product_id,
            "name": name,
            "quantity": parseInt(quantity),
            "price": parseFloat(price),
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/shopcarts/" + shopcart_id + "/items",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_item_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    // -------- Update an Item in a Shopcart --------
    $("#update-item-btn").click(function () {
        var shopcart_id = $("#item_shopcart_id").val();
        var item_id = $("#item_id").val();
        var product_id = $("#item_product_id").val();
        var name = $("#item_name").val();
        var quantity = $("#item_quantity").val();
        var price = $("#item_price").val();

        $("#flash_message").empty();

        if (!shopcart_id) {
            flash_message("Error: Shopcart ID is required to update an item");
            return;
        }

        if (!item_id) {
            flash_message("Error: Item ID is required to update an item");
            return;
        }

        var data = {
            "product_id": product_id,
            "name": name,
            "quantity": parseInt(quantity),
            "price": parseFloat(price),
        };

        var ajax = $.ajax({
            type: "PUT",
            url: "/shopcarts/" + shopcart_id + "/items/" + item_id,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_item_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    // -------- List Items in a Shopcart --------
    $("#list-item-btn").click(function () {
        var shopcart_id = $("#item_shopcart_id").val();
        var item_id = $("#item_id").val();

        $("#flash_message").empty();

        // Shopcart ID is required
        if (!shopcart_id) {
            flash_message("Error: Shopcart ID is required to list items");
            return;
        }

        // If Item ID is provided, retrieve that specific item
        if (item_id) {
            var ajax = $.ajax({
                type: "GET",
                url: "/shopcarts/" + shopcart_id + "/items/" + item_id,
                contentType: "application/json",
                data: ''
            });

            ajax.done(function(res){
                $("#item_results_body").empty();
                var item = res;
                var row = "<tr id='item_row_0'>" +
                    "<td>" + item.id + "</td>" +
                    "<td>" + item.shopcart_id + "</td>" +
                    "<td>" + item.product_id + "</td>" +
                    "<td>" + item.name + "</td>" +
                    "<td>" + item.quantity + "</td>" +
                    "<td>" + item.price.toFixed(2) + "</td>" +
                    "</tr>";
                $("#item_results_body").append(row);
                flash_message("Success");
            });

            ajax.fail(function(res){
                $("#item_results_body").empty();
                flash_message(res.responseJSON.message);
            });
        } else {
            // No Item ID: list all items in the shopcart
            var ajax = $.ajax({
                type: "GET",
                url: "/shopcarts/" + shopcart_id + "/items",
                contentType: "application/json",
                data: ''
            });

            ajax.done(function(res){
                $("#item_results_body").empty();
                if (res.length === 0) {
                    flash_message("No Items found");
                } else {
                    for(var i = 0; i < res.length; i++) {
                        var item = res[i];
                        var row = "<tr id='item_row_" + i + "'>" +
                            "<td>" + item.id + "</td>" +
                            "<td>" + item.shopcart_id + "</td>" +
                            "<td>" + item.product_id + "</td>" +
                            "<td>" + item.name + "</td>" +
                            "<td>" + item.quantity + "</td>" +
                            "<td>" + item.price.toFixed(2) + "</td>" +
                            "</tr>";
                        $("#item_results_body").append(row);
                    }
                    flash_message("Success");
                }
            });

            ajax.fail(function(res){
                flash_message(res.responseJSON.message);
            });
        }
    });

    // -------- Delete an Item from a Shopcart --------
    $("#delete-item-btn").click(function () {
        var shopcart_id = $("#item_shopcart_id").val();
        var item_id = $("#item_id").val();

        $("#flash_message").empty();

        if (!shopcart_id) {
            flash_message("Error: Shopcart ID is required to delete an item");
            return;
        }

        if (!item_id) {
            flash_message("Error: Item ID is required to delete an item");
            return;
        }

        var ajax = $.ajax({
            type: "DELETE",
            url: "/shopcarts/" + shopcart_id + "/items/" + item_id,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            clear_item_form_data();
            flash_message("Item has been Deleted!");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    // -------- Clear Item Form --------
    $("#clear-item-btn").click(function () {
        $("#item_id").val("");
        $("#flash_message").empty();
        clear_item_form_data();
    });

});
