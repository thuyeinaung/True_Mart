// pos_membership_odoo js
//console.log("custom callleddddddddddddddddddddd")
odoo.define('pos_membership_odoo.pos', function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');
    var rpc = require('web.rpc');

    var QWeb = core.qweb;
	var _t = core._t;
	
	
	/*var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        set_pricelist: function (pricelist) {
			var self = this;

	        var order = self.pos.get_order();
	        var orderlines = order ? order.get_orderlines() : null;
        				
			this.pricelist = pricelist;

				for (var i = 0; i < orderlines.length; i++) {
					var lines = orderlines[i];
					var price = orderlines[i].product.price;
					price = pricelist;
				    lines.set_unit_price(price);
				    return;
				}
			
			this.trigger('change');
			
		
		},
    });*/


    // ApplyMembershipPopupWidget start

    var ApplyMembershipPopupWidget = popups.extend({
        template: 'ApplyMembershipPopupWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        //
        show: function(options) {
            var self = this;
            this._super(options);

        },
        //
        renderElement: function() {
            var self = this;
            this._super();
            var order = this.pos.get_order();
            var selectedOrder = self.pos.get('selectedOrder');
            this.$('#apply_membership_card').click(function() {
                var entered_code = $("#enter_card_code").val();
                var used = false;
                var partner_id = false
                if (order.get_client() != null)
                    partner_id = order.get_client();
                    
                rpc.query({
		            model: 'pos.membership',
		            method: 'apply_membership_cards',
		            args: [partner_id, entered_code],

                }).then(function(output) {
                    var orderlines = order.orderlines;
                    if (!partner_id) {
                        self.gui.show_popup('error', {
                            'title': _t('Unknown customer'),
                            'body': _t('You cannot use Membership Card Code. Select customer first.'),
                        });
                        return;
                    }

                    if (orderlines.length === 0) {
                        self.gui.show_popup('error', {
                            'title': _t('Empty Order'),
                            'body': _t('There must be at least one product in your order before it can be apply for Membership Card Code.'),
                        });
                        return;
                    }

                    if (orderlines.models.length) {
                        if (output == true) {
                            var selectedOrder = self.pos.get('selectedOrder');
                            rpc.query({
								model: 'pos.membership',
								method: 'search_membership_cards',
								args: [partner_id, entered_code],

						    }).then(function(output) {
                                //var code = output[0];
                                var membership_discount = output[1];
                                var expiry = output[2];
                                var membership_partner = output[3];

		                        var current_date = new Date().toUTCString();
		                        var d = new Date();
		                        var month = '' + (d.getMonth() + 1);
		                        var day = '' + d.getDate();
								var year = d.getFullYear();
								var date_format = [year, month, day].join('-');
								var hours = d.getHours();
								var minutes = d.getMinutes();
		                        var seconds = d.getSeconds();
		                        var time_format = [hours, minutes, seconds].join(':');
		                        var date_time = [date_format, time_format].join(' ');
		                        //console.log("date_timeeeeeeeeeeeeeeeeeeeeeeeeeeeee", date_time, expiry, date_time > expiry);
		                        
		                        /*
		                        if (date_time > expiry){ // expired
							    	self.gui.show_popup('error', {
							            'title': _t('Expired'),
							            'body': _t("The Membership Card Code You are trying to apply is Expired"),
							        });
							    }
							    */


						        if (membership_partner != partner_id.id){
							    	self.gui.show_popup('error', {
							            'title': _t('Invalid Customer !!!'),
							            'body': _t("This Membership Card Code is not applicable for this Customer"),
							        });
						        }
						       
                                else { // if coupon is not used
                                					                                        
					                orderlines.models.forEach(function(orderline) {
										orderline.set_discount(membership_discount);
										$(".membershipmessage").html("<strong>" + "Congratulations... " + membership_discount + " % Membership Discount Applied</b>");
									});
								}
									
                            });
                            
                            
                            self.gui.show_screen('payment');
                        } else { //Invalid Membership Card Code
                            self.gui.show_popup('error', {
                                'title': _t('Invalid Membership Card Code !!!'),
                                'body': _t("Membership Card Code Entered by you is Invalid. Enter Valid Code..."),
                            });
                        }
                        

                    } else { // Popup Shows, you can't use more than one Membership Card Code in single order.
                        self.gui.show_popup('error', {
                            'title': _t('Already Used !!!'),
                            'body': _t("You have already use this Membership Card Code, at a time you can use One Membership Card Code in a Single Order"),
                        });
                    }

                });
            });
        },

    });
    gui.define_popup({
        name: 'apply_membership_popup_widget',
        widget: ApplyMembershipPopupWidget
    });

    // End Popup start
    
    

	// PaymentScreenWidget start
	screens.PaymentScreenWidget.include({
		//
		show: function(){
			var self = this;
			this.pos.get_order().clean_empty_paymentlines();
			this.reset_input();
			this.render_paymentlines();
			this.order_changes();
			window.document.body.addEventListener('keypress',this.keyboard_handler);
			window.document.body.addEventListener('keydown',this.keyboard_keydown_handler);
			this._super();
			
			self.$('.button.usemembershipmethod').click(function(){
				//console.log("clickkkeddddddddddddddddd");
				self.gui.show_popup('apply_membership_popup_widget', {});
				window.document.body.removeEventListener('keypress',self.keyboard_handler);
				window.document.body.removeEventListener('keydown',self.keyboard_keydown_handler);
				$('#enter_card_code').focus();
			});
			
			
		},
		
	 
	});    
        
    

});
