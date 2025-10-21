# ==================== bot.py (Updated) ====================
import telebot
import subprocess
import re
import os
from threading import Thread
import time

# Lấy token từ biến môi trường
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("⚠️ Chưa cấu hình BOT_TOKEN trong environment variables!")

bot = telebot.TeleBot(BOT_TOKEN)

# Heartbeat để giữ service hoạt động
def keep_alive():
    while True:
        time.sleep(300)  # Ping mỗi 5 phút
        print("🔄 Bot đang hoạt động...")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
                 "🤖 Bot đang chạy trên Render!\n\n"
                 "Sử dụng lệnh:\n"
                 "/sms <10 số> <2 số>\n\n"
                 "Ví dụ: /sms 0123456789 12")

@bot.message_handler(commands=['sms'])
def handle_sms(message):
    try:
        # Lấy các tham số từ lệnh
        args = message.text.split()[1:]
        
        # Kiểm tra số lượng tham số
        if len(args) != 2:
            bot.reply_to(message, "❌ Lỗi: Cần đúng 2 tham số!\n"
                                  "Sử dụng: /sms <10 số> <2 số>")
            return
        
        phone_number = args[0]
        two_digit = args[1]
        
        # Kiểm tra định dạng số điện thoại (10 chữ số)
        if not re.match(r'^\d{10}$', phone_number):
            bot.reply_to(message, "❌ Lỗi: Số điện thoại phải có đúng 10 chữ số!")
            return
        
        # Kiểm tra định dạng 2 chữ số
        if not re.match(r'^\d{2}$', two_digit):
            bot.reply_to(message, "❌ Lỗi: Tham số thứ 2 phải có đúng 2 chữ số!")
            return
        
        # Thông báo đang xử lý
        bot.reply_to(message, f"⏳ Đang thực thi lệnh với:\n"
                              f"📱 Số: {phone_number}\n"
                              f"🔢 Mã: {two_digit}")
        
        # Chạy lệnh python start.py với các tham số
        cmd = ['python', 'start.py', phone_number, two_digit]
        
        # Thực thi lệnh
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # Timeout 5 phút
        )
        
        # Gửi kết quả
        if result.returncode == 0:
            output = result.stdout if result.stdout else "✅ Lệnh thực thi thành công!"
            # Giới hạn 4000 ký tự cho Telegram
            if len(output) > 4000:
                bot.reply_to(message, f"✅ Hoàn thành!\n\n{output[:3900]}...\n\n(Kết quả quá dài, đã cắt bớt)")
            else:
                bot.reply_to(message, f"✅ Hoàn thành!\n\n{output}")
        else:
            error = result.stderr if result.stderr else "Lỗi không xác định"
            if len(error) > 4000:
                bot.reply_to(message, f"❌ Lỗi:\n\n{error[:3900]}...\n\n(Lỗi quá dài, đã cắt bớt)")
            else:
                bot.reply_to(message, f"❌ Lỗi khi thực thi:\n\n{error}")
            
    except subprocess.TimeoutExpired:
        bot.reply_to(message, "⏱️ Lệnh thực thi quá lâu (timeout 5 phút)")
    except FileNotFoundError:
        bot.reply_to(message, "❌ Không tìm thấy file start.py!\n"
                              "Đảm bảo file start.py đã được deploy lên Render.")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
📖 Hướng dẫn sử dụng:

/start - Khởi động bot
/sms <10 số> <2 số> - Chạy lệnh với tham số
/status - Kiểm tra trạng thái bot
/help - Xem hướng dẫn

Ví dụ:
/sms 0123456789 12

🌐 Bot đang chạy trên Render
"""
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['status'])
def send_status(message):
    status_text = f"""
✅ Bot đang hoạt động!

📊 Thông tin:
- Platform: Render
- Python: {os.sys.version.split()[0]}
- Thư mục: {os.getcwd()}
"""
    bot.reply_to(message, status_text)

if __name__ == '__main__':
    print("🚀 Bot đang khởi động trên Render...")
    print(f"📁 Thư mục hiện tại: {os.getcwd()}")
    print(f"📄 Files: {os.listdir('.')}")
    
    # Chạy heartbeat trong background
    Thread(target=keep_alive, daemon=True).start()
    
    # Chạy bot
    print("🤖 Bot đã sẵn sàng!")
    bot.infinity_polling()