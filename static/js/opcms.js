/*
* opcms javascript
*/

function defaultAjax(url, data, type, callbackFunction, showError) {
    var processing = $("#id_modal_processing");
    $.ajax({
        url : url,
        data : data,
        type : type,
        dataType : "json",
        contentType : "application/json; charset=UTF-8",
        timeout : 5000,
        beforeSend : function(xhr, settings) {
            processing.modal("show");
            xhr.setRequestHeader("Content-type", "application/json; charset=UTF-8");
            xhr.setRequestHeader("Cache-Control", "no-cache");
        },
        success : function(data, textStatus, jqXHR) {
            processing.modal("hide");
            callbackFunction(data);
        },
        error : function(jqXHR, textStatus, errorThrown) {
            processing.modal("hide");
            if (showError) { alert("Erro de comunicação " + url); }
            callbackFunction({ status : false, info : "Erro de comunicação " + url });
        }
    });
};

function defaultAjaxUploadFiles(url, data, fileInputs, callbackFunction, showError) {
    var processing = $("#id_modal_processing");
    $.ajax({
        url : url,
        data : data,
        type: "POST",
        dataType : "iframe json",
        fileInputs: fileInputs,
        timeout : 60000,
        beforeSend : function(xhr, settings) {
            processing.modal("show");
        },
        success : function(data, textStatus, jqXHR) {
            processing.modal("hide");
            callbackFunction(data);
        },
        error : function(jqXHR, textStatus, errorThrown) {
            processing.modal("hide");
            if (showError) { alert("Erro de comunicação " + url); }
            callbackFunction({ status : false, info : "Erro de comunicação " + url });
        }
    });
};

function defaultFormSubmit(formId, resultId, formSubmitUrl, callbackFunction, showError) {
    var forms = $(formId);
    var results = $(resultId);
    forms.bind( "submit", function(event) {
        event.stopPropagation();
        event.preventDefault();
        results.html("").hide();
        defaultAjax(formSubmitUrl, $(this).serialize(), "POST", function(json) {
            if (json.status) {
                results.removeClass("alert-success alert-danger").addClass("alert-success").html(json.info).show();
            } else {
                results.removeClass("alert-success alert-danger").addClass("alert-danger").html(json.info).show();
            }
            setTimeout( function() { results.fadeOut(1500); }, 1500 );
            callbackFunction(json);
        }, showError);
        return false;
    });
};

function defaultUploadFilesSubmit(formId, formData, resultId, showImgId, formSubmitUrl, callbackFunction, showError) {
    var results = $(resultId);
    var showImg = $(showImgId);
    $(formId).bind( "submit", function(event) {
        event.stopPropagation();
        event.preventDefault();
        results.html("").hide();
        showImg.html("").hide();
        var data = $.isFunction(formData) ? formData() : formData;
        var fileInputs = $("input[type='file']", $(this));
        defaultAjaxUploadFiles(formSubmitUrl, data, fileInputs, function(json) {
            if (json.status) {
                results.removeClass("alert-success alert-danger").addClass("alert-success").html(json.info).show();
                showImg.html(
                    "<img src='" + json.thumbnail + "?timestamp=" + new Date().getTime() + "' class='img-thumbnail center-block' width='200' height='200'/>"
                ).fadeIn(2500);
            } else {
                results.removeClass("alert-success alert-danger").addClass("alert-danger").html(json.info).show();
            }
            setTimeout( function() { results.fadeOut(1500); }, 1500 );
            callbackFunction(json);
        }, false);
        return false;
    });
};

function defaultClickSubmit(btnId, resultId, btnSubmitUrl, callbackFunction, showError, showConfirm, showConfirmName) {
    var results = $(resultId);
    $(btnId).bind( "click", function(event) {
        event.stopPropagation();
        event.preventDefault();
        results.html("").hide();
        var data = $(this).attr("href").split("?")[1];
        function ajaxAction() {
            defaultAjax(btnSubmitUrl, data, "POST", function(json) {
                if (json.status) {
                    results.removeClass("alert-success alert-danger").addClass("alert-success").html(json.info).show();
                } else {
                    results.removeClass("alert-success alert-danger").addClass("alert-danger").html(json.info).show();
                }
                setTimeout( function() { results.fadeOut(1500); }, 1500 );
                callbackFunction(json);
            }, showError);
        };
        if (showConfirm) {
            $("#id_confirm_name").text(showConfirmName);
            $("#id_modal_confirm").modal("show").one("click", "#id_confirm_yes", function (event) {
                event.stopPropagation();
                event.preventDefault();
                ajaxAction();
                return false;
            });
        } else {
            ajaxAction();
        }
        return false;
    });
};
