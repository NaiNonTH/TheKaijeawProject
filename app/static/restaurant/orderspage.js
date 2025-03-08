(function() {
    const orders = document.getElementById("orders");
    const noOrder = document.getElementById("no-orders-text")
    
    const socket = new WebSocket(`ws://${location.host}/ws/order-watcher`);
    const audio = new Audio("/static/bell.wav");

    const markOrderAsDone = function(event) {
        event.preventDefault();
        const data = {
            id: event.currentTarget.dataset.id
        }

        socket.send(JSON.stringify(data));
    };
    
    // เช็คเมื่อมี order ใหม่เข้ามาแล้วเพิ่ม order เข้าไปใน UI
    socket.addEventListener("message", function(event) {
        const data = JSON.parse(event.data)

        if (data.type === "order_added") {
            noOrder.hidden = true;
            const orderCard = document.createElement("div");
            orderCard.innerHTML = createOrderCard(data);

            orderCard.querySelector("form button[type='submit']")
                .addEventListener("click", markOrderAsDone);

            orders.appendChild(orderCard.firstChild);

            audio.play();
        }
        else if (data.type === "order_marked_as_done") {
            if (data.success) {
                document.getElementById("order-" + data.order_id).remove();
                
                if (document.querySelectorAll(".order").length == 0)
                    noOrder.hidden = false;
            }
            else {
                console.error(data.message);
            }
        }
    });
    
    // หยุุดการเชื่อมต่อเมื่อปิด web browser หรือเปลี่ยนหน้า
    window.addEventListener("close", function() {
        socket.close();
    });

    document.querySelectorAll("form button[type='submit']")
        .forEach(function(button) {
            button.addEventListener("click", markOrderAsDone);
        });
})();