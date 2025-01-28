import time
import mss
import numpy as np
import serial


BRIGHT_R = 0.3
DELTA_R = 0  # 20
BRIGHT_G = 0.2
DELTA_G = 0  # 25
BRIGHT_B = 0.2
DELTA_B = 0  # 22
LED_BY_HARIZONTAL = 21
LED_BY_VERTICAL = 12


def get_leds_color(sct, screen_width: int, screen_height: int, segment_width: int, segment_height: int, led_by_horizontal: int, led_by_vertical: int) -> list:
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
        # result.append([round(average_color[0] * BRIGHT_B), round(average_color[1] * BRIGHT_G), round(average_color[2] * BRIGHT_R)])
        result.append([round(
            average_color[0] * BRIGHT_B - DELTA_B if average_color[0] * BRIGHT_B - DELTA_B > 0 else 0
        ), round(
            average_color[1] * BRIGHT_G - DELTA_G if average_color[1] * BRIGHT_G - DELTA_G > 0 else 0
        ), round(
            average_color[2] * BRIGHT_R - DELTA_R if average_color[2] * BRIGHT_R - DELTA_R > 0 else 0
        )])
    return result


def main():
# Подключаемся к экрану
    with mss.mss() as sct:
        # Определяем размер экрана...
        screen_width = sct.monitors[1].get("width", 0)
        screen_height = sct.monitors[1].get("height", 0)
        # Подсчитываем размер сегмента изображения...
        segment_width = screen_width // LED_BY_HARIZONTAL
        segment_height = screen_height // LED_BY_VERTICAL
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
                leds =get_leds_color(sct, screen_width, screen_height, segment_width, segment_height, LED_BY_HARIZONTAL, LED_BY_VERTICAL)
                for led in leds:
                    srl.write(bytearray([led[2] if led[2] > 0 else 0, led[1] if led[1] > 0 else 0, led[0] if led[0] > 0 else 0]))


if __name__=="__main__":
    main()