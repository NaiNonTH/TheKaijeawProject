# The Kaijeaw Project

โปรเจ็กต์แอพจัดคิวร้านไข่เจียว

## สิ่งที่ต้องใช้
* Python
* git

## Run บนเครื่องตัวเอง

1. ให้ clone repository ของแอพ The Kaijeaw Project ด้วยคำสั่งนี้

```ps1
git clone https://github.com/NaiNonTH/TheKaijeawProject.git
```

2. เข้าไปที่โฟล์เดอร์ TheKaijeawProject แล้วสร้าง Python Virtual Environment โดยใช้คำสั่ง

```ps1
python -m venv .venv
```

3. ให้ Activate Virtual Environment ที่สร้างขึ้นมาโดยใช้หนึ่งในคำสั่งเหล่านี้ ขึ้นอยู่กับ Shell ที่ใช้
  * สำหรับ Powershell

  ```ps1
  ./.venv/Scripts/activate.ps1
  ```

  * สำหรับ Command Prompt (Batch)

  ```bat
  ./.venv/Scripts/activate.bat
  ```

  * สำหรับ Bash หรือ zsh

  ```sh
  ./.venv/Scripts/activate
  ```

  * สำหรับ fish

  ```fish
  ./.venv/Scripts/activate.fish
  ```

4. ให้ติดตั้ง Packages จากไฟล์ `requirements.txt` ที่ต้องใช้โดยใช้คำสั่งนี้

```ps1
pip install -r requirements.txt
```

5. Migrate เพื่อสร้างตารางและฐานข้อมูล

```ps1
python manage.py migrate
```

6. รัน server ด้วยคำสั่งนี้

```ps1
python manage.py runserver
```