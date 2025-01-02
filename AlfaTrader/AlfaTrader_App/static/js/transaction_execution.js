document.addEventListener('DOMContentLoaded', function() {
    var csrftoken = document.querySelector('[name=csrf-token]').getAttribute('content');
    console.log("CSRF Token", csrftoken);
    // Fukcja do obliczania wartosci i ustawiania wartosci w polu value
    function calculateValue(row) {
        var quantity = row.querySelector('.quantity_buy').value;
        var close = row.querySelector('.quantity_buy').getAttribute('data-close');
        var valueInput = row.querySelector('.value_buy');
        var feesInput = row.querySelector('.fee_buy');
        var totalInput = row.querySelector('.total_buy');
        var stockId = row.querySelector('.btn.buy').getAttribute('data-id');


    //Jesli wpisano ilosc, oblicz wartosc
        if (quantity && !isNaN(quantity) && close && !isNaN(close)) {
            var value = (parseFloat(close) * parseFloat(quantity)).toFixed(2);
            valueInput.value = value;
            var fees = Math.max(parseFloat(value) * 0.002, 10).toFixed(2);
            feesInput.value = fees;
            var total = (parseFloat(value) + parseFloat(fees)).toFixed(2);
            totalInput.value = total;

            // Debugowanie: Logowanie wyników obliczeń
            console.log("Quantity: ", quantity);
            console.log("Close price: ", close);
            console.log("Calculated value: ", value);
            console.log("Calculated fees: ", fees);
            console.log("Calculated total: ", total);
            console.log("Stock id: ", stockId);

        } else {
            valueInput.value = "0";
            feesInput.value = "0";
            totalInput.value = "0";
        }
    }

    //Obsluga zmainy w polu quantity
    document.querySelector('.quantity_buy').addEventListener('input', function () {
        var row = this.closest('table');
        var quantityBuy = this.value;

        if (parseInt(quantityBuy) <1) {
            this.value = 1;
        }
        calculateValue(row);
    });
        });




    // //Oblsuga klikniecia przycisku buy
    // document.querySelectorAll('.btn.btn-primary.buy').forEach(function(button) {
    //     button.addEventListener('click', function(event) {
    //         var row = event.target.closest('table');
    //         var quantity = row.querySelector('.quantity_buy').value;
    //         var value = row.querySelector('.value_buy').value;
    //         var stockId = row.querySelector('.btn.btn-primary.buy').getAttribute('data-id');
    //         var close = row.querySelector('.quantity_buy').getAttribute('data-close');
    //         var fees = row.querySelector('.fee_buy').value;
    // //Jesli ilosc jest podana wyslij dane do serwera za pomoca AJAX
    //
    //
    //         if (quantity && value && close && fees) {
    //             var xhr = new XMLHttpRequest();
    //             xhr.open('POST', '/buy_transaction/', true);
    //             xhr.setRequestHeader('Content-Type', 'application/json');
    //             xhr.setRequestHeader('X-CSRFToken', csrftoken);
    //
    // //Dane do wyslania
    //             var data = JSON.stringify({
    //                 'stock_id': stockId,
    //                 'quantity': quantity,
    //                 'value': value,
    //                 'close': close,
    //                 'transaction_type': 'BUY',
    //                 'fees': fees,
    //             });
    //
    //             console.log("Sending data:", data)
    //
    //             xhr.onload = function() {
    //                 if (xhr.status == 200) {
    //                     alert('Transaction successful!');
    //                 } else {
    //                     console.error('Error response', xhr.responseText);
    //                     alert('Transaction failed', + xhr.responseText)
    //                 }
    //             };
    //             xhr.onerror = function() {
    //                 alert('Network error occured.');
    //             };
    //
    //             if (data.trim() === "") {
    //                 console.error("Data is empty");
    //             }
    //
    //             xhr.send(data);
    //         } else {
    //             alert('Please enter quantity and value.');
    //         }
    //     });
    // });











