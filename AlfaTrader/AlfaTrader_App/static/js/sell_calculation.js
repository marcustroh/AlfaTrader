document.addEventListener('DOMContentLoaded', function() {
    var csrftoken = document.querySelector('[name=csrf-token]').getAttribute('content');
    console.log("CSRF Token", csrftoken);

    // Pobieramy dostępne akcje z formularza
    var remainingShares = parseInt(document.querySelector('[name="remaining_shares"]').value);

    // Ustawiamy atrybut max w polu quantity_sell
    var quantitySellInput = document.querySelector('.quantity_sell');
    quantitySellInput.setAttribute('max', remainingShares);

    // Fukcja do obliczania wartosci i ustawiania wartosci w polu value
    function calculateValueSell(row) {
        var quantitySell = row.querySelector('.quantity_sell').value;
        var close = row.querySelector('.close_price_sell').value;
        var costPrice = row.querySelector('.cost_price').value;
        var valueInputSell = row.querySelector('.value_sell');
        var feesInputSell = row.querySelector('.fees_sell');
        var totalInputSell = row.querySelector('.total_sell');
        var profitLoss = row.querySelector('.profit-loss');
        var stockId = row.querySelector('.btn.sell').getAttribute('data-id');

        // Sprawdzamy, czy użytkownik nie wpisał więcej niż dostępne akcje
        if (quantitySell && !isNaN(quantitySell)) {
            // Ograniczamy maksymalną ilość akcji do dostępnych
            if (parseInt(quantitySell) > remainingShares) {
                alert("You cannot sell more shares than you have available.");
                row.querySelector('.quantity_sell').value = remainingShares;  // Resetujemy wartość do dostępnych akcji
                quantitySell = remainingShares;  // Zaktualizowanie wartości
            }
            if (parseInt(quantitySell) <1) {
                row.querySelector('.quantity_sell').value = 1;
            }
        }


    //Jesli wpisano ilosc, oblicz wartosc
        if (quantitySell && !isNaN(quantitySell) && close && !isNaN(close) && costPrice && !isNaN(costPrice)) {
            var value = (parseFloat(close) * parseFloat(quantitySell)).toFixed(2);
            valueInputSell.value = value;
            var fees = Math.max(parseFloat(value) * 0.002, 10).toFixed(2);
            feesInputSell.value = fees;
            var total = (parseFloat(value) - parseFloat(fees)).toFixed(2);
            totalInputSell.value = total;
            var gainLoss = ((((parseFloat(close) - parseFloat(costPrice)) * parseFloat(quantitySell))) - parseFloat(fees)).toFixed(2)
            profitLoss.value = gainLoss


            // Debugowanie: Logowanie wyników obliczeń
            console.log("Quantity: ", quantitySell);
            console.log("Close price: ", close);
            console.log("Cost price", costPrice);
            console.log("Calculated value: ", value);
            console.log("Calculated fees: ", fees);
            console.log("Calculated total: ", total);
            console.log("Calculated Profit Loss:", gainLoss);
            console.log("Stock id: ", stockId);

        } else {
            valueInputSell.value = "0";
            feesInputSell.value = "0";
            totalInputSell.value = "0";
            profitLoss.value = "0";
        }
    }

    // Obsluga zmainy w polu quantity
    document.querySelector('.quantity_sell').addEventListener('input', function () {
        var row = this.closest('.sell-table');
        calculateValueSell(row);
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























