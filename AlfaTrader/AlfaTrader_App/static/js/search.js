document.addEventListener('DOMContentLoaded', function(){
    // Fukcja do obliczania wartosci i ustawiania wartosci w polu value
    function calculateValue(row) {
        var quantity = row.querySelector('.quantity').value;
        var close = row.querySelector('.quantity').getAttribute('data-close');

    //Jesli wpisano ilosc, oblicz wartosc
        if (quantity && !isNaN(quantity) && close && !isNaN(close)) {
            var value = (parseFloat(close) * parseFloat(quantity)).toFixed(2);
            row.querySelector('.value').value = value;
        } else {
            row.querySelector('.value').value = "0";
        }
    }
    //Obsluga zmainy w polu quantity
    document.querySelectorAll('.quantity').forEach(function(input) {
        input.addEventListener('input', function(event) {
            var row = event.target.closest('tr');
            calculateValue(row);
        });
    });
    //Oblsuga klikniecia przycisku buy
    document.querySelectorAll('.buy-btn').forEach(function(button) {
        button.addEventListener('click', function(event) {
            var row = event.target.closest('tr');
            var quantity = row.querySelector('.quantity').value;
            var value = row.querySelector('.value').value;
            var stockId = row.querySelector('.buy-btn').getAttribute('data-id');
            var close = row.querySelector('.close').textContent;
    //Jesli ilosc jest podana wyslij dane do serwera za pomoca AJAX
            if (quantity && value) {
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/buy_transaction/', true);
                xhr.setRequestHeader('Content-Type', 'application/json');
    //Dane do wyslania
                var data = JSON.stringify({
                    'stock_id': stockId,
                    'quantity': quantity,
                    'value': value,
                    'close': close
                });
                xhr.onload = function() {
                    if (xhr.status == 200) {
                        alert('Transaction successful!');
                    } else {
                        alert('Transaction failed.');
                    }
                };
                xhr.send(data);
            } else {
                alert('Please enter quantity.');
            }
        });
    });


    function searchTable() {
        var input, filter, table, tr, td, i, txtValue;
        input = document.getElementById('search');
        filter = input.value.toUpperCase();
        table = document.querySelector('table');
        tr = table.getElementsByTagName('tr');

        for (i = 1; i < tr.length; i++) {
            td = tr[i].getElementsByTagName('td')[1];
            if (td) {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = '';
                } else {
                    tr[i].style.display = 'none';
                }
            }
        }
    }
    document.getElementById('search').addEventListener('keyup', searchTable);

});