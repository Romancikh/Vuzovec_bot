import xlsxwriter as xw
from datetime import date

FOLDER = "app/user_books/"


def edit_user_data(ud: str):
    sub_id = ud.index("[")
    sphere = ud[:sub_id]
    ud = ud[sub_id:]
    sub_id = ud.index("]") + 1
    subs = ud[:sub_id][1:][:-1].replace("'", "").split(', ')
    ud = ud[sub_id:]
    sub_id = ud.index("]") + 1
    pts = list(map(int, ud[:sub_id][1:][:-1].split(', ')))
    ud = ud[sub_id:]
    return (sphere, subs, pts, ud)


def get_formarts(workbook) -> list:
    format = []
    bot_label = workbook.add_format({
        'font_name': 'Arial',
        'font_size': 28,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#B6B6FC'
    })  # 0
    format.append(bot_label)

    header_center_text = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#B6B6FC'
    })  # 1
    format.append(header_center_text)

    list_label = workbook.add_format({
        'bg_color': '#FEABC4',
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True
    })  # 2
    format.append(list_label)

    city_label = workbook.add_format({
        'bg_color': '#C9E1B9',
        'align': 'center',
        'valign': 'vcenter'
    })  # 3
    format.append(city_label)

    default_format = workbook.add_format({
        'bg_color': '#FFF4D1',
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True,
        'border': True
    })  # 4
    format.append(default_format)

    default_format_left = workbook.add_format({
        'bg_color': '#FFF4D1',
        'align': 'left',
        'valign': 'vcenter',
        'text_wrap': True
    })  # 5
    format.append(default_format_left)

    return format


def print_labels(worksheet, format, line):
    worksheet.write('B%s' % (line), 'ВУЗ', format[2])
    worksheet.write('C%s' % (line), 'Направление', format[2])
    worksheet.write('D%s' % (line), 'Код', format[2])
    worksheet.write('E%s' % (line), 'Кол-во мест', format[2])
    worksheet.write('F%s' % (line), 'Баллы', format[2])
    worksheet.write('G%s' % (line), 'Цена обучения (руб./год)', format[2])


def header(user_data: str, worksheet, format):
    worksheet.set_column_pixels(0, 7, 20)
    worksheet.set_column_pixels(1, 1, 250, format[4])
    worksheet.set_column_pixels(2, 6, 160, format[4])
    worksheet.set_row_pixels(0, 60)
    worksheet.merge_range('B1:G1', '@ISPPR_bot', format[0])
    worksheet.merge_range('B2:G2', 'Здравствуй, дорогой абитуриент! Вот обещанный материал специально для тебя.',
                          format[1])
    worksheet.merge_range('B3:G3',
                          'Не забудь рассказать друзьям и одноклассникам о нашем чат-боте, если тебе понравился результат',
                          format[1])
    worksheet.merge_range('B4:G4',
                          'Список рекомендованных для поступления вузов и направлений по предпочтениям абитуриента',
                          format[2])
    worksheet.set_column_pixels(8, 9, 160)
    worksheet.write(1, 8, user_data[3])
    worksheet.merge_range('I2:J2', user_data[3], format[2])
    worksheet.write(2, 8, 'Сфера обучения: ', format[5])
    worksheet.write(2, 9, user_data[0], format[5])
    worksheet.write(4, 8, 'Сдаваемый предмет', format[2])
    worksheet.write(4, 9, 'Балл за экзамен', format[2])
    subs = user_data[1]
    pts = user_data[2]
    for i in range(len(subs)):
        worksheet.write(5 + i, 8, subs[i], format[5])
        worksheet.write(5 + i, 9, pts[i], format[5])
    worksheet.write(5 + len(subs), 8, 'Общий балл: ', format[5])
    worksheet.write(5 + len(subs), 9, sum(pts), format[5])
    return 8 + len(subs)


def body(specialties: dict, worksheet, format):
    line = 5
    for city in specialties.keys():
        worksheet.merge_range('B%s:G%s' % (line, line), city, format[3])
        line += 1
        print_labels(worksheet, format, line)
        line += 1
        for university in specialties[city].keys():
            if len(specialties[city][university].keys()) > 1:
                worksheet.merge_range('B%s:B%s' % (line, line + len(specialties[city][university].keys()) - 1),
                                      university)
            else:
                worksheet.write('B%s' % (line), university)
            for specialty in specialties[city][university].keys():
                sp_data = specialties[city][university][specialty]
                worksheet.write('C%s' % (line), sp_data.get('name'))
                worksheet.write('D%s' % (line), specialty)
                worksheet.write('E%s' % (line),
                                "Б" + str(sp_data.get('budget_place')) + "/Д" + str(sp_data.get('contractual_place')))
                worksheet.write('F%s' % (line),
                                "Б" + str(sp_data.get('budget_points')) + "/Д" + str(sp_data.get('contractual_points')))
                worksheet.write('G%s' % (line), str(sp_data.get('price')))
                line += 1
    return line + 1


