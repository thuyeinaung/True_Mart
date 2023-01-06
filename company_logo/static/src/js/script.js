odoo.define('company_logo.AbstractWebClient', function (require) {
"use strict";

var ActionManager = require('web.ActionManager');
var concurrency = require('web.concurrency');
var core = require('web.core');
var config = require('web.config');
var crash_manager = require('web.crash_manager');
var data_manager = require('web.data_manager');
var Dialog = require('web.Dialog');
var Loading = require('web.Loading');
var mixins = require('web.mixins');
var NotificationManager = require('web.notification').NotificationManager;
var RainbowMan = require('web.rainbow_man');
var session = require('web.session');
var Widget = require('web.Widget');
var ajax = require('web.ajax');
var core = require('web.core');
var Dialog = require('web.Dialog');

var QWeb = core.qweb;
var _t = core._t;
var _lt = core._lt;

var AbstractWebClient = require('web.AbstractWebClient');

AbstractWebClient.include({
 init: function (parent) {
        this.client_options = {};
        mixins.ServiceProvider.init.call(this);
        this._super(parent);
        this.origin = undefined;
        this._current_state = null;
        this.menu_dm = new concurrency.DropMisordered();
        this.action_mutex = new concurrency.Mutex();
        this.set('title_part', {"zopenerp": "FH Myanmar"});
    },
 });

CrashManager.include({
	 rpc_error: function(error) {
	        var self = this;
	        if (!this.active) {
	            return;
	        }
	        if (this.connection_lost) {
	            return;
	        }
	        if (error.code === -32098) {
	            core.bus.trigger('connection_lost');
	            this.connection_lost = true;
	            var timeinterval = setInterval(function() {
	                ajax.jsonRpc('/web/webclient/version_info').then(function() {
	                    clearInterval(timeinterval);
	                    core.bus.trigger('connection_restored');
	                    self.connection_lost = false;
	                });
	            }, 2000);
	            return;
	        }
	        var handler = core.crash_registry.get(error.data.name, true);
	        if (handler) {
	            new (handler)(this, error).display();
	            return;
	        }
	        if (error.data.name === "odoo.http.SessionExpiredException" || error.data.name === "werkzeug.exceptions.Forbidden") {
	            this.show_warning({type: _t("Session Expired"), data: {message: _t("Your session expired. Please refresh the current web page.")}});
	            return;
	        }
	        if (_.has(map_title, error.data.exception_type)) {
	            if(error.data.exception_type === 'except_orm'){
	                if(error.data.arguments[1]) {
	                    error = _.extend({}, error,
	                                {
	                                    data: _.extend({}, error.data,
	                                        {
	                                            message: error.data.arguments[1],
	                                            title: error.data.arguments[0] !== 'Warning' ? (" - " + error.data.arguments[0]) : '',
	                                        })
	                                });
	                }
	                else {
	                    error = _.extend({}, error,
	                                {
	                                    data: _.extend({}, error.data,
	                                        {
	                                            message: error.data.arguments[0],
	                                            title:  '',
	                                        })
	                                });
	                }
	            }
	            else {
	                error = _.extend({}, error,
	                            {
	                                data: _.extend({}, error.data,
	                                    {
	                                        message: error.data.arguments[0],
	                                        title: map_title[error.data.exception_type] !== 'Warning' ? (" - " + map_title[error.data.exception_type]) : '',
	                                    })
	                            });
	            }

	            this.show_warning(error);
	        //InternalError

	        } else {
	            this.show_error(error);
	        }
	    },
	    show_warning: function(error) {
	        if (!this.active) {
	            return;
	        }
	     // Error message contains odoo title. Replace it
	        error.message = error.message && error.message.replace("Odoo", "")
	        new Dialog(this, {
	            size: 'medium',
	            title: _.str.capitalize(error.type || error.message) || _t("Warning"),
	            subtitle: error.data.title,
	            $content: $(QWeb.render('CrashManager.warning', {error: error}))
	        }).open();
	    },
	    show_error: function(error) {
	        if (!this.active) {
	            return;
	        }
	        error.message = error.message && error.message.replace("Odoo", "")
	        var dialog = new Dialog(this, {
	            title: _.str.capitalize(error.type || error.message) || _t("Error"),
	            $content: $(QWeb.render('CrashManager.error', {error: error}))
	        });

	        // When the dialog opens, initialize the copy feature and destroy it when the dialog is closed
	        var $clipboardBtn;
	        var clipboard;
	        dialog.opened(function () {
	            // When the full traceback is shown, scroll it to the end (useful for better python error reporting)
	            dialog.$(".o_error_detail").on("shown.bs.collapse", function (e) {
	                e.target.scrollTop = e.target.scrollHeight;
	            });

	            $clipboardBtn = dialog.$(".o_clipboard_button");
	            $clipboardBtn.tooltip({title: _t("Copied !"), trigger: "manual", placement: "left"});
	            clipboard = new window.Clipboard($clipboardBtn[0], {
	                text: function () {
	                    return (_t("Error") + ":\n" + error.message + "\n\n" + error.data.debug).trim();
	                }
	            });
	            clipboard.on("success", function (e) {
	                _.defer(function () {
	                    $clipboardBtn.tooltip("show");
	                    _.delay(function () {
	                        $clipboardBtn.tooltip("hide");
	                    }, 800);
	                });
	            });
	        });
	        dialog.on("closed", this, function () {
	            $clipboardBtn.tooltip("destroy");
	            clipboard.destroy();
	        });

	        dialog.open();
	    },
	    show_message: function(exception) {
	        this.show_error({
	            type: _t("Client Error"),
	            message: exception,
	            data: {debug: ""}
	        });
	    },
});

weclient.include({
    update_logo: function(reload) {
    // This function change the debranding logo to default company logo
        var company = session.company_id;
        var img = session.url('/company_logo/static/src/img/logo3.png' + '?db=' + session.db + (company ? '&company=' + company : ''));
//        this.$('.o_sub_menu_logo img').attr('src', '').attr('src', img + (reload ? "&t=" + Date.now() : ''));
        this.$('.oe_logo_edit').toggleClass('oe_logo_edit_admin', session.is_superuser);
    },
});

});