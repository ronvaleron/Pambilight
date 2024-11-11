import time
import mss
import numpy as np
import serial

bright_r = 0.50
bright_g = 0.50
bright_b = 0.40
led_by_horizontal = 21
led_by_vertical = 12


def get_leds_color(sct, srl, screen_width: int, screen_height: int, segment_width: int, segment_height: int, led_by_horizontal: int, led_by_vertical: int) -> list:
    # Result in the BGR, not RGB = [[B], [G], [R]]
    result =  []
    average_color = None

    for led_num in range(0, (led_by_horizontal + led_by_vertical) * 2, 1):
        # Нижняя
        if led_num + 1 <= led_by_horizontal:
            side_led_num = led_num
            x1 = segment_width * side_led_num
            y1 = screen_height - segment_height
            segment_shot = sct.grab((x1, y1, x1 + segment_width, y1 + segment_height))
            image_array = np.array(segment_shot)
            average_color = np.mean(image_array, axis=(0, 1))
        # Правая
        elif led_by_horizontal < led_num + 1 <= (led_by_horizontal + led_by_vertical):
            side_led_num = led_num - led_by_horizontal
            if led_by_horizontal == led_num:
                average_color = result[led_num - 1]
            else:
                x1 = screen_width - segment_width
                y1 = screen_height - segment_height * (side_led_num + 1)
                segment_shot = sct.grab((x1, y1, x1 + segment_width, y1 + segment_height))
                image_array = np.array(segment_shot)
                average_color = np.mean(image_array, axis=(0, 1))
        # Верхняя
        elif (led_by_horizontal + led_by_vertical) < led_num + 1 <= (led_by_horizontal * 2 + led_by_vertical):
            side_led_num = led_num - (led_by_horizontal + led_by_vertical)
            if led_by_horizontal + led_by_vertical == led_num:
                average_color = result[led_num - 1]
            else:
                x1 = screen_width - segment_width * (side_led_num + 1)
                y1 = 0
                segment_shot = sct.grab((x1, y1, x1 + segment_width, y1 + segment_height))
                image_array = np.array(segment_shot)
                average_color = np.mean(image_array, axis=(0, 1))
        # Левая
        elif (led_by_horizontal * 2 + led_by_vertical) < led_num + 1:
            side_led_num = led_num - (led_by_horizontal * 2 + led_by_vertical)
            if (led_by_horizontal * 2 + led_by_vertical) == led_num:
                average_color = result[led_num - 1]
            elif (led_by_horizontal + led_by_vertical) * 2 == led_num + 1:
                average_color = result[0]
            else:
                x1 = 0
                y1 = segment_height * side_led_num
                segment_shot = sct.grab((x1, y1, x1 + segment_width, y1 + segment_height))
                image_array = np.array(segment_shot)
                average_color = np.mean(image_array, axis=(0, 1))
        else:
            exit()
        # result.append([round(average_color[0] * bright_b), round(average_color[1] * bright_g), round(average_color[2] * bright_r)])
        result.append([round(average_color[0] - 30), round(average_color[1] - 30), round(average_color[2]  - 30)])
    return result


# Подключаемся к экрану
with mss.mss() as sct:
    # Определяем размер экрана...
    screen_width = sct.monitors[0].get("width", 0)
    screen_height = sct.monitors[0].get("height", 0)
    # Подсчитываем размер сегмента изображения...
    segment_width = screen_width // led_by_horizontal
    segment_height = screen_height // led_by_vertical
    # Подключаемся к Ардуино...
    with serial.Serial('/dev/ttyUSB0', 115200) as srl:
        while True:
            # Делаем обработку 30 кадров в сек, для уменьшения нагрузки на процессор...
            time.sleep(0.03333)
            # Кодируем префикс обращения как Adalight, что бы работало и в Ambibox...
            prefix = (ord('A'), ord('d'), ord('a'))
            hi = 10
            lo = 5
            chk = 90
            # Передаем шифр
            srl.write(bytearray([*prefix, hi, lo, chk]))
            # Получаем значение цвета для каждого светодиода...
            leds =get_leds_color(sct, srl, screen_width, screen_height, segment_width, segment_height, led_by_horizontal, led_by_vertical)
            for led in leds:
                srl.write(bytearray([led[2] if led[2] > 0 else 0, led[1] if led[1] > 0 else 0, led[0] if led[0] > 0 else 0]))