
/**
 * First we will load all of this project's JavaScript dependencies which
 * includes Vue and other libraries. It is a great starting point when
 * building robust, powerful web applications using Vue and Laravel.
 */

require('./bootstrap');

window.Vue = require('vue');

/** Plugins */
import swalDefault from 'sweetalert2'

window.swal = swalDefault.mixin({
    confirmButtonClass: 'btn btn-primary m-3',
    cancelButtonClass: 'btn btn-danger m-3',
    buttonsStyling: false,
    reverseButtons: true
});

import toastr from 'toastr';
window.toastr = toastr;

/**
 * Next, we will create a fresh Vue application instance and attach it to
 * the page. Then, you may begin adding components to this application
 * or customize the JavaScript scaffolding to fit your unique needs.
 */

import {
    Card, ExampleComponent,
    SideBarCard, SideBarListItem,
} from './components';

Vue.component('card', Card);
Vue.component('example-component', ExampleComponent);
Vue.component('side-bar-card', SideBarCard);
Vue.component('side-bar-list-item', SideBarListItem);

/** VueJS Plugins */
import SlideUpDown from 'vue-slide-up-down';
Vue.component('slide-up-down', SlideUpDown);

const app = new Vue({
    el: '#app',
    data() {
        return {
            User: window.User,
            App: window.App,
        }
    },
});

window.freezeSubmitButton = function (form, callback = function () {}, timeout = timeout) {
    let submitButton = $(form).find('button[type="submit"]');
    let currentHtml = submitButton.html();
    let newHtml = currentHtml + '<i class="fa fa-fw fa-spinner fa-spin"></i>';
    submitButton.html(newHtml);
    submitButton.attr('disabled', 'disabled');

    setTimeout(function () {
        submitButton.html(currentHtml);
        submitButton.removeAttr('disabled');

        callback();
    }, 1000);
}

window.respondAxiosSuccess = function (data) {
    if (data.success) {
        toastr.success(data.success, 'Success!');
    }

    if (data.error) {
        toastr.error(data.error, 'Error!');
    }

    if (data.redirect) {
        setTimeout(function() {
            window.location = data.redirect;
        }, 2000);
    }
}

window.displayServerSideErrors = function (error, form) {
    // Process server-side errors, and display them.
    let errorsToShow = {};
    $.each(error.response.data.errors, function(fieldName, errorsArray) {
        let firstError = errorsArray.shift();
        errorsToShow[fieldName] = firstError;
    });

    $(form).validate().showErrors(errorsToShow);
}

$(document).on('click', '.delete-button', function () {
    let deleteUrl = $(this).data('url');
    let deleteType = $(this).data('type') || "warning";
    let deleteTitle = $(this).data('title') || "Are you sure?";
    let deleteItem = $(this).data('item') || "it";
    let deleteText = $(this).data('text') || "Are you sure you want to delete %ITEM%?";

    let dismissText = $(this).data('text') || "%ITEM% was not deleted.";

    swal({
        title: deleteTitle,
        html: deleteText.replace('%ITEM%', deleteItem),
        type: deleteType,
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'No, cancel!',
    }).then(function(result) {
        if (result.value) {
            $('#deleteForm').attr('action', deleteUrl).submit();
        } else if (result.dismiss === swal.DismissReason.cancel) {
            swal('Cancelled', dismissText.replace('%ITEM%', deleteItem), 'error');
        }
    });
});
