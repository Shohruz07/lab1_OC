import threading
import time

class MutexData:
    def __init__(self):
        self.m_mutex = threading.Lock() # Мьютекс (синхронизация доступа к данным)
        self.m_notification = threading.Condition(self.m_mutex) # Ожидание уведомлений от других потоков
        self.m_data = 0 # Данные
        self.m_isReady = False # Флаг (готовность к обработке)

# Функция отправки данных и уведомления об их готовности
def SendDataToChannel(channel, data):
    # Блокируем мьютекс
    with channel.m_mutex:
        # Записываем данные, готовые к обработке
        channel.m_data = data
        # Устанавливаем флаг, указывающий, что данные готовы для обработки
        channel.m_isReady = True
        # Отправляем сообщение одному из потоков, ожидающих данные для обработки
        channel.m_notification.notify()
        # Ждём обработки данных
        channel.m_notification.wait_for(lambda: not channel.m_isReady)

# Функция отправки данных в канал (поток-поставщик данных)
def DataProviderThread(channel):
    # Отправка данных
    for i in range(1, 10):
        # Приостанавливаем поток на 1 секунду перед отправкой новых данных
        time.sleep(1)
        # Показываем, что задание отправляется
        print(f"Поток-поставщик отправил задание №{i}")
        # Вызываем функцию для отправки данных
        SendDataToChannel(channel, i)

# Функция обработки данных
def ProcessDataFromChannel(channel):
    # Блокируем мьютекс
    with channel.m_mutex:
        # Ждём обработки данных
        channel.m_notification.wait_for(lambda: channel.m_isReady)
        # Извлекаем данные для последующей обработки
        data = channel.m_data
        # Сбрасываем флаг, указывающий, что данные обработаны
        channel.m_isReady = False
        # Отправляем сообщение одному из потоков, ожидающих данные для следующей передачи
        channel.m_notification.notify()
        # Возвращаем обработанные данные
        return data

# Функция получения и обработки данных из канала (поток-потребитель данных)
def DataProcessThread(channel):
    # Переменная для сохранения полученного из канала значения
    data = 0
    while data != 9:
        # Вызываем функцию для извлечения данных из канала и их последующей обработки
        data = ProcessDataFromChannel(channel)
        # Показываем, что сообщение было получено
        print(f"Поток-потребитель получил задание № {data}")

if __name__ == "__main__":
    # Создаём экземпляр MutexData
    mutexData = MutexData()
    # Запускаем потоки поставщика
    providerThread = threading.Thread(target=DataProviderThread, args=(mutexData,))
    # Запускаем потоки потребителя
    processThread = threading.Thread(target=DataProcessThread, args=(mutexData,))
    # Запускаем потоки
    providerThread.start()
    processThread.start()
    # Ждём завершения выполнения потоков
    providerThread.join()
    processThread.join()

