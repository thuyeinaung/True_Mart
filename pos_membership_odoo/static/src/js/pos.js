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
	
	models.load_models({
        model: 'product.pricelist',
        fields: ['id','name','currency_id'],
        //domain: function(self) { return [ ['currency_id', '=', self.currency.id] ]; },
        domain: null,
        loaded: function(self, pricelists) {
        	
        	var pos_pricelist;
        	var pos_pricelist_id = self.config.pricelist_id[0];
            self.db.get_pricelists_by_id = {};
            pricelists.forEach(function(pricelist) {
                self.db.get_pricelists_by_id[pricelist.id] = pricelist;
                if (pricelist.id == pos_pricelist_id) {
                    self.pricelist = pricelist;
                    pos_pricelist = pricelist;
                }
            });

            self.pricelists = pricelists;
        
        },
        
    });
	
		
	models.load_models({
        model: 'product.pricelist.item',
        fields: ['id', 'fixed_price', 'date_end', 'applied_on', 'min_quantity', 'percent_price', 'date_start', 'product_tmpl_id', 'pricelist_id', 'compute_price', 'categ_id', 'price_discount', 'price_round', 'price_surcharge', 'price_min_margin', 'price_max_margin','base','base_pricelist_id'],
        domain: null,
        loaded: function(self, pricelist_items) {
            self.pricelist_items = pricelist_items;
        },
    });
    
    models.load_models({
			model:  'product.product',
			fields: ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'barcode', 'default_code',
			         'to_weight', 'uom_id', 'description_sale', 'description', 'categ_id', 'product_tmpl_id','tracking'],
			//order:  ['sequence','name'],
			order:  _.map(['sequence','default_code','name'], function (name) { return {name: name}; }),
			domain: [['sale_ok','=',true],['available_in_pos','=',true]],
			context: function(self){ return {display_default_code: false }; },
			loaded: function(self, products){
				
				self.get_products = [];
            	self.get_products_by_id = [];
            	
		        self.get_products = products;
		        products.forEach(function(product) {
		            self.get_products_by_id.push(product.id);
		        });
			    //self.db.add_products(products);
                
			},   
	});
	
	models.load_models({
        model: 'pos.membership',
        fields: ['membership_id', 'name', 'membership_code', 'hide_barcode', 'issue_date', 'expiry_date', 'partner_id', 'membership_template'],
        domain: null,
        loaded: function(self, pos_membership) {
            self.pos_membership = pos_membership;
        },
    });
    
	
	
	
	//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	
	
	var _super = models.Order.prototype;
    models.Order = models.Order.extend({
        
		/*set_client: function(client){
		    var self = this;
		    var selected_pricelist = self.pos.pricelist;
		    _super.set_client.call(this, client);
		    if (self.pos.chrome.screens != null) {
				if (client != null) {
		                var partner_pricelist_id = client.property_product_pricelist[0];
		                if (selected_pricelist.id != partner_pricelist_id) {
		                    self.get_final_pricelist = self.pos.db.get_pricelists_by_id[partner_pricelist_id]
		                    self.pos.chrome.screens.clientlist.apply_pricelist();
		                } else {
		                	self.get_final_pricelist = self.pos.db.get_pricelists_by_id[partner_pricelist_id]
		                    self.pos.chrome.screens.clientlist.apply_pricelist();
		            }
                }
                _super.set_client.call(this, client);
               }  
		},*/
		

        /*add_product: function (product, options) {
            var self = this;
            var order = self.pos.get_order();
            //var pricelist_id1 = order.pricelist
            //var conf_pricelist = self.pos.config.pricelist_id[0]
            if(this.get_client()){
                var pricelist_order_id = this.get_client().property_product_pricelist[0];
                console.log('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',pricelist_order_id)
            }
            _super.add_product.call(this, product, options);
            if (pricelist_order_id){
                    console.log('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',pricelist_order_id)
                    self.apply_pricelist(pricelist_order_id); 
            }
        },*/
    
		
		
		apply_pricelist: function(pricelist_id){
            var self = this;
            var pricelist_items = self.pos.pricelist_items;
            var items = [];
            for (var i in pricelist_items){
                if(pricelist_items[i].pricelist_id[0] == pricelist_id){
                    items.push(pricelist_items[i]);
                }
            }
            pricelist_items = [];
            var today = moment().format('YYYY-MM-DD');
            for (var i in items){
                if(((items[i].date_start == false) || (items[i].date_start <= today))
                                        && ((items[i].date_end == false) || (items[i].date_end >= today)))
                                        {
                                            pricelist_items.push(items[i]);
                                        }
            }
            var global_items = [];
            var category_items = [];
            var category_ids = [];
            var product_items = [];
            var product_ids = [];
            
            for(var i in pricelist_items){
                switch(pricelist_items[i].applied_on){
                case '3_global': global_items.push(pricelist_items[i]); break;
                case '2_product_category': category_items.push(pricelist_items[i]);
                    category_ids.push(pricelist_items[i].categ_id[0]) ; break;
                case '1_product': product_items.push(pricelist_items[i]);
                    product_ids.push(pricelist_items[i].product_tmpl_id[0]) ;break;
                }
            }
            

            var order = self.pos.get_order();
            var lines = order ? order.get_orderlines() : null;

            for (var l in lines){
                var product_item = self.find_pricelist_item(lines[l].product.product_tmpl_id, product_ids);
                var categ_item = self.find_pricelist_item(lines[l].product.categ_id[0], category_ids);
                
                var temp = -1;
                var new_price = lines[l].product.price;
                
                if(product_item){
                    
                    for(var j in product_items){
                        if(product_items[j].product_tmpl_id[0] == lines[l].product.product_tmpl_id){
                           if(lines[l].quantity >= product_items[j].min_quantity){
                                if(temp < 0){
                                    temp = lines[l].quantity - product_items[j].min_quantity;
                                    new_price = self.set_price(lines[l], product_items[j]);
                                }
                                else if(temp > (lines[l].quantity - product_items[j].min_quantity) &&
                                    (lines[l].quantity - product_items[j].min_quantity) >= 0){
                                    
                                    temp = lines[l].quantity - product_items[j].min_quantity;
                                    new_price = self.set_price(lines[l], product_items[j]);
                                }
                            }
                        }
                    }
                    lines[l].set_unit_price(new_price);
                }
                else if(categ_item){
                    for(var j in category_items){
                        if(category_items[j].categ_id[0] == lines[l].product.categ_id[0]){
                           if(lines[l].quantity >= category_items[j].min_quantity)
                            {
                                if(temp < 0){
                                    temp = lines[l].quantity - category_items[j].min_quantity;
                                    new_price = self.set_price(lines[l], category_items[j]);
                                }
                                else if(temp > (lines[l].quantity - category_items[j].min_quantity) &&
                                    (lines[l].quantity - category_items[j].min_quantity) >= 0){
                                    temp = lines[l].quantity - category_items[j].min_quantity;
                                    new_price = self.set_price(lines[l], category_items[j]);
                                }
                            }
                        }
                    }
                    lines[l].set_unit_price(new_price);
                }
//                if there are no rules set for product or category, we will check global pricelists
                else if(global_items.length > 0){
                    for(var j in global_items){
                        if(lines[l].quantity >= global_items[j].min_quantity)
                        {
                            if(temp < 0){
                                temp = lines[l].quantity - global_items[j].min_quantity;
                                new_price = self.set_price(lines[l], global_items[j]);
                            }
                            else if(temp > (lines[l].quantity - global_items[j].min_quantity) &&
                                (lines[l].quantity - global_items[j].min_quantity) >= 0){
                                temp = lines[l].quantity - global_items[j].min_quantity;
                                new_price = self.set_price(lines[l], global_items[j]);
                                
                            }
                        }
                    }
                    lines[l].set_unit_price(new_price);
                }
//                else we set the original price
                else{
                    lines[l].set_unit_price(lines[l].product.price);
                }
            }
        },
        
        set_price: function (line, item) {
            var self = this;
            var new_price = 0;
            
            if(item.compute_price == 'fixed'){
                new_price = item.fixed_price;
            }
            else if(item.compute_price == 'percentage'){
                
                new_price = line.product.lst_price -(line.product.lst_price * item.percent_price / 100);
                
            }
            else if(item.compute_price == 'formula'){
                
                new_price = line.product.lst_price

                if (item.base === 'pricelist') {
                    var pricelist_items = self.pos.pricelist_items;
                    for(var pr=0; pr < pricelist_items.length; pr++){
                        if(pricelist_items[pr]['id'] == item.base_pricelist_id[0]){
                            new_price = self.set_price(line, pricelist_items[pr])
                        }
                    }
                    
                } else if (item.base === 'standard_price') {
                    new_price = line.product.standard_price;
                }

                var price_limit = new_price;
                new_price = new_price - (new_price * (item.price_discount / 100));
                if (item.price_round) {
                    new_price = round_pr(new_price, item.price_round);
                }
                if (item.price_surcharge) {
                    new_price += item.price_surcharge;
                }
                if (item.price_min_margin) {
                    new_price = Math.max(new_price, price_limit + item.price_min_margin);
                }
                if (item.price_max_margin) {
                    new_price = Math.min(new_price, price_limit + item.price_max_margin);
                }
            }
            
            
            return new_price;
        },
        
        find_pricelist_item: function (id, item_ids) {
            for (var j in item_ids){
                if(item_ids[j] == id){
                    return true;
                    break;
                }
            }
            return false;
        },
        
        export_as_JSON: function() {
            var json = _super.export_as_JSON.apply(this,arguments);
            json.pricelist = this.pricelist;
            return json;
        },

	
	});
	
	
	//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	
	

        
    // ApplyMembershipPopupWidget start

    var ApplyMembershipPopupWidget = popups.extend({
        template: 'ApplyMembershipPopupWidget',
        
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        
        events: {
        	'click .button.confirm': 'apply_membership', 
        	'click .button.cancel': 'cancel_mem',        
        },
        
        cancel_mem: function(){
        	var self = this;
        	self.gui.close_popup();
        },
        
        apply_membership: function(){
        	var self = this;
        	var order = this.pos.get_order();
       		var selectedOrder = self.pos.get('selectedOrder');
       		var orderlines = order.orderlines;
        	var entered_code = $("#enter_card_code").val();
            var used = false;
            var mem_card_id = false;
            var pos_membership_card = self.pos.pos_membership
            var partner_id = false
            if (order.get_client() != null)
                partner_id = order.get_client();
        
            
            
            rpc.query({
		            model: 'pos.membership',
		            method: 'apply_membership_cards',
		            args: [partner_id ? partner_id.id : 0, entered_code],

                }).done(function(output) {
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
                        if (output == 'true') {
            
							rpc.query({
								model: 'pos.membership',
								method: 'search_membership_cards',
								args: [pos_membership_card[0].id, entered_code], //user_email
						
							}).fail(function(unused, event) {
							}).done(function(output) {
								
								mem_card_id = output[1];
								var mem_partner = output[3]
							
								if (mem_partner != partner_id.id){
									self.gui.show_popup('error', {
										'title': _t('Invalid Customer !!!'),
										'body': _t("This Membership Card Code is not applicable for this Customer"),
									});
								}
								else{
									order.apply_pricelist(mem_card_id); 
									$(".membershipmessage").html("<strong>" + "Congratulations... Membership Discount Applied</b>");
								}

								
							});
						}else { //Invalid Membership Card Code
                            alert('Invalid Membership Card Code');
                            self.gui.show_popup('error', {
                                'title': _t('Invalid Membership Card Code !!!'),
                                'body': _t("Membership Card Code Entered by you is Invalid. Enter Valid Code..."),
                            });
                        }
                    }
                    else { // Popup Shows, you can't use more than one Membership Card Code in single order.
                        self.gui.show_popup('error', {
                            'title': _t('Already Used !!!'),
                            'body': _t("You have already use this Membership Card Code, at a time you can use One Membership Card Code in a Single Order"),
                        });
                    }
						
            
            
            
            
            //console.log('?????????????????????????????????????????????',pos_membership_card)
            /*for(var m=0; m < pos_membership_card.length; m++){
            	if(pos_membership_card[m].membership_code == entered_code){
            		mem_card_id = pos_membership_card[m].membership_id.pricelist_id.id;
            		console.log('XXXXXXXXXXXXXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxXXXXXXXXXXXXXXXX',mem_card_id)
            	}
            		
            }*/
            
            //if (order.get_client() != null){
              //  partner_id = order.get_client();
            //}
                
            /*if (!partner_id) {
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
            }*/
            
            //if(mem_card_id != false){
            	//order.apply_pricelist(mem_card_id); 
            //}

	        self.pos.chrome.screens.payment.render_paymentlines();
	        self.gui.close_popup();
                        

			$('body').on('keypress', self.chrome.screens.payment.keyboard_handler);
			$('body').on('keydown', self.chrome.screens.payment.keyboard_keydown_handler);
			window.document.body.addEventListener('keypress', self.chrome.screens.payment.keyboard_handler);
			window.document.body.addEventListener('keydown', self.chrome.screens.payment.keyboard_keydown_handler);
			});

         
        },
        
        show: function(options) {
            var self = this;
            this._super(options);
            

        },

    });
    gui.define_popup({
        name: 'apply_membership_popup_widget',
        widget: ApplyMembershipPopupWidget
    });

    // End Popup start
    
    

	// PaymentScreenWidget start
	screens.PaymentScreenWidget.include({

		
		show: function(){
			var self = this;
			this.pos.get_order().clean_empty_paymentlines();
			this.reset_input();
			this.render_paymentlines();
			this.order_changes();
			
			this._super();
			
			
			self.$('.button.usemembershipmethod').click(function(){
				
				self.gui.show_popup('apply_membership_popup_widget', {});
				$('body').off('keypress', self.keyboard_handler);
            	$('body').off('keydown', self.keyboard_keydown_handler); 
				window.document.body.removeEventListener('keypress',self.keyboard_handler);
				window.document.body.removeEventListener('keydown',self.keyboard_keydown_handler);
				$('#enter_card_code').focus();
			});
			
			
		},
		
	 
	});    
        
    

});
