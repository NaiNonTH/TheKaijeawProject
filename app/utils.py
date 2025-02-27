from .models import Order, Filling, Egg, Restaurant

class OrderBuilder: # builder class (Builder Design Pattern)
    __order = None

    def __init__(self, egg_amount_obj):
        queue_number = self.get_queue_number()

        self.__order = Order.objects.create(
            egg_amount=egg_amount_obj,
            queue_number=queue_number
        )

    @classmethod # factory method (Factory Design Pattern)
    def validate_and_create(self, post_data):
        user_errors = []

        if "egg" not in post_data:
            user_errors.append("ท่านไม่ได้ระบุจำนวนไข่")

        restaurant = Restaurant.objects.last()

        fillings_list = post_data.getlist("filling")
        if len(fillings_list) > restaurant.max_fillings:
            user_errors.append(f"ท่านเลือกไส้เกิน {restaurant.max_fillings} ตัวเลือก")

        if len(user_errors) > 0:
            return None, {
                "intro_text": "ข้อมูลที่กรอกไม่สมบูรณ์เนื่องจาก...",
                "middle_list": user_errors,
                "outro_text": "กรุณากรอกข้อมูลให้ครบถ้วนแล้วลองใหม่อีกครั้ง"
            }

        try:
            egg_amount_obj = Egg.objects.get(pk=post_data["egg"])
        except Egg.DoesNotExist:
            user_errors.append("ไม่พบจำนวนไข่ที่ระบุ")
            return None, {
                "intro_text": "ข้อมูลที่กรอกไม่สมบูรณ์เนื่องจาก...",
                "middle_list": user_errors,
                "outro_text": "กรุณากรอกข้อมูลให้ครบถ้วนแล้วลองใหม่อีกครั้ง"
            }

        is_takeaway = "is_takeaway" in post_data
        unavailable_titles = []
        
        unavailable_fillings = Filling.objects.filter(name__in=fillings_list, is_available=False)

        if unavailable_fillings.exists():
            unavailable_titles.extend([f.title for f in unavailable_fillings])
        
        cannot_takeaway = is_takeaway and not restaurant.allow_takeaway
        
        if cannot_takeaway:
            unavailable_titles.append("กล่อง")
        
        if unavailable_titles:
            return None, {
                "intro_text": "รายละเอียดเมนูที่ท่านเลือกเหล่านี้มีการเปลี่ยนแปลง",
                "middle_list": unavailable_titles,
                "outro_text": "กรุณาเลือกใหม่อีกครั้ง และขออภัยในความไม่สะดวก"
            }
        
        # ข้อมูลผ่านการ validate แล้ว
        builder = self(egg_amount_obj)
        return builder, None

    def takeaway(self, is_takeaway=True):
        self.__order.is_takeaway = is_takeaway
        return self

    def add_fillings(self, fillings_list):
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
                raise self.NoQueueLeftError

            queue_number = unavailable_queues[-1] % max_queue_number + 1

            while queue_number in unavailable_queues:
                queue_number = (queue_number + 1) % max_queue_number

        return queue_number
    
    class NoQueueLeftError(Exception): ...

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_order_changes(instance):
    channel_layer = get_channel_layer()

    fillings_data = [filling.title for filling in instance.fillings.all()]

    async_to_sync(channel_layer.group_send)(
        "order_watcher",
        {
            "type": "order_update",
            "message": {
                "type": "order_added",
                "id": instance.pk,
                "queue_number": instance.queue_number,
                "fillings": fillings_data,
                "egg": instance.egg_amount.amount,
                "box": instance.is_takeaway
            }
        }
    )