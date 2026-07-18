// /** @odoo-module **/

// import publicWidget from "@web/legacy/js/public/public_widget";

// publicWidget.registry.SignUpForm.include({
//     selector: '.oe_signup_form',
//     events: Object.assign({}, publicWidget.registry.SignUpForm.prototype.events, {
//         'change select.country_id': '_onChangeCountryId',
//     }),

//     //--------------------------------------------------------------------------
//     // Handlers
//     //--------------------------------------------------------------------------

//     /**
//      * @private
//      */
//     // _onSubmit: function () {
//     //     var $btn = this.$('.oe_login_buttons > button[type="submit"]');
//     //     $btn.attr('disabled', 'disabled');
//     //     $btn.prepend('<i class="fa fa-refresh fa-spin"/> ');
//     // },

//     /**
//      * @private
//      */
//     _onChangeCountryId:function(ev){
//         const $target = $(ev.currentTarget);
//         const $state = $target.closest("form.oe_signup_form").find('select[name="state_id"]');
//         $state.find('option').hide();
//         let countryId = $target.val();
//         $state.find('option')[0].selected=true;
//         if (!countryId) {
//             return;
//         }
//         $state.find(`option[data-country_id="${countryId}"]`).show();

//     },
// });
