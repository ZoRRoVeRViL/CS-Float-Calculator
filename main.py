import flet as ft
import re
import asyncio
import struct
from itertools import combinations


def ieee754_convert(exit_float):
    packed = struct.pack('>f', exit_float)
    stored_value = struct.unpack('>f', packed)[0]
    return stored_value


def main(page: ft.Page):
    page.title = "CS Float Calculator"
    page.padding = 0
    page.bgcolor = ft.Colors.BLACK
    page.window.width = 1200
    page.window.height = 750
    page.window.min_width = 1200
    page.window.min_height = 750

    hover_scale = 1.03
    hover_opacity = 1
    normal_scale = 1.0
    normal_opacity = 0.4
    animation_duration = 150

    def animate_container(e):
        if e.data == "true":
            e.control.scale = hover_scale
            e.control.opacity = hover_opacity
        else:
            e.control.scale = normal_scale
            e.control.opacity = normal_opacity
        e.control.update()

    text_style = ft.TextStyle(
        size=48,
        weight=ft.FontWeight.BOLD,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK54),
        color=ft.Colors.WHITE
    )

    def open_new_window(e):
        min_float_field = ft.TextField(
            label="Минимальный флоат",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.WHITE,
            focused_border_color=ft.Colors.WHITE,
            max_length=25,
        )

        max_float_field = ft.TextField(
            label="Максимальный флоат",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.WHITE,
            focused_border_color=ft.Colors.WHITE,
            max_length=25,
        )

        final_float_field = ft.TextField(
            label="Желаемый флоат",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.WHITE,
            focused_border_color=ft.Colors.WHITE,
            max_length=25,
        )

        max_count_field = ft.TextField(
            label="Максимальное количество комбинаций",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.WHITE,
            focused_border_color=ft.Colors.WHITE
        )

        error_text = ft.Text(value='', color=ft.Colors.RED)

        find_button = ft.TextButton(
            "Найти",
            width=150,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                side=ft.BorderSide(1, ft.Colors.GREY),
                color=ft.Colors.GREY,
            ),
        )

        stop_button = ft.TextButton(
            "Стоп",
            width=150,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                side=ft.BorderSide(1, "#FFC0CB"),
                color=ft.Colors.GREY,
            ),
            disabled=True,
        )

        fields = [min_float_field, max_float_field, final_float_field, max_count_field]

        text_area = ft.TextField(
            label="Введите список float",
            multiline=True,
            min_lines=10,
            expand=True,
            border_color=ft.Colors.WHITE,
            focused_border_color=ft.Colors.WHITE,
            max_lines=10
        )

        result_text = ft.Text(value='', color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER)

        result_list_view = ft.ListView(
            controls=[result_text],
            height=150,
            auto_scroll=True,
        )

        result_container = ft.Container(
            content=result_list_view,
            border=ft.border.all(1, ft.Colors.with_opacity(0.5, ft.Colors.WHITE)),
            padding=10,
            border_radius=10,
        )

        def extract_numbers(text):
            pattern = r'[-+]?\d*\.\d+'
            numbers = re.findall(pattern, text)
            filtered_numbers = [num for num in numbers if len(num.split('.')[1]) > 5]
            result = ', '.join(filtered_numbers)

            return result

        def filter_text(e):
            text_area.value = extract_numbers(text_area.value)
            text_area.update()

        filter_button = ft.TextButton(
            "Фильтр",
            width=150,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                side=ft.BorderSide(1, ft.Colors.BLUE),
            ),
            on_click=filter_text
        )

        def close_dlg(e):
            dlg.open = False
            page.update()

        search_task = None
        stop_search = False

        async def search_float(e):
            nonlocal stop_search
            nonlocal search_task

            stop_search = False
            find_button.disabled = True
            find_button.style.side = ft.BorderSide(1, ft.Colors.GREY)
            find_button.style.color = ft.Colors.GREY
            stop_button.disabled = False
            stop_button.style.side = ft.BorderSide(1, ft.Colors.RED)
            stop_button.style.color = ft.Colors.RED
            page.update()

            try:
                min_float = float(min_float_field.value)
                max_float = float(max_float_field.value)
                final_float = float(final_float_field.value)
                max_count = int(max_count_field.value)
                float_values = [float(x) for x in text_area.value.split(',')] if text_area.value else []
            except ValueError:
                result_text.value = "Ошибка преобразования чисел"
                find_button.disabled = False
                find_button.style.side = ft.BorderSide(1, ft.Colors.BLUE)
                find_button.style.color = ft.Colors.BLUE
                stop_button.disabled = True
                stop_button.style.side = ft.BorderSide(1, "#FFC0CB")
                stop_button.style.color = ft.Colors.GREY
                page.update()
                return

            result_text.value = ''
            page.update()

            value_float = (max_float - min_float) / 10
            count = 0
            found = False

            for comb in combinations(float_values, 10):
                if stop_search:
                    result_text.value += '\nПоиск остановлен пользователем.'
                    break

                sum_comb = sum(comb)
                count += 1
                exit_float = sum_comb * value_float + min_float
                ieee_float = ieee754_convert(exit_float)

                if count % 1000000 == 0:
                    result_text.value += f'\n{count}) {ieee_float} Нет совпадений...'
                    page.update()

                if count == max_count:
                    result_text.value += '\nНе найдено подходящих комбинаций (достигнут лимит).'
                    page.update()
                    found = True
                    break

                if abs(ieee_float - final_float) < 1e-7:
                    result_text.value += f'\nНайдена комбинация:\n{count}) {ieee_float} | {comb}'
                    page.update()
                    found = True
                    break

            if not found and not stop_search:
                result_text.value += '\nНе найдено подходящих комбинаций.'
                page.update()

            find_button.disabled = False
            find_button.style.side = ft.BorderSide(1, ft.Colors.BLUE)
            find_button.style.color = ft.Colors.BLUE
            stop_button.disabled = True
            stop_button.style.side = ft.BorderSide(1, "#FFC0CB")
            stop_button.style.color = ft.Colors.GREY
            page.update()

        def find_float(e):
            nonlocal search_task

            is_valid = True
            for field in fields:
                if not field.value:
                    field.border_color = ft.Colors.RED
                    is_valid = False
                else:
                    field.border_color = None

            if is_valid and text_area.value:
                error_text.value = ""
                page.update()
                asyncio.run(search_float(e))
            else:
                if not text_area.value:
                    text_area.border_color = ft.Colors.RED
                else:
                    text_area.border_color = ft.Colors.WHITE
                error_text.value = "Заполните все поля"
                page.update()
                return

        def stop_float(e):
            nonlocal stop_search
            stop_search = True

        def validate_float(e):
            if e.control.value:
                e.control.value = e.control.value.replace(",", ".")
                try:
                    value = float(e.control.value)
                    if not 0 <= value <= 1:
                        e.control.error_text = "Значение должно быть от 0 до 1"
                    else:
                        e.control.error_text = None
                except ValueError:
                    e.control.error_text = "Введите число"
            else:
                e.control.error_text = "Введите значение"
            update_button_state()
            e.control.update()

        def validate_max_count(e):
            if e.control.value:
                try:
                    value = int(e.control.value)
                    if value <= 0:
                        e.control.error_text = "Значение должно быть больше 0"
                    else:
                        e.control.error_text = None
                except ValueError:
                    e.control.error_text = "Введите целое число"
            else:
                e.control.error_text = "Введите значение"
            update_button_state()
            e.control.update()

        def validate_max_float(e):
            if e.control.value:
                e.control.value = e.control.value.replace(",", ".")
                try:
                    value = float(e.control.value)
                    if value > 1:
                        e.control.error_text = "Значение не должно быть больше 1"
                    elif value <= 0:
                        e.control.error_text = "Значение должно быть больше 0"
                    else:
                        e.control.error_text = None
                except ValueError:
                    e.control.error_text = "Введите число"
            else:
                e.control.error_text = "Введите значение"
            update_button_state()
            e.control.update()

        def update_button_state():
            is_any_field_invalid = False
            for field in fields:
                if field.error_text or not field.value:
                    is_any_field_invalid = True
                    break
            find_button.disabled = is_any_field_invalid or not text_area.value
            if not find_button.disabled:
                find_button.style.side = ft.BorderSide(1, ft.Colors.BLUE)
                find_button.style.color = ft.Colors.BLUE
            else:
                find_button.style.side = ft.BorderSide(1, ft.Colors.GREY)
                find_button.style.color = ft.Colors.GREY

            page.update()

        def validate_text_area(e):
            if not e.control.value:
                e.control.border_color = ft.Colors.RED
            else:
                e.control.border_color = ft.Colors.WHITE
            update_button_state()
            e.control.update()

        min_float_field.on_change = validate_float
        max_float_field.on_change = validate_max_float
        final_float_field.on_change = validate_float
        max_count_field.on_change = validate_max_count

        text_area.on_change = validate_text_area

        find_button.on_click = find_float
        stop_button.on_click = stop_float

        update_button_state()

        left_container = ft.Container(
            content=ft.Column(
                [
                    min_float_field,
                    max_float_field,
                    final_float_field,
                    max_count_field,
                    error_text,
                    find_button,
                    stop_button,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=350,
            padding=10
        )

        right_container = ft.Container(
            content=ft.Column(
                [
                    text_area,
                    filter_button,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=350,
            padding=10,
        )

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Text("Найти комбинации для float", expand=True),
                ft.IconButton(ft.Icons.CLOSE, on_click=close_dlg),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        left_container,
                        right_container,
                    ],
                    ),
                    result_container,
                ],
                )
            ),
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    left_image = ft.Container(
        image_src="assets/left_image.jpg",
        image_fit=ft.ImageFit.COVER,
        expand=True,
        margin=0,
        border_radius=0
    )

    left_text = ft.Container(
        content=ft.Text(
            "Вычислить\nитоговый float",
            style=text_style,
            text_align=ft.TextAlign.CENTER
        ),
        alignment=ft.alignment.center,
        expand=True
    )

    left_panel = ft.Stack(
        controls=[
            left_image,
            ft.GestureDetector(
                content=left_text,
                mouse_cursor="default"
            )
        ],
        expand=True
    )

    right_image = ft.Container(
        image_src="assets/right_image.jpg",
        image_fit=ft.ImageFit.COVER,
        expand=True,
        margin=0,
        border_radius=0
    )

    right_text = ft.Container(
        content=ft.Text(
            "Найти\nкомбинации для float",
            style=text_style,
            text_align=ft.TextAlign.CENTER
        ),
        alignment=ft.alignment.center,
        expand=True
    )

    right_panel = ft.Stack(
        controls=[
            right_image,
            ft.GestureDetector(
                content=right_text,
                mouse_cursor="default",
                on_tap=open_new_window
            )
        ],
        expand=True
    )

    main_layout = (ft.Row(
        controls=[
            ft.Container(
                content=left_panel,
                on_hover=animate_container,
                scale=normal_scale,
                opacity=normal_opacity,
                animate_scale=ft.Animation(animation_duration, ft.AnimationCurve.EASE_OUT),
                animate_opacity=ft.Animation(animation_duration, ft.AnimationCurve.EASE_OUT),
                expand=True
            ),
            ft.Container(
                content=right_panel,
                on_hover=animate_container,
                scale=normal_scale,
                opacity=normal_opacity,
                animate_scale=ft.Animation(animation_duration, ft.AnimationCurve.EASE_OUT),
                animate_opacity=ft.Animation(animation_duration, ft.AnimationCurve.EASE_OUT),
                expand=True
            )
        ],
        expand=True,
        spacing=0,
        tight=True
    ))

    page.add(main_layout)


ft.app(target=main, assets_dir="assets")
