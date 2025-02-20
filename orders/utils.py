from .models import Order, Filling, Egg, Restaurant, Validator

class OrderBuilder:
    __order = None

    def __init__(self, amount):
        egg_amount = Egg.objects.get(pk=amount)
        queue_number = self.get_queue_number()

        self.__order = Order.objects.create(
            egg_amount=egg_amount,
            queue_number=queue_number
        )

    def takeaway(self, is_takeaway = True):
        self.__order.is_takeaway = is_takeaway
        return self

    def add_fillings(self, fillings_list):
        if len(fillings_list) > 3:
            raise Validator.TooManyFillingsError
    
        for filling_name in fillings_list:
            filling = Filling.objects.get(pk=filling_name)
            self.__order.fillings.add(filling)

        return self
    
    def build(self):
        return self.__order

    def get_queue_number(self):
        if len(Order.objects.filter(is_completed=False).all()) == 0:
            queue_number = 1
        else:
            incompleted_orders = Order.objects.filter(is_completed=False)
            unavailable_queues = [order.queue_number for order in list(incompleted_orders.all())]

            max_queue_number = Restaurant.objects.last().queue_capacity

            if len(unavailable_queues) == max_queue_number:
                raise Validator.NoQueueLeftError

            queue_number = unavailable_queues[-1] % max_queue_number + 1

            while queue_number in unavailable_queues:
                queue_number = (queue_number + 1) % max_queue_number

        return queue_number