def footer(worksheet, format, line, body_line):
    worksheet.merge_range('I%s:J%s' % (line, line + 1),
                          'Спасибо, что воспользовались нашим сервисом! Мы будем признательны, если Вы поможете в продвижении бота, поделившись им с каждым!',
                          format[5])
    line += 2
    worksheet.merge_range('I%s:J%s' % (line, line), 'Примечания', format[2])
    line += 1
    worksheet.merge_range('I%s:J%s' % (line, line + 1),
                          'Направление - это обобщённое обозначение, а специальность - узкое, конкретная область деятельности',
                          format[5])
    line += 2
    worksheet.merge_range('I%s:J%s' % (line, line), 'Код - это специальный шифр напрaвлений подготовки', format[5])
    line += 1
    worksheet.merge_range('I%s:J%s' % (line, line), 'Б - бюджет', format[5])
    line += 1
    worksheet.merge_range('I%s:J%s' % (line, line), 'Д - договор', format[5])
    line += 1
    worksheet.merge_range('I%s:J%s' % (line, line + 1),
                          'Cимвол "-" это отсутвие программы обучения по бюджету или договору', format[5])
    line += 2
    worksheet.merge_range('I%s:J%s' % (line, line + 1), 'Указаны проходные баллы, то есть порог для поступления',
                          format[5])
    line += 2
    worksheet.merge_range('I%s:J%s' % (line, line + 1), 'Заявления можно подать только в 5 вузов',
                          format[5])
    line += 2
    worksheet.merge_range('I%s:J%s' % (line, line + 1),
                          'Тех. Поддержка: @romankutimskiy, @white_tears_of_autumn, @Artyomeister',
                          format[5])
    line += 2
    if line < body_line:
        worksheet.merge_range('B%s:G%s' % (body_line, body_line + 1), ' ', format[0])
    else:
        worksheet.merge_range('B%s:G%s' % (line, line + 1), ' ', format[0])


def make_book(user_data: str, specialties: dict):
    user_data = edit_user_data(user_data)
    workbook = xw.Workbook(FOLDER + str(date.today()) + user_data[3] + '.xlsx')
    format = get_formarts(workbook)
    worksheet = workbook.add_worksheet('Итоговый чек-лист')
    worksheet.protect("2180")
    worksheet.hide_gridlines(2)
    line = header(user_data, worksheet, format)
    body_line= body(specialties, worksheet, format)
    footer(worksheet, format, line, body_line)
    worksheet.set_default_row(hide_unused_rows=True)
    workbook.close()
    return FOLDER + str(date.today()) + user_data[3] + '.xlsx'


if __name__ == "__main__":
    FOLDER = "user_books/"
    specialties = {'Москва': {
        'РГСУ': {
            '09.03.01': {
                'name': 'Информатика и вычислительная техника',
                'ege_subjects': ['математика', 'русский язык', ['физика', 'информатика и ИКТ']],
                'budget_points': 146,
                'contractual_points': 118,
                'budget_place': 28,
                'contractual_place': 62,
                'price': 236000},
            '09.03.02': {
                'name': 'Информатика и вычислительная техника',
                'ege_subjects': ['математика', 'русский язык', ['физика', 'информатика и ИКТ']],
                'budget_points': 146,
                'contractual_points': 118,
                'budget_place': 28,
                'contractual_place': 62,
                'price': 236000}}},
        'Санкт-Петербург': {
            'РГГМУ': {
                '10.05.02': {
                    'name': 'Информационная безопасность телекоммуникационных систем',
                    'ege_subjects': ['математика', 'физика', 'русский язык'],
                    'budget_points': 148,
                    'contractual_points': 148,
                    'budget_place': 20,
                    'contractual_place': 15,
                    'price': 202000}}}
    }
    user_data = "IT['русский язык', 'математика', 'физика'][80, 80, 80]@romankutimskiy"
    make_book(user_data, specialties)
