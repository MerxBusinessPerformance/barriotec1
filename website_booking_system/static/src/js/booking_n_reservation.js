/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* @License       : https://store.webkul.com/license.html */

odoo.define("website_booking_system.booking_n_reservation", function (require) {
  "use strict"

  var ajax = require("web.ajax")
  var core = require("web.core")
  var _t = core._t

  var Days = {
    sun: 0,
    mon: 1,
    tue: 2,
    wed: 3,
    thu: 4,
    fri: 5,
    sat: 6,
  }

  // Traducción de calendario
  $.datepicker.regional["es"] = {
    //  https://stackoverflow.com/questions/1452681/jquery-datepicker-localization
    closeText: "Seleccionar",
    currentText: "Hoy",
    monthNames: [
      "Enero",
      "Febrero",
      "Marzo",
      "Abril",
      "Mayo",
      "Junio",
      "Julio",
      "Agosto",
      "Septiembre",
      "Octubre",
      "Noviembre",
      "Diciembre",
    ],
    monthNamesShort: [
      "Ene",
      "Feb",
      "Mar",
      "Abr",
      "May",
      "Jun",
      "Jul",
      "Ago",
      "Sep",
      "Oct",
      "Nov",
      "Dic",
    ],
  }
  $.datepicker.setDefaults($.datepicker.regional["es"])

  $(document).ready(function () {
    var startDate = new Date()
    var endDate = new Date()
    var PlanPrice
    //  Costo de plan
    let base_price = 0

    var reset_total_price = function () {
      var bk_total_price = $("#booking_modal").find(
        ".bk_total_price .oe_currency_value"
      )
      bk_total_price.html("0.00")
    }

    var get_w_closed_days = function (w_c_days) {
      if (w_c_days) {
        return w_c_days.map(day => Days[day])
      }
      return []
    }

    function GetFormate(num) {
      if (num < 10) {
        return "0" + num
      }
      return num
    }

    function GetFormattedDate(date) {
      var month = GetFormate(date.getMonth() + 1)
      var day = GetFormate(date.getDate())
      var year = date.getFullYear()
      return day + "/" + month + "/" + year
    }

    var update_total_price = function () {
      let extra = base_price
      PlanPrice = extra

      var appdiv = $("#booking_modal")
      var product_id = parseInt(appdiv.data("res_id"), 10)
      var bk_loader = $("#bk_n_res_loader")

      bk_loader.show()
      ajax
        .jsonRpc("/booking/reservation/modal/update_price", "call", {
          product_id: product_id,
          from_date: GetFormattedDate(startDate),
          to_date: GetFormattedDate(endDate),
        })
        .then(function (result) {
          bk_loader.hide()
          var bk_plan_base_price = $("#booking_modal").find(
            ".bk_plan_base_price .oe_currency_value"
          )
          var bk_total_price = appdiv.find(".bk_total_price .oe_currency_value")

          bk_plan_base_price.html((result.price + PlanPrice).toFixed(2))
          bk_total_price.html((result.price + PlanPrice).toFixed(2))
          ajax
            .jsonRpc("/booking/reservation/price_list_plus_plan", "call", {
              product_id,
            })
            .then(respuesta => {
              let price_list_plus_plan = respuesta.price + PlanPrice

              price_list_plus_plan = parseFloat(
                price_list_plus_plan
              ).toLocaleString("en", { minimumFractionDigits: 2 })

              $("#total_especial").html(price_list_plus_plan)

              // Agregamos la descripcion del plan

              let plan_name = $(
                ".bk_model_plans input:checked + .bk_plan_div .d-none.d-sm-block div:first-child "
              )
                .text()
                .trim()

              let $plan_descripcion = $("#booking_modal_descripcion_plan")
              if (plan_name) {
                $plan_descripcion.removeClass("d-none")
                $plan_descripcion
                  .find(".texto")
                  .html(
                    respuesta.plans.find(x => plan_name === x.name).description
                  )
              } else {
                $plan_descripcion.addClass("d-none")
              }
            })
            .catch(_ => console.log("error", _))
        })
    }

    // Booking pop-up modal
    $("#booking_and_reservation").click(function (evnt) {
      var appdiv = $("#booking_modal")
      var bk_loader = $("#bk_n_res_loader")
      var product_id = parseInt(appdiv.data("res_id"), 10)
      var redirect = window.location.pathname
      bk_loader.show()
      ajax
        .jsonRpc("/booking/reservation/modal", "call", {
          product_id: product_id,
        })
        .then(function (modal) {
          bk_loader.hide()
          var $modal = $(modal)

          $modal
            .appendTo(appdiv)
            .modal("show")
            .on("hidden.bs.modal", function () {
              $(this).remove()
            })

          function datepicker_onClose(dateText, inst) {
            function isDonePressed() {
              return (
                $("#ui-datepicker-div")
                  .html()
                  .indexOf(
                    "ui-datepicker-close ui-state-default ui-priority-primary ui-corner-all ui-state-hover"
                  ) > -1
              )
            }

            if (isDonePressed()) {
              var month = $(
                "#ui-datepicker-div .ui-datepicker-month :selected"
              ).val()
              var year = $(
                "#ui-datepicker-div .ui-datepicker-year :selected"
              ).val()
              $(this)
                .datepicker(
                  "setDate",
                  new Date(year, month, new Date().getDate())
                )
                .trigger("change")

              $(".date-picker").focusout() //Added to remove focus from datepicker input box on selecting date
            }
          }
          $(function () {
            function datepicker_beforeShow(input, inst) {
              inst.dpDiv.addClass("month_year_datepicker")
              let datestr = $(this).val()
              if (datestr.length < 1) {
                let year = datestr.substring(datestr.length - 4, datestr.length)
                let month = datestr.substring(0, 2)
                let day = new Date().getDate()

                $(this).datepicker("setDate", new Date(year, month - 1, day))
                $(".ui-datepicker-calendar").hide()
              }
            }
            $("#bk_sel_date").datepicker({
              dateFormat: "yy-mm-dd",
              format: "YYYY-MM-DD",
              changeMonth: true,
              changeYear: true,
              showButtonPanel: true,
              icons: {
                date: "fa fa-calendar",
                next: "fa fa-chevron-right",
                previous: "fa fa-chevron-left",
              },
              minDate: $("#bk_datepicker").data("bk_default_date"),
              maxDate: $("#bk_datepicker").data("bk_end_date"),
              daysOfWeekDisabled: get_w_closed_days(
                $("#bk_datepicker").data("w_c_days")
              ),
              onClose: datepicker_onClose,
              beforeShow: datepicker_beforeShow,
            })

            $("#bk_sel_date_out").datepicker({
              dateFormat: "yy-mm-dd",
              format: "YYYY-MM-DD",
              changeMonth: true,
              changeYear: true,
              showButtonPanel: true,
              icons: {
                date: "fa fa-calendar",
                next: "fa fa-chevron-right",
                previous: "fa fa-chevron-left",
              },
              minDate: startDate,
              maxDate: $("#bk_datepicker").data("bk_end_date"),
              daysOfWeekDisabled: get_w_closed_days(
                $("#bk_datepicker").data("w_c_days")
              ),
              onClose: datepicker_onClose,
              beforeShow: datepicker_beforeShow,
            })
          })

          $("#bk_datepicker").on("change.datetimepicker", function (e) {
            startDate = new Date($(this).find("input").val())
            //Actualizar fecha minima
            $("#bk_sel_date_out").datepicker(
              "option",
              "minDate",
              new Date(startDate.setMonth(startDate.getMonth() + 1))
            )

            var booking_modal = $("#booking_modal")
            // booking_modal
            //   .find(".bk_model_plans")
            //   .find("input[name='bk_plan']")
            //   .prop("checked", false)
            update_total_price()
          })

          $("#bk_datepicker_out").on("change.datetimepicker", function (e) {
            // var date = new Date(e.date)
            // var o_date = new Date(e.oldDate)

            var booking_modal = $("#booking_modal")
            // booking_modal
            //   .find(".bk_model_plans")
            //   .find("input[name='bk_plan']")
            //   .prop("checked", false)

            // if (GetFormattedDate(date) != GetFormattedDate(o_date)) {
            endDate = new Date($(this).find("input").val())
            update_total_price()
            // }
          })
        })
    })

    // Booking day slot selection
    $("#booking_modal").on("click", ".bk_slot_div", function (evnt) {
      var $this = $(this)
      var slot_plans = $this.data("slot_plans")
      var booking_modal = $("#booking_modal")
      var bk_loader = $("#bk_n_res_loader")
      var time_slot_id = parseInt($this.data("time_slot_id"), 10)
      var model_plans = booking_modal.find(".bk_model_plans")
      var bk_modal_slots = booking_modal.find(".bk_modal_slots")
      var product_id = parseInt(booking_modal.data("res_id"), 10)
      var bk_sel_date = $("#bk_sel_date")
      bk_loader.show()
      ajax
        .jsonRpc("/booking/reservation/slot/plans", "call", {
          time_slot_id: time_slot_id,
          slot_plans: slot_plans,
          sel_date: bk_sel_date.val(),
          product_id: product_id,
        })
        .then(function (result) {
          bk_loader.hide()
          reset_total_price()
          model_plans.html(result)
        })
      bk_modal_slots
        .find(".bk_slot_div")
        .not($this)
        .each(function () {
          var $this = $(this)
          if ($this.hasClass("bk_active")) {
            $this.removeClass("bk_active")
          }
        })
      if (!$this.hasClass("bk_active")) {
        $this.addClass("bk_active")
      }
    })

    // Booking Week Day Selection
    $("#booking_modal").on("click", ".bk_days", function (evnt) {
      var $this = $(this)
      if ($this.hasClass("bk_disable")) {
        return false
      }
      var booking_modal = $("#booking_modal")
      var bk_loader = $("#bk_n_res_loader")
      var product_id = parseInt(booking_modal.data("res_id"), 10)
      var bk_week_days = booking_modal.find(".bk_week_days")
      var bk_model_cart = booking_modal.find(".bk_model_cart")
      var bk_model_plans = booking_modal.find(".bk_model_plans")
      var bk_slots_n_plans_div = booking_modal.find(".bk_slots_n_plans_div")
      var w_day = $this.data("w_day")
      var w_date = $this.data("w_date")
      var bk_sel_date = $("#bk_sel_date")
      bk_week_days
        .find(".bk_days")
        .not($this)
        .each(function () {
          var $this = $(this)
          if ($this.hasClass("bk_active")) {
            $this.removeClass("bk_active")
          }
        })
      if (!$this.hasClass("bk_active")) {
        $this.addClass("bk_active")
      }
      bk_loader.show()
      ajax
        .jsonRpc("/booking/reservation/update/slots", "call", {
          w_day: w_day,
          w_date: w_date,
          product_id: product_id,
        })
        .then(function (result) {
          bk_loader.hide()
          reset_total_price()
          bk_slots_n_plans_div.html(result)
        })
      bk_sel_date.val(w_date)
    })

    // Booking quantity Selection
    $("#booking_modal").on("change", ".bk_qty_sel", function (evnt) {
      var bk_qty = parseInt($(this).val(), 10)
      var booking_modal = $("#booking_modal")
      // var add_qty = booking_modal.closest('form').find("input[name='add_qty']");
      var bk_base_price = parseFloat(
        booking_modal.find(".bk_plan_base_price .oe_currency_value").html(),
        10
      )
      var bk_total_price = booking_modal.find(
        ".bk_total_price .oe_currency_value"
      )
      // add_qty.val(bk_qty);
      bk_total_price.html((bk_base_price * bk_qty).toFixed(2))
    })

    // Click on Book Now button on booking modal: submit a form available on product page
    $("#booking_modal").on("click", ".bk-submit", function (event) {
      var $this = $(this)
      var booking_modal = $("#booking_modal")
      var bk_loader = $("#bk_n_res_loader")
      var product_id = parseInt(booking_modal.data("res_id"), 10)
      var bk_model_plans = booking_modal
        .find(".bk_model_plans")
        .find("input[name='bk_plan']:checked")
      var bk_modal_err = booking_modal.find(".bk_modal_err")
      if (bk_model_plans.length == 0) {
        bk_modal_err.html("Please select a plan to proceed further!!!").show()
        setTimeout(function () {
          bk_modal_err.empty().hide()
        }, 3000)
      } else {
        if (!event.isDefaultPrevented() && !$this.is(".disabled")) {
          bk_loader.show()
          ajax
            .jsonRpc("/booking/reservation/cart/validate", "call", {
              product_id: product_id,
            })
            .then(function (result) {
              if (result == true) {
                event.preventDefault()
                $this.closest("form").submit()
              } else {
                bk_loader.hide()
                bk_modal_err
                  .html(
                    "Este producto ya está en tu carrito. Por favor remuevlo e intenta de nuevo"
                  )
                  .show()
                setTimeout(function () {
                  bk_modal_err.empty().hide()
                }, 3000)
              }
            })
        }
      }
    })

    // Booking Slot Plan Selection
    $("#booking_modal").on("click", "input[name='bk_plan']", function (event) {
      var bk_plan_div = $(this).closest("label").find(".bk_plan_div")
      base_price = parseInt(bk_plan_div.data("plan_price"), 10)

      if (isNaN(base_price)) {
        base_price = 0.0
      }

      update_total_price()
      // var booking_modal = $('#booking_modal');
      // var bk_plan_div = $(this).closest('label').find('.bk_plan_div');
      // var bk_plan_base_price = $('#booking_modal').find(".bk_plan_base_price .oe_currency_value");
      // var base_price = parseInt(bk_plan_div.data('plan_price'), 10);
      // var bk_total_price = booking_modal.find('.bk_total_price .oe_currency_value');
      // var bk_qty = parseInt(booking_modal.find('.bk_qty_sel').val(),10);
      // if(bk_plan_div.hasClass('bk_disable')){
      //     return false;
      // };
      // if(isNaN(base_price)){
      //     base_price = 0.0;
      // }

      // console.log(base_price.toFixed(2))

      // bk_plan_base_price.html(base_price.toFixed(2));
      // bk_total_price.html((base_price*bk_qty).toFixed(2));
    })

    // Click on remove button available on sold out product in cart line
    $(".oe_website_sale").each(function () {
      var oe_website_sale = this
      $(oe_website_sale).on("click", ".remove-cart-line", function () {
        var $dom = $(this).closest("tr")
        var td_qty = $dom.find(".td-qty")
        var line_id = parseInt(td_qty.data("line-id"), 10)
        var product_id = parseInt(td_qty.data("product-id"), 10)
        ajax
          .jsonRpc("/shop/cart/update_json", "call", {
            line_id: line_id,
            product_id: product_id,
            set_qty: 0.0,
          })
          .then(function (data) {
            var $q = $(".my_cart_quantity")
            $q.parent().parent().removeClass("hidden", !data.quantity)
            $q.html(data.cart_quantity).hide().fadeIn(600)
            location.reload()
          })
      })
    })
  })
})